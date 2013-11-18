"""Optimise the SQ data in relax.

To run this, type:

$ rm -f optimise_sq.log; ../../../../../relax --tee optimise_sq.log optimise_sq.py
"""

# relax module imports.
from specific_analyses.relax_disp.disp_data import generate_r20_key
from specific_analyses.relax_disp.variables import EXP_TYPE_CPMG_SQ


# Create a data pipe.
pipe.create('R2eff', 'relax_disp')

# Create the spin system.
spin.create(res_name='Asp', res_num=9, spin_name='N')
spin.element('N', spin_id='@N')
spin.isotope('15N', spin_id='@N')

# The spectral data - experiment ID, R2eff file name, experiment type, spin ID string, spectrometer frequency in Hertz, relaxation time.
data = [
    ['15N_CPMG_500_MHz', 'ns_500.res', EXP_TYPE_CPMG_SQ, ':9@N', 500e6, 0.04],
    ['15N_CPMG_600_MHz', 'ns_600.res', EXP_TYPE_CPMG_SQ, ':9@N', 600e6, 0.04],
    ['15N_CPMG_800_MHz', 'ns_800.res', EXP_TYPE_CPMG_SQ, ':9@N', 800e6, 0.04]
]
cpmg_frqs = [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0]

# Loop over the files, reading in the data.
for id, file, exp_type, spin_id, H_frq, relax_time in data:
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

    # Read the R2eff data.
    relax_disp.r2eff_read_spin(id=id, file=file, dir='..', spin_id=spin_id, disp_point_col=1, data_col=2, error_col=3)

# Change the model.
relax_disp.select_model('MMQ 2-site')

# The R20 keys.
r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=600e6)
r20_key3 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)

# Manually set the parameter values to the cpmg_fit results.
spin = cdp.mol[0].res[0].spin[0]
spin.r2 = {r20_key1: 8.400699, r20_key2: 8.847946, r20_key3: 10.289079}
spin.pA = 0.950701
spin.kex = 435.592
spin.dw = 4.356895
spin.chi2 = 17.49720

# Optimisation.
minimise(min_algor='simplex')

# Monte Carlo simulations.
monte_carlo.setup(number=3)
monte_carlo.create_data(method='back_calc')
monte_carlo.initial_values()
minimise(min_algor='simplex')
monte_carlo.error_analysis()

# Plot the dispersion curves.
relax_disp.plot_disp_curves(dir='disp_curves', force=True)

# Save the results.
state.save('state', dir='sq', compress_type=1, force=True)
