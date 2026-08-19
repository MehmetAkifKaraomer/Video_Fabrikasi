# Stil Rehberi — Video Fabrikası

Bu dosya sabittir, her video için yeniden sorulmaz. Değiştirmek
isterseniz elle düzenleyip commit'leyin — hiçbir ajan bu dosyayı
otomatik değiştirmez.

## Format (kritik, asla atlanmaz)

- **Dikey 9:16, 1080x1920 piksel** (Instagram Reels/Shorts).
- Render aracı `manim -r 1080,1920 ...` bayrağıyla çalıştırılır —
  Sanat Yönetmeni sahne kodunda bunu elle ayarlamaya ÇALIŞMAZ, render
  aracı hallediyor. Sahne kodu sadece nesneleri dikey alana göre
  yerleştirir (geniş yatay kompozisyonlardan kaçının).
- Süre: senaryodaki `hedef_sure_sn` neyse (40-50 sn aralığı).
- Ana kompozisyon çerçevenin ortasına, dikeyde en az %70, yatayda en
  az %60 alan kullanacak şekilde ölçeklenir — dar bir şeride sıkışmaz,
  kenarlarda büyük boşluk bırakmaz.

## Boyut kararı: 2D (sabit)

3D kullanılmaz. `ThreeDScene`, `Sphere`, `Cube`, kamera açısı
değiştirme gibi 3D öğeler istenmedikçe (yalnızca `brief.md`'de açık
"3D" notu varsa) kullanılmaz. 2D, bu projenin standart ve tek
kararıdır — bkz. Fourier/epicycle örneği: en etkileyici matematik
animasyonları bile çoğu zaman 2D'dir.

## Renk paleti (KCL referans görselinden çıkarıldı)

| Kullanım | Renk | Hex |
|---|---|---|
| Arka plan | neredeyse siyah | `#0B0B0F` |
| Akım/üst hat/vurgu | neon turuncu | `#FFA630` |
| Bileşen/doğru durum | neon yeşil | `#39FF14` |
| Toprak/alt hat | neon mavi | `#4FC3F7` |
| Metin/formül | kırık beyaz | `#F5F5F5` |

Manim'de sabitler olarak tanımlayın:
```python
ARKA_PLAN = "#0B0B0F"
TURUNCU = "#FFA630"
YESIL = "#39FF14"
MAVI = "#4FC3F7"
METIN = "#F5F5F5"
```

Düğüm/uç harfi etiketleri (A, B gibi), bağlı olduğu telin rengiyle
eşleşir — üst hat turuncuysa üst düğüm harfi turuncu, alt hat
maviyse alt düğüm harfi mavi.

## Glow efekti (referans görseldeki parlama)

Gerçek bloom shader yok — iç içe, giderek saydamlaşan daire yığınıyla
taklit edilir:
```python
def glow(merkez, renk, taban_yaricap=0.12):
    return VGroup(*[
        Circle(radius=taban_yaricap * f, stroke_width=0,
               fill_color=renk, fill_opacity=o).move_to(merkez)
        for f, o in [(3.5, 0.04), (2.5, 0.08), (1.6, 0.18), (1.0, 0.45)]
    ])
```
Düğüm noktalarında, dirençlerin üstünde bu fonksiyonu kullanın.

Opacity değerleri `[0.05, 0.12, 0.25, 0.6]`'dan `[0.04, 0.08, 0.18,
0.45]`'e düşürülmüştür — genel parlaklık azalır ama düğüm noktaları
hâlâ görünür kalır.

`glow()` fonksiyonu yalnızca devre düğüm noktaları ve bileşenler
içindir; metin, formül veya sayı etiketlerine glow uygulanmaz,
okunabilirliği bozar.

## Bileşen sembolleri

Voltaj kaynağı (pil) sembolündeki çizgiler ince ve zarif olmalı,
stroke_width devre teline göre daha kalın olmamalı, gereksiz
kabalık istenmiyor.

## Akım animasyonu

Referans görseldeki "noktalı akış" için `Dot` nesnelerini bir
`Line`/path üzerinde `MoveAlongPath` ile hareket ettirin; tek seferlik
değil, `always_redraw` veya döngüsel `Succession` ile sürekli aksın.

`MoveAlongPath`'e (veya akım noktalarının izlediği path'e) verilen
yol, düz bir kısayol çizgisi değil, bileşenin gerçek geometrisi
olmalı; bir direnç zigzag çiziliyorsa akım noktası da o zigzag'ı
takip etmeli.

Dot geçişleri varsayılan hızdan %30 daha hızlı olsun (run_time
değerlerini buna göre düşür), akış gözle daha net takip edilsin.

## Tipografi

- Başlık (varsa): üstte, `Write` animasyonuyla, `METIN` rengi.
- Formüller: `MathTex`, önemli terimler ilgili aksan renginde
  (örn. `V` turuncu, `I` yeşil, `R` mavi — Ohm örneğinde olduğu gibi).
- Gövde metni yok — bu videolarda anlatım tamamen seslendirmede,
  ekranda sadece formül/şema/sayı olur.
- Aynı denklemin iki farklı yönden yazılmış hali (I1+I2=I3 ve
  I3=I1+I2 gibi) aynı sahnede aynı anda ekranda birlikte tutulmaz —
  biri FadeOut olmadan diğeri gelmez.
