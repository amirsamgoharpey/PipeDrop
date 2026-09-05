# PipeDrop

> A 2D Pipe Pressure Drop Solver

---

## Overview

**PipeDrop** is a computational tool for calculating pressure drop in pipes with arbitrary cross-sectional geometries by numerically solving the governing flow equation under a set of simplifying physical assumptions.

The main goal of the project is to investigate how the geometry of a pipe cross-section affects its velocity profile, flow rate, and pressure drop.

---

## Motivation

The idea for this project started with a question in a Fluid Mechanics class two years ago:

> **What is the pressure drop for an arbitrary regular polygon?**

In Landau's *Fluid Mechanics*, an analytical solution can be found for flow through a triangular cross-section. At the time, we gave up on trying to find a general analytical solution.

However, the question stayed with me:

> **Is there a general relation for the pressure drop of a regular polygon with** `n` **sides?**

PipeDrop started as an attempt to explore this question computationally.

Rather than deriving an analytical solution for every possible geometry, PipeDrop solves the governing equation numerically and allows the pressure drop to be investigated for arbitrary cross-sectional shapes.

---

## Physical Problem

PipeDrop currently considers steady, incompressible, laminar flow of a Newtonian fluid with constant viscosity.

The main assumptions are:

* Steady flow
* Incompressible fluid
* Newtonian fluid
* Constant viscosity
* Laminar flow
* Fully developed flow
* No-slip boundary condition at the pipe wall
* Straight pipe
* Two-dimensional cross-section

Under these assumptions, the three-dimensional flow problem can be reduced to a two-dimensional problem over the pipe cross-section.

### Governing Equations

The flow is governed by the incompressible Navier–Stokes equations.

The continuity equation is

$$\nabla \cdot \mathbf{u} = 0$$

where $\mathbf{u}$ is the velocity field.

The momentum equation is

$$\rho(\mathbf{u}\cdot\nabla)\mathbf{u} = -\nabla p+\mu\nabla^2\mathbf{u}$$

where $\rho$ is the fluid density, $p$ is the pressure, and $\mu$ is the dynamic viscosity.

For steady, fully developed flow through a straight pipe, the velocity is assumed to have only an axial component:

$$\mathbf{u} = \begin{pmatrix} 0 ,\\ 0 ,\\ u(x,y) \end{pmatrix}$$

Here, $x$ and $y$ describe the pipe cross-section, while $u(x,y)$ is the axial velocity.

Since the flow is fully developed, the velocity does not vary along the pipe axis:

$$\frac{\partial u}{\partial z}=0$$
The velocity has no transverse components, so the convective term vanishes:

$$(\mathbf{u}\cdot\nabla)\mathbf{u}=0$$

The axial component of the Navier–Stokes equation therefore becomes

$$0 = -\frac{\partial p}{\partial z} + \mu \left( \frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2} \right)$$

Rearranging gives

$$\frac{\partial^2 u}{\partial x^2} + \frac{\partial^2 u}{\partial y^2} = \frac{1}{\mu}\frac{\partial p}{\partial z}$$

Since the pressure gradient is constant for fully developed flow,

$$\nabla_\perp^2 u = \frac{1}{\mu}\frac{dp}{dz} = \frac{-G}{\mu}$$

where

$$ G = -\frac{dp}{dz}$$

and

$$\nabla_\perp^2 = \frac{\partial^2}{\partial x^2} + \frac{\partial^2}{\partial y^2}$$

is the Laplacian over the pipe cross-section.

This is a **Poisson equation for the axial velocity field**.

The no-slip boundary condition at the pipe wall is

$$u(x,y)=0 \qquad \text{on the boundary}$$

Once the velocity field is obtained, the volumetric flow rate is calculated from

$$Q=\int_A u(x,y)\,dA$$

with

$$\boxed{u=0 \quad\text{on the pipe boundary}}$$

---

## Dimensionless Shape Factor

Since PipeDrop takes the pipe cross-section directly from a grayscale image, the geometry is initially defined in pixels rather than physical units.

Therefore, quantities such as the volumetric flow rate $Q$ and pressure gradient $\frac{dp}{dz}$ do not have an absolute physical scale unless a physical length scale is assigned to the input image.

To compare different geometries and image resolutions independently of this arbitrary scale, PipeDrop uses a dimensionless shape factor $C$.

The pressure gradient is related to the volumetric flow rate by

$$G = C\frac{\mu Q}{A^2}$$

where

* $C$ is the dimensionless shape factor,
* $\mu$ is the dynamic viscosity,
* $Q$ is the volumetric flow rate,
* $A$ is the cross-sectional area.

Therefore,

$$\boxed{C = \frac{A^2}{\mu Q}G}$$

