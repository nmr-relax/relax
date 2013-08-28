# Optimise the R1rho on-resonance synthetic data using the DPL94 model.


# Python module imports.
from os import sep

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Analysis variables.
#####################

# The dispersion models.
MODELS = ['R2eff', 'TP02']

# The grid search size (the number of increments per dimension).
GRID_INC = 3

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 3


# Set up the data pipe.
#######################

# The results directory.
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = None

# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# The path to the data files (use the M61 model data for now).
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'r1rho_off_res_tp02'

# Create the sequence data.
spin.create(res_name='Trp', res_num=1, spin_name='N')
spin.create(res_name='Trp', res_num=2, spin_name='N')

# Set the isotope information.
spin.isotope(isotope='15N')

# Set the relaxation dispersion experiment type.
relax_disp.exp_type('r1rho fixed')

# Loop over the frequencies.
frq = [500, 800]
frq_label = ['500MHz', '800MHz']
error = 200000.0
for frq_index in range(len(frq)):
    # Load the R1 data.
    label = 'R1_%s' % frq_label[frq_index]
    relax_data.read(ri_id=label, ri_type='R1', frq=frq[frq_index]*1e6, file='%s.out'%label, dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

    # The spectral data - spectrum ID, peak lists, offset frequency (Hz).
    data = []
    spin_lock = [1000.0, 1500.0, 2000.0, 2500.0, 3000.0, 3500.0, 4000.0, 4500.0, 5000.0, 5500.0, 6000.0]
    for spin_lock_index in range(len(spin_lock)):
        data.append(["nu_%s_%s" % (spin_lock[spin_lock_index], frq_label[frq_index]), "nu_%s_%s.list" % (spin_lock[spin_lock_index], frq_label[frq_index]), spin_lock[spin_lock_index]])

    # Load the reference spectrum.
    spectrum.read_intensities(file="ref_%s.list" % frq_label[frq_index], dir=data_path, spectrum_id='ref_%s' % frq_label[frq_index], int_method='height', dim=1)
    spectrum.baseplane_rmsd(spectrum_id='ref_%s' % frq_label[frq_index], error=error)

    # Set as the reference.
    relax_disp.spin_lock_field(spectrum_id='ref_%s' % frq_label[frq_index], field=None)
    relax_disp.spin_lock_offset(spectrum_id='ref_%s' % frq_label[frq_index], offset=110.0)
    relax_disp.relax_time(spectrum_id='ref_%s' % frq_label[frq_index], time=0.1)

    # Set the spectrometer frequency.
    spectrometer.frequency(id='ref_%s' % frq_label[frq_index], frq=frq[frq_index], units='MHz')

    # Loop over the spectral data, loading it and setting the metadata.
    for id, file, field in data:
        # Load the peak intensities and set the errors.
        spectrum.read_intensities(file=file, dir=data_path, spectrum_id=id, int_method='height')
        spectrum.baseplane_rmsd(spectrum_id=id, error=error)

        # Set the relaxation dispersion spin-lock field strength (nu1).
        relax_disp.spin_lock_field(spectrum_id=id, field=field)

        # Set the spin-lock offset.
        relax_disp.spin_lock_offset(spectrum_id=id, offset=110.0)

        # Set the relaxation times.
        relax_disp.relax_time(spectrum_id=id, time=0.1)

        # Set the spectrometer frequency.
        spectrometer.frequency(id=id, frq=frq[frq_index], units='MHz')

# Clustering.
#relax_disp.cluster(cluster_id='cluster', spin_id='@N,NE1')

# Read the chemical shift data.
chemical_shift.read(file='ref_500MHz.list', dir=data_path)



# Auto-analysis execution.
##########################

# Run faster.
Relax_disp.opt_func_tol = 1e-10
Relax_disp.opt_max_iterations = 10000

# Do not change!
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir=ds.tmpdir, models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM)

# Save the program state.
state.save('devnull', force=True)
