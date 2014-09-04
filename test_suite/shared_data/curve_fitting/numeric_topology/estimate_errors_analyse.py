# Calculate the R and I0 errors via bootstrapping.
# As this is an exact solution, bootstrapping is identical to Monte Carlo simulations.

# Python module imports.
from collections import OrderedDict
#import pickle
import pickle as pickle
from numpy import array, asarray, diag, ones, std, sqrt
from os import getcwd, makedirs, path, sep

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
make_plots = False
make_peak_lists = True

if make_plots:
    from pylab import show, plot, legend, figure, title, subplots
    from matplotlib.font_manager import FontProperties
    fontP = FontProperties()
    fontP.set_size('small')

# Print to screen?
print_log = True

# Loop over nt_max. Create lists in dic.
dic_d = OrderedDict()
for nt_max in nt_max_list:
    # Create index in dic.
    dic_d[nt_max] = OrderedDict()

    dic_d[nt_max]['nt_l'] = []
    dic_d[nt_max]['R_e_l'] = []
    dic_d[nt_max]['R_ew_l'] = []
    dic_d[nt_max]['sigma_R_l'] = []
    dic_d[nt_max]['R_m_l'] = []
    dic_d[nt_max]['R_m_l'] = []
    dic_d[nt_max]['I0_m_l'] = []
    dic_d[nt_max]['sigma_R_covar_l'] = []
    dic_d[nt_max]['sigma_I0_covar_l'] = []
    dic_d[nt_max]['sigma_R_sim_l'] = []
    dic_d[nt_max]['sigma_I0_sim_l'] = []
    dic_d[nt_max]['sigma_R_covar_scale_l'] = []
    dic_d[nt_max]['sigma_I0_covar_scale_l'] = []


# Loop over nt_max. Create lists in dic.
dic = OrderedDict()
for nt_max in nt_max_list:
    # Open data.
    dic = pickle.load( open( "estimate_errors_data_nt%i.cp"%nt_max, "rb" ) )

    # Extract, if random time points was used.
    do_random_nr_time_points = dic['do_random_nr_time_points']
    print("# Random timepoints=%s, nt_max=%i" % (do_random_nr_time_points, nt_max))

    # Loop over dic to collect data.
    if print_log:
        text = "#%7s %-7s %-7s %-7s %-7s %-7s %-7s %-7s, %-7s" % ('i', 'R_e', 'R_ew', 'R_m', 'sigma_R_covar', 'sigma_I0_covar', 'sigma_R_sim', 'sigma_I0_sim', 'sigma_R_diff')
        print(text)

    #for i in range(1):
    for i in range(np):
        # Base data
        nt = dic[i]['nt']
        dic_d[nt_max]['nt_l'].append(nt)
        times = dic[i]['times']
        indexes = dic[i]['indexes']
        errors = dic[i]['errors']
        I = dic[i]['I']
        I_err = dic[i]['I_err']

        # Estimated from linear problem.
        R_e = dic[i]['R_e']
        dic_d[nt_max]['R_e_l'].append(R_e)
        I0_e = dic[i]['I0_e']

        # Estimated from weighted linear problem.
        R_ew = dic[i]['R_ew']
        dic_d[nt_max]['R_ew_l'].append(R_ew)
        I0_ew = dic[i]['I0_ew']

        # Estimated from propagation of errors.
        sigma_R = dic[i]['sigma_R']
        dic_d[nt_max]['sigma_R_l'].append(std(sigma_R))

        # Output from minfx.
        R_m = dic[i]['R_m']
        I0_m = dic[i]['I0_m']

        # Co-variance estimation.
        jacobian = dic[i]['jacobian']
        weights = dic[i]['weights']
        pcov = dic[i]['pcov']

        # The sigma from Co-variance.
        sigma_R_covar = dic[i]['sigma_R_covar']
        dic_d[nt_max]['sigma_R_covar_l'].append(sigma_R_covar)
        sigma_I0_covar = dic[i]['sigma_I0_covar']
        dic_d[nt_max]['sigma_I0_covar_l'].append(sigma_I0_covar)

        # The sigma from Monte-Carlo.
        sigma_R_sim = dic[i]['sigma_R_sim']
        dic_d[nt_max]['sigma_R_sim_l'].append(sigma_R_sim)
        sigma_I0_sim = dic[i]['sigma_I0_sim']
        dic_d[nt_max]['sigma_I0_sim_l'].append(sigma_I0_sim)

        # Scale the Co-variance.
        N = nt
        p = 2
        # Number of degrees of freedom.
        n = N - p
        pcov_scale = pcov / n
        sigma_R_covar_scale, sigma_I0_covar_scale = sqrt(diag(pcov_scale))
        # Collect
        dic_d[nt_max]['sigma_R_covar_scale_l'].append(sigma_R_covar_scale)
        dic_d[nt_max]['sigma_I0_covar_scale_l'].append(sigma_I0_covar_scale)

        # Calculate the difference between Monte Carlo and Covar
        sigma_R_diff = sigma_R_sim - sigma_R_covar

        if print_log:
            text = " %6i   %1.2f   %1.2f   %4.2f   %4.8f   %4.8f   %4.8f   %4.8f   %4.8f" % (i, R_e, R_ew, R_m, sigma_R_covar, sigma_I0_covar, sigma_R_sim, sigma_I0_sim, sigma_R_diff)
            print(text)

