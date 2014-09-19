#!/usr/bin/env python

###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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

"""
This script is for testing how to stride over matrices, in a large data array, when they are positioned in the end of the dimensions.

It also serves as a validation tool, and an efficient way to profile the calculation.
It is optimal to eventually try to implement a faster matrix power calculation.

"""


# Python module imports.
import cProfile
import pstats
import tempfile

from numpy.lib.stride_tricks import as_strided
from numpy import any, arange, int16, zeros
from numpy.linalg import matrix_power

def main():
    # Nr of iterations.
    nr_iter = 10

    # Print statistics.
    verbose = True

    # Calc for single_normal.
    if True:
    #if False:
        # Define filename
        sn_filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('single_normal(iter=%s)'%nr_iter, sn_filename)

        # Read all stats files into a single object
        sn_stats = pstats.Stats(sn_filename)

        # Clean up filenames for the report
        sn_stats.strip_dirs()

        # Sort the statistics by the cumulative time spent in the function. cumulative, time, calls
        sn_stats.sort_stats('cumulative')

        # Print report for single.
        if verbose:
            print("This is the report for single normal.")
            sn_stats.print_stats()

    # Calc for single_strided.
    if True:
    #if False:
        # Define filename
        ss_filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('single_strided(iter=%s)'%nr_iter, ss_filename)

        # Read all stats files into a single object
        ss_stats = pstats.Stats(ss_filename)

        # Clean up filenames for the report
        ss_stats.strip_dirs()

        # Sort the statistics by the cumulative time spent in the function. cumulative, time, calls
        ss_stats.sort_stats('cumulative')

        # Print report for single.
        if verbose:
            print("This is the report for single strided.")
            ss_stats.print_stats()

    # Calc for cluster_normal.
    if True:
    #if False:
        # Define filename
        cn_filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a cluster spin.
        cProfile.run('cluster_normal(iter=%s)'%nr_iter, cn_filename)

        # Read all stats files into a single object
        cn_stats = pstats.Stats(cn_filename)

        # Clean up filenames for the report
        cn_stats.strip_dirs()

        # Sort the statistics by the cumulative time spent in the function. cumulative, time, calls
        cn_stats.sort_stats('cumulative')

        # Print report for cluster.
        if verbose:
            print("This is the report for cluster normal.")
            cn_stats.print_stats()

    # Calc for cluster_strided.
    if True:
    #if False:
        # Define filename
        cs_filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a cluster spin.
        cProfile.run('cluster_strided(iter=%s)'%nr_iter, cs_filename)

        # Read all stats files into a single object
        cs_stats = pstats.Stats(cs_filename)

        # Clean up filenames for the report
        cs_stats.strip_dirs()

        # Sort the statistics by the cumulative time spent in the function. cumulative, time, calls
        cs_stats.sort_stats('cumulative')

        # Print report for cluster.
        if verbose:
            print("This is the report for cluster strided.")
            cs_stats.print_stats()

