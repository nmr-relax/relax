"""Optimise the SQ data in relax.

To run this, type:

$ rm -f optimise_sq.log; ../../../../../relax --tee optimise_sq.log optimise_sq.py
"""

# relax module imports.
from specific_analyses.relax_disp.data import generate_r20_key
from specific_analyses.relax_disp.variables import EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_SQ


# Create a data pipe.
pipe.create('R2eff', 'relax_disp')

# Create the spin system.
spin.create(res_name='Asp', res_num=9, spin_name='H')
spin.create(res_name='Asp', res_num=9, spin_name='N')
spin.element('H', spin_id='@H')
spin.element('N', spin_id='@N')
spin.isotope('1H', spin_id='@H')
spin.isotope('15N', spin_id='@N')

# Define the magnetic dipole-dipole relaxation interaction.
interatom.define(spin_id1=':9@N', spin_id2=':9@H', direct_bond=True)

# The spectral data - experiment ID, R2eff file name, experiment type, spin ID string, spectrometer frequency in Hertz, relaxation time.
data = [
    ['1H_CPMG_500_MHz',  'hs_500.res', '1H SQ CPMG', ':9@H', 500e6, 0.03],
    ['1H_CPMG_600_MHz',  'hs_600.res', '1H SQ CPMG', ':9@H', 600e6, 0.03],
    ['1H_CPMG_800_MHz',  'hs_800.res', '1H SQ CPMG', ':9@H', 800e6, 0.03],
    ['15N_CPMG_500_MHz', 'ns_500.res', 'SQ CPMG', ':9@N', 500e6, 0.04],
    ['15N_CPMG_600_MHz', 'ns_600.res', 'SQ CPMG', ':9@N', 600e6, 0.04],
    ['15N_CPMG_800_MHz', 'ns_800.res', 'SQ CPMG', ':9@N', 800e6, 0.04]
]
h_cpmg_frqs = [67.0, 133.0, 267.0, 400.0, 533.0, 667.0, 800.0, 933.0, 1067.0, 1600.0, 2133.0, 2667.0]
n_cpmg_frqs = [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0]

# Loop over the files, reading in the data.
for id, file, exp_type, spin_id, H_frq, relax_time in data:
    # Alias the CPMG frequencies.
    if spin_id[-1] == 'H':
        cpmg_frqs = h_cpmg_frqs
    else:
        cpmg_frqs = n_cpmg_frqs

    # Loop over each CPMG frequency.
    for cpmg_frq in cpmg_frqs:
        # The id.
        new_id = "%s_%s" % (id, cpmg_frq)

        # Set the NMR field strength.
        spectrometer.frequency(id=new_id, frq=H_frq)

        # Set the relaxation dispersion experiment type.
        relax_disp.exp_type(spectrum_id=new_id, exp_type=exp_type)

        # Relaxation dispersion CPMG constant time delay T (in s).
        relax_disp.relax_time(spectrum_id=new_id, time=relax_time)

        # Set the CPMG frequency.
        relax_disp.cpmg_setup(spectrum_id=new_id, cpmg_frq=cpmg_frq)

    # Read the R2eff data.
    relax_disp.r2eff_read_spin(id=id, file=file, dir='..', spin_id=spin_id, disp_point_col=1, data_col=2, error_col=3)

# Change the model.
relax_disp.select_model('NS MMQ 2-site')

# The R20 keys.
r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=600e6)
r20_key3 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)
r20_key4 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=500e6)
r20_key5 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=600e6)
r20_key6 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=800e6)

# Manually set the parameter values.
spin_N = cdp.mol[0].res[0].spin[1]
spin_N.r2 = {r20_key1: 8.412998, r20_key2: 8.847946, r20_key3: 10.329567, r20_key4: 6.779626, r20_key5: 7.089813, r20_key6: 5.610770}
spin_N.pA = 0.947960
spin_N.kex = 408.394
spin_N.dw = 4.369907
spin_N.dwH = -0.267240

# Optimisation.
minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-25, grad_tol=None, max_iter=10000000, constraints=True, scaling=True, verbosity=1)

# Monte Carlo simulations.
monte_carlo.setup(number=3)
monte_carlo.create_data(method='back_calc')
monte_carlo.initial_values()
minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-25, grad_tol=None, max_iter=10000000, constraints=True, scaling=True, verbosity=1)
monte_carlo.error_analysis()

# Plot the dispersion curves.
relax_disp.plot_disp_curves(dir='disp_curves', force=True)

# Save the results.
state.save('state', dir='sq', compress_type=1, force=True)
