###############################################################################
#                                                                             #
# Copyright (C) 2000-2001 Nikolai Skrynnikov                                  #
# Copyright (C) 2000-2001 Martin Tollinger                                    #
# Copyright (C) 2010-2013 Paul Schanda (https://gna.org/users/pasa)           #
# Copyright (C) 2013 Mathilde Lescanne                                        #
# Copyright (C) 2013 Dominique Marion                                         #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""The numerical fit of 2-site Bloch-McConnell equations for CPMG-type experiments, the U{NS CPMG 2-site expanded<http://wiki.nmr-relax.com/NS_CPMG_2-site_expanded>} model.

Description
===========

This function is exact, just as the explicit Bloch-McConnell numerical treatments.  It comes from a Maple derivation based on the Bloch-McConnell equations.  It is much faster than the numerical Bloch-McConnell solution.  It was derived by Nikolai Skrynnikov and is provided with his permission.


Code origin
===========

The code originates as optimization function number 5 from the fitting_main_kex.py script from Mathilde Lescanne, Paul Schanda, and Dominique Marion (see U{http://thread.gmane.org/gmane.science.nmr.relax.devel/4138}, U{https://gna.org/task/?7712#comment2} and U{https://gna.org/support/download.php?file_id=18262}).

Links to the copyright licensing agreements from all authors are:

    - Nikolai Skrynnikov, U{http://article.gmane.org/gmane.science.nmr.relax.devel/4279},
    - Martin Tollinger, U{http://article.gmane.org/gmane.science.nmr.relax.devel/4276},
    - Paul Schanda, U{http://article.gmane.org/gmane.science.nmr.relax.devel/4271},
    - Mathilde Lescanne, U{http://article.gmane.org/gmane.science.nmr.relax.devel/4138},
    - Dominique Marion, U{http://article.gmane.org/gmane.science.nmr.relax.devel/4157}.


Code evolution
--------------

The complex path of the code from the original Maple to relax can be described as:

    - p3.analytical (Maple input text file at U{https://gna.org/task/?7712#comment8}),
    - Automatically generated FORTRAN,
    - Manually converted to Matlab by Nikolai (sim_all.tar at U{https://gna.org/task/?7712#comment5})
    - Manually converted to Python by Paul, Mathilde, and Dominique (fitting_main.py at U{https://gna.org/task/?7712#comment1})
    - Converted into Python code for relax (here).


Maple p3.analytical script
--------------------------

For reference, the original Maple script written by Nikolai for the expansion of the equations is::

    with(linalg):
    with(tensor):
    #Ka:=30;
    #Kb:=1200;
    #dW:=300;
    #N:=2;
    #tcp:=0.040/N;
    
    Ksym:=sqrt(Ka*Kb);
    #dX:=(Ka-Kb+I*dw)/2;	# Ra=Rb
    dX:=((Ra-Rb)+(Ka-Kb)+I*dw)/2;
    
    L:=([[-dX, Ksym], [Ksym, dX]]);
     
    # in the end everything is multiplied by exp(-0.5*(Ra+Rb+Ka+Kb)*(Tc+2*tpalmer))
    # where 0.5*(Ra+Rb) is the same as Rinf, and (Ka+Kb) is kex.
    
    y:=eigenvects(L);
    TP1:=array([[y[1][3][1][1],y[2][3][1][1]],[y[1][3][1][2],y[2][3][1][2]]]);
    iTP1:=inverse(TP1);
    P1:=array([[exp(y[1][1]*tcp/2),0],[0,exp(y[2][1]*tcp/2)]]);
    
    P1palmer:=array([[exp(y[1][1]*tpalmer),0],[0,exp(y[2][1]*tpalmer)]]);
    
    TP2:=map(z->conj(z),TP1);
    iTP2:=map(z->conj(z),iTP1);
    P2:=array([[exp(conj(y[1][1])*tcp),0],[0,exp(conj(y[2][1])*tcp)]]);
    
    P2palmer:=array([[exp(conj(y[1][1])*tpalmer),0],[0,exp(conj(y[2][1])*tpalmer)]]);
    
    cP1:=evalm(TP1&*P1&*iTP1);
    cP2:=evalm(TP2&*P2&*iTP2);
    
    cP1palmer:=evalm(TP1&*P1palmer&*iTP1);
    cP2palmer:=evalm(TP2&*P2palmer&*iTP2);
    
    Ps:=evalm(cP1&*cP2&*cP1);
    # Ps is symmetric; cf. simplify(Ps[1,2]-Ps[2,1]);
    Pspalmer:=evalm(cP2palmer&*cP1palmer);
    
    
    dummy:=array([[a,b],[b,c]]);
    x:=eigenvects(dummy);
    TG1:=array([[x[1][3][1][1],x[2][3][1][1]],[x[1][3][1][2],x[2][3][1][2]]]);
    iTG1:=inverse(TG1);
    G1:=array([[x[1][1]^(N/4),0],[0,x[2][1]^(N/4)]]);
    GG1:=evalm(TG1&*G1&*iTG1);
    GG2:=map(z->conj(z),GG1);
    
    cGG:=evalm(GG2&*Pspalmer&*GG1);
    
    #s0:=array([Kb, Ka]);
    s0:=array([sqrt(Kb),sqrt(Ka)]);	# accounts for exchange symmetrization
    st:=evalm(cGG&*s0);
    #obs:=(1/(Ka+Kb))*st[1];
    obs:=(sqrt(Kb)/(Ka+Kb))*st[1];  # accounts for exchange symmetrization
    
    obs1:=eval(obs,[a=Ps[1,1],b=Ps[1,2],c=Ps[2,2]]);
    #obs2:=simplify(obs1):
    
    print(obs1):
    
    cGGref:=evalm(Pspalmer);
    stref:=evalm(cGGref&*s0);
    obsref:=(sqrt(Kb)/(Ka+Kb))*stref[1];  # accounts for exchange symmetrization
    
    print(obsref):
    
    writeto(result_test):
    
    fortran([intensity=obs1, intensity_ref=obsref], optimized):


Matlab sim_all.tar funNikolai.m script
--------------------------------------

Also for reference, the Matlab code from Nikolai and Martin manually converted from the automatically generated FORTRAN from the previous script into the funNikolai.m file is::

    function residual = funNikolai(optpar)

    % extended Carver's equation derived via Maple, Ra-Rb = 0 by Skrynnikov
    
    global nu_0 x y Rcalc rms nfields
    global Tc
    
    Rcalc=zeros(nfields,size(x,2));
    
    tau_ex=optpar(1);
    pb=optpar(2);
    
    pa=1-pb;
    kex=1/tau_ex;
    Ka=kex*pb;
    Kb=kex*pa;
    
    nu_cpmg=x;
    tcp=1./(2*nu_cpmg);
    N=round(Tc./tcp);
    
    for k=1:nfields
        dw=2*pi*nu_0(k)*optpar(3);
        Rinf=optpar(3+k);
        
        t3 = i;
        t4 = t3*dw;
        t5 = Kb^2;
        t8 = 2*t3*Kb*dw;
        t10 = 2*Kb*Ka;
        t11 = dw^2;
        t14 = 2*t3*Ka*dw;
        t15 = Ka^2;
        t17 = sqrt(t5-t8+t10-t11+t14+t15);
        t21 = exp((-Kb+t4-Ka+t17)*tcp/4);
        t22 = 1/t17;
        t28 = exp((-Kb+t4-Ka-t17)*tcp/4);
        t31 = t21*t22*Ka-t28*t22*Ka;
        t33 = sqrt(t5+t8+t10-t11-t14+t15);
        t34 = Kb+t4-Ka+t33;
        t37 = exp((-Kb-t4-Ka+t33)*tcp/2);
        t39 = 1/t33;
        t41 = Kb+t4-Ka-t33;
        t44 = exp((-Kb-t4-Ka-t33)*tcp/2);
        t47 = t34*t37*t39/2-t41*t44*t39/2;
        t49 = Kb-t4-Ka-t17;
        t51 = t21*t49*t22;
        t52 = Kb-t4-Ka+t17;
        t54 = t28*t52*t22;
        t55 = -t51+t54;
        t60 = t37*t39*Ka-t44*t39*Ka;
        t62 = t31.*t47+t55.*t60/2;
        t63 = 1/Ka;
        t68 = -t52*t63*t51/2+t49*t63*t54/2;
        t69 = t62.*t68/2;
        t72 = t37*t41*t39;
        t76 = t44*t34*t39;
        t78 = -t34*t63*t72/2+t41*t63*t76/2;
        t80 = -t72+t76;
        t82 = t31.*t78/2+t55.*t80/4;
        t83 = t82.*t55/2;
        t88 = t52*t21*t22/2-t49*t28*t22/2;
        t91 = t88.*t47+t68.*t60/2;
        t92 = t91.*t88;
        t95 = t88.*t78/2+t68.*t80/4;
        t96 = t95.*t31;
        t97 = t69+t83;
        t98 = t97.^2;
        t99 = t92+t96;
        t102 = t99.^2;
        t108 = t62.*t88+t82.*t31;
        t112 = sqrt(t98-2*t99.*t97+t102+4*(t91.*t68/2+t95.*t55/2).*t108);
        t113 = t69+t83-t92-t96-t112;
        t115 = N/2;
        t116 = (t69/2+t83/2+t92/2+t96/2+t112/2).^t115;
        t118 = 1./t112;
        t120 = t69+t83-t92-t96+t112;
        t122 = (t69/2+t83/2+t92/2+t96/2-t112/2).^t115;
        t127 = 1./t108;
        t139 = 1/(Ka+Kb)*((-t113.*t116.*t118/2+t120.*t122.*t118/2)*Kb+(-t113.*t127.*t116.*t120.*t118/2+t120.*t127.*t122.*t113.*t118/2)*Ka/2);
        
        intensity0 = pa;                             % pA
        intensity = real(t139)*exp(-Tc*Rinf);        % that's "homogeneous" relaxation
        Rcalc(k,:)=(1/Tc)*log(intensity0./intensity); 
        
    end
    
    if (size(Rcalc)==size(y))
        residual=sum(sum((y-Rcalc).^2)); 
        rms=sqrt(residual/(size(y,1)*size(y,2)));
    end


Links
=====

More information on the NS CPMG 2-site expanded model can be found in the:

    - U{relax wiki<http://wiki.nmr-relax.com/NS_CPMG_2-site_expanded>},
    - U{relax manual<http://www.nmr-relax.com/manual/NS_2_site_expanded_CPMG_model.html>},
    - U{relaxation dispersion page of the relax website<http://www.nmr-relax.com/analyses/relaxation_dispersion.html#NS_CPMG_2-site_expanded>}.
"""

# Python module imports.
from numpy import exp, isfinite, fabs, power, log, min, sqrt, sum
from numpy.ma import fix_invalid, masked_where


def r2eff_ns_cpmg_2site_expanded(r20=None, pA=None, dw=None, dw_orig=None, kex=None, relax_time=None, inv_relax_time=None, tcp=None, back_calc=None, num_cpmg=None):
    """The 2-site numerical solution to the Bloch-McConnell equation using complex conjugate matrices.

    This function calculates and stores the R2eff values.


    @keyword r20:               The R2 value for both states A and B in the absence of exchange.
    @type r20:                  numpy float array of rank [NE][NS][[NM][NO][ND]
    @keyword pA:                The population of state A.
    @type pA:                   float
    @keyword dw:                The chemical exchange difference between states A and B in rad/s.
    @type dw:                   numpy float array of rank [NE][NS][[NM][NO][ND]
    @keyword dw_orig:           The chemical exchange difference between states A and B in ppm. This is only for faster checking of zero value, which result in no exchange.
    @type dw_orig:              numpy float array of rank-1
    @keyword kex:               The kex parameter value (the exchange rate in rad/s).
    @type kex:                  float
    @keyword relax_time:        The total relaxation time period (in seconds).
    @type relax_time:           numpy float array of rank [NE][NS][[NM][NO][ND]
    @keyword inv_relax_time:    The inverse of the total relaxation time period (in inverse seconds).
    @type inv_relax_time:       numpy float array of rank [NE][NS][[NM][NO][ND]
    @keyword tcp:               The tau_CPMG times (1 / 4.nu1).
    @type tcp:                  numpy float array of rank [NE][NS][[NM][NO][ND]
    @keyword back_calc:         The array for holding the back calculated R2eff values.  Each element corresponds to one of the CPMG nu1 frequencies.
    @type back_calc:            numpy float array of rank [NE][NS][[NM][NO][ND]
    @keyword num_cpmg:          The array of numbers of CPMG blocks.
    @type num_cpmg:             numpy int16 array of rank [NE][NS][[NM][NO][ND]
    """

    # Flag to tell if values should be replaced if math function is violated.
    t_dw_zero = False

    # Catch parameter values that will result in no exchange, returning flat R2eff = R20 lines (when kex = 0.0, k_AB = 0.0).
    if pA == 1.0 or kex == 0.0:
        back_calc[:] = r20
        return

    # Test if dw is zero. Wait for replacement, since this is spin specific.
    if min(fabs(dw_orig)) == 0.0:
        t_dw_zero = True
        mask_dw_zero = masked_where(dw == 0.0, dw)

    # Once off parameter conversions.
    pB = 1.0 - pA
    k_BA = pA * kex
    k_AB = pB * kex


    # Repeditive calculations.
    half_tcp = 0.5 * tcp
    k_AB_plus_k_BA = k_AB + k_BA
    k_BA_minus_k_AB = k_BA - k_AB

    # The expansion factors (in numpy array form for all dispersion points).
    t3 = 1.j
    t4 = t3 * dw
    two_t4 = 2.0 * t4
    t5 = k_BA**2
    t8 = two_t4 * k_BA
    t10 = 2.0 * k_BA * k_AB
    t11 = dw**2
    t14 = two_t4 * k_AB
    t15 = k_AB**2
    t5_t10_t11_t15 = t5 + t10 - t11 + t15
    t8_t14 = t8 - t14
    t17 = sqrt(t5_t10_t11_t15 - t8_t14)

    k_AB_plus_k_BA_minus_t4 = k_AB_plus_k_BA - t4
    t21 = exp((t17 - k_AB_plus_k_BA_minus_t4) * half_tcp)
    t22 = 1.0/t17
    t28 = exp(-(t17 + k_AB_plus_k_BA_minus_t4) * half_tcp)
    t31 = t22*k_AB * (t21 - t28)
    t33 = sqrt(t5_t10_t11_t15 + t8_t14)

    k_AB_plus_k_BA_plus_t4 = k_AB_plus_k_BA + t4
    k_BA_minus_k_AB_plus_t4 = k_BA_minus_k_AB + t4
    t34 = k_BA_minus_k_AB_plus_t4 + t33
    t37 = exp((t33 - k_AB_plus_k_BA_plus_t4) * tcp)
    t39 = 1.0/t33
    t41 = k_BA_minus_k_AB_plus_t4 - t33
    t44 = exp(-(t33 + k_AB_plus_k_BA_plus_t4) * tcp)
    t47 = 0.5*t39 * (t34*t37 - t41*t44)

    k_BA_minus_k_AB_minus_t4 = k_BA_minus_k_AB - t4
    t49 = k_BA_minus_k_AB_minus_t4 - t17
    t51 = t21 * t49 * t22
    t52 = k_BA_minus_k_AB_minus_t4 + t17
    t54 = t28 * t52 * t22
    t55 = -t51 + t54
    t60 = 0.5*t39*k_AB * (t37 - t44)
    t62 = t31*t47 + t55*t60
    t63 = 1.0/k_AB
    t68 = 0.5*t63 * (t49*t54 - t52*t51)
    t69 = 0.5*t62 * t68
    t72 = t37 * t41 * t39
    t76 = t44 * t34 * t39
    t78 = 0.5*t63 * (t41*t76 - t34*t72)
    t80 = 0.5 * (t76 - t72)
    t82 = 0.5 * (t31*t78 + t55*t80)
    t83 = t82 * t55/2.0
    t88 = 0.5 * t22 * (t52*t21 - t49*t28)
    t91 = t88 * t47 + t68*t60
    t92 = t91 * t88
    t95 = 0.5 * (t88*t78 + t68*t80)
    t96 = t95 * t31
    t97 = t69 + t83
    t98 = t97**2
    t99 = t92 + t96
    t102 = t99**2
    t108 = t62 * t88 + t82 * t31
    t112 = sqrt(t98 - 2.0 * t99 * t97 + t102 + 2.0 * (t91 * t68 + t95 * t55) * t108)
    t97_t99 = t97 + t99
    t97_nt99 = t97 - t99
    t113 = t97_nt99 - t112
    t115 = num_cpmg
    t116 = power(0.5*(t97_t99 + t112), t115)
    t118 = 1.0/t112
    t120 = t97_nt99 + t112
    t122 = power(0.5*(t97_t99 - t112), t115)
    t127 = 0.5/t108
    t120_t122 = t120*t122
    t139 = 0.5/(k_AB + k_BA) * ((t120_t122 - t113*t116)*t118*k_BA + (t120_t122 - t116*t120)*t127*t113*t118*k_AB)

    # Calculate the initial and final peak intensities.
    intensity0 = pA
    intensity = t139.real * exp(-relax_time * r20)

    # The magnetisation vector.
    Mx = intensity / intensity0

    # Calculate the R2eff using a two-point approximation, i.e. assuming that the decay is mono-exponential, and store it for each dispersion point.
    back_calc[:] = -inv_relax_time * log(Mx)

    # Replace data in array.
    # If dw is zero.
    if t_dw_zero:
        back_calc[mask_dw_zero.mask] = r20[mask_dw_zero.mask]

    # Catch errors, taking a sum over array is the fastest way to check for
    # +/- inf (infinity) and nan (not a number).
    if not isfinite(sum(back_calc)):
        # Replaces nan, inf, etc. with fill value.
        fix_invalid(back_calc, copy=False, fill_value=1e100)
