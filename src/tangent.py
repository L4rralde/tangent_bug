#!/usr/bin/env python3
"""
Simulation of the tangent bug algorithm
Author: Emmanuel Larralde
"""

from subprocess import check_output

import numpy as np
import cv2

from scene.scenes import Scene, SvgScene, GLUtils, Point


git_root_cmd = check_output("git rev-parse --show-toplevel".split())
GIT_ROOT = git_root_cmd.rstrip().decode()


class ParticleSvgScene(SvgScene):
    """
    Simulation Scence from an SVG image and with a Particle-like robot
    """
    def __init__(self, title: str, svg: str, max_fps: int, origin: Point, goal: Point) -> None:
        super().__init__(title, svg, max_fps)
        #Normalized coords = [(-1, -1), (1, 1)]
        self.robot = origin #Initial position of the robot in normalized coords.
        self.free_path_sensor = FreepathSensor(self.grid)
        self.goal = goal #Position of the goal in normalized coords.
        self.vision = Perception(self.grid) #Computer vision sensor
        self._state = "CHASE"
        self.prev_vx, self.prev_vy = 0, 0 #Latest saved speed. Used to keep the direction.
        self.best_distance = -1 #Used to track point to leave boundary following

    def update(self) -> None:
        """
        Updates data used to render simulation.
        """
        super().update()
        if self._state == "CHASE" and not self.is_blocked():
            self.chase_goal()
        else:
            self.boundary_following()

    def render(self) -> None:
        """
        Renders the simulation
        """
        super().render()
        GLUtils.draw_point(self.robot.x, self.robot.y, 4) #Draws the robot
        GLUtils.draw_point(self.goal.x, self.goal.y, 4) #Draws goal
        GLUtils.draw_line([self.robot, self.get_free_path()]) #Draws free path

    def get_free_path(self) -> np.array:
        """
        Get collision free path from robot to goal
        """
        #gc: grid coords
        gc_origin = self.to_screen(self.robot)
        gc_goal = self.to_screen(self.goal)
        met = self.free_path_sensor(gc_origin, gc_goal)
        return self.to_ortho(met)

    def is_blocked(self) -> bool:
        """
        Checks if the free path is blocked
        """
        gc_origin = self.to_screen(self.robot)
        gc_goal = self.to_screen(self.goal)
        return self.free_path_sensor.is_blocked(gc_origin, gc_goal, 10)

    def chase_goal(self) -> None:
        """
        Makes the robot follow the free path
        """
        #Converting normalized coords to image coords.
        #cv sensor and algorithms work on image coords.
        robot_pos_screen = self.to_screen(self.robot)
        self.best_distance = -1
        self.vision(robot_pos_screen) #Displays image captured by cv sensor
        d_vector = self.get_free_path().coord - self.robot.coord #Compute vector to follow
        self.robot.update(d_vector, self.delta_time, 0.1) #Make the robot follow the vector

    def boundary_following(self) -> None:
        """
        Make the robot follow a boundary
        """
        #Convert normalized coords to image coords
        robot_pos_screen = self.to_screen(self.robot)
        distance_to_goal = np.linalg.norm(self.robot.coord - self.goal.coord)
        if self.best_distance == -1: #Check if it is the first time met this boundary
            self.best_distance = distance_to_goal
        self._state = "FOLLOWING"
        img = self.vision.get_img(robot_pos_screen) #Gets cv sensor imagge
        edges = self.vision.canny(img)
        edge_display = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        
        points = np.column_stack(np.where(edges > 0))
        if len(points) == 0: #Check if there are points for the algorithm
            return
        #Computes the direction of the edges of the boundary
        [vx, vy, x0, y0] = cv2.fitLine(points, cv2.DIST_L2, 0, 0.01, 0.01)
        x0 = int(x0[0])
        y0 = int(y0[0])
        
        #Check if the current direction makes sense
        dot_product = self.prev_vx * vx + self.prev_vy * vy
        if dot_product < 0:  
            vx, vy = -vx, -vy

        # Update previous direction
        self.prev_vx, self.prev_vy = vx, vy

        x1, y1 = int(x0 + vx * 20), int(y0 + vy * 20)
        #Displays the boundary and its vector
        cv2.arrowedLine(edge_display, [y0, x0], [y1, x1], (0, 0, 255), 1, tipLength=0.3)

        #Computes vector to keep distance to boundary
        c0 = self.vision.len
        distance_to_boundary = np.linalg.norm([x0 - c0, y0 - c0])
        x1_p, y1_p = int(x0 + vy * 20), int(y0 - vx *20)
        #Draw distance to boundary vector
        cv2.arrowedLine(edge_display, [y0, x0], [y1_p, x1_p], (0, 0, 255), 1, tipLength=0.3)
        #Adjusts robot velocity vector if too close to boundary
        if distance_to_boundary < 5:
            vx += 0.2*vy
            vy += -0.2*vx

        #Adjusts effect of normalized coords on (image coords) vectors.
        scale = self.screen_width/self.screen_height
        #Make the robot folow the computed speed vector
        self.robot.update(np.array([vy, scale*vx]), self.delta_time, 0.1)
        #Show visual results of the cv algorithm
        self.vision.imshow(edge_display)
        #Check if the robot must stop boundary following
        if not self.is_blocked() and distance_to_goal < self.best_distance:
            print("back to chase")
            self._state = "CHASE"


