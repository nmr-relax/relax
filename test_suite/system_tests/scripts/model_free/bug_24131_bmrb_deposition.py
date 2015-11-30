# Python module imports.
from os import sep

# relax imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Path of the files.
path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'

pipe.create('model_free_final', 'mf')
results.read(file='bug_24131_bmrb_deposition.bz2', dir=path)

spin.isotope(isotope='15N', spin_id='@N', force=True)
spin.isotope(isotope='15N', spin_id='@NE1', force=True)
spin.isotope(isotope='1H', spin_id='@H', force=True)
spin.isotope(isotope='1H', spin_id='@HE1', force=True)

spin.element(element='N', spin_id=':*@N*', force=True)
spin.element(element='H', spin_id=':*@H*', force=True)

relax_data.peak_intensity_type(ri_id='R1_600',type='height')
relax_data.peak_intensity_type(ri_id='R2_600',type='height')
relax_data.peak_intensity_type(ri_id='NOE_600',type='height')
relax_data.peak_intensity_type(ri_id='R1_750',type='height')
relax_data.peak_intensity_type(ri_id='R2_750',type='height')
relax_data.peak_intensity_type(ri_id='NOE_750',type='height')


relax_data.temp_calibration(ri_id='R1_600', method='methanol')
relax_data.temp_calibration(ri_id='R2_600', method='methanol')
relax_data.temp_calibration(ri_id='NOE_600', method='methanol')
relax_data.temp_calibration(ri_id='R1_750', method='methanol')
relax_data.temp_calibration(ri_id='R2_750', method='methanol')
relax_data.temp_calibration(ri_id='NOE_750', method='methanol')


relax_data.temp_control(ri_id='R1_600', method='single fid interleaving')
relax_data.temp_control(ri_id='R2_600', method='single fid interleaving')
relax_data.temp_control(ri_id='NOE_600', method='single fid interleaving')
relax_data.temp_control(ri_id='R1_750', method='single fid interleaving')
relax_data.temp_control(ri_id='R2_750', method='single fid interleaving')
relax_data.temp_control(ri_id='NOE_750', method='single fid interleaving')

molecule.type(mol_id='#1ogt-hkca_mol2', type='protein', force=True)
bmrb.thiol_state(state='free and disulfide bound')

bmrb.write(file=ds.tmpfile, dir=None, version='3.1', force=True)
