# Python module imports.
from collections import OrderedDict
#import pickle
import cPickle as pickle
from numpy import array, asarray, diag, ones, std, sqrt
from numpy.random import normal
from minfx.generic import generic_minimise
from os import getcwd, makedirs, path, sep
from random import gauss
from tempfile import mkdtemp, NamedTemporaryFile

# relax imports
from status import Status; status = Status()
import dep_check
from pipe_control.mol_res_spin import generate_spin_string, return_spin, spin_loop
from specific_analyses.relax_disp.data import average_intensity, check_intensity_errors, generate_r20_key, get_curve_type, has_exponential_exp_type, has_r1rho_exp_type, loop_exp_frq, loop_exp_frq_offset_point, loop_exp_frq_offset_point_time, loop_time, return_grace_file_name_ini, return_param_key_from_data
from specific_analyses.relax_disp.data import check_intensity_errors
from specific_analyses.relax_disp.variables import MODEL_R2EFF

# C modules.
if dep_check.C_module_exp_fn:
    from specific_analyses.relax_fit.optimisation import func_wrapper, dfunc_wrapper, d2func_wrapper
    from target_functions.relax_fit import jacobian, jacobian_chi2, setup
    # Call the python wrapper function to help with list to numpy array conversion.
    func = func_wrapper
    dfunc = dfunc_wrapper
    d2func = d2func_wrapper


# Open data.
dic_s = pickle.load( open( "estimate_errors_data_settings.cp", "rb" ) )

# Extract
R = dic_s['R']
I0 = dic_s['I0']
params = dic_s['params']
np = dic_s['np']
sim = dic_s['sim']
nt_min = dic_s['nt_min']
nt_max_list = dic_s['nt_max_list']
all_times = dic_s['all_times']
I_err_level = dic_s['I_err_level']
I_err_std = dic_s['I_err_std']
all_errors = dic_s['all_errors']

# Make plots?
make_plots = True
make_peak_lists = True

if make_plots:
    from pylab import show, plot, legend, figure, title, subplots
    from matplotlib.font_manager import FontProperties
    fontP = FontProperties()
    fontP.set_size('small')


# Set which data to open for.
nt_max = 10
# Open data.
dic = pickle.load( open( "estimate_errors_data_nt%i.cp"%nt_max, "rb" ) )

##### Relax
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'curve_fitting'+sep+'numeric_topology'+sep+'estimate_errors_peak_lists'

pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe_type = 'relax_disp'

# Create the data pipe.
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type=pipe_type)

# Read the spins.
plist = "ntmax_%i_disp_%i.ser" % (nt_max, 0)
spectrum.read_spins(file=plist, dir=data_path)

# Name the isotope for field strength scaling.
spin.isotope(isotope='15N')
centerPPM_N15 = 110.000

chemical_shift.read(file=plist, dir=data_path)

#for i in range(np):
for i in range(1):
    nt = dic[i]['nt']
    errors = dic[i]['errors']
    times = dic[i]['times']

    # Load the peak intensities.  First create how spectrums should be named.
    spectrum_id_list = []
    for j in range(nt):
         spectrum_id_list.append('%iZ_A%i'%(i, j))
    file_name = "ntmax_%i_disp_%i.ser" % (nt_max, i)
    spectrum.read_intensities(file=file_name, dir=data_path, spectrum_id=spectrum_id_list, int_method='height', int_col=range(nt))

    for j in range(nt):
        spectrum_id = '%iZ_A%i'%(i, j)

        # Set the peak intensity errors, as defined as the baseplane RMSD.
        error = errors[j]
        spectrum.baseplane_rmsd(error=error, spectrum_id=spectrum_id)

        # Set the relaxation dispersion experiment type.
        relax_disp.exp_type(spectrum_id=spectrum_id, exp_type='R1rho')

        # Set The spin-lock field strength, nu1, in Hz
        spin_lock_field_strength = 1000. + i
        relax_disp.spin_lock_field(spectrum_id=spectrum_id, field=spin_lock_field_strength)

        # Set The spin-lock offset, omega_rf, in ppm.
        relax_disp.spin_lock_offset(spectrum_id=spectrum_id, offset=120.0)

        # Set the relaxation times (in s).
        time = times[j]
        relax_disp.relax_time(spectrum_id=spectrum_id, time=time)

        # Set the spectrometer frequency.
        spectrometer.frequency(id=spectrum_id, frq=800.1, units='MHz')