class Profile():
    """
    Class Profile inherits the Dispersion container class object.
    """

    def __init__(self, NE=1, NS=3, NM=2, NO=1, ND=20, Row=7, Col=7):

        # Setup the size of data array:
        self.NE = NE
        self.NS = NS
        self.NM = NM
        self.NO = NO
        self.ND = ND
        self.Row = Row
        self.Col = Col

        # Create the data matrix
        self.data = self.create_data()

        # Create the index matrix
        self.index = self.create_index()

        # Create the power matrix
        self.power = self.create_power()

        # Create the validation matrix
        self.vali = self.create_vali()


    def create_data(self):
        """ Method to create the imagninary data structure"""

        NE = self.NE
        NS = self.NS
        NM = self.NM
        NO = self.NO
        ND = self.ND
        Row = self.Row
        Col = self.Col
    
        # Create the data matrix for testing.
        data = arange(NE*NS*NM*NO*ND*Row*Col).reshape(NE, NS, NM, NO, ND, Row, Col)

        return data


    def create_index(self):
        """ Method to create the helper index matrix, to help figuring out the index to store in the data matrix. """

        NE = self.NE
        NS = self.NS
        NM = self.NM
        NO = self.NO
        ND = self.ND
    
        # Make array to store index.
        index = zeros([NE, NS, NM, NO, ND, 5], int16)

        for ei in range(NE):
            for si in range(NS):
                for mi in range(NM):
                    for oi in range(NO):
                        for di in range(ND):
                            index[ei, si, mi, oi, di] = ei, si, mi, oi, di

        return index


    def create_power(self):
        """ Method to create the test power data array. """

        NE = self.NE
        NS = self.NS
        NM = self.NM
        NO = self.NO
        ND = self.ND

        power = zeros([NE, NS, NM, NO, ND], int16)
   
        # Preform the power array, to be outside profiling test.
        for ei in range(NE):
            for si in range(NS):
                for mi in range(NM):
                    for oi in range(NO):
                        for di in range(ND):
                            power[ei, si, mi, oi, di] = 1+ei+si+mi+mi+di

        return power


    def create_vali(self):
        """ Create validation matrix for power array calculation. """

        NE = self.NE
        NS = self.NS
        NM = self.NM
        NO = self.NO
        ND = self.ND
        Row = self.Row
        Col = self.Col

        power = self.power
        data = self.data

        # Make array to store results
        vali = zeros([NE, NS, NM, NO, ND, Row, Col])

        # Normal way, by loop of loops.
        for ei in range(NE):
            for si in range(NS):
                for mi in range(NM):
                    for oi in range(NO):
                        for di in range(ND):
                            # Get the outer square data matrix,
                            data_i = data[ei, si, mi, oi, di]

                            # Get the power.
                            power_i = power[ei, si, mi, oi, di]

                            # Do power calculation with numpy method.
                            data_power_i = matrix_power(data_i, power_i)

                            # Store result.
                            vali[ei, si, mi, oi, di] = data_power_i

        return vali


    def stride_help_square_matrix(self, data):
        """ Method to stride through the data matrix, extracting the outer Row X Col matrix. """

        # Extract shapes from data.
        NE, NS, NM, NO, ND, Row, Col = data.shape

        # Calculate how many small matrices.
        Nr_mat = NE * NS * NM * NO * ND

        # Define the shape for the stride view.
        shape = (Nr_mat, Row, Col)
    
        # Get itemsize, Length of one array element in bytes. Depends on dtype. float64=8, complex128=16.
        itz = data.itemsize
    
        # Bytes_between_elements
        bbe = 1 * itz
    
        # Bytes between row. The distance in bytes to next row is number of Columns elements multiplied with itemsize.
        bbr = Col * itz
    
        # Bytes between matrices.  The byte distance is separated by the number of rows.
        bbm = Row * Col * itz

        # Make a tuple of the strides.
        strides = (bbm, bbr, bbe)

        # Make the stride view.
        data_view = as_strided(data, shape=shape, strides=strides)

        return data_view


    def stride_help_array(self, data):
        """ Method to stride through the data matrix, extracting the outer array with nr of elements as Column length. """

        # Extract shapes from data.
        NE, NS, NM, NO, ND, Col = data.shape

        # Calculate how many small matrices.
        Nr_mat = NE * NS * NM * NO * ND

        # Define the shape for the stride view.
        shape = (Nr_mat, Col)
    
        # Get itemsize, Length of one array element in bytes. Depends on dtype. float64=8, complex128=16.
        itz = data.itemsize
    
        # Bytes_between_elements
        bbe = 1 * itz
    
        # Bytes between row. The distance in bytes to next row is number of Columns elements multiplied with itemsize.
        bbr = Col * itz
    
        # Make a tuple of the strides.
        strides = (bbr, bbe)

        # Make the stride view.
        data_view = as_strided(data, shape=shape, strides=strides)

        return data_view


    def stride_help_element(self, data):
        """ Method to stride through the data matrix, extracting the outer element. """

        # Extract shapes from data.
        NE, NS, NM, NO, Col = data.shape

        # Calculate how many small matrices.
        Nr_mat = NE * NS * NM * NO * Col

        # Define the shape for the stride view.
        shape = (Nr_mat, 1)
    
        # Get itemsize, Length of one array element in bytes. Depends on dtype. float64=8, complex128=16.
        itz = data.itemsize
    
        # FIXME: Explain this.
        bbe = Col * itz
    
        # FIXME: Explain this.
        bbr = 1 * itz
    
        # Make a tuple of the strides.
        strides = (bbr, bbe)

        # Make the stride view.
        data_view = as_strided(data, shape=shape, strides=strides)

        return data_view


    def calc_normal(self, data, power):
        """ The normal way to do the calculation """

        # Extract shapes from data.
        NE, NS, NM, NO, ND, Row, Col = data.shape

        # Make array to store results
        calc = zeros([NE, NS, NM, NO, ND, Row, Col])

        # Normal way, by loop of loops.
        for ei in range(NE):
            for si in range(NS):
                for mi in range(NM):
                    for oi in range(NO):
                        for di in range(ND):
                            # Get the outer square data matrix,
                            data_i = data[ei, si, mi, oi, di]

                            # Get the power.
                            power_i = power[ei, si, mi, oi, di]

                            # Do power calculation with numpy method.
                            data_power_i = matrix_power(data_i, power_i)

                            # Store result.
                            calc[ei, si, mi, oi, di] = data_power_i

        return calc
        

    def calc_strided(self, data, power):
        """ The strided way to do the calculation """

        # Extract shapes from data.
        NE, NS, NM, NO, ND, Row, Col = data.shape

        # Make array to store results
        calc = zeros([NE, NS, NM, NO, ND, Row, Col])

        # Get the data view, from the helper function.
        data_view = self.stride_help_square_matrix(data)

        # Get the power view, from the helpwer function.
        power_view = self.stride_help_element(power)

        # The index view could be pre formed in init.
        index = self.index
        index_view = self.stride_help_array(index)

        # Zip them together and iterate over them.
        for data_i, power_i, index_i in zip(data_view, power_view, index_view):
            # Do power calculation with numpy method.
            data_power_i = matrix_power(data_i, int(power_i))

            # Extract index from index_view.
            ei, si, mi, oi, di = index_i

            # Store the result.
            calc[ei, si, mi, oi, di] = data_power_i

        return calc


    def validate(self):
        """ The validation of calculations """

        data = self.data
        power = self.power

        # Calculate by normal way.
        calc_normal = self.calc_normal(data, power)

        # Find the difference to the validated method.
        diff_normal_test = calc_normal != self.vali

        if any(diff_normal_test):
            diff_normal = calc_normal - self.vali
            print("The normal method is different from the validated data")
            print(diff_normal)

        # Calculate by strided way.
        calc_strided = self.calc_strided(data, power)

        # Find the difference to the validated method.
        diff_strided_test = calc_strided != self.vali

        if any(diff_strided_test):
            diff_strided = calc_strided - self.vali
            print("The strided method is different from the validated data")
            print(diff_strided )


