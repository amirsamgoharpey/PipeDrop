from PIL import Image, ImageDraw
import numpy as np
import os
import math


# ============================================================
# Parameters
# ============================================================

area_fraction = 0.30

min_sides = 3
max_sides = 50

resolutions = [128, 256, 512, 1024, 2048]

output_folder = "polygons"


# ============================================================
# Generate one regular polygon
# ============================================================

def generate_polygon(n, resolution, area_fraction):

    # --------------------------------------------------------
    # 1. Target area
    # --------------------------------------------------------

    image_area = resolution ** 2

    target_area = area_fraction * image_area


    # --------------------------------------------------------
    # 2. Calculate circumradius R
    #
    # A = (n/2) R^2 sin(2*pi/n)
    # --------------------------------------------------------

    R = math.sqrt(
        (2 * target_area)
        / (n * math.sin(2 * math.pi / n))
    )


    # --------------------------------------------------------
    # 3. Image center
    # --------------------------------------------------------

    cx = resolution / 2
    cy = resolution / 2


    # --------------------------------------------------------
    # 4. Calculate vertex angles
    #
    # We want the top side to be horizontal.
    #
    # theta_0 = pi/2 - pi/n
    # --------------------------------------------------------

    theta0 = math.pi / 2 - math.pi / n


    # --------------------------------------------------------
    # 5. Calculate vertex coordinates
    # --------------------------------------------------------

    points = []

    for k in range(n):

        theta = theta0 + k * (2 * math.pi / n)

        x = cx + R * math.cos(theta)
        y = cy - R * math.sin(theta)

        points.append((x, y))


    # --------------------------------------------------------
    # 6. Check that polygon is inside the image
    # --------------------------------------------------------

    for x, y in points:

        if x < 0 or x >= resolution or y < 0 or y >= resolution:

            raise ValueError(
                f"Polygon with {n} sides does not fit "
                f"inside {resolution}x{resolution} image."
            )


    # --------------------------------------------------------
    # 7. Create black image
    # --------------------------------------------------------

    image = Image.new(
        "L",
        (resolution, resolution),
        0
    )

    draw = ImageDraw.Draw(image)


    # --------------------------------------------------------
    # 8. Draw white polygon
    # --------------------------------------------------------

    draw.polygon(
        points,
        fill=255
    )


    return image, target_area, R


# ============================================================
# Main program
# ============================================================

os.makedirs(output_folder, exist_ok=True)


for n in range(min_sides, max_sides + 1):

    # Folder name
    folder_name = f"{n}-gon"

    folder_path = os.path.join(
        output_folder,
        folder_name
    )

    os.makedirs(folder_path, exist_ok=True)


    print(f"\nGenerating {n}-gon...")


    for resolution in resolutions:

        image, target_area, R = generate_polygon(
            n,
            resolution,
            area_fraction
        )


        # File name
        filename = f"{resolution}.png"

        filepath = os.path.join(
            folder_path,
            filename
        )


        image.save(filepath)


        print(
            f"  {resolution}x{resolution}"
            f" | target area = {target_area:.2f}"
            f" | R = {R:.3f}"
            f" | saved: {filepath}"
        )


print("\nGeneration complete!")
