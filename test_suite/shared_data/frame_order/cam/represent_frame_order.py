# Load the final state.
state.load('frame_order')

# Re-create the PDB representation (for debugging).
frame_order.pdb_model(ave_pos='ave_pos', rep='frame_order', dist=None, compress_type=2, force=True)

# PyMOL.
pymol.view()
pymol.command('show spheres')
pymol.frame_order(ave_pos='ave_pos_true', rep='frame_order_true', dist=None)
pymol.frame_order(ave_pos='ave_pos_fixed_piv', rep='frame_order_fixed_piv', dist=None)
pymol.frame_order(ave_pos='ave_pos', rep='frame_order', dist=None)
