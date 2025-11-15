from django.urls import path
from . import views
from django.shortcuts import redirect

def redirect_root(request):
    return redirect('login')  # bisa redirect ke login atau home_kasir

urlpatterns = [
    # Default redirect
    path('', redirect_root, name='redirect_root'),

    # 🔐 Login & Logout
    path('login/', views.login_views, name='login'),
    path('logout/', views.logout_view, name='logout'),

  # 📌 Kasir
path('kasir/home/', views.home_kasir, name='home_kasir'),
path('kasir/transaksi/tambah/', views.tambah_transaksi, name='tambah_transaksi'),
path('kasir/transaksi/cetak/', views.cetak_transaksi, name='cetak_transaksi'),
path('kasir/produk/', views.produk, name='produk'),
path('kasir/transaksi/history/', views.history_transaksi_hari_ini, name='history_transaksi'),
path('kasir/transaksi/detail/<int:pk>/', views.detail_transaksi_kasir, name='detail_transaksi_kasir'),

# 📌 Bos / Admin
path('bos/home/', views.home_admin, name='home_admin'),
path('bos/produk/', views.produk_list, name='produk_list'),
path('bos/produk/tambah/', views.tambah_produk, name='tambah_produk'),
path('bos/produk/<int:pk>/edit/', views.edit_produk, name='edit_produk'),
path('bos/produk/<int:pk>/delete/', views.delete_produk, name='delete_produk'),

# 📊 Laporan
path('bos/laporan/', views.laporan, name='laporan'),
path('bos/laporan/harian/', views.laporan_harian, name='laporan_harian'),
path('bos/laporan/mingguan/', views.laporan_mingguan, name='laporan_mingguan'),
path('bos/laporan/bulanan/', views.laporan_bulanan, name='laporan_bulanan'),
]
