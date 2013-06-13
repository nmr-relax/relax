# Generate some synthetic RDC and PCS data.

# Python module imports.
from numpy import array, float64


# Create a data pipe.
pipe.create('data generation', 'N-state')

# Load the structure.
structure.read_pdb('fancy_mol.pdb', set_mol_name='fancy_mol')

# Set up the 15N and 1H spin information.
structure.load_spins()
spin.isotope(isotope='15N', spin_id='@N')
spin.isotope(isotope='1H', spin_id='@H')


# Define the magnetic dipole-dipole interaction.
interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
interatom.unit_vectors()

# Initialise some random tensors.
align_tensor.init(tensor='Dy', align_id='dy', params=(-0.000283041921495, 0.00017331020651, 0.000348144461756, 0.00109678563394, -0.000261126459214), param_types=2)
align_tensor.init(tensor='Dy', align_id='dy', params=(1.32405973595e-05, 1.69451339335e-05, 1.11420056339e-05, 1.2902359091e-05, 1.06231229491e-05), param_types=2, errors=True)
align_tensor.init(tensor='Tb', align_id='tb', params=(0.000167738428636, -0.000311103377008, 0.000231043994111, 0.000927908442481, -0.00042448381621), param_types=2)
align_tensor.init(tensor='Tb', align_id='tb', params=(9.23106516114e-06, 1.23864406564e-05, 9.25138110416e-06, 1.0025121852e-05, 8.6027985631e-06), param_types=2, errors=True)
align_tensor.init(tensor='Tm', align_id='tm', params=(-0.000214531334757, 0.000250016686133, -0.000318452894707, -0.000566585709341, 0.000458689017372), param_types=2)
align_tensor.init(tensor='Tm', align_id='tm', params=(8.18656207912e-06, 1.09649975373e-05, 8.43998269558e-06, 8.63599444168e-06, 7.95937745247e-06), param_types=2, errors=True)
align_tensor.init(tensor='Er', align_id='er', params=(-9.34632913359e-05, 7.71986454118e-05, -0.000234020357448, -0.000363596427557, 0.000177874820425), param_types=2)
align_tensor.init(tensor='Er', align_id='er', params=(6.32851257036e-06, 9.3721066722e-06, 7.36682050165e-06, 7.52806731357e-06, 9.79003188793e-06), param_types=2, errors=True)
align_tensor.init(tensor='Yb', align_id='yb', params=(2.20524016343e-05, -6.04903356962e-05, -0.000114723702615, -0.000214855846027, 0.000143730520814), param_types=2)
align_tensor.init(tensor='Yb', align_id='yb', params=(4.2812326053e-06, 5.43186247053e-06, 4.83605375312e-06, 5.10468453851e-06, 4.31847329676e-06), param_types=2, errors=True)
align_tensor.init(tensor='Ho', align_id='ho', params=(-6.99147985047e-05, -8.00899711508e-06, 0.000102219102441, 0.000424559081645, -0.000255281322523), param_types=2)
align_tensor.init(tensor='Ho', align_id='ho', params=(7.74711876341e-06, 9.55677606858e-06, 9.13852550558e-06, 7.82230105216e-06, 7.33515152376e-06), param_types=2, errors=True)

# Set the temperature and frequency.
ids = ['dy', 'tb', 'tm', 'er', 'yb', 'ho']
for id in ids:
    spectrometer.temperature(id, temp=303.0)
    spectrometer.frequency(id, frq=800.0, units="MHz")

# Set the number of states.
n_state_model.number_of_states(1)

# Initialise.
paramag.centre(pos=array([-5, -7, -9], float64))

# Back calculate the data.
rdc.back_calc()
pcs.back_calc()

# Write the data.
for id in ids:
    rdc.write(id, "rdc_%s.txt"%id, bc=True, force=True)
    pcs.write(id, "pcs_%s.txt"%id, bc=True, force=True)
