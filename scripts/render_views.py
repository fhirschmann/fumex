#!/usr/bin/env python3
"""Render documentation images from the current model (skill openscad-print-project).

VIEWS in print_project.py: image name -> (OpenSCAD code, camera "eye_x,eye_y,eye_z,centre_x,centre_y,centre_z"
[, options]). Images go to IMG_DIR (default img/). Uses --render, because the OpenCSG preview shows differences
with imported meshes wrongly.

The images work on light and dark pages (GitHub/Forgejo dark mode): the background is keyed out to transparency,
the scene is rendered `supersample` times larger and scaled down (smooth edges) and gets a soft shadow. OpenSCAD
lights faces by their direction on screen (up bright, left medium, right dark), wherever the camera is: with
light="auto" every view is also rendered mirrored in x and flipped back, which moves the light to the right, and
the brighter image wins. Uncoloured geometry and faces cut by an uncoloured intersection() take the scheme's face
colour (do not wrap a view in color(): an outer color() overrides all inner ones). RENDER in print_project.py overrides the settings, the optional third VIEWS entry overrides them per
view, e.g. {"light": "left"}. Post-processing needs Pillow or ffmpeg; without both the plain opaque render is kept.
"""
import argparse
import shutil
import subprocess

import numpy as np
from scipy import ndimage

from print_tools import BUILD, P, ROOT, SOURCE

try:
    from PIL import Image
except ImportError:
    Image = None

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("names", nargs="*", help="only these views")
args = parser.parse_args()
views = getattr(P, "VIEWS", {})
# DeepOcean: uncoloured geometry and cut faces neutral grey, background (51, 51, 51) keyed out
settings = dict(imgsize="1200,1000", colorscheme="DeepOcean", projection="o", transparent=True, supersample=2,
                light="auto", shadow=0.3) | getattr(P, "RENDER", {})
folder = BUILD / "views"
folder.mkdir(parents=True, exist_ok=True)
target = ROOT / getattr(P, "IMG_DIR", "img")
target.mkdir(exist_ok=True)
openscad = shutil.which("openscad") or "openscad"
ffmpeg = shutil.which("ffmpeg")


def render(name, code, camera, size, out, opts, mirrored=False):
    if mirrored:
        values = camera.split(",")
        camera = ",".join(f"{-float(v):g}" if i in (0, 3) else v for i, v in enumerate(values))
        code = f"mirror([1, 0, 0]) {{ {code} }}"
    wrapper = folder / f"{name}{'_mirrored' if mirrored else ''}.scad"
    wrapper.write_text(f"include <{SOURCE.as_posix()}>\n{code}\n")
    subprocess.run([openscad, "--hardwarnings", "--render", f"--imgsize={size[0]},{size[1]}",
                    f"--colorscheme={opts['colorscheme']}", f"--projection={opts['projection']}", f"--camera={camera}",
                    "--autocenter", "--viewall", "-D", 'part="none"', "-o", str(out), str(wrapper)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def read_rgb(path, size):
    if Image:
        return np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)
    raw = subprocess.run([ffmpeg, "-v", "error", "-i", str(path), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(size[1], size[0], 3).astype(np.float64)


def write_rgba(path, rgba):
    data = np.clip(np.rint(rgba), 0, 255).astype(np.uint8)
    if Image:
        Image.fromarray(data, "RGBA").save(path, optimize=True)
        return
    subprocess.run([ffmpeg, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{data.shape[1]}x{data.shape[0]}",
                    "-i", "-", "-frames:v", "1", "-pix_fmt", "rgba", str(path)], input=data.tobytes(), check=True)


def keyed(rgb, k):
    """Alpha from the background colour (OpenSCAD does not antialias), premultiplied colour scaled down by k."""
    bg = rgb[0, 0]
    assert all((c == bg).all() for c in (rgb[0, -1], rgb[-1, 0], rgb[-1, -1])), "View touches the image corners: background not detectable"
    alpha = (np.abs(rgb - bg).max(-1) > 0).astype(np.float64)
    h, w = alpha.shape[0] // k * k, alpha.shape[1] // k * k
    pre = (rgb * alpha[..., None])[:h, :w].reshape(h // k, k, w // k, k, 3).mean((1, 3))
    return pre, alpha[:h, :w].reshape(h // k, k, w // k, k).mean((1, 3))


for name, (code, camera, *extra) in views.items():
    if args.names and name not in args.names:
        continue
    opts = settings | (extra[0] if extra else {})
    size = [int(v) for v in opts["imgsize"].split(",")]
    if not (opts["transparent"] and (Image or ffmpeg)):
        render(name, code, camera, size, target / f"{name}.png", opts | dict(transparent=False))
        print(name, flush=True)
        continue
    k = int(opts["supersample"])
    big = [s * k for s in size]
    mirrorable = len(camera.split(",")) == 6
    variants = [False, True] if opts["light"] == "auto" and mirrorable else [opts["light"] == "right" and mirrorable]
    best = None
    for mirrored in variants:
        raw = folder / f"{name}{'_mirrored' if mirrored else ''}.png"
        render(name, code, camera, big, raw, opts, mirrored)
        rgb = read_rgb(raw, big)
        pre, alpha = keyed(rgb[:, ::-1] if mirrored else rgb, k)
        brightness = pre.sum() / max(alpha.sum(), 1) / 3
        if best is None or brightness > best[0]:
            best = (brightness, pre, alpha, mirrored)
    _, pre, alpha, mirrored = best
    if opts["shadow"]:   # soft shadow below the object: helps on light pages, disappears on dark ones
        shadow = ndimage.shift(ndimage.gaussian_filter(alpha, size[0] * 0.01), (size[1] * 0.008, 0), order=1) * opts["shadow"]
        total = alpha + shadow * (1 - alpha)
    else:
        total = alpha
    rgb = pre / np.maximum(total, 1e-6)[..., None]
    write_rgba(target / f"{name}.png", np.dstack([rgb, total * 255]))
    print(f"{name}: light from the {'right' if mirrored else 'left'}", flush=True)
