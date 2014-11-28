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
from numpy import arange
import matplotlib.pyplot as plt
import matplotlib.cm

# relax module imports.
from extern import nmrglue
from lib.errors import RelaxError
from lib.io import get_file_path
from lib.spectrum.objects import Nmrglue_data


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


def hist_plot(ndarray=None, show=False):
    """Flatten the 2D numpy array, and plot as histogram.

    @keyword ndarray:           The numpy array to flatten, and plot as histogram.
    @type ndarray:              numpy array
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

    #kwargs = {'bins': 3000, 'spam': 'ham'}

    # Make the plot.
    n, bins, patches = ax.hist(data, bins=1000, range=None, normed=False, facecolor='green', alpha=0.75)

    # Calculate the bin centers.
    bincenters = 0.5*(bins[1:]+bins[:-1])

    # Set limits.
    ax.set_ylim(0, 10000)
    ax.set_xlim(-30000, 50000)

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
