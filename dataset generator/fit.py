import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

# -------------------------
# Read CSV
# -------------------------

df = pd.read_csv("results.csv")


# -------------------------
# Model
# -------------------------

def model(N, a, b, c):
    return a + b * N**c


# -------------------------
# Fit each Sides
# -------------------------

results = []

for side, group in df.groupby("Sides"):

    N = group["Resolution"].values.astype(float)
    C = group["C_shape"].values.astype(float)

    # Sort by resolution
    idx = np.argsort(N)
    N = N[idx]
    C = C[idx]

    # Automatic initial guesses
    a0 = C.max() * 1.01
    b0 = C.min() - a0
    c0 = -1.0

    p0 = [a0, b0, c0]

    try:
        params, covariance = curve_fit(
            model,
            N,
            C,
            p0=p0,
            maxfev=100000
        )

        a, b, c = params

        errors = np.sqrt(np.diag(covariance))


        C_pred = model(N, a, b, c)

        SS_res = np.sum((C - C_pred)**2)
        SS_tot = np.sum((C - np.mean(C))**2)

        R2 = 1 - SS_res / SS_tot

        results.append({
            "Sides": side,
            "a": a,
            "a_error": errors[0],
            "b": b,
            "b_error": errors[1],
            "c": c,
            "c_error": errors[2],
	    "R2" : R2
        })

    except RuntimeError:
        print(f"Fit failed for side = {side}")


# -------------------------
# Save results
# -------------------------

results_df = pd.DataFrame(results)

print(results_df)

results_df.to_csv(
    "extrapolated_results.csv",
    index=False
)
