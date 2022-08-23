# %%
from sympy import symbols, Eq, Function
from sympy import I
from sympy.solvers.ode.systems import dsolve_system
import sympy.functions.elementary.complexes as comp
from sympy.plotting import plot

f, g = symbols("f g", cls=Function)
t = symbols("t")
w1 = symbols("w1")
w2 = symbols("w2")
D = symbols("D")

eqs = [Eq(f(t).diff(t),
          I * comp.Abs(w1**2) / D * f(t) + I * w1*comp.conjugate(w2) / D * g(t)),
       Eq(g(t).diff(t),
          I * comp.Abs(w2**2) / D * f(t) + I * w2*comp.conjugate(w1) / D * f(t))]
ics = {f(0): 1, g(0): 0}
solution = dsolve_system(eqs=eqs, ics=ics)
solution = solution[0]
substitution_values = {w1: 1, w2: 1, D: 30}
f_abs = comp.Abs(solution[0].rhs.subs(substitution_values))
# %%
p = plot(comp.Abs(solution[0].rhs.subs(substitution_values)), xlim=(-100, 100), ylim=(-20, 20))
# %%
from sympy.utilities.lambdify import lambdify
lam_f = lambdify(t, f_abs)


import numpy as np
import matplotlib.pyplot as plt
x = np.linspace(-100, 100, 300)
y = lam_f(x)

plt.plot(x, y)
