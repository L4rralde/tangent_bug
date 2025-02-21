# TangentBug

[![video](https://img.youtube.com/vi/KXCm3vgtcbM/0.jpg)](https://www.youtube.com/watch?v=KXCm3vgtcbM)


## Sobre el software

El simulador se programó usando python. La ventana principal es manejada por `pygame`, pero el renderizado se logra através de instrucciones de `OpenGL`. Los algoritmos de visión y la visualización de la imágen de la cámara se logra a través de `OpenCV`.

### Instalación

1. Clona el repositorio:

```sh
git clone https://github.com/L4rralde/tangent_bug.git
cd tangent_bug
```

2. (Opcional) Usa un ambiente virtual de python

```sh
python -m venv .venv
source .venv/bin/activate
```

3. Instala las dependencias

```sh
pip intstall -r requirements.txt
```

### Uso

Revisando una porción del código:

```python
def main():
    svg_path = f"{GIT_ROOT}/media/mundo_circ.jpg"
    origin = Robot(-0.7, 0.5)
    goal = Point(0.45, 0.35)
    scene = ParticleSvgScene("Tangent Bug", svg_path, 20, origin, goal)
    scene.run()
```

- Modifica `svg_path` si quieres usar ontro ambiente, en el directorio `media/` encontrarás varias imágenes `*.jpg` que funcionan como ambientes.

- Modifica las coordenadas en `Robot()` si quieres modificar la posición original del robot.

- Modifica las coordenadas en `goal = Point()` si quieres modificar las coordenadas de la meta.

Estas coordenadas están normalizadas, i.e., $x \in [-1, 1]$, $y \in [-1, 1]$.

