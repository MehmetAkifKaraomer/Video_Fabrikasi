from manim import *
class Test(Scene):
    def construct(self):
        self.camera.background_color = "#0B0B0F"
        self.play(Write(Text("Merhaba", color="#F5F5F5")))
        self.wait(1)