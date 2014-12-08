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
from data_store.nmrglue import Nmrglue, Nmrglue_dict
from lib.errors import RelaxError
from lib.software.nmrglue import contour_plot, hist_plot, read_spectrum
from pipe_control.pipes import check_pipe
from pipe_control.spectrum import check_spectrum_id, delete


def add_nmrglue_data(nmrglue_id=None, dic=None, udic=None, data=None):
    """Add the nmrglue data to the data store under the the given object_name within a dictionary with nmrglue_id key.

    @keyword nmrglue_id:    The dictionary key, to access the data as cdp.nmrglue['nmrglue_id'].
    @type nmrglue_id:       str
    @keyword dic:           The dic structure from nmrglue.
    @type dic:              dict
    @keyword udic:          The dic structure from nmrglue.
    @type udic:             dict
    @keyword data:          The type of data depending on called function.
    @type data:             depend on function
    """

    # Initialise the structure, if needed.
    if not hasattr(cdp, 'nmrglue'):
        cdp.nmrglue = Nmrglue_dict()

    # Add the data under the dictionary key.
    cdp.nmrglue[nmrglue_id] = Nmrglue(dic=dic, udic=udic, data=data)


def add_nmrglue_id(nmrglue_id=None):
    """Add the nmrglue ID to the data store.

    @keyword nmrglue_id:   The nmrglue ID string.
    @type nmrglue_id:      str
    """

    # Initialise the structure, if needed.
    if not hasattr(cdp, 'nmrglue_ids'):
        cdp.nmrglue_ids = []

    # The ID already exists.
    if nmrglue_id in cdp.nmrglue_ids:
        return

    # Add the ID.
    cdp.nmrglue_ids.append(nmrglue_id)


def read(file=None, dir=None, nmrglue_id=None):
    """Read the spectrum file.

    @keyword file:          The name of the file(s) containing the spectrum.
    @type file:             str or list of str
    @keyword dir:           The directory where the file is located.
    @type dir:              str
    @keyword nmrglue_id:    The spectrum identification string.
    @type nmrglue_id:       str or list of str
    """

    # Data checks.
    check_pipe()

    # Check the file name.
    if file == None:
        raise RelaxError("The file name must be supplied.")

    # Multiple ID flags.
    flag_multi = False
    flag_multi_file = False
    if isinstance(nmrglue_id, list):
        flag_multi = True
    if isinstance(file, list):
        flag_multi_file = True

    # List argument checks.
    if flag_multi:
        # Both of list type,
        if not flag_multi_file:
            raise RelaxError("The file and spectrum ID  must both be of list type.")

        # List lengths for multiple files.
        if flag_multi_file and len(nmrglue_id) != len(file):
            raise RelaxError("The file list %s and spectrum ID list %s do not have the same number of elements." % (file, nmrglue_id))

    # More list argument checks (when only one spectrum ID is supplied).
    else:
        # Multiple files.
        if flag_multi_file:
            raise RelaxError("If multiple files are supplied, then multiple spectrum IDs must also be supplied.")

    # Convert the file argument to a list if necessary.
    if not isinstance(file, list):
        file = [file]

    # Convert the nmrglue_id argument to a list if necessary.
    if not isinstance(nmrglue_id, list):
        nmrglue_id = [nmrglue_id]

    # Loop over the files.
    for i, file_i in enumerate(file):
        # Assign spectrum id.
        nmrglue_id_i = nmrglue_id[i]

        # Add spectrum ID.
        add_nmrglue_id(nmrglue_id_i)

        # Read the spectrum, and get it back two dictionaries, and a numpy array.
        dic, udic, data = read_spectrum(file=file_i, dir=dir)

        # Store the data.
        add_nmrglue_data(nmrglue_id=nmrglue_id_i, dic=dic, udic=udic, data=data)


def plot_contour(nmrglue_id=None, contour_start=30000., contour_num=20, contour_factor=1.20, ppm=True, show=False):
    """Plot the spectrum as contour plot.

    @keyword nmrglue_id:        The spectrum identification string.
    @type nmrglue_id:           str or list of str
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
    dic  = cdp.nmrglue[nmrglue_id].dic
    udic  = cdp.nmrglue[nmrglue_id].udic
    data = cdp.nmrglue[nmrglue_id].data

    # Call the contour plot.
    ax = contour_plot(dic=dic, udic=udic, data=data, contour_start=contour_start, contour_num=contour_num, contour_factor=contour_factor, ppm=ppm, show=show)

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

