from PIL import Image
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
import os
import time
import csv


# ============================================================
# Parameters
# ============================================================

input_folder = "polygons"

output_csv = "results.csv"


# ============================================================
# Solve one image
# ============================================================

def solve_image(image_path , folder_path):

    # --------------------------------------------------------
    # 1. Read image
    # --------------------------------------------------------

    image = Image.open(image_path).convert("L")
    img = np.array(image)

    # White = fluid
    # Black = wall/outside
    fluid = img > 128


    # --------------------------------------------------------
    # 2. Physical / numerical parameters
    # --------------------------------------------------------

    h = 1.0

    # We solve the problem for:
    #
    #       G / mu = 1
    #
    # Then:
    #
    #       C_shape = A^2 / Q1
    #

    G_over_mu = 1.0


    # --------------------------------------------------------
    # 3. Area and number of unknowns
    # --------------------------------------------------------

    A = np.sum(fluid) * h**2

    N = np.sum(fluid)


    # --------------------------------------------------------
    # 4. Map 2D fluid pixels -> 1D equation numbers
    # --------------------------------------------------------

    index_map = -np.ones(
        fluid.shape,
        dtype=int
    )

    index_map[fluid] = np.arange(N)


    # --------------------------------------------------------
    # 5. Create sparse matrix
    # --------------------------------------------------------

    A_matrix = lil_matrix(
        (N, N),
        dtype=float
    )

    b = np.full(
        N,
        G_over_mu * h**2,
        dtype=float
    )


    # --------------------------------------------------------
    # 6. Build finite-difference equations
    # --------------------------------------------------------

    start_build = time.perf_counter()


    for i in range(1, img.shape[0] - 1):

        for j in range(1, img.shape[1] - 1):

            if fluid[i, j]:

                # Equation number of current pixel
                p = index_map[i, j]

                # Center coefficient
                A_matrix[p, p] = 4.0


                # ------------------------------------------------
                # North neighbor
                # ------------------------------------------------

                if fluid[i - 1, j]:

                    n = index_map[i - 1, j]

                    A_matrix[p, n] = -1.0


                # ------------------------------------------------
                # South neighbor
                # ------------------------------------------------

                if fluid[i + 1, j]:

                    s = index_map[i + 1, j]

                    A_matrix[p, s] = -1.0


                # ------------------------------------------------
                # West neighbor
                # ------------------------------------------------

                if fluid[i, j - 1]:

                    w = index_map[i, j - 1]

                    A_matrix[p, w] = -1.0


                # ------------------------------------------------
                # East neighbor
                # ------------------------------------------------

                if fluid[i, j + 1]:

                    e = index_map[i, j + 1]

                    A_matrix[p, e] = -1.0


    # Convert to CSR format for the solver

    A_matrix = A_matrix.tocsr()


    build_time = (
        time.perf_counter()
        - start_build
    )


    # --------------------------------------------------------
    # 7. Solve linear system
    # --------------------------------------------------------

    start_solve = time.perf_counter()


    u_vector = spsolve(
        A_matrix,
        b
    )


    solve_time = (
        time.perf_counter()
        - start_solve
    )


    # --------------------------------------------------------
    # 8. Put velocity back into 2D image
    # --------------------------------------------------------

    u = np.zeros_like(
        img,
        dtype=float
    )

    u[fluid] = u_vector


    # --------------------------------------------------------
    # 9. Calculate residual
    # --------------------------------------------------------

    north = u[:-2, 1:-1]

    south = u[2:, 1:-1]

    west = u[1:-1, :-2]

    east = u[1:-1, 2:]

    center = u[1:-1, 1:-1]


    residual = (
        4.0 * center
        - north
        - south
        - west
        - east
    ) / h**2 - G_over_mu


    fluid_inside = fluid[1:-1, 1:-1]


    residual_rms = np.sqrt(
        np.mean(
            residual[fluid_inside]**2
        )
    )


    # --------------------------------------------------------
    # 10. Calculate Q1
    # --------------------------------------------------------

    Q1 = np.sum(
        u[fluid]
    ) * h**2


    # --------------------------------------------------------
    # 11. Calculate shape coefficient
    # --------------------------------------------------------

    C_shape = A**2 / Q1


    # ============================================================
    # 12. Create velocity image
    # ============================================================

    u_max = np.max(u[fluid])

    velocity_img = np.zeros_like(u, dtype=np.uint8)

    velocity_img[fluid] = (
        255 * u[fluid] / u_max
    ).astype(np.uint8)


    velocity_image = Image.fromarray(velocity_img)

    velocity_image.save(f"{folder_path}/velocity{img.shape[0]}.png")


    print("Velocity image saved")


    # --------------------------------------------------------
    # 13. Return results
    # --------------------------------------------------------

    return {

        "resolution": img.shape[0],

        "area": A,

        "unknowns": N,

        "Q1": Q1,

        "C_shape": C_shape,

        "build_time": build_time,

        "solve_time": solve_time,

        "residual": residual_rms,

        "nnz": A_matrix.nnz
    }


