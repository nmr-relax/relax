# Script for calculation RDCs and PCSs for the rigid frame order model.

# relax module imports.
from generic_fns.mol_res_spin import spin_loop


# Create a data pipe.
pipe.create('bc', 'N-state')

# Load the average C-domain pos.
structure.read_pdb('ave_pos')

# Load the spins.
structure.load_spins('@N')
structure.load_spins('@H')

# Load the NH vectors.
structure.vectors(spin_id='@N', attached='H', ave=False)

# Set the values needed to calculate the dipolar constant.
value.set(1.041 * 1e-10, 'bond_length', spin_id="@N")
value.set('15N', 'heteronucleus', spin_id="@N")
value.set('1H', 'proton', spin_id="@N")

# Load the tensors.
execfile('../../tensors.py')

# Set up the model.
n_state_model.select_model(model='fixed')

# Set the paramagnetic centre.
paramag.centre(pos=[35.934, 12.194, -4.206])

# Loop over the alignments.
ids = ['dy', 'tb', 'tm', 'er']
for id in ids:
    # Load the distribution-based PCS.
    pcs.read(align_id=id, file='pcs_%s.txt'%id, dir='..', res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

    # The temperature and field strength.
    temperature(id=id, temp=303)
    frq.set(id=id, frq=900e6)

    # Back-calculate the data.
    rdc.back_calc(id)
    pcs.back_calc(id)

    # Set 1 Hz and 0.1 ppm errors on all data.
    for spin in spin_loop():
        # Init.
        if not hasattr(spin, 'rdc_err'):
            spin.rdc_err = {}
        if not hasattr(spin, 'pcs_err'):
            spin.pcs_err = {}

        # Set the errors.
        spin.rdc_err[id] = 1.0
        spin.pcs_err[id] = 0.1

    # Write the data.
    rdc.write(align_id=id, file='ave_pos_rdc_%s.txt'%id, bc=True, force=True)
    pcs.write(align_id=id, file='ave_pos_pcs_%s.txt'%id, bc=True, force=True)

# Calculate Q-factors.
rdc.calc_q_factors()
pcs.calc_q_factors()

# Grace plot.
file = open('pcs_comp.agr', 'w')

# Real data plotted.
for i in range(len(ids)):
    # Header.
    file.write("@target G0.S%i\n@type xy\n" % i)

    # The spin data.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        # The data.
        if hasattr(spin, 'rdc'):
            file.write("%s %s\n" % (res_num, spin.rdc[ids[i]])
    # End.
    file.write("&\n")

# Ave structure data plotted.
for i in range(len(ids)):
    # Header.
    file.write("@target G1.S%i\n@type xy\n" % i)

    # The spin data.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        # The data.
        if hasattr(spin, 'rdc_bc'):
            file.write("%s %s\n" % (res_num, spin.rdc_bc[ids[i]])
    # End.
    file.write("&\n")


# Store the state.
state.save('ave_pos_back_calc', force=True)
