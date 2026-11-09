"""
Generate high-resolution geometric sci-fi WARPGATE logo and icon using Pillow.
"""
from PIL import Image, ImageDraw, ImageFilter
import math
import os

def create_warpgate_logo():
    size = 1024
    img = Image.new("RGBA", (size, size), (15, 17, 23, 255))
    draw = ImageDraw.Draw(img)
    center = size // 2

    # Draw dark radial hexagon / portal backdrop
    angles = [math.radians(60 * i - 30) for i in range(6)]
    hex_radius = 440
    hex_points = [
        (center + hex_radius * math.cos(a), center + hex_radius * math.sin(a))
        for a in angles
    ]
    draw.polygon(hex_points, fill=(24, 28, 38, 255), outline=(45, 52, 70, 255), width=6)

    # Outer Neon Ring (Cyan & Electric Blue glow)
    for r, alpha in [(370, 40), (365, 80), (360, 160), (355, 255)]:
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            outline=(0, 229, 255, alpha),
            width=5
        )

    # Tech tick marks around the ring
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        r_inner = 330 if deg % 45 == 0 else 342
        r_outer = 355
        x1 = center + r_inner * math.cos(rad)
        y1 = center + r_inner * math.sin(rad)
        x2 = center + r_outer * math.cos(rad)
        y2 = center + r_outer * math.sin(rad)
        color = (255, 153, 0, 255) if deg % 90 == 0 else (0, 229, 255, 200)
        w = 4 if deg % 45 == 0 else 2
        draw.line([(x1, y1), (x2, y2)], fill=color, width=w)

    # Middle Ring (Overwatch orange / Ember neon)
    r_mid = 270
    draw.ellipse(
        [center - r_mid, center - r_mid, center + r_mid, center + r_mid],
        outline=(255, 140, 0, 240),
        width=8
    )

    # Central Warpgate Geometry (Dual Inverted Tech Triangles forming a Gate)
    top_w = 190
    top_gate = [
        (center - top_w, center - 180),
        (center + top_w, center - 180),
        (center + 60, center + 40),
        (center - 60, center + 40)
    ]
    draw.polygon(top_gate, fill=(255, 120, 0, 230), outline=(255, 200, 50, 255), width=4)

    # Inner Core Portal (Vibrant Cyan Core)
    inner_core = [
        (center, center - 110),
        (center + 120, center + 90),
        (center, center + 50),
        (center - 120, center + 90)
    ]
    draw.polygon(inner_core, fill=(0, 240, 255, 240), outline=(255, 255, 255, 255), width=4)

    # Laser Core center aperture
    r_core = 42
    draw.ellipse(
        [center - r_core, center - r_core, center + r_core, center + r_core],
        fill=(255, 255, 255, 255),
        outline=(0, 229, 255, 255),
        width=6
    )

    os.makedirs("assets", exist_ok=True)
    logo_path = os.path.join("assets", "warpgate_logo.png")
    img.save(logo_path, "PNG")
    print(f"Saved logo to {logo_path}")

    # Generate .ico file for application
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    ico_path = os.path.join("assets", "warpgate.ico")
    img.save(ico_path, format="ICO", sizes=icon_sizes)
    img.save("LOGO_SMALL_APPLICATION.ico", format="ICO", sizes=icon_sizes)
    print(f"Saved application icons to {ico_path} and LOGO_SMALL_APPLICATION.ico")

if __name__ == "__main__":
    create_warpgate_logo()
