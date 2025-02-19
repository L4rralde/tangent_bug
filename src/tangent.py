import os

import numpy as np

from scene.scenes import Scene, SvgScene, GLUtils, Point

class ParticleSvgScene(SvgScene):
    def __init__(self, title: str, svg: str, max_fps: int) -> None:
        super().__init__(title, svg, max_fps)
        self.particle = Robot(-0.5, 0.5)
        self.free_path_sensor = FreepathSensor(self.grid)
        self.goal = Point(0.5, 0)

    def update(self) -> None:
        super().update()
        if not self.is_blocked():
            self.particle.chace_goal(self.get_free_path(), self.delta_time)

    def render(self) -> None:
        super().render()
        GLUtils.draw_point(self.particle.x, self.particle.y, 4)
        GLUtils.draw_point(self.goal.x, self.goal.y, 4)
        GLUtils.draw_line([self.particle, self.get_free_path()])

    def get_free_path(self) -> np.array:
        #gc: grid coords
        gc_origin = self.to_screen(self.particle)
        gc_goal = self.to_screen(self.goal)
        met = self.free_path_sensor(gc_origin, gc_goal)
        return self.to_ortho(met)

    def is_blocked(self) -> bool:
        gc_origin = self.to_screen(self.particle)
        gc_goal = self.to_screen(self.goal)
        return self.free_path_sensor.is_blocked(gc_origin, gc_goal, 10)


class FreepathSensor:
    def __init__(self, grid: np.array) -> None:
        self.grid = grid

    def __call__(self, gc_origin: Point, gc_goal: Point) -> Point:
        slope = (gc_goal.y - gc_origin.y)/(gc_goal.x - gc_origin.x)
        xs = np.linspace(
            gc_origin.x,
            gc_goal.x,
            int(gc_goal.x - gc_origin.x) + 1
        ).astype('int')
        ys = np.round(gc_origin.y + slope*(xs - gc_origin.x)).astype('int')
        met = gc_goal
        for x, y in zip(xs, ys):
            if self.grid[y, x]:
                met = Point(x, y)
                break
        return met

    def is_blocked(self, gc_origin: Point, gc_goal: Point, min_dist: float = 5) -> bool:
        target = self.__call__(gc_origin, gc_goal)
        return np.linalg.norm(target.coord - gc_origin.coord) < min_dist


class Robot(Point):
    def chace_goal(self, gc_goal: Point, dt: float) -> None:
        d_vector = gc_goal.coord - self.coord
        v_vector = 0.2 * d_vector/np.linalg.norm(d_vector)
        self.update(v_vector, dt)

    def update(self, v_vector: np.array, dt: float) -> None:
        self.x += v_vector[0]*dt
        self.y += v_vector[1]*dt

def main():
    svg_path = '/Users/l4rralde/Desktop/CIMAT/Semestres/Segundo/Robotica/Tareas/Tarea1/media/mundo_free.jpg'
    scene = ParticleSvgScene("Tangent Bug", svg_path, 20)
    scene.run()


if __name__ == '__main__':
    main()
