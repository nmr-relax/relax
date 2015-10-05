# Python imports
import numpy as np
from numpy.lib import recfunctions 
import pandas as pd
import sys
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from matplotlib import style
from scipy import stats
style.use('ggplot')

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.mol_res_spin import spin_loop

# Read data
state.load("data_state")
pipe.current()
pipe.display()

# Loop over pipes
pipes = ['ref_data', 'new_data']

# Make global lists
res_nums = []
res_names = []
spin_dws = []
spin_dw_avgs = []
spin_dw_errs = []

for i_pipe in pipes:
    pipe.switch(pipe_name=i_pipe)

    # Make lokal list
    res_num = []
    res_name = []
    spin_dw = []
    spin_dw_avg = []
    spin_dw_err = []


    # Make some few histograms
    i = 0
    i_max = 3
    for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
        #print cur_spin.__dict__.keys(), cur_spin.name, cur_spin.num, cur_spin.select
        res_num.append(resi)
        res_name.append(resn)
        spin_dw.append(cur_spin.dw)
        spin_dw_err.append(cur_spin.dw_err)

        # Calculate the average of dw from sim list
        dw_avg = np.average(cur_spin.dw_sim)
        spin_dw_avg.append(dw_avg)

        # Calculate the standard deviation with numpy and compare with stored value.
        dw_std = np.std(cur_spin.dw_sim, ddof=1)
        if not np.allclose(dw_std, cur_spin.dw_err, rtol=1e-14, atol=1e-14):
            print "The std errors are not equal !"
            print dw_std - cur_spin.dw_err
            sys.exit()

        # Print distribution of simulated values
        if i < i_max:
            fig = plt.figure()
            ax = fig.gca()
            weights = np.ones_like(cur_spin.dw_sim)/len(cur_spin.dw_sim)
            n, bins, patches = plt.hist(cur_spin.dw_sim, 50, normed=True, histtype='stepfilled', label=spin_id)
            #n, bins, patches = plt.hist(cur_spin.dw_sim, 50, weights=weights, histtype='stepfilled', label=spin_id)
            plt.setp(patches, 'facecolor', 'g', 'alpha', 0.75)
            plt.legend()

            # add a line showing the expected distribution
            y = mlab.normpdf( bins, cur_spin.dw, cur_spin.dw_err)
            plt.plot(bins, y, 'k--', linewidth=1.5)

            y = mlab.normpdf( bins, dw_avg, cur_spin.dw_err)
            ym = y.max()
            plt.plot(bins, y, 'r--', linewidth=1.5)

            # Annotate
            ax.annotate('dw', xy=(cur_spin.dw, 0.0), xytext=(cur_spin.dw, 0.5*ym), arrowprops=dict(facecolor='black', shrink=0.1))
            ax.annotate('dw_avg', xy=(dw_avg, 0.0), xytext=(dw_avg, 0.8*ym), arrowprops=dict(facecolor='red', shrink=0.1))


        # Add to counter
        i += 1

    # Add to global list
    res_nums.append(np.asarray(res_num))
    res_names.append(np.asarray(res_name))
    spin_dws.append(np.asarray(spin_dw))
    spin_dw_avgs.append(np.asarray(spin_dw_avg))
    spin_dw_errs.append(np.asarray(spin_dw_err))

# Sanity tests
if not np.all(res_nums[0] == res_nums[1]):
    print "Res nums are not equal !"
    sys.exit()

if not np.all(res_names[0] == res_names[1]):
    print "Res names are not equal !"
    sys.exit()

# Plot the data as it is
plt.figure()
plt.errorbar(spin_dws[0], spin_dws[1], xerr=spin_dw_errs[0], yerr=spin_dw_errs[1], fmt='.')
# Plot the new means
plt.plot(spin_dw_avgs[0], spin_dw_avgs[1], linestyle='', marker='o', fillstyle='full')

# Ref line
x = np.linspace(spin_dws[0].min(), spin_dws[0].max(), num=50)
plt.plot(x, x, linestyle='-', marker='')

# Try do linear regression
slope, intercept, r_value, p_value, std_err = stats.linregress(spin_dws[0], spin_dws[1])
print "lin reg for original data points: a=%1.5f, b=%1.4f, r=%1.3f, p=%1.8f, std_err=%1.5f" % (slope, intercept, r_value, p_value, std_err)

