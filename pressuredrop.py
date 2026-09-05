from PIL import Image
import numpy as np

from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve

import time


# ============================================================
# 1. Read image
# ============================================================
inp = input("what is the file name: ")
image = Image.open(inp).convert("L")

img = np.array(image)

fluid = img > 128


print("Image shape:", img.shape)
print("Number of fluid pixels:", np.sum(fluid))


# ============================================================
# 2. Parameters
# ============================================================

h = 1.0

G_over_mu = 1.0


# ============================================================
# 3. Calculate area
# ============================================================

A = np.sum(fluid) * h**2

print("Area =", A)


# ============================================================
# 4. Number all fluid pixels
# ============================================================

# Each fluid pixel gets a number:
#
# -1 means solid/wall
#  0, 1, 2, ... are unknown velocity indices

index_map = -np.ones(fluid.shape, dtype=int)

index_map[fluid] = np.arange(np.sum(fluid))

N = np.sum(fluid)

print("Number of unknowns =", N)


# ============================================================
# 5. Create sparse matrix A and vector b
# ============================================================

A_matrix = lil_matrix((N, N), dtype=float)

b = np.full(
    N,
    G_over_mu * h**2,
    dtype=float
)


# ============================================================
# 6. Build the equations
# ============================================================

start_build = time.time()


for i in range(1, img.shape[0] - 1):

    for j in range(1, img.shape[1] - 1):

        # Only create equation for fluid pixels
        if fluid[i, j]:

            # Equation number for this pixel
            p = index_map[i, j]


            # Diagonal term: 4*u_P
            A_matrix[p, p] = 4.0


            # ----------------------------------------
            # North neighbor
            # ----------------------------------------

            if fluid[i - 1, j]:

                n = index_map[i - 1, j]

                A_matrix[p, n] = -1.0


            # ----------------------------------------
            # South neighbor
            # ----------------------------------------

            if fluid[i + 1, j]:

                s = index_map[i + 1, j]

                A_matrix[p, s] = -1.0


            # ----------------------------------------
            # West neighbor
            # ----------------------------------------

            if fluid[i, j - 1]:

                w = index_map[i, j - 1]

                A_matrix[p, w] = -1.0


            # ----------------------------------------
            # East neighbor
            # ----------------------------------------

            if fluid[i, j + 1]:

                e = index_map[i, j + 1]

                A_matrix[p, e] = -1.0


build_time = time.time() - start_build

print("Matrix construction time =", build_time, "seconds")


# ============================================================
# 7. Convert matrix to CSR format
# ============================================================

A_matrix = A_matrix.tocsr()

print("Sparse matrix shape =", A_matrix.shape)

print("Number of non-zero elements =", A_matrix.nnz)


# ============================================================
# 8. Solve A*u = b
# ============================================================

print("\nSolving sparse linear system...")

start_solve = time.time()


u_vector = spsolve(A_matrix, b)


solve_time = time.time() - start_solve

print("Solve time =", solve_time, "seconds")


# ============================================================
# 9. Put solution back into image-shaped array
# ============================================================

u = np.zeros_like(img, dtype=float)

u[fluid] = u_vector


# ============================================================
# 10. Calculate residual
# ============================================================

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


print("RMS residual =", residual_rms)


# ============================================================
# 11. Calculate Q
# ============================================================

Q = np.sum(u[fluid]) * h**2

print("\nQ flow rate =", Q)


# ============================================================
# 12. Calculate shape coefficient
# ============================================================

C_shape = A**2 / Q

print("Shape coefficient C =", C_shape)


# ============================================================
# 13. Create velocity image
# ============================================================

u_max = np.max(u[fluid])

velocity_img = np.zeros_like(u, dtype=np.uint8)

velocity_img[fluid] = (
    255 * u[fluid] / u_max
).astype(np.uint8)


velocity_image = Image.fromarray(velocity_img)

velocity_image.save(f"velocity{inp}")


print(f"Velocity image saved as velocity{inp}")
