###############################################################################
#                                                                             #
# Copyright (C) 2008-2010,2012-2013 Edward d'Auvergne                         #
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
"""Module for the calculation of RDCs."""

# Python imports.
from numpy import dot, sum


def ave_rdc_5D(dj, vect, N, A, weights=None):
    r"""Calculate the ensemble average RDC, using the 5D tensor.

    This function calculates the average RDC for a set of XH bond vectors from a structural ensemble, using the 5D vector form of the alignment tensor.  The formula for this ensemble average RDC value is::

                     _N_
                     \ 
        Dij(theta) =  >  pc . RDC_ijc (theta),
                     /__
                     c=1

    where:
        - i is the alignment tensor index,
        - j is the index over spins,
        - theta is the parameter vector consisting of the alignment tensor parameters {Axx, Ayy, Axy, Axz, Ayz} for each alignment,
        - c is the index over the states or multiple structures,
        - N is the total number of states or structures,
        - pc is the population probability or weight associated with state c (equally weighted to
        - RDC_ijc is the back-calculated RDC value for alignment tensor i, spin system j and structure c.

    The back-calculated RDC is given by the formula::

        RDC_ijc(theta) = (x_jc**2 - z_jc**2)Axx_i + (y_jc**2 - z_jc**2)Ayy_i + 2x_jc.y_jc.Axy_i + 2x_jc.z_jc.Axz_i + 2y_jc.z_jc.Ayz_i.


    @param dj:          The dipolar constant for spin j.
    @type dj:           float
    @param vect:        The unit XH bond vector matrix.  The first dimension corresponds to the structural index, the second dimension is the coordinates of the unit vector.
    @type vect:         numpy matrix
    @param N:           The total number of structures.
    @type N:            int
    @param A:           The 5D vector object.  The vector format is {Axx, Ayy, Axy, Axz, Ayz}.
    @type A:            numpy 5D vector
    @param weights:     The weights for each member of the ensemble (the last member need not be supplied).
    @type weights:      numpy rank-1 array
    @return:            The average RDC value.
    @rtype:             float
    """

    # Initial back-calculated RDC value.
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

    # Back-calculate the RDC.
    for c in range(N):
        val = val + weights[c] * (vect[c, 0]**2 - vect[c, 2]**2)*A[0] + (vect[c, 1]**2 - vect[c, 2]**2)*A[1] + 2.0*vect[c, 0]*vect[c, 1]*A[2] + 2.0*vect[c, 0]*vect[c, 2]*A[3] + 2.0*vect[c, 1]*vect[c, 2]*A[4]

    # Return the average RDC.
    return dj * val


def ave_rdc_tensor(dj, vect, N, A, weights=None):
    r"""Calculate the ensemble average RDC, using the 3D tensor.

    This function calculates the average RDC for a set of XH bond vectors from a structural ensemble, using the 3D tensorial form of the alignment tensor.  The formula for this ensemble average RDC value is::

                         _N_
                         \             T
        Dij(theta)  = dj  >  pc . mu_jc . Ai . mu_jc,
                         /__
                         c=1

    where:
        - i is the alignment tensor index,
        - j is the index over spins,
        - c is the index over the states or multiple structures,
        - theta is the parameter vector,
        - dj is the dipolar constant for spin j,
        - N is the total number of states or structures,
        - pc is the population probability or weight associated with state c (equally weighted to 1/N if weights are not provided),
        - mu_jc is the unit vector corresponding to spin j and state c,
        - Ai is the alignment tensor.

    The dipolar constant is defined as::

        dj = 3 / (2pi) d',

    where the factor of 2pi is to convert from units of rad.s^-1 to Hertz, the factor of 3 is associated with the alignment tensor and the pure dipolar constant in SI units is::

               mu0 gI.gS.h_bar
        d' = - --- ----------- ,
               4pi    r**3

    where:
        - mu0 is the permeability of free space,
        - gI and gS are the gyromagnetic ratios of the I and S spins,
        - h_bar is Dirac's constant which is equal to Planck's constant divided by 2pi,
        - r is the distance between the two spins.


    @param dj:          The dipolar constant for spin j.
    @type dj:           float
    @param vect:        The unit XH bond vector matrix.  The first dimension corresponds to the structural index, the second dimension is the coordinates of the unit vector.
    @type vect:         numpy matrix
    @param N:           The total number of structures.
    @type N:            int
    @param A:           The alignment tensor.
    @type A:            numpy rank-2 3D tensor
    @keyword weights:   The weights for each member of the ensemble (the last member need not be supplied).
    @type weights:      numpy rank-1 array or None
    @return:            The average RDC value.
    @rtype:             float
    """

    # Initial back-calculated RDC value.
    val = 0.0

    # No weights given.
    if weights is None:
        pc = 1.0 / N
        weights = [pc] * N

    # Missing last weight.
    if len(weights) < N:
        pN = 1.0 - sum(weights, axis=0)
        weights = weights.tolist()
        weights.append(pN)

    # Back-calculate the RDC.
    for c in range(N):
        val = val + weights[c] * dot(vect[c], dot(A, vect[c]))

    # Return the average RDC.
    return dj * val