# ============================================================
# Main dataset loop
# ============================================================

results = []


# ------------------------------------------------------------
# Check input folder
# ------------------------------------------------------------

if not os.path.isdir(input_folder):

    raise FileNotFoundError(
        f"Input folder not found: {input_folder}"
    )


# ------------------------------------------------------------
# Loop over polygon folders
# ------------------------------------------------------------

for folder_name in os.listdir(input_folder):

    folder_path = os.path.join(
        input_folder,
        folder_name
    )


    # Ignore files
    if not os.path.isdir(folder_path):

        continue


    # --------------------------------------------------------
    # Extract number of sides
    #
    # Example:
    #
    # "3-gon" -> 3
    # "10-gon" -> 10
    # --------------------------------------------------------

    try:

        sides = int(
            folder_name.split("-")[0]
        )

    except ValueError:

        print(
            f"Skipping unknown folder: {folder_name}"
        )

        continue


    print("\n================================")
    print(f"Processing {folder_name}")
    print("================================")


    # --------------------------------------------------------
    # Loop over images
    # --------------------------------------------------------

    for filename in os.listdir(folder_path):

        if not filename.lower().endswith(".png") or filename.startswith("velocity"):

            continue


        image_path = os.path.join(
            folder_path,
            filename
        )


        print(
            f"\nSolving {image_path}"
        )


        # ----------------------------------------------------
        # Solve image
        # ----------------------------------------------------

        result = solve_image(
            image_path , folder_path
        )


        # ----------------------------------------------------
        # Add dataset information
        # ----------------------------------------------------

        result["sides"] = sides

        result["filename"] = filename


        # Add result to dataset

        results.append(result)


        # ----------------------------------------------------
        # Print result
        # ----------------------------------------------------

        print(
            f"  Resolution = "
            f"{result['resolution']}"
        )

        print(
            f"  Area       = "
            f"{result['area']}"
        )

        print(
            f"  Q1         = "
            f"{result['Q1']:.10f}"
        )

        print(
            f"  C_shape    = "
            f"{result['C_shape']:.10f}"
        )

        print(
            f"  Residual   = "
            f"{result['residual']:.3e}"
        )

        print(
            f"  Build time = "
            f"{result['build_time']:.4f} s"
        )

        print(
            f"  Solve time = "
            f"{result['solve_time']:.4f} s"
        )

        print(
            f"  NNZ        = "
            f"{result['nnz']}"
        )


# ============================================================
# Create CSV file
# ============================================================

headers = [

    "Sides",

    "Resolution",

    "Filename",

    "Area",

    "Unknowns",

    "Q1",

    "C_shape",

    "Build Time (s)",

    "Solve Time (s)",

    "Residual",

    "NNZ"
]


# ------------------------------------------------------------
# Write CSV
# ------------------------------------------------------------

with open(
    output_csv,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    # Header
    writer.writerow(headers)


    # Data
    for result in results:

        writer.writerow([

            result["sides"],

            result["resolution"],

            result["filename"],

            result["area"],

            result["unknowns"],

            result["Q1"],

            result["C_shape"],

            result["build_time"],

            result["solve_time"],

            result["residual"],

            result["nnz"]
        ])


# ============================================================
# Finished
# ============================================================

print("\n================================")
print("Dataset solving complete!")
print(f"Total cases = {len(results)}")
print(f"Results saved to: {output_csv}")
print("================================")
