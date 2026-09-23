#!/usr/bin/env python3
"""Round features from OpenSCAD CSG dumps and their alignment across assembly bodies (skill openscad-print-project).

`openscad -o body.csg` writes the evaluated tree before any boolean: every transform is a multmatrix and a
hole is still a cylinder (or a circle in a linear_extrude) with its diameter. print_tools.py exports one dump
per assembly body; align() then finds round features of two bodies that are parallel and overlap along
their axis but sit slightly off axis (screw hole next to its insert hole, shaft next to its bore).

Limits: cylinders under hull/minkowski/offset/resize/rotate_extrude are ignored (rounded corners, fillets),
as are cones, elliptical or sheared cylinders, scaled or twisted extrusions and stubs shorter than 5 % of
their diameter. The sign follows difference() only; intersection() keeps the sign of its children.

  python3 scripts/holes.py build/assembly/back.csg build/assembly/body.csg   features and alignment
"""
import ast
import itertools
import json
from pathlib import Path
import re
import sys

import numpy as np

MASKED = {"hull", "minkowski", "offset", "resize", "rotate_extrude", "projection", "roof", "skin"}
PASS_THROUGH = {"group", "union", "intersection", "render", "color"}
NAME = re.compile(r"[A-Za-z_$][\w$]*")


def parse(text):
    """CSG text -> nested list of (modifier, name, args, children)."""
    pos, size = 0, len(text)

    def skip():
        nonlocal pos
        while pos < size:
            if text[pos] in " \t\r\n":
                pos += 1
            elif text.startswith("//", pos):
                pos = text.find("\n", pos) if "\n" in text[pos:] else size
            else:
                break

    def arguments():
        nonlocal pos
        depth, start, quoted = 0, pos + 1, False
        while pos < size:
            ch = text[pos]
            if quoted:
                if ch == "\\":
                    pos += 1
                elif ch == '"':
                    quoted = False
            elif ch == '"':
                quoted = True
            elif ch in "([":
                depth += 1
            elif ch in ")]":
                depth -= 1
                if depth == 0:
                    pos += 1
                    return text[start:pos - 1]
            pos += 1
        raise ValueError("Unterminated argument list in CSG dump")

    def nodes(closing):
        nonlocal pos
        out = []
        while True:
            skip()
            if pos >= size:
                if closing:
                    raise ValueError("Unterminated block in CSG dump")
                return out
            if text[pos] == "}":
                pos += 1
                return out
            modifier = ""
            while text[pos] in "%*#!":
                modifier += text[pos]
                pos += 1
            match = NAME.match(text, pos)
            if not match:
                raise ValueError(f"Unexpected CSG text at {pos}: {text[pos:pos + 40]!r}")
            pos = match.end()
            skip()
            args = arguments() if pos < size and text[pos] == "(" else ""
            skip()
            children = []
            if pos < size and text[pos] == "{":
                pos += 1
                children = nodes(True)
            elif pos < size and text[pos] == ";":
                pos += 1
            out.append((modifier, match.group(), args, children))

    return nodes(False)


def split_top(text):
    parts, depth, quoted, start, i = [], 0, False, 0, 0
    while i < len(text):
        ch = text[i]
        if quoted:
            if ch == "\\":
                i += 1
            elif ch == '"':
                quoted = False
        elif ch == '"':
            quoted = True
        elif ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(text[start:i])
            start = i + 1
        i += 1
    parts.append(text[start:])
    return [p.strip() for p in parts if p.strip()]


def value(text):
    text = text.strip()
    if text in ("true", "false"):
        return text == "true"
    try:
        return float(text)
    except ValueError:
        pass
    if text.startswith("["):
        try:
            return ast.literal_eval(re.sub(r"\btrue\b", "True", re.sub(r"\bfalse\b", "False", text)))
        except (ValueError, SyntaxError):
            return text
    return text


def kwargs(args):
    out = {}
    for i, part in enumerate(split_top(args)):
        key, sep, rest = part.partition("=")
        if sep and NAME.fullmatch(key.strip()):
            out[key.strip()] = value(rest)
        else:
            out[i] = value(part)
    return out


