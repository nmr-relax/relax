###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for the wrapper functions around the nmrglue module."""

# Python module imports.
import matplotlib.pyplot as plt
import matplotlib.cm
from minfx.generic import generic_minimise
from numpy import arange, argmax, asarray, exp, log, max, ones, pi, sqrt


# relax module imports.
from extern import nmrglue
from lib.errors import RelaxError
from lib.io import get_file_path
from lib.spectrum.objects import Nmrglue_data
from target_functions.chi2 import chi2_rankN


def contour_plot(spectrum_id=None, contour_start=30000., contour_num=20, contour_factor=1.20, ppm=True, show=False):
    """Plot the spectrum as contour plot.

    @keyword spectrum_id:       The spectrum identification string.
    @type spectrum_id:          str or list of str
    @keyword contour_start:     Contour level start value
    @type contour_start:        float
    @keyword contour_num:       Number of contour levels
    @type contour_num:          int
    @keyword contour_factor:    Scaling factor between contour levels
    @type contour_factor:       float
    @keyword ppm:               A flag which if True will make the plot in ppm scale. Else it is in points.
    @type ppm:                  bool
    @keyword show:              A flag which if True will make a call to matplotlib.pyplot.show().
    @type show:                 bool
    @return:                    The matplotlib.axes.AxesSubplot class, which can be manipulated to add additional text to the axis.
    @rtype:                     matplotlib.axes.AxesSubplot
    """

    # Extract the data.
    dic  = cdp.ngdata[spectrum_id].dic
    udic  = cdp.ngdata[spectrum_id].udic
    data = cdp.ngdata[spectrum_id].data

    # Setup plot parameters
    # contour map (colors to use for contours)
    cmap = matplotlib.cm.Blues_r

    # Calculate contour levels
    cl = contour_start * contour_factor ** arange(contour_num)

    # Create the figure
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Plot the contours

    # Plot in ppm scale
    if ppm:
        # make ppm scales
        uc_dim1 = nmrglue.pipe.make_uc(dic, data, dim=1)
        ppm_dim1 = uc_dim1.ppm_scale()
        ppm_dim1_0, ppm_dim1_1 = uc_dim1.ppm_limits()
        uc_dim0 = nmrglue.pipe.make_uc(dic, data, dim=0)
        ppm_dim0 = uc_dim0.ppm_scale()
        ppm_dim0_0, ppm_dim0_1 = uc_dim0.ppm_limits()

        ax.contour(data, cl, cmap=cmap, extent=(ppm_dim1_0, ppm_dim1_1, ppm_dim0_0, ppm_dim0_1))

        # Decorate
        ax.set_ylabel("%s (ppm)"%udic[0]['label'])
        ax.set_xlabel("%s (ppm)"%udic[1]['label'])
        ax.set_title("Spectrum")
        lim_dim1 = [ppm_dim1_0, ppm_dim1_1]
        lim_dim0 = [ppm_dim0_0, ppm_dim0_1]
        ax.set_xlim(max(lim_dim1), min(lim_dim1))
        ax.set_ylim(max(lim_dim0), min(lim_dim0))

    else:
        # Plot in points.
        ax.contour(data, cl, cmap=cmap, extent=(0, data.shape[1] - 1, 0, data.shape[0] - 1))

        # Decorate
        ax.set_ylabel("%s (points)"%udic[0]['label'])
        ax.set_xlabel("%s (points)"%udic[1]['label'])
        ax.set_title("Spectrum")

    # If show.
    if show:
        plt.show()

    # Return ax
    return ax


def func_gauss(params=None, x=None):
    """Calculate the Gaussian distribution for a given x value.

    @param params:  The vector of parameter values.
    @type params:   numpy rank-1 float array
    @keyword x:     The x value to calculate the probability for.
    @type x:        numpy array
    @return:        The probability corresponding to x.
    @rtype:         float
    """

    # Unpack,
    # a: The amplitude of the distribution.
    # mu: The center of the distribution.
    # sigma: The standard deviation of the distribution.
    a, mu, sigma = params

    # Calculate and return the probability.
    return a*exp(-(x-mu)**2/(2*sigma**2))


def func_gauss_chi2(params=None, x=None, values=None):
    """Target function for minimising chi2 in minfx, for Gaussian function fit.

    @param params:  The vector of parameter values.
    @type params:   numpy rank-1 float array
    @keyword x:     The x points.
    @type x:        numpy array
    @param values:  The measured y values.
    @type values:   numpy array
    @return:        The chi2 value.
    @rtype:         float
    """

    # Calculate.
    back_calc = func_gauss(params=params, x=x)

    # Return the total chi-squared value.
    errors = ones(values.shape)
    chi2 = chi2_rankN(data=values, back_calc_vals=back_calc, errors=errors)

    # Calculate and return the chi-squared value.
    return chi2


