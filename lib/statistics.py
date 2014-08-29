###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""Module for calculating simple statistics."""

# Python module imports.
from numpy import absolute, diag, dot, eye, multiply, transpose
from numpy.linalg import inv, qr

# Python module imports.
from math import exp, pi, sqrt


def bucket(values=None, lower=0.0, upper=200.0, inc=100, verbose=False):
    """Generate a discrete probability distribution for the given values.

    @keyword values:    The list of values to convert.
    @type values:       list of float
    @keyword lower:     The lower bound of the distribution.
    @type lower:        float
    @keyword upper:     The upper bound of the distribution.
    @type upper:        float
    @keyword inc:       The number of discrete increments for the distribution between the lower and upper bounds.
    @type inc:          int
    @keyword verbose:   A flag which if True will enable printouts.
    @type verbose:      bool
    @return:            The discrete probability distribution.
    @rtype:             list of lists of float
    """

    # The bin width.
    bin_width = (upper - lower)/float(inc)

    # Init the dist object.
    dist = []
    for i in range(inc):
        dist.append([bin_width*i+lower, 0])

    # Loop over the values.
    for val in values:
        # The bin.
        bin = int((val - lower)/bin_width)

        # Outside of the limits.
        if bin < 0 or bin >= inc:
            if verbose:
                print("Outside of the limits: '%s'" % val)
            continue

        # Increment the count.
        dist[bin][1] = dist[bin][1] + 1

    # Convert the counts to frequencies.
    total_pr = 0.0
    for i in range(inc):
        dist[i][1] = dist[i][1] / float(len(values))
        total_pr = total_pr + dist[i][1]

    # Printout.
    if verbose:
        print("Total Pr: %s" % total_pr)

    # Return the dist.
    return dist


def gaussian(x=None, mu=0.0, sigma=1.0):
    """Calculate the probability for a Gaussian probability distribution for a given x value.

    @keyword x:     The x value to calculate the probability for.
    @type x:        float
    @keyword mu:    The mean of the distribution.
    @type mu:       float
    @keyword sigma: The standard deviation of the distribution.
    @type sigma:    float
    @return:        The probability corresponding to x.
    @rtype:         float
    """

    # Calculate and return the probability.
    return exp(-(x-mu)**2 / (2.0*sigma**2)) / (sigma * sqrt(2.0 * pi))


def std(values=None, skip=None, dof=1):
    """Calculate the standard deviation of the given values, skipping values if asked.

    @keyword values:    The list of values to calculate the standard deviation of.
    @type values:       list of float
    @keyword skip:      An optional list of booleans specifying if a value should be skipped.  The length of this list must match the values.  An element of True will cause the corresponding value to not be included in the calculation.
    @type skip:         list of bool or None.
    @keyword dof:       The degrees of freedom, whereby the standard deviation is multipled by 1/(N - dof).
    @type dof:          int
    @return:            The standard deviation.
    @rtype:             float
    """

    # The total number of points.
    n = 0
    for i in range(len(values)):
        # Skip deselected values.
        if skip != None and not skip[i]:
            continue

        # Increment n.
        n = n + 1

    # Calculate the sum of the values for all points.
    Xsum = 0.0
    for i in range(len(values)):
        # Skip deselected values.
        if skip != None and not skip[i]:
            continue

        # Sum.
        Xsum = Xsum + values[i]

    # Calculate the mean value for all points.
    if n == 0:
        Xav = 0.0
    else:
        Xav = Xsum / float(n)

    # Calculate the sum part of the standard deviation.
    sd = 0.0
    for i in range(len(values)):
        # Skip deselected values.
        if skip != None and not skip[i]:
            continue

        # Sum.
        sd = sd + (values[i] - Xav)**2

    # Calculate the standard deviation.
    if n <= 1:
        sd = 0.0
    else:
        sd = sqrt(sd / (float(n) - float(dof)))

    # Return the SD.
    return sd


