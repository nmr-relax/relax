"""Simulate relaxation curves for an on resonance R1rho-type experiment using the M61 model.

This is the Meiboom 1961 model for 2-site fast exchange.  The equation is:

                       phi_ex * kex
    R1rho = R1rho' + ----------------- ,
                     kex^2 + omega_e^2

where R1rho' is the R1rho value in the absence of exchange,

    phi_ex = pA * pB * delta_omega^2 ,

kex is the chemical exchange rate constant, pA and pB are the populations of states A and B, delta_omega is the chemical shift difference between the two states (in rad/s), and omega_e is the effective field in the rotating frame.

To run the script, simply type:

$ ../../../../relax generate.py
"""

# Python module imports.
from math import exp, pi

# relax module imports.
from lib.software.sparky import write_list


# Setup for 2 spin systems.
i0 = [100000.0, 20000.0]    # Initial peak intensities.
times = [0.00, 0.01, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.15]    # The relaxation delay times in seconds.
spin_lock = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000]    # The spin-lock field strengths in Hz.
r1rho_prime = [2.25, 24.0]    # The R1rho' value per spin.
pA = 0.7
kex = 1000.0
delta_omega = [1.0, 2.0]    # The chemical shift difference in ppm.
frq = -81.1177503272

# Setup for the Sparky peak list.
res_names = ['Trp', 'Trp']
res_nums = [1, 1]
atom1_names = ['N', 'NE1']
atom2_names = ['HN', 'HE1']
w1 = [122.454, 111.978]
w2 = [8.397, 8.720]

# Loop over the spin-lock fields.
for spin_lock_index in range(len(spin_lock)):
    # Loop over the relaxation times.
    for time_index in range(len(times)):
        # Loop over the spins.
        intensities = []
        for spin_index in range(len(r1rho_prime)):
            # Phi of exchange.
            phi_ex = pA * (1.0 - pA) * (delta_omega[spin_index]*frq*2*pi)**2

            # The rate.
            rx = r1rho_prime[spin_index] + (phi_ex * kex) / (kex**2 + (2*pi*spin_lock[spin_lock_index])**2)

            # The peak intensity.
            intensities.append(i0[spin_index] * exp(-rx*times[time_index]))

            # Printout.
            if time_index == 8:
                print("Phi_ex:  %s" % phi_ex)
                print("Rex:  %s" % ((phi_ex * kex) / (kex**2 + (2*pi*spin_lock[spin_lock_index])**2)))
                print("Rate:  %s" % rx)
                print("Intensity:  %s\n" % intensities[spin_index])

        # Create a Sparky .list file.
        write_list(file_prefix='nu_%s_ncyc%s' % (spin_lock[spin_lock_index], time_index+1), dir=None, res_names=res_names, res_nums=res_nums, atom1_names=atom1_names, atom2_names=atom2_names, w1=w1, w2=w2, data_height=intensities)
