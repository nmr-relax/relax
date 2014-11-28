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
"""Module for the using of nmrglue."""

# relax module imports.
from lib.errors import RelaxError
from lib.software.nmrglue import contour_plot, hist_plot, read_spectrum
from pipe_control.pipes import check_pipe
from pipe_control.spectrum import add_spectrum_id, check_spectrum_id, delete


def add_nmrglue_data(spectrum_id=None, nmrglue_data=None):
    """Add the nmrglue_data to the data store.

    @keyword spectrum_id:   The spectrum ID string.
    @type spectrum_id:      str
    @keyword nmrglue_data:  The nmrglue data as class instance object.
    @type nmrglue_data:     lib.spectrum.objects.Nmrglue_data instance
    """

    # Initialise the structure, if needed.
    if not hasattr(cdp, 'ngdata'):
        cdp.ngdata = {}

    # Add the data under the spectrum ID.
    cdp.ngdata[spectrum_id] = nmrglue_data[0]


def read(file=None, dir=None, spectrum_id=None):
    """Read the spectrum file.

    @keyword file:          The name of the file(s) containing the spectrum.
    @type file:             str or list of str
    @keyword dir:           The directory where the file is located.
    @type dir:              str
    @keyword spectrum_id:   The spectrum identification string.
    @type spectrum_id:      str or list of str
    """

    # Data checks.
    check_pipe()

    # Check the file name.
    if file == None:
        raise RelaxError("The file name must be supplied.")

    # Add spectrum ID.
    add_spectrum_id(spectrum_id)

    # Read the spectrum, and get it back as a class instance object.
    nmrglue_data = read_spectrum(file=file, dir=dir)

    # Store the data.
    add_nmrglue_data(spectrum_id=spectrum_id, nmrglue_data=nmrglue_data)


def plot_contour(spectrum_id=None, contour_start=30000., contour_num=20, contour_factor=1.20, ppm=True, show=False):
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

    # Call the contour plot.
    ax = contour_plot(spectrum_id=spectrum_id, contour_start=contour_start, contour_num=contour_num, contour_factor=contour_factor, ppm=ppm, show=show)

    # Return the axis instance, for possibility for additional decoration.
    return ax


def plot_hist(ndarray=None, hist_kwargs=None, show=False):
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

    # Call the contour plot.
    ax = hist_plot(ndarray=ndarray, hist_kwargs=hist_kwargs, show=show)

    # Return the axis instance, for possibility for additional decoration.
    return ax

