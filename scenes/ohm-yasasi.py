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
        for f, o in [(3.5, 0.05), (2.5, 0.12), (1.6, 0.25), (1.0, 0.6)]
    ])


def create_circuit(center=ORIGIN, w=2.4, h=3.2):
    """Basit bir seri devre semasi: solda pil (turuncu uzun + mavi kisa
    cizgi), sagda zigzag direnc (yesil), araları birlestiren kirik beyaz
    (METIN) teller. Dugum noktalarina glow eklenir."""
    top_left = center + np.array([-w / 2, h / 2, 0])
    top_right = center + np.array([w / 2, h / 2, 0])
    bottom_left = center + np.array([-w / 2, -h / 2, 0])
    bottom_right = center + np.array([w / 2, -h / 2, 0])

    top_wire = Line(top_left, top_right, color=METIN, stroke_width=3)
    bottom_wire = Line(bottom_left, bottom_right, color=METIN, stroke_width=3)

    # Sol taraf - pil sembolu
    left_mid = center + np.array([-w / 2, 0, 0])
    gap = 0.35
    left_wire_top = Line(top_left, left_mid + UP * gap, color=METIN, stroke_width=3)
    left_wire_bottom = Line(left_mid + DOWN * gap, bottom_left, color=METIN, stroke_width=3)

    pil_uzun = Line(left_mid + UP * gap * 0.55 + LEFT * 0.28,
                     left_mid + UP * gap * 0.55 + RIGHT * 0.28,
                     color=TURUNCU, stroke_width=6)
    pil_kisa = Line(left_mid + DOWN * gap * 0.55 + LEFT * 0.14,
                     left_mid + DOWN * gap * 0.55 + RIGHT * 0.14,
                     color=MAVI, stroke_width=10)
    pil = VGroup(pil_uzun, pil_kisa)

    # Sag taraf - zigzag direnc
    right_mid = center + np.array([w / 2, 0, 0])
    zgap = 0.7
    right_wire_top = Line(top_right, right_mid + UP * zgap, color=METIN, stroke_width=3)
    right_wire_bottom = Line(right_mid + DOWN * zgap, bottom_right, color=METIN, stroke_width=3)

    n_zig = 5
    zigzag_points = [right_mid + UP * zgap]
    for i in range(n_zig):
        y = zgap - (2 * zgap) * (i + 1) / (n_zig + 1)
        x_off = 0.18 if i % 2 == 0 else -0.18
        zigzag_points.append(right_mid + np.array([x_off, y, 0]))
    zigzag_points.append(right_mid + DOWN * zgap)

    direnc = VMobject(color=YESIL, stroke_width=4)
    direnc.set_points_as_corners(zigzag_points)

    devre = VGroup(top_wire, bottom_wire, left_wire_top, left_wire_bottom,
                    pil, right_wire_top, right_wire_bottom, direnc)

    nodes = [top_left, top_right, bottom_left, bottom_right]
    dugum_glow = VGroup(*[glow(pt, METIN, 0.08) for pt in nodes])

    # Akan noktalarin izleyecegi kapali yol: devrenin GERCEK geometrisini
    # (ust tel, sag ust tel, zigzag direnc, sag alt tel, alt tel, sol alt
    # tel, pil arasi, sol ust tel) sirayla birlestirerek olusturulur - duz
    # bir kisayol degil, zigzag'i birebir takip eder.
    yol_noktalari = (
        [top_left, top_right]
        + zigzag_points
        + [bottom_right, bottom_left, left_mid + DOWN * gap, left_mid + UP * gap, top_left]
    )
    yol = VMobject(stroke_width=0, fill_opacity=0)
    yol.set_points_as_corners(yol_noktalari)

    parcalar = {"direnc": direnc, "pil": pil}
    return devre, dugum_glow, yol, parcalar


def make_flow_dots(path, n, speed, color=TURUNCU, radius=0.055):
    """Path uzerinde surekli akan (dt tabanli) nokta grubu olusturur."""
    dots = VGroup()
    for i in range(n):
        d = Dot(radius=radius, color=color)
        d.ilerleme = i / n
        d.move_to(path.point_from_proportion(d.ilerleme))

        def guncelle(mob, dt, path=path, speed=speed):
            mob.ilerleme = (mob.ilerleme + dt * speed) % 1
            mob.move_to(path.point_from_proportion(mob.ilerleme))

        d.add_updater(guncelle)
        dots.add(d)
    return dots


