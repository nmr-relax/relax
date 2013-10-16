"""Script for CPMG relaxation dispersion curve fitting to the 'MQ CR72' model using Dr. Flemming Hansen's data from http://dx.doi.org/10.1021/jp074793o.

This is to test the nesting of the 'CR72' and 'MQ CR72' models.  The 'MQ CR72' results should be identical to the 'CR72' results but with dwH = 0.

To run:

$ ../../../../../relax --tee analysis_mq_cr72.log analysis_mq_cr72.py
"""


# Python module imports.
from os import sep

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.mol_res_spin import return_spin
from status import Status; status = Status()


# Analysis variables.
#####################

# The dispersion models.
MODELS = ['R2eff', 'MQ CR72']

# The grid search size (the number of increments per dimension).
GRID_INC = 6

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 3



# Set up the data pipe.
#######################

# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen'

# Load the sequence.
sequence.read('fake_sequence.in', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Hansen', res_num_col=1, res_name_col=2)

# Name the spins so they can be matched to the assignments, and the isotope for field strength scaling.
spin.name(name='N')
spin.isotope(isotope='15N')

# The spectral data - spectrum ID, peak list file name, CPMG frequency (Hz), spectrometer frequency in Hertz.
data = [
    ['500_reference.in',    '500_MHz'+sep+'reference.in_sparky',           None,  500e6],
    ['500_66.667.in',       '500_MHz'+sep+'66.667.in_sparky',           66.6666,  500e6],
    ['500_133.33.in',       '500_MHz'+sep+'133.33.in_sparky',          133.3333,  500e6],
    ['500_133.33.in.bis',   '500_MHz'+sep+'133.33.in.bis_sparky',      133.3333,  500e6],
    ['500_200.in',          '500_MHz'+sep+'200.in_sparky',             200.0000,  500e6],
    ['500_266.67.in',       '500_MHz'+sep+'266.67.in_sparky',          266.6666,  500e6],
    ['500_333.33.in',       '500_MHz'+sep+'333.33.in_sparky',          333.3333,  500e6],
    ['500_400.in',          '500_MHz'+sep+'400.in_sparky',             400.0000,  500e6],
    ['500_466.67.in',       '500_MHz'+sep+'466.67.in_sparky',          466.6666,  500e6],
    ['500_533.33.in',       '500_MHz'+sep+'533.33.in_sparky',          533.3333,  500e6],
    ['500_533.33.in.bis',   '500_MHz'+sep+'533.33.in.bis_sparky',      533.3333,  500e6],
    ['500_600.in',          '500_MHz'+sep+'600.in_sparky',             600.0000,  500e6],
    ['500_666.67.in',       '500_MHz'+sep+'666.67.in_sparky',          666.6666,  500e6],
    ['500_733.33.in',       '500_MHz'+sep+'733.33.in_sparky',          733.3333,  500e6],
    ['500_800.in',          '500_MHz'+sep+'800.in_sparky',             800.0000,  500e6],
    ['500_866.67.in',       '500_MHz'+sep+'866.67.in_sparky',          866.6666,  500e6],
    ['500_933.33.in',       '500_MHz'+sep+'933.33.in_sparky',          933.3333,  500e6],
    ['500_933.33.in.bis',   '500_MHz'+sep+'933.33.in.bis_sparky',      933.3333,  500e6],
    ['500_1000.in',         '500_MHz'+sep+'1000.in_sparky',           1000.0000,  500e6],
    ['800_reference.in',    '800_MHz'+sep+'reference.in_sparky',           None,  800e6],
    ['800_66.667.in',       '800_MHz'+sep+'66.667.in_sparky',           66.6666,  800e6],
    ['800_133.33.in',       '800_MHz'+sep+'133.33.in_sparky',          133.3333,  800e6],
    ['800_133.33.in.bis',   '800_MHz'+sep+'133.33.in.bis_sparky',      133.3333,  800e6],
    ['800_200.in',          '800_MHz'+sep+'200.in_sparky',             200.0000,  800e6],
    ['800_266.67.in',       '800_MHz'+sep+'266.67.in_sparky',          266.6666,  800e6],
    ['800_333.33.in',       '800_MHz'+sep+'333.33.in_sparky',          333.3333,  800e6],
    ['800_400.in',          '800_MHz'+sep+'400.in_sparky',             400.0000,  800e6],
    ['800_466.67.in',       '800_MHz'+sep+'466.67.in_sparky',          466.6666,  800e6],
    ['800_533.33.in',       '800_MHz'+sep+'533.33.in_sparky',          533.3333,  800e6],
    ['800_533.33.in.bis',   '800_MHz'+sep+'533.33.in.bis_sparky',      533.3333,  800e6],
    ['800_600.in',          '800_MHz'+sep+'600.in_sparky',             600.0000,  800e6],
    ['800_666.67.in',       '800_MHz'+sep+'666.67.in_sparky',          666.6666,  800e6],
    ['800_733.33.in',       '800_MHz'+sep+'733.33.in_sparky',          733.3333,  800e6],
    ['800_800.in',          '800_MHz'+sep+'800.in_sparky',             800.0000,  800e6],
    ['800_866.67.in',       '800_MHz'+sep+'866.67.in_sparky',          866.6666,  800e6],
    ['800_933.33.in',       '800_MHz'+sep+'933.33.in_sparky',          933.3333,  800e6],
    ['800_933.33.in.bis',   '800_MHz'+sep+'933.33.in.bis_sparky',      933.3333,  800e6],
    ['800_1000.in',         '800_MHz'+sep+'1000.in_sparky',           1000.0000,  800e6]
]

# Loop over the spectra.
for id, file, cpmg_frq, H_frq in data:
    # Load the peak intensities.
    spectrum.read_intensities(file=file, dir=data_path, spectrum_id=id, int_method='height')

    # Set the relaxation dispersion experiment type.
    relax_disp.exp_type(spectrum_id=id, exp_type='MQ CPMG')

    # Set the relaxation dispersion CPMG frequencies.
    relax_disp.cpmg_frq(spectrum_id=id, cpmg_frq=cpmg_frq)

    # Set the NMR field strength of the spectrum.
    spectrometer.frequency(id=id, frq=H_frq)

    # Relaxation dispersion CPMG constant time delay T (in s).
    relax_disp.relax_time(spectrum_id=id, time=0.030)

# Specify the duplicated spectra.
spectrum.replicated(spectrum_ids=['500_133.33.in', '500_133.33.in.bis'])
spectrum.replicated(spectrum_ids=['500_533.33.in', '500_533.33.in.bis'])
spectrum.replicated(spectrum_ids=['500_933.33.in', '500_933.33.in.bis'])
spectrum.replicated(spectrum_ids=['800_133.33.in', '800_133.33.in.bis'])
spectrum.replicated(spectrum_ids=['800_533.33.in', '800_533.33.in.bis'])
spectrum.replicated(spectrum_ids=['800_933.33.in', '800_933.33.in.bis'])

# Peak intensity error analysis.
spectrum.error_analysis(subset=['500_reference.in', '500_66.667.in', '500_133.33.in', '500_133.33.in.bis', '500_200.in', '500_266.67.in', '500_333.33.in', '500_400.in', '500_466.67.in', '500_533.33.in', '500_533.33.in.bis', '500_600.in', '500_666.67.in', '500_733.33.in', '500_800.in', '500_866.67.in', '500_933.33.in', '500_933.33.in.bis', '500_1000.in'])
spectrum.error_analysis(subset=['800_reference.in', '800_66.667.in', '800_133.33.in', '800_133.33.in.bis', '800_200.in', '800_266.67.in', '800_333.33.in', '800_400.in', '800_466.67.in', '800_533.33.in', '800_533.33.in.bis', '800_600.in', '800_666.67.in', '800_733.33.in', '800_800.in', '800_866.67.in', '800_933.33.in', '800_933.33.in.bis', '800_1000.in'])

# Deselect unresolved spins.
deselect.read(file='unresolved', dir=data_path+sep+'500_MHz', res_num_col=1)
deselect.read(file='unresolved', dir=data_path+sep+'800_MHz', res_num_col=1)

# Select just spins :70@N and :71@N.
select.spin(":70-71", change_all=True)



# Auto-analysis execution (manually replicated).
################################################

# Do not change!
#Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM)


# The 'R2eff' model.
#~~~~~~~~~~~~~~~~~~~

# Pipe setup.
model = MODELS[0]
pipe.copy(pipe_from='base pipe', pipe_to=model, bundle_to='relax_disp')
pipe.switch(pipe_name=model)
relax_disp.select_model(model='R2eff')

# Optimisation.
calc(verbosity=1)


# The 'MQ CR72' model.
#~~~~~~~~~~~~~~~~~~~~~

# Pipe setup.
model = MODELS[1]
pipe.copy(pipe_from='base pipe', pipe_to=model, bundle_to='relax_disp')
pipe.switch(pipe_name=model)
relax_disp.select_model(model=model)
value.copy(pipe_from='R2eff', pipe_to=model, param='r2eff')

# Alias the spins.
spin70 = return_spin(":70")
spin71 = return_spin(":71")

# Set the initial parameter values (from the CR72 model).
spin70.r2 = [7.011, 9.465]
spin70.pA = 0.990
spin70.dw = 5.577
spin70.kex = 1765.993
spin70.chi2 = 18.450
spin71.r2 = [4.978, 10.0]
spin71.pA = 0.997
spin71.dw = 4.460
spin71.kex = 1879.584
spin71.chi2 = 1.379

# Optimisation.
#grid_search(lower=None, upper=None, inc=6, constraints=True, verbosity=1)
minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-25, grad_tol=None, max_iter=10000000, constraints=True, scaling=True, verbosity=1)
spin70.dwH = 0.0
spin71.dwH = 0.0
minimise(min_algor='simplex', line_search=None, hessian_mod=None, hessian_type=None, func_tol=1e-25, grad_tol=None, max_iter=10000000, constraints=True, scaling=True, verbosity=1)

