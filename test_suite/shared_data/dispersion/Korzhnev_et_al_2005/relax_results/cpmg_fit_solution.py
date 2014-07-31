"""Compare the cpmg_fit and relax solutions.

To run this, type:

$ rm -f cpmg_fit_solution.log; ../../../../../relax --tee cpmg_fit_solution.log cpmg_fit_solution.py


This uses the data from Dmitry Korzhnev's paper at U{DOI: 10.1021/ja054550e<http://dx.doi.org/10.1021/ja054550e>}.  This is the 1H SQ, 15N SQ, ZQ, DQ, 1H MQ and 15N MQ data for residue Asp 9 of the Fyn SH3 domain mutant.

Here all data will be used.  The values found by cpmg_fit using just this data are:

    - r2 = {'H-S 500': 6.778901685616349, 'H-S 600':  7.097457574164754, 'H-S 800':  5.635892738874367,
            'N-S 500': 8.481132052795216, 'N-S 600':  8.977844777932544, 'N-S 800': 10.490256957494095,
            'NHZ 500': 6.043941666541193, 'NHZ 600':  6.827801822697070, 'NHZ 800':  6.946693082577048,
            'NHD 500': 8.693570244455426, 'NHD 600': 10.744671857325738, 'NHD 800': 12.647868752250540,
            'HNM 500': 7.887263548378362, 'HNM 600':  8.506480948916035, 'HNM 800': 11.276893369084453,
            'NHM 500': 9.245925304879110, 'NHM 600':  9.949254911695823, 'NHM 800': 12.053030643443734},
    - pA = 0.944322334629977,
    - kex = 368.075224340237810,
    - dw = 4.413451295385187,
    - dwH = -0.271799433880579,
    - chi2 = 162.379807990821462.
"""

# Python module imports.
from os import remove
from shutil import move

# relax module imports.
from specific_analyses.relax_disp.data import generate_r20_key
from specific_analyses.relax_disp.variables import EXP_TYPE_CPMG_DQ, EXP_TYPE_CPMG_MQ, EXP_TYPE_CPMG_PROTON_MQ, EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_ZQ


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
    ['1H SQ', '1H_SQ_CPMG_500_MHz',  'hs_500.res', EXP_TYPE_CPMG_PROTON_SQ, ':9@H', 500e6, 0.03],
    ['1H SQ', '1H_SQ_CPMG_600_MHz',  'hs_600.res', EXP_TYPE_CPMG_PROTON_SQ, ':9@H', 600e6, 0.03],
    ['1H SQ', '1H_SQ_CPMG_800_MHz',  'hs_800.res', EXP_TYPE_CPMG_PROTON_SQ, ':9@H', 800e6, 0.03],
    ['SQ',    '15N_SQ_CPMG_500_MHz', 'ns_500.res', EXP_TYPE_CPMG_SQ,        ':9@N', 500e6, 0.04],
    ['SQ',    '15N_SQ_CPMG_600_MHz', 'ns_600.res', EXP_TYPE_CPMG_SQ,        ':9@N', 600e6, 0.04],
    ['SQ',    '15N_SQ_CPMG_800_MHz', 'ns_800.res', EXP_TYPE_CPMG_SQ,        ':9@N', 800e6, 0.04],
    ['ZQ',    '15N_ZQ_CPMG_500_MHz', 'zq_500.res', EXP_TYPE_CPMG_ZQ,        ':9@N', 500e6, 0.03],
    ['ZQ',    '15N_ZQ_CPMG_600_MHz', 'zq_600.res', EXP_TYPE_CPMG_ZQ,        ':9@N', 600e6, 0.03],
    ['ZQ',    '15N_ZQ_CPMG_800_MHz', 'zq_800.res', EXP_TYPE_CPMG_ZQ,        ':9@N', 800e6, 0.03],
    ['DQ',    '15N_DQ_CPMG_500_MHz', 'dq_500.res', EXP_TYPE_CPMG_DQ,        ':9@N', 500e6, 0.03],
    ['DQ',    '15N_DQ_CPMG_600_MHz', 'dq_600.res', EXP_TYPE_CPMG_DQ,        ':9@N', 600e6, 0.03],
    ['DQ',    '15N_DQ_CPMG_800_MHz', 'dq_800.res', EXP_TYPE_CPMG_DQ,        ':9@N', 800e6, 0.03],
    ['1H MQ', '1H_MQ_CPMG_500_MHz',  'hm_500.res', EXP_TYPE_CPMG_PROTON_MQ, ':9@H', 500e6, 0.02],
    ['1H MQ', '1H_MQ_CPMG_600_MHz',  'hm_600.res', EXP_TYPE_CPMG_PROTON_MQ, ':9@H', 600e6, 0.02],
    ['1H MQ', '1H_MQ_CPMG_800_MHz',  'hm_800.res', EXP_TYPE_CPMG_PROTON_MQ, ':9@H', 800e6, 0.02],
    ['MQ',    '15N_MQ_CPMG_500_MHz', 'nm_500.res', EXP_TYPE_CPMG_MQ,        ':9@N', 500e6, 0.02],
    ['MQ',    '15N_MQ_CPMG_600_MHz', 'nm_600.res', EXP_TYPE_CPMG_MQ,        ':9@N', 600e6, 0.02],
    ['MQ',    '15N_MQ_CPMG_800_MHz', 'nm_800.res', EXP_TYPE_CPMG_MQ,        ':9@N', 800e6, 0.02]
]
cpmg_frqs_1h_sq = [67.0, 133.0, 267.0, 400.0, 533.0, 667.0, 800.0, 933.0, 1067.0, 1600.0, 2133.0, 2667.0]
cpmg_frqs_sq = [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0]
cpmg_frqs_dq = [33.0, 67.0, 133.0, 200.0, 267.0, 333.0, 400.0, 467.0, 533.0, 667.0, 800.0, 933.0, 1067.0]
cpmg_frqs_zq = [33.0, 67.0, 133.0, 200.0, 267.0, 333.0, 400.0, 467.0, 533.0, 667.0, 800.0, 933.0, 1067.0]
cpmg_frqs_1h_mq = [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 1000.0, 1500.0, 2000.0, 2500.0]
cpmg_frqs_mq = [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0]

