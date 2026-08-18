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

## Glow efekti (referans görseldeki parlama)

Gerçek bloom shader yok — iç içe, giderek saydamlaşan daire yığınıyla
taklit edilir:
```python
def glow(merkez, renk, taban_yaricap=0.12):
    return VGroup(*[
        Circle(radius=taban_yaricap * f, stroke_width=0,
               fill_color=renk, fill_opacity=o).move_to(merkez)
        for f, o in [(3.5, 0.05), (2.5, 0.12), (1.6, 0.25), (1.0, 0.6)]
    ])
```
Düğüm noktalarında, dirençlerin üstünde bu fonksiyonu kullanın.

## Akım animasyonu

Referans görseldeki "noktalı akış" için `Dot` nesnelerini bir
`Line`/path üzerinde `MoveAlongPath` ile hareket ettirin; tek seferlik
değil, `always_redraw` veya döngüsel `Succession` ile sürekli aksın.

## Tipografi

- Başlık (varsa): üstte, `Write` animasyonuyla, `METIN` rengi.
- Formüller: `MathTex`, önemli terimler ilgili aksan renginde
  (örn. `V` turuncu, `I` yeşil, `R` mavi — Ohm örneğinde olduğu gibi).
- Gövde metni yok — bu videolarda anlatım tamamen seslendirmede,
  ekranda sadece formül/şema/sayı olur.
