# Script for calculating synthetics CPMG data.

# Python module imports.
from os import sep
from tempfile import mkdtemp
from math import sqrt

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from lib.io import mkdir_nofail, open_write_file
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.mol_res_spin import return_spin, spin_loop
from specific_analyses.relax_disp.data import generate_r20_key, loop_exp_frq, loop_offset, loop_frq, loop_offset_point
from specific_analyses.relax_disp.variables import EXP_TYPE_CPMG_SQ
from specific_analyses.relax_disp import optimisation
from status import Status; status = Status()

# Analysis variables.
#####################
# The dispersion model to test.
if not hasattr(ds, 'data'):
    model = "CR72"

    ## Experiments
    # Exp 1
    sfrq_1 = 599.8908617*1E6
    r20_key_1 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_1)
    time_T2_1 = 0.06
    ncycs_1 = [2, 4, 8, 10, 20, 30, 40, 60]
    r2eff_errs_1 = [0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05]
    exp_1 = [sfrq_1, time_T2_1, ncycs_1, r2eff_errs_1]

    sfrq_2 = 499.8908617*1E6
    r20_key_2 = generate_r20_key(exp_type=EXP_TYPE_CPMG_SQ, frq=sfrq_2)
    time_T2_2 = 0.05
    ncycs_2 = [2, 4, 8, 10, 30, 35, 40, 50]
    r2eff_errs_2 = [0.05, -0.05, 0.05, -0.05, 0.05, -0.05, 0.05, -0.05]
    exp_2 = [sfrq_2, time_T2_2, ncycs_2, r2eff_errs_2]

    # Collect all exps
    exps = [exp_1, exp_2]

    spins = [
            ['Ala', 1, 'N', {'r2': {r20_key_1:10, r20_key_2:11.5}, 'kex': 1000, 'pA': 0.99, 'dw': 2} ],
            ['Ala', 2, 'N', {'r2': {r20_key_1:13, r20_key_2:14.5}, 'kex': 1000, 'pA': 0.99, 'dw': 1} ]
            ]

    ds.data = [model, spins, exps]

# The tmp directory.
if not hasattr(ds, 'tmpdir'):
    ds.tmpdir = None

# The results directory.
if not hasattr(ds, 'resdir'):
    ds.resdir = None

# Do set_grid_r20_from_min_r2eff ?.
if not hasattr(ds, 'set_grid_r20_from_min_r2eff'):
    ds.set_grid_r20_from_min_r2eff = True

# Remove insignificant level.
if not hasattr(ds, 'insignificance'):
    ds.insignificance = 0.0

# The grid search size (the number of increments per dimension).
if not hasattr(ds, 'GRID_INC'):
    ds.GRID_INC = 12

# The function tolerance.  This is used to terminate minimisation once the function value between iterations is less than the tolerance.
# The default value is 1e-25.
if not hasattr(ds, 'set_func_tol'):
    ds.set_func_tol = 1e-25

# The maximum number of iterations.
# The default value is 1e7.
if not hasattr(ds, 'set_max_iter'):
    ds.set_max_iter = 10000000

# The verbosity level.
if not hasattr(ds, 'verbosity'):
    ds.verbosity = 1

# The rel_change WARNING level.
if not hasattr(ds, 'rel_change'):
    ds.rel_change = 0.05

# The plot_curves.
if not hasattr(ds, 'plot_curves'):
    ds.plot_curves = True

# The set r2eff err.
if not hasattr(ds, 'r2eff_err'):
    ds.r2eff_err = 0.1

# The number of Monte Carlo simulations to be used for the error analyses.
if not hasattr(ds, 'MC_NUM'):
    ds.MC_NUM = 3

# The print result info.
if not hasattr(ds, 'print_res'):
    ds.print_res = True

# Set up the data pipe.
#######################

# Create the data pipe.
pipe_name = 'base pipe'
pipe_type = 'relax_disp'
pipe_bundle = 'relax_disp'
pipe_name_r2eff = "%s_%s_R2eff"%(ds.data[0], pipe_name)
#pipe_name_r2eff_calc = "%s_calc"%(pipe_name_r2eff)
pipe.create(pipe_name=pipe_name, pipe_type=pipe_type, bundle = pipe_bundle)


# Generate the sequence.
cur_spins = ds.data[1]
for res_name, res_num, spin_name, params in cur_spins:
    spin.create(res_name=res_name, res_num=res_num, spin_name=spin_name)

# Set isotope
spin.isotope('15N', spin_id='@N')


# Extract experiment settings.
exps = ds.data[2]

