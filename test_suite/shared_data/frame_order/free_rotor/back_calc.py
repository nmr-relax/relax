# Script for calculation RDCs and PCSs for the rigid frame order model.

# relax module imports.
from generic_fns.interatomic import interatomic_loop
from generic_fns.mol_res_spin import spin_loop


# Create a data pipe.
pipe.create('bc', 'N-state')

# Load the C-domain distribution.
structure.read_pdb('distribution')

# Load the spins.
structure.load_spins('@N')
structure.load_spins('@H')

# Define the magnetic dipole-dipole relaxation interaction.
dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
dipole_pair.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
dipole_pair.unit_vectors(ave=False)

# Set the nuclear isotope type.
spin.isotope(isotope='15N', spin_id='@N')
spin.isotope(isotope='1H', spin_id='@H')

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

    # Set 1 Hz errors on all RDC data.
    for interatom in interatomic_loop():
        # Init.
        if not hasattr(interatom, 'rdc_err'):
            interatom.rdc_err = {}

        # Set the errors.
        interatom.rdc_err[tag] = 1.0

    # Set 0.1 ppm errors on all PCS data.
    for spin in spin_loop():
        # Init.
        if not hasattr(spin, 'pcs_err'):
            spin.pcs_err = {}

        # Set the errors.
        spin.pcs_err[tag] = 0.1

    # Write the data.
    rdc.write(align_id=tag, file='rdc_%s.txt'%tensors[i], bc=True, force=True)
    pcs.write(align_id=tag, file='pcs_%s.txt'%tensors[i], bc=True, force=True)

# Store the state.
state.save('back_calc', force=True)
