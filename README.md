# Kavrama Stüdyosu

*(Eski çalışma adı: Video Fabrikası — klasör/repo adı değişmedi, bu
yalnızca proje adı.)*

**GitHub:** https://github.com/MehmetAkifKaraomer/Video_Fabrikasi

Matematik, fizik ve elektrik/elektronik konularını 40-80 saniyelik
dikey (9:16, Instagram Reels/Shorts formatı) eğitim videolarına
dönüştüren, çoklu ajan orkestrasyonuna dayalı otonom bir sistem.
SENG 456 — Ajan Orkestrasyonu ve Multimodal Sistemler dönem projesi.

## Mimari

Sistem 4 alt ajan + 1 MCP aracı + bir şef (Claude Code, `CLAUDE.md`
kurallarıyla yönetilir) etrafında kurulu:

| Bileşen | Rol | Yetki |
|---|---|---|
| `yazar` | Konuyu senaryo + görsel tarife çevirir | Read, Write |
| `icerik-denetcisi` | Senaryoyu teknik doğruluk/pedagoji açısından denetler | Read, Grep (yalnız okur) |
| `sanat-yonetmeni` | Görsel tarifi Manim koduna çevirir | Read, Write |
| `render_manim_scene` (MCP) | Kodu çalıştırır, video + kare üretir | — |
| `vision-qc` | Render edilen kareleri görsel olarak denetler | Read (+ vision) |

Akış: `Yazar → İçerik Denetçisi → (geçemezse Yazar'a geri döner) →
Sanat Yönetmeni → Render → Vision QC → (geçemezse Sanat Yönetmeni'ne
geri döner, maks 3 tur) → insan onayı`. Tam akış tanımı `CLAUDE.md`
içinde.

Tasarım ilkeleri: bağlam izolasyonu (her ajan yalnızca kendi görev
dosyasını okur), least-privilege araç yetkilendirmesi, denetleyici
ajanların Write yetkisi yok (kararlarını JSON olarak döndürür, dosyaya
yazma işini şef yapar), şef alt-ajan kararlarını asla kendi yorumuyla
değiştirmez.

## Kurulum

1. **Python 3.13** ve **Manim Community** (`pip install manim
   --break-system-packages`)
2. **ffmpeg** (video render/kare çıkarımı için)
3. **MiKTeX** ya da başka bir LaTeX dağıtımı (`MathTex` formülleri
   için — Manim'in kendisi LaTeX olmadan formül render edemez)
4. **MCP Python SDK** (`pip install "mcp[cli]" --break-system-packages`)
5. **Claude Code** (proje kökünden `claude` ile başlatılmalı —
   `.mcp.json` proje-scope olduğu için yalnızca doğru dizinden
   başlatılan oturumlar `manim-render` aracını görür)
6. İlk çalıştırmada Claude Code, `.mcp.json`'daki sunucu için bir
   güven onayı isteyecektir — onaylayın (`Use this and all future MCP
   servers in this project` seçeneği önerilir).

## Çalıştırma

Proje kökünden bir Claude Code oturumu açıp doğal dilde konu verin:

```
"Ohm Yasası konusunu anlat — CLAUDE.md'deki akışı baştan sona işlet"
```

Sistem `brief.md` oluşturur, dört ajanı ve render aracını sırasıyla
çağırır, sonunda video yolunu onayınıza sunar. Video
`output/<konu-slug>/videos/<konu-slug>/1920p60/*.mp4` altında, Vision
QC'nin incelediği kareler `output/<konu-slug>/kareler/` altında
oluşur.

## Klasör yapısı

```
.claude/agents/       — alt ajan tanımları (.md)
mcp_server/           — render_manim_scene MCP aracı
scenes/                — Sanat Yönetmeni'nin ürettiği Manim kodu
output/                — render edilen video ve kareler (git'e girmez)
stil-rehberi.md        — sabit görsel kimlik (renk, format, glow, kompozisyon)
CLAUDE.md              — şefin akış kuralları
brief.md, senaryo.md   — çalışma anındaki görev dosyaları (devir sözleşmesi)
denetim-raporu.json    — İçerik Denetçisi'nin son kararı
vision-raporu.json     — Vision QC'nin son kararı
```

## Örnek çıktılar

| Konu | Sonuç | Not |
|---|---|---|
| Ohm Yasası | `gecti: true`, puan 88 | 1 turda; ayrıca şefin bir alt-ajan kararını yanlışlıkla ezmeye çalışıp CLAUDE.md kuralıyla düzeltildiği bir yönetişim örneği içeriyor |
| Kirchhoff Akım Yasası (Düğüm Analizi) | `gecti: true`, puan 94 | İçerik Denetçisi bir devre hatasını (kısa devre çelişkisi) yakalayıp geri gönderdi (1 retry), Vision QC bir renk kuralı ihlalini yakalayıp geri gönderdi (1 retry) — hata toleransı döngüsünün iki farklı katmanda çalıştığının kanıtı |
| Kirchhoff Gerilim Yasası (KVL, 3 gözlü devre) | `gecti: false`, durduruldu | 5 render/Vision-QC turunda (3 otomatik + 2 yönlendirmeli) kompozisyon/yerleşim sorunu kalıcı çözülemedi; sistem tasarlandığı durma koşulu gereği otomatik 6. turu başlatmadı, insana danıştı. İnsan, maliyet/fayda değerlendirmesiyle videoyu teslim etmemeyi seçti. **Bu, hata toleransının bir başarısızlığı değil, sınırının doğru çalıştığının kanıtıdır** — bkz. teslim belgesi Bölüm 6.

## Bilinen teknik notlar

- MCP sunucusu bir Python kaynak dosyası olarak yalnızca oturum
  başlangıcında yüklenir; `mcp_server/manim_render.py` değiştiğinde
  Claude Code'un tamamen yeniden başlatılması gerekir (`.claude/agents/*.md`
  gibi ajan tanımları için bu gerekmez, her çağrıda taze okunur).
- Render aracı `manim`/`ffmpeg`/`ffprobe`'u PATH yerine `shutil.which`
  + mutlak yol yedeğiyle çağırır — MCP sunucu sürecinin PATH'i,
  interaktif terminal PATH'inden farklı davranabildiği için.
- Aynı `konu_slug` ile tekrar render edilirken önceki çıktı klasörü
  tamamen temizlenir ve alt süreçler `stdin=DEVNULL` ile çalıştırılır
  — üzerine yazma onayı bekleyen bir alt sürecin sonsuza kadar
  takılı kalmasını önlemek için.

## Kapsam dışı (bilinçli karar)

Günlük otomatik video üretimi ve sosyal medyaya otomatik paylaşım bu
sürümde yok — bkz. teslim belgesinin "Sonuç ve Gelecek Çalışmalar"
bölümü.
