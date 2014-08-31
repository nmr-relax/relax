# Calculate the R and I0 errors via bootstrapping.
# As this is an exact solution, bootstrapping is identical to Monte Carlo simulations.

# Python module imports.
from collections import OrderedDict
#import pickle
import cPickle as pickle
from numpy import array, asarray, ones, std

# Open data.
dic = pickle.load( open( "estimate_errors.p", "rb" ) )

# Extract
R = dic['R']
I0 = dic['I0']
params = dic['params']
np = dic['np']
sim = dic['sim']
nt_min = dic['nt_min']
nt_max = dic['nt_max']
all_times = dic['all_times']
I_err_level = dic['I_err_level']
I_err_std = dic['I_err_std']
all_errors = dic['all_errors']

# Make plots?
make_plots = True
if make_plots:
    from pylab import show, plot, legend, figure, title, subplots
    from matplotlib.font_manager import FontProperties
    fontP = FontProperties()
    fontP.set_size('small')

# Print to screen?
print_log = True

nt_l = []
R_e_l = []
R_ew_l = []
sigma_R_l = []
R_m_l = []
R_m_l = []
I0_m_l = []
sigma_R_covar_l = []
sigma_I0_covar_l = []
sigma_R_sim_l = []
sigma_I0_sim_l = []

# Loop over dic to collect data.
if print_log:
    text = "#%7s %-7s %-7s %-7s %-7s %-7s %-10s %-7s" % ('i', 'R_e', 'R_ew', 'R_m', 'sigma_R_covar', 'sigma_I0_covar', 'sigma_R_sim', 'sigma_I0_sim')
    print(text)

#for i in range(1):
for i in range(np):
    # Base data
    nt = dic[i]['nt']
    nt_l.append(nt)
    times = dic[i]['times']
    indexes = dic[i]['indexes']
    errors = dic[i]['errors']
    I = dic[i]['I']
    I_err = dic[i]['I_err']

    # Estimated from linear problem.
    R_e = dic[i]['R_e']
    R_e_l.append(R_e)
    I0_e = dic[i]['I0_e']

    # Estimated from weighted linear problem.
    R_ew = dic[i]['R_ew']
    R_ew_l.append(R_ew)
    I0_ew = dic[i]['I0_ew']

    # Estimated from propagation of errors.
    sigma_R = dic[i]['sigma_R']
    sigma_R_l.append(std(sigma_R))

    # Output from minfx.
    R_m = dic[i]['R_m']
    I0_m = dic[i]['I0_m']

    # Co-variance estimation.
    jacobian = dic[i]['jacobian']
    weights = dic[i]['weights']
    pcov = dic[i]['pcov']

    # The sigma from Co-variance.
    sigma_R_covar = dic[i]['sigma_R_covar']
    sigma_R_covar_l.append(sigma_R_covar)
    sigma_I0_covar = dic[i]['sigma_I0_covar']
    sigma_I0_covar_l.append(sigma_I0_covar)

    # The sigma from Monte-Carlo.
    sigma_R_sim = dic[i]['sigma_R_sim']
    sigma_R_sim_l.append(sigma_R_sim)
    sigma_I0_sim = dic[i]['sigma_I0_sim']
    sigma_I0_sim_l.append(sigma_I0_sim)

    if print_log:
        text = " %6i   %1.2f   %1.2f   %4.2f   %4.8f   %4.8f   %4.8f   %4.8f" % (i, R_e, R_ew, R_m, sigma_R_covar, sigma_I0_covar, sigma_R_sim, sigma_I0_sim)
        print(text)

# Printout.
#print("\n\nParameter errors:")
#print("Monte-Carlo sigma_R_minfx:   %25.20f" % sigma_R_minfx)
#print("Monte-Carlo sigma_I0_minfx:  %25.20f" % sigma_I0_minfx)
#print("Intensity errror level was: %3.3f" % (I_err_level) )
#print("Intensity std dev was: %3.3f" % (I_err_std) )
#I0_err_str = " ".join(format(x, "1.2f") for x in all_errors)
#print("I0 errors was drawn from: %s" % (I0_err_str) )

if make_plots:
    # sigma R
    fig = figure(num=1, figsize=(20, 8))

    ax1 = fig.add_subplot(121)
    title("Correlation plot of Sigma R\n per R2eff point. Estimation method vs Monte-Carlo.")

    ax2 = ax1.twinx()
    ax1.set_xlabel('R_err')
    ax1.set_ylabel('R_err')
    ax2.set_ylabel('Nr of points')

    ax1.plot(asarray(sigma_R_sim_l), asarray(sigma_R_sim_l), 'b.', label='Monte-Carlo')
    ax1.plot(asarray(sigma_R_sim_l), asarray(sigma_R_covar_l), 'r.', label='Covar')
    ax2.plot(asarray(sigma_R_sim_l), asarray(nt_l), 'k.', label='Number of points')

    ax1.legend(loc='upper left', shadow=True, prop = fontP)
    ax2.legend(loc='upper right', shadow=True, prop = fontP)

    # sigma I0
    ax1 = fig.add_subplot(122)
    title("Correlation plot of Sigma I\n per R2eff point. Estimation method vs Monte-Carlo.")

    ax2 = ax1.twinx()
    ax1.set_xlabel('I_err')
    ax1.set_ylabel('I_err')
    ax2.set_ylabel('Nr of points')

    ax1.plot(asarray(sigma_I0_sim_l), asarray(sigma_I0_sim_l), 'b.', label='Monte-Carlo')
    ax1.plot(asarray(sigma_I0_sim_l), asarray(sigma_I0_covar_l), 'r.', label='Covar')
    ax2.plot(asarray(sigma_I0_sim_l), asarray(nt_l), 'k.', label='Number of points')

if make_plots:
    show()