# Now loop over the experiments
exp_ids = []
for exp in exps:
    sfrq, time_T2, ncycs, r2eff_errs = exp
    exp_id = 'CPMG_%3.1f' % (sfrq/1E6)
    exp_ids.append(exp_id)

    ids = []
    for ncyc in ncycs:
        nu_cpmg = ncyc / time_T2
        cur_id = '%s_%.1f' % (exp_id, nu_cpmg)
        print cur_id
        ids.append(cur_id)

        # Set the spectrometer frequency.
        spectrometer.frequency(id=cur_id, frq=sfrq)

        # Set the experiment type.
        relax_disp.exp_type(spectrum_id=cur_id, exp_type=EXP_TYPE_CPMG_SQ)

        # Set the relaxation dispersion CPMG constant time delay T (in s).
        relax_disp.relax_time(spectrum_id=cur_id, time=time_T2)

        # Set the relaxation dispersion CPMG frequencies.
        relax_disp.cpmg_frq(spectrum_id=cur_id, cpmg_frq=nu_cpmg)

print("\n\nThe experiment IDs are %s." % ids)

## Now prepare to calculate the synthetic R2eff values.
pipe.copy(pipe_from=pipe_name, pipe_to=pipe_name_r2eff, bundle_to = pipe_bundle)
pipe.switch(pipe_name=pipe_name_r2eff)

# Then select model.
relax_disp.select_model(model=ds.data[0])

# First loop over the spins and set the model parameters.
for res_name, res_num, spin_name, params in cur_spins:
    cur_spin_id = ":%i@%s"%(res_num, spin_name)
    cur_spin = return_spin(cur_spin_id)
    #print cur_spin.model, cur_spin.name, cur_spin.isotope

    # Now set the parameters.
    for mo_param in cur_spin.params:
        # The R2 is a dictionary, depending on spectrometer frequency.
        if isinstance(getattr(cur_spin, mo_param), dict):
            set_r2 = params[mo_param]
            for key, val in set_r2.items():
                # Update value to float
                set_r2.update({ key : float(val) })
                print cur_spin.model, res_name, cur_spin_id, mo_param, key, float(val)
            setattr(cur_spin, mo_param, set_r2)
        else:
            before = getattr(cur_spin, mo_param)
            setattr(cur_spin, mo_param, float(params[mo_param]))
            after = getattr(cur_spin, mo_param)
            print cur_spin.model, res_name, cur_spin_id, mo_param, before, after


## Now doing the back calculation of R2eff values.

# First loop over the frequencies.
i = 0
for exp_type, frq, ei, mi in loop_exp_frq(return_indices=True):
    exp_id = exp_ids[mi]
    exp = exps[mi]
    sfrq, time_T2, ncycs, r2eff_errs = exp

    # Then loop over the spins.
    for res_name, res_num, spin_name, params in cur_spins:
        cur_spin_id = ":%i@%s"%(res_num, spin_name)
        cur_spin = return_spin(cur_spin_id)

        ## First do a fake R2eff structure.
        # Define file name
        file_name = "%s%s.txt" % (exp_id, cur_spin_id .replace('#', '_').replace(':', '_').replace('@', '_'))
        file = open_write_file(file_name=file_name, dir=ds.tmpdir, force=True)

        # Then loop over the points, make a fake R2eff value.
        for offset, point, oi, di in loop_offset_point(exp_type=EXP_TYPE_CPMG_SQ, frq=frq, return_indices=True):
            string = "%.15f 1.0 %.3f\n"%(point, ds.r2eff_err)
            file.write(string)

        # Close file.
        file.close()

        # Read in the R2eff file to create the structure
        relax_disp.r2eff_read_spin(id=exp_id, spin_id=cur_spin_id, file=file_name, dir=ds.tmpdir, disp_point_col=1, data_col=2, error_col=3)

        ###Now back calculate, and stuff it back.
        r2effs = optimisation.back_calc_r2eff(spin=cur_spin, spin_id=cur_spin_id)

        file = open_write_file(file_name=file_name, dir=ds.resdir, force=True)
        ## Loop over the R2eff structure
        # Loop over the points.
        for offset, point, oi, di in loop_offset_point(exp_type=EXP_TYPE_CPMG_SQ, frq=frq, return_indices=True):
            # Extract the Calculated R2eff.
            r2eff = r2effs[ei][0][mi][oi][di]

            # Find the defined error setup.
            set_r2eff_err = r2eff_errs[di]

            # Add the defined error to the calculated error.
            r2eff_w_err = r2eff + set_r2eff_err

            string = "%.15f %.15f %.3f %.15f\n"%(point, r2eff_w_err, ds.r2eff_err, r2eff)
            file.write(string)

        # Close file.
        file.close()

        # Read in the R2eff file to put into spin structure.
        relax_disp.r2eff_read_spin(id=exp_id, spin_id=cur_spin_id, file=file_name, dir=ds.resdir, disp_point_col=1, data_col=2, error_col=3)

        # Add to counter.
        i += 1

