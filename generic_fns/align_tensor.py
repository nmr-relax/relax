###############################################################################
#                                                                             #
# Copyright (C) 2003-2007 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Python module imports.
from copy import deepcopy
from math import cos, pi, sin
from numpy import arccos, dot, float64, linalg, transpose, zeros
from re import search
import sys

# relax module imports.
from angles import wrap_angles
from data import Data as relax_data_store
from data.align_tensor import AlignTensorList
from data.data_classes import SpecificData
from physical_constants import g13C, g1H, g15N, g17O, g31P, h_bar, mu0
import pipes
from relax_errors import RelaxError, RelaxNoPipeError, RelaxNoTensorError, RelaxStrError, RelaxTensorError, RelaxUnknownParamCombError, RelaxUnknownParamError


def align_data_exists(tensor, pipe=None):
    """Function for determining if alignment data exists in the current data pipe.

    @param tensor:  The alignment tensor identification string.
    @type tensor:   str
    @param pipe:    The data pipe to search for data in.
    @type pipe:     str
    @return:        The answer to the question.
    @type return:   bool
    """

    # The data pipe to check.
    if pipe == None:
        pipe = relax_data_store.current_pipe

    # Test if Axy exists.
    if hasattr(relax_data_store[pipe], 'align_tensor') and relax_data_store[pipe].align_tensor.has_key(tensor):
        return True
    else:
        return False


def copy(tensor_from=None, pipe_from=None, tensor_to=None, pipe_to=None):
    """Function for copying alignment tensor data from one data pipe to another.

    @param tensor_from: The identification string of the alignment tensor to copy the data from.
    @type tensor_from:  str
    @param pipe_from:   The data pipe to copy the alignment tensor data from.  This defaults to the
                        current data pipe.
    @type pipe_from:    str
    @param tensor_to:   The identification string of the alignment tensor to copy the data to.
    @type tensor_to:    str
    @param pipe_to:     The data pipe to copy the alignment tensor data to.  This defaults to the
                        current data pipe.
    @type pipe_to:      str
    """

    # Defaults.
    if tensor_from == tensor_to and pipe_from == None and pipe_to == None:
        raise RelaxError, "The pipe_from and pipe_to arguments cannot both be set to None when the tensor names are the same."
    elif pipe_from == None:
        pipe_from = relax_data_store.current_pipe
    elif pipe_to == None:
        pipe_to = relax_data_store.current_pipe

    # Test if the pipe_from and pipe_to data pipes exist.
    pipes.test(pipe_from)
    pipes.test(pipe_to)

    # Test if pipe_from contains alignment tensor data.
    if not align_data_exists(tensor_from, pipe_from):
        raise RelaxNoTensorError, 'alignment'

    # Test if pipe_to contains alignment tensor data.
    if align_data_exists(tensor_to, pipe_to):
        raise RelaxTensorError, 'alignment'

    # Create the align_tensor dictionary if it doesn't yet exist.
    if not hasattr(relax_data_store[pipe_to], 'align_tensor'):
        relax_data_store[pipe_to].align_tensor = SpecificData()

    # Copy the data.
    relax_data_store[pipe_to].align_tensor[tensor_to] = deepcopy(relax_data_store[pipe_from].align_tensor[tensor_from])


def data_names():
    """Function for returning a list of names of data structures associated with the sequence."""

    names = [ 'align_params' ]

    return names


def default_value(param):
    """
    Alignment tensor parameter default values
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ________________________________________________________________________
    |                        |                    |                        |
    | Data type              | Object name        | Value                  |
    |________________________|____________________|________________________|
    |                        |                    |                        |
    | Axx                    | 'Axx'              | 0.0                    |
    |                        |                    |                        |
    | Ayy                    | 'Ayy'              | 0.0                    |
    |                        |                    |                        |
    | Azz                    | 'Azz'              | 0.0                    |
    |                        |                    |                        |
    | Axxyy                  | 'Axxyy'            | 0.0                    |
    |                        |                    |                        |
    | Axy                    | 'Axy'              | 0.0                    |
    |                        |                    |                        |
    | Axz                    | 'Axz'              | 0.0                    |
    |                        |                    |                        |
    | Ayz                    | 'Ayz'              | 0.0                    |
    |                        |                    |                        |
    | alpha                  | 'alpha'            | 0.0                    |
    |                        |                    |                        |
    | beta                   | 'beta'             | 0.0                    |
    |                        |                    |                        |
    | gamma                  | 'gamma'            | 0.0                    |
    |________________________|____________________|________________________|

    """

    # Return 0.0.
    return 0.0


def delete(tensor):
    """Function for deleting alignment tensor data.

    @param tensor:          The alignment tensor identification string.
    @type tensor:           str
    """

    # Test if the current data pipe exists.
    pipes.test(relax_data_store.current_pipe)

    # Test if alignment tensor data exists.
    if not align_data_exists(tensor):
        raise RelaxNoTensorError, 'alignment'

    # Alias the tensor dictionary.
    align_tensor = relax_data_store[relax_data_store.current_pipe].align_tensor

    # Delete the alignment data.
    align_tensor.pop(tensor)

    # Delete the dictionary if empty.
    if not len(align_tensor):
        del(relax_data_store[relax_data_store.current_pipe].align_tensor)