# Loop over the files, reading in the data.
for data_type, id, file, exp_type, spin_id, H_frq, relax_time in data:
    # Alias the CPMG frequencies.
    if data_type == 'SQ':
        cpmg_frqs = cpmg_frqs_sq
    elif data_type == '1H SQ':
        cpmg_frqs = cpmg_frqs_1h_sq
    elif data_type == 'DQ':
        cpmg_frqs = cpmg_frqs_dq
    elif data_type == 'ZQ':
        cpmg_frqs = cpmg_frqs_zq
    elif data_type == '1H MQ':
        cpmg_frqs = cpmg_frqs_1h_mq
    elif data_type == 'MQ':
        cpmg_frqs = cpmg_frqs_mq

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
r20_key1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=500e6)
r20_key2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=600e6)
r20_key3 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=800e6)
r20_key4 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=500e6)
r20_key5 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=600e6)
r20_key6 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)
r20_key7 = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=500e6)
r20_key8 = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=600e6)
r20_key9 = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=800e6)
r20_key10 = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=500e6)
r20_key11 = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=600e6)
r20_key12 = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=800e6)
r20_key13 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=500e6)
r20_key14 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=600e6)
r20_key15 = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=800e6)
r20_key16 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=500e6)
r20_key17 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=600e6)
r20_key18 = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=800e6)

# Manually set the parameter values.
spin_N = cdp.mol[0].res[0].spin[1]
spin_N.r2 = {
    r20_key1:  6.778901685616349, r20_key2:   7.097457574164754, r20_key3:   5.635892738874367,
    r20_key4:  8.481132052795216, r20_key5:   8.977844777932544, r20_key6:  10.490256957494095,
    r20_key7:  6.043941666541193, r20_key8:   6.827801822697070, r20_key9:   6.946693082577048,
    r20_key10: 8.693570244455426, r20_key11: 10.744671857325738, r20_key12: 12.647868752250540,
    r20_key13: 7.887263548378362, r20_key14:  8.506480948916035, r20_key15: 11.276893369084453,
    r20_key16: 9.245925304879110, r20_key17:  9.949254911695823, r20_key18: 12.053030643443734,
}
spin_N.pA = 0.944322334629977
spin_N.kex = 368.075224340237810
spin_N.dw = 4.413451295385187
spin_N.dwH = -0.271799433880579

# Calculate.
minimise.calculate()

# Plot the dispersion curves.
relax_disp.plot_disp_curves(dir='.', num_points=100, extend=0, force=True)

# Save the results.
state.save('cpmg_fit_solution', dir='.', compress_type=1, force=True)

# Cleanup.
print("\n\nMoving 'disp_9_N.agr' to 'cpmg_fit_solution.agr'.")
move('disp_9_N.agr', 'cpmg_fit_solution.agr')
print("Deleting 'grace2images.py'.")
remove('grace2images.py')
