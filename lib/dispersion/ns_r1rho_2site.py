###############################################################################
#                                                                             #
# Copyright (C) 2000-2001 Nikolai Skrynnikov                                  #
# Copyright (C) 2000-2001 Martin Tollinger                                    #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
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
"""The numerical solution for the 2-site Bloch-McConnell equations for R1rho-type data, the U{NS R1rho 2-site<http://wiki.nmr-relax.com/NS_R1rho_2-site>} model.

Description
===========

This is the model of the numerical solution for the 2-site Bloch-McConnell equations.  It originates from the funNumrho.m file from the Skrynikov & Tollinger code (the sim_all.tar file U{https://gna.org/support/download.php?file_id=18404} attached to U{https://gna.org/task/?7712#comment5}).  That code is::

    function residual = funNumrho(optpar)


    global nu_0 x y Rcalc rms nfields offset w1 Tc w1 R1_51 R1_81
    %keyboard
    Rcalc=zeros(nfields,size(w1,2));
    tau_ex=optpar(1);
    pb=optpar(2);
    pa=1-pb;
    kex=1/tau_ex; k_u=pb*kex; k_f=(1-pb)*kex;

    for k=1:nfields
        % we assume that A resonates at 0 [s^-1], without loss of generality
        dw=nu_0(k)*optpar(3)*2*pi;   	% [s^-1]
        Wa=0*2*pi;             		% Larmor frequ. [s^-1]
        Wb=dw;         			% Larmor frequ. [s^-1]
        Wsl=offset*2*pi;   			% Larmor frequ. of spin lock [s^-1]
        da=Wa-Wsl;				% offset of sl from A
        db=Wb-Wsl;				% offset of sl from B


        Rinf=optpar(3+k);

        for kk=1:length(w1)
          w1x=w1(kk);
          if k==1; R1=R1_51; end; if k==2; R1=R1_81; end

          R=-[Rinf+k_u   -k_f       da       0       0       0     ;
               -k_u    Rinf+k_f      0      db       0       0     ;
               -da         0     Rinf+k_u  -k_f     w1x      0     ;
               0          -db      -k_u  Rinf+k_f    0      w1x    ;
               0           0       -w1x      0    R1+k_u   -k_f    ;
               0           0         0     -w1x    -k_u   R1+k_f  ];
        % keyboard
         MAx0= pa; MBx0= pb; MAy0= 0; MBy0= 0; MAz0= 0; MBz0= 0;
         Mof0=[MAx0 MBx0 MAy0 MBy0 MAz0 MBz0]';

    % the following lines: rotate the magnetization previous to spin lock into the weff frame
    % a new Mof0 is otained: Mof0=[sin(thetaa)*pa sin(thetab)*pb 0 0 cos(thetaa)*pa cos(thetab)*pb];
    thetaa=atan(w1x/da);thetaa_degrees=thetaa*360/(2*pi);
    thetab=atan(w1x/db);thetab_degrees=thetab*360/(2*pi);
    MAxnew=sin(thetaa)*pa;
    MBxnew=sin(thetab)*pb;
    MAynew=MAy0;
    MBynew=MBy0;
    MAznew=cos(thetaa)*pa;
    MBznew=cos(thetab)*pb;
    Mof0=[MAxnew MBxnew MAynew MBynew MAznew MBznew]';

         Moft(1:6)=(expm3(R*Tc)*Mof0)';
         MAx=real(Moft(1))/pa;
         MAy=real(Moft(3))/pa;
         MAz=real(Moft(5))/pa;

         MA=sqrt(MAx^2+MAy^2+MAz^2); % for spin A, is equal to 1 if nothing happens (no relaxation)
         intrat(k,kk)=MA;
         Rcalc(k,kk)=(-1.0/Tc)*log(intrat(k,kk));
        end

    end

    if (size(Rcalc)==size(y))
        residual=sum(sum((y-Rcalc).^2));
        rms=sqrt(residual/(size(y,1)*size(y,2)));
    end


References
==========

The solution has been modified to use the from presented in:

    - Korzhnev, D. M., Orekhov, V. Y., and Kay, L. E. (2005).  Off-resonance R(1rho) NMR studies of exchange dynamics in proteins with low spin-lock fields:  an application to a Fyn SH3 domain.  I{J. Am. Chem. Soc.}, B{127}, 713-721. (U{DOI: 10.1021/ja0446855<http://dx.doi.org/10.1021/ja0446855>}).


Links
=====

More information on the NS R1rho 2-site model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/NS_R1rho_2-site>},
    - U{relax manual<http://www.nmr-relax.com/manual/The_NS_2_site_R1_rho_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#NS_R1rho_2-site>}.
"""