# Set the model.
relax_disp.select_model(MODEL_R2EFF)

# Check if intensity errors have already been calculated.
check_intensity_errors()

# Do a grid search.
minimise.grid_search(lower=None, upper=None, inc=11, constraints=False, verbosity=0)

# Minimise.
minimise.execute(min_algor='Newton', constraints=False, verbosity=0)

grace_file_path = NamedTemporaryFile(delete=False).name
grace_dir_name = path.dirname(grace_file_path)
grace_file_name = path.basename(grace_file_path)
relax_disp.plot_exp_curves(file=grace_file_name, dir=grace_dir_name, force=True, norm=True)
print("Grace intensity file is: %s in %s for file %s"%(grace_file_path, grace_dir_name, grace_file_name))

## Estimate R2eff errors.
#relax_disp.r2eff_err_estimate()

# Do boot strapping ?
do_boot = True

min_algor = 'Newton'
min_options = ()
sim_boot = 100000
scaling_list = [1.0, 1.0]

# Start dic.
my_dic = OrderedDict()

# Get the data.
for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
    # Add key to dic.
    my_dic[spin_id] = OrderedDict()

    # Generate spin string.
    spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

    for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
        # Generate the param_key.
        param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

        # Add key to dic.
        my_dic[spin_id][param_key] = OrderedDict()

        # Get the value.
        r2eff = getattr(cur_spin, 'r2eff')[param_key]
        my_dic[spin_id][param_key]['r2eff'] = r2eff
        #r2eff_err = getattr(cur_spin, 'r2eff_err')[param_key]
        i0 = getattr(cur_spin, 'i0')[param_key]
        #i0_err = getattr(cur_spin, 'i0_err')[param_key]
        my_dic[spin_id][param_key]['i0'] = i0

        if do_boot:
            values = []
            errors = []
            times = []
            for time in loop_time(exp_type=exp_type, frq=frq, offset=offset, point=point):
                values.append(average_intensity(spin=cur_spin, exp_type=exp_type, frq=frq, offset=offset, point=point, time=time))
                errors.append(average_intensity(spin=cur_spin, exp_type=exp_type, frq=frq, offset=offset, point=point, time=time, error=True))
                times.append(time)

            # Convert to numpy array.
            values = asarray(values)
            errors = asarray(errors)
            times = asarray(times)

            R_m_sim_l = []
            I0_m_sim_l = []
            for j in range(sim_boot):
                if j in range(0, 100000, 100):
                    print("Simulation %i"%j)
                # Start minimisation.

                # Produce errors
                I_err = []
                for j, error in enumerate(errors):
                    I_error = gauss(values[j], error)
                    I_err.append(I_error)
                # Convert to numpy array.
                I_err = asarray(I_err)

                x0 = [r2eff, i0]
                setup(num_params=len(x0), num_times=len(times), values=I_err, sd=errors, relax_times=times, scaling_matrix=scaling_list)

                params_minfx_sim_j, chi2_minfx_sim_j, iter_count, f_count, g_count, h_count, warning = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=x0, min_algor=min_algor, min_options=min_options, full_output=True, print_flag=0)
                R_m_sim_j, I0_m_sim_j = params_minfx_sim_j
                R_m_sim_l.append(R_m_sim_j)
                I0_m_sim_l.append(I0_m_sim_j)

            my_dic[spin_id][param_key]['r2eff_array_boot'] = asarray(R_m_sim_l)
            my_dic[spin_id][param_key]['i0_array_boot'] = asarray(I0_m_sim_l)

            # Get stats on distribution.
            sigma_R_sim = std(asarray(R_m_sim_l), ddof=1)
            sigma_I0_sim = std(asarray(I0_m_sim_l), ddof=1)
            my_dic[spin_id][param_key]['r2eff_err_boot'] = sigma_R_sim
            my_dic[spin_id][param_key]['i0_err_boot'] = sigma_I0_sim


