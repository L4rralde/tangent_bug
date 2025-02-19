from flask import Flask, request, jsonify
from threading import Thread

from scenes import Scene, GLUtils, DrawingObstacles
from models import Particle

app = Flask(__name__)
acceleration = {"ax": 0, "ay": 0}
stop = False

@app.route("/set_acceleration", methods=["POST"])
def set_acceleration():
    global acceleration
    try:
        data = request.get_json()
        ax = float(data.get("ax", 0.0))
        ay = float(data.get("ay", 0.0))
        acceleration["ax"] = ax
        acceleration["ay"] = ay
        return jsonify({
            "message": "Acceleration updated",
            "acceleration": acceleration
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/stop", methods=["POST"])
def stop():
    global stop
    global acceleration
    try:
        _ = request.get_json()
        stop = True
        acceleration["ax"] = 0
        acceleration["ay"] = 0
        return jsonify({"message": "Stopped"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

class ParticleScene(DrawingObstacles):
    def __init__(self, title: str, width: int, height: int, max_fps: int) -> None:
        super().__init__(title, width, height, max_fps)
        self.particle = Particle()

    def update(self) -> None:
        global stop
        if stop:
            print("Stop!!!")
            stop = False
            self.particle.stop()
            return

        global acceleration
        self.particle.set_accel(
            acceleration["ax"],
            acceleration["ay"]
        )
        self.particle.update(self.delta_time)

    def render(self) -> None:
        super().render()
        GLUtils.draw_point(self.particle.x, self.particle.y, 5)


def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False)


def main():
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()

    scene = ParticleScene("Particle", 900, 600, 20)
    scene.run()


if __name__ == '__main__':
    main()
