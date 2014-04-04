"""Compare the synthetic cpmg_fit data to the relax solution.

To run this, type:

$ rm -f solution.log; ../../../../../relax --tee solution.log solution.py
"""

# relax module imports.
from lib.nmr import frequency_to_ppm
from specific_analyses.relax_disp.data import generate_r20_key
from specific_analyses.relax_disp.variables import EXP_TYPE_R1RHO


# Create a data pipe.
pipe.create('R2eff', 'relax_disp')

# Create the spin system.
spin.create(res_name='X', res_num=1, spin_name='N')
spin.element('N', spin_id='@N')
spin.isotope('15N', spin_id='@N')

# The spectral data - experiment ID, R2eff file name, spectrometer frequency in Hertz, spin-lock field strength, relaxation time.
data = [
    ['600_MHz_50',     '600_MHz_50.res',     600e6,  50,   0.04],
    ['600_MHz_75',     '600_MHz_75.res',     600e6,  75,   0.04],
    ['600_MHz_100',    '600_MHz_100.res',    600e6,  100,  0.04],
    ['600_MHz_200',    '600_MHz_200.res',    600e6,  200,  0.04],
    ['600_MHz_300',    '600_MHz_300.res',    600e6,  300,  0.04],
    ['600_MHz_400',    '600_MHz_400.res',    600e6,  400,  0.04],
    ['600_MHz_500',    '600_MHz_500.res',    600e6,  500,  0.04],
    ['600_MHz_1000',   '600_MHz_1000.res',   600e6,  1000, 0.04],
    ['600_MHz_1500',   '600_MHz_1500.res',   600e6,  1500, 0.04],
    ['600_MHz_2000',   '600_MHz_2000.res',   600e6,  2000, 0.04],
    ['600_MHz_2500',   '600_MHz_2500.res',   600e6,  2500, 0.04],
    ['600_MHz_3000',   '600_MHz_3000.res',   600e6,  3000, 0.04],
    ['600_MHz_3500',   '600_MHz_3500.res',   600e6,  3500, 0.04],
    ['600_MHz_4000',   '600_MHz_4000.res',   600e6,  4000, 0.04],
    ['600_MHz_4500',   '600_MHz_4500.res',   600e6,  4500, 0.04],
    ['600_MHz_5000',   '600_MHz_5000.res',   600e6,  5000, 0.04],
    ['600_MHz_5500',   '600_MHz_5500.res',   600e6,  5500, 0.04],
    ['600_MHz_6000',   '600_MHz_6000.res',   600e6,  6000, 0.04],
    ['800_MHz_50',     '800_MHz_50.res',     800e6,  50,   0.04],
    ['800_MHz_75',     '800_MHz_75.res',     800e6,  75,   0.04],
    ['800_MHz_100',    '800_MHz_100.res',    800e6,  100,  0.04],
    ['800_MHz_200',    '800_MHz_200.res',    800e6,  200,  0.04],
    ['800_MHz_300',    '800_MHz_300.res',    800e6,  300,  0.04],
    ['800_MHz_400',    '800_MHz_400.res',    800e6,  400,  0.04],
    ['800_MHz_500',    '800_MHz_500.res',    800e6,  500,  0.04],
    ['800_MHz_1000',   '800_MHz_1000.res',   800e6,  1000, 0.04],
    ['800_MHz_1500',   '800_MHz_1500.res',   800e6,  1500, 0.04],
    ['800_MHz_2000',   '800_MHz_2000.res',   800e6,  2000, 0.04],
    ['800_MHz_2500',   '800_MHz_2500.res',   800e6,  2500, 0.04],
    ['800_MHz_3000',   '800_MHz_3000.res',   800e6,  3000, 0.04],
    ['800_MHz_3500',   '800_MHz_3500.res',   800e6,  3500, 0.04],
    ['800_MHz_4000',   '800_MHz_4000.res',   800e6,  4000, 0.04],
    ['800_MHz_4500',   '800_MHz_4500.res',   800e6,  4500, 0.04],
    ['800_MHz_5000',   '800_MHz_5000.res',   800e6,  5000, 0.04],
    ['800_MHz_5500',   '800_MHz_5500.res',   800e6,  5500, 0.04],
    ['800_MHz_6000',   '800_MHz_6000.res',   800e6,  6000, 0.04]
]
offsets = []
for i in range(81):
    offsets.append(i * 25.0 - 1000.0)

# Loop over the files, reading in the data.
for id, file, H_frq, field, relax_time in data:
    # Loop over each offset.
    for offset in offsets:
        # The id.
        new_id = "%s_%.3i" % (id, offset)

        # Set the NMR field strength.
        spectrometer.frequency(id=new_id, frq=H_frq)

        # Set the relaxation dispersion experiment type.
        relax_disp.exp_type(spectrum_id=new_id, exp_type='R1rho')

        # Relaxation dispersion constant time delay T (in s).
        relax_disp.relax_time(spectrum_id=new_id, time=relax_time)

        # Set the spin-lock field strength.
        relax_disp.spin_lock_field(spectrum_id=new_id, field=field)

        # Set the offset.
        relax_disp.spin_lock_offset(spectrum_id=new_id, offset=-frequency_to_ppm(frq=offset, B0=H_frq, isotope='15N'))

    # Read the R2eff data.
    relax_disp.r2eff_read_spin(id=id, file=file, dir='..', spin_id=':1', offset_col=6, data_col=10, error_col=9)

# Load the R1 data.
relax_data.read(ri_id='600MHz', ri_type='R1', frq=600e6, file='R1_600MHz.out', dir='..', mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)
relax_data.read(ri_id='800MHz', ri_type='R1', frq=800e6, file='R1_800MHz.out', dir='..', mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

# Change the model.
relax_disp.select_model('NS R1rho 3-site linear')

# The R20 keys.
r20_600_key = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=600e6)
r20_800_key = generate_r20_key(exp_type=EXP_TYPE_R1RHO, frq=800e6)

# Manually set the parameter values.
spin = cdp.mol[0].res[0].spin[0]
spin.r2 = {
    r20_600_key:   8.000284037933310,
    r20_800_key:   9.000296050530716,
}
spin.pA = 0.850029879276267
spin.pB = 0.049922261890898
spin.pC = 0.100047858832835
spin.kex_AB = 500.991549690434681
spin.kex_AC = 0.0
spin.kex_BC = 2003.189830166320235
spin.dw_AB = -2.991465198310455
spin.dw_AC =  8.006033548997912
spin.dw_BC = spin.dw_AC - spin.dw_AB

# Calculate.
calc()
print("%-40s %20.15f" % ("chi2:", spin.chi2))

# Minimisation.
#minimise('simplex', constraints=True)

# Plot the dispersion curves.
relax_disp.plot_disp_curves(dir='.', num_points=100, extend=0, force=True)

# Save the results.
state.save('state', dir='.', compress_type=1, force=True)
