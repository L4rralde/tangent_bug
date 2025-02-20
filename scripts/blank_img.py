#!/usr/bin/env python3
"""
Generates a blank image with same dimensions as another one.
Author: Emmanuel Larralde
"""

from subprocess import check_output

from PIL import Image
import numpy as np


git_root_cmd = check_output("git rev-parse --show-toplevel".split())
GIT_ROOT = git_root_cmd.rstrip().decode()


def main():
    src = f"{GIT_ROOT}/media/mundo_free.jpg"
    dst = f"{GIT_ROOT}/media/blank.jpg"
    img = np.asarray(Image.open(src))
    blank = np.ones_like(img)
    blank_img = Image.fromarray(255 * blank)
    blank_img.save(dst)


if __name__ == '__main__':
    main()
