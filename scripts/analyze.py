#!/usr/bin/env python3
"""Printability analysis of exported print meshes (skill openscad-print-project).

  islands  regions that start in mid-air: a layer component without overlap with the layer below
           (the slicer calls them "floating regions"; they need support or a design change)
  ridges   webs and lines narrower than --min-width in cross-sections at --z (default 0.4 mm, i.e.
           inside engravings that are open to the bed); tiny components below --ignore-area are skipped
  inlays   multicolour inlay pieces on their first layer (bed or a face higher up): bodies, area and features narrower than --min-width
  overhangs  areas of a layer steeper than 45 degrees over the layer below (bridges, rebates and grooves in the
           bed face, cantilevers), larger than --min-area (default 100 mm2) and wider than --min-span (default
           2 mm, narrower strips are short bridges over grooves); --max-z limits the height
  fins     slender free-standing towers: layer components thin in every direction (inscribed width below
           --min-width, default 2 mm) that run --min-height or more (default 4 mm) and then end in a free tip.
           A slender run that merges back into a solid cross-section is braced at both ends (the webs between
           intake slots, the legs of a bridged loop) and is not reported; a thin wall inside a larger
           cross-section is thickness's job. These break off when handled and thickness cannot see them:
           it passes anything at or above --min-width and never looks at how far a feature stands unbraced
  thickness  wall thickness along the inward normal at random surface points (one per --density mm2): percentiles
           per part and regions thinner than --min-width (default 1.2 mm, three perimeters) larger than --min-area
           (default 2 mm2) and wider than --min-span (default 2 mm; narrower strips are edges and chamfer tips)

Without names all print parts (islands, ridges) or all multicolour pieces (inlays) are analysed.
Reads build/print and build/color (run print_tools.py build first); --committed reads the STL folders.
Exit code 1 when anything is found, so a clean run can be used as a gate. Report: build/analysis/<command>.json
"""
import argparse
import json
import sys

import manifold3d as md
import numpy as np
import trimesh

from print_tools import BUILD, COLOR_DIR, COLOR_PIECES, PARTS, STL_DIR, manifold

RAY_CHUNK = 10000       # thickness: rays per intersection query


def load(name, committed):
    color = name in COLOR_PIECES
    folder = (COLOR_DIR if color else STL_DIR) if committed else BUILD / ("color" if color else "print")
    mesh = trimesh.load_mesh(folder / f"{name}.stl")
    return mesh, manifold(mesh)


def box(section):
    return [round(v, 2) for v in section.bounds()]


def islands(mesh, solid, layer, min_area):
    found = []
    top = float(mesh.bounds[1, 2])
    below = solid.slice(layer / 2)
    for k in range(1, int(np.ceil(top / layer))):
        z = (k + 0.5) * layer
        section = solid.slice(z)
        for piece in section.decompose():
            area = piece.area()
            if area >= min_area and (piece ^ below).area() < 0.01:
                found.append(dict(z_mm=round(z, 3), area_mm2=round(area, 3), bounds_xy=box(piece)))
        below = section
    return found


def overhangs(mesh, solid, layer, min_area, max_z, min_span=2.0):
    found = []
    top = min(float(mesh.bounds[1, 2]), max_z or float("inf"))
    below = solid.slice(layer / 2)
    for k in range(1, int(np.ceil(top / layer))):
        z = (k + 0.5) * layer
        section = solid.slice(z)
        supported = below.offset(layer, md.JoinType.Miter)    # 45 degrees per layer
        unsupported = section - supported
        if min_span:   # drop strips narrower than min_span: short bridges over engravings and slots print fine
            unsupported = unsupported.offset(-min_span / 2, md.JoinType.Miter).offset(min_span / 2, md.JoinType.Miter)
        for piece in unsupported.decompose():
            if piece.area() >= min_area:
                found.append(dict(z_mm=round(z, 3), area_mm2=round(piece.area(), 1), bounds_xy=box(piece)))
        below = section
    return found


def thin(section, width, ignore_area, min_area):
    found = []
    radius = width / 2 - 0.01          # a web of exactly the minimum width passes
    for piece in section.decompose():
        if piece.area() < ignore_area:
            continue
        opened = piece.offset(-radius, md.JoinType.Miter).offset(radius, md.JoinType.Miter)
        for sliver in (piece - opened).decompose():
            if sliver.area() >= min_area:
                found.append(dict(area_mm2=round(sliver.area(), 3), bounds_xy=box(sliver)))
    return found


