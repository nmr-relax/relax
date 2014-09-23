"""Compare the synthetic cpmg_fit data to the relax solution.

To run this, type:

$ rm -f solution_ns_r1rho_2site.log; ../../../../../relax --tee solution_ns_r1rho_2site.log solution_ns_r1rho_2site.py
"""

# Python module imports.
from os import remove
from shutil import move

# relax module imports.
from lib.dispersion.variables import EXP_TYPE_R1RHO
from lib.nmr import frequency_to_ppm
from specific_analyses.relax_disp.data import generate_r20_key

# Create a data pipe.
pipe.create('R2eff', 'relax_disp')

# Create the spin system.
spin.create(res_name='X', res_num=14, spin_name='N')
spin.element('N', spin_id='@N')
spin.isotope('15N', spin_id='@N')

# The spectral data - experiment ID, R2eff file name, experiment type, spin ID string, spectrometer frequency in Hertz, relaxation time.
data = [
    ['600_MHz_nu1_50_Hz',  'T14_600_50.dsp',   ':14@N', 600e6,  50,  0.04],
    ['600_MHz_nu1_75_Hz',  'T14_600_75.dsp',   ':14@N', 600e6,  75,  0.04],
    ['600_MHz_nu1_100_Hz', 'T14_600_100.dsp',  ':14@N', 600e6,  100, 0.04],
    ['600_MHz_nu1_150_Hz', 'T14_600_150.dsp',  ':14@N', 600e6,  150, 0.04],
    ['600_MHz_nu1_200_Hz', 'T14_600_200.dsp',  ':14@N', 600e6,  200, 0.04],
    ['800_MHz_nu1_100_Hz', 'T14_800_100.dsp',  ':14@N', 800e6,  100, 0.04],
    ['800_MHz_nu1_200_Hz', 'T14_800_200.dsp',  ':14@N', 800e6,  200, 0.04],
    ['800_MHz_nu1_400_Hz', 'T14_800_400.dsp',  ':14@N', 800e6,  400, 0.04]
]
spin_lock_offset = {}
spin_lock_offset['600_MHz_nu1_50_Hz'] = [     340.0,     330.0,     320.0,     310.0,     300.0,     290.0,     280.0,     270.0,     260.0,     250.0,     240.0,     230.0,     220.0,     210.0,     200.0,     190.0,     180.0,     170.0,     160.0,     150.0,     140.0,     130.0,     120.0,     110.0,     100.0,      90.0,      80.0,      70.0,      60.0,      50.0,      40.0,      30.0,      20.0,      10.0,       0.0,     -10.0,     -20.0,     -30.0,     -40.0,     -50.0,     -60.0,     -70.0,     -80.0,     -90.0]
spin_lock_offset['600_MHz_nu1_75_Hz'] = [     340.0,     330.0,     320.0,     310.0,     300.0,     290.0,     280.0,     270.0,     260.0,     250.0,     240.0,     230.0,     220.0,     210.0,     200.0,     190.0,     180.0,     170.0,     160.0,     150.0,     140.0,     130.0,     120.0,     110.0,     100.0,      90.0,      80.0,      70.0,      60.0,      50.0,      40.0,      30.0,      20.0,      10.0,       0.0,     -10.0,     -20.0,     -30.0,     -40.0,     -50.0,     -60.0,     -70.0,     -80.0,     -90.0]
spin_lock_offset['600_MHz_nu1_100_Hz'] = [     340.0,     330.0,     320.0,     310.0,     300.0,     290.0,     280.0,     270.0,     260.0,     250.0,     240.0,     230.0,     220.0,     210.0,     200.0,     190.0,     180.0,     170.0,     160.0,     150.0,     140.0,     130.0,     120.0,     110.0,     100.0,      90.0,      80.0,      70.0,      60.0,      50.0,      40.0,      30.0,      20.0,      10.0,       0.0,     -10.0,     -20.0,     -30.0,     -40.0,     -50.0,     -60.0,     -70.0,     -80.0,     -90.0]
spin_lock_offset['600_MHz_nu1_150_Hz'] = [     385.0,     370.0,     355.0,     340.0,     325.0,     310.0,     295.0,     280.0,     265.0,     250.0,     235.0,     220.0,     205.0,     190.0,     175.0,     160.0,     145.0,     130.0,     115.0,     100.0,      85.0,      70.0,      55.0,      40.0,      25.0,      10.0,      -5.0,     -20.0,     -35.0,     -50.0,     -65.0,     -80.0,     -95.0,    -110.0,    -125.0,    -140.0,    -155.0,    -170.0,    -185.0]
spin_lock_offset['600_MHz_nu1_200_Hz'] = [     385.0,     370.0,     355.0,     340.0,     325.0,     310.0,     295.0,     280.0,     265.0,     250.0,     235.0,     220.0,     205.0,     190.0,     175.0,     160.0,     145.0,     130.0,     115.0,     100.0,      85.0,      70.0,      55.0,      40.0,      25.0,      10.0,      -5.0,     -20.0,     -35.0,     -50.0,     -65.0,     -80.0,     -95.0,    -110.0,    -125.0,    -140.0,    -155.0,    -170.0,    -185.0]
spin_lock_offset['800_MHz_nu1_100_Hz'] = [     780.0,     750.0,     720.0,     690.0,     660.0,     630.0,     600.0,     570.0,     540.0,     510.0,     480.0,     450.0,     420.0,     390.0,     360.0,     330.0,     300.0,     270.0,     240.0,     210.0,     180.0,     150.0,     120.0,      90.0,      60.0,      30.0,       0.0,     -30.0,     -60.0,     -90.0,    -120.0,    -150.0,    -180.0,    -210.0,    -240.0,    -270.0,    -300.0,    -330.0,    -360.0]
spin_lock_offset['800_MHz_nu1_200_Hz'] = [     960.0,     920.0,     880.0,     840.0,     800.0,     760.0,     720.0,     680.0,     640.0,     600.0,     560.0,     520.0,     480.0,     440.0,     400.0,     360.0,     320.0,     280.0,     240.0,     200.0,     160.0,     120.0,      80.0,      40.0,       0.0,     -40.0,     -80.0,    -120.0,    -160.0,    -200.0,    -240.0,    -280.0,    -320.0,    -360.0,    -400.0,    -440.0,    -480.0,    -520.0,    -560.0]
spin_lock_offset['800_MHz_nu1_400_Hz'] = [    1150.0,    1100.0,    1050.0,    1000.0,     950.0,     900.0,     850.0,     800.0,     750.0,     700.0,     650.0,     600.0,     550.0,     500.0,     450.0,     400.0,     350.0,     300.0,     250.0,     200.0,     150.0,     100.0,      50.0,       0.0,     -50.0,    -100.0,    -150.0,    -200.0,    -250.0,    -300.0,    -350.0,    -400.0,    -450.0,    -500.0,    -550.0,    -600.0,    -650.0,    -700.0,    -750.0]