print("Did following number of iterations: %i"%i)

# Now do fitting.

# Change pipe.
pipe_name_MODEL = "%s_%s"%(pipe_name, ds.data[0])
pipe.copy(pipe_from=pipe_name, pipe_to=pipe_name_MODEL, bundle_to = pipe_bundle)
pipe.switch(pipe_name=pipe_name_MODEL)

# Copy R2eff, but not the original parameters
value.copy(pipe_from=pipe_name_r2eff, pipe_to=pipe_name_MODEL, param='r2eff')

# Then select model.
relax_disp.select_model(model=ds.data[0])

# Set the R20 parameters in the default grid search using the minimum R2eff value.
if ds.set_grid_r20_from_min_r2eff:
    relax_disp.set_grid_r20_from_min_r2eff(force=False)

# Remove insignificant
relax_disp.insignificance(level=ds.insignificance)

# Perform Grid Search.
grid_search(lower=None, upper=None, inc=ds.GRID_INC, constraints=True, verbosity=ds.verbosity)

# Define function to store grid results.
def save_res(res_spins):
    res_list = []
    for res_name, res_num, spin_name, params in res_spins:
        cur_spin_id = ":%i@%s"%(res_num, spin_name)
        cur_spin = return_spin(cur_spin_id)

        par_dic = {}
        # Now read the parameters.
        for mo_param in cur_spin.params:
            par_dic.update({mo_param : getattr(cur_spin, mo_param) })

        # Append result.
        res_list.append([res_name, res_num, spin_name, par_dic])

    return res_list

ds.grid_results = save_res(cur_spins)

## Now do minimisation.
minimise(min_algor='simplex', func_tol=ds.set_func_tol, max_iter=ds.set_max_iter, constraints=True, scaling=True, verbosity=ds.verbosity)

ds.min_results = save_res(cur_spins)

# Compare results.
for i in range(len(cur_spins)):
    res_name, res_num, spin_name, params = cur_spins[i]
    cur_spin_id = ":%i@%s"%(res_num, spin_name)
    cur_spin = return_spin(cur_spin_id)

    grid_params = ds.grid_results[i][3]
    min_params = ds.min_results[i][3]
    # Now read the parameters.
    print("For spin: '%s'"%cur_spin_id)
    for mo_param in cur_spin.params:
        # The R2 is a dictionary, depending on spectrometer frequency.
        if isinstance(getattr(cur_spin, mo_param), dict):
            grid_r2 = grid_params[mo_param]
            min_r2 = min_params[mo_param]
            set_r2 = params[mo_param]
            for key, val in set_r2.items():
                grid_r2_frq = grid_r2[key]
                min_r2_frq = min_r2[key]
                set_r2_frq = set_r2[key]
                frq = float(key.split(EXP_TYPE_CPMG_SQ+' - ')[-1].split('MHz')[0])
                rel_change = sqrt( (min_r2_frq - set_r2_frq)**2/(min_r2_frq)**2 )
                if ds.print_res:
                    print("%s %s %s %s %.1f GRID=%.3f MIN=%.3f SET=%.3f RELC=%.3f"%(cur_spin.model, res_name, cur_spin_id, mo_param, frq, grid_r2_frq, min_r2_frq, set_r2_frq, rel_change) )
                if rel_change > ds.rel_change:
                    if ds.print_res:
                        print("WARNING: rel change level is above %.2f, and is %.4f."%(ds.rel_change, rel_change))
                        print("###################################")
        else:
            grid_val = grid_params[mo_param]
            min_val = min_params[mo_param]
            set_val = params[mo_param]
            rel_change = sqrt( (min_val - set_val)**2/(min_val)**2 )
            if ds.print_res:
                print("%s %s %s %s GRID=%.3f MIN=%.3f SET=%.3f RELC=%.3f"%(cur_spin.model, res_name, cur_spin_id, mo_param, grid_val, min_val, set_val, rel_change) )
            if rel_change > ds.rel_change:
                if ds.print_res:
                    print("WARNING: rel change level is above %.2f, and is %.4f."%(ds.rel_change, rel_change))
                    print("###################################")

# Plot curves.
if ds.plot_curves:
    relax_disp.plot_disp_curves(dir=ds.resdir, force=True)
