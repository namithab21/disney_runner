"""
scenery.py - 3D Environment Scenery and Prop Geometry Generators.
Creates vertex arrays for stylized trees, roadside barriers, and decorative elements.
Vertex layout: [Position (3), Color (3), Normal (3)]
"""

import numpy as np


def add_quad(
    vertices_list: list,
    p1: list[float],
    p2: list[float],
    p3: list[float],
    p4: list[float],
    color: list[float],
    normal: list[float] | None = None
) -> None:
    """
    Appends a textured/colored quad (2 counter-clockwise triangles, 6 vertices) to vertices_list.
    p1: bottom-left, p2: bottom-right, p3: top-right, p4: top-left.
    """
    if normal is None:
        # Calculate normal using cross product of (p2 - p1) x (p4 - p1)
        v1 = np.array(p2) - np.array(p1)
        v2 = np.array(p4) - np.array(p1)
        n = np.cross(v1, v2)
        norm = np.linalg.norm(n)
        if norm > 1e-6:
            n = n / norm
        else:
            n = np.array([0.0, 1.0, 0.0])
        normal = n.tolist()

    r, g, b = color[0], color[1], color[2]
    nx, ny, nz = normal[0], normal[1], normal[2]

    # Triangle 1: p1 -> p2 -> p3
    vertices_list.extend([
        p1[0], p1[1], p1[2],  r, g, b,  nx, ny, nz,
        p2[0], p2[1], p2[2],  r, g, b,  nx, ny, nz,
        p3[0], p3[1], p3[2],  r, g, b,  nx, ny, nz,
    ])

    # Triangle 2: p1 -> p3 -> p4
    vertices_list.extend([
        p1[0], p1[1], p1[2],  r, g, b,  nx, ny, nz,
        p3[0], p3[1], p3[2],  r, g, b,  nx, ny, nz,
        p4[0], p4[1], p4[2],  r, g, b,  nx, ny, nz,
    ])


def add_box(
    vertices_list: list,
    min_corner: list[float],
    max_corner: list[float],
    color: list[float]
) -> None:
    """Adds an axis-aligned box between min_corner and max_corner."""
    x0, y0, z0 = min_corner
    x1, y1, z1 = max_corner

    # Front (+Z)
    add_quad(vertices_list, [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1], color, [0.0, 0.0, 1.0])
    # Back (-Z)
    add_quad(vertices_list, [x1, y0, z0], [x0, y0, z0], [x0, y1, z0], [x1, y1, z0], color, [0.0, 0.0, -1.0])
    # Top (+Y)
    add_quad(vertices_list, [x0, y1, z1], [x1, y1, z1], [x1, y1, z0], [x0, y1, z0], color, [0.0, 1.0, 0.0])
    # Bottom (-Y)
    add_quad(vertices_list, [x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1], color, [0.0, -1.0, 0.0])
    # Right (+X)
    add_quad(vertices_list, [x1, y0, z1], [x1, y0, z0], [x1, y1, z0], [x1, y1, z1], color, [1.0, 0.0, 0.0])
    # Left (-X)
    add_quad(vertices_list, [x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0], color, [-1.0, 0.0, 0.0])


def add_tree(
    vertices_list: list,
    x: float,
    z: float,
    scale: float = 1.0,
    foliage_tint: list[float] | None = None
) -> None:
    """
    Adds a stylized low-poly Disney-themed pine tree at (x, 0, z).
    Consists of a trunk and 3 stacked tiered pyramidal cones for lush volume.
    """
    trunk_color = [0.42, 0.28, 0.16]
    c1 = foliage_tint if foliage_tint else [0.14, 0.48, 0.22]
    c2 = [c1[0] * 1.15, c1[1] * 1.15, c1[2] * 1.10]
    c3 = [c1[0] * 1.30, c1[1] * 1.30, c1[2] * 1.20]

    # Trunk (brown column)
    tw = 0.22 * scale
    th = 1.2 * scale
    add_box(vertices_list, [x - tw, 0.0, z - tw], [x + tw, th, z + tw], trunk_color)

    # Helper for a 4-sided pyramid foliage tier
    def add_pyramid(base_y: float, top_y: float, half_w: float, color: list[float]):
        tip = [x, top_y, z]
        b1 = [x - half_w, base_y, z + half_w]
        b2 = [x + half_w, base_y, z + half_w]
        b3 = [x + half_w, base_y, z - half_w]
        b4 = [x - half_w, base_y, z - half_w]

        # 4 sloping triangular faces
        for p_start, p_end in [(b1, b2), (b2, b3), (b3, b4), (b4, b1)]:
            v1 = np.array(p_end) - np.array(p_start)
            v2 = np.array(tip) - np.array(p_start)
            n = np.cross(v1, v2)
            norm = np.linalg.norm(n)
            n = (n / norm).tolist() if norm > 1e-6 else [0.0, 1.0, 0.0]

            r, g, b = color[0], color[1], color[2]
            nx, ny, nz = n[0], n[1], n[2]

            vertices_list.extend([
                p_start[0], p_start[1], p_start[2],  r, g, b,  nx, ny, nz,
                p_end[0],   p_end[1],   p_end[2],    r, g, b,  nx, ny, nz,
                tip[0],     tip[1],     tip[2],      r, g, b,  nx, ny, nz,
            ])

        # Bottom base cap
        add_quad(vertices_list, b4, b3, b2, b1, color, [0.0, -1.0, 0.0])

    # Tier 1 (Lower canopy)
    add_pyramid(base_y=0.9 * scale, top_y=2.5 * scale, half_w=1.4 * scale, color=c1)
    # Tier 2 (Middle canopy)
    add_pyramid(base_y=2.0 * scale, top_y=3.8 * scale, half_w=1.1 * scale, color=c2)
    # Tier 3 (Top canopy)
    add_pyramid(base_y=3.2 * scale, top_y=5.0 * scale, half_w=0.75 * scale, color=c3)


def add_guardrail(
    vertices_list: list,
    x: float,
    z_start: float,
    z_end: float,
    base_y: float = 0.25,
    num_posts: int = 5
) -> None:
    """Adds a modern safety guardrail with vertical posts and horizontal beam."""
    post_color = [0.70, 0.70, 0.72]
    rail_color = [0.92, 0.90, 0.85]

    pw = 0.05
    ph = 0.65

    # Posts
    z_step = (z_end - z_start) / max(1, num_posts - 1)
    for i in range(num_posts):
        pz = z_start + i * z_step
        add_box(
            vertices_list,
            [x - pw, base_y, pz - pw],
            [x + pw, base_y + ph, pz + pw],
            post_color
        )

    # Horizontal rail
    rw = 0.06
    rh = 0.12
    ry = base_y + ph * 0.75
    add_box(
        vertices_list,
        [x - rw, ry - rh / 2.0, min(z_start, z_end)],
        [x + rw, ry + rh / 2.0, max(z_start, z_end)],
        rail_color
    )
