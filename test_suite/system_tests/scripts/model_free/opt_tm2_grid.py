"""Script for setting up the data pipe for testing optimisation."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()


# Path of the files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'tm2_grid'

# Create the sequence.
molecule.create(mol_name='Polycarbonate')
for i in range(3*3*3):
    spin.create(spin_num=1, spin_name='C1', res_num=i+1, res_name='Bisphenol_A', mol_name='Polycarbonate')

# The proton frequencies in MHz.
frq = ['400', '500', '600', '700', '800', '900', '1000']

# Load the relaxation data.
for i in range(len(frq)):
    relax_data.read('NOE', frq[i], float(frq[i])*1e6, 'noe.%s.out' % frq[i], dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
    relax_data.read('R1',  frq[i], float(frq[i])*1e6, 'r1.%s.out' % frq[i],  dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
    relax_data.read('R2',  frq[i], float(frq[i])*1e6, 'r2.%s.out' % frq[i],  dir=path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

# Setup other values.
value.set(1.20 * 1e-10, 'bond_length')
value.set(200 * 1e-6, 'csa')
value.set('13C', 'heteronucleus')
value.set('1H', 'proton')

# Select the model-free model.
model_free.select_model(model=cdp._model)

# The model-free parameters.
tm = [2e-9, 10e-9, 21e-9]
s2 = [0.2, 0.8, 0.95]
te = [2e-12, 40e-12, 1e-9]

# Deselect all spins.
deselect.spin()

# Residue index.
res_index = 0

# Loop over te.
for te_index in range(3):
    # Loop over s2.
    for s2_index in range(3):
        # Loop over tm.
        for tm_index in range(3):
            # Alias the relevent spin container.
            spin = cdp.mol[0].res[res_index].spin[0]

            # Select the spin.
            spin.select = True

            # Set up the diffusion tensor.
            if cdp._model in ['m2', 'm4']:
                if res_index:
                    diffusion_tensor.delete()
                diffusion_tensor.init(tm[tm_index])

            # Set up the initial model-free parameter values (bypass the grid search for speed).
            if cdp._model in ['tm2']:
                spin.local_tm = tm[tm_index]
            if cdp._model in ['m2', 'm4']:
                spin.s2 = s2[s2_index]
            if cdp._model in ['m2', 'm4']:
                spin.te = te[te_index]
            if cdp._model in ['m4']:
                spin.rex = 0.0

            # Minimise.
            minimise('newton', 'gmw', 'back', constraints=False)

            # Check the values.
            if cdp._model == 'm2':
                cdp._value_test(spin, s2=s2[s2_index], te=te[te_index]*1e12, chi2=0.0)
            elif cdp._model == 'm4':
                cdp._value_test(spin, s2=s2[s2_index], te=te[te_index]*1e12, rex=0.0, chi2=0.0)
            elif cdp._model == 'tm2':
                cdp._value_test(spin, local_tm=tm[tm_index]*1e9, s2=s2[s2_index], te=te[te_index]*1e12, chi2=0.0)

            # Increment the residue index and deselect the spin.
            res_index += 1
            spin.select = False
