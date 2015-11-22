###############################################################################
#                                                                             #
# Copyright (C) 2015 Troels E. Linnet                                         #
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
# relax module imports.
from status import Status; status = Status()
outdir = status.outdir

from os import sep

# Minimum: Just read the sequence data, but this misses a lot of information.
sequence.read(file='residues.txt', res_num_col=1, dir=outdir)

# Open the settings file
set_file = open(outdir + sep + "exp_settings.txt")
set_file_lines = set_file.readlines()

for line in set_file_lines:
    if "#" in line[0]:
        continue

    # Get data
    field, RF_field_strength_kHz, f_name = line.split()

    # Assign data
    spec_id = f_name
    relax_disp.exp_type(spectrum_id=spec_id, exp_type='R1rho')

    # Set the spectrometer frequency
    spectrometer.frequency(id=spec_id, frq=float(field), units='MHz')

    # Is in kHz, som convert to Hz
    #http://wiki.nmr-relax.com/Relax_disp.spin_lock_offset%2Bfield
    #http://www.nmr-relax.com/manual/relax_disp_spin_lock_field.html
    disp_frq = float(RF_field_strength_kHz)*1000

    # Set The spin-lock field strength, nu1, in Hz
    relax_disp.spin_lock_field(spectrum_id=spec_id, field=disp_frq)

    # Read the R2eff data
    relax_disp.r2eff_read(id=spec_id, file=f_name, dir=None, disp_frq=disp_frq, res_num_col=1, data_col=2, error_col=3)

    # Is this necessary? The time, in seconds, of the relaxation period.
    #relax_disp.relax_time(spectrum_id=spec_id, time=time_sl)


# Name the isotope for field strength scaling.
spin.isotope(isotope='15N')
relax_disp.select_model(model='R2eff')

# Plot data
relax_disp.plot_disp_curves(dir=outdir + sep + 'grace', y_axis='r2_eff', x_axis='disp', num_points=1000, extend_hz=500.0, extend_ppm=500.0, interpolate='disp', force=True)

state.save("temp_state", force=True, dir=outdir)