# Python module imports.
from numpy import array, einsum, float64, isfinite, log, min, multiply, sum
from numpy.ma import fix_invalid, masked_less

# relax module imports.
from lib.dispersion.matrix_exponential import matrix_exponential

# Repetitive calculations (to speed up calculations).
m_r1rho_prime = array([
    [-1,  0,  0,  0,  0,  0],
    [ 0, -1,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0,  0, -1,  0,  0],
    [ 0,  0,  0,  0, -1,  0],
    [ 0,  0,  0,  0,  0,  0]], float64)

m_wA = array([
    [ 0, -1,  0,  0,  0,  0],
    [ 1,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0]], float64)

m_wB = array([
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0, -1,  0],
    [ 0,  0,  0,  1,  0,  0],
    [ 0,  0,  0,  0,  0,  0]], float64)

m_w1 = array([
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0, -1,  0,  0,  0],
    [ 0,  1,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0, -1],
    [ 0,  0,  0,  0,  1,  0]], float64)

m_k_AB = array([
    [-1,  0,  0,  0,  0,  0],
    [ 0, -1,  0,  0,  0,  0],
    [ 0,  0, -1,  0,  0,  0],
    [ 1,  0,  0,  0,  0,  0],
    [ 0,  1,  0,  0,  0,  0],
    [ 0,  0,  1,  0,  0,  0]], float64)

m_k_BA = array([
    [ 0,  0,  0,  1,  0,  0],
    [ 0,  0,  0,  0,  1,  0],
    [ 0,  0,  0,  0,  0,  1],
    [ 0,  0,  0, -1,  0,  0],
    [ 0,  0,  0,  0, -1,  0],
    [ 0,  0,  0,  0,  0, -1]], float64)

m_R1 = array([
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0, -1,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0,  0],
    [ 0,  0,  0,  0,  0, -1]], float64)


def rr1rho_3d_2site_rankN(R1=None, r1rho_prime=None, dw=None, omega=None, offset=None, w1=None, k_AB=None, k_BA=None, relax_time=None):
    """Definition of the multidimensional 3D exchange matrix, of rank [NE][NS][NM][NO][ND][6][6].

    This code originates from the funNumrho.m file from the Skrynikov & Tollinger code (the sim_all.tar file https://gna.org/support/download.php?file_id=18404 attached to https://gna.org/task/?7712#comment5).


    @keyword R1:            The longitudinal, spin-lattice relaxation rate.
    @type R1:               numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword r1rho_prime:   The R1rho transverse, spin-spin relaxation rate in the absence of exchange.
    @type r1rho_prime:      numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword dw:            The chemical exchange difference between states A and B in rad/s.
    @type dw:               numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword omega:         The chemical shift for the spin in rad/s.
    @type omega:            numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword offset:        The spin-lock offsets for the data.
    @type offset:           numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword w1:            The spin-lock field strength in rad/s.
    @type w1:               numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword k_AB:          The forward exchange rate from state A to state B.
    @type k_AB:             float
    @keyword k_BA:          The reverse exchange rate from state B to state A.
    @type k_BA:             float
    @keyword relax_time:    The total relaxation time period for each spin-lock field strength (in seconds).
    @type relax_time:       numpy float array of rank [NE][NS][NM][NO][ND]
    @return:                The relaxation matrix.
    @rtype:                 numpy float array of rank [NE][NS][NM][NO][ND][6][6]
    """

    # Wa: The chemical shift offset of state A from the spin-lock. Larmor frequency [s^-1].
    Wa = omega
    # Wb: The chemical shift offset of state A from the spin-lock. Larmor frequency [s^-1].
    Wb = omega + dw

    # Population-averaged Larmor frequency [s^-1].
    #W = pA*Wa + pB*Wb

    # Offset of spin-lock from A.
    dA = Wa - offset

    # Offset of spin-lock from B.
    dB = Wb - offset

    # Offset of spin-lock from population-average.
    #d = W - offset

    # Alias to original parameter name.
    wA = dA
    wB = dB

    # Multiply and expand.
    mat_r1rho_prime = multiply.outer( r1rho_prime * relax_time, m_r1rho_prime )

    mat_wA = multiply.outer( wA * relax_time, m_wA )
    mat_wB = multiply.outer( wB * relax_time, m_wB )

    mat_w1 = multiply.outer( w1 * relax_time, m_w1 )

    mat_k_AB = multiply.outer( k_AB * relax_time, m_k_AB )
    mat_k_BA = multiply.outer( k_BA * relax_time, m_k_BA )

    mat_R1 = multiply.outer( R1 * relax_time, m_R1 )

    # Collect matrix.
    matrix = (mat_r1rho_prime + mat_wA + mat_wB
        + mat_w1 + mat_k_AB + mat_k_BA
        + mat_R1)

    # Return the matrix.
    return matrix


