# GitHub ödev rehberi
Önce öğretmenin yapay zekâ desteğine izin verdiğini doğrulayın. Hazır prototipi kendi çalışmanız gibi veya geçmişte yapılmış geliştirme olarak göstermeyin.
1. GitHub'da stok-envanter adlı depo oluşturun. Projects altında Board oluşturun, Status seçeneklerini Yapılacak, Devam Ediyor, Tamamlandı olarak düzenleyin.
2. Aşağıdaki beş Issue'yu oluşturup panoya ekleyin. Gerçek durumlarını kaydedin. Hazır prototipi başlangıç olarak yüklediyseniz ilk iki özellik zaten vardır; yeni geliştirme görevi olarak #3 ve #5'i seçebilir, gerçekten geliştirip test edebilirsiniz. Alternatif olarak öğretmenin onayıyla başlangıçtan itibaren kendi uygulamanızı geliştirin.
3. Yeni geliştirmelerde önce kartı Devam Ediyor'a taşıyın, feature branch açın, kodu değiştirin, test edin, commit ve PR oluşturun. Gerçek bağlantıyı karta ekleyin. Kabul kriteri sağlandığında Tamamlandı'ya taşıyın.
4. README'ye gerçek pano bağlantısını ve gerçekten geliştirilen iki özelliğin deneme adımlarını ekleyin. Gizli depo/pano için musanmaz hesabına erişim verin. E-postaya depo bağlantısıyla yanıt verin.

## Issue 1 — Ürün ekleme
Açıklama: Ürün kodu, adı, kategori, fiyat ve miktar kaydı.
Kabul: Geçerli kayıt saklanır; yinelenen kod ve negatif miktar reddedilir.

## Issue 2 — Envanter listeleme
Açıklama: Kayıtları tabloda göster.
Kabul: Sayfa yenileme ve sunucu yeniden başlatma sonrasında kayıt görünür.

## Issue 3 — Stok giriş ve çıkışı
Açıklama: Ürünün miktarını artır veya azalt.
Kabul: 10 adet üründen 3 çıkış yapınca 7 kalır; 8 çıkış reddedilir.

## Issue 4 — Ürün güncelleme ve silme
Açıklama: Ürün bilgilerini düzenle ve onayla sil.
Kabul: Değişiklik kalıcıdır; onaylanan silme sonrasında ürün listelenmez.

## Issue 5 — Kritik stok uyarısı
Açıklama: Düşük stokları işaretle.
Kabul: Eşik 5 ise 4 adet stok uyarı alır, 5 adet almaz.