def display(tensor):
    """Function for displaying the alignment tensor.

    @param tensor:          The alignment tensor identification string.
    @type tensor:           str
    """

    # Test if the current data pipe exists.
    pipes.test(relax_data_store.current_pipe)

    # Test if alignment tensor data exists.
    if not align_data_exists(tensor):
        raise RelaxNoTensorError, 'alignment'

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Header.
    print "Tensor: " + tensor + "\n"

    # The parameter set {Sxx, Syy, Sxy, Sxz, Syz}.
    print "Parameters {Sxx, Syy, Sxy, Sxz, Syz}."
    print "%-15s%15.8f" % ("Sxx:  ", cdp.align_tensor[tensor].Sxx)
    print "%-15s%15.8f" % ("Syy:  ", cdp.align_tensor[tensor].Syy)
    print "%-15s%15.8f" % ("Sxy:  ", cdp.align_tensor[tensor].Sxy)
    print "%-15s%15.8f" % ("Sxz:  ", cdp.align_tensor[tensor].Sxz)
    print "%-15s%15.8f" % ("Syz:  ", cdp.align_tensor[tensor].Syz)

    # The parameter set {Szz, Sxx-yy, Sxy, Sxz, Syz}.
    print "\nParameters {Szz, Sxx-yy, Sxy, Sxz, Syz} (the Pales default format)."
    print "%-15s%15.8f" % ("Szz:  ", cdp.align_tensor[tensor].Szz)
    print "%-15s%15.8f" % ("Sxx-yy:  ", cdp.align_tensor[tensor].Sxxyy)
    print "%-15s%15.8f" % ("Sxy:  ", cdp.align_tensor[tensor].Sxy)
    print "%-15s%15.8f" % ("Sxz:  ", cdp.align_tensor[tensor].Sxz)
    print "%-15s%15.8f" % ("Syz:  ", cdp.align_tensor[tensor].Syz)

    # The parameter set {Axx, Ayy, Axy, Axz, Ayz}.
    print "Parameters {Axx, Ayy, Axy, Axz, Ayz}."
    print "%-15s%15.8f" % ("Axx:  ", cdp.align_tensor[tensor].Axx)
    print "%-15s%15.8f" % ("Ayy:  ", cdp.align_tensor[tensor].Ayy)
    print "%-15s%15.8f" % ("Axy:  ", cdp.align_tensor[tensor].Axy)
    print "%-15s%15.8f" % ("Axz:  ", cdp.align_tensor[tensor].Axz)
    print "%-15s%15.8f" % ("Ayz:  ", cdp.align_tensor[tensor].Ayz)

    # The parameter set {Azz, Axx-yy, Axy, Axz, Ayz}.
    print "\nParameters {Azz, Axx-yy, Axy, Axz, Ayz}."
    print "%-15s%15.8f" % ("Azz:  ", cdp.align_tensor[tensor].Azz)
    print "%-15s%15.8f" % ("Axx-yy:  ", cdp.align_tensor[tensor].Axxyy)
    print "%-15s%15.8f" % ("Axy:  ", cdp.align_tensor[tensor].Axy)
    print "%-15s%15.8f" % ("Axz:  ", cdp.align_tensor[tensor].Axz)
    print "%-15s%15.8f" % ("Ayz:  ", cdp.align_tensor[tensor].Ayz)

    # The parameter set {Pxx, Pyy, Pxy, Pxz, Pyz}.
    print "Parameters {Pxx, Pyy, Pxy, Pxz, Pyz}."
    print "%-15s%15.8f" % ("Pxx:  ", cdp.align_tensor[tensor].Pxx)
    print "%-15s%15.8f" % ("Pyy:  ", cdp.align_tensor[tensor].Pyy)
    print "%-15s%15.8f" % ("Pxy:  ", cdp.align_tensor[tensor].Pxy)
    print "%-15s%15.8f" % ("Pxz:  ", cdp.align_tensor[tensor].Pxz)
    print "%-15s%15.8f" % ("Pyz:  ", cdp.align_tensor[tensor].Pyz)

    # The parameter set {Pzz, Pxx-yy, Pxy, Pxz, Pyz}.
    print "\nParameters {Pzz, Pxx-yy, Pxy, Pxz, Pyz}."
    print "%-15s%15.8f" % ("Pzz:  ", cdp.align_tensor[tensor].Pzz)
    print "%-15s%15.8f" % ("Pxx-yy:  ", cdp.align_tensor[tensor].Pxxyy)
    print "%-15s%15.8f" % ("Pxy:  ", cdp.align_tensor[tensor].Pxy)
    print "%-15s%15.8f" % ("Pxz:  ", cdp.align_tensor[tensor].Pxz)
    print "%-15s%15.8f" % ("Pyz:  ", cdp.align_tensor[tensor].Pyz)



