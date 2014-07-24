# This script generates an SVG file showing the Rosenbrock function.
# The code originates from the public domain code at http://commons.wikimedia.org/wiki/File:Rosenbrock_function.svg.

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib.colors import LogNorm
import matplotlib.pyplot as plt
import numpy as np
 

fig = plt.figure()
ax = fig.gca(projection='3d')
ax.view_init(elev=90, azim=-90)
ax.set_axis_off()
ax.dist = 100
s = .05
X = np.arange(-2, 2.+s, s)
Y = np.arange(-1, 3.+s, s)
X, Y = np.meshgrid(X, Y)
Z = (1.-X)**2 + 100.*(Y-X*X)**2
ax.plot_surface(X, Y, Z, rstride=1, cstride=1, norm=LogNorm(), cmap=cm.jet, linewidth=0)
 
plt.savefig("rosenbrock.png", dpi=1200)
 
plt.show()
