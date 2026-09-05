import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


# ============================================================
# 1. CSV
# ============================================================

df = pd.read_csv("extrapolated_results.csv")

df = df.sort_values("Sides")


# ============================================================
# 2. model
# ============================================================
# a(Sides) = A + B * Sides^C

def model(x, A, B, C):
    return A + B * x**C


# ============================================================
# 3. even or odd
# ============================================================

odd = df[df["Sides"] % 2 == 1]
even = df[df["Sides"] % 2 == 0]

### if you want the vice versa just change the 1 in odd to 0 and the 0 in even to 1

# training data
x_train = odd["Sides"].values.astype(float)
y_train = odd["a"].values.astype(float)


# test data
x_test = even["Sides"].values.astype(float)
y_test = even["a"].values.astype(float)


print("Number of odd data points :", len(x_train))
print("Number of even data points:", len(x_test))


# ============================================================
# 4. inital guess
# ============================================================

A0 = y_train.max()

C0 = -1.0

B0 = y_train[0] - A0
B0 = B0 / (x_train[0] ** C0)

p0 = [A0, B0, C0]


print("\nInitial guess:")
print("A0 =", A0)
print("B0 =", B0)
print("C0 =", C0)


# ============================================================
# 5. Fiting on train data
# ============================================================

params, covariance = curve_fit(
    model,
    x_train,
    y_train,
    p0=p0,
    maxfev=100000
)


A, B, C = params


parameter_errors = np.sqrt(np.diag(covariance))

A_error = parameter_errors[0]
B_error = parameter_errors[1]
C_error = parameter_errors[2]


y_train_pred = model(x_train, A, B, C)

SS_res = np.sum((y_train - y_train_pred) ** 2)
SS_tot = np.sum((y_train - np.mean(y_train)) ** 2)

R2_train = 1 - SS_res / SS_tot


# ============================================================
# 6. test data prediction
# ============================================================

y_test_pred = model(x_test, A, B, C)


# ============================================================
# 7. error on prediction data
# ============================================================

errors = y_test - y_test_pred

absolute_errors = np.abs(errors)

relative_errors = (
    np.abs(errors / y_test) * 100
)


MAE = np.mean(absolute_errors)

RMSE = np.sqrt(
    np.mean(errors ** 2)
)

mean_relative_error = np.mean(relative_errors)


# ============================================================
# 8. results
# ============================================================

print("\n")
print("=" * 60)
print("FIT RESULTS")
print("=" * 60)

print(f"A = {A:.12f} ± {A_error:.12f}")
print(f"B = {B:.12f} ± {B_error:.12f}")
print(f"C = {C:.12f} ± {C_error:.12f}")

print(f"\nR² (training) = {R2_train:.12f}")


print("\n")
print("=" * 80)
print("EVEN-SIDE PREDICTIONS")
print("=" * 80)

print(
    f"{'Sides':>8}"
    f"{'Actual':>18}"
    f"{'Predicted':>18}"
    f"{'Error':>18}"
    f"{'Relative Error':>18}"
)

print("-" * 80)


for side, actual, predicted, error, relative in zip(
    x_test,
    y_test,
    y_test_pred,
    errors,
    relative_errors
):

    print(
        f"{int(side):>8}"
        f"{actual:>18.10f}"
        f"{predicted:>18.10f}"
        f"{error:>+18.10f}"
        f"{relative:>17.6f}%"
    )


print("\n")
print("=" * 60)
print("TEST ERROR")
print("=" * 60)

print(f"MAE                 = {MAE:.12f}")
print(f"RMSE                = {RMSE:.12f}")
print(f"Mean relative error = {mean_relative_error:.8f}%")

x_curve = np.linspace(
    x_train.min(),
    x_train.max(),
    1000
)

y_curve = model(
    x_curve,
    A,
    B,
    C
)

plt.figure(figsize=(10, 6))

plt.scatter(
    x_train,
    y_train,
    label="Odd sides (training)"
)


plt.scatter(
    x_test,
    y_test,
    marker="x",
    s=70,
    label="Even sides (actual)"
)


plt.plot(
    x_curve,
    y_curve,
    label=r"Fit: $A + Bx^C$"
)


plt.scatter(
    x_test,
    y_test_pred,
    marker="o",
    facecolors="none",
    label="Even sides (predicted)"
)


plt.xlabel("Number of sides")
plt.ylabel("a")

plt.title(
    "Fit using odd sides and prediction of even sides"
)

plt.grid(True)
plt.legend()

plt.tight_layout()

plt.show()
