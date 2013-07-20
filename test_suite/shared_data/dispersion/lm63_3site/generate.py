"""Simulate relaxation curves for the 'LM63 3-site' CPMG dispersion model.

This is the Luz and Meiboom 1963 model for fast 3-site exchange.  The equation is:

                   _3_
                   \    phi_ex_i   /     4 * nu_cpmg         /     ki      \ \ 
    R2eff = R20 +   >   -------- * | 1 - -----------  * tanh | ----------- | | .
                   /__     ki      \         ki              \ 4 * nu_cpmg / /
                   i=2

To run the script, simply type:

$ ../../../../relax generate.py --tee generate.log
"""

# Python module imports.
from math import exp, pi, tanh

# relax module imports.
from lib.software.sparky import write_list


# Setup for 2 spin systems.
i0 = [[100000000.0, 20000000.0], [150000000.0, 25000000.0]]    # Initial peak intensities.
times = [0.0, 0.4]    # The relaxation delay times in seconds.
cpmg_frq = [66.6666, 133.3333, 133.3333, 200.0, 266.6666, 333.3333, 400.0, 466.6666, 533.3333, 533.3333, 600.0, 666.6666, 733.3333, 800.0, 866.6666, 933.3333, 933.3333, 1000.0]    # The spin-lock field strengths in Hz.
r20 = [[12.0, 12.0], [15.0, 15.0]]   # The R20 value per spin and per field (the same per field to allow comparison to CPMGFit).
phi_ex_B = 0.5
phi_ex_C = 2.0
kB = 1500.0
kC = 2500.0
delta_omega = [1.0, 2.0]    # The chemical shift difference in ppm.
frqs = [-50.6985939545, -81.1177503272]
frq_label = ['500MHz', '800MHz']

# Setup for the Sparky peak list.
res_names = ['Trp', 'Trp']
res_nums = [1, 1]
atom1_names = ['N', 'NE1']
atom2_names = ['HN', 'HE1']
w1 = [122.454, 111.978]
w2 = [8.397, 8.720]

# Loop over the spectrometer frequencies.
for frq_index in range(len(frqs)):
    # Convert the phi_ex values from ppm^2 to (rad/s)^2.
    frq2 = frqs[frq_index]**2
    phi_ex_B_scaled = phi_ex_B * frq2
    phi_ex_C_scaled = phi_ex_C * frq2

    # Loop over the CPMG frequencies.
    for cpmg_frq_index in range(len(cpmg_frq)):
        # Loop over the relaxation times.
        for time_index in range(len(times)):
            # Loop over the spins.
            intensities = []
            for spin_index in range(len(r20)):
                # i == B.
                B_rate = phi_ex_B / kB * (1.0 - 4.0*cpmg_frq[cpmg_frq_index]/kB * tanh(kB / (4.0*cpmg_frq[cpmg_frq_index])))

                # i == C.
                C_rate = phi_ex_C / kC * (1.0 - 4.0*cpmg_frq[cpmg_frq_index]/kC * tanh(kC / (4.0*cpmg_frq[cpmg_frq_index])))

                # The rate.
                rx = r20[spin_index][frq_index] + B_rate + C_rate

                # The peak intensity.
                intensities.append(i0[frq_index][spin_index] * exp(-rx*times[time_index]))

            # Create a Sparky .list file.
            if time_index == 0 and cpmg_frq_index == 0:
                name = 'nu_%s_ref' % frq_label[frq_index]
            elif time_index == 0:
                name = None
            else:
                name = 'nu_%s_%s' % (frq_label[frq_index], cpmg_frq[cpmg_frq_index])
            if name:
                write_list(file_prefix=name, dir=None, res_names=res_names, res_nums=res_nums, atom1_names=atom1_names, atom2_names=atom2_names, w1=w1, w2=w2, data_height=intensities)