def features(tree):
    """Round features in the dump frame: dicts with d, p0, p1 (axis end points) and sign (+1 solid, -1 hole)."""
    found = []

    def add(m, centre, z0, z1, radius, sign):
        p0 = m @ np.array([centre[0], centre[1], z0, 1.0])
        p1 = m @ np.array([centre[0], centre[1], z1, 1.0])
        axis = p1[:3] - p0[:3]
        length = float(np.linalg.norm(axis))
        ex, ey = m[:3, 0], m[:3, 1]
        sx, sy = float(np.linalg.norm(ex)), float(np.linalg.norm(ey))
        if length < 1e-9 or sx < 1e-9:
            return
        u = axis / length
        tol = 1e-6 * max(1.0, sx)
        if abs(sx - sy) > tol or abs(ex @ ey) > tol * sx or abs(ex @ u) > tol or abs(ey @ u) > tol:
            return          # elliptical or sheared
        d = 2 * radius * sx
        if d > 0 and length >= 0.05 * d:
            found.append(dict(d=round(d, 4), p0=p0[:3].round(4).tolist(), p1=p1[:3].round(4).tolist(), sign=sign))

    def walk(nodes, m, sign, extrude):
        for modifier, name, args, children in nodes:
            if "%" in modifier or "*" in modifier or name in MASKED:
                continue
            if name == "multmatrix":
                walk(children, m @ np.array(kwargs(args)[0], dtype=float), sign, extrude)
            elif name == "difference":
                walk(children[:1], m, sign, extrude)
                walk(children[1:], m, -sign, extrude)
            elif name in PASS_THROUGH:
                walk(children, m, sign, extrude)
            elif name == "linear_extrude" and extrude is None:
                kw = kwargs(args)
                height = kw.get("height")
                if isinstance(kw.get("v"), list):
                    vx, vy, vz = kw["v"]
                    height = vz if abs(vx) < 1e-9 and abs(vy) < 1e-9 else None
                scale = kw.get("scale", 1.0)
                scale = scale if isinstance(scale, list) else [scale, scale]
                if not isinstance(height, float) or kw.get("twist", 0.0) or any(abs(s - 1) > 1e-9 for s in scale):
                    continue
                z0, z1 = (-height / 2, height / 2) if kw.get("center") is True else (0.0, height)
                walk(children, np.eye(4), sign, (m, z0, z1))
            elif name == "cylinder" and extrude is None:
                kw = kwargs(args)
                if abs(kw["r1"] - kw["r2"]) <= 1e-6:
                    z0, z1 = (-kw["h"] / 2, kw["h"] / 2) if kw.get("center") is True else (0.0, kw["h"])
                    add(m, (0.0, 0.0), z0, z1, kw["r1"], sign)
            elif name == "circle" and extrude is not None:
                outer, z0, z1 = extrude
                ex, ey = m[:2, 0], m[:2, 1]
                sx, sy = float(np.linalg.norm(ex)), float(np.linalg.norm(ey))
                if abs(sx - sy) <= 1e-6 * max(1.0, sx) and abs(ex @ ey) <= 1e-6 * max(1.0, sx):
                    centre = m @ np.array([0.0, 0.0, 0.0, 1.0])
                    add(outer, centre[:2], z0, z1, kwargs(args)["r"] * sx, sign)
            # cube, sphere, polyhedron, square, polygon, text, import, surface: no round feature

    walk(tree, np.eye(4), 1, None)
    return found


def load(path):
    return features(parse(Path(path).read_text()))


def align(bodies, tolerance=0.2, near_miss=2.0, allowed=()):
    """Pairs of round features from different bodies, at least one of them a hole, parallel and overlapping
    along the axis (within near_miss): coaxial within tolerance, misaligned between tolerance and near_miss."""
    allowed = {frozenset(pair) for pair in allowed}
    items = [(body, f) for body, found in bodies.items() for f in found]
    if not items:
        return dict(features=0, coaxial_pairs={}, misaligned=[], allowed_misaligned=0)
    body = np.array([b for b, _ in items])
    p0 = np.array([f["p0"] for _, f in items])
    p1 = np.array([f["p1"] for _, f in items])
    hole = np.array([f["sign"] < 0 for _, f in items])
    u = (p1 - p0) / np.linalg.norm(p1 - p0, axis=1)[:, None]
    parallel = np.abs(u @ u.T) >= np.cos(np.radians(0.5))
    candidate = parallel & (body[:, None] != body[None, :]) & (hole[:, None] | hole[None, :])
    candidate &= np.triu(np.ones_like(candidate), 1).astype(bool)
    coaxial, misaligned, skipped = {}, [], 0
    for i, j in zip(*np.nonzero(candidate)):
        w = p0[j] - p0[i]
        offset = float(np.linalg.norm(w - (w @ u[i]) * u[i]))
        if offset > near_miss:
            continue
        a0, a1 = sorted((p0[i] @ u[i], p1[i] @ u[i]))
        b0, b1 = sorted((p0[j] @ u[i], p1[j] @ u[i]))
        if b0 > a1 + near_miss or a0 > b1 + near_miss:
            continue
        pair = frozenset((body[i], body[j]))
        if offset <= tolerance:
            key = "|".join(sorted(pair))
            coaxial[key] = coaxial.get(key, 0) + 1
        elif pair in allowed:
            skipped += 1
        else:
            fi, fj = items[i][1], items[j][1]
            misaligned.append(dict(a=str(body[i]), a_d=fi["d"], a_hole=bool(hole[i]), b=str(body[j]), b_d=fj["d"],
                                   b_hole=bool(hole[j]), offset_mm=round(offset, 3),
                                   at=((p0[i] + p1[i]) / 2).round(2).tolist()))
    misaligned.sort(key=lambda row: row["offset_mm"])
    return dict(features=len(items), coaxial_pairs=dict(sorted(coaxial.items())), misaligned=misaligned,
                allowed_misaligned=skipped)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    bodies = {Path(name).stem: load(name) for name in sys.argv[1:]}
    for name, found in bodies.items():
        holes = sum(f["sign"] < 0 for f in found)
        print(f"{name}: {len(found)} round features, {holes} holes")
        for f in found:
            print(f"  {'hole ' if f['sign'] < 0 else 'solid'} d {f['d']:g}  {f['p0']} -> {f['p1']}")
    if len(bodies) > 1:
        print(json.dumps(align(bodies), indent=2))


if __name__ == "__main__":
    main()
