from math import pi
from lib.physical_constants import return_gyromagnetic_ratio

H_frq = 900.21422558574e6
print("The magnetic field strength as the proton frequency in MegaHertz: %3.2f" % (H_frq / 1.E6) )

xOBS_Hz = H_frq
B0_tesla =  xOBS_Hz / return_gyromagnetic_ratio(nucleus='1H') * 2.0 * pi
print("BO in Tesla: %3.2f" % B0_tesla)

yOBS_N15_Hz = abs( xOBS_Hz / return_gyromagnetic_ratio(nucleus='1H') *
return_gyromagnetic_ratio(nucleus='15N') )
print("The precess frequency for 15N in MHz: %3.2f" % (yOBS_N15_Hz / 1.E6) )

offset_Hz = 6500.

offset_ppm_N15 = offset_Hz / yOBS_N15_Hz * 1E6
print("The offset ppm: %3.2f" % (offset_ppm_N15) )

# Position of carrier.
yCAR_N15_ppm = 118.00
print("The center position of the carrier: %3.2f" % (yCAR_N15_ppm) )

print ("The offset in Hz: %3.2f" % (offset_Hz))
omega_rf_ppm = yCAR_N15_ppm + offset_ppm_N15
print("The omega_rf in ppm: %3.2f" % (omega_rf_ppm) )
