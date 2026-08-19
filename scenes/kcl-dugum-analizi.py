from manim import *
import numpy as np

ARKA_PLAN = "#0B0B0F"
TURUNCU = "#FFA630"
YESIL = "#39FF14"
MAVI = "#4FC3F7"
METIN = "#F5F5F5"


def glow(merkez, renk, taban_yaricap=0.12):
    return VGroup(*[
        Circle(radius=taban_yaricap * f, stroke_width=0,
               fill_color=renk, fill_opacity=o).move_to(merkez)
        for f, o in [(3.5, 0.04), (2.5, 0.08), (1.6, 0.18), (1.0, 0.45)]
    ])


def zigzag_points(start, end, segments=6, amp=0.15):
    """Baslangictan bitise, dogru cizgi yerine kirik (zigzag) bir direnc
    sembolu izleyen nokta listesi uretir."""
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)
    pts = [start]
    for i in range(1, segments):
        t = i / segments
        base = start + (end - start) * t
        offset = amp if i % 2 == 1 else -amp
        pts.append(base + np.array([offset, 0.0, 0.0]))
    pts.append(end)
    return pts


def build_branch(x, y_top, y_bottom, has_battery, direnc_etiket, gerilim_etiket=None):
    """Node A bus'indan (y_top) Node B bus'ina (y_bottom) inen bir dal
    olusturur. Her dalda mutlaka bir zigzag direnc bulunur; pilli dallarda
    ayrica bir pil sembolu eklenir (hicbir dal sifir direncli duz tel
    degildir)."""
    top = np.array([x, y_top, 0.0])
    bottom = np.array([x, y_bottom, 0.0])

    if has_battery:
        res_top = np.array([x, 1.9, 0.0])
        res_bottom = np.array([x, 1.1, 0.0])
        batt_top = np.array([x, 0.5, 0.0])
        batt_bottom = np.array([x, 0.1, 0.0])
        pts = [top] + zigzag_points(res_top, res_bottom) + [batt_top, batt_bottom, bottom]
        res_mid_y = (res_top[1] + res_bottom[1]) / 2
    else:
        res_top = np.array([x, 1.3, 0.0])
        res_bottom = np.array([x, 0.5, 0.0])
        pts = [top] + zigzag_points(res_top, res_bottom) + [bottom]
        res_mid_y = (res_top[1] + res_bottom[1]) / 2

    yol = VMobject(stroke_color=YESIL, stroke_width=3.5)
    yol.set_points_as_corners(pts)

    tel_grubu = VGroup(yol)
    if has_battery:
        pil_uzun = Line(np.array([x - 0.26, 0.45, 0.0]), np.array([x + 0.26, 0.45, 0.0]),
                         color=YESIL, stroke_width=2.5)
        pil_kisa = Line(np.array([x - 0.15, 0.15, 0.0]), np.array([x + 0.15, 0.15, 0.0]),
                         color=YESIL, stroke_width=7)
        tel_grubu.add(pil_uzun, pil_kisa)

    etiket_grubu = VGroup()
    r_etiket = Text(direnc_etiket, color=METIN, font_size=24)
    r_etiket.move_to(np.array([x + 0.5, res_mid_y, 0.0]))
    etiket_grubu.add(r_etiket)

    if has_battery and gerilim_etiket is not None:
        v_etiket = Text(gerilim_etiket, color=METIN, font_size=24)
        v_etiket.move_to(np.array([x + 0.5, 0.3, 0.0]))
        etiket_grubu.add(v_etiket)

    return yol, tel_grubu, etiket_grubu


def make_flow(path, tur_suresi, renk, ters=False, taban_yaricap=0.09,
              dot_yaricap=0.05, baslangic=0.0):
    """Path (dalin gercek zigzag geometrisi) uzerinde surekli, donguesel
    olarak akan (dt tabanli, add_updater ile) TURUNCU glow'lu bir Dot
    grubu olusturur. ters=True ise akis Node B'den Node A'ya dogrudur."""
    grup = VGroup(glow(ORIGIN, renk, taban_yaricap),
                   Dot(radius=dot_yaricap, color=renk, fill_opacity=1))
    grup.ilerleme = baslangic
    hiz = 1.0 / tur_suresi

    def guncelle(mob, dt, path=path, hiz=hiz, ters=ters):
        mob.ilerleme = (mob.ilerleme + dt * hiz) % 1
        t = (1 - mob.ilerleme) if ters else mob.ilerleme
        mob.move_to(path.point_from_proportion(t))

    grup.add_updater(guncelle)
    baslangic_t = (1 - baslangic) if ters else baslangic
    grup.move_to(path.point_from_proportion(baslangic_t))
    return grup


