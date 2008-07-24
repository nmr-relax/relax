###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
"""Module for the calculation of RDCs."""

# Python imports.
from numpy import dot, sum


def average_rdc_5D(vect, K, A, weights=None):
    """Calculate the average RDC for an ensemble set of XH bond vectors, using the 5D notation.

    This function calculates the average RDC for a set of XH bond vectors from a structural
    ensemble, using the 5D vector form of the alignment tensor.  The formula for this ensemble
    average RDC value is::

                    _K_
                  1 \ 
        <RDC_i> = -  >  RDC_ik (theta),
                  K /__
                    k=1

    where K is the total number of structures,  k is the index over the multiple structures, RDC_ik
    is the back-calculated RDC value for spin system i and structure k, and theta is the parameter
    vector consisting of the alignment tensor parameters {Axx, Ayy, Axy, Axz, Ayz}.  The
    back-calculated RDC is given by the formula::

        RDC_ik(theta) = (x**2 - z**2)Axx + (y**2 - z**2)Ayy + 2x.y.Axy + 2x.z.Axz + 2y.z.Ayz.


    @param vect:        The unit XH bond vector matrix.  The first dimension corresponds to the
                        structural index, the second dimension is the coordinates of the unit
                        vector.
    @type vect:         numpy matrix
    @param K:           The total number of structures.
    @type K:            int
    @param A:           The 5D vector object.  The vector format is {Axx, Ayy, Axy, Axz, Ayz}.
    @type A:            numpy 5D vector
    @param weights:     The weights for each member of the ensemble.  The last weight is assumed to
                        be missing, and is calculated by this function.  Hence the length should be
                        one less than K.
    @type weights:      numpy rank-1 array
    @return:            The average RDC value.
    @rtype:             float
    """

    # Initial back-calculated RDC value.
    val = 0.0

    # Averaging factor.
    if weights == None:
        c = 1.0 / K

    # Loop over the structures k.
    for k in xrange(K):
        # The weights.
        if weights != None:
            if k == K-1: 
                c = 1.0 - sum(weights, axis=0)
            else:
                c = weights[k]

        # Back-calculate the RDC.
        val = val + c * (vect[k,0]**2 - vect[k,2]**2)*A[0] + (vect[k,1]**2 - vect[k,2]**2)*A[1] + 2.0*vect[k,0]*vect[k,1]*A[2] + 2.0*vect[k,0]*vect[k,2]*A[3] + 2.0*vect[k,1]*vect[k,2]*A[4]

    # Return the average RDC.
    return val


def average_rdc_tensor(vect, K, A, weights=None):
    """Calculate the average RDC for an ensemble set of XH bond vectors, using the 3D tensor.

    This function calculates the average RDC for a set of XH bond vectors from a structural
    ensemble, using the 3D tensorial form of the alignment tensor.  The formula for this ensemble
    average RDC value is::

                    _K_
                  1 \ 
        <RDC_i> = -  >  RDC_ik (theta),
                  K /__
                    k=1

    where K is the total number of structures,  k is the index over the multiple structures, RDC_ik
    is the back-calculated RDC value for spin system i and structure k, and theta is the parameter
    vector consisting of the alignment tensor.  The back-calculated RDC is given by the formula::

        RDC_ik(theta) = muT . A . mu,

    where mu is the unit XH bond vector, T is the transpose, and A is the alignment tensor matrix.


    @param vect:        The unit XH bond vector matrix.  The first dimension corresponds to the
                        structural index, the second dimension is the coordinates of the unit
                        vector.
    @type vect:         numpy matrix
    @param K:           The total number of structures.
    @type K:            int
    @param A:           The alignment tensor.
    @type A:            numpy rank-2 3D tensor
    @param weights:     The weights for each member of the ensemble.  The last weight is assumed to
                        be missing, and is calculated by this function.  Hence the length should be
                        one less than K.
    @type weights:      numpy rank-1 array
    @return:            The average RDC value.
    @rtype:             float
    """

    # Initial back-calculated RDC value.
    val = 0.0

    # Averaging factor.
    if weights == None:
        c = 1.0 / K

    # Loop over the structures k.
    for k in xrange(K):
        # The weights.
        if weights != None:
            if k == K-1: 
                c = 1.0 - sum(weights, axis=0)
            else:
                c = weights[k]

        # Back-calculate the RDC.
        val = val + c * dot(vect[k], dot(A, vect[k]))

    # Return the average RDC.
    return val
