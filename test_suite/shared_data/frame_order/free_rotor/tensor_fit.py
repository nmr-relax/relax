# Script for calculating the RDC alignment tensors for the test model.

from string import upper


# The tensor file for reading into relax.
out = open('tensors.py', 'w')

# Loop over the alignments.
ln = ['dy', 'tb', 'tm', 'er']
for i in range(len(ln)):
    # Create a new data pipe.
    pipe.create(ln[i], 'N-state')

    # Load the rotated C-domain.
    structure.read_pdb('1J7P_1st_NH_rot.pdb', dir='..')

    # Load the spins.
    structure.load_spins('@N')
    structure.load_spins('@H')

    # Load the NH vectors.
    structure.vectors(spin_id='@N', attached='H', ave=False)

    # Set the values needed to calculate the dipolar constant.
    value.set(1.041 * 1e-10, 'r', spin_id="@N")
    value.set('15N', 'heteronuc_type', spin_id="@N")
    value.set('1H', 'proton_type', spin_id="@N")

    # Load the RDCs.
    rdc.read(align_id=ln[i], file='rdc_%s.txt'%ln[i], res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

    # Set up the model.
    n_state_model.select_model(model='fixed')

    # Minimisation.
    grid_search(inc=7)
    minimise('newton', constraints=True)

    # Monte Carlo simulations.
    monte_carlo.setup(number=1000)
    monte_carlo.create_data()
    monte_carlo.initial_values()
    minimise('newton', constraints=False)
    monte_carlo.error_analysis()

    # Alias the tensor.
    A = cdp.align_tensors[0]

    # Write out the tensors.
    out.write("align_tensor.init(tensor='%s%s %s-dom', params=(%s, %s, %s, %s, %s), param_types=2)\n" % (upper(ln[i][0]), ln[i][1], 'C', A.Axx, A.Ayy, A.Axy, A.Axz, A.Ayz))
    out.write("align_tensor.init(tensor='%s%s %s-dom', params=(%s, %s, %s, %s, %s), param_types=2, errors=True)\n" % (upper(ln[i][0]), ln[i][1], 'C', A.Axx_err, A.Ayy_err, A.Axy_err, A.Axz_err, A.Ayz_err))
