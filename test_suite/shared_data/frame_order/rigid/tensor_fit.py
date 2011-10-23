# Script for calculating the RDC alignment tensors for the test model.


# Create a new data pipe.
pipe.create('fit', 'N-state')

# Load the rotated C-domain.
structure.read_pdb('1J7P_1st_NH_rot.pdb', dir='..')

# Load the spins.
structure.load_spins('@N')
structure.load_spins('@H')

# Load the NH vectors.
structure.vectors(spin_id='@N', attached='H', ave=False)

# Set the values needed to calculate the dipolar constant.
value.set(1.041 * 1e-10, 'bond_length', spin_id="@N")
value.set('15N', 'heteronucleus', spin_id="@N")
value.set('1H', 'proton', spin_id="@N")

# Loop over the alignments.
for tag in ['Ln1', 'Ln2', 'Ln3', 'Ln4']:
    # Load the RDCs.
    rdc.read(align_id=tag, file='rdc_%s.txt'%tag, spin_id_col=1, data_col=2, error_col=None)

    # Set up the model.
    n_state_model.select_model(model='fixed')

    # Minimisation.
    grid_search(inc=11)
    minimise('bfgs', constraints=True)

    # Fix the tensor.
    align_tensor.fix(tag)