def single_normal(NS=1, iter=None):

    # Instantiate class
    MC = Profile(NS=NS)

    # Get the init data.
    data = MC.data
    power = MC.power

    # Loop 100 times for each spin in the clustered analysis (to make the timing numbers equivalent).
    for spin_index in xrange(100):
        # Repeat the function call, to simulate minimisation.
        for i in xrange(iter):
            calc = MC.calc_normal(data, power)


def single_strided(NS=1, iter=None):

    # Instantiate class
    MC = Profile(NS=NS)

    # Get the init data.
    data = MC.data
    power = MC.power

    # Loop 100 times for each spin in the clustered analysis (to make the timing numbers equivalent).
    for spin_index in xrange(100):
        # Repeat the function call, to simulate minimisation.
        for i in xrange(iter):
            calc = MC.calc_strided(data, power)


def cluster_normal(NS=100, iter=None):

    # Instantiate class
    MC = Profile(NS=NS)

    # Get the init data.
    data = MC.data
    power = MC.power

    # Repeat the function call, to simulate minimisation.
    for i in xrange(iter):
        calc = MC.calc_normal(data, power)


def cluster_strided(NS=100, iter=None):

    # Instantiate class
    MC = Profile(NS=NS)

    # Get the init data.
    data = MC.data
    power = MC.power

    # Repeat the function call, to simulate minimisation.
    for i in xrange(iter):
        calc = MC.calc_strided(data, power)


# First validate
#Initiate My Class.
MC = Profile()

# Validate all calculations.
MC.validate()


# Execute main function.
if __name__ == "__main__":
    # Initiate cProfiling.
    main()
