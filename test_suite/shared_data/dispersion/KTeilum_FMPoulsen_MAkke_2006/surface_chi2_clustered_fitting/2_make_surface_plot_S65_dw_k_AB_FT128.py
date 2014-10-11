import numpy as np
import scipy.interpolate
from numpy.ma import masked_where

from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm

resfile = open('1_create_surface_data_S65_dw_k_AB_FT128.txt', 'r')

lines = resfile.readlines()
resfile.close()

params = lines[0].split()[1:]
mp = lines[1].split()
mp_x = np.array([float(mp[0])])
mp_y = np.array([float(mp[1])])
mp_z = np.array([float(mp[2])])
min_point = np.concatenate((mp_x, mp_y, mp_z))

# Collect data
x = []
y = []
z = []

nr_dp = len(lines[2:])

for line in lines[2:]:
    x_l, y_l, z_l = line.split()
    x.append(float(x_l))
    y.append(float(y_l))
    z.append(float(z_l))

# Make numpy arrays
x = np.asarray(x)
y = np.asarray(y)
z = np.asarray(z)

x_min = x.min()
x_max = x.max()
y_min = y.min()
y_max = y.max()
z_min = z.min()
z_max = z.max()


# Expand axis and tile, to make mesh.
x_tile = np.tile(x[np.newaxis, Ellipsis], (nr_dp, 1) )
y_tile = np.tile(y[Ellipsis, np.newaxis], (1, nr_dp) )

# Or do it by meshgrid
x_mesh, y_mesh = np.meshgrid(x, y)

# Test if new axis and tiling is the same
print np.array_equal(x_tile, x_mesh)
print np.array_equal(y_tile, y_mesh)

# 2d contour plot from 3 lists : x, y and z?
# http://stackoverflow.com/questions/9008370/python-2d-contour-plot-from-3-lists-x-y-and-rho

# Set up a regular grid of interpolation points
int_points = 300
xi, yi = np.linspace(x_min, x_max, int_points), np.linspace(y_min, y_max, int_points)
xi, yi = np.meshgrid(xi, yi)

# This causes memor problem or a very long time.
#rbf = scipy.interpolate.Rbf(x, y, z, function='linear')
#zi = rbf(xi, yi)

zi = scipy.interpolate.griddata((x, y), z, (xi, yi), method='linear')
#z_mesh = scipy.interpolate.griddata((x, y), z, (x_mesh, y_mesh), method='linear')

fig = plt.figure()
ax = fig.gca(projection='3d')

# Set which x, y, z to plot
x_p = xi
y_p = yi
z_p = zi

# Replace out-lier value.
# First get index os largest values
out_val = 5*z_min
z_p_mask = masked_where(z_p >= out_val, z_p)
z_mask = masked_where(z >= out_val, z)

# Replace with 0.0
z_p[z_p_mask.mask] = 0.0
z[z_mask.mask] = 0.0
# Find new max
new_max = np.max(z_p)
z_p[z_p_mask.mask] = new_max
z[z_mask.mask] = new_max

ax.plot_surface(x_p, y_p, z_p, rstride=8, cstride=8, alpha=0.3)

cset = ax.contour(x_p, y_p, z_p, zdir='z', offset=0, cmap=cm.coolwarm)
cset = ax.contour(x_p, y_p, z_p, zdir='x', offset=x_min, cmap=cm.coolwarm)
cset = ax.contour(x_p, y_p, z_p, zdir='y', offset=y_min, cmap=cm.coolwarm)

ax.scatter(mp_x, mp_y, mp_z, c='r', marker='o', s=200)
ax.scatter(x, y, z, c='b', marker='o', s=5)

ax.set_xlabel('%s'%params[0])
ax.set_xlim(x_min, x_max)

ax.set_ylabel('%s'%params[1])
ax.set_ylim(y_min, y_max)

ax.set_zlabel('%s'%params[2])
ax.set_zlim(0, out_val)

plt.show()


