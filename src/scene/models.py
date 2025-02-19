class Particle:
    def __init__(
            self,
            x_spawn: float = 0,
            y_spawn: float = 0,
            bounds: list = [-1, 1, 1, -1]
        ) -> None:
        self.x = x_spawn
        self.y = y_spawn
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0
        self.x_left_lim = bounds[0]
        self.y_upp_lim = bounds[1]
        self.x_right_lim = bounds[2]
        self.y_low_lim = bounds[3]

    def set_accel(self, ax: float, ay: float) -> None:
        self.ax = ax
        self.ay = ay

    def get_pos(self) -> tuple:
        return self.x, self.y

    def update(self, dt: float) -> None:
        self.x += self.vx*dt + 0.5*self.ax*dt*dt
        self.vx += self.ax*dt
        self.y += self.vy*dt + 0.5*self.ay*dt*dt
        self.vy += self.ay*dt

        if self.x < self.x_left_lim or self.x > self.x_right_lim:
            self.vx *= -1
        if self.y < self.y_low_lim or self.y > self.y_upp_lim:
            self.vy *= -1

        self.x = max(self.x_left_lim, min(self.x, self.x_right_lim))
        self.y = max(self.y_low_lim, min(self.y, self.y_upp_lim))

    def stop(self) -> None:
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0