class KCLDugumAnalizi(Scene):
    def construct(self):
        self.camera.background_color = ARKA_PLAN

        Y_A = 2.5
        Y_B = -2.5
        LEFT_X = -1.3
        MID_X = 0.0
        RIGHT_X = 1.3
        BUS_YARI = 1.6

        # ================= 1) [00:00-00:05] Baslik + soru isareti =================
        baslik = Text("Kirchhoff Akım Yasası", color=METIN, font_size=34)
        if baslik.width > 3.9:
            baslik.scale_to_fit_width(3.9)
        baslik.move_to(np.array([0, 3.4, 0]))

        soru = Text("?", color=METIN, font_size=72).move_to(np.array([0, 0.3, 0]))
        cember = Circle(radius=0.4, stroke_width=2, stroke_color=METIN,
                         stroke_opacity=0.8, fill_opacity=0).move_to(soru.get_center())

        self.play(Write(baslik), run_time=0.8)
        self.play(Write(soru), run_time=0.3)
        self.play(cember.animate.scale(6).set_stroke(opacity=0),
                   FadeOut(soru), run_time=1.0)
        self.play(FadeOut(baslik), FadeOut(cember), run_time=0.4)
        self.wait(2.5)

        # ================= 2) [00:05-00:12] Devre iskeleti =================
        bus_a = Line(np.array([-BUS_YARI, Y_A, 0]), np.array([BUS_YARI, Y_A, 0]),
                     color=TURUNCU, stroke_width=4)
        bus_b = Line(np.array([-BUS_YARI, Y_B, 0]), np.array([BUS_YARI, Y_B, 0]),
                     color=MAVI, stroke_width=4)

        dugum_a_glow = glow(np.array([BUS_YARI, Y_A, 0]), TURUNCU, taban_yaricap=0.13)
        dugum_b_glow = glow(np.array([BUS_YARI, Y_B, 0]), MAVI, taban_yaricap=0.13)
        etiket_a = Text("A", color=METIN, font_size=32).next_to(
            np.array([BUS_YARI, Y_A, 0]), RIGHT, buff=0.3)
        etiket_b = Text("B", color=METIN, font_size=32).next_to(
            np.array([BUS_YARI, Y_B, 0]), RIGHT, buff=0.3)

        self.play(Create(bus_a), Create(bus_b), run_time=0.6)
        self.play(FadeIn(dugum_a_glow), FadeIn(dugum_b_glow),
                   Write(etiket_a), Write(etiket_b), run_time=0.5)

        sol_yol, sol_tel, sol_etiket = build_branch(
            LEFT_X, Y_A, Y_B, True, "R1", "10V")
        orta_yol, orta_tel, orta_etiket = build_branch(
            MID_X, Y_A, Y_B, False, "R3")
        sag_yol, sag_tel, sag_etiket = build_branch(
            RIGHT_X, Y_A, Y_B, True, "R2", "20V")

        self.play(Create(sol_tel), run_time=0.6)
        self.play(Create(orta_tel), run_time=0.6)
        self.play(Create(sag_tel), run_time=0.6)
        self.play(Write(sol_etiket), Write(orta_etiket), Write(sag_etiket), run_time=0.6)
        self.wait(3.5)

        # ================= 3) [00:12-00:20] Sureklir akan I1, I2, I3 =================
        sol_dot = make_flow(sol_yol, tur_suresi=1.2, renk=TURUNCU, ters=True, baslangic=0.1)
        sag_dot = make_flow(sag_yol, tur_suresi=1.2, renk=TURUNCU, ters=True, baslangic=0.55)
        orta_dot = make_flow(orta_yol, tur_suresi=1.2, renk=TURUNCU, ters=False, baslangic=0.3)

        self.play(FadeIn(sol_dot), FadeIn(sag_dot), FadeIn(orta_dot), run_time=0.4)

        i1_etiket = MathTex("I_1", color=TURUNCU).scale(0.8).move_to(
            np.array([LEFT_X - 0.35, Y_A - 0.5, 0]))
        i2_etiket = MathTex("I_2", color=TURUNCU).scale(0.8).move_to(
            np.array([RIGHT_X + 0.35, Y_A - 0.5, 0]))
        i3_etiket = MathTex("I_3", color=TURUNCU).scale(0.8).move_to(
            np.array([MID_X + 0.35, Y_A - 0.5, 0]))

        self.play(Write(i1_etiket), Write(i2_etiket), run_time=0.5)
        self.play(Write(i3_etiket), run_time=0.4)
        self.wait(6.7)

        # ================= 4) [00:20-00:28] I1 + I2 = I3 =================
        self.play(dugum_a_glow.animate.scale(1.15), rate_func=there_and_back, run_time=0.4)
        self.play(dugum_a_glow.animate.scale(1.15), rate_func=there_and_back, run_time=0.4)

        # Her parca ayri bir MathTex olarak olusturulup arrange edilir; boylece
        # '+' ve '=' isaretleri renk sizintisi olmadan METIN renginde kalir,
        # yalnizca I1/I2/I3 TURUNCU olur (segment 6'daki guvenli desenle ayni).
        f1_i1 = MathTex("I_1", color=TURUNCU)
        f1_arti = MathTex("+", color=METIN)
        f1_i2 = MathTex("I_2", color=TURUNCU)
        f1_esit = MathTex("=", color=METIN)
        f1_i3 = MathTex("I_3", color=TURUNCU)
        formul1 = VGroup(f1_i1, f1_arti, f1_i2, f1_esit, f1_i3)
        formul1.arrange(RIGHT, buff=0.25).scale(1.1)
        formul1.move_to(np.array([0, 3.3, 0]))

        self.play(Write(formul1), run_time=1.0)
        self.wait(2.0)
        self.wait(4.2)

        # ================= 5) [00:28-00:37] I3 = I1 + I2 =================
        self.play(dugum_b_glow.animate.scale(1.15), rate_func=there_and_back, run_time=0.4)
        self.play(dugum_b_glow.animate.scale(1.15), rate_func=there_and_back, run_time=0.4)

        f2_i3 = MathTex("I_3", color=TURUNCU)
        f2_esit = MathTex("=", color=METIN)
        f2_i1 = MathTex("I_1", color=TURUNCU)
        f2_arti = MathTex("+", color=METIN)
        f2_i2 = MathTex("I_2", color=TURUNCU)
        formul2 = VGroup(f2_i3, f2_esit, f2_i1, f2_arti, f2_i2)
        formul2.arrange(RIGHT, buff=0.25).scale(1.1)
        formul2.move_to(np.array([0, -3.3, 0]))

        self.play(Write(formul2), run_time=1.0)
        self.wait(2.0)
        self.wait(5.2)

        # ================= 6) [00:37-00:45] Genel yasa + kapanis =================
        self.play(FadeOut(formul1), FadeOut(formul2), run_time=0.4)

        devre_grubu = VGroup(
            bus_a, bus_b, dugum_a_glow, dugum_b_glow, etiket_a, etiket_b,
            sol_tel, orta_tel, sag_tel, sol_etiket, orta_etiket, sag_etiket,
            i1_etiket, i2_etiket, i3_etiket,
        )
        self.play(devre_grubu.animate.scale(0.7).shift(DOWN * 1.3), run_time=0.6)

        genel_sol = Text("ΣI giren", color=TURUNCU, font_size=34)
        genel_esit = Text("=", color=METIN, font_size=34)
        genel_sag = Text("ΣI çıkan", color=MAVI, font_size=34)
        genel_formul = VGroup(genel_sol, genel_esit, genel_sag).arrange(RIGHT, buff=0.25)
        if genel_formul.width > 3.9:
            genel_formul.scale_to_fit_width(3.9)
        genel_formul.move_to(np.array([0, 3.3, 0]))

        self.play(Write(genel_formul), run_time=1.0)
        self.play(dugum_a_glow.animate.scale(1.3), dugum_b_glow.animate.scale(1.3),
                   rate_func=there_and_back, run_time=0.3)
        self.wait(4.7)

        for d in (sol_dot, sag_dot, orta_dot):
            d.clear_updaters()

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
