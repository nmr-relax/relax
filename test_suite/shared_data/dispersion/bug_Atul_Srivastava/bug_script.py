"""Script for performing a full relaxation dispersion analysis using off-resonance R1rho-type data."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()

# Set up the data pipe.
#######################

DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_Atul_Srivastava'

# Load the sequence.
#sequence.read('fake_sequence.in', dir=DATA_PATH, res_num_col=1, res_name_col=2)
# Name the spins so they can be matched to the assignments.
#spin.name(name='N')

# Read the spins from a spectum file instead. This already contain the spin name.
spectrum.read_spins(file='2100_off_reso_R1rho.list', dir=DATA_PATH)

# Set the isotope information.
spin.isotope(isotope='15N')

# The spectral data - spectrum ID, peak list file name, spin-lock field strength (Hz), the spin-lock offset (ppm), the relaxation time (s), spectrometer frequency (Hz), and experimental error (RMSD of the base plane noise for each spectrum).
data = [
    ['ref_off_reso_R1rho',	'ref_off_reso_R1rho.list',	None,	150.87,	0.002,  900.21422558574e6, 90000.0],
    ['2100_off_reso_R1rho',	'2100_off_reso_R1rho.list',	1500.0,	141.01,	0.320,  900.21422558574e6, 90000.0],
    ['2728_off_reso_R1rho',	'2728_off_reso_R1rho.list',	1500.0,	147.89,	0.320,  900.21422558574e6, 90000.0],
    ['3357_off_reso_R1rho',	'3357_off_reso_R1rho.list',	1500.0,	154.78,	0.320,  900.21422558574e6, 90000.0],
    ['3985_off_reso_R1rho',	'3985_off_reso_R1rho.list',	1500.0,	161.66,	0.320,  900.21422558574e6, 90000.0],
    ['4614_off_reso_R1rho',	'4614_off_reso_R1rho.list',	1500.0,	168.55,	0.320,  900.21422558574e6, 90000.0],
    ['5242_off_reso_R1rho',	'5242_off_reso_R1rho.list',	1500.0,	175.43,	0.320,  900.21422558574e6, 90000.0],
    ['5871_off_reso_R1rho',	'5871_off_reso_R1rho.list',	1500.0,	182.32,	0.320,  900.21422558574e6, 90000.0],
    ['6500_off_reso_R1rho',	'6500_off_reso_R1rho.list',	1500.0,	189.21,	0.320,  900.21422558574e6, 90000.0]
]

# Loop over the spectra.
for id, file, field, offset, relax_time, H_frq, rmsd in data:
    # Load the peak intensities and set the errors.
    spectrum.read_intensities(file=file, dir=DATA_PATH, spectrum_id=id, int_method='height')
    spectrum.baseplane_rmsd(spectrum_id=id, error=rmsd)

    # Set the relaxation dispersion experiment type.
    relax_disp.exp_type(spectrum_id=id, exp_type='R1rho')

    # Set the relaxation dispersion spin-lock field strength (nu1).
    relax_disp.spin_lock_field(spectrum_id=id, field=field)

    # Set the spin-lock offset.
    relax_disp.spin_lock_offset(spectrum_id=id, offset=offset)

    # Set the relaxation times (in s).
    relax_disp.relax_time(spectrum_id=id, time=relax_time)

    # Set the NMR field strength of the spectrum.
    spectrometer.frequency(id=id, frq=H_frq)

# Load the R1 data.
relax_data.read(ri_id='900MHz', ri_type='R1', frq=900.21422558574e6, file='R1_relax.out', dir=DATA_PATH, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

# Clustering (only to be activated after an initial analysis without clustering).
#relax_disp.cluster(cluster_id='cluster', spin_id=':1-50')

# Read the chemical shift data.
#chemical_shift.read(file='chemical_shifts.list', dir=DATA_PATH)
chemical_shift.read(file='2100_off_reso_R1rho.list', dir=DATA_PATH)

# Deselect unresolved spins.
#deselect.read(file='unresolved', dir=DATA_PATH, res_num_col=1)