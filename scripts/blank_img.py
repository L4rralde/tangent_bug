from PIL import Image
import numpy as np


def main():
    src = "/Users/l4rralde/Desktop/CIMAT/Semestres/Segundo/Robotica/Tareas/Tarea1/media/mundo_free.jpg"
    dst = "/Users/l4rralde/Desktop/CIMAT/Semestres/Segundo/Robotica/Tareas/Tarea1/media/blank.jpg"
    img = np.asarray(Image.open(src))
    blank = np.ones_like(img)
    blank_img = Image.fromarray(255 * blank)
    blank_img.save(dst)


if __name__ == '__main__':
    main()