def hist_plot(ndarray=None, hist_kwargs=None, show=False):
    """Flatten the 2D numpy array, and plot as histogram.

    @keyword ndarray:           The numpy array to flatten, and plot as histogram.
    @type ndarray:              numpy array
    @keyword hist_kwargs:       The dictionary of keyword arguments to be send to matplotlib.pyplot.hist() plot function.  If None, standard values will be used.
    @type hist_kwargs:          None or dic
    @keyword show:              A flag which if True will make a call to matplotlib.pyplot.show().
    @type show:                 bool
    @return:                    The matplotlib.axes.AxesSubplot class, which can be manipulated to add additional text to the axis.
    @rtype:                     matplotlib.axes.AxesSubplot
    """

    # Flatten the numpy data array.
    data = ndarray.flatten()

    # Now make a histogram.
    # http://matplotlib.org/1.2.1/examples/api/histogram_demo.html
    fig = plt.figure()
    ax = fig.add_subplot(111)

    if hist_kwargs == None:
        hist_kwargs = {'bins': 1000, 'range': None, 'normed': False, 'facecolor':'green', 'alpha':0.75}

    # Make the plot, and unpack the dictionary keywords.
    #n : array or list of arrays. The values of the histogram bins.
    #bins : array. The edges of the bins.
    #patches : list or list of lists. Silent list of individual patches used to create the histogram.
    n, bins, patches = ax.hist(data, **hist_kwargs)

    # Calculate the bin centers.
    bincenters = 0.5*(bins[1:]+bins[:-1])

    # Find index for maximum number in a bin.
    i = argmax(n)

    # Get the position for the maximum.
    bin_max_x = bincenters[i]

    # Get the amplitude for the maximum.
    bin_max_y = n[i]

    # Try find Full width at half maximum (FWHM). FWHM = 2 * sqrt(2 ln(2 )) * sigma ~ 2.355 * sigma.
    # Half maximum
    hm = 0.5 * bin_max_y

    # Find the first instances of left and right bin, where is lower than hm.
    for j in range(1, len(bins)):
        # Find the center values of the bins.
        left_bin_x = bincenters[i-j]
        right_bin_x = bincenters[i+j]

        # Find the values of the bins.
        left_bin_y = n[i-j]
        right_bin_y = n[i+j]

        if left_bin_y < hm and right_bin_y < hm:
            fwhm = right_bin_x - left_bin_x
            fwhm_std = fwhm / (2 * sqrt(2 * log(2)))
            break

    # Define function to minimise for minfx.
    t_func = func_gauss_chi2

    # All args to function. Params are packed out through function, then other parameters.
    args=(bincenters, n)

    # Initial guess for minimisation.
    x0 = asarray( [bin_max_y, bin_max_x, fwhm_std] )

    # Minimise.
    results_minfx = generic_minimise(func=t_func, args=args, x0=x0, min_algor='simplex', min_options=(), func_tol=1e-25, grad_tol=None, maxiter=10000000, A=None, b=None, full_output=True, print_flag=1)

    # Unpack
    param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results_minfx

    # Extract parameters from vector.
    amp, mu, sigma  = param_vector

    # Recalculate Full width at half maximum (FWHM)
    hm = 0.5 * amp
    fwhm = (2 * sqrt(2 * log(2))) * sigma
    left_bin_x = mu - 0.5 * fwhm
    right_bin_x = mu + 0.5 * fwhm

    # Annotate the center.
    ax.annotate("%3.2f"%mu, xy=(mu, 0.0), xycoords='data', xytext=(mu, 0.25*amp), textcoords='data', size=8, horizontalalignment="center", arrowprops=dict(arrowstyle="->", connectionstyle="arc3, rad=0"), bbox=dict(boxstyle="round", facecolor="w"))

    # Annotate the Full width at half maximum.
    ax.annotate("", xy=(left_bin_x, hm), xycoords='data', xytext=(right_bin_x, hm), textcoords='data', arrowprops=dict(arrowstyle="<->", connectionstyle="arc3, rad=0"))
    ax.annotate("HM=%3.2f\nFWHM=%3.2f\nstd=%3.2f"%(hm, fwhm, sigma), xy=(mu, hm), xycoords="data", size=8, va="center", horizontalalignment="center", bbox=dict(boxstyle="round", facecolor="w"))

    # Calculate and plot the gauss values.
    gauss = func_gauss(params=param_vector, x=bincenters)
    ax.plot(bincenters, gauss, 'r-', label='gauss')

    # Set limits.
    ax.set_xlim(mu-5*sigma, mu+25*sigma)
    ax.set_ylim(0, amp*1.01)

    # If show.
    if show:
        plt.show()

    # Return ax
    return ax


def read_spectrum(file=None, dir=None):
    """Read the spectrum data.

    @keyword file:          The name of the file containing the spectrum.
    @type file:             str
    @keyword dir:           The directory where the file is located.
    @type dir:              str
    @return:                The nmrglue data object containing all relevant data in the spectrum.
    @rtype:                 lib.spectrum.objects.Nmrglue_data instance
    """

    # File path.
    file_path = get_file_path(file, dir)

    # Open file
    dic, data = nmrglue.pipe.read(file_path)
    udic = nmrglue.pipe.guess_udic(dic, data)

    # Initialise the nmrglue data object.
    nmrglue_data = Nmrglue_data()

    # Add the data.
    nmrglue_data.add(file_path=file_path, dic=dic, udic=udic, data=data)

    # Return the nmrglue data object.
    return nmrglue_data