#floats_str = " ".join(format(x, "1.2f") for x in all_floats)
if make_plots:
    # sigma R
    fig = figure(num=1, figsize=(20, 8))

    nt_max = 5
    sigma_R_sim_l = dic_d[nt_max]['sigma_R_sim_l']
    sigma_R_covar_l = dic_d[nt_max]['sigma_R_covar_l']
    sigma_R_covar_scale_l = dic_d[nt_max]['sigma_R_covar_scale_l']
    nt_l = dic_d[nt_max]['nt_l']

    ax1 = fig.add_subplot(121)
    title("Correlation plot of Sigma R.\nEstimation method vs Monte-Carlo. nt=%i"%nt_max)

    ax2 = ax1.twinx()
    ax1.set_xlabel('R_err')
    ax1.set_ylabel('R_err')
    ax2.set_ylabel('Nr of points')

    ax1.plot(asarray(sigma_R_sim_l), asarray(sigma_R_sim_l), 'b.-', label='Monte-Carlo')
    ax1.plot(asarray(sigma_R_sim_l), asarray(sigma_R_covar_l), 'r.', label='Covar')
    ax1.plot(asarray(sigma_R_sim_l), asarray(sigma_R_covar_scale_l), 'g.', label='Covar scale')
    ax2.plot(asarray(sigma_R_sim_l), asarray(nt_l), 'k.', label='Number of points')

    ax1.legend(loc='upper left', shadow=True, prop = fontP)
    ax2.legend(loc='upper right', shadow=True, prop = fontP)

    # sigma I0
    ax1 = fig.add_subplot(122)
    title("Correlation plot of Sigma I.\nEstimation method vs Monte-Carlo. nt=%i"%nt_max)

    sigma_I0_sim_l = dic_d[nt_max]['sigma_I0_sim_l']
    sigma_I0_covar_l = dic_d[nt_max]['sigma_I0_covar_l']
    sigma_I0_covar_scale_l = dic_d[nt_max]['sigma_I0_covar_scale_l']
    nt_l = dic_d[nt_max]['nt_l']

    ax2 = ax1.twinx()
    ax1.set_xlabel('I_err')
    ax1.set_ylabel('I_err')
    ax2.set_ylabel('Nr of points')

    ax1.plot(asarray(sigma_I0_sim_l), asarray(sigma_I0_sim_l), 'b.-', label='Monte-Carlo')
    ax1.plot(asarray(sigma_I0_sim_l), asarray(sigma_I0_covar_l), 'r.', label='Covar')
    ax1.plot(asarray(sigma_I0_sim_l), asarray(sigma_I0_covar_scale_l), 'g.', label='Covar scale')
    ax2.plot(asarray(sigma_I0_sim_l), asarray(nt_l), 'k.', label='Number of points')

