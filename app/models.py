from django.contrib.auth.models import User
from django.db import models

class Produk(models.Model):
    nama = models.CharField(max_length=100)
    stok = models.IntegerField()
    harga = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return self.nama

class Transaksi(models.Model):
    tanggal = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    kasir = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    
class ItemTransaksi(models.Model):
    transaksi = models.ForeignKey(Transaksi, on_delete=models.CASCADE)
    produk = models.ForeignKey(Produk, on_delete=models.CASCADE)
    jumlah = models.IntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