# Now do relax monte carli
monte_carlo.setup(number=sim_boot)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise.execute(min_algor=min_algor, constraints=False)
eliminate()
monte_carlo.error_analysis()

# Get the data.
for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
    # Generate spin string.
    spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

    for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
        # Generate the param_key.
        param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

        # Loop over all sim, and collect data.
        r2eff_sim_l = []
        i0_sim_l = []
        for i, r2eff_sim in enumerate(cur_spin.r2eff_sim):
            i0_sim = cur_spin.i0_sim[i]

            r2eff_sim_i = r2eff_sim[param_key]
            r2eff_sim_l.append(r2eff_sim_i)
            i0_sim_i = i0_sim[param_key]
            i0_sim_l.append(i0_sim_i)

        my_dic[spin_id][param_key]['r2eff_array_sim'] = asarray(r2eff_sim_l)
        my_dic[spin_id][param_key]['i0_array_sim'] = asarray(i0_sim_l)

        # Take the standard deviation of all values.
        r2eff_sim_err = std(asarray(r2eff_sim_l), ddof=1)
        i0_sim_err = std(asarray(i0_sim_l), ddof=1)
        my_dic[spin_id][param_key]['r2eff_err_sim'] = r2eff_sim_err
        my_dic[spin_id][param_key]['i0_err_sim'] = i0_sim_err


# http://bespokeblog.wordpress.com/2011/07/11/basic-data-plotting-with-matplotlib-part-3-histograms/
if make_plots:
    fig_nr = 1
    for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
        for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
            # Create figure
            fig = figure(num=fig_nr, figsize=(20, 8))

            # Generate the param_key.
            param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

            # Original solution
            r2eff = my_dic[spin_id][param_key]['r2eff']

            # Extraxt from boot
            r2eff_array_boot = my_dic[spin_id][param_key]['r2eff_array_boot']
            r2eff_err_boot = my_dic[spin_id][param_key]['r2eff_err_boot']
            gauss_ref_boot = normal(loc=r2eff, scale=r2eff_err_boot, size=1000000)

            # Extract from relax Monte-Carlo
            r2eff_array_sim = my_dic[spin_id][param_key]['r2eff_array_sim']
            r2eff_sim_err = my_dic[spin_id][param_key]['r2eff_err_sim']
            gauss_ref_sim = normal(loc=r2eff, scale=r2eff_sim_err, size=1000000)

            # Plot histogram
            # For boot
            ax1 = fig.add_subplot(121)
            #ax1.hist(r2eff_array_boot, bins=100, histtype='stepfilled', normed=False, color='b', alpha=0.9, label='%i boot'%sim_boot)
            ax1.hist(r2eff_array_boot, bins=100, histtype='stepfilled', normed=True, color='b', alpha=0.9, label='%i boot'%sim_boot)
            ax1.hist(gauss_ref_boot, bins=100, histtype='step', normed=True, color='r', alpha=0.5, label='boot gauss')
            ax1.set_xlim([0.9,1.1])
            ax1.set_xlabel('R')
            ax1.legend(loc='upper left', shadow=True, prop = fontP)

            # For Monte-Carlo
            ax1 = fig.add_subplot(122)
            #ax1.hist(r2eff_array_sim, bins=100, histtype='stepfilled', normed=False, color='b', alpha=0.9, label='%i MC'%sim_boot)
            ax1.hist(r2eff_array_sim, bins=100, histtype='stepfilled', normed=True, color='b', alpha=0.9, label='%i MC'%sim_boot)
            ax1.hist(gauss_ref_sim, bins=100, histtype='step', normed=True, color='r', alpha=0.5, label='MC gauss')
            ax1.set_xlim([0.9,1.1])
            ax1.set_xlabel('R')
            ax1.legend(loc='upper left', shadow=True, prop = fontP)

            fig_nr += 1

if make_plots:
    show()