# Loop over the files, reading in the data.
for id, file, spin_id, H_frq, field, relax_time in data:
    # Loop over each CPMG frequency.
    for offset in spin_lock_offset[id]:
        # The id.
        new_id = "%s_%.3f" % (id, offset)

        # Set the NMR field strength.
        spectrometer.frequency(id=new_id, frq=H_frq)

        # Set the relaxation dispersion experiment type.
        relax_disp.exp_type(spectrum_id=new_id, exp_type=EXP_TYPE_R1RHO)

        # Relaxation dispersion CPMG constant time delay T (in s).
        relax_disp.relax_time(spectrum_id=new_id, time=relax_time)

        # Set the relaxation dispersion spin-lock field strength (nu1).
        relax_disp.spin_lock_field(spectrum_id=new_id, field=field)

        # Set the spin-lock offset, converting back to ppm.
        relax_disp.spin_lock_offset(spectrum_id=new_id, offset=-frequency_to_ppm(frq=offset, B0=H_frq, isotope='15N'))

    # Read the R2eff data.
    relax_disp.r2eff_read_spin(id=id, file=file, dir='..', spin_id=spin_id, offset_col=1, data_col=2, error_col=3)

# Load the R1 data.
relax_data.read(ri_id='600MHz', ri_type='R1', frq=600e6, file='R1_600MHz.out', dir='..', mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
relax_data.read(ri_id='800MHz', ri_type='R1', frq=800e6, file='R1_800MHz.out', dir='..', mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

# Change the model.
relax_disp.select_model('NS R1rho 2-site')

# The R20 keys.
r20_600_key = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=600e6)
r20_800_key = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=800e6)

# Manually set the parameter values to the cpmg_fit solution.
spin_N = cdp.mol[0].res[0].spin[0]
spin_N.r2 = {
    r20_600_key:   7.360025311434811,
    r20_800_key:  12.144725123551275,
}
spin_N.pA = 0.939453418719417
spin_N.pB = 0.060546581280583
spin_N.kex = 345.382272267647522
spin_N.dw = 4.300343252657507
spin_N.ri_data['600MHz'] = 1.613234983209703
spin_N.ri_data['800MHz'] = 2.876934088364565

# Calculate.
minimise.calculate()
print("%-40s %20.15f" % ("relax chi2:", spin_N.chi2))
print("%-40s %20.15f" % ("cpmg_fit chi2 (corrections turned off):", 436.970448079015682))

# Minimisation.
minimise.grid_search(inc=7)
minimise.execute('simplex', constraints=True)

# Plot the dispersion curves.
relax_disp.plot_disp_curves(dir='.', num_points=100, extend=0, force=True)

# Save the results.
state.save('solution_ns_r1rho_2site', dir='.', compress_type=1, force=True)

# Cleanup.
print("\n\nMoving 'disp_14_N.agr' to 'solution_ns_r1rho_2site.agr'.")
move('disp_14_N.agr', 'solution_ns_r1rho_2site.agr')
print("Deleting 'grace2images.py'.")
remove('grace2images.py')
