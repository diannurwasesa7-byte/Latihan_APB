from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.timezone import now, timedelta
from django.utils import timezone
from django.db.models import Sum, Count
from .models import Produk, Transaksi, ItemTransaksi

# ========================
# CEK ROLE GRUP
# ========================
def is_kasir(user):
    return user.groups.filter(name='Kasir').exists()

def is_bos(user):
    return user.groups.filter(name='Bos').exists()

# ========================
# LOGIN VIEW
# ========================
def login_views(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if is_kasir(user):
                return redirect('home_kasir')
            elif is_bos(user):
                return redirect('home_admin')
            else:
                messages.error(request, 'Akun tidak memiliki role yang dikenali.')
                return redirect('login')
        else:
            messages.error(request, 'Username atau password salah')
    return render(request, 'login.html')

# ========================
# LOGOUT VIEW
# ========================
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# ========================
# DASHBOARD KASIR
# ========================
@login_required
@user_passes_test(is_kasir)
def home_kasir(request):
    today = timezone.now().date()
    total_harian = Transaksi.objects.filter(tanggal__date=today).aggregate(Sum('total'))['total__sum'] or 0
    count_harian = Transaksi.objects.filter(tanggal__date=today).count()
    total_produk = Produk.objects.count()
    return render(request, 'kasir/home.html', {
        'total_harian': total_harian,
        'count_harian': count_harian,
        'total_produk': total_produk,
        'now': timezone.now(),
    })

@login_required
@user_passes_test(is_kasir)
def tambah_transaksi(request):
    produk = Produk.objects.all()
    if request.method == 'POST':
        produk_id_list = request.POST.getlist('produk_id')
        jumlah_list = request.POST.getlist('jumlah')

        transaksi = Transaksi.objects.create(kasir=request.user, total=0)
        total = 0

        for i in range(len(produk_id_list)):
            p = Produk.objects.get(id=produk_id_list[i])
            jml = int(jumlah_list[i])

            if jml > 0:
                if jml > p.stok:
                    transaksi.delete()  # batalkan transaksi
                    messages.error(request, f"Stok untuk produk '{p.nama}' tidak mencukupi. Tersisa {p.stok} item.")
                    return redirect('tambah_transaksi')

                subtotal = p.harga * jml
                total += subtotal

                ItemTransaksi.objects.create(
                    transaksi=transaksi,
                    produk=p,
                    jumlah=jml,
                    subtotal=subtotal
                )

                p.stok -= jml
                p.save()

        transaksi.total = total
        transaksi.save()
        return redirect('cetak_transaksi')

    return render(request, 'kasir/tambah_transaksi.html', {'produk': produk})

@login_required
@user_passes_test(is_kasir)
def cetak_transaksi(request):
    transaksi = Transaksi.objects.last()
    items = ItemTransaksi.objects.filter(transaksi=transaksi)
    return render(request, 'kasir/cetak_transaksi.html', {
        'transaksi': transaksi,
        'items': items
    })

@login_required
@user_passes_test(is_kasir)
def produk(request):
    query = request.GET.get('q', '')
    if query:
        produk = Produk.objects.filter(nama__icontains=query)
    else:
        produk = Produk.objects.all()
    return render(request, 'kasir/produk.html', {'produk': produk})


# ========================
# DASHBOARD BOS
# ========================
@login_required
@user_passes_test(is_bos)
def home_admin(request):
    today = now().date()
    agg = Transaksi.objects.filter(tanggal__date=today).aggregate(
        total_harian=Sum('total'),
        count_harian=Count('id')
    )
    total_harian = agg['total_harian'] or 0
    count_harian = agg['count_harian'] or 0

    week_ago = now().date() - timedelta(days=7)
    agg_week = Transaksi.objects.filter(tanggal__date__gte=week_ago).aggregate(
        total_mingguan=Sum('total'),
        count_mingguan=Count('id')
    )
    total_mingguan = agg_week['total_mingguan'] or 0
    count_mingguan = agg_week['count_mingguan'] or 0

    total_produk = Produk.objects.count()
    stok_habis = Produk.objects.filter(stok__lte=0).count()

    return render(request, 'bos/home.html', {
        'today': today,
        'total_harian': total_harian,
        'count_harian': count_harian,
        'total_mingguan': total_mingguan,
        'count_mingguan': count_mingguan,
        'total_produk': total_produk,
        'stok_habis': stok_habis,
    })

@login_required
@user_passes_test(is_bos)
def produk_list(request):
    query = request.GET.get('q', '')
    if query:
        produk = Produk.objects.filter(nama__icontains=query)
    else:
        produk = Produk.objects.all()
    return render(request, 'bos/produk_list.html', {'produk': produk})

@login_required
@user_passes_test(is_bos)
def tambah_produk(request):
    if request.method == 'POST':
        nama_input = request.POST['nama'].strip().lower()
        harga_input = request.POST['harga']
        stok_input = int(request.POST['stok'])

        existing_produk = Produk.objects.filter(nama__iexact=nama_input).first()

        if existing_produk:
            existing_produk.stok += stok_input
            existing_produk.harga = harga_input
            existing_produk.save()
        else:
            Produk.objects.create(
                nama=nama_input,
                harga=harga_input,
                stok=stok_input
            )

        return redirect('produk_list')

    return render(request, 'bos/tambah_produk.html')

@login_required
@user_passes_test(is_bos)
def edit_produk(request, pk):
    produk = get_object_or_404(Produk, pk=pk)
    if request.method == 'POST':
        produk.nama = request.POST['nama']
        produk.harga = request.POST['harga']
        produk.stok = request.POST['stok']
        produk.save()
        return redirect('produk_list')
    return render(request, 'bos/edit_produk.html', {'produk': produk})

@login_required
@user_passes_test(is_bos)
def delete_produk(request, pk):
    produk = get_object_or_404(Produk, pk=pk)
    if request.method == 'POST':
        produk.delete()
        return redirect('produk_list')
    return render(request, 'bos/konfirmasi_hapus.html', {'produk': produk})

@login_required
@user_passes_test(is_kasir)
def history_transaksi_hari_ini(request):
    today = now().date()
    transaksi = Transaksi.objects.filter(kasir=request.user, tanggal__date=today).order_by('-tanggal')
    return render(request, 'kasir/history_transaksi.html', {'transaksi': transaksi})

@login_required
@user_passes_test(is_kasir)
def detail_transaksi_kasir(request, pk):
    transaksi = get_object_or_404(Transaksi, pk=pk, kasir=request.user)
    items = ItemTransaksi.objects.filter(transaksi=transaksi)
    return render(request, 'kasir/detail_transaksi.html', {'transaksi': transaksi,'items': items,})

# ========================
# LAPORAN
# ========================
@login_required
@user_passes_test(is_bos)
def laporan(request):
    transaksi = Transaksi.objects.all()
    return render(request, 'bos/laporan.html', {'transaksi': transaksi})

@login_required
@user_passes_test(is_bos)
def laporan_harian(request):
    today = now().date()
    transaksi = Transaksi.objects.filter(tanggal__date=today)
    return render(request, 'bos/laporan_harian.html', {'transaksi': transaksi})

@login_required
@user_passes_test(is_bos)
def laporan_mingguan(request):
    minggu_lalu = now() - timedelta(days=7)
    transaksi = Transaksi.objects.filter(tanggal__gte=minggu_lalu)
    return render(request, 'bos/laporan_mingguan.html', {'transaksi': transaksi})

@login_required
@user_passes_test(is_bos)
def laporan_bulanan(request):
    bulan_lalu = now() - timedelta(days=30)
    transaksi = Transaksi.objects.filter(tanggal__gte=bulan_lalu)
    return render(request, 'bos/laporan_bulanan.html', {'transaksi': transaksi})
