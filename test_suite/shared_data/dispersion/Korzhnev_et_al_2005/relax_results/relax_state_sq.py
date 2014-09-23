"""Create a relax state file for the 1H and 15N SQ data.

To run this, type:

$ rm -f relax_state_sq.log; ../../../../../relax --tee relax_state_sq.log relax_state_sq.py
"""

# relax module imports.
from lib.dispersion.variables import EXP_TYPE_CPMG_SQ
from specific_analyses.relax_disp.data import return_param_key_from_data


# Create a data pipe.
pipe.create('R2eff', 'relax_disp')

# Create the spin system.
spin.create(res_name='Asp', res_num=9, spin_name='H')
spin.create(res_name='Asp', res_num=9, spin_name='N')
spin.isotope('1H', spin_id='@H')
spin.isotope('15N', spin_id='@N')

# Initialise the global data structures.
cdp.dispersion_points = 0
cdp.cpmg_frqs = {}
cdp.cpmg_frqs_list = []
cdp.exp_type = {}
cdp.exp_type_list = ['SQ CPMG']
cdp.relax_times = {}
cdp.relax_time_list = [500000]
cdp.spectrometer_frq = {}
cdp.spectrometer_frq_list = []
cdp.spectrometer_frq_count = 0
cdp.spectrum_ids = []

# Loop over the spin data.
for spin_label in ['hs', 'ns']:
    # Alias the spin container.
    spin_cont = cdp.mol[0].res[0].spin[0]
    if spin_label == 'ns':
        spin_cont = cdp.mol[0].res[0].spin[1]

    # Initialise the data structures.
    spin_cont.model = 'R2eff'
    spin_cont.r2eff = {}
    spin_cont.r2eff_err = {}
    spin_cont.intensities = {}

    # Loop over the spectrometer frequencies.
    for frq in [500, 600, 800]:
        # The file data.
        file_name = "../%s_%s.res" % (spin_label, frq)
        print("Reading the data from the file '%s'." % file_name)
        file = open(file_name)
        lines = file.readlines()
        file.close()

        # Loop over the dispersion points.
        for i in range(len(lines)):
            # Split up the line.
            row = lines[i].split()

            # Convert the data.
            cpmg_frq = float(row[0])
            r2eff = float(row[1])
            r2eff_err = float(row[2])

            # A key for the global data (the pseudo-spectrum ID).
            key = "%s_%s" % (frq, row[0])

            # Update the global data.
            if key not in cdp.spectrum_ids:
                # Add the spectrum ID.
                cdp.spectrum_ids.append(key)

                # Some fake intensity data.
                spin_cont.intensities[key] = 0.0

                # The dispersion point data.
                cdp.cpmg_frqs[key] = cpmg_frq
                if frq == 500:
                    cdp.cpmg_frqs_list.append(cpmg_frq)

                # The experiment type.
                cdp.exp_type[key] = cdp.exp_type_list[0]

                # The unused relaxation period time.
                cdp.relax_times[key] = cdp.relax_time_list[0]

                # The spectrometer frequency.
                frq_hz = frq * 1e6
                cdp.spectrometer_frq[key] = frq_hz
                if frq_hz not in cdp.spectrometer_frq_list:
                    cdp.spectrometer_frq_list.append(frq_hz)
                    cdp.spectrometer_frq_count += 1

                # The dispersion point count.
                if frq == 500:
                    cdp.dispersion_points += 1

            # The dispersion point key.
            key = return_param_key_from_data(exp_type=EXP_TYPE_CPMG_SQ, frq=frq*1e6, point=cpmg_frq)

            # Store the spin data.
            spin_cont.r2eff[key] = r2eff
            spin_cont.r2eff_err[key] = r2eff_err

# Save the state.
state.save('sq_state', force=True)
