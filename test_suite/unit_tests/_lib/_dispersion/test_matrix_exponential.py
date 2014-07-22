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

# Python module imports.
from os import path, sep
from numpy import complex64, complex128, dot, einsum, load, sum
from unittest import TestCase

# relax module imports.
from lib.dispersion.ns_cpmg_2site_3d import rcpmg_3d_rankN
from lib.dispersion.ns_mmq_2site import rmmq_2site_rankN
from lib.linear_algebra.matrix_exponential import matrix_exponential
from lib.dispersion.matrix_exponential import matrix_exponential_rank_NE_NS_NM_NO_ND_x_x, matrix_exponential_rank_NS_NM_NO_ND_x_x
from status import Status; status = Status()


class Test_matrix_exponential(TestCase):
    """Unit tests for the lib.dispersion.matrix_exponential relax module."""

    def setUp(self):
        """Set up for all unit tests."""

        # Default parameter values.
        self.data = status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'unit_tests'+sep+'lib'+sep+'dispersion'+sep+'matrix_exponential'

    def return_data_ns_cpmg_2site_3d(self, fname):
        """Return the data structures from the data path."""

        r180x = load(fname+"_r180x"+".npy")
        M0 = load(fname+"_M0"+".npy")
        r10a = load(fname+"_r10a"+".npy")
        r10b = load(fname+"_r10b"+".npy")
        r20a = load(fname+"_r20a"+".npy")
        r20b = load(fname+"_r20b"+".npy")
        pA = load(fname+"_pA"+".npy")
        dw = load(fname+"_dw"+".npy")
        dw_orig = load(fname+"_dw_orig"+".npy")
        kex = load(fname+"_kex"+".npy")
        inv_tcpmg = load(fname+"_inv_tcpmg"+".npy")
        tcp = load(fname+"_tcp"+".npy")
        num_points = load(fname+"_num_points"+".npy")
        power = load(fname+"_power"+".npy")
        back_calc = load(fname+"_back_calc"+".npy")

        # Once off parameter conversions.
        pB = 1.0 - pA
        k_BA = pA * kex
        k_AB = pB * kex

        return r180x, M0, r10a, r10b, r20a, r20b, pA, dw, dw_orig, kex, inv_tcpmg, tcp, num_points, power, back_calc, pB, k_BA, k_AB


    def return_data_mmq_2site(self, fname):
        """Return the data structures from the data path."""

        M0 = load(fname+"_M0"+".npy")
        r20a = load(fname+"_r20a"+".npy")
        r20b = load(fname+"_r20b"+".npy")
        pA = load(fname+"_pA"+".npy")
        dw = load(fname+"_dw"+".npy")
        dwH = load(fname+"_dwH"+".npy")
        kex = load(fname+"_kex"+".npy")
        inv_tcpmg = load(fname+"_inv_tcpmg"+".npy")
        tcp = load(fname+"_tcp"+".npy")
        num_points = load(fname+"_num_points"+".npy")
        power = load(fname+"_power"+".npy")
        back_calc = load(fname+"_back_calc"+".npy")

        # Once off parameter conversions.
        pB = 1.0 - pA
        k_BA = pA * kex
        k_AB = pB * kex

        return M0, r20a, r20b, pA, dw, dwH, kex, inv_tcpmg, tcp, num_points, power, back_calc, pB, k_BA, k_AB


    def test_ns_cpmg_2site_3d_hansen_cpmg_data(self):
        """Test the matrix_exponential_rankN() function for higher dimensional data, and compare to matrix_exponential.  This uses the data from systemtest Relax_disp.test_hansen_cpmg_data_to_ns_cpmg_2site_3D."""

        fname = self.data + sep+ "test_hansen_cpmg_data_to_ns_cpmg_2site_3D"
        r180x, M0, r10a, r10b, r20a, r20b, pA, dw, dw_orig, kex, inv_tcpmg, tcp, num_points, power, back_calc, pB, k_BA, k_AB = self.return_data_ns_cpmg_2site_3d(fname)

        # Extract the total numbers of experiments, number of spins, number of magnetic field strength, number of offsets, maximum number of dispersion point.
        NE, NS, NM, NO, ND = back_calc.shape

        # The matrix R that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
        R_mat = rcpmg_3d_rankN(R1A=r10a, R1B=r10b, R2A=r20a, R2B=r20b, pA=pA, pB=pB, dw=dw, k_AB=k_AB, k_BA=k_BA, tcp=tcp)
    
        # This matrix is a propagator that will evolve the magnetization with the matrix R for a delay tcp.
        Rexpo_mat = matrix_exponential_rank_NE_NS_NM_NO_ND_x_x(R_mat)
    
        # Loop over the spins
        for si in range(NS):
            # Loop over the spectrometer frequencies.
            for mi in range(NM):
                # Extract number of points.
                num_points_si_mi = int(num_points[0, si, mi, 0])
    
                # Loop over the time points, back calculating the R2eff values.
                for di in range(num_points_si_mi):
                    # Test the two different methods.
                    R_mat_i = R_mat[0, si, mi, 0, di]
 
                    # The lower dimensional matrix exponential.
                    Rexpo = matrix_exponential(R_mat_i)
    
                    # The higher dimensional matrix exponential.
                    Rexpo_mat_i = Rexpo_mat[0, si, mi, 0, di]

                    diff = Rexpo - Rexpo_mat_i
                    diff_sum = sum(diff)

                    # Test that the sum difference is zero.                                        
                    self.assertAlmostEqual(diff_sum, 0.0)


    def test_ns_mmq_2site_korzhnev_2005_15n_dq_data_complex64(self):
        """Test the matrix_exponential_rankN() function for higher dimensional data, and compare to matrix_exponential.  This uses the data from systemtest Relax_disp.test_korzhnev_2005_15n_dq_data.
        This test does the matrix exponential in complex64."""

        fname = self.data + sep+ "test_korzhnev_2005_15n_dq_data"
        M0, R20A, R20B, pA, dw, dwH, kex, inv_tcpmg, tcp, num_points, power, back_calc, pB, k_BA, k_AB = self.return_data_mmq_2site(fname)

        # Extract the total numbers of experiments, number of spins, number of magnetic field strength, number of offsets, maximum number of dispersion point.
        NS, NM, NO = num_points.shape

        # Populate the m1 and m2 matrices (only once per function call for speed).
        m1_mat = rmmq_2site_rankN(R20A=R20A, R20B=R20B, dw=dw, k_AB=k_AB, k_BA=k_BA, tcp=tcp)
        m2_mat = rmmq_2site_rankN(R20A=R20A, R20B=R20B, dw=-dw, k_AB=k_AB, k_BA=k_BA, tcp=tcp)
    
        # The A+/- matrices.
        A_pos_mat = matrix_exponential_rank_NS_NM_NO_ND_x_x(m1_mat, dtype=complex64)
        A_neg_mat = matrix_exponential_rank_NS_NM_NO_ND_x_x(m2_mat, dtype=complex64)
    
        # Loop over spins.
        for si in range(NS):
            # Loop over the spectrometer frequencies.
            for mi in range(NM):
                # Loop over offsets:
                for oi in range(NO):
                    # Extract number of points.
                    num_points_i = num_points[si, mi, oi]
    
                    # Loop over the time points, back calculating the R2eff values.
                    for i in range(num_points_i):
                        # Test the two different methods.
                        # The A+/- matrices.
                        A_pos_i = A_pos_mat[si, mi, oi, i]
                        A_neg_i = A_neg_mat[si, mi, oi, i]
    
                        # The lower dimensional matrix exponential.
                        A_pos = matrix_exponential(m1_mat[si, mi, oi, i])
                        A_neg = matrix_exponential(m2_mat[si, mi, oi, i])
    
                        # Calculate differences
                        diff_A_pos_real = A_pos_i.real - A_pos.real
                        diff_A_pos_real_sum = sum(diff_A_pos_real)
                        diff_A_pos_imag = A_pos_i.imag - A_pos.imag
                        diff_A_pos_imag_sum = sum(diff_A_pos_imag)

                        diff_A_neg_real = A_neg_i.real - A_neg.real
                        diff_A_neg_real_sum = sum(diff_A_neg_real)
                        diff_A_neg_imag = A_neg_i.imag - A_neg.imag
                        diff_A_neg_imag_sum = sum(diff_A_neg_imag)

                        # Test that the sum difference is zero.                                        
                        self.assertAlmostEqual(diff_A_pos_real_sum , 0.0, 6)
                        self.assertAlmostEqual(diff_A_pos_imag_sum , 0.0, 6)
                        self.assertAlmostEqual(diff_A_neg_real_sum , 0.0, 6)
                        self.assertAlmostEqual(diff_A_neg_imag_sum , 0.0, 6)


    def test_ns_mmq_2site_korzhnev_2005_15n_dq_data_complex128(self):
        """Test the matrix_exponential_rankN() function for higher dimensional data, and compare to matrix_exponential.  This uses the data from systemtest Relax_disp.test_korzhnev_2005_15n_dq_data.
        This test does the matrix exponential in complex128."""

        fname = self.data + sep+ "test_korzhnev_2005_15n_dq_data"
        M0, R20A, R20B, pA, dw, dwH, kex, inv_tcpmg, tcp, num_points, power, back_calc, pB, k_BA, k_AB = self.return_data_mmq_2site(fname)

        # Extract the total numbers of experiments, number of spins, number of magnetic field strength, number of offsets, maximum number of dispersion point.
        NS, NM, NO = num_points.shape

        # Populate the m1 and m2 matrices (only once per function call for speed).
        m1_mat = rmmq_2site_rankN(R20A=R20A, R20B=R20B, dw=dw, k_AB=k_AB, k_BA=k_BA, tcp=tcp)
        m2_mat = rmmq_2site_rankN(R20A=R20A, R20B=R20B, dw=-dw, k_AB=k_AB, k_BA=k_BA, tcp=tcp)
    
        # The A+/- matrices.
        A_pos_mat = matrix_exponential_rank_NS_NM_NO_ND_x_x(m1_mat)
        A_neg_mat = matrix_exponential_rank_NS_NM_NO_ND_x_x(m2_mat)
    
        # Loop over spins.
        for si in range(NS):
            # Loop over the spectrometer frequencies.
            for mi in range(NM):
                # Loop over offsets:
                for oi in range(NO):
                    # Extract number of points.
                    num_points_i = num_points[si, mi, oi]
    
                    # Loop over the time points, back calculating the R2eff values.
                    for i in range(num_points_i):
                        # Test the two different methods.
                        # The A+/- matrices.
                        A_pos_i = A_pos_mat[si, mi, oi, i]
                        A_neg_i = A_neg_mat[si, mi, oi, i]
    
                        # The lower dimensional matrix exponential.
                        A_pos = matrix_exponential(m1_mat[si, mi, oi, i])
                        A_neg = matrix_exponential(m2_mat[si, mi, oi, i])
    
                        # Calculate differences
                        diff_A_pos_real = A_pos_i.real - A_pos.real
                        diff_A_pos_real_sum = sum(diff_A_pos_real)
                        diff_A_pos_imag = A_pos_i.imag - A_pos.imag
                        diff_A_pos_imag_sum = sum(diff_A_pos_imag)

                        diff_A_neg_real = A_neg_i.real - A_neg.real
                        diff_A_neg_real_sum = sum(diff_A_neg_real)
                        diff_A_neg_imag = A_neg_i.imag - A_neg.imag
                        diff_A_neg_imag_sum = sum(diff_A_neg_imag)

                        # Test that the sum difference is zero.                                        
                        self.assertEqual(diff_A_pos_real_sum , 0.0)
                        self.assertEqual(diff_A_pos_imag_sum , 0.0)
                        self.assertEqual(diff_A_neg_real_sum , 0.0)
                        self.assertEqual(diff_A_neg_imag_sum , 0.0)