def multifit_covar(J=None, epsrel=0.0, weights=None):
    """This is the implementation of the multifit covariance.

    This is inspired from GNU Scientific Library (GSL).

    This function uses the Jacobian matrix J to compute the covariance matrix of the best-fit parameters, covar.

    The parameter 'epsrel' is used to remove linear-dependent columns when J is rank deficient.

    The weighting matrix 'W', is a square symmetric matrix. For independent measurements, this is a diagonal matrix. Larger values indicate greater significance.  It is formed by multiplying and Identity matrix with the supplied weights vector::

        W = I. w

    The weights should normally be supplied as a vector: 1 / errors^2. 

    The covariance matrix is given by::

        covar = (J^T.W.J)^{-1} ,

    and is computed by QR decomposition of J with column-pivoting. Any columns of R which satisfy::

        |R_{kk}| <= epsrel |R_{11}| ,

    are considered linearly-dependent and are excluded from the covariance matrix (the corresponding rows and columns of the covariance matrix are set to zero).  If the minimisation uses the weighted least-squares function::

        f_i = (Y(x, t_i) - y_i) / sigma_i ,

    then the covariance matrix above gives the statistical error on the best-fit parameters resulting from the Gaussian errors 'sigma_i' on the underlying data 'y_i'.

    This can be verified from the relation 'd_f = J d_c' and the fact that the fluctuations in 'f' from the data 'y_i' are normalised by 'sigma_i' and so satisfy::

        <d_f d_f^T> = I. ,

    For an unweighted least-squares function f_i = (Y(x, t_i) - y_i) the covariance matrix above should be multiplied by the variance of the residuals about the best-fit::

        sigma^2 = sum ( (y_i - Y(x, t_i))^2 / (n-p) ) ,

    to give the variance-covariance matrix sigma^2 C.  This estimates the statistical error on the best-fit parameters from the scatter of the underlying data.

    Links
    =====

    More information ca be found here:

        - U{GSL - GNU Scientific Library<http://www.gnu.org/software/gsl/>}
        - U{Manual: Overview<http://www.gnu.org/software/gsl/manual/gsl-ref_37.html#SEC510>}
        - U{Manual: Computing the covariance matrix of best fit parameters<http://www.gnu.org/software/gsl/manual/gsl-ref_38.html#SEC528>}
        - U{Other reference<http://www.orbitals.com/self/least/least.htm>}

    @param J:               The Jacobian matrix.
    @type J:                numpy array
    @param epsrel:          Any columns of R which satisfy |R_{kk}| <= epsrel |R_{11}| are considered linearly-dependent and are excluded from the covariance matrix, where the corresponding rows and columns of the covariance matrix are set to zero.
    @type epsrel:           float
    @keyword weigths:       The weigths which to scale with.  Normally submitted as the 1 over standard deviation of the measured intensity values per time point in power 2. weigths = 1 / sd_i^2.
    @type weigths:          numpy array
    @return:                The co-variance matrix
    @rtype:                 square numpy array
    """

    # Weighting matrix. This is a square symmetric matrix.
    # For independent measurements, this is a diagonal matrix. Larger values indicate greater significance.

    # Make a square diagonal matrix.
    eye_mat = eye(weights.shape[0])

    # Form weight matrix.
    W = multiply(eye_mat, weights)

    # The covariance matrix (sometimes referred to as the variance-covariance matrix), Qxx, is defined as:
    # Qxx = (J^t W J)^(-1)

    # Calculate step by step, by matrix multiplication.
    Jt = transpose(J)
    Jt_W = dot(Jt, W)
    Jt_W_J = dot(Jt_W, J)

    # Invert matrix by QR decomposition, to check columns of R which satisfy: |R_{kk}| <= epsrel |R_{11}|
    Q, R = qr(Jt_W_J)

    # Make the state ment matrix.
    abs_epsrel_R11 = absolute( multiply(epsrel, R[0, 0]) )

    # Make and array of True/False statements.
    # These are considered linearly-dependent and are excluded from the covariance matrix.
    # The corresponding rows and columns of the covariance matrix are set to zero
    epsrel_check = absolute(R) <= abs_epsrel_R11

    # Form the covariance matrix.
    Qxx = dot(inv(R), transpose(Q) )
    #Qxx2 = dot(inv(R), inv(Q) )
    #print(Qxx - Qxx2)

    # Test direct invert matrix of matrix.
    #Qxx_test = inv(Jt_W_J)

    # Replace values in Covariance matrix with inf.
    Qxx[epsrel_check] = 0.0

    # Throw a warning, that some colums are considered linearly-dependent and are excluded from the covariance matrix.
    # Only check for the diagonal, since the that holds the variance.
    diag_epsrel_check = diag(epsrel_check)

    # If any of the diagonals does not meet the epsrel condition.
    if any(diag_epsrel_check):
        for i in range(diag_epsrel_check.shape[0]):
            abs_Rkk = absolute(R[i, i])
            if abs_Rkk <= abs_epsrel_R11:
                warn(RelaxWarning("Co-Variance element k,k=%i was found to meet |R_{kk}| <= epsrel |R_{11}|, meaning %1.1f <= %1.3f * %1.1f , and is therefore determined to be linearly-dependent and are excluded from the covariance matrix by setting the value to 0.0." % (i+1, abs_Rkk, epsrel, abs_epsrel_R11/epsrel) ))
                #print(cond(Jt_W_J) < 1./spacing(1.) )

    return Qxx
