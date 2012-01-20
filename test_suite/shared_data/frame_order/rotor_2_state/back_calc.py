# Script for calculation RDCs and PCSs for the rigid frame order model.

# relax module imports.
from generic_fns.mol_res_spin import spin_loop


# Create a data pipe.
pipe.create('bc', 'N-state')

# Load the C-domain distribution.
structure.read_pdb('distribution')

# Load the spins.
structure.load_spins('@N')
structure.load_spins('@H')

# Load the NH vectors.
structure.vectors(spin_id='@N', attached='H', ave=False)

# Set the values needed to calculate the dipolar constant.
value.set(1.041 * 1e-10, 'r', spin_id="@N")
value.set('15N', 'heteronuc_type', spin_id="@N")
value.set('1H', 'proton_type', spin_id="@N")

# Load the tensors.
execfile('../tensors.py')

# Set up the model.
n_state_model.select_model(model='fixed')

# Set the paramagnetic centre.
paramag.centre(pos=[35.934, 12.194, -4.206])

# Loop over the alignments.
tensors = ['dy', 'tb', 'tm', 'er']
for i in range(len(cdp.align_tensors)):
    # The tag.
    tag = cdp.align_tensors[i].name

    # The temperature and field strength.
    temperature(id=tag, temp=303)
    frq.set(id=tag, frq=900e6)

    # Back-calculate the data.
    rdc.back_calc(tag)
    pcs.back_calc(tag)

    # Set 1 Hz and 0.1 ppm errors on all data.
    for spin in spin_loop():
        # Init.
        if not hasattr(spin, 'rdc_err'):
            spin.rdc_err = {}
        if not hasattr(spin, 'pcs_err'):
            spin.pcs_err = {}

        # Set the errors.
        spin.rdc_err[tag] = 1.0
        spin.pcs_err[tag] = 0.1

    # Write the data.
    rdc.write(align_id=tag, file='rdc_%s.txt'%tensors[i], bc=True, force=True)
    pcs.write(align_id=tag, file='pcs_%s.txt'%tensors[i], bc=True, force=True)

# Store the state.
state.save('back_calc', force=True)
