###############################################################################
#                                                                             #
# Copyright (C) 2008-2013 Edward d'Auvergne                                   #
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
"""Module for the calculation of pseudocontact shifts."""

# Python imports.
from math import pi
from numpy import dot, sum

# relax module imports.
from physical_constants import kB, mu0


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
    for c in range(N):
        val = val + weights[c] * dj[c] * dot(vect[c], dot(A, vect[c]))

    # Return the average PCS.
    return val


def ave_pcs_tensor_ddeltaij_dAmn(dj, vect, N, dAi_dAmn, weights=None):
    """Calculate the ensemble average PCS gradient element for Amn, using the 3D tensor.

    This function calculates the alignment tensor parameter part of the average PCS gradient for a set of electron-nuclear spin unit vectors (paramagnetic to the nuclear spin) from a structural ensemble, using the 3D tensorial form of the alignment tensor.  The formula for this ensemble average PCS gradient element is::

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
    for c in range(N):
        grad = grad + weights[c] * dj[c] * dot(vect[c], dot(dAi_dAmn, vect[c]))

    # Return the average PCS gradient element.
    return grad


def ave_pcs_tensor_ddeltaij_dc(ddj=None, dj=None, r=None, unit_vect=None, N=None, Ai=None, dr_dc=None, weights=None):
    """Calculate the ensemble average PCS gradient element for the paramagnetic centre coordinate c, using the 3D tensor.

    This function calculates the paramagnetic centre coordinate part of the average PCS gradient for a set of electron-nuclear spin unit vectors (paramagnetic to the nuclear spin) from a structural ensemble, using the 3D tensorial form of the alignment tensor.  The formula for this ensemble average PCS gradient element is::

                            _N_
        ddelta_ij(theta)    \        / ddjc                       dr_jcT                          dr_jc \ 
        ----------------  =  >  pc . | ----.r_jcT.Ai.r_jc  +  djc.------.Ai.r_jc  +  djc.r_jcT.Ai.----- | ,
               dc           /__      \  dc                          dc                             dc   /
                            c=1

    where the last two terms in the sum are equal due to the symmetry of the alignment tensor, and:
        - i is the alignment tensor index,
        - j is the index over spins,
        - c is the index over the states or multiple structures,
        - theta is the parameter vector,
        - djc is the PCS constant for spin j and state c,
        - N is the total number of states or structures,
        - pc is the population probability or weight associated with state c (equally weighted to 1/N if weights are not provided),
        - r_jc is the vector corresponding to spin j and state c,

    and where::

        ddjc    mu0 15kT            4c
        ----  = --- ----- ------------------------  ,
         dc     4pi Bo**2 5(x**2+y**2+z**2)**(3/5)

    and::

        dr      | 1 |   dr      | 0 |   dr      | 0 |
        --  = - | 0 | , --  = - | 1 | , --  = - | 0 | .
        dx      | 0 |   dy      | 0 |   dy      | 1 |

    The pseudocontact shift constant is defined here as::

            mu0 15kT   1
        d = --- ----- ---- ,
            4pi Bo**2 r**5

  
    @keyword ddj:        The PCS constant gradient for each structure c for spin j.  This should be an array with indices corresponding to c.
    @type ddj:           numpy rank-1 array
    @keyword dj:          The PCS constants for each structure c for spin j.  This should be an array with indices corresponding to c.
    @type dj:           numpy rank-1 array
    @keyword r:         The distance between the paramagnetic centre and the spin (in meters).
    @type r:            float
    @keyword vect:        The electron-nuclear unit vector matrix.  The first dimension corresponds to the structural index, the second dimension is the coordinates of the unit vector.  The vectors should be parallel to the vector connecting the paramagnetic centre to the nuclear spin.
    @type vect:         numpy matrix
    @keyword N:           The total number of structures.
    @type N:            int
    @keyword Ai:          The alignment tensor i.
    @type Ai:           numpy rank-2, 3D tensor
    @keyword weights:     The weights for each member of the ensemble (the last member need not be supplied).
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

    # Loop over each state.
    for c in range(N):
        # Recreate the full length vector.
        vect = unit_vect[c] * r[c]

        # Modified PCS constant (from r**-3 to r**-5).
        const = dj[c] / r[c]**2

        # Back-calculate the PCS gradient element.
        grad += weights[c] * (ddj[c] * dot(vect, dot(Ai, vect))  +  2.0 * const * dot(dr_dc, dot(Ai, vect)))

    # Return the average PCS gradient element.
    return grad


def pcs_constant_grad(T=None, Bo=None, r=None, unit_vect=None, grad=None):
    """Calculate the PCS constant gradient with respect to the paramagnetic centre position.

    The pseudocontact shift constant is defined here as::

            mu0 15kT   1
        d = --- ----- ---- ,
            4pi Bo**2 r**5

    where:
        - mu0 is the permeability of free space,
        - k is Boltzmann's constant,
        - T is the absolute temperature,
        - Bo is the magnetic field strength,
        - r is the distance between the paramagnetic centre (electron spin) and the nuclear spin.

    The 5th power of the distance is used to simplify the PCS derivative.  The pseudocontact shift constant derivative is::

        dd    mu0 15kT            5c
        --  = --- ----- ------------------------  ,
        dc    4pi Bo**2 (x**2+y**2+z**2)**(7/2)
  
    where:
        - c is the one of the coordinates {x, y, z} of the paramagnetic centre to spin vector.


    @keyword T:         The temperature in kelvin.
    @type T:            float
    @keyword Bo:        The magnetic field strength.
    @type Bo:           float
    @keyword r:         The distance between the paramagnetic centre and the spin (in meters).
    @type r:            float
    @keyword unit_vect: The paramagnetic centre to spin unit vector.
    @type unit_vect:    numpy rank-1, 3D array
    @keyword grad:      The gradient component to update.  The indices {0, 1, 2} match the {dx, dy, dz} derivatives.
    @type grad:         numpy rank-1, 3D array
    """

    # Recreate the full length vector.
    vect = unit_vect * r

    # Calculate the invariant part.
    a = 18.75 * mu0 / pi * kB * T / Bo**2

    # Calculate the coordinate part.
    b = r**7

    # Combine.
    for i in range(3):
        grad[i] = a * vect[i] / b


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