The shape factor depends only on the geometry of the cross-section under the assumptions of steady, incompressible, fully developed, laminar flow.

This provides a convenient way to compare different cross-sectional geometries without requiring an absolute physical scale for the input image.

For geometrically similar shapes represented at different resolutions, the computed value of `$C$` should converge toward the same limiting value as the numerical resolution is increased.

---

## Method

The core of PipeDrop solves the resulting Poisson equation numerically by discretizing the pipe cross-section.

The general workflow is:

1. Generate or provide the desired pipe geometry.
2. Convert the cross-section into a computational grid.
3. Identify fluid and wall regions.
4. Discretize the Poisson equation using finite differences.
5. Construct the resulting linear system.
6. Solve for the velocity field.
7. Calculate the volumetric flow rate.
8. Calculate the pressure gradient and pressure drop.
9. Compute the dimensionless shape factor $C$.

### Numerical Method

* **Discretization:** Finite Difference Method (FDM)
* **Governing equation:** 2D Poisson equation
* **Linear system:** $A\mathbf{u}=\mathbf{b}$
* **Linear solver:** SciPy sparse linear solver
* **Boundary condition:** No-slip, $u=0$, at the pipe wall

---

## Geometry

PipeDrop is designed to work with arbitrary cross-sectional geometries.

The cross-section is provided as a grayscale image. Each pixel is classified as either fluid or solid according to its grayscale value.

Pixels with grayscale values **above 128** are treated as fluid, while pixels with grayscale values **at or below 128** are considered solid walls.

This allows PipeDrop to work with geometries that are difficult or impossible to describe analytically.

### Example Geometry

![Random pipe geometry](/png/random%20cross%20section/random.png)

The corresponding velocity field is(white pixels are the fastest and the black pixels are zero velocity):

![Random pipe velocity profile](/png/random%20cross%20section/velocityrandom.png)


> resolution : 256


---

## Results

The solver calculates the velocity distribution over the pipe cross-section and uses it to determine the corresponding flow rate, pressure gradient, and shape factor.

The main outputs are:

* **Velocity field** — saved as a PNG image
* $Q$ — volumetric flow rate in computational units
* $\frac{dp}{dz}$ — pressure gradient in computational units
* $C$ — dimensionless shape factor

### Example Result

For example, a circular cross-section evaluated at a $2048\times2048$ resolution produced:

| Quantity                 |              Value |
| ------------------------ | -----------------: |
| Geometry                 |             Circle |
| Grid resolution          |   $2048\times2048$ |
| Cross-sectional area     |   1,731,076 pixels |
| Volumetric flow rate $Q$ | 119467650396.47943 |
| Shape factor $C$         |  25.08314265687029 |

---

## Validation

The numerical solver is validated using geometries for which an analytical solution is available.

The validation focuses on two questions:

1. Does the numerical solution converge as the grid resolution is increased?
2. Does the converged numerical result agree with the analytical solution?

### Test Case 1 — Circular Cross-Section

A circular pipe is used as the first validation case because its analytical solution is known.

For a circular cross-section, the exact dimensionless shape factor is

$$C_{\mathrm{exact}} = 8\pi \approx 25.132741$$

Because PipeDrop represents the geometry using pixels, the numerical result depends on the resolution of the input image.

The same circular geometry is therefore evaluated at several different resolutions.

### Resolution Study

The computational cost increases with the grid resolution because a finer grid produces a larger numerical system.

The computed shape factor for each resolution and the time taken is recorded below:

|  Grid Resolution | Computed `C_N` | time(s) |
| ---------------: | -------------: | -------------: |
|  `256`  |            24.7862137 |                0.4      |
|  `512`  |            24.9379812 |             3.0         |
|  `1024` |            25.0484250 |           11.5          |
| `2048`  |            25.0831427 |          99.6           |

The values of C are then fitted as a function of the grid resolution $N$.

### Regression and Extrapolation

The numerical results are fitted using a power-law convergence model of the form

$$C(N)=a+bN^c$$

where $N$ is the grid resolution and $a$, $b$, and $c$ are fitting parameters.

For a convergent numerical method, the exponent satisfies

$c<0$

so that

$$\lim_{N\rightarrow\infty}N^c=0$$

Therefore, the asymptotic value predicted by the regression is

$$\boxed{C_{\mathrm{expected}}=a}$$

This extrapolated value represents the estimated infinite-resolution result of the numerical method.

The regression result will be reported as

$$\boxed{C(N)=a+bN^c}$$

with the fitted values of $a$, $b$, and $c$.

The estimated infinite-resolution value is then compared with the analytical result

$$C_{\mathrm{exact}}=8\pi$$

The final validation therefore compares the **extrapolated infinite-resolution value**, rather than an individual finite-resolution simulation, with the analytical solution.

### Validation Summary

