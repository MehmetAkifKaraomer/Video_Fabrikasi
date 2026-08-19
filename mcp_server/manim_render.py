"""
MCP render aracı: scenes/ altındaki bir Manim sahnesini dikey (9:16,
1080x1920) formatta render eder, sonra Vision QC'nin okuyacağı
kareleri (PNG) çıkarır.

Kurulum (bir kere): pip install "mcp[cli]" --break-system-packages
Çalıştırma: Claude Code, .mcp.json üzerinden bunu otomatik başlatır -
elle çalıştırmanıza gerek yok.
"""

import subprocess
import pathlib
import shutil
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("manim-render")

PROJE_KOKU = pathlib.Path(__file__).resolve().parent.parent
SAHNELER = PROJE_KOKU / "scenes"
CIKTI = PROJE_KOKU / "output"


def _video_suresi(video_yolu: pathlib.Path) -> float:
    komut = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(video_yolu),
    ]
    try:
        sonuc = subprocess.run(
            komut, capture_output=True, text=True, timeout=15,
            stdin=subprocess.DEVNULL,
        )
        return float(sonuc.stdout.strip())
    except (ValueError, subprocess.TimeoutExpired):
        return 45.0  # güvenli varsayılan, kare çıkarımı yine de çalışır


@mcp.tool()
def render_manim_scene(dosya_adi: str, sinif_adi: str, konu_slug: str) -> dict:
    """
    scenes/<dosya_adi> içindeki <sinif_adi> Scene sınıfını dikey
    (1080x1920) formatta render eder, videodan %25/%50/%75 zaman
    noktalarında PNG kareler çıkarır.

    dosya_adi: scenes/ altındaki .py dosyasının adı (örn: "ohm-yasasi.py")
    sinif_adi: dosya içindeki Scene alt sınıfının tam adı (örn: "OhmYasasi")
    konu_slug: çıktı klasörü adı, tire ile ayrılmış (örn: "ohm-yasasi")

    Döner: {"basarili": bool, "video_yolu": str, "kareler": [str, ...]}
    ya da hata durumunda {"basarili": False, "hata": str}
    """
    sahne_yolu = SAHNELER / dosya_adi
    if not sahne_yolu.exists():
        return {"basarili": False, "hata": f"{sahne_yolu} bulunamadı"}

    video_cikti_klasoru = CIKTI / konu_slug
    if video_cikti_klasoru.exists():
        shutil.rmtree(video_cikti_klasoru)
    video_cikti_klasoru.mkdir(parents=True, exist_ok=True)

    komut = [
        "manim", "render",
        "-r", "1080,1920",
        "--format", "mp4",
        "--media_dir", str(video_cikti_klasoru),
        str(sahne_yolu), sinif_adi,
    ]

    try:
        sonuc = subprocess.run(
            komut, capture_output=True, text=True, timeout=600,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return {"basarili": False, "hata": "Render 600 saniyeyi aştı - sahne çok karmaşık olabilir"}

    if sonuc.returncode != 0:
        # Son 2000 karakter yeterli - tüm Manim logunu Sanat Yönetmeni'ne
        # göndermek gereksiz token harcar (bağlam izolasyonu ilkesi).
        return {"basarili": False, "hata": sonuc.stderr[-2000:]}

    video_dosyalari = list(video_cikti_klasoru.rglob(f"{sinif_adi}.mp4"))
    if not video_dosyalari:
        return {"basarili": False, "hata": "Render hatasız bitti ama mp4 bulunamadı - dosya adı uyuşmazlığı olabilir"}
    video_yolu = video_dosyalari[0]

    kareler_klasoru = video_cikti_klasoru / "kareler"
    kareler_klasoru.mkdir(exist_ok=True)
    sure = _video_suresi(video_yolu)

    kare_yollari = []
    for i, oran in enumerate([0.25, 0.5, 0.75]):
        zaman = round(sure * oran, 2)
        kare_yolu = kareler_klasoru / f"kare_{i}.png"
        ffmpeg_komut = [
            "ffmpeg", "-y", "-ss", str(zaman), "-i", str(video_yolu),
            "-frames:v", "1", str(kare_yolu),
        ]
        try:
            subprocess.run(
                ffmpeg_komut, capture_output=True, timeout=30,
                stdin=subprocess.DEVNULL,
            )
        except subprocess.TimeoutExpired:
            continue
        if kare_yolu.exists():
            kare_yollari.append(str(kare_yolu))

    if not kare_yollari:
        return {"basarili": False, "hata": "Video render edildi ama hiç kare çıkarılamadı - ffmpeg kurulumunu kontrol edin"}

    return {
        "basarili": True,
        "video_yolu": str(video_yolu),
        "kareler": kare_yollari,
    }


if __name__ == "__main__":
    mcp.run()
