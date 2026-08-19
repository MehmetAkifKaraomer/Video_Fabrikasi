# Video Fabrikası

Matematik/fizik/elektrik/elektronik konularını 40-50 saniyelik dikey
(9:16) eğitim videolarına dönüştüren çoklu ajan sistemi. Bu dosya
şefin (senin, orkestratörün) kalıcı kural setidir - her oturumda
otomatik yüklenir, elle hatırlatılmasına gerek yok.

## Sabit kararlar (değişmez, her video için aynı)
- Format: dikey, 1080x1920.
- Görsel kimlik: `stil-rehberi.md` - renk paleti, glow tekniği, 2D
  kararı. Bu dosya değişmez, hiçbir ajan onu düzenlemez.
- 3D yalnızca `brief.md`'de açık bir "3D" notu varsa kullanılır.

## Akış: "X konusunu anlat" komutu geldiğinde

1. `brief.md` oluştur/güncelle: `konu`, `hedef_sure_sn` (40-50),
   `onceki_oneri` (ilk turda boş).
2. `yazar` alt ajanını çağır → `senaryo.md` üretir.
3. `icerik-denetcisi` alt ajanını çağır → `denetim-raporu.json`.
   - `gecti: false` ise: `brief.md`'nin `onceki_oneri` alanını
     raporun `oneri`'siyle güncelle, adım 2'ye dön.
4. `sanat-yonetmeni` alt ajanını çağır → `scenes/<konu-slug>.py`.
5. `render_manim_scene` MCP aracını çağır (`dosya_adi`, `sinif_adi`,
   `konu_slug` ile).
   - `basarili: false` dönerse: `hata` alanını sanat-yonetmeni'ne
     ilet, adım 4'e dön.
6. `vision-qc` alt ajanını çağır (kareler üzerinden) → `vision-raporu.json`.
   - `gecti: false` ise: `oneri`'yi sanat-yonetmeni'ne ilet, adım 4'e
     dön.
7. **Durma koşulu**: adım 4-6 döngüsü en fazla 3 kez döner (sayacı
   sen tutuyorsun, ajanlar tutmuyor). 3. denemede hâlâ
   `gecti: false` ise DUR - otomatik 4. denemeyi başlatma, kullanıcıya
   durumu özetle (hangi turlarda ne reddedildi) ve nasıl ilerlemek
   istediğini sor.
8. `gecti: true` olduğunda: video yolunu kullanıcıya göster, onay
   iste. Onaysız hiçbir dosyayı "final" olarak işaretleme.

## Devir sözleşmesi (hand-off contract)
- Ajanlar arası iletişim yalnızca dosya üzerinden olur, konuşma
  geçmişi kopyalanarak değil (bağlam izolasyonu - her ajan yalnızca
  kendi görev dosyasını okur).
- Tüm denetleyiciler aynı JSON şemasını kullanır:
  `{"gecti": bool, "puan": int, "bulgular": [string], "oneri": string}`.
- Şef, alt ajanların döndürdüğü JSON kararlarını asla kendi
  yorumuyla değiştirmez, yalnızca olduğu gibi dosyaya yazar. Bir
  kararla anlaşmıyorsa, o ajanı ek bağlamla tekrar çağırır, kararı
  kendisi değiştirmez.

## Kapsam dışı (bilinçli karar, şimdilik yapılmayacak)
- Günlük otomatik video üretimi yok.
- Sosyal medyaya otomatik paylaşım yok.
- Bu ikisi teslim belgesinin "Gelecek Çalışmalar" bölümünde madde
  olarak kalır, kod olarak inşa edilmez.