def fins(mesh, solid, layer, min_width, min_area, min_height):
    """Slender towers with a free tip, layer by layer. Slender = the component's inscribed circle is below
    min_width, so it is thin in every direction, not just across one wall. A run is reported when it ends
    without a solid cross-section overlapping it, i.e. nothing braces its far end."""
    top = float(mesh.bounds[1, 2])
    radius = min_width / 2 - 0.01          # a tower of exactly the minimum width passes

    def slender(piece):
        x0, y0, x1, y1 = piece.bounds()
        return (min(x1 - x0, y1 - y0) < min_width          # cheap reject before the offset
                and piece.offset(-radius, md.JoinType.Round).area() < 0.01)

    def over(bounds, pieces):
        x0, y0, x1, y1 = bounds
        return [p for p in pieces if p.bounds()[0] < x1 and p.bounds()[2] > x0
                and p.bounds()[1] < y1 and p.bounds()[3] > y0]

    def close(run, braced):
        height = run["z1"] - run["z0"] + layer
        if not braced and height >= min_height:
            found.append(dict(height_mm=round(height, 2), **run))

    found, runs = [], []
    for k in range(int(np.ceil(top / layer))):
        z = (k + 0.5) * layer
        pieces = [p for p in solid.slice(z).decompose() if p.area() >= min_area]
        carried = []
        for piece in [p for p in pieces if slender(p)]:
            run = next((r for r in runs if over(r["bounds_xy"], [piece])), None)
            if run:
                runs.remove(run)
                run.update(z1=round(z, 3), bounds_xy=box(piece), area_mm2=round(piece.area(), 3))
            else:
                run = dict(z0=round(z, 3), z1=round(z, 3), bounds_xy=box(piece), area_mm2=round(piece.area(), 3))
            carried.append(run)
        for run in runs:                   # the tower stopped below this layer
            close(run, braced=any(not slender(p) for p in over(run["bounds_xy"], pieces)))
        runs = carried
    for run in runs:                       # still standing at the top face: a free tip by definition
        close(run, braced=False)
    return found


