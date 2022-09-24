from manim import *


class VideoTitle(Scene):
    def construct(self):
        title = Text("Résoudre MasterMind", color=BLUE).shift(1 * UP)
        subtitle = Text("Avec la théorie de l'information", color=WHITE).set_opacity(0.8).scale(0.8)
        subtitle.next_to(title, DOWN, buff=0.3)
        self.add(title)
        self.play(Write(subtitle))
        self.wait()


class AnimatedSquareToCircle(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        square = Square()  # create a square

        self.play(Create(square))  # show the square on screen
        self.play(square.animate.rotate(PI / 4))  # rotate the square
        self.play(
            ReplacementTransform(square, circle)
        )  # transform the square into a circle
        self.play(
            circle.animate.set_fill(PINK, opacity=0.5)
        )  # color the circle on screen
