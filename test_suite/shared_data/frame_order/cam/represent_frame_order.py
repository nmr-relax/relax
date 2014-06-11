# Load the final state.
state.load('frame_order')

# Re-create the PDB representation (for debugging).
frame_order.pdb_model(ave_pos_file='ave_pos.pdb.gz', rep_file='frame_order.pdb.gz', dist_file=None, force=True)

# PyMOL.
pymol.view()
pymol.command('show spheres')
pymol.frame_order(ave_pos_file='ave_pos_true.pdb.gz', rep_file='frame_order_true.pdb.gz', dist_file=None)
pymol.frame_order(ave_pos_file='ave_pos_fixed_piv.pdb.gz', rep_file='frame_order_fixed_piv.pdb.gz', dist_file=None)
pymol.frame_order(ave_pos_file='ave_pos.pdb.gz', rep_file='frame_order.pdb.gz', dist_file=None)
