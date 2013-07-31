"""Simulate relaxation curves for an on resonance R1rho-type experiment using the M61 model.

This is the Meiboom 1961 model for on-resonance 2-site exchange with skewed populations (pA >> pB).  The equation is:

                                                  pA.pB.delta_omega^2.kex
    R1rho = R1*cos(theta) + R2*sin(theta) + -------------------------------------- ,
                                            kex^2 + pA.delta_omega^2 + omega_1^2

where R1rho' is the R1rho value in the absence of exchange, kex is the chemical exchange rate constant, pA and pB are the populations of states A and B, delta_omega is the chemical shift difference between the two states, and omega_1 = omega_e is the effective field in the rotating frame.

To run the script, simply type:

$ ../../../../relax generate.py --tee generate.log
"""

# Python module imports.
from math import exp, pi
from numpy import array

# relax module imports.
from lib.software.sparky import write_list


# Setup for 2 spin systems.
i0 = [[1e8, 1.5e8], [2e7, 2.5e7]]    # Initial peak intensities per spin and per field.
times = [0.0, 0.1]    # The relaxation delay times in seconds.
spin_lock = [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000]    # The spin-lock field strengths in Hz.
spin_lock_frq = 110.0
r1rho_prime = [[10.0, 15.0], [12.0, 18.0]]  # The R1rho' value per spin and per field.
r1 = [[1.0, 1.2], [1.1, 1.3]]    # The R1 value per spin and per field.
pA = 0.80
kex = 2000.0
delta_omega = [1.0, 2.0]    # The chemical shift difference in ppm.
frqs = [-50.6985939545, -81.1177503272]
frq_label = ['500MHz', '800MHz']

# Setup for the Sparky peak list.
res_names = ['Trp', 'Lys']
res_nums = [1, 2]
atom1_names = ['N', 'N']
atom2_names = ['HN', 'HN']
w1 = [122.454, 111.978]
w2 = [8.397, 8.720]

# Loop over the spectrometer frequencies.
for frq_index in range(len(frqs)):
    # Convert the dw values from ppm^2 to (rad/s)^2.
    frq2 = (2.0 * pi * frqs[frq_index])**2
    dw_scaled = array(delta_omega) * frq2

    # Loop over the spin-lock fields.
    for spin_lock_index in range(len(spin_lock)):
        # Loop over the relaxation times.
        for time_index in range(len(times)):
            # Loop over the spins.
            intensities = []
            for spin_index in range(len(r1rho_prime)):
                # The rate.
                nomen = pA**2 * (1.0 - pA) * (delta_omega[spin_index]*frqs[frq_index]*2*pi)**2 * kex
                denom = kex**2 + pA**2 * (delta_omega[spin_index]*frqs[frq_index]*2*pi)**2 + (2*pi*spin_lock[spin_lock_index])**2
                rx = r1rho_prime[spin_index] + nomen / denom
    
                # The peak intensity.
                intensities.append(i0[spin_index] * exp(-rx*times[time_index]))

            # Create a Sparky .list file.
            if time_index == 0 and spin_lock_index == 0:
                name = 'nu_%s_ref' % frq_label[frq_index]
            elif time_index == 0:
                name = None
            else:
                name = 'nu_%s_%s' % (frq_label[frq_index], spin_lock[spin_lock_index])
            if name:
                write_list(file_prefix=name, dir=None, res_names=res_names, res_nums=res_nums, atom1_names=atom1_names, atom2_names=atom2_names, w1=w1, w2=w2, data_height=intensities)