class OhmYasasi(Scene):
    def construct(self):
        self.camera.background_color = ARKA_PLAN

        # ---------- 1) [00:00-00:05] Devre semasi belirir ----------
        devre, dugum_glow, yol, parcalar = create_circuit(center=UP * 0.6)
        devre_tum = VGroup(devre, dugum_glow, yol)

        self.play(FadeIn(devre_tum), run_time=1)
        self.wait(4)

        # ---------- 2) [00:05-00:12] Akan noktalar (4 adet) ----------
        akim_dots = make_flow_dots(yol, n=4, speed=0.12, color=TURUNCU)
        self.play(FadeIn(akim_dots), run_time=0.5)
        self.wait(6.5)

        # ---------- 3) [00:12-00:20] Devre kuculur, formul yazilir ----------
        self.play(devre_tum.animate.scale(0.5).to_edge(UP, buff=0.4), run_time=1.5)

        formul = MathTex("V", "=", "I", r"\times", "R", color=METIN).scale(1.5)
        formul[0].set_color(TURUNCU)
        formul[2].set_color(YESIL)
        formul[4].set_color(MAVI)
        formul.next_to(devre_tum, DOWN, buff=0.9)

        self.play(Write(formul), run_time=2)
        self.wait(4.5)

        # ---------- 4) [00:20-00:27] V buyur, akim hizlanir (4->7) ----------
        akim_dots_hizli = make_flow_dots(yol, n=7, speed=0.24, color=TURUNCU)
        self.play(
            Indicate(formul[0], scale_factor=1.3, color=TURUNCU),
            FadeOut(akim_dots),
            FadeIn(akim_dots_hizli),
            run_time=1,
        )
        akim_dots = akim_dots_hizli
        self.wait(6)

        # ---------- 5) [00:27-00:34] R buyur, direnc kalinlasir, akim yavaslar (7->3) ----------
        direnc = parcalar["direnc"]
        direnc_glow = glow(direnc.get_center(), MAVI, 0.16)
        akim_dots_yavas = make_flow_dots(yol, n=3, speed=0.06, color=TURUNCU)

        self.play(
            Indicate(formul[4], scale_factor=1.3, color=MAVI),
            direnc.animate.set_stroke(width=direnc.get_stroke_width() * 1.3),
            FadeIn(direnc_glow),
            FadeOut(akim_dots),
            FadeIn(akim_dots_yavas),
            run_time=1,
        )
        akim_dots = akim_dots_yavas
        self.wait(6)

        # ---------- 6) [00:34-00:41] V=10V, R=5Ohm, I sayaci 0->2 ----------
        v_deger = MathTex("V = 10\\,V", color=TURUNCU).scale(0.9)
        v_deger.next_to(formul, DOWN, buff=0.6)
        self.play(Write(v_deger), run_time=1)

        r_deger = MathTex("R = 5\\,\\Omega", color=MAVI).scale(0.9)
        r_deger.next_to(v_deger, DOWN, buff=0.4)
        self.play(Write(r_deger), run_time=1)

        i_tracker = ValueTracker(0)
        i_deger = always_redraw(
            lambda: MathTex(
                f"I = {round(i_tracker.get_value())}\\,A", color=YESIL
            ).scale(0.9).next_to(r_deger, DOWN, buff=0.4)
        )
        self.add(i_deger)
        self.play(i_tracker.animate.set_value(2), run_time=1.5, rate_func=linear)
        self.wait(3.5)

        # ---------- 7) [00:41-00:45] V, I, R pulse glow (Flash) + sahne kararma ----------
        self.play(Flash(formul[0].get_center(), color=TURUNCU,
                         flash_radius=0.35, line_length=0.2), run_time=0.3)
        self.play(Flash(formul[2].get_center(), color=YESIL,
                         flash_radius=0.35, line_length=0.2), run_time=0.3)
        self.play(Flash(formul[4].get_center(), color=MAVI,
                         flash_radius=0.35, line_length=0.2), run_time=0.3)
        self.wait(2.6)

        for m in akim_dots:
            m.clear_updaters()

        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)
