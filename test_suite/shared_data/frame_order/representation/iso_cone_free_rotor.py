from numpy import array, float64, zeros

from lib.geometry.coord_transform import cartesian_to_spherical
from lib.geometry.rotations import euler_to_R_zyz
from lib.frame_order.conversions import create_rotor_axis_spherical


# Create the data pipe.
pipe.create(pipe_name='frame order', pipe_type='frame order')

# Select the model.
frame_order.select_model('iso cone, free rotor')

# The eigenframe.
axis_theta = 0.0
axis_phi = 0.0

# Set the average domain position translation parameters.
value.set(param='ave_pos_x', val=0.0)
value.set(param='ave_pos_y', val=0.0)
value.set(param='ave_pos_z', val=0.0)
value.set(param='ave_pos_alpha', val=0.0)
value.set(param='ave_pos_beta', val=0.0)
value.set(param='ave_pos_gamma', val=0.0)
value.set(param='axis_theta', val=axis_theta)
value.set(param='axis_phi', val=axis_phi)
value.set(param='cone_theta', val=2.0)

# Set the pivot.
frame_order.pivot(pivot=[1, 1, 1], fix=True)

# Create the PDB.
frame_order.pdb_model(inc=10, size=45, rep='iso_cone_free_rotor', force=True)
