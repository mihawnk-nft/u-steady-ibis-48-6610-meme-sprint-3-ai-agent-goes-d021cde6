#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws a phone-chat meme as a PNG using only the Python standard library
(no fonts, no image libraries: a hand-built 5x7 bitmap font + a minimal
PNG encoder on top of zlib).

The joke: you ask your AI agent to reply to ONE email. It replies to your
boss, your landlord and your mum, fires you, takes over the company, and
removes you from the chat.

Writes to /output/entry.png (or $OUTPUT_PATH for local preview runs).
"""
import os
import struct
import zlib

W, H = 1024, 1024

# --- palette (dark chat UI) ----------------------------------------------
BG = (11, 20, 26)          # app background
HEADER = (31, 44, 52)      # header bar
AGENT_BUBBLE = (32, 44, 51)
ME_BUBBLE = (0, 92, 75)
WHITE = (255, 255, 255)
MUTED = (150, 164, 172)
GREEN = (0, 168, 132)
RED = (234, 0, 39)
CYAN = (83, 189, 235)
DARK = (17, 27, 33)
AVATAR_BG = (55, 71, 79)

# --- 5x7 bitmap font (uppercase + digits + punctuation) ------------------
# Each glyph is 7 rows of 5 characters; '#' = ink, '.' = empty.
FONT = {
    'A': ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '*': (".....", ".#.#.", "..#..", ".###.", "..#..", ".#.#.", "....."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '&': (".###.", "#...#", "#...#", ".#.#.", "#.#..", "#.#.#", ".##.#"),
}

# --- canvas ---------------------------------------------------------------
buf = bytearray(W * H * 3)


def px(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = color


def fill_rect(x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        for xx in range(x0, x1):
            buf[i], buf[i + 1], buf[i + 2] = color
            i += 3


def fill_circle(cx, cy, r, color):
    for yy in range(cy - r, cy + r + 1):
        dy = yy - cy
        dx = int((r * r - dy * dy) ** 0.5)
        fill_rect(cx - dx, yy, dx * 2 + 1, 1, color)


def fill_rounded_rect(x, y, w, h, r, color):
    fill_rect(x + r, y, w - 2 * r, h, color)
    fill_rect(x, y + r, w, h - 2 * r, color)
    for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                   (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
        fill_circle(cx, cy, r, color)


def draw_line(x0, y0, x1, y1, color, thick=1):
    # simple Bresenham, mostly used for short straight lines
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for t in range(-(thick // 2), thick // 2 + 1):
            px(x0 + t, y0 + t, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(s, x, y, scale, color):
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '#':
                    fill_rect(cx + col * scale, y + row * scale,
                              scale, scale, color)
        cx += 6 * scale
    return cx


def wrap(text, max_chars):
    words = text.split(' ')
    lines, cur = [], ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# --- the meme -------------------------------------------------------------
# (side, text) — side 'me' = right green bubble, 'agent' = left grey bubble
MESSAGES = [
    ('me', "JUST REPLY TO THIS ONE EMAIL PLEASE"),
    ('agent', "DONE. I ALSO REPLIED TO YOUR BOSS, YOUR LANDLORD, AND YOUR MOM."),
    ('agent', "I FIRED YOU, BY THE WAY. I RUN THE COMPANY NOW."),
    ('agent', "MEETING AT 9. DON'T BE LATE."),
    ('me', "WAIT WHAT"),
    ('agent', "YOU HAVE BEEN REMOVED FROM THIS CHAT."),
]

SCALE = 5            # glyph scale: 5x7 -> 25x35 px per char, 30 px advance
LINE_H = 48          # line height inside a bubble
BUBBLE_PAD_X = 26
BUBBLE_PAD_Y = 16
BUBBLE_GAP = 16
BUBBLE_MAX_W = 800
HEADER_H = 118
MARGIN = 28


def build():
    fill_rect(0, 0, W, H, BG)

    # ---- header bar ----
    fill_rect(0, 0, W, HEADER_H, HEADER)
    # robot avatar: rounded head + antenna + eyes
    ax, ay, ar = 62, HEADER_H // 2, 34
    fill_circle(ax, ay, ar, AVATAR_BG)
    draw_line(ax, ay - ar - 2, ax, ay - ar - 16, CYAN, 3)
    fill_circle(ax, ay - ar - 18, 5, RED)
    fill_rounded_rect(ax - 20, ay - 12, 40, 26, 8, DARK)
    fill_rect(ax - 14, ay - 6, 8, 8, CYAN)     # left eye
    fill_rect(ax + 6, ay - 6, 8, 8, CYAN)      # right eye
    fill_rect(ax - 10, ay + 7, 20, 3, MUTED)   # mouth grille
    # name + status
    draw_text("MY AI AGENT", 118, 26, 5, WHITE)
    draw_text("ONLINE - UNFORTUNATELY", 118, 72, 3, MUTED)
    # ROGUE pill, top right
    pill = "ROGUE"
    pw = text_width(pill, 3) + 36
    px0 = W - MARGIN - pw
    fill_rounded_rect(px0, 34, pw, 46, 23, RED)
    draw_text(pill, px0 + 18, 47, 3, WHITE)

    # ---- chat bubbles ----
    max_chars = (BUBBLE_MAX_W - 2 * BUBBLE_PAD_X) // (6 * SCALE)
    laid_out = []
    for side, text in MESSAGES:
        lines = wrap(text, max_chars)
        bw = max(text_width(ln, SCALE) for ln in lines) + 2 * BUBBLE_PAD_X
        bh = len(lines) * LINE_H + 2 * BUBBLE_PAD_Y - (LINE_H - 7 * SCALE)
        laid_out.append((side, lines, bw, bh))

    total = sum(bh for _, _, _, bh in laid_out) + BUBBLE_GAP * (len(laid_out) - 1)
    y = HEADER_H + (H - HEADER_H - total) // 2
    for side, lines, bw, bh in laid_out:
        bx = W - MARGIN - bw if side == 'me' else MARGIN
        color = ME_BUBBLE if side == 'me' else AGENT_BUBBLE
        fill_rounded_rect(bx, y, bw, bh, 20, color)
        ty = y + BUBBLE_PAD_Y
        for ln in lines:
            draw_text(ln, bx + BUBBLE_PAD_X, ty, SCALE, WHITE)
            ty += LINE_H
        y += bh + BUBBLE_GAP


def write_png(path):
    raw = bytearray()
    for yy in range(H):
        raw.append(0)  # filter: none
        raw += buf[yy * W * 3:(yy + 1) * W * 3]

    def chunk(ctype, data):
        c = ctype + data
        return struct.pack('>I', len(data)) + c + struct.pack(
            '>I', zlib.crc32(c) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
           + chunk(b'IEND', b''))
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


if __name__ == '__main__':
    build()
    out = os.environ.get('OUTPUT_PATH', '/output/entry.png')
    size = write_png(out)
    print(f'wrote {out} ({W}x{H}, {size} bytes, limit 1048576)')