def thickness(mesh, min_width, density, min_area, min_span=2.0, edge_angle=30):
    """Distance from a surface point along the inward normal to the next face turned away from the ray.
    The single minimum is often a tessellation sliver, so percentiles and connected thin regions are reported.
    Points closer than min_span to a convex edge sharper than edge_angle (degrees) are skipped (min_span 0 skips none): next to a ridge crest, chamfer tip or letter
    edge the depth runs to zero without being a wall (ridges and inlays cover those)."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    from scipy.spatial import cKDTree
    count = int(np.clip(mesh.area / density, 2000, 100000))
    spacing = np.sqrt(mesh.area / count)
    points, faces = trimesh.sample.sample_surface(mesh, count, seed=1)
    inward = -mesh.face_normals[faces]
    origins = points + inward * 1e-4
    depth = np.full(count, np.inf)
    for start in range(0, count, RAY_CHUNK):    # in chunks: a grille or lattice returns many hits per ray, all rays at once run out of memory
        stop = min(start + RAY_CHUNK, count)
        origin, direction = origins[start:stop], inward[start:stop]
        tri, ray, hits = mesh.ray.intersects_id(origin, direction, multiple_hits=True, return_locations=True)
        along = np.einsum("ij,ij->i", hits - origin[ray], direction[ray])
        exits = (np.einsum("ij,ij->i", mesh.face_normals[tri], direction[ray]) > 0) & (along > 0)
        np.minimum.at(depth, ray[exits] + start, along[exits] + 1e-4)
    measured = depth[np.isfinite(depth)]
    stats = dict(samples=count, measured=len(measured), mm2_per_sample=round(float(mesh.area / count), 3),
                 **{key: round(float(np.percentile(measured, q)), 3) for key, q in (("p01", 1), ("p05", 5), ("median", 50))})
    thin = np.nonzero(depth < min_width - 0.01)[0]          # a wall of exactly the minimum passes
    sharp = mesh.face_adjacency_edges[(mesh.face_adjacency_angles > np.radians(edge_angle)) & mesh.face_adjacency_convex]
    if len(thin) and len(sharp) and min_span > 0:
        a, b = mesh.vertices[sharp[:, 0]], mesh.vertices[sharp[:, 1]]
        steps = np.maximum(1, np.ceil(np.linalg.norm(b - a, axis=1) / (min(min_width, min_span) / 4))).astype(int)
        index = np.repeat(np.arange(len(sharp)), steps + 1)
        t = np.concatenate([np.linspace(0, 1, n + 1) for n in steps])
        edge_points = a[index] + (b - a)[index] * t[:, None]
        thin = thin[cKDTree(edge_points).query(points[thin])[0] > min_span]
    found = []
    if len(thin):
        pairs = cKDTree(points[thin]).query_pairs(3 * spacing, output_type="ndarray")
        graph = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(len(thin), len(thin)))
        labels = connected_components(graph, directed=False)[1]
        for label in np.unique(labels):
            members = thin[labels == label]
            area = float(len(members) * mesh.area / count)
            if area >= min_area:
                found.append(dict(area_mm2=round(area, 1), min_mm=round(float(depth[members].min()), 2),
                                  median_mm=round(float(np.median(depth[members])), 2),
                                  bounds=np.vstack([points[members].min(axis=0), points[members].max(axis=0)]).round(1).tolist()))
    found.sort(key=lambda item: -item["area_mm2"])
    return stats, found


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=("islands", "ridges", "inlays", "overhangs", "thickness", "fins"))
    parser.add_argument("names", nargs="*")
    parser.add_argument("--committed", action="store_true", help="analyse the committed STL folders instead of build/")
    parser.add_argument("--layer", type=float, default=0.2, help="islands, overhangs: layer height")
    parser.add_argument("--max-z", type=float, help="overhangs: only up to this height")
    parser.add_argument("--min-span", type=float, default=2.0,
                        help="overhangs: ignore unsupported strips narrower than this (bridges over grooves); "
                             "thickness: ignore thin strips narrower than this (edges); 0 = report all")
    parser.add_argument("--min-area", type=float, default=None,
                        help="smallest finding in mm2 (islands 0.05, ridges/inlays/fins 0.1, overhangs 100, thickness 2)")
    parser.add_argument("--z", type=float, nargs="+", default=[0.4], help="ridges: section heights")
    parser.add_argument("--min-width", type=float, default=None, help="ridges 1.1 mm, inlays 0.8 mm, thickness 1.2 mm, fins 2 mm")
    parser.add_argument("--min-height", type=float, default=4.0, help="fins: shortest unbraced run to report (mm)")
    parser.add_argument("--density", type=float, default=2.0, help="thickness: surface mm2 per sample point (2000-100000 points)")
    parser.add_argument("--ignore-area", type=float, default=5.0, help="ridges: skip components smaller than this (mm2)")
    args = parser.parse_args()
    names = args.names or (COLOR_PIECES if args.command == "inlays" else list(PARTS))
    if args.command == "inlays":
        names = [n for n in names if not n.endswith("_base")]
    report, total = {}, 0
    for name in names:
        mesh, solid = load(name, args.committed)
        if args.command == "islands":
            found = islands(mesh, solid, args.layer, args.min_area or 0.05)
        elif args.command == "overhangs":
            found = overhangs(mesh, solid, args.layer, args.min_area or 100, args.max_z, args.min_span)
        elif args.command == "ridges":
            found = [dict(z_mm=z, **item) for z in args.z
                     for item in thin(solid.slice(z), args.min_width or 1.1, args.ignore_area, args.min_area or 0.1)]
        elif args.command == "fins":
            found = fins(mesh, solid, args.layer, args.min_width or 2.0, args.min_area or 0.1, args.min_height)
        elif args.command == "thickness":
            stats, found = thickness(mesh, args.min_width or 1.2, args.density, args.min_area or 2.0, min_span=args.min_span)
            print(f"{name}: wall thickness p01 {stats['p01']} / p05 {stats['p05']} / median {stats['median']} mm "
                  f"({stats['measured']} of {stats['samples']} points)")
        else:
            z0 = float(mesh.bounds[0, 2])   # first layer of the inlay itself
            section = solid.slice(z0 + 0.1)
            pieces = section.decompose()
            found = thin(section, args.min_width or 0.8, 0, args.min_area or 0.1)
            print(f"{name}: {len(pieces)} bodies on its first layer (z {z0:.2f}), {section.area():.1f} mm2, "
                  f"smallest {min((p.area() for p in pieces), default=0):.2f} mm2")
        report[name] = dict(stats, regions=found) if args.command == "thickness" else found
        total += len(found)
        print(f"{args.command} {name}: {len(found)} found", flush=True)
        for item in found[:12]:
            print(f"  {item}")
        if len(found) > 12:
            print(f"  ... {len(found) - 12} more")
    path = BUILD / "analysis" / f"{args.command}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(f"{'FOUND' if total else 'CLEAN'}: {total} {args.command} findings in {len(names)} meshes -> {path}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
