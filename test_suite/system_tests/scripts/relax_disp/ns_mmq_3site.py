"""Compare the synthetic cpmg_fit data to the relax solution."""

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from lib.dispersion.variables import EXP_TYPE_CPMG_DQ, EXP_TYPE_CPMG_MQ, EXP_TYPE_CPMG_PROTON_MQ, EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_ZQ
from specific_analyses.relax_disp.data import generate_r20_key
from status import Status; status = Status()


# The path to the data files.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'ns_mmq_3site'


# Create a data pipe.
pipe.create('R2eff', 'relax_disp')

# Create the spin system.
spin.create(res_name='X', res_num=1, spin_name='H')
spin.create(res_name='X', res_num=1, spin_name='N')
spin.element('H', spin_id='@H')
spin.element('N', spin_id='@N')
spin.isotope('1H', spin_id='@H')
spin.isotope('15N', spin_id='@N')

# Define the magnetic dipole-dipole relaxation interaction.
interatom.define(spin_id1=':1@N', spin_id2=':1@H', direct_bond=True)

# The spectral data - experiment ID, R2eff file name, experiment type, spin ID string, spectrometer frequency in Hertz, relaxation time.
data = [
    ['1H SQ', '1H_SQ_CPMG_400_MHz',   'HS_400.res',  EXP_TYPE_CPMG_PROTON_SQ, ':1@H', 400e6,  0.03],
    ['1H SQ', '1H_SQ_CPMG_600_MHz',   'HS_600.res',  EXP_TYPE_CPMG_PROTON_SQ, ':1@H', 600e6,  0.03],
    ['1H SQ', '1H_SQ_CPMG_800_MHz',   'HS_800.res',  EXP_TYPE_CPMG_PROTON_SQ, ':1@H', 800e6,  0.03],
    ['1H SQ', '1H_SQ_CPMG_1000_MHz',  'HS_1000.res', EXP_TYPE_CPMG_PROTON_SQ, ':1@H', 1000e6, 0.03],
    ['SQ',    '15N_SQ_CPMG_400_MHz',  'NS_400.res',  EXP_TYPE_CPMG_SQ,        ':1@N', 400e6,  0.04],
    ['SQ',    '15N_SQ_CPMG_600_MHz',  'NS_600.res',  EXP_TYPE_CPMG_SQ,        ':1@N', 600e6,  0.04],
    ['SQ',    '15N_SQ_CPMG_800_MHz',  'NS_800.res',  EXP_TYPE_CPMG_SQ,        ':1@N', 800e6,  0.04],
    ['SQ',    '15N_SQ_CPMG_1000_MHz', 'NS_1000.res', EXP_TYPE_CPMG_SQ,        ':1@N', 1000e6, 0.04],
    ['ZQ',    '15N_ZQ_CPMG_400_MHz',  'ZQ_400.res',  EXP_TYPE_CPMG_ZQ,        ':1@N', 400e6,  0.03],
    ['ZQ',    '15N_ZQ_CPMG_600_MHz',  'ZQ_600.res',  EXP_TYPE_CPMG_ZQ,        ':1@N', 600e6,  0.03],
    ['ZQ',    '15N_ZQ_CPMG_800_MHz',  'ZQ_800.res',  EXP_TYPE_CPMG_ZQ,        ':1@N', 800e6,  0.03],
    ['ZQ',    '15N_ZQ_CPMG_1000_MHz', 'ZQ_1000.res', EXP_TYPE_CPMG_ZQ,        ':1@N', 1000e6, 0.03],
    ['DQ',    '15N_DQ_CPMG_400_MHz',  'DQ_400.res',  EXP_TYPE_CPMG_DQ,        ':1@N', 400e6,  0.03],
    ['DQ',    '15N_DQ_CPMG_600_MHz',  'DQ_600.res',  EXP_TYPE_CPMG_DQ,        ':1@N', 600e6,  0.03],
    ['DQ',    '15N_DQ_CPMG_800_MHz',  'DQ_800.res',  EXP_TYPE_CPMG_DQ,        ':1@N', 800e6,  0.03],
    ['DQ',    '15N_DQ_CPMG_1000_MHz', 'DQ_1000.res', EXP_TYPE_CPMG_DQ,        ':1@N', 1000e6, 0.03],
    ['1H MQ', '1H_MQ_CPMG_400_MHz',   'HM_400.res',  EXP_TYPE_CPMG_PROTON_MQ, ':1@H', 400e6,  0.02],
    ['1H MQ', '1H_MQ_CPMG_600_MHz',   'HM_600.res',  EXP_TYPE_CPMG_PROTON_MQ, ':1@H', 600e6,  0.02],
    ['1H MQ', '1H_MQ_CPMG_800_MHz',   'HM_800.res',  EXP_TYPE_CPMG_PROTON_MQ, ':1@H', 800e6,  0.02],
    ['1H MQ', '1H_MQ_CPMG_1000_MHz',  'HM_1000.res', EXP_TYPE_CPMG_PROTON_MQ, ':1@H', 1000e6, 0.02],
    ['MQ',    '15N_MQ_CPMG_400_MHz',  'NM_400.res',  EXP_TYPE_CPMG_MQ,        ':1@N', 400e6,  0.02],
    ['MQ',    '15N_MQ_CPMG_600_MHz',  'NM_600.res',  EXP_TYPE_CPMG_MQ,        ':1@N', 600e6,  0.02],
    ['MQ',    '15N_MQ_CPMG_800_MHz',  'NM_800.res',  EXP_TYPE_CPMG_MQ,        ':1@N', 800e6,  0.02],
    ['MQ',    '15N_MQ_CPMG_1000_MHz', 'NM_1000.res', EXP_TYPE_CPMG_MQ,        ':1@N', 1000e6, 0.02]
]
cpmg_frqs_1h_sq = []
for i in range(80):
    cpmg_frqs_1h_sq.append(100/3.0 * (i + 1))