def ave_rdc_tensor_dDij_dAmn(dj, vect, N, dAi_dAmn, weights=None):
    r"""Calculate the ensemble average RDC gradient element for Amn, using the 3D tensor.

    This function calculates the average RDC gradient for a set of XH bond vectors from a structural ensemble, using the 3D tensorial form of the alignment tensor.  The formula for this ensemble average RDC gradient element is::

                          _N_
        dDij(theta)       \             T   dAi
        -----------  = dj  >  pc . mu_jc . ---- . mu_jc,
           dAmn           /__              dAmn
                          c=1

    where:
        - i is the alignment tensor index,
        - j is the index over spins,
        - m, the index over the first dimension of the alignment tensor m = {x, y, z}.
        - n, the index over the second dimension of the alignment tensor n = {x, y, z},
        - c is the index over the states or multiple structures,
        - theta is the parameter vector,
        - Amn is the matrix element of the alignment tensor,
        - dj is the dipolar constant for spin j,
        - N is the total number of states or structures,
        - pc is the population probability or weight associated with state c (equally weighted to 1/N if weights are not provided),
        - mu_jc is the unit vector corresponding to spin j and state c,
        - dAi/dAmn is the partial derivative of the alignment tensor with respect to element Amn.


    @param dj:          The dipolar constant for spin j.
    @type dj:           float
    @param vect:        The unit XH bond vector matrix.  The first dimension corresponds to the structural index, the second dimension is the coordinates of the unit vector.
    @type vect:         numpy matrix
    @param N:           The total number of structures.
    @type N:            int
    @param dAi_dAmn:    The alignment tensor derivative with respect to parameter Amn.
    @type dAi_dAmn:     numpy rank-2 3D tensor
    @keyword weights:   The weights for each member of the ensemble (the last member need not be supplied).
    @type weights:      numpy rank-1 array
    @return:            The average RDC gradient element.
    @rtype:             float
    """

    # Initial back-calculated RDC gradient.
    grad = 0.0

    # No weights given.
    if weights is None:
        pc = 1.0 / N
        weights = [pc] * N

    # Missing last weight.
    if len(weights) < N:
        pN = 1.0 - sum(weights, axis=0)
        weights = weights.tolist()
        weights.append(pN)

    # Back-calculate the RDC gradient element.
    for c in range(N):
        grad = grad + weights[c] * dot(vect[c], dot(dAi_dAmn, vect[c]))

    # Return the average RDC gradient element.
    return dj * grad


def ave_rdc_tensor_pseudoatom(dj, vect, N, A, weights=None):
    r"""Calculate the ensemble and pseudo-atom averaged RDC, using the 3D tensor.

    This function calculates the average RDC for a set of XH bond vectors from a structural ensemble, using the 3D tensorial form of the alignment tensor.  The RDC for each pseudo-atom is calculated and then averaged.  The formula for this ensemble and pseudo-atom average RDC value is::

                         _N_        _M_
                         \        1 \         T
        Dij(theta)  = dj  >  pc . -  >  mu_jcd . Ai . mu_jcd,
                         /__      M /__
                         c=1        d=1

    where:
        - i is the alignment tensor index,
        - j is the index over spins,
        - c is the index over the states or multiple structures,
        - d is the index over the pseudo-atoms,
        - theta is the parameter vector,
        - dj is the dipolar constant for spin j,
        - N is the total number of states or structures,
        - M is the total number of pseudo-atoms,
        - pc is the population probability or weight associated with state c (equally weighted to 1/N if weights are not provided),
        - mu_jcd is the unit vector corresponding to spin j, state c, and pseudo-atom d,
        - Ai is the alignment tensor.

    The dipolar constant is defined as::

        dj = 3 / (2pi) d',

    where the factor of 2pi is to convert from units of rad.s^-1 to Hertz, the factor of 3 is associated with the alignment tensor and the pure dipolar constant in SI units is::

               mu0 gI.gS.h_bar
        d' = - --- ----------- ,
               4pi    r**3

    where:
        - mu0 is the permeability of free space,
        - gI and gS are the gyromagnetic ratios of the I and S spins,
        - h_bar is Dirac's constant which is equal to Planck's constant divided by 2pi,
        - r is the distance between the two spins.


    @param dj:          The dipolar constant for spin j.
    @type dj:           list of float
    @param vect:        The unit vector matrix.  The first dimension corresponds to the structural index, the second dimension to the pseudo-atom index, and the third dimension is the coordinates of the unit vector.
    @type vect:         numpy matrix
    @param N:           The total number of structures.
    @type N:            int
    @param A:           The alignment tensor.
    @type A:            numpy rank-2 3D tensor
    @keyword weights:   The weights for each member of the ensemble (the last member need not be supplied).
    @type weights:      numpy rank-1 array or None
    @return:            The average RDC value.
    @rtype:             float
    """

    # Calculate M.
    M = len(dj)

    # Initial back-calculated RDC value.
    val = 0.0

    # Loop over the pseudo-atoms, calculating the average RDC for the structural ensemble.
    for d in range(M):
        val += ave_rdc_tensor(dj[d], vect[:, d,:], N, A, weights)

    # Average.
    val = val / M

    # Return the averaged value.
    return val


