from PIL import Image, ImageDraw, ImageFilter
import math, random

SRC = r"C:\Users\RAMZI\AppData\Local\Temp\opencode\farma3334\assets\new-banner.png"
W, H = 3840, 1536
FPS = 8
DURATION = int(1000 / FPS)
TOTAL = 24

LAV = (217, 194, 255)
GOLD = (219, 162, 254)

def load_source():
    img = Image.open(SRC).convert("RGBA")
    return img.resize((W, H), Image.LANCZOS)

def ken_burns(base, t):
    return base

def add_glow_orbs(img, t):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    orbs = [
        (0.15, 0.30, 0.35, (117, 89, 178), 60),
        (0.85, 0.28, 0.42, (164, 80, 190), 55),
        (0.5, 0.85, 0.30, (117, 89, 178), 45),
        (0.75, 0.7, 0.24, (219, 162, 254), 40),
        (0.25, 0.7, 0.28, (70, 45, 110), 50),
    ]
    for i, (bx, by, speed, col, st) in enumerate(orbs):
        cx = int(W * (bx + 0.10 * math.sin(t * speed + i * 1.7)))
        cy = int(H * (by + 0.08 * math.cos(t * speed * 0.8 + i * 2.1)))
        r = int(H * 0.35)
        for rr in range(r, 0, -8):
            a = int(st * (1 - rr / r) ** 2 * (0.6 + 0.4 * math.sin(t * 1.3 + i)))
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=col + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, layer)
    return img

def add_scanline(img, t):
    sy = int(((t * 600) % (H + 400)) - 200)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    h = 150
    for i in range(h):
        a = int(10 * math.exp(-i / (h * 0.35)))
        d.line([0, sy + i, W, sy + i], fill=(255, 255, 255, a))
    img = Image.alpha_composite(img, layer)
    return img

def add_particles(img, t):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    prng = random.Random(13)
    for i in range(80):
        pp = (prng.random() * W, ((prng.random() * H) - (t * 70) % H) % H)
        a = int(25 + 60 * math.sin(t * 2.2 + i))
        r = int(2 + (i % 5))
        col = GOLD if i % 3 else LAV
        d.ellipse([pp[0], pp[1], pp[0] + r, pp[1] + r], fill=col + (a,))
    img = Image.alpha_composite(img, layer)
    return img

def add_vignette(img, t):
    # breathing brightness
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    r = int(H * 0.72)
    cx, cy = W // 2, H // 2
    for rr in range(r, 0, -10):
        a = int(28 * (1 - rr / r) ** 1.5)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(0, 0, 0, a))
    img = Image.alpha_composite(img, layer)
    # global breathe
    b = 1.0 + 0.04 * math.sin(t * 1.2)
    img = img.point(lambda p, b=b: int(min(255, p * b)))
    return img

def main():
    base = load_source()
    frames = []
    for i in range(TOTAL):
        t = i / FPS
        frame = ken_burns(base, t)
        frame = add_glow_orbs(frame, t)
        frame = add_scanline(frame, t)
        frame = add_particles(frame, t)
        frame = add_vignette(frame, t)
        down = frame.convert("P", palette=Image.ADAPTIVE, colors=32)
        frames.append(down)
        if i % 15 == 0:
            print("frame", i, "/", TOTAL)

    out = r"C:\Users\RAMZI\AppData\Local\Temp\opencode\farma3334\farma-banner.gif"
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=DURATION, loop=0, optimize=True, transparency=0)
    import os
    print("wrote", out, "frames:", len(frames), "bytes:", os.path.getsize(out))

if __name__ == "__main__":
    main()
