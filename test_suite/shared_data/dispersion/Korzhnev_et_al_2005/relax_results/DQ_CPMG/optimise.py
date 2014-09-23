"""Optimise the SQ data in relax.

To run this, type:

$ rm -f optimise.log; ../../../../../../relax --tee optimise.log optimise.py
"""

# relax module imports.
from lib.dispersion.variables import EXP_TYPE_CPMG_DQ, EXP_TYPE_CPMG_MQ, EXP_TYPE_CPMG_PROTON_MQ, EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_ZQ
from specific_analyses.relax_disp.data import generate_r20_key


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
    ['ZQ_CPMG_500_MHz', 'zq_500.res', EXP_TYPE_CPMG_ZQ, ':9@N', 500e6, 0.03],
    ['ZQ_CPMG_600_MHz', 'zq_600.res', EXP_TYPE_CPMG_ZQ, ':9@N', 600e6, 0.03],
    ['ZQ_CPMG_800_MHz', 'zq_800.res', EXP_TYPE_CPMG_ZQ, ':9@N', 800e6, 0.03]
]
cpmg_frqs = [33.0, 67.0, 133.0, 200.0, 267.0, 333.0, 400.0, 467.0, 533.0, 667.0, 800.0, 933.0, 1067.0]

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

        # Set the CPMG frequency.
        relax_disp.cpmg_setup(spectrum_id=new_id, cpmg_frq=cpmg_frq)

    # Read the R2eff data.
    relax_disp.r2eff_read_spin(id=id, file=file, dir='../..', spin_id=spin_id, disp_point_col=1, data_col=2, error_col=3)

# Change the model.
relax_disp.select_model('NS MMQ 2-site')

# The R20 keys.
r20_key_sq_500 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
r20_key_sq_600 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=600e6)
r20_key_sq_800 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)
r20_key_1h_sq_500 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=500e6)
r20_key_1h_sq_600 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=600e6)
r20_key_1h_sq_800 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=800e6)
r20_key_zq_500 = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=500e6)
r20_key_zq_600 = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=600e6)
r20_key_zq_800 = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=800e6)
r20_key_dq_500 = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=500e6)
r20_key_dq_600 = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=600e6)
r20_key_dq_800 = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=800e6)
r20_key_mq_500 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=500e6)
r20_key_mq_600 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=600e6)
r20_key_mq_800 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=800e6)
r20_key_1h_mq_500 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=500e6)
r20_key_1h_mq_600 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=600e6)
r20_key_1h_mq_800 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=800e6)

# Manually set the parameter values to the cpmg_fit results for all data.
spin = cdp.mol[0].res[0].spin[1]
spin.r2 = {
    r20_key_sq_500: 8.481132,
    r20_key_sq_600: 8.977845,
    r20_key_sq_800: 10.490257,
    r20_key_1h_sq_500: 6.778902,
    r20_key_1h_sq_600: 7.097458,
    r20_key_1h_sq_800: 5.635893,
    r20_key_zq_500: 6.043942,
    r20_key_zq_600: 6.827802,
    r20_key_zq_800: 6.946693,
    r20_key_dq_500: 8.693570,
    r20_key_dq_600: 10.744672,
    r20_key_dq_800: 12.647869,
    r20_key_mq_500: 9.245925,
    r20_key_mq_600: 9.949255,
    r20_key_mq_800: 12.053031,
    r20_key_1h_mq_500: 7.887264,
    r20_key_1h_mq_600: 8.506481,
    r20_key_1h_mq_800: 11.276893
}
spin.pA = 0.944322
spin.kex = 368.075
spin.dw = 4.413451
spin.dwH = -0.271799

# Optimisation.
minimise.execute(min_algor='simplex')

# Monte Carlo simulations.
monte_carlo.setup(number=3)
monte_carlo.create_data(method='back_calc')
monte_carlo.initial_values()
minimise.execute(min_algor='simplex', max_iter=100)
monte_carlo.error_analysis()

# Plot the dispersion curves.
relax_disp.plot_disp_curves(dir='.', force=True)

# Save the results.
state.save('state', compress_type=1, force=True)