def ave_rdc_tensor_pseudoatom_dDij_dAmn(dj, vect, N, dAi_dAmn, weights=None):
    r"""Calculate the ensemble and pseudo-atom average RDC gradient element for Amn, using the 3D tensor.

    This function calculates the average RDC gradient for a set of XH bond vectors from a structural ensemble, using the 3D tensorial form of the alignment tensor.  The formula for this ensemble average RDC gradient element is::

                          _N_        _M_
        dDij(theta)       \        1 \         T   dAi
        -----------  = dj  >  pc . -  >  mu_jcd . ---- . mu_jcd,
           dAmn           /__      M /__          dAmn
                          c=1        d=1

    where:
        - i is the alignment tensor index,
        - j is the index over spins,
        - m, the index over the first dimension of the alignment tensor m = {x, y, z}.
        - n, the index over the second dimension of the alignment tensor n = {x, y, z},
        - c is the index over the states or multiple structures,
        - d is the index over the pseudo-atoms,
        - theta is the parameter vector,
        - Amn is the matrix element of the alignment tensor,
        - dj is the dipolar constant for spin j,
        - N is the total number of states or structures,
        - M is the total number of pseudo-atoms,
        - pc is the population probability or weight associated with state c (equally weighted to 1/N if weights are not provided),
        - mu_jc is the unit vector corresponding to spin j and state c,
        - dAi/dAmn is the partial derivative of the alignment tensor with respect to element Amn.


    @param dj:          The dipolar constant for spin j.
    @type dj:           float
    @param vect:        The unit XH bond vector matrix.  The first dimension corresponds to the structural index, the second dimension is the coordinates of the unit vector.
    @type vect:         numpy matrix
    @param N:           The total number of structures.
    @type N:            int
    @param dAi_dAmn:    The alignment tensor derivative with respect to parameter Amn.
    @type dAi_dAmn:     numpy rank-2 3D tensor
    @keyword weights:   The weights for each member of the ensemble (the last member need not be supplied).
    @type weights:      numpy rank-1 array
    @return:            The average RDC gradient element.
    @rtype:             float
    """

    # Calculate M.
    M = len(dj)

    # Initial back-calculated RDC value.
    grad = 0.0

    # Loop over the pseudo-atoms, calculating the average RDC for the structural ensemble.
    for d in range(M):
        grad += ave_rdc_tensor_dDij_dAmn(dj[d], vect[:, d,:], N, dAi_dAmn, weights)

    # Average.
    grad = grad / M

    # Return the average RDC gradient element.
    return grad


def rdc_tensor(dj, mu, A):
    """Calculate the RDC, using the 3D alignment tensor.

    The RDC value is::

                               T
        Dij(theta)  = dj . mu_j . Ai . mu_j,

    where:
        - i is the alignment tensor index,
        - j is the index over spins,
        - theta is the parameter vector,
        - dj is the dipolar constant for spin j,
        - mu_j i the unit vector corresponding to spin j,
        - Ai is the alignment tensor.

    The dipolar constant is defined as::

        dj = 3 / (2pi) d',

    where the factor of 2pi is to convert from units of rad.s^-1 to Hertz, the factor of 3 is
    associated with the alignment tensor and the pure dipolar constant in SI units is::

               mu0 gI.gS.h_bar
        d' = - --- ----------- ,
               4pi    r**3

    where:
        - mu0 is the permeability of free space,
        - gI and gS are the gyromagnetic ratios of the I and S spins,
        - h_bar is Dirac's constant which is equal to Planck's constant divided by 2pi,
        - r is the distance between the two spins.


    @param dj:          The dipolar constant for spin j.
    @type dj:           float
    @param mu:          The unit XH bond vector.
    @type mu:           numpy rank-1 3D array
    @param A:           The alignment tensor.
    @type A:            numpy rank-2 3D tensor
    @return:            The RDC value.
    @rtype:             float
    """

    # Return the RDC.
    return dj * dot(mu, dot(A, mu))
