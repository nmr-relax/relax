"""Script for testing diffusion tensor optimisation."""

# Python module imports.
from numpy import array, float64
from os import sep


# Loop over all diffusion tensor types.
for diff_type in ['sphere', 'oblate', 'prolate', 'ellipsoid']:
    # A data pipe.
    pipe.create(diff_type, 'mf')

    # Load the sequence.
    sequence.read('NOE.500.out', res_num_col=1)

    # Load a PDB file.
    structure.read_pdb('uniform.pdb')

    # Set the spin names.
    spin.name(name='N')

    # Load the relaxation data.
    frq = array([500, 600, 700, 800], float64)
    for i in range(len(frq)):
        relax_data.read(ri_id='R1_%i'%frq[i],  ri_type='R1',  frq=frq[i]*1e6, file='R1.%i.out'%frq[i],  res_num_col=1, data_col=2, error_col=3)
        relax_data.read(ri_id='R2_%i'%frq[i],  ri_type='R2',  frq=frq[i]*1e6, file='R2.%i.out'%frq[i],  res_num_col=1, data_col=2, error_col=3)
        relax_data.read(ri_id='NOE_%i'%frq[i], ri_type='NOE', frq=frq[i]*1e6, file='NOE.%i.out'%frq[i], res_num_col=1, data_col=2, error_col=3)

    # Initialise the diffusion tensors.
    if diff_type == 'sphere':
        diffusion_tensor.init(1.0/(6.0*2e7), fixed=False)
    elif diff_type == 'prolate':
        diffusion_tensor.init((1.0/(6.0*7e7/3.0), 1e7, 2.0, pi-0.5), angle_units='rad', fixed=False)
    elif diff_type == 'oblate':
        diffusion_tensor.init((1.0/(6.0*7e7/3.0), -1e7, 2.0, pi-0.5), angle_units='rad', fixed=False)
    elif diff_type == 'ellipsoid':
        diffusion_tensor.init((8.3333333333333335e-09, 15000000.0, 0.33333333333333331, 1.0, 2.0, 0.5), angle_units='rad', fixed=False)

    # Create the proton spins.
    sequence.attach_protons()

    # Define the magnetic dipole-dipole relaxation interaction.
    spin.element('N', '@N')
    structure.get_pos("@N")
    structure.get_pos("@H")
    interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
    interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.02 * 1e-10)
    interatom.unit_vectors()

    # Define the chemical shift relaxation interaction.
    value.set(-172 * 1e-6, 'csa', spin_id='@N')

    # Set the nuclear isotope type.
    spin.isotope('15N', spin_id='@N')

    # Select the model-free model.
    model_free.select_model(model='m0')

    # Optimisation.
    minimise.execute('newton')

    # Save the PDB representation of the tensor.
    structure.create_diff_tensor_pdb(file=diff_type+'.pdb', force=True)