def ns_r1rho_2site(M0=None, M0_T=None, r1rho_prime=None, omega=None, offset=None, r1=0.0, pA=None, dw=None, kex=None, spin_lock_fields=None, relax_time=None, inv_relax_time=None, back_calc=None):
    """The 2-site numerical solution to the Bloch-McConnell equation for R1rho data.

    This function calculates and stores the R1rho values.


    @keyword M0:                This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
    @type M0:                   numpy float array of rank [NE][NS][NM][NO][ND][6][1]
    @keyword M0_T:              This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations, where the outer two axis has been swapped for efficient dot operations.
    @type M0_T:                 numpy float array of rank [NE][NS][NM][NO][ND][1][6]
    @keyword r1rho_prime:       The R1rho_prime parameter value (R1rho with no exchange).
    @type r1rho_prime:          numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword omega:             The chemical shift for the spin in rad/s.
    @type omega:                numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword offset:            The spin-lock offsets for the data.
    @type offset:               numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword r1:                The R1 relaxation rate.
    @type r1:                   numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword pA:                The population of state A.
    @type pA:                   float
    @keyword dw:                The chemical exchange difference between states A and B in rad/s.
    @type dw:                   numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword kex:               The kex parameter value (the exchange rate in rad/s).
    @type kex:                  float
    @keyword spin_lock_fields:  The R1rho spin-lock field strengths (in rad.s^-1).
    @type spin_lock_fields:     numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword relax_time:        The total relaxation time period for each spin-lock field strength (in seconds).
    @type relax_time:           numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword inv_relax_time:    The inverse of the relaxation time period for each spin-lock field strength (in inverse seconds).  This is used for faster calculations.
    @type inv_relax_time:       numpy float array of rank [NE][NS][NM][NO][ND]
    @keyword back_calc:         The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:            numpy float array of rank [NE][NS][NM][NO][ND]
    """

    # Once off parameter conversions.
    pB = 1.0 - pA
    k_BA = pA * kex
    k_AB = pB * kex

    # The matrix that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
    R_mat = rr1rho_3d_2site_rankN(R1=r1, r1rho_prime=r1rho_prime, dw=dw, omega=omega, offset=offset, w1=spin_lock_fields, k_AB=k_AB, k_BA=k_BA, relax_time=relax_time)

    # This matrix is a propagator that will evolve the magnetization with the matrix R.
    Rexpo_mat = matrix_exponential(R_mat)

    # Magnetization evolution.
    Rexpo_M0_mat = einsum('...ij, ...jk', Rexpo_mat, M0)

    # Magnetization evolution, which include all dimensions.
    MA_mat = einsum('...ij, ...jk', M0_T, Rexpo_M0_mat)[:, :, :, :, :, 0, 0]

    # Insert safe checks.
    if min(MA_mat) < 0.0:
        mask_min_MA_mat = masked_less(MA_mat, 0.0)
        # Fill with high values.
        MA_mat[mask_min_MA_mat.mask] = 1e100

    # Do back calculation.
    back_calc[:] = -inv_relax_time * log(MA_mat)

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(back_calc)):
        # Replaces nan, inf, etc. with fill value.
        fix_invalid(back_calc, copy=False, fill_value=1e100)


