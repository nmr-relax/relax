"""Script for optimising the 'MQ NS 2-site' model.

This performs the analysis of:

    Remco Sprangers, Anna Gribun, Peter M. Hwang, Walid A. Houry, and Lewis E. Kay (2005)  Quantitative NMR spectroscopy of supramolecular complexes: Dynamic side pores in ClpP are important for product release, PNAS, 102 (46), 16678-16683.  (doi: http://dx.doi.org/10.1073/pnas.0507370102)
"""

# Python module imports.
from os import sep

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Analysis variables.
#####################

# The dispersion models.
MODELS = ['R2eff', 'No Rex', 'MQ CR72']

# The grid search size (the number of increments per dimension).
GRID_INC = 11

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 3

# The results directory.
RESULTS_DIR = 'mq_cr72_analysis_clustered'


# Set up the data pipe.
#######################

# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Sprangers_ClpP'

# Create the sequence.
spin.create(res_num=135, spin_name='S')
spin.create(res_num=135, spin_name='F')
spin.create(res_num=137, spin_name='S')
spin.create(res_num=137, spin_name='F')

# Set the isotope for field strength scaling.
spin.isotope(isotope='13C')

# The spectral data - spectrum ID, peak list file name, intensity column, CPMG frequency (Hz), spectrometer frequency in Hertz.
ncyc_frq = 800/12.
data = [
    ['600_ref',     '600.out',  6,  None,           600e6],
    ['600_ncyc12',  '600.out',  7,  ncyc_frq * 12,  600e6],
    ['600_ncyc1',   '600.out',  8,  ncyc_frq * 1,   600e6],
    ['600_ncyc10',  '600.out',  9,  ncyc_frq * 10,  600e6],
    ['600_ncyc2',   '600.out', 10,  ncyc_frq * 2,   600e6],
    ['600_ncyc8',   '600.out', 11,  ncyc_frq * 8,   600e6],
    ['600_ncyc3',   '600.out', 12,  ncyc_frq * 3,   600e6],
    ['600_ncyc6',   '600.out', 13,  ncyc_frq * 6,   600e6],
    ['600_ncyc4',   '600.out', 14,  ncyc_frq * 4,   600e6],
    ['600_ncyc5',   '600.out', 15,  ncyc_frq * 5,   600e6],
    ['600_ncyc1b',  '600.out', 16,  ncyc_frq * 1,   600e6],
    ['600_ncyc2b',  '600.out', 17,  ncyc_frq * 2,   600e6],
    ['600_ncyc3b',  '600.out', 18,  ncyc_frq * 3,   600e6],
    ['800_ref',     '800.out',  6,  None,           800e6],
    ['800_ncyc12',  '800.out',  7,  ncyc_frq * 12,  800e6],
    ['800_ncyc1',   '800.out',  8,  ncyc_frq * 1,   800e6],
    ['800_ncyc10',  '800.out',  9,  ncyc_frq * 10,  800e6],
    ['800_ncyc2',   '800.out', 10,  ncyc_frq * 2,   800e6],
    ['800_ncyc8',   '800.out', 11,  ncyc_frq * 8,   800e6],
    ['800_ncyc3',   '800.out', 12,  ncyc_frq * 3,   800e6],
    ['800_ncyc6',   '800.out', 13,  ncyc_frq * 6,   800e6],
    ['800_ncyc4',   '800.out', 14,  ncyc_frq * 4,   800e6],
    ['800_ncyc5',   '800.out', 15,  ncyc_frq * 5,   800e6],
    ['800_ncyc1b',  '800.out', 16,  ncyc_frq * 1,   800e6],
    ['800_ncyc2b',  '800.out', 17,  ncyc_frq * 2,   800e6],
    ['800_ncyc3b',  '800.out', 18,  ncyc_frq * 3,   800e6]
]

# Loop over the spectra.
for id, file, int_col, cpmg_frq, H_frq in data:
    # Load the peak intensities.
    spectrum.read_intensities(file=file, dir=data_path, spectrum_id=id, int_method='height', res_num_col=1, spin_name_col=2, int_col=int_col)

    # Set the relaxation dispersion experiment type.
    relax_disp.exp_type(spectrum_id=id, exp_type='MQ CPMG')

    # Set the relaxation dispersion CPMG frequencies.
    relax_disp.cpmg_frq(spectrum_id=id, cpmg_frq=cpmg_frq)

    # Set the NMR field strength of the spectrum.
    spectrometer.frequency(id=id, frq=H_frq)

    # Relaxation dispersion CPMG constant time delay T (in s).
    relax_disp.relax_time(spectrum_id=id, time=0.015)

# Specify the duplicated spectra.
spectrum.replicated(spectrum_ids=['600_ncyc1', '600_ncyc1b'])
spectrum.replicated(spectrum_ids=['600_ncyc2', '600_ncyc2b'])
spectrum.replicated(spectrum_ids=['600_ncyc3', '600_ncyc3b'])
spectrum.replicated(spectrum_ids=['800_ncyc1', '800_ncyc1b'])
spectrum.replicated(spectrum_ids=['800_ncyc2', '800_ncyc2b'])
spectrum.replicated(spectrum_ids=['800_ncyc3', '800_ncyc3b'])

# Measured chemical shift differences.
value.set(val=0.625, param='dw', spin_id=":135")
value.set(val=0.033, param='dwH', spin_id=":135")
value.set(val=0.981, param='dw', spin_id=":137")
value.set(val=0.010, param='dwH', spin_id=":137")
#value.set(val=0.5, param='pA')
#value.set(val=67.5, param='kex')

# Cluster all spins.
relax_disp.cluster(cluster_id='all', spin_id=":135-137")



# Auto-analysis execution.
##########################

# Do not change!
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=RESULTS_DIR, pre_run_dir='mq_cr72_analysis', models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM)