class FreepathSensor:
    """
    Sensor which computes the nearest collision free path
    aligned to goal.
    """
    def __init__(self, grid: np.array) -> None:
        self.grid = grid

    def __call__(self, gc_origin: Point, gc_goal: Point) -> Point:
        """
        Returns, within the path from origin to goal, the closest
        collision-free point to goal.
        """
        slope = (gc_goal.y - gc_origin.y)/(gc_goal.x - gc_origin.x + 1e-8)
        xs = np.linspace(
            gc_origin.x,
            gc_goal.x,
            int(abs(gc_goal.x - gc_origin.x)) + 1
        ).astype('int')
        ys = np.round(gc_origin.y + slope*(xs - gc_origin.x)).astype('int')
        met = gc_goal
        for x, y in zip(xs, ys):
            if self.grid[y, x]:
                met = Point(x, y)
                break
        return met

    def is_blocked(self, gc_origin: Point, gc_goal: Point, min_dist: float = 10) -> bool:
        """
        Check if it is not possible to chase the goal.
        """
        target = self.__call__(gc_origin, gc_goal)
        return np.linalg.norm(target.coord - gc_origin.coord) < min_dist


class Robot(Point):
    """
    Movable point-like robot with constant (given) speed
    """
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y)
    
    def update(self, v_vector: np.array, dt: float, speed: float) -> None:
        """
        Updates the position of the robot given a vector and constant speed.
        """
        v_vector_norm = speed * v_vector/np.linalg.norm(v_vector)
        self.x += v_vector_norm[0]*dt
        self.y += v_vector_norm[1]*dt


class Perception:
    """
    Computer Vision sensor
    """
    def __init__(self, grid: np.array, len: int = 20) -> None:
        self.grid = grid #Grid of the scence
        self.len = len #lenght of the image captured
        self.h, self.w = grid.shape

    def get_img(self, pos: Point) -> np.array:
        """
        Returns the image captured by the sensor
        """
        minx = max(0, pos.x - self.len)
        maxx = min(self.w, pos.x + self.len)
        miny = max(0, pos.y - self.len)
        maxy = min(self.h, pos.y + self.len)
        sub_img = self.grid[
            miny: maxy,
            minx: maxx
        ]
        cv2_sub_img = 255*np.asarray(sub_img).astype('uint8')
        return cv2_sub_img

    def imshow(self, img: np.array, s: int=40) -> np.array:
        """
        Shows the image on a new window.
        """
        resized = cv2.resize(img, (s*self.len, s*self.len))
        cv2.imshow("img", resized)
        cv2.waitKey(1)

    def __call__(self, pos: Point) -> None:
        """
        Gets and display image
        """
        img = self.get_img(pos)
        self.imshow(img)

    def canny(self, img: np.array) -> np.array:
        """
        Canny edge detection
        """
        return cv2.Canny(img, 50, 150)


def main():
    svg_path = f"{GIT_ROOT}/media/mundo_circ.jpg"
    origin = Robot(-0.7, 0.5)
    goal = Point(0.45, 0.35)
    scene = ParticleSvgScene("Tangent Bug", svg_path, 20, origin, goal)
    scene.run()


if __name__ == '__main__':
    main()