def fold_angles(sim_index=None):
    """Wrap the Euler angles and remove the glide reflection and translational symmetries.

    Wrap the angles such that

        0 <= alpha <= 2pi,
        0 <= beta <= pi,
        0 <= gamma <= 2pi.


    For the simulated values, the angles are wrapped as

        alpha - pi <= alpha_sim <= alpha + pi
        beta - pi/2 <= beta_sim <= beta + pi/2
        gamma - pi <= gamma_sim <= gamma + pi


    @param sim_index:   The simulation index.  If set to None then the actual values will be folded
                        rather than the simulation values.
    @type sim_index:    int or None
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]


    # Wrap the angles.
    ##################

    # Get the current angles.
    alpha = cdp.align_tensor.alpha
    beta  = cdp.align_tensor.beta
    gamma = cdp.align_tensor.gamma

    # Simulated values.
    if sim_index != None:
        alpha_sim = cdp.align_tensor.alpha_sim[sim_index]
        beta_sim  = cdp.align_tensor.beta_sim[sim_index]
        gamma_sim = cdp.align_tensor.gamma_sim[sim_index]

    # Normal value.
    if sim_index == None:
        cdp.align_tensor.alpha = wrap_angles(alpha, 0.0, 2.0*pi)
        cdp.align_tensor.beta  = wrap_angles(beta, 0.0, 2.0*pi)
        cdp.align_tensor.gamma = wrap_angles(gamma, 0.0, 2.0*pi)

    # Simulation values.
    else:
        cdp.align_tensor.alpha_sim[sim_index] = wrap_angles(alpha_sim, alpha - pi, alpha + pi)
        cdp.align_tensor.beta_sim[sim_index]  = wrap_angles(beta_sim, beta - pi, beta + pi)
        cdp.align_tensor.gamma_sim[sim_index] = wrap_angles(gamma_sim, gamma - pi, gamma + pi)


    # Remove the glide reflection and translational symmetries.
    ###########################################################

    # Normal value.
    if sim_index == None:
        # Fold beta inside 0 and pi.
        if cdp.align_tensor.beta >= pi:
            cdp.align_tensor.alpha = pi - cdp.align_tensor.alpha
            cdp.align_tensor.beta = cdp.align_tensor.beta - pi

    # Simulation values.
    else:
        # Fold beta_sim inside beta-pi/2 and beta+pi/2.
        if cdp.align_tensor.beta_sim[sim_index] >= cdp.align_tensor.beta + pi/2.0:
            cdp.align_tensor.alpha_sim[sim_index] = pi - cdp.align_tensor.alpha_sim[sim_index]
            cdp.align_tensor.beta_sim[sim_index] = cdp.align_tensor.beta_sim[sim_index] - pi
        elif cdp.align_tensor.beta_sim[sim_index] <= cdp.align_tensor.beta - pi/2.0:
            cdp.align_tensor.alpha_sim[sim_index] = pi - cdp.align_tensor.alpha_sim[sim_index]
            cdp.align_tensor.beta_sim[sim_index] = cdp.align_tensor.beta_sim[sim_index] + pi


def init(tensor=None, params=None, scale=1.0, angle_units='deg', param_types=0, errors=0):
    """Function for initialising the alignment tensor.

    @param tensor:          The alignment tensor identification string.
    @type tensor:           str
    @param params:          The alignment tensor parameters.
    @type params:           float
    @param scale:           The alignment tensor eigenvalue scaling value.
    @type scale:            float
    @param angle_units:     The units for the angle parameters (either 'deg' or 'rad').
    @type angle_units:      str
    @param param_types:     The type of parameters supplied.  The flag values correspond to, 0:
                            {Axx, Ayy, Axy, Axz, Ayz}, and 1: {Azz, Axx-yy, Axy, Axz, Ayz}.
    @type param_types:      int
    @param errors:          A flag which determines if the alignment tensor data or its errors are
                            being input.
    @type errors:           bin
    """

    # Test if the current data pipe exists.
    pipes.test(relax_data_store.current_pipe)

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if alignment tensor data already exists.
    if align_data_exists(tensor):
        raise RelaxTensorError, 'alignment'

    # Check the validity of the angle_units argument.
    valid_types = ['deg', 'rad']
    if not angle_units in valid_types:
        raise RelaxError, "The alignment tensor 'angle_units' argument " + `angle_units` + " should be either 'deg' or 'rad'."

    # Add the align_tensor object to the data pipe.
    if not hasattr(cdp, 'align_tensor'):
        cdp.align_tensor = AlignTensorList()
    cdp.align_tensor.add_item(tensor)

    # {Sxx, Syy, Sxy, Sxz, Syz}.
    if param_types == 0:
        # Unpack the tuple.
        Sxx, Syy, Sxy, Sxz, Syz = params

        # Scaling.
        Sxx = Sxx * scale
        Syy = Syy * scale
        Sxy = Sxy * scale
        Sxz = Sxz * scale
        Syz = Syz * scale

        # Set the parameters.
        set(tensor=cdp.align_tensor[-1], value=[Sxx, Syy, Sxy, Sxz, Syz], param=['Sxx', 'Syy', 'Sxy', 'Sxz', 'Syz'])

    # {Szz, Sxx-yy, Sxy, Sxz, Syz}.
    elif param_types == 1:
        # Unpack the tuple.
        Szz, Sxxyy, Sxy, Sxz, Syz = params

        # Scaling.
        Szz = Szz * scale
        Sxxyy = Sxxyy * scale
        Sxy = Sxy * scale
        Sxz = Sxz * scale
        Syz = Syz * scale

        # Set the parameters.
        set(tensor=cdp.align_tensor[-1], value=[Szz, Sxxyy, Sxy, Sxz, Syz], param=['Szz', 'Sxxyy', 'Sxy', 'Sxz', 'Syz'])

    # {Axx, Ayy, Axy, Axz, Ayz}.
    elif param_types == 2:
        # Unpack the tuple.
        Axx, Ayy, Axy, Axz, Ayz = params

        # Scaling.
        Axx = Axx * scale
        Ayy = Ayy * scale
        Axy = Axy * scale
        Axz = Axz * scale
        Ayz = Ayz * scale

        # Set the parameters.
        set(tensor=cdp.align_tensor[-1], value=[Axx, Ayy, Axy, Axz, Ayz], param=['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'])

    # {Azz, Axx-yy, Axy, Axz, Ayz}.
    elif param_types == 3:
        # Unpack the tuple.
        Azz, Axxyy, Axy, Axz, Ayz = params

        # Scaling.
        Azz = Azz * scale
        Axxyy = Axxyy * scale
        Axy = Axy * scale
        Axz = Axz * scale
        Ayz = Ayz * scale

        # Set the parameters.
        set(tensor=cdp.align_tensor[-1], value=[Azz, Axxyy, Axy, Axz, Ayz], param=['Azz', 'Axxyy', 'Axy', 'Axz', 'Ayz'])

    # {Axx, Ayy, Axy, Axz, Ayz}.
    elif param_types == 4:
        # Unpack the tuple.
        Axx, Ayy, Axy, Axz, Ayz = params

        # Get the bond length.
        r = None
        for spin in spin_loop():
            # First spin.
            if r == None:
                r = spin.r

            # Different value.
            if r != spin.r:
                raise RelaxError, "Not all spins have the same bond length."

        # Scaling.
        scale = scale / kappa() * r**3
        Axx = Axx * scale
        Ayy = Ayy * scale
        Axy = Axy * scale
        Axz = Axz * scale
        Ayz = Ayz * scale

        # Set the parameters.
        set(tensor=cdp.align_tensor[-1], value=[Axx, Ayy, Axy, Axz, Ayz], param=['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'])

    # {Azz, Axx-yy, Axy, Axz, Ayz}.
    elif param_types == 5:
        # Unpack the tuple.
        Azz, Axxyy, Axy, Axz, Ayz = params

        # Get the bond length.
        r = None
        for spin in spin_loop():
            # First spin.
            if r == None:
                r = spin.r

            # Different value.
            if r != spin.r:
                raise RelaxError, "Not all spins have the same bond length."

        # Scaling.
        scale = scale / kappa() * r**3
        Azz = Azz * scale
        Axxyy = Axxyy * scale
        Axy = Axy * scale
        Axz = Axz * scale
        Ayz = Ayz * scale

        # Set the parameters.
        set(tensor=cdp.align_tensor[-1], value=[Azz, Axxyy, Axy, Axz, Ayz], param=['Azz', 'Axxyy', 'Axy', 'Axz', 'Ayz'])

    # {Pxx, Pyy, Pxy, Pxz, Pyz}.
    elif param_types == 6:
        # Unpack the tuple.
        Pxx, Pyy, Pxy, Pxz, Pyz = params

        # Scaling.
        Pxx = Pxx * scale
        Pyy = Pyy * scale
        Pxy = Pxy * scale
        Pxz = Pxz * scale
        Pyz = Pyz * scale

        # Set the parameters.
        set(tensor=cdp.align_tensor[-1], value=[Pxx, Pyy, Pxy, Pxz, Pyz], param=['Pxx', 'Pyy', 'Pxy', 'Pxz', 'Pyz'])

    # {Pzz, Pxx-yy, Pxy, Pxz, Pyz}.
    elif param_types == 7:
        # Unpack the tuple.
        Pzz, Pxxyy, Pxy, Pxz, Pyz = params

        # Scaling.
        Pzz = Pzz * scale
        Pxxyy = Pxxyy * scale
        Pxy = Pxy * scale
        Pxz = Pxz * scale
        Pyz = Pyz * scale

        # Set the parameters.
        set(tensor=cdp.align_tensor[-1], value=[Pzz, Pxxyy, Pxy, Pxz, Pyz], param=['Pzz', 'Pxxyy', 'Pxy', 'Pxz', 'Pyz'])

    # Unknown parameter combination.
    else:
        raise RelaxUnknownParamCombError, ('param_types', param_types)


def map_bounds(param):
    """The function for creating bounds for the mapping function."""

    # {Axx, Ayy, Azz, Axxyy, Axy, Axz, Ayz}.
    if param in ['Axx', 'Ayy', 'Azz', 'Axxyy', 'Axy', 'Axz', 'Ayz']:
        return [-50, 50]

    # alpha.
    elif param == 'alpha':
        return [0, 2*pi]

    # beta.
    elif param == 'beta':
        return [0, pi]

    # gamma.
    elif param == 'gamma':
        return [0, 2*pi]


def kappa(nuc1='N', nuc2='H'):
    """Function for calculating the kappa constant.

    The kappa constant is

        kappa = -3/(8pi^2).gI.gS.mu0.h_bar,

    where gI and gS are the gyromagnetic ratios of the I and S spins, mu0 is the permeability of
    free space, and h_bar is Planck's constant divided by 2pi.

    @param nuc1:    The first nucleus type.
    @type nuc1:     str
    @param nuc2:    The first nucleus type.
    @type nuc2:     str
    @return:        The kappa constant value.
    @return type:   float
    """

    # Gyromagnetic ratio of the first nucleus.
    if nuc1 == 'C':
        gI = g13C
    elif nuc1 == 'H':
        gI = g1H
    elif nuc1 == 'N':
        gI = g15N
    elif nuc1 == 'O':
        gI = g17O
    elif nuc1 == 'P':
        gI = g31P

    # Gyromagnetic ratio of the second nucleus.
    if nuc2 == 'C':
        gS = g13C
    elif nuc2 == 'H':
        gS = g1H
    elif nuc2 == 'N':
        gS = g15N
    elif nuc2 == 'O':
        gS = g17O
    elif nuc2 == 'P':
        gS = g31P

    # Kappa.
    return -3.0/(8.0*pi**2) * gI * gS * mu0 * h_bar


def map_labels(index, params, bounds, swap, inc):
    """Function for creating labels, tick locations, and tick values for an OpenDX map.

    @param index:   The index (which isn't used here?!?).
    @type index:    int
    @param params:  The list of parameter names.
    @type params:   list of str
    @param bounds:  The bounds of the map.
    @type params:   list of lists (of a float and bin)
    @param swap:    An array for switching axes around.
    @type swap:     list of int
    @param inc:     The number of increments of one dimension in the map.
    @type inc:      list of int
    """

    # Initialise.
    labels = "{"
    tick_locations = []
    tick_values = []
    n = len(params)
    axis_incs = 5
    loc_inc = inc / axis_incs

    # Increment over the model parameters.
    for i in xrange(n):
        # Parameter conversion factors.
        factor = return_conversion_factor(params[swap[i]])

        # Parameter units.
        units = return_units(params[swap[i]])

        # Labels.
        if units:
            labels = labels + "\"" + params[swap[i]] + " (" + units + ")\""
        else:
            labels = labels + "\"" + params[swap[i]] + "\""

        # Tick values.
        vals = bounds[swap[i], 0] / factor
        val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / (axis_incs * factor)

        if i < n - 1:
            labels = labels + " "
        else:
            labels = labels + "}"

        # Tick locations.
        string = "{"
        val = 0.0
        for j in xrange(axis_incs + 1):
            string = string + " " + `val`
            val = val + loc_inc
        string = string + " }"
        tick_locations.append(string)

        # Tick values.
        string = "{"
        for j in xrange(axis_incs + 1):
            string = string + "\"" + "%.2f" % vals + "\" "
            vals = vals + val_inc
        string = string + "}"
        tick_values.append(string)

    return labels, tick_locations, tick_values


def matrix_angles(basis_set=0):
    """Function for calculating the 5D angles between the alignment tensors.

    The basis set used for the 5D vector construction changes the angles calculated.

    @param basis_set:   The basis set to use for constructing the 5D vectors.  If set to 0, the
                        basis set is {Sxx, Syy, Sxy, Sxz, Syz}.  If 1, then the basis set is {Szz,
                        Sxxyy, Sxy, Sxz, Syz}.
    @type basis_set:    int
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test that alignment tensor data exists.
    if not hasattr(cdp, 'align_tensor') or len(cdp.align_tensor) == 0:
        raise RelaxNoTensorError, 'alignment'

    # The number of tensors.
    tensor_num = len(cdp.align_tensor)

    # Create the matrix which contains the 5D vectors.
    matrix = zeros((tensor_num, 5), float64)

    # Loop over the tensors.
    i = 0
    for key in cdp.align_tensor.keys():
        # Unitary basis set.
        if basis_set == 0:
            # Pack the elements.
            matrix[i,0] = cdp.align_tensor[key].Sxx
            matrix[i,1] = cdp.align_tensor[key].Syy
            matrix[i,2] = cdp.align_tensor[key].Sxy
            matrix[i,3] = cdp.align_tensor[key].Sxz
            matrix[i,4] = cdp.align_tensor[key].Syz

        # Geometric basis set.
        elif basis_set == 1:
            # Pack the elements.
            matrix[i,0] = cdp.align_tensor[key].Szz
            matrix[i,1] = cdp.align_tensor[key].Sxxyy
            matrix[i,2] = cdp.align_tensor[key].Sxy
            matrix[i,3] = cdp.align_tensor[key].Sxz
            matrix[i,4] = cdp.align_tensor[key].Syz

        # Normalisation.
        norm = linalg.norm(matrix[i])
        matrix[i] = matrix[i] / norm

        # Increment the index.
        i = i + 1

    # Initialise the matrix of angles.
    cdp.align_tensor.angles = zeros((tensor_num, tensor_num), float64)

    # Header print out.
    sys.stdout.write("\nData pipe: " + `relax_data_store.current_pipe` + "\n")
    sys.stdout.write("\n5D angles in deg between the vectors ")
    if basis_set == 0:
        sys.stdout.write("{Sxx, Syy, Sxy, Sxz, Syz}")
    elif basis_set == 1:
        sys.stdout.write("{Szz, Sxx-yy, Sxy, Sxz, Syz}")
    sys.stdout.write(":\n")
    sys.stdout.write("%8s" % '')
    for i in xrange(tensor_num):
        sys.stdout.write("%8i" % i)
    sys.stdout.write("\n")

    # First loop.
    for i in xrange(tensor_num):
        # Print out.
        sys.stdout.write("%8i" % i)

        # Second loop.
        for j in xrange(tensor_num):
            # Skip the diagonal and arccos problems.
            if i != j:
                # The angle (in rad).
                cdp.align_tensor.angles[i, j] = arccos(dot(matrix[i], matrix[j]))

            # Print out the angles in degrees.
            sys.stdout.write("%8.1f" % (cdp.align_tensor.angles[i, j]*180.0/pi))

        # Print out.
        sys.stdout.write("\n")


def return_conversion_factor(param):
    """Function for returning the factor of conversion between different parameter units.

    @param param:   The parameter name.
    @type param:    str
    @return:        The conversion factor.
    @type return:   float
    """

    # Get the object name.
    object_name = return_data_name(param)

    # {Axx, Ayy, Azz, Axxyy, Axy, Axz, Ayz}.
    if object_name in ['Axx', 'Ayy', 'Azz', 'Axxyy', 'Axy', 'Axz', 'Ayz']:
        return 1.0

    # Angles.
    elif object_name in ['alpha', 'beta', 'gamma']:
        return (2.0*pi) / 360.0

    # No conversion factor.
    else:
        return 1.0


def return_data_name(name):
    """
    Alignment tensor parameter string matching patterns
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ____________________________________________________________________________________________
    |                                                        |              |                  |
    | Data type                                              | Object name  | Patterns         |
    |________________________________________________________|______________|__________________|
    |                                                        |              |                  |
    | The xx component of the Saupe order matrix - Sxx       | 'Sxx'        | '^[Sa]xx$'       |
    |                                                        |              |                  |
    | The yy component of the Saupe order matrix - Syy       | 'Syy'        | '^[Sa]yy$'       |
    |                                                        |              |                  |
    | The zz component of the Saupe order matrix - Szz       | 'Szz'        | '^[Sa]zz$'       |
    |                                                        |              |                  |
    | The xy component of the Saupe order matrix - Sxy       | 'Sxy'        | '^[Sa]xy$'       |
    |                                                        |              |                  |
    | The xz component of the Saupe order matrix - Sxz       | 'Sxz'        | '^[Sa]xz$'       |
    |                                                        |              |                  |
    | The yz component of the Saupe order matrix - Syz       | 'Syz'        | '^[Sa]yz$'       |
    |                                                        |              |                  |
    | The xx-yy component of the Saupe order matrix - Sxx-yy | 'Sxxyy'      | '^[Sa]xxyy$'     |
    |                                                        |              |                  |
    | The xx component of the alignment tensor - Axx         | 'Axx'        | '^[Aa]xx$'       |
    |                                                        |              |                  |
    | The yy component of the alignment tensor - Ayy         | 'Ayy'        | '^[Aa]yy$'       |
    |                                                        |              |                  |
    | The zz component of the alignment tensor - Azz         | 'Azz'        | '^[Aa]zz$'       |
    |                                                        |              |                  |
    | The xy component of the alignment tensor - Axy         | 'Axy'        | '^[Aa]xy$'       |
    |                                                        |              |                  |
    | The xz component of the alignment tensor - Axz         | 'Axz'        | '^[Aa]xz$'       |
    |                                                        |              |                  |
    | The yz component of the alignment tensor - Ayz         | 'Ayz'        | '^[Aa]yz$'       |
    |                                                        |              |                  |
    | The xx-yy component of the alignment tensor - Axx-yy   | 'Axxyy'      | '^[Aa]xxyy$'     |
    |                                                        |              |                  |
    | The xx component of the probability matrix - Pxx       | 'Pxx'        | '^[Pa]xx$'       |
    |                                                        |              |                  |
    | The yy component of the probability matrix - Pyy       | 'Pyy'        | '^[Pa]yy$'       |
    |                                                        |              |                  |
    | The zz component of the probability matrix - Pzz       | 'Pzz'        | '^[Pa]zz$'       |
    |                                                        |              |                  |
    | The xy component of the probability matrix - Pxy       | 'Pxy'        | '^[Pa]xy$'       |
    |                                                        |              |                  |
    | The xz component of the probability matrix - Pxz       | 'Pxz'        | '^[Pa]xz$'       |
    |                                                        |              |                  |
    | The yz component of the probability matrix - Pyz       | 'Pyz'        | '^[Pa]yz$'       |
    |                                                        |              |                  |
    | The xx-yy component of the probability matrix - Pxx-yy | 'Pxxyy'      | '^[Pa]xxyy$'     |
    |                                                        |              |                  |
    | The first Euler angle of the alignment tensor - alpha  | 'alpha'      | '^a$' or 'alpha' |
    |                                                        |              |                  |
    | The second Euler angle of the alignment tensor - beta  | 'beta'       | '^b$' or 'beta'  |
    |                                                        |              |                  |
    | The third Euler angle of the alignment tensor - gamma  | 'gamma'      | '^g$' or 'gamma' |
    |________________________________________________________|______________|__________________|
    """

    # Enforce that the name must be a string.
    if type(name) != str:
        raise RelaxStrError, ('name', name)

    # Sxx.
    if search('^[Ss]xx$', name):
        return 'Sxx'

    # Syy.
    if search('^[Ss]yy$', name):
        return 'Syy'

    # Szz.
    if search('^[Ss]zz$', name):
        return 'Szz'

    # Sxy.
    if search('^[Ss]xy$', name):
        return 'Sxy'

    # Sxz.
    if search('^[Ss]xz$', name):
        return 'Sxz'

    # Syz.
    if search('^[Ss]yz$', name):
        return 'Syz'

    # Sxx-yy.
    if search('^[Ss]xxyy$', name):
        return 'Sxxyy'

    # Axx.
    if search('^[Aa]xx$', name):
        return 'Axx'

    # Ayy.
    if search('^[Aa]yy$', name):
        return 'Ayy'

    # Azz.
    if search('^[Aa]zz$', name):
        return 'Azz'

    # Axy.
    if search('^[Aa]xy$', name):
        return 'Axy'

    # Axz.
    if search('^[Aa]xz$', name):
        return 'Axz'

    # Ayz.
    if search('^[Aa]yz$', name):
        return 'Ayz'

    # Axx-yy.
    if search('^[Aa]xxyy$', name):
        return 'Axxyy'

    # Pxx.
    if search('^[Pp]xx$', name):
        return 'Pxx'

    # Pyy.
    if search('^[Pp]yy$', name):
        return 'Pyy'

    # Pzz.
    if search('^[Pp]zz$', name):
        return 'Pzz'

    # Pxy.
    if search('^[Pp]xy$', name):
        return 'Pxy'

    # Pxz.
    if search('^[Pp]xz$', name):
        return 'Pxz'

    # Pyz.
    if search('^[Pp]yz$', name):
        return 'Pyz'

    # Pxx-yy.
    if search('^[Pp]xxyy$', name):
        return 'Pxxyy'

    # alpha.
    if search('^a$', name) or search('alpha', name):
        return 'alpha'

    # beta.
    if search('^b$', name) or search('beta', name):
        return 'beta'

    # gamma.
    if search('^g$', name) or search('gamma', name):
        return 'gamma'

    # No parameter?
    raise RelaxUnknownParamError, name


def return_units(param):
    """Function for returning a string representing the parameters units.

    @param param:   The parameter name.
    @type param:    str
    @return:        The string representation of the units.
    @type return:   str
    """

    # Get the object name.
    object_name = return_data_name(param)

    # {Axx, Ayy, Azz, Axxyy, Axy, Axz, Ayz}.
    if object_name in ['Axx', 'Ayy', 'Azz', 'Axxyy', 'Axy', 'Axz', 'Ayz']:
        return 'Hz'

    # Angles.
    elif object_name in ['alpha', 'beta', 'gamma']:
        return 'deg'


def set(tensor=None, value=None, param=None):
    """
    Alignment tensor set details
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    If the alignment tensor has not been setup, use the more powerful function
    'alignment_tensor.init' to initialise the tensor parameters.

    The alignment tensor parameters can only be set when the data pipe corresponds to model-free
    analysis.  The units of the parameters are:

        Unitless for Sxx, Syy, Szz, Sxxyy, Sxy, Sxz, Syz.
        Unitless for Axx, Ayy, Azz, Axxyy, Axy, Axz, Ayz.
        Unitless for Pxx, Pyy, Pzz, Pxxyy, Pxy, Pxz, Pyz.
        Radians for all angles (alpha, beta, gamma).

    If a single geometric parameter is supplied, it must be one of Bxx, Byy, Bxy, Bxz, Byz, where B
    is one of S, A, or P.  For the parameters Bzz and Bxxyy, it is not possible to determine how to
    use the currently set values together with the supplied value to calculate the new internal
    parameters.  When supplying multiple geometric parameters, the set must belong to one of

        {Sxx, Syy, Sxy, Sxz, Syz},
        {Szz, Sxxyy, Sxy, Sxz, Syz}.
        {Axx, Ayy, Axy, Axz, Ayz},
        {Azz, Axxyy, Axy, Axz, Ayz}.
        {Pxx, Pyy, Pxy, Pxz, Pyz},
        {Pzz, Pxxyy, Pxy, Pxz, Pyz}.
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Initialise.
    geo_params = []
    geo_values = []
    orient_params = []
    orient_values = []

    # Loop over the parameters.
    for i in xrange(len(param)):
        # Get the object name.
        param[i] = return_data_name(param[i])

        # Unknown parameter.
        if param[i] == None:
            raise RelaxUnknownParamError, ("alignment tensor", 'None')

        # Default value.
        if value[i] == None:
            value[i] = default_value(object_names[i])

        # Geometric parameter.
        if param[i] in ['Sxx', 'Syy', 'Szz', 'Sxxyy', 'Sxy', 'Sxz', 'Syz', 'Axx', 'Ayy', 'Azz', 'Axxyy', 'Axy', 'Axz', 'Ayz', 'Pxx', 'Pyy', 'Pzz', 'Pxxyy', 'Pxy', 'Pxz', 'Pyz']:
            geo_params.append(param[i])
            geo_values.append(value[i])

        # Orientational parameter.
        if param[i] in ['alpha', 'beta', 'gamma']:
            orient_params.append(param[i])
            orient_values.append(value[i])


    # Geometric parameters.
    #######################

    # A single geometric parameter.
    if len(geo_params) == 1:
        # Saupe order matrix.
        #####################

        # The single parameter Sxx.
        if geo_params[0] == 'Sxx':
            tensor.Sxx = geo_values[0]

        # The single parameter Syy.
        elif geo_params[0] == 'Syy':
            tensor.Syy = geo_values[0]

        # The single parameter Sxy.
        elif geo_params[0] == 'Sxy':
            tensor.Sxy = geo_values[0]

        # The single parameter Sxz.
        elif geo_params[0] == 'Sxz':
            tensor.Sxz = geo_values[0]

        # The single parameter Syz.
        elif geo_params[0] == 'Syz':
            tensor.Syz = geo_values[0]


        # Alignment tensor.
        ###################

        # The single parameter Axx.
        elif geo_params[0] == 'Axx':
            tensor.Sxx = 3.0/2.0 * geo_values[0]

        # The single parameter Ayy.
        elif geo_params[0] == 'Ayy':
            tensor.Syy = 3.0/2.0 * geo_values[0]

        # The single parameter Axy.
        elif geo_params[0] == 'Axy':
            tensor.Sxy = 3.0/2.0 * geo_values[0]

        # The single parameter Axz.
        elif geo_params[0] == 'Axz':
            tensor.Sxz = 3.0/2.0 * geo_values[0]

        # The single parameter Ayz.
        elif geo_params[0] == 'Ayz':
            tensor.Syz = 3.0/2.0 * geo_values[0]


        # Probability tensor.
        #####################

        # The single parameter Pxx.
        elif geo_params[0] == 'Pxx':
            tensor.Sxx = 3.0/2.0 * (geo_values[0] - 1.0/3.0)

        # The single parameter Pyy.
        elif geo_params[0] == 'Pyy':
            tensor.Syy = 3.0/2.0 * (geo_values[0] - 1.0/3.0)

        # The single parameter Pxy.
        elif geo_params[0] == 'Pxy':
            tensor.Sxy = 3.0/2.0 * geo_values[0]

        # The single parameter Pxz.
        elif geo_params[0] == 'Pxz':
            tensor.Sxz = 3.0/2.0 * geo_values[0]

        # The single parameter Pyz.
        elif geo_params[0] == 'Pyz':
            tensor.Syz = 3.0/2.0 * geo_values[0]

        # Cannot set the single parameter.
        else:
            raise RelaxError, "The geometric alignment parameter " + `geo_params[0]` + " cannot be set."

    # 5 geometric parameters.
    elif len(geo_params) == 5:
        # The geometric parameter set {Sxx, Syy, Sxy, Sxz, Syz}.
        if geo_params.count('Sxx') == 1 and geo_params.count('Syy') == 1 and geo_params.count('Sxy') == 1 and geo_params.count('Sxz') == 1 and geo_params.count('Syz') == 1:
            # The parameters.
            Sxx = geo_values[geo_params.index('Sxx')]
            Syy = geo_values[geo_params.index('Syy')]
            Sxy = geo_values[geo_params.index('Sxy')]
            Sxz = geo_values[geo_params.index('Sxz')]
            Syz = geo_values[geo_params.index('Syz')]

            # Set the internal parameter values.
            tensor.Sxx = Sxx
            tensor.Syy = Syy
            tensor.Sxy = Sxy
            tensor.Sxz = Sxz
            tensor.Syz = Syz

        # The geometric parameter set {Szz, Sxxyy, Sxy, Sxz, Syz}.
        elif geo_params.count('Szz') == 1 and geo_params.count('Sxxyy') == 1 and geo_params.count('Sxy') == 1 and geo_params.count('Sxz') == 1 and geo_params.count('Syz') == 1:
            # The parameters.
            Szz = geo_values[geo_params.index('Szz')]
            Sxxyy = geo_values[geo_params.index('Sxxyy')]
            Sxy = geo_values[geo_params.index('Sxy')]
            Sxz = geo_values[geo_params.index('Sxz')]
            Syz = geo_values[geo_params.index('Syz')]

            # Set the internal parameter values.
            tensor.Sxx = -0.5*(Szz-Sxxyy)
            tensor.Syy = -0.5*(Szz+Sxxyy)
            tensor.Sxy = Sxy
            tensor.Sxz = Sxz
            tensor.Syz = Syz

        # The geometric parameter set {Axx, Ayy, Axy, Axz, Ayz}.
        elif geo_params.count('Axx') == 1 and geo_params.count('Ayy') == 1 and geo_params.count('Axy') == 1 and geo_params.count('Axz') == 1 and geo_params.count('Ayz') == 1:
            # The parameters.
            Axx = geo_values[geo_params.index('Axx')]
            Ayy = geo_values[geo_params.index('Ayy')]
            Axy = geo_values[geo_params.index('Axy')]
            Axz = geo_values[geo_params.index('Axz')]
            Ayz = geo_values[geo_params.index('Ayz')]

            # Set the internal parameter values.
            tensor.Sxx = 3.0/2.0 * Axx
            tensor.Syy = 3.0/2.0 * Ayy
            tensor.Sxy = 3.0/2.0 * Axy
            tensor.Sxz = 3.0/2.0 * Axz
            tensor.Syz = 3.0/2.0 * Ayz

        # The geometric parameter set {Azz, Axxyy, Axy, Axz, Ayz}.
        elif geo_params.count('Azz') == 1 and geo_params.count('Axxyy') == 1 and geo_params.count('Axy') == 1 and geo_params.count('Axz') == 1 and geo_params.count('Ayz') == 1:
            # The parameters.
            Azz = geo_values[geo_params.index('Azz')]
            Axxyy = geo_values[geo_params.index('Axxyy')]
            Axy = geo_values[geo_params.index('Axy')]
            Axz = geo_values[geo_params.index('Axz')]
            Ayz = geo_values[geo_params.index('Ayz')]

            # Set the internal parameter values.
            tensor.Sxx = 3.0/2.0 * -0.5*(Azz-Axxyy)
            tensor.Syy = 3.0/2.0 * -0.5*(Azz+Axxyy)
            tensor.Sxy = 3.0/2.0 * Axy
            tensor.Sxz = 3.0/2.0 * Axz
            tensor.Syz = 3.0/2.0 * Ayz

        # The geometric parameter set {Pxx, Pyy, Pxy, Pxz, Pyz}.
        elif geo_params.count('Pxx') == 1 and geo_params.count('Pyy') == 1 and geo_params.count('Pxy') == 1 and geo_params.count('Pxz') == 1 and geo_params.count('Pyz') == 1:
            # The parameters.
            Pxx = geo_values[geo_params.index('Pxx')]
            Pyy = geo_values[geo_params.index('Pyy')]
            Pxy = geo_values[geo_params.index('Pxy')]
            Pxz = geo_values[geo_params.index('Pxz')]
            Pyz = geo_values[geo_params.index('Pyz')]

            # Set the internal parameter values.
            tensor.Sxx = 3.0/2.0 * (Pxx - 1.0/3.0)
            tensor.Syy = 3.0/2.0 * (Pyy - 1.0/3.0)
            tensor.Sxy = 3.0/2.0 * Pxy
            tensor.Sxz = 3.0/2.0 * Pxz
            tensor.Syz = 3.0/2.0 * Pyz

        # The geometric parameter set {Pzz, Pxxyy, Pxy, Pxz, Pyz}.
        elif geo_params.count('Pzz') == 1 and geo_params.count('Pxxyy') == 1 and geo_params.count('Pxy') == 1 and geo_params.count('Pxz') == 1 and geo_params.count('Pyz') == 1:
            # The parameters.
            Pzz = geo_values[geo_params.index('Pzz')]
            Pxxyy = geo_values[geo_params.index('Pxxyy')]
            Pxy = geo_values[geo_params.index('Pxy')]
            Pxz = geo_values[geo_params.index('Pxz')]
            Pyz = geo_values[geo_params.index('Pyz')]

            # Set the internal parameter values.
            tensor.Sxx = 3.0/2.0 * (-0.5*(Pzz-Pxxyy) - 1.0/3.0)
            tensor.Syy = 3.0/2.0 * (-0.5*(Pzz+Pxxyy) - 1.0/3.0)
            tensor.Sxy = 3.0/2.0 * Pxy
            tensor.Sxz = 3.0/2.0 * Pxz
            tensor.Syz = 3.0/2.0 * Pyz

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)


    # Unknown geometric parameters.
    else:
        raise RelaxUnknownParamCombError, ('geometric parameter set', geo_params)


    # Orientational parameters.
    ###########################

    # A single orientational parameter.
    if len(orient_params) == 1:
        # The single parameter alpha.
        if orient_params[0] == 'alpha':
            tensor.alpha = orient_values[orient_params.index('alpha')]

        # The single parameter beta.
        elif orient_params[0] == 'beta':
            tensor.beta = orient_values[orient_params.index('beta')]

        # The single parameter gamma.
        elif orient_params[0] == 'gamma':
            tensor.gamma = orient_values[orient_params.index('gamma')]

    # Two orientational parameters.
    elif len(orient_params) == 2:
        # The orientational parameter set {alpha, beta}.
        if orient_params.count('alpha') == 1 and orient_params.count('beta') == 1:
            tensor.alpha = orient_values[orient_params.index('alpha')]
            tensor.beta = orient_values[orient_params.index('beta')]

        # The orientational parameter set {alpha, gamma}.
        if orient_params.count('alpha') == 1 and orient_params.count('gamma') == 1:
            tensor.alpha = orient_values[orient_params.index('alpha')]
            tensor.gamma = orient_values[orient_params.index('gamma')]

        # The orientational parameter set {beta, gamma}.
        if orient_params.count('beta') == 1 and orient_params.count('gamma') == 1:
            tensor.beta = orient_values[orient_params.index('beta')]
            tensor.gamma = orient_values[orient_params.index('gamma')]

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)

    # Three orientational parameters.
    elif len(orient_params) == 3:
        # The orientational parameter set {alpha, beta, gamma}.
        if orient_params.count('alpha') == 1 and orient_params.count('beta') == 1:
            tensor.alpha = orient_values[orient_params.index('alpha')]
            tensor.beta = orient_values[orient_params.index('beta')]
            tensor.gamma = orient_values[orient_params.index('gamma')]

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)

    # More than three orientational parameters.
    elif len(orient_params) > 3:
        raise RelaxUnknownParamCombError, ('orientational parameter set', orient_params)


    # Fold the angles in.
    #####################

    if orient_params:
        fold_angles()


def svd(basis_set=0):
    """Function for calculating the singular values of all the loaded tensors.

    The matrix on which SVD will be performed is:

        | Sxx1 Syy1 Sxy1 Sxz1 Syz1 |
        | Sxx2 Syy2 Sxy2 Sxz2 Syz2 |
        | Sxx3 Syy3 Sxy3 Sxz3 Syz3 |
        |  .    .    .    .    .   |
        |  .    .    .    .    .   |
        |  .    .    .    .    .   |
        | SxxN SyyN SxyN SxzN SyzN |

    This is the default unitary basis set (selected when basis_set is 0).  Alternatively a geometric
    basis set consisting of the stretching and skewing parameters Szz and Sxx-yy respectively
    replacing Sxx and Syy can be chosen by setting basis_set to 1.  The matrix in this case is:

        | Szz1 Sxxyy1 Sxy1 Sxz1 Syz1 |
        | Szz2 Sxxyy2 Sxy2 Sxz2 Syz2 |
        | Szz3 Sxxyy3 Sxy3 Sxz3 Syz3 |
        |  .     .     .    .    .   |
        |  .     .     .    .    .   |
        |  .     .     .    .    .   |
        | SzzN SxxyyN SxyN SxzN SyzN |

    The relationships between the geometric and unitary basis sets are:

        Szz = - Sxx - Syy,
        Sxxyy = Sxx - Syy,

    The SVD values and condition number are dependendent upon the basis set chosen.
    """

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test that alignment tensor data exists.
    if not hasattr(cdp, 'align_tensor') or len(cdp.align_tensor) == 0:
        raise RelaxNoTensorError, 'alignment'

    # Create the matrix to apply SVD on.
    matrix = zeros((len(cdp.align_tensor), 5), float64)

    # Pack the elements.
    i = 0
    for key in cdp.align_tensor.keys():
        # Unitary basis set.
        if basis_set == 0:
            matrix[i,0] = cdp.align_tensor[key].Sxx
            matrix[i,1] = cdp.align_tensor[key].Syy
            matrix[i,2] = cdp.align_tensor[key].Sxy
            matrix[i,3] = cdp.align_tensor[key].Sxz
            matrix[i,4] = cdp.align_tensor[key].Syz

        # Geometric basis set.
        elif basis_set == 1:
            matrix[i,0] = cdp.align_tensor[key].Szz
            matrix[i,1] = cdp.align_tensor[key].Sxxyy
            matrix[i,2] = cdp.align_tensor[key].Sxy
            matrix[i,3] = cdp.align_tensor[key].Sxz
            matrix[i,4] = cdp.align_tensor[key].Syz

        # Increment the index.
        i = i + 1

    # SVD.
    u, s, vh = linalg.svd(matrix)

    # Store the singular values.
    cdp.align_tensor.singular_vals = s

    # Calculate and store the condition number.
    cdp.align_tensor.cond_num = s[0] / s[-1]

    # Print out.
    print "\nData pipe: " + `relax_data_store.current_pipe`
    print "\nSingular values:"
    for val in s:
        print "\t" + `val`
    print "\nCondition number: " + `cdp.align_tensor.cond_num`
