"""fc_viewmodel.py — the first-person hand and held item, in real perspective.

Minecraft draws the held item as an *extruded* model, not as the flat inventory
sprite: every opaque texel becomes a slab one sixteenth deep, the silhouette
gets side walls, and the whole thing is rendered through the same projection as
the world, held in a hand that is itself a box off the player model.

Compositing that layer as 2D art instead is the single most obvious tell that a
frame was assembled rather than captured. A sprite rotated by a non-right angle
picks up ragged stair-stepped edges that nothing else in a block world has, it
has no thickness, and it does not foreshorten with the rest of the frame — so
the arm reads as a paper cut-out laid over a 3D scene.

So this builds both in **camera space** (X right, Y up, Z forward) and hands
them to fc_pov.paint_camera_quads, which runs them through the same near-clip
and projection the world uses. The sleeve samples the pack's own apprentice
armour layer, so the Hero's arm wears what the Hero wears.
"""
from __future__ import annotations

import math

from PIL import Image

import fc_pov as P
from fc_lib import RP

ITEM_TEX = RP / "textures" / "items"
ARMOR_TEX = RP / "textures" / "models" / "armor"

# Vanilla skin/armour UV for the 4x12x4 right-arm box on a 64x32 layer sheet.
ARM_UV = {
    "up": (44, 16, 48, 20),
    "down": (48, 16, 52, 20),
    "right": (40, 20, 44, 32),
    "front": (44, 20, 48, 32),
    "left": (48, 20, 52, 32),
    "back": (52, 20, 56, 32),
}

SKIN = (222, 176, 136)

# A fixed key light for the view model. The world is shaded by world-space
# normals; the hand is pinned to the camera, so it gets its own constant
# direction — which is also what keeps it readable against any background.
VIEW_LIGHT = P.norm((-0.35, 0.72, -0.60))


def _shade(rgb, normal, brightness):
    lit = 0.58 + 0.52 * max(0.0, P.dot(normal, VIEW_LIGHT))
    scale = lit * brightness
    return tuple(max(0, min(255, int(c * scale))) for c in rgb[:3])


# ---------------------------------------------------------------------------
# rotation
# ---------------------------------------------------------------------------

def _basis(yaw, pitch, roll):
    """Orthonormal (right, up, forward) for the given Euler angles, in radians.

    Applied roll -> pitch -> yaw, which is the order that lets the item's tilt
    in the picture plane be dialled independently of how far it is turned away
    from the viewer.
    """
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)

    def rot(v):
        x, y, z = v
        x, y = x * cr - y * sr, x * sr + y * cr          # roll about Z
        y, z = y * cp - z * sp, y * sp + z * cp          # pitch about X
        x, z = x * cy + z * sy, -x * sy + z * cy         # yaw about Y
        return (x, y, z)

    return rot((1, 0, 0)), rot((0, 1, 0)), rot((0, 0, 1))


def _place(local, origin, basis):
    r, u, f = basis
    return (origin[0] + r[0] * local[0] + u[0] * local[1] + f[0] * local[2],
            origin[1] + r[1] * local[0] + u[1] * local[1] + f[1] * local[2],
            origin[2] + r[2] * local[0] + u[2] * local[1] + f[2] * local[2])


# ---------------------------------------------------------------------------
# the item
# ---------------------------------------------------------------------------

_ITEM_CACHE = {}


def _item_texture(item_id):
    if item_id not in _ITEM_CACHE:
        path = ITEM_TEX / f"{item_id}.png"
        _ITEM_CACHE[item_id] = (Image.open(path).convert("RGBA")
                                if path.exists() else None)
    return _ITEM_CACHE[item_id]


