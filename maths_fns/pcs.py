###############################################################################
#                                                                             #
# Copyright (C) 2008, 2010 Edward d'Auvergne                                  #
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

# Module docstring.
"""Module for the calculation of pseudocontact shifts."""

# Python imports.
from numpy import dot, sum


def ave_pcs_tensor(dj, vect, N, A, weights=None):
    """Calculate the ensemble average PCS, using the 3D tensor.

    This function calculates the average PCS for a set of XH bond vectors from a structural ensemble, using the 3D tensorial form of the alignment tensor.  The formula for this ensemble average PCS value is::

                             _N_
                             \                   T
        <delta_ij(theta)>  =  >  pc . djc . mu_jc . Ai . mu_jc,
                             /__
                             c=1

    where:
        - i is the alignment tensor index,
        - j is the index over spins,
        - c is the index over the states or multiple structures,
        - N is the total number of states or structures,
        - theta is the parameter vector,
        - djc is the PCS constant for spin j and state c,
        - pc is the population probability or weight associated with state c (equally weighted to 1/N if weights are not provided),
        - mu_jc is the unit vector corresponding to spin j and state c,
        - Ai is the alignment tensor.

    The PCS constant is defined as::

             mu0 15kT   1
        dj = --- ----- ---- ,
             4pi Bo**2 r**3

    where:
        - mu0 is the permeability of free space,
        - k is Boltzmann's constant,
        - T is the absolute temperature,
        - Bo is the magnetic field strength,
        - r is the distance between the paramagnetic centre (electron spin) and the nuclear spin.


    @param dj:          The PCS constants for each structure c for spin j.  This should be an array with indices corresponding to c.
    @type dj:           numpy rank-1 array
    @param vect:        The electron-nuclear unit vector matrix.  The first dimension corresponds to the structural index, the second dimension is the coordinates of the unit vector.  The vectors should be parallel to the vector connecting the paramagnetic centre to the nuclear spin.
    @type vect:         numpy matrix
    @param N:           The total number of structures.
    @type N:            int
    @param A:           The alignment tensor.
    @type A:            numpy rank-2 3D tensor
    @param weights:     The weights for each member of the ensemble (the last member need not be supplied).
    @type weights:      numpy rank-1 array
    @return:            The average PCS value.
    @rtype:             float
    """

    # Initial back-calculated PCS value.
    val = 0.0

    # No weights given.
    if weights == None:
        pc = 1.0 / N
        weights = [pc] * N

    # Missing last weight.
    if len(weights) < N:
        pN = 1.0 - sum(weights, axis=0)
        weights = weights.tolist()
        weights.append(pN)

    # Back-calculate the PCS.
    for c in xrange(N):
        val = val + weights[c] * dj[c] * dot(vect[c], dot(A, vect[c]))

    # Return the average PCS.
    return val


def ave_pcs_tensor_ddeltaij_dAmn(dj, vect, N, dAi_dAmn, weights=None):
    """Calculate the ensemble average PCS gradient element for Amn, using the 3D tensor.

    This function calculates the average PCS gradient for a set of electron-nuclear spin unit vectors (paramagnetic to the nuclear spin) from a structural ensemble, using the 3D tensorial form of the alignment tensor.  The formula for this ensemble average PCS gradient element is::

                            _N_
        ddelta_ij(theta)    \                   T   dAi
        ----------------  =  >  pc . djc . mu_jc . ---- . mu_jc,
              dAmn          /__                    dAmn
                            c=1

    where:
        - i is the alignment tensor index,
        - j is the index over spins,
        - m, the index over the first dimension of the alignment tensor m = {x, y, z}.
        - n, the index over the second dimension of the alignment tensor n = {x, y, z},
        - c is the index over the states or multiple structures,
        - theta is the parameter vector,
        - Amn is the matrix element of the alignment tensor,
        - djc is the PCS constant for spin j and state c,
        - N is the total number of states or structures,
        - pc is the population probability or weight associated with state c (equally weighted to 1/N if weights are not provided),
        - mu_jc is the unit vector corresponding to spin j and state c,
        - dAi/dAmn is the partial derivative of the alignment tensor with respect to element Amn.


    @param dj:          The PCS constants for each structure c for spin j.  This should be an array with indices corresponding to c.
    @type dj:           numpy rank-1 array
    @param vect:        The electron-nuclear unit vector matrix.  The first dimension corresponds to the structural index, the second dimension is the coordinates of the unit vector.  The vectors should be parallel to the vector connecting the paramagnetic centre to the nuclear spin.
    @type vect:         numpy matrix
    @param N:           The total number of structures.
    @type N:            int
    @param dAi_dAmn:    The alignment tensor derivative with respect to parameter Amn.
    @type dAi_dAmn:     numpy rank-2 3D tensor
    @param weights:     The weights for each member of the ensemble (the last member need not be supplied).
    @type weights:      numpy rank-1 array
    @return:            The average PCS gradient element.
    @rtype:             float
    """

    # Initial back-calculated PCS gradient.
    grad = 0.0

    # No weights given.
    if weights == None:
        pc = 1.0 / N
        weights = [pc] * N

    # Missing last weight.
    if len(weights) < N:
        pN = 1.0 - sum(weights, axis=0)
        weights = weights.tolist()
        weights.append(pN)

    # Back-calculate the PCS gradient element.
    for c in xrange(N):
        grad = grad + weights[c] * dj[c] * dot(vect[c], dot(dAi_dAmn, vect[c]))

    # Return the average PCS gradient element.
    return grad


def pcs_tensor(dj, mu, A):
    """Calculate the PCS, using the 3D alignment tensor.

    The PCS value is::

                                    T
        delta_ij(theta)  = dj . mu_j . Ai . mu_j,

    where:
        - i is the alignment tensor index,
        - j is the index over spins,
        - theta is the parameter vector,
        - dj is the PCS constant for spin j,
        - mu_j i the unit vector corresponding to spin j,
        - Ai is the alignment tensor.

    The PCS constant is defined as::

             mu0 15kT   1
        dj = --- ----- ---- ,
             4pi Bo**2 r**3

    where:
        - mu0 is the permeability of free space,
        - k is Boltzmann's constant,
        - T is the absolute temperature,
        - Bo is the magnetic field strength,
        - r is the distance between the paramagnetic centre (electron spin) and the nuclear spin.


    @param dj:          The PCS constant for spin j.
    @type dj:           float
    @param mu:          The unit vector connecting the electron and nuclear spins.
    @type mu:           numpy rank-1 3D array
    @param A:           The alignment tensor.
    @type A:            numpy rank-2 3D tensor
    @return:            The PCS value.
    @rtype:             float
    """

    # Return the PCS.
    return dj * dot(mu, dot(A, mu))
