from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, random

W, H = 3840, 1536
SCALE = 1
SW, SH = W, H
FPS = 15
DURATION = int(1000 / FPS)
TOTAL = 60  # 4s loop

BG = (8, 6, 13, 255)
BASE = (20, 15, 34, 255)
VIOLET = (117, 89, 178)
LAV = (217, 194, 255)
LIGHT = (219, 162, 254)
MAGENTA = (164, 80, 190)
DIM = (60, 52, 88)
TEXT = (222, 212, 240)
MUT = (110, 100, 140)

NAME_FONT = r"C:\Windows\Fonts\seguisb.ttf"
MONO_FONT = r"C:\Windows\Fonts\consolab.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def clamp255(v):
    return max(0, min(255, int(v)))

def lerp_color(c1, c2, t):
    return tuple(clamp255(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def draw_blob(img, cx, cy, r, color, strength=90):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(r, 0, -6):
        a = int(strength * (1 - i / r) ** 1.6)
        d.ellipse([cx - i, cy - i, cx + i, cy + i], fill=color + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(30))
    img.alpha_composite(layer)

def draw_orbs(img, t):
    # drifting glow orbs like the source banner
    orbs = [
        (0.18, 0.25, 0.42, VIOLET, 150),
        (0.82, 0.30, 0.55, MAGENTA, 130),
        (0.30, 0.75, 0.35, VIOLET, 110),
        (0.75, 0.72, 0.28, LAV, 90),
        (0.50, 0.55, 0.50, (70, 45, 110), 160),
    ]
    for i, (bx, by, speed, col, strength) in enumerate(orbs):
        cx = int(W * (bx + 0.12 * math.sin(t * speed + i * 1.7)))
        cy = int(H * (by + 0.10 * math.cos(t * speed * 0.8 + i * 2.1)))
        draw_blob(img, cx, cy, int(H * 0.30), col, strength)

def draw_grid(img, t):
    g = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    step = 90
    offset = int((t * 30) % step)
    for gx in range(0, W, step):
        d.line([gx, 0, gx, H], fill=LAV + (8,))
    for gy in range(-step, H + step, step):
        d.line([0, gy + offset, W, gy + offset], fill=LAV + (6,))
    img.alpha_composite(g)

def draw_frame(img, t, d):
    # orbs
    draw_orbs(img, t)

    # subtle film grain / dots
    prng = random.Random(5)
    for i in range(140):
        pxp = (prng.random() * W, prng.random() * H)
        a = int(8 + 12 * math.sin(t * 2 + i))
        r = int(2 + (i % 4))
        d.ellipse([pxp[0], pxp[1], pxp[0] + r, pxp[1] + r], fill=LAV + (a,))

    # corner brackets
    cb = 90
    pul = 120 + 60 * math.sin(t * 2.2)
    ccol = LAV + (int(pul),)
    pad = 70
    for cx, cy, sx, sy in [(pad, pad, 1, 1),
                           (W - pad, pad, -1, 1),
                           (pad, H - pad, 1, -1),
                           (W - pad, H - pad, -1, -1)]:
        d.line([cx, cy, cx + cb * sx, cy], fill=ccol, width=6)
        d.line([cx, cy, cx, cy + cb * sy], fill=ccol, width=6)

    # status line
    mf = font(MONO_FONT, 30)
    d.text((110, 100), "Farma@profile:~$ ./launch boostUP", font=mf, fill=MUT)
    if int(t * 2) % 2 == 0:
        d.ellipse([W - 220, 92, W - 180, 132], fill=LAV)

    # name glow
    hf = font(NAME_FONT, 320)
    words = "FARMA"
    x = (W - d.textlength(words, font=hf)) // 2
    y = int(H * 0.40)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.text((x, y), words, font=hf, fill=LAV + (int(70 + 50 * math.sin(t * 2)),))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img.alpha_composite(glow)
    # shimmering per-letter gradient
    xpos = x
    for i, ch in enumerate(words):
        col = lerp_color(LIGHT, LAV, (math.sin(t * 1.4 + i * 0.7) + 1) / 2)
        d.text((xpos, y), ch, font=hf, fill=col + (255,))
        xpos += d.textlength(ch, font=hf)

    # subtitle
    sf = font(NAME_FONT, 52)
    sub = "Desktop Apps  \u00b7  Discord Bots"
    sx = (W - d.textlength(sub, font=sf)) // 2
    d.text((sx, y + 380), sub, font=sf, fill=TEXT)

    # progress bar centered
    pw = int(W * 0.26)
    px, py = (W - pw) // 2, y + 470
    d.rounded_rectangle([px, py, px + pw, py + 14], radius=7, fill=(35, 28, 55, 255))
    prog = min(1.0, ((t * 0.4) % 1.0))
    d.rounded_rectangle([px, py, px + pw * prog, py + 14], radius=7, fill=LAV)
    sheen = px + ((t * 2.0 * pw) % (pw + 60)) - 30
    d.rounded_rectangle([sheen, py, sheen + 40, py + 14], radius=7, fill=(255, 255, 255, 130))
    d.text((px + pw + 40, py - 8), f"{int(prog * 100)}%", font=mf, fill=LIGHT)

    # scanline
    sy = int(((t * 500) % (H + 300)) - 150)
    scan = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    h = 120
    for i in range(h):
        a = int(9 * math.exp(-i / (h * 0.3)))
        sd.line([pad, sy + i, W - pad, sy + i], fill=LAV + (a,))
    img.alpha_composite(scan)

    # floating particles
    prng = random.Random(13)
    for i in range(60):
        pp = (prng.random() * W, ((prng.random() * H) - (t * 60) % H) % H)
        a = int(30 + 60 * math.sin(t * 2.2 + i))
        r = int(2 + (i % 5))
        d.ellipse([pp[0], pp[1], pp[0] + r, pp[1] + r], fill=LAV + (a,))

def main():
    frames = []
    for i in range(TOTAL):
        t = i / FPS
        img = Image.new("RGBA", (SW, SH), BG)
        d = ImageDraw.Draw(img)
        draw_frame(img, t, d)
        down = img.convert("P", palette=Image.ADAPTIVE, colors=255)
        frames.append(down)
        if i % 10 == 0:
            print("frame", i, "/", TOTAL)

    out = r"C:\Users\RAMZI\AppData\Local\Temp\opencode\farma3334\farma-banner.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=DURATION, loop=0, optimize=True)
    import os
    print("wrote", out, "frames:", len(frames), "bytes:", os.path.getsize(out))

if __name__ == "__main__":
    main()