def extrude_item(item_id, origin, basis, scale, brightness=1.0, depth_px=1.0):
    """Build the held item as Minecraft builds it: a slab per opaque texel.

    Front and back faces come from the texel's own colour; side walls are
    emitted only where an opaque texel meets a transparent one, which is what
    gives the model a silhouette with real thickness instead of a paper edge.
    """
    tex = _item_texture(item_id)
    if tex is None:
        return []
    w, h = tex.size
    px = tex.load()
    half_d = depth_px * scale / 2.0

    def opaque(x, y):
        return 0 <= x < w and 0 <= y < h and px[x, y][3] >= 32

    r, u, f = basis
    front_n = (-f[0], -f[1], -f[2])
    quads = []

    for y in range(h):
        for x in range(w):
            if not opaque(x, y):
                continue
            colour = px[x, y]
            alpha = colour[3]
            # Texel corners in model space, centred on the sprite.
            x0 = (x - w / 2.0) * scale
            x1 = (x + 1 - w / 2.0) * scale
            y0 = (h / 2.0 - y - 1) * scale
            y1 = (h / 2.0 - y) * scale

            def at(lx, ly, lz):
                return _place((lx, ly, lz), origin, basis)

            front = [at(x0, y0, -half_d), at(x0, y1, -half_d),
                     at(x1, y1, -half_d), at(x1, y0, -half_d)]
            back = [at(x1, y0, half_d), at(x1, y1, half_d),
                    at(x0, y1, half_d), at(x0, y0, half_d)]
            quads.append((front, _shade(colour, front_n, brightness), alpha))
            quads.append((back, _shade(colour, f, brightness), alpha))

            # Side walls along the silhouette only.
            if not opaque(x - 1, y):
                quads.append(([at(x0, y0, half_d), at(x0, y1, half_d),
                               at(x0, y1, -half_d), at(x0, y0, -half_d)],
                              _shade(colour, (-r[0], -r[1], -r[2]), brightness), alpha))
            if not opaque(x + 1, y):
                quads.append(([at(x1, y0, -half_d), at(x1, y1, -half_d),
                               at(x1, y1, half_d), at(x1, y0, half_d)],
                              _shade(colour, r, brightness), alpha))
            if not opaque(x, y - 1):
                quads.append(([at(x0, y1, -half_d), at(x0, y1, half_d),
                               at(x1, y1, half_d), at(x1, y1, -half_d)],
                              _shade(colour, u, brightness), alpha))
            if not opaque(x, y + 1):
                quads.append(([at(x0, y0, half_d), at(x0, y0, -half_d),
                               at(x1, y0, -half_d), at(x1, y0, half_d)],
                              _shade(colour, (-u[0], -u[1], -u[2]), brightness), alpha))
    return quads


# ---------------------------------------------------------------------------
# the arm
# ---------------------------------------------------------------------------

_SLEEVE_CACHE = {}
BANDS = 6          # slices along the arm; enough to show a cuff and shading


