# Create the data pipe.
pipe.create(pipe_name='frame order', pipe_type='frame order')

# Select the model.
frame_order.select_model('free rotor')

# The eigenframe.
axis_alpha = pi / 2.0

# Set the average domain position translation parameters.
value.set(param='ave_pos_x', val=0.0)
value.set(param='ave_pos_y', val=0.0)
value.set(param='ave_pos_z', val=0.0)
value.set(param='ave_pos_alpha', val=0.0)
value.set(param='ave_pos_beta', val=0.0)
value.set(param='ave_pos_gamma', val=0.0)
value.set(param='axis_alpha', val=axis_alpha)
value.set(param='cone_sigma_max', val=0.0)

# Set the pivot.
frame_order.pivot(pivot=[1, 0, 0], fix=True)

# Create the PDB.
frame_order.pdb_model(inc=10, size=45, rep='free_rotor', force=True)
