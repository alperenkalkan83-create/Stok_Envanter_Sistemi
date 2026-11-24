# Stok ve Envanter Yönetim Sistemi
Küçük işletmelerin ürün bilgilerini ve mevcut stoklarını tek bir yerden takip etmesini sağlayan yerel web prototipi. Dağınık ürün kayıtlarının düzenlenmesini hedefler.

## Kurulum
Python 3.10+ gereklidir. Ek paket gerekmez. Terminalde proje klasöründe `python app.py` çalıştırın ve http://127.0.0.1:8000 adresini açın.

## İki özelliği deneyin
1. Ürün ekleme: URN-001, Fare, Elektronik, 250.50 TL, 10 adet girin. Kayıt başarılı olmalıdır. Aynı kodu tekrar girin; reddedilmelidir. Negatif stok ve boş isim kabul edilmemelidir.
2. Listeleme: Ürün tabloda görünmelidir. Sayfayı yenileyin ve sunucuyu yeniden başlatın; kayıt korunmalıdır.

## Otomatik testler
`python -m unittest discover -s tests -v`

## İş takip panosu
Gerçek GitHub Projects bağlantısı oluşturulduktan sonra buraya eklenmelidir. Görev kartları ve teslim rehberi: [docs/GITHUB.md](docs/GITHUB.md).

## Sınırlar
Yerel tek kullanıcılı prototip; kimlik doğrulama yoktur. Stok hareketleri, düzenleme/silme ve kritik stok uyarısı planlanmıştır, uygulanmamıştır. İnternete açık sunucuda kullanıma hazır değildir.