def sleeve_bands(set_name="apprentice", bands=BANDS):
    """Per-face colour bands down the arm, read off the pack's armour layer.

    Averaging each face to a single colour turned the sleeve into a flat pale
    slab. The armour layer's real structure runs *along* the arm — cuff, folds,
    shading — so slicing each face into bands down its length recovers the part
    of the texture that actually reads at this size, without paying for full UV
    mapping on a model that is a few hundred pixels tall.
    """
    key = (set_name, bands)
    if key in _SLEEVE_CACHE:
        return _SLEEVE_CACHE[key]
    path = ARMOR_TEX / f"fc_{set_name}_layer_1.png"
    if not path.exists():
        out = {face: [(104, 78, 52)] * bands for face in ARM_UV}
        _SLEEVE_CACHE[key] = out
        return out
    sheet = Image.open(path).convert("RGBA")
    out = {}
    for face, (u0, v0, u1, v1) in ARM_UV.items():
        rows = []
        for i in range(bands):
            # Band 0 is the shoulder end, the last band the wrist.
            y0 = v0 + (v1 - v0) * i // bands
            y1 = max(y0 + 1, v0 + (v1 - v0) * (i + 1) // bands)
            pixels = [p for p in sheet.crop((u0, y0, u1, y1)).getdata() if p[3] >= 32]
            if pixels:
                n = len(pixels)
                rows.append((sum(p[0] for p in pixels) // n,
                             sum(p[1] for p in pixels) // n,
                             sum(p[2] for p in pixels) // n))
            else:
                rows.append(rows[-1] if rows else (104, 78, 52))
        out[face] = rows
    _SLEEVE_CACHE[key] = out
    return out


def banded_box(centre, size, basis, bands_by_face, brightness, skin=False):
    """A box sliced into bands along its `up` axis, each band its own colour."""
    r, u, f = basis
    length = size[1]
    count = len(next(iter(bands_by_face.values())))
    quads = []
    for i in range(count):
        # Band i measured from the far (shoulder) end toward the hand.
        offset = length / 2 - length * (i + 0.5) / count
        band_centre = (centre[0] - u[0] * offset,
                       centre[1] - u[1] * offset,
                       centre[2] - u[2] * offset)
        faces = {}
        for name, rows in bands_by_face.items():
            rgb = rows[i] if not skin else SKIN
            faces[name] = (_shade(rgb, _face_normal(name, basis), brightness), 255)
        quads += P.box_quads(band_centre, (size[0], length / count, size[2]),
                             basis, faces)
    return quads


def arm_quads(hand, direction, brightness=1.0, width=0.175, sleeve_len=None,
              hand_len=0.10, set_name="apprentice"):
    """The forearm as two oriented boxes: an armoured sleeve and a bare hand.

    `direction` points from the elbow toward the hand, so the arm runs back out
    of frame at the bottom right the way a real first-person arm does.
    """
    reach = math.sqrt(sum(c * c for c in direction))
    if sleeve_len is None:
        # Run from the wrist back past the elbow, so the arm leaves the frame
        # instead of ending in mid-air.
        sleeve_len = max(0.25, reach - hand_len + 0.22)
    up = P.norm(direction)
    # Any vector not parallel to the arm gives a stable roll reference.
    ref = (0.0, 0.0, 1.0) if abs(up[2]) < 0.9 else (1.0, 0.0, 0.0)
    right = P.norm(P.cross(ref, up))
    fwd = P.cross(right, up)
    basis = (right, up, fwd)

    quads = []
    hand_centre = (hand[0] - up[0] * hand_len / 2,
                   hand[1] - up[1] * hand_len / 2,
                   hand[2] - up[2] * hand_len / 2)
    quads += banded_box(hand_centre, (width * 0.94, hand_len, width * 0.94), basis,
                        {name: [SKIN] * 2 for name in ARM_UV}, brightness, skin=True)

    sleeve_centre = (hand[0] - up[0] * (hand_len + sleeve_len / 2),
                     hand[1] - up[1] * (hand_len + sleeve_len / 2),
                     hand[2] - up[2] * (hand_len + sleeve_len / 2))
    quads += banded_box(sleeve_centre, (width, sleeve_len, width), basis,
                        sleeve_bands(set_name), brightness)
    return quads


def _face_normal(name, basis):
    r, u, f = basis
    return {"up": u, "down": (-u[0], -u[1], -u[2]),
            "front": (-f[0], -f[1], -f[2]), "back": f,
            "left": (-r[0], -r[1], -r[2]), "right": r}[name]


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------

# Where the hand sits in camera space, and how the item is turned in it. These
# are tuned to read like the vanilla right-hand pose: the item held out to the
# lower right, tilted back and turned away from the viewer so its thickness
# shows along one edge.
HAND = (0.506, -0.545, 1.00)
ITEM_OFFSET = (0.125, 0.180, -0.020)
ITEM_YAW = math.radians(-16.0)
ITEM_PITCH = math.radians(-6.0)
ITEM_ROLL = math.radians(4.0)
ITEM_SPAN = 0.46                 # how wide the 16-texel sprite is, in blocks
# The elbow has to sit well out to the right and *below* the hand in camera
# space, not merely below it on screen: an elbow close to the view axis makes
# the forearm point almost straight at the lens, and it foreshortens into a
# flat wedge in the corner instead of reading as an arm.
ELBOW = (1.00, -1.05, 0.60)
ARM_DIRECTION = tuple(HAND[i] - ELBOW[i] for i in range(3))


def build(cam, item_id, brightness=1.0, set_name="apprentice"):
    """Camera-space quads for the whole view model, item first."""
    quads = []
    basis = _basis(ITEM_YAW, ITEM_PITCH, ITEM_ROLL)
    origin = (HAND[0] + ITEM_OFFSET[0], HAND[1] + ITEM_OFFSET[1],
              HAND[2] + ITEM_OFFSET[2])
    quads += arm_quads(HAND, ARM_DIRECTION, brightness=brightness,
                       set_name=set_name)
    if item_id:
        quads += extrude_item(item_id, origin, basis, ITEM_SPAN / 16.0,
                              brightness=brightness)
    return quads


def draw(canvas, cam, item_id, brightness=1.0, set_name="apprentice"):
    """Render the view model onto a finished world frame."""
    P.paint_camera_quads(canvas, cam, build(cam, item_id, brightness, set_name))
    return canvas