slope_avg, intercept_avg, r_value_avg, p_value_avg, std_err_avg = stats.linregress(spin_dw_avgs[0], spin_dw_avgs[1])
print "lin reg for avg MC   data points: a=%1.5f, b=%1.4f, r=%1.3f, p=%1.8f, std_err=%1.5f" % (slope_avg, intercept_avg, r_value_avg, p_value_avg, std_err_avg)

#plt.show()
for i in plt.get_fignums():
    plt.figure(i)
    plt.savefig('figure%d.png' % i)


# Make t-test
data = np.array([res_nums[0], res_names[0], spin_dws[0], spin_dws[1], spin_dw_avgs[0], spin_dw_avgs[1], spin_dw_errs[0], spin_dw_errs[1]])
data = np.core.records.fromarrays(data, names='res_num, res_name, ref_val, ni_val, ref_avg_val, ni_avg_val, ref_err, ni_err', formats = 'i8, S1, f8, f8, f8, f8, f8, f8')

# The number of data points in each
ref_n = 500
ni_n = 500


# Make a selection of those whose p value is under 0.05
alpha = 0.05

# Loop over the mean types
means = [('ref_val', 'ni_val', 'n'), ('ref_avg_val', 'ni_avg_val', 'a')]

for ref_val, ni_val, t in means:
    ## Try a t calculation with Welch's t test, Equal or unequal sample sizes, unequal variances
    ## https://en.wikipedia.org/wiki/Welch%27s_t_test#Calculations
    print ref_val, ni_val, t
    t_w = np.abs( (data[ref_val] - data[ni_val])/np.sqrt(data['ref_err']**2/ref_n + data['ni_err']**2/ni_n) )
    data = recfunctions.append_fields(data, 't_w_%s'%t, t_w, dtypes=data['ni_val'].dtype, usemask=False, asrecarray=True)

    # The within-group degrees of freedom with Welch t-test
    df_wt = np.square(data['ref_err']**2/ref_n + data['ni_err']**2/ni_n) / ( np.square(data['ref_err']**2)/(np.square(ref_n)*(ref_n-1)) + np.square(data['ni_err']**2)/(np.square(ni_n)*(ni_n-1)) )
    data = recfunctions.append_fields(data, 'df_wt_%s'%t, df_wt, dtypes=data['ref_val'].dtype, usemask=False, asrecarray=True)

    # The p-value for the Welch t-test
    # The multiplication by 2, is the meaning of a two-tailed test
    p_wt = stats.distributions.t.sf(np.abs(t_w), df_wt )*2
    data = recfunctions.append_fields(data, 'p_wt_%s'%t, p_wt, dtypes=data['ni_val'].dtype, usemask=False, asrecarray=True)

    # Now sort the data according to the p-values
    print "Sorting according to Welch's tests p-value column.\n"
    data = np.sort(data, order=['p_wt_%s'%t])

    # Number of groups
    k = data.shape[0] 

    # Now add the i column to the data
    i = np.array(range(k, 0, -1))
    data = recfunctions.append_fields(data, 'i_%s'%t, i, dtypes=data['res_num'].dtype, usemask=False, asrecarray=True)

    print "alpha=%1.2f"%(alpha)
    p_sel = data['p_wt_%s'%t] < alpha 
    print "Number of test which p_value is below alpha=%1.2f is equal: %i, out of k groups: %i\n"%(alpha, np.sum(p_sel), k)

    # Now calculate the adjusted alpha value fom Holm-sidak
    a_adj = alpha / i
    data = recfunctions.append_fields(data, 'a_adj_%s'%t, a_adj, dtypes=data['ni_val'].dtype, usemask=False, asrecarray=True)

    # Now test if each p-value is less than its corresponding adjusted alpha value
    p_pass = data['p_wt_%s'%t] < a_adj
    r = np.sum(p_pass)
    data = recfunctions.append_fields(data, 'p_pass_%s'%t, p_pass, dtypes=bool, usemask=False, asrecarray=True)

    print "Number of test which p_value is below its adjusted alpha value is equal: %i, out of k groups: %i\n"%(r, k)

# Print
#print " ".join(data.dtype.names)
#for cols in data:  
#    print "{0:7d} {1:>8s} {2:>7.4f} {3:>6.4f} {4:>11.4f} {5:>10.4f} {6:>7.4f} {7:>6.4f} {8:>5.3f} {9:>7.1f} {10:>6.3f} {11:>2d}".format(cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], cols[6], cols[7], cols[8], cols[9], cols[10], cols[11], cols[12], cols[13]) 

# Print by pandas
data_pd = pd.DataFrame(data)
pd.set_option('display.width', 1000)
#pd.options.display.float_format = '{:5,.4f}'.format

print data_pd
