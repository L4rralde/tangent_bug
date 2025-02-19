import sys

import pygame
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from PIL import Image


class Point:
    def __init__(self, x: int, y: int) -> None:
        self.coord = np.array([x, y])

    @property
    def x(self) -> float:
        return self.coord[0]
    
    @x.setter
    def x(self, value: float) -> None:
        self.coord[0] = value

    @property
    def y(self) -> float:
        return self.coord[1]
    
    @y.setter
    def y(self, value: float) -> None:
        self.coord[1] = value

    def __eq__(self, other: object) -> bool:
        return self.coord == other.coord

    def __str__(self) -> str:
        return f"(x:{self.x}, y:{self.y}) "

class Line:
    def __init__(self) -> None:
        self.points = []

    def __str__(self) -> str:
        return " ".join([str(pt) for pt in self.points])

    def append(self, new_point: Point) -> None:
        if self.points and self.points[-1] == new_point:
            return
        self.points.append(new_point)

class Loop(Line):
    def __init__(self) -> None:
        super().__init__()
        self.looped = False

    def is_loop(self) -> bool:
        if not self.points:
            return False
        if self.looped:
            return True
        self.looped = self.points[-1] in self.points[:-1]
        return self.looped

class Scene:
    def __init__(self, title: str, width: int, height: int, max_fps: int) -> None:
        self.title = title
        self.max_fps = max_fps
        self.screen_width = width
        self.screen_height = height
        pygame.init()
        self.display = pygame.display.set_mode(
            (width, height),
            DOUBLEBUF | OPENGL
        )
        self.clock = pygame.time.Clock()

    def run(self) -> None:
        self.setup()
        while True:
            self.events = pygame.event.get()
            for event in self.events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            self.delta_time = self.clock.tick(self.max_fps)/1000
            self.get_inputs()
            self.update()
            self.render()

            pygame.display.flip()
            pygame.display.set_caption(
                f"{self.title} ({self.clock.get_fps():.2f} fps)"
            )
    
    def setup(self) -> None:
        GLUtils.init_ortho(-1, 1, 1, -1)

    def get_inputs(self) -> None:
        pass

    def update(self) -> None:
        pass

    def render(self) -> None:
        GLUtils.prepare_render()

    def to_ortho(self, point: Point) -> Point:
        new_point = Point(
            (2*point.x - self.screen_width)/self.screen_width,
            (2*point.y - self.screen_height)/self.screen_height
        )
        return new_point

    def to_screen(self, point: Point) -> Point:
        new_point = Point(
            (self.screen_width * (point.x + 1))//2,
            (self.screen_height * (point.y + 1))//2
        )
        return new_point


class GLUtils:
    @staticmethod
    def init_ortho(left: int, right: int, top: int, bottom: int) -> None:
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(left, right, top, bottom)

    @staticmethod
    def prepare_render() -> None:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    @staticmethod
    def draw_point(x: int, y: int, size: int) -> None:
        glColor(1.0, 1.0, 1.0, 1.0)
        glPointSize(size)
        glBegin(GL_POINTS)
        glVertex2f(x, y)
        glEnd()

    @staticmethod
    def draw_graph() -> None:
        glPointSize(2)
        glBegin(GL_POINTS)
        for px in np.arange(0, 15, 0.025):
            glColor3f(0, 0, 255)
            glVertex2f(px, np.sin(px))
            glColor3f(0, 255, 0)
            glVertex2f(px, np.cos(px))
        glEnd()

    @staticmethod
    def draw_points(points: list) -> None:
        glColor(0.5, 0.0, 0.0, 1)
        glPointSize(5)
        glBegin(GL_POINTS)
        for point in points:
            glVertex2f(point.x, point.y)
        glEnd()

    @staticmethod
    def draw_line(points: list) -> None:
        glPointSize(1)
        glBegin(GL_LINE_STRIP)
        for point in points:
            glVertex2f(point.x, point.y)
        glEnd()

    @staticmethod
    def draw_lines(lines: list) -> None:
        glPointSize(1)
        for line in lines:
            GLUtils.draw_line(line.points)

    @staticmethod
    def draw_polygon(points: list, draw_points = True) -> None:
        glColor(0.1, 0.1, 0.2, 1)
        glPointSize(1)
        glBegin(GL_TRIANGLE_FAN)
        for point in points:
            glVertex2f(point.x, point.y)
        glEnd()
        if draw_points:
            GLUtils.draw_points(points)


class SvgScene(Scene):
    def __init__(self, title: str, svg: str, max_fps: int) -> None:
        image = Image.open(svg)
        h, w = image.size
        image = np.asarray(image.resize((h//5, w//5)))
        h, w = image.shape
        super().__init__(title, w, h, max_fps)
        xs, ys = np.where(image == 0)
        self.grid = image==0
        self.contours = [
            self.to_ortho(Point(y, x))
            for x,y in zip(xs, ys)
        ]

    def render(self) -> None:
        super().render()
        GLUtils.draw_points(self.contours)


class GLScene(Scene):
    def setup(self) -> None:
        GLUtils.init_ortho(0, 15, -1.5, 1.5)

    def render(self) -> None:
        GLUtils.prepare_render()


class DrawingScene(Scene):
    def __init__(self, title: str, width: int, height: int, max_fps: int) -> None:
        super().__init__(title, width, height, max_fps)
        self.points = []

    def get_inputs(self) -> None:
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                print("Mouse clickled")
                x, y = pygame.mouse.get_pos()
                screen_point = Point(x, y)
                ortho_point = self.to_ortho(screen_point)
                self.points.append(ortho_point)

    def render(self) -> None:
        super().render()
        GLUtils.draw_points(self.points)
        GLUtils.draw_line(self.points)


class DrawingObstacles(Scene): #To be renamed
    def __init__(self, title: str, width: int, height: int, max_fps: int) -> None:
        super().__init__(title, width, height, max_fps)
        self.obstacles = []
        self.mouse_down = False

    def get_inputs(self) -> None:
        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down = True
                self.obstacles.append(Loop())
                print("Staring a new line")
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_down = False
                print("Finishing last line")
                current_obstacle = self.obstacles[-1]
                if not current_obstacle.is_loop():
                    self.obstacles.pop()
            elif event.type == pygame.MOUSEMOTION and self.mouse_down:
                x, y = pygame.mouse.get_pos()
                screen_point = Point(x, y)
                ortho_point = self.to_ortho(screen_point)
                current_obstacle = self.obstacles[-1]
                self.obstacles[-1].append(ortho_point)
                if current_obstacle.is_loop():
                    print("Found loop")
                    self.mouse_down = False

    def render(self) -> None:
        super().render()
        if not self.obstacles:
            return
        for obstacle in self.obstacles:
            GLUtils.draw_polygon(obstacle.points, not obstacle.looped)

if __name__ == '__main__':
    scene = DrawingObstacles("OpenGL", 900, 600, 20)
    scene.run()
