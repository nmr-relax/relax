# Script for calculating R2eff values.

# Python module imports.
from os import sep

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.mol_res_spin import spin_loop
from status import Status; status = Status()


# Analysis variables.
#####################

# The dispersion models.
MODELS = ['R2eff']

# The results directory.
RESULTS_DIR = '.'


# Set up the data pipe.
#######################

# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'lm63_3site'

# Create the sequence.
spin.create(res_name='Trp', res_num=1, spin_name='N')
spin.create(res_name='Lys', res_num=2, spin_name='N')

# Set the relaxation dispersion experiment type.
relax_disp.exp_type('cpmg fixed')

# The spectral data - spectrum ID, peak list file name, CPMG frequency (Hz), spectrometer frequency in Hertz.
data = [
    ['500_reference',   'nu_500MHz_ref.list',             None,  500e6],
    ['500_66.6666',     'nu_500MHz_66.6666.list',      66.6666,  500e6],
    ['500_133.3333',    'nu_500MHz_133.3333.list',    133.3333,  500e6],
    ['500_200.0',       'nu_500MHz_200.0.list',       200.0000,  500e6],
    ['500_266.6666',    'nu_500MHz_266.6666.list',    266.6666,  500e6],
    ['500_333.3333',    'nu_500MHz_333.3333.list',    333.3333,  500e6],
    ['500_400.0',       'nu_500MHz_400.0.list',       400.0000,  500e6],
    ['500_466.6666',    'nu_500MHz_466.6666.list',    466.6666,  500e6],
    ['500_533.3333',    'nu_500MHz_533.3333.list',    533.3333,  500e6],
    ['500_600.0',       'nu_500MHz_600.0.list',       600.0000,  500e6],
    ['500_666.6666',    'nu_500MHz_666.6666.list',    666.6666,  500e6],
    ['500_733.3333',    'nu_500MHz_733.3333.list',    733.3333,  500e6],
    ['500_800.0',       'nu_500MHz_800.0.list',       800.0000,  500e6],
    ['500_866.6666',    'nu_500MHz_866.6666.list',    866.6666,  500e6],
    ['500_933.3333',    'nu_500MHz_933.3333.list',    933.3333,  500e6],
    ['500_1000.0',      'nu_500MHz_1000.0.list',     1000.0000,  500e6],
    ['800_reference',   'nu_800MHz_ref.list',             None,  800e6],
    ['800_66.6666',     'nu_800MHz_66.6666.list',      66.6666,  800e6],
    ['800_133.3333',    'nu_800MHz_133.3333.list',    133.3333,  800e6],
    ['800_200.0',       'nu_800MHz_200.0.list',       200.0000,  800e6],
    ['800_266.6666',    'nu_800MHz_266.6666.list',    266.6666,  800e6],
    ['800_333.3333',    'nu_800MHz_333.3333.list',    333.3333,  800e6],
    ['800_400.0',       'nu_800MHz_400.0.list',       400.0000,  800e6],
    ['800_466.6666',    'nu_800MHz_466.6666.list',    466.6666,  800e6],
    ['800_533.3333',    'nu_800MHz_533.3333.list',    533.3333,  800e6],
    ['800_600.0',       'nu_800MHz_600.0.list',       600.0000,  800e6],
    ['800_666.6666',    'nu_800MHz_666.6666.list',    666.6666,  800e6],
    ['800_733.3333',    'nu_800MHz_733.3333.list',    733.3333,  800e6],
    ['800_800.0',       'nu_800MHz_800.0.list',       800.0000,  800e6],
    ['800_866.6666',    'nu_800MHz_866.6666.list',    866.6666,  800e6],
    ['800_933.3333',    'nu_800MHz_933.3333.list',    933.3333,  800e6],
    ['800_1000.0',      'nu_800MHz_1000.0.list',     1000.0000,  800e6]
]

# Loop over the spectra.
for id, file, cpmg_frq, H_frq in data:
    # Load the peak intensities.
    spectrum.read_intensities(file=file, dir=data_path, spectrum_id=id, heteronuc='N', proton='HN', int_method='height')

    # Set the relaxation dispersion CPMG frequencies.
    relax_disp.cpmg_frq(spectrum_id=id, cpmg_frq=cpmg_frq)

    # Set the NMR field strength of the spectrum.
    spectrometer.frequency(id=id, frq=H_frq)

    # Relaxation dispersion CPMG constant time delay T (in s).
    relax_disp.relax_time(spectrum_id=id, time=0.1)

    # Errors.
    spectrum.baseplane_rmsd(error=1000000.0, spectrum_id=id)

# Peak intensity error analysis.
spectrum.error_analysis(subset=['500_reference', '500_66.6666', '500_133.3333', '500_200.0', '500_266.6666', '500_333.3333', '500_400.0', '500_466.6666', '500_533.3333', '500_600.0', '500_666.6666', '500_733.3333', '500_800.0', '500_866.6666', '500_933.3333', '500_1000.0'])
spectrum.error_analysis(subset=['800_reference', '800_66.6666', '800_133.3333', '800_200.0', '800_266.6666', '800_333.3333', '800_400.0', '800_466.6666', '800_533.3333', '800_600.0', '800_666.6666', '800_733.3333', '800_800.0', '800_866.6666', '800_933.3333', '800_1000.0'])


# Auto-analysis execution.
##########################

# Do not change!
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=RESULTS_DIR, models=MODELS)

# Save the program state.
state.save('r2eff_values', force=True)