| Quantity                             |              Value |
| ------------------------------------ | -----------------: |
| Analytical $C$                       | $8\pi \approx 25.132741$ |
| Regression model                     |            $C(N)=a+bN^c$ |
| Extrapolated $C_{\mathrm{expected}}$ |                 25.15558 |
| Relative error                       |                    0.09% |


---


## Dataset Generation

After validating the numerical solver, PipeDrop is used to investigate the original question:

> **Is there a general relation between the shape factor and the number of sides of a regular polygon?**

To investigate this numerically, a dataset of regular polygonal cross-sections is generated and solved using PipeDrop.

The geometry generator creates regular polygons with different numbers of sides while keeping the cross-sectional area fixed. Each generated geometry is converted into a grayscale image and passed to the solver.

The main parameters varied during dataset generation are:

* Number of polygon sides \(n\)
* Grid resolution

The generated data can then be analyzed to investigate the relationship between \(C\) and \(n\).

### Data Analysis

Matplotlib is used to visualize and analyze the generated dataset. The computed values of $C$ can be plotted as a function of the number of polygon sides:

$C=C(n)$

This plot makes it possible to identify the trend we are looking for. then The analysis allows the numerical data to be compared with the regression model to determine whether the proposed regression form is appropriate.

### Final Regression

The numerical results are fitted using a nonlinear power-law model:

$C(n)=a+bn^c$

where $a$, $b$, and $c$ are obtained from the final regression.

For large $n$, the polygon approaches a circular cross-section. Therefore, if \(c<0\), the model approaches

$$\lim_{n\rightarrow\infty}C(n)=a$$

This makes $a$ the predicted shape factor in the infinite-sided limit.

The regression is not only used to obtain a convenient fitting curve, but also to investigate whether a simple mathematical relation can describe the dependence of hydraulic resistance on polygon geometry.

### Even and Odd Polygons

An important consideration in this analysis is the difference between polygons with an even and an odd number of sides.

When the numerical data are fitted using a single smooth function of $n$, the even and odd sequences may introduce different numerical behavior. This can be particularly important when the geometry is represented on a Cartesian pixel grid.

For example, using only even-sided polygons to fit the regression and then predicting a triangular cross-section (\(n=3\)) requires extrapolation beyond the fitted data range. Such an extrapolation can produce a significantly larger error.

In contrast, if the regression is trained on odd-sided polygons, the even-sided polygons can lie between the available training points. In that case, their prediction becomes an interpolation problem rather than an extrapolation problem.

This distinction is important because interpolation is generally more reliable than extrapolation.

Therefore, the regression analysis should not be evaluated only by how well the fitted curve describes the points used to obtain it. The model should also be tested on polygon geometries that were not included in the fitting process.

The final analysis will therefore consider:

* The overall regression using all available polygon data
* The regression using only even-sided polygons
* The regression using only odd-sided polygons
* Predictions for excluded polygon geometries
* The corresponding prediction errors

This allows the robustness of the proposed relation $C(n)=a+bn^c$ to be investigated rather than assuming that a good visual fit automatically implies a valid predictive model.

### Regression Results

The final fitted relation is reported in the following form:

$C(n)=a+bn^c$

with the fitted parameters for 3 to 50 sides polygons :

| Parameter | Value |
| --------- | ----: |
| $R^2$     |    0.9993   |
| $a$     |   25.154 ± 0.006 |
| $b$    |   430  ±  10|
| $c$     |   -3.48 ± 0.03 |

![main question solution](png/polygon%20data.png)



Dataset generator structure:
```text
1. generator.py (generates the polygons for the solver) -> creates the polygons folder and the n-gon folder
2. solver.py ( a special version of main code for working with the generated polygons) -> creates the results.csv file
3. fit.py (for the problem with pixelation) -> creates the extrapolated_results.csv
4. finalregression.py (for the final regression) -> gives out the a,b,c and the graph of C(n)
5. testfit.py (for checking the regression) -> gives out the relative error of using only odd data to find the even data and vice versa
```

---

## Installation

### Requirements

* Python3
* NumPy
* SciPy
* Matplotlib (for data set analyze)

### Installation

```bash
git clone https://github.com/amirsamgoharpey/PipeDrop.git
cd PipeDrop

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

---

## Limitations

The current version has several limitations:

* The current model is restricted to steady, incompressible, laminar, fully developed flow.
* The geometry is represented using a pixel-based Cartesian grid.
* Pixelation introduces a resolution-dependent approximation of the actual geometry.
* The current solver is intended for arbitrary cross-sectional shapes but does not yet model three-dimensional effects.
* The physical length scale of the input image must be specified separately if dimensional physical quantities are required.

---


## References

1. Landau and Lifshitz, *Fluid Mechanics*


---