cpmg_frqs_sq = []
for i in range(40):
    cpmg_frqs_sq.append(25.0 * (i + 1))
cpmg_frqs_dq = []
for i in range(32):
    cpmg_frqs_dq.append(100/3.0 * (i + 1))
cpmg_frqs_zq = []
for i in range(32):
    cpmg_frqs_zq.append(100/3.0 * (i + 1))
cpmg_frqs_1h_mq = []
for i in range(50):
    cpmg_frqs_1h_mq.append(50.0 * (i + 1))
cpmg_frqs_mq = []
for i in range(20):
    cpmg_frqs_mq.append(50.0 * (i + 1))

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
        new_id = "%s_%.3f" % (id, cpmg_frq)

        # Set the NMR field strength.
        spectrometer.frequency(id=new_id, frq=H_frq)

        # Set the relaxation dispersion experiment type.
        relax_disp.exp_type(spectrum_id=new_id, exp_type=exp_type)

        # Relaxation dispersion CPMG constant time delay T (in s).
        relax_disp.relax_time(spectrum_id=new_id, time=relax_time)

        # Set the CPMG frequency.
        relax_disp.cpmg_setup(spectrum_id=new_id, cpmg_frq=cpmg_frq)

    # Read the R2eff data.
    relax_disp.r2eff_read_spin(id=id, file=file, dir=DATA_PATH, spin_id=spin_id, disp_point_col=7, data_col=10, error_col=9)

# Change the model.
relax_disp.select_model('NS MMQ 3-site')

# The R20 keys.
r20_1h_sq_400_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=400e6)
r20_1h_sq_600_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=600e6)
r20_1h_sq_800_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=800e6)
r20_1h_sq_1000_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_SQ, frq=1000e6)
r20_sq_400_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=400e6)
r20_sq_600_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=600e6)
r20_sq_800_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=800e6)
r20_sq_1000_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=1000e6)
r20_zq_400_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=400e6)
r20_zq_600_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=600e6)
r20_zq_800_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=800e6)
r20_zq_1000_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_ZQ, frq=1000e6)
r20_dq_400_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=400e6)
r20_dq_600_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=600e6)
r20_dq_800_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=800e6)
r20_dq_1000_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_DQ, frq=1000e6)
r20_1h_mq_400_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=400e6)
r20_1h_mq_600_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=600e6)
r20_1h_mq_800_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=800e6)
r20_1h_mq_1000_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_PROTON_MQ, frq=1000e6)
r20_mq_400_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=400e6)
r20_mq_600_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=600e6)
r20_mq_800_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=800e6)
r20_mq_1000_key = generate_r20_key(exp_type=EXP_TYPE_CPMG_MQ, frq=1000e6)

# Manually set the parameter values.
spin_N = cdp.mol[0].res[0].spin[1]
spin_N.r2 = {
    r20_1h_sq_400_key:   6.5,
    r20_1h_sq_600_key:   7.0,
    r20_1h_sq_800_key:   5.5,
    r20_1h_sq_1000_key:  5.0,
    r20_sq_400_key:      8.0,
    r20_sq_600_key:      9.0,
    r20_sq_800_key:     10.5,
    r20_sq_1000_key:    11.5,
    r20_zq_400_key:      6.0,
    r20_zq_600_key:      7.5,
    r20_zq_800_key:      7.0,
    r20_zq_1000_key:     6.5,   
    r20_dq_400_key:      8.5,
    r20_dq_600_key:     10.5,
    r20_dq_800_key:     12.5,
    r20_dq_1000_key:    14.5,
    r20_1h_mq_400_key:   7.5,
    r20_1h_mq_600_key:   8.5,
    r20_1h_mq_800_key:  11.5,
    r20_1h_mq_1000_key: 13.5,
    r20_mq_400_key:      9.0,
    r20_mq_600_key:     10.0,
    r20_mq_800_key:     12.0,
    r20_mq_1000_key:    13.0
}
spin_N.pA = 0.85
spin_N.pB = 0.05
spin_N.pC = 0.10
spin_N.kex_AB = 500.0
spin_N.kex_AC = 1000.0
spin_N.kex_BC = 2000.0
spin_N.dw_AB = -3.0
spin_N.dw_AC =  8.0
spin_N.dw_BC = 11.0
spin_N.dwH_AB =  0.5
spin_N.dwH_AC = -1.5
spin_N.dwH_BC = -2.0

# Calculate.
minimise.calculate()

# Plot the dispersion curves (too slow).
#relax_disp.plot_disp_curves(dir=ds.tmpdir, num_points=100, extend=0, force=True)

# Save the results.
state.save('state', dir=ds.tmpdir, compress_type=1, force=True)