# Results output.
results_dir = data_path + sep + model
relax_disp.plot_disp_curves(dir=results_dir, force=True)
value.write(param='pA', file='pA.out', dir=results_dir, scaling=1.0, comment=None, bc=False, force=True)
value.write(param='pB', file='pB.out', dir=results_dir, scaling=1.0, comment=None, bc=False, force=True)
grace.write(x_data_type='res_num', y_data_type='pA', spin_id=None, plot_data='value', file='pA.agr', dir=results_dir, force=True, norm=False)
grace.write(x_data_type='res_num', y_data_type='pB', spin_id=None, plot_data='value', file='pB.agr', dir=results_dir, force=True, norm=False)
value.write(param='dw', file='dw.out', dir=results_dir, scaling=1.0, comment=None, bc=False, force=True)
grace.write(x_data_type='res_num', y_data_type='dw', spin_id=None, plot_data='value', file='dw.agr', dir=results_dir, force=True, norm=False)
value.write(param='dwH', file='dwH.out', dir=results_dir, scaling=1.0, comment=None, bc=False, force=True)
grace.write(x_data_type='res_num', y_data_type='dwH', spin_id=None, plot_data='value', file='dwH.agr', dir=results_dir, force=True, norm=False)
value.write(param='k_AB', file='k_AB.out', dir=results_dir, scaling=1.0, comment=None, bc=False, force=True)
value.write(param='kex', file='kex.out', dir=results_dir, scaling=1.0, comment=None, bc=False, force=True)
value.write(param='tex', file='tex.out', dir=results_dir, scaling=1.0, comment=None, bc=False, force=True)
grace.write(x_data_type='res_num', y_data_type='k_AB', spin_id=None, plot_data='value', file='k_AB.agr', dir=results_dir, force=True, norm=False)
grace.write(x_data_type='res_num', y_data_type='kex', spin_id=None, plot_data='value', file='kex.agr', dir=results_dir, force=True, norm=False)
grace.write(x_data_type='res_num', y_data_type='tex', spin_id=None, plot_data='value', file='tex.agr', dir=results_dir, force=True, norm=False)
grace.write(x_data_type='res_num', y_data_type='chi2', spin_id=None, plot_data='value', file='chi2.agr', dir=results_dir, force=True, norm=False)
results.write(file='results', dir=results_dir, compress_type=1, force=True)
