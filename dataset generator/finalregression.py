import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# =========================
# Read CSV
# =========================

df = pd.read_csv("extrapolated_results.csv")

x = df["Sides"].values.astype(float)
y = df["a"].values.astype(float)

idx = np.argsort(x)
x = x[idx]
y = y[idx]


# =========================
# Model
# y = A + B*x^C
# =========================

def model(x, A, B, C):
    return A + B * x**C


# =========================
# Initial guess
# =========================

A0 = y[-1]
B0 = y[0] - A0
C0 = -1.0

p0 = [A0, B0, C0]


# =========================
# Fit
# =========================

params, covariance = curve_fit(
    model,
    x,
    y,
    p0=p0,
    maxfev=100000
)

A, B, C = params


errors = np.sqrt(np.diag(covariance))

A_err, B_err, C_err = errors


# =========================
# R²
# =========================

y_pred = model(x, A, B, C)

SS_res = np.sum((y - y_pred)**2)
SS_tot = np.sum((y - np.mean(y))**2)

R2 = 1 - SS_res / SS_tot


# =========================
# Print results
# =========================

print("\n===== FIT RESULTS =====")

print(f"A = {A:.10f} ± {A_err:.10f}")
print(f"B = {B:.10f} ± {B_err:.10f}")
print(f"C = {C:.10f} ± {C_err:.10f}")

print(f"R² = {R2:.10f}")


# =========================
# Smooth curve
# =========================

x_fit = np.linspace(x.min(), x.max(), 1000)
y_fit = model(x_fit, A, B, C)


# =========================
# Plot
# =========================

plt.figure(figsize=(9, 6))

plt.scatter(
    x,
    y,
    label="Data"
)

plt.plot(
    x_fit,
    y_fit,
    label=fr"Fit: $A + Bx^C$"
)

plt.xlabel("Number of sides")
plt.ylabel("a")

plt.title("Extrapolated continuum value vs number of sides")

plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