#####################################################################################
    fig = figure(num=2, figsize=(20, 8))

    nt_max = 10
    sigma_R_sim_l = dic_d[nt_max]['sigma_R_sim_l']
    sigma_R_covar_l = dic_d[nt_max]['sigma_R_covar_l']
    sigma_R_covar_scale_l = dic_d[nt_max]['sigma_R_covar_scale_l']
    nt_l = dic_d[nt_max]['nt_l']

    ax1 = fig.add_subplot(121)
    title("Correlation plot of Sigma R.\nEstimation method vs Monte-Carlo. nt=%i"%nt_max)

    ax2 = ax1.twinx()
    ax1.set_xlabel('R_err')
    ax1.set_ylabel('R_err')
    ax2.set_ylabel('Nr of points')

    ax1.plot(asarray(sigma_R_sim_l), asarray(sigma_R_sim_l), 'b.-', label='Monte-Carlo')
    ax1.plot(asarray(sigma_R_sim_l), asarray(sigma_R_covar_l), 'r.', label='Covar')
    ax1.plot(asarray(sigma_R_sim_l), asarray(sigma_R_covar_scale_l), 'g.', label='Covar scale')
    ax2.plot(asarray(sigma_R_sim_l), asarray(nt_l), 'k.', label='Number of points')

    ax1.legend(loc='upper left', shadow=True, prop = fontP)
    ax2.legend(loc='upper right', shadow=True, prop = fontP)

    # sigma I0
    ax1 = fig.add_subplot(122)
    title("Correlation plot of Sigma I.\nEstimation method vs Monte-Carlo. nt=%i"%nt_max)

    sigma_I0_sim_l = dic_d[nt_max]['sigma_I0_sim_l']
    sigma_I0_covar_l = dic_d[nt_max]['sigma_I0_covar_l']
    sigma_I0_covar_scale_l = dic_d[nt_max]['sigma_I0_covar_scale_l']
    nt_l = dic_d[nt_max]['nt_l']

    ax2 = ax1.twinx()
    ax1.set_xlabel('I_err')
    ax1.set_ylabel('I_err')
    ax2.set_ylabel('Nr of points')

    ax1.plot(asarray(sigma_I0_sim_l), asarray(sigma_I0_sim_l), 'b.-', label='Monte-Carlo')
    ax1.plot(asarray(sigma_I0_sim_l), asarray(sigma_I0_covar_l), 'r.', label='Covar')
    ax1.plot(asarray(sigma_I0_sim_l), asarray(sigma_I0_covar_scale_l), 'g.', label='Covar scale')
    ax2.plot(asarray(sigma_I0_sim_l), asarray(nt_l), 'k.', label='Number of points')

if make_plots:
    show()

if make_peak_lists:
    # Create dir for peak lists.
    peak_dir = getcwd() + sep + 'estimate_errors_peak_lists'
    if not path.exists(peak_dir):
        makedirs(peak_dir)

    # Set which data to write for.
    nt_max = 10
    # Open data.
    dic = pickle.load( open( "estimate_errors_data_nt%i.cp"%nt_max, "rb" ) )

    # Loop over original intensity, or noise true data.
    for ref_int in ['I', 'I_err']:
        #for i in range(np):
        for i in range(1):
            if ref_int == 'I':
                file_path = peak_dir + sep + "ntmax_%i_disp_%i_ref.ser" % (nt_max, i)
            else:
                file_path = peak_dir + sep + "ntmax_%i_disp_%i.ser" % (nt_max, i)
    
            wfile = open(file_path, 'w')
    
            wfile.write("REMARK SeriesTab Input:" + "\n")
            wfile.write("REMARK Mode: Maximum Dimensions: 2" + "\n")
            wfile.write("REMARK Input Region:    X +/- 0 X-ZF: 1" + "\n")
            wfile.write("REMARK Analysis Region: X +/- 0" + "\n")
            wfile.write("REMARK Input Region:    Y +/- 0 Y-ZF: 1" + "\n")
            wfile.write("REMARK Analysis Region: Y +/- 0" + "\n")
            wfile.write("" + "\n")
            # Get number of intensities.
    
            nt = dic[i]['nt']
            times = dic[i]['times']
            errors = dic[i]['errors']
            I = dic[i]['I']
            I_err = dic[i]['I_err']
            if ref_int == 'I':
                I_val = I
            else:
                I_val = I_err
    
            Z_A_list = 'Z_A' + ' Z_A'.join(str(x) for x in range(nt))
            f_list = " ".join(nt*['%7.4f'])
            wfile.write("VARS   INDEX X_AXIS Y_AXIS X_PPM Y_PPM VOL ASS X1 X3 Y1 Y3 " + Z_A_list + "\n")
            wfile.write("FORMAT %5d %9.3f %9.3f %8.3f %8.3f %+e %s %4d %4d %4d %4d " + f_list + "\n")
            wfile.write("" + "\n")
            wfile.write("NULLVALUE -666" + "\n")
            wfile.write("NULLSTRING *" + "\n")
            wfile.write("" + "\n")
    
            # Write for all spins.
            for spin in range(1, 2):
                INDEX = spin
                X_AXIS = 450.000 
                Y_AXIS = 100.000
                X_PPM = 8.000
                Y_PPM = 120.000
                VOL = I_err[0]
                ASS = "A%iN-HN"%spin
                X1 = 400
                X3 = 403
                Y1 = 75
                Y3 = 77
                I_val_mod = I_val / VOL
                I_val_mod_str = " ".join(format(x, "1.4f") for x in I_val_mod)
    
                text = "%5s   %3.3f   %3.3f   %2.3f  %3.3f %1.6e %8s  %3i  %3i  %3i  %3i  %s" % (INDEX, X_AXIS, Y_AXIS, X_PPM, Y_PPM, VOL, ASS, X1, X3, Y1, Y3, I_val_mod_str)
                wfile.write(text + "\n")

            wfile.close()
