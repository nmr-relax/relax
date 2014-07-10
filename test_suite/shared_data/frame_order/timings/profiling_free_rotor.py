"""Script for profiling the pseudo-ellipse model.

The user functions below were obtained by running:

$ ./relax -sd Frame_order.test_cam_free_rotor | grep "relax>" > log

To profile, set the profiling flag in the 'relax' file.
"""

# Python module imports.
from numpy import array

# relax module imports.
from specific_analyses.frame_order.optimisation import target_fn_setup


# All the user functions from the Frame_order.test_cam_pseudo_ellipse system test until the first target function call.
pipe.create(pipe_name='frame order', pipe_type='frame order', bundle=None)
structure.read_pdb(file='1J7O_1st_NH.pdb', dir='/data/relax/branches/frame_order_cleanup/test_suite/shared_data/frame_order/cam/', read_mol=None, set_mol_name='N-dom', read_model=None, set_model_num=None, alt_loc=None, verbosity=1, merge=False)
structure.read_pdb(file='1J7P_1st_NH_rot.pdb', dir='/data/relax/branches/frame_order_cleanup/test_suite/shared_data/frame_order/cam/', read_mol=None, set_mol_name='C-dom', read_model=None, set_model_num=None, alt_loc=None, verbosity=1, merge=False)
structure.load_spins(spin_id='@N', mol_name_target=None, ave_pos=False)
structure.load_spins(spin_id='@H', mol_name_target=None, ave_pos=False)
spin.isotope(isotope='15N', spin_id='@N', force=False)
spin.isotope(isotope='1H', spin_id='@H', force=False)
interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True, pipe=None)
interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.041e-10, unit='meter')
interatom.unit_vectors(ave=True)
rdc.read(align_id='dy', file='rdc_dy.txt', dir='/data/relax/branches/frame_order_cleanup/test_suite/shared_data/frame_order/cam/free_rotor', data_type='D', spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4, sep=None, neg_g_corr=False, absolute=False)
pcs.read(align_id='dy', file='pcs_dy_subset.txt', dir='/data/relax/branches/frame_order_cleanup/test_suite/shared_data/frame_order/cam/free_rotor', spin_id_col=None, mol_name_col=1, res_num_col=2, res_name_col=None, spin_num_col=None, spin_name_col=5, data_col=6, error_col=7, sep=None, spin_id=None)
spectrometer.temperature(id='dy', temp=303)
spectrometer.frequency(id='dy', frq=900000000.0, units='Hz')
rdc.read(align_id='tb', file='rdc_tb.txt', dir='/data/relax/branches/frame_order_cleanup/test_suite/shared_data/frame_order/cam/free_rotor', data_type='D', spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4, sep=None, neg_g_corr=False, absolute=False)
pcs.read(align_id='tb', file='pcs_tb_subset.txt', dir='/data/relax/branches/frame_order_cleanup/test_suite/shared_data/frame_order/cam/free_rotor', spin_id_col=None, mol_name_col=1, res_num_col=2, res_name_col=None, spin_num_col=None, spin_name_col=5, data_col=6, error_col=7, sep=None, spin_id=None)
spectrometer.temperature(id='tb', temp=303)
spectrometer.frequency(id='tb', frq=900000000.0, units='Hz')
rdc.read(align_id='tm', file='rdc_tm.txt', dir='/data/relax/branches/frame_order_cleanup/test_suite/shared_data/frame_order/cam/free_rotor', data_type='D', spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4, sep=None, neg_g_corr=False, absolute=False)
pcs.read(align_id='tm', file='pcs_tm_subset.txt', dir='/data/relax/branches/frame_order_cleanup/test_suite/shared_data/frame_order/cam/free_rotor', spin_id_col=None, mol_name_col=1, res_num_col=2, res_name_col=None, spin_num_col=None, spin_name_col=5, data_col=6, error_col=7, sep=None, spin_id=None)
spectrometer.temperature(id='tm', temp=303)
spectrometer.frequency(id='tm', frq=900000000.0, units='Hz')
rdc.read(align_id='er', file='rdc_er.txt', dir='/data/relax/branches/frame_order_cleanup/test_suite/shared_data/frame_order/cam/free_rotor', data_type='D', spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4, sep=None, neg_g_corr=False, absolute=False)
pcs.read(align_id='er', file='pcs_er_subset.txt', dir='/data/relax/branches/frame_order_cleanup/test_suite/shared_data/frame_order/cam/free_rotor', spin_id_col=None, mol_name_col=1, res_num_col=2, res_name_col=None, spin_num_col=None, spin_name_col=5, data_col=6, error_col=7, sep=None, spin_id=None)
spectrometer.temperature(id='er', temp=303)
spectrometer.frequency(id='er', frq=900000000.0, units='Hz')
script(file='/data/relax/branches/frame_order_cleanup/test_suite/shared_data/frame_order/cam/tensors.py', dir=None)
align_tensor.init(tensor='Dy N-dom', align_id='dy', domain=None, params=(0.000622191953772, 1.35210609663e-05, -0.000133742852942, 0.000756743581636, 0.000550729840729), scale=1.0, angle_units='deg', param_types=2, errors=False)
align_tensor.init(tensor='Dy N-dom', align_id='dy', domain=None, params=(2.35766523882e-05, 2.51785772774e-05, 1.99369755031e-05, 1.86674275393e-05, 2.01343581166e-05), scale=1.0, angle_units='deg', param_types=2, errors=True)
align_tensor.init(tensor='Tb N-dom', align_id='tb', domain=None, params=(0.000617222650166, -0.000438128542649, -0.000375477068228, 0.000760687126774, 0.00034129025543), scale=1.0, angle_units='deg', param_types=2, errors=False)
align_tensor.init(tensor='Tb N-dom', align_id='tb', domain=None, params=(1.63152405109e-05, 1.86581336167e-05, 1.34361351013e-05, 1.46648001703e-05, 1.76633948194e-05), scale=1.0, angle_units='deg', param_types=2, errors=True)
align_tensor.init(tensor='Tm N-dom', align_id='tm', domain=None, params=(-0.000385660891266, 0.000325292994524, 0.000318318888621, -0.00044409190064, -0.000473507384479), scale=1.0, angle_units='deg', param_types=2, errors=False)
align_tensor.init(tensor='Tm N-dom', align_id='tm', domain=None, params=(1.47916817671e-05, 1.81460089395e-05, 1.27148330285e-05, 1.54915569205e-05, 1.55953362766e-05), scale=1.0, angle_units='deg', param_types=2, errors=True)
align_tensor.init(tensor='Er N-dom', align_id='er', domain=None, params=(-0.000187529356988, 0.000130813961653, 7.14700966617e-05, -0.000264275852243, -0.000343164086618), scale=1.0, angle_units='deg', param_types=2, errors=False)
align_tensor.init(tensor='Er N-dom', align_id='er', domain=None, params=(1.88459382279e-05, 1.66197299895e-05, 1.69306486018e-05, 2.12500669486e-05, 1.96610327688e-05), scale=1.0, angle_units='deg', param_types=2, errors=True)
domain(id='N', spin_id='#N-dom')
domain(id='C', spin_id='#C-dom')
align_tensor.init(tensor='Dy C-dom', align_id='dy', domain=None, params=(0, 0, 0, 0, 0), scale=1.0, angle_units='deg', param_types=2, errors=False)
align_tensor.set_domain(tensor='Dy N-dom', domain='N')
align_tensor.set_domain(tensor='Dy C-dom', domain='C')
align_tensor.reduction(full_tensor='Dy N-dom', red_tensor='Dy C-dom')
align_tensor.init(tensor='Tb C-dom', align_id='tb', domain=None, params=(0, 0, 0, 0, 0), scale=1.0, angle_units='deg', param_types=2, errors=False)
align_tensor.set_domain(tensor='Tb N-dom', domain='N')
align_tensor.set_domain(tensor='Tb C-dom', domain='C')
align_tensor.reduction(full_tensor='Tb N-dom', red_tensor='Tb C-dom')
align_tensor.init(tensor='Tm C-dom', align_id='tm', domain=None, params=(0, 0, 0, 0, 0), scale=1.0, angle_units='deg', param_types=2, errors=False)
align_tensor.set_domain(tensor='Tm N-dom', domain='N')
align_tensor.set_domain(tensor='Tm C-dom', domain='C')
align_tensor.reduction(full_tensor='Tm N-dom', red_tensor='Tm C-dom')
align_tensor.init(tensor='Er C-dom', align_id='er', domain=None, params=(0, 0, 0, 0, 0), scale=1.0, angle_units='deg', param_types=2, errors=False)
align_tensor.set_domain(tensor='Er N-dom', domain='N')
align_tensor.set_domain(tensor='Er C-dom', domain='C')
align_tensor.reduction(full_tensor='Er N-dom', red_tensor='Er C-dom')
frame_order.select_model(model='free rotor')
frame_order.ref_domain(ref='N')
frame_order.pivot(pivot=array([ 39.482819802779524,   3.255542739800277,  14.265680648645716]), order=1, fix=False)
paramag.centre(pos=[35.934, 12.194, -4.206], atom_id=None, pipe=None, verbosity=1, fix=True, ave_pos=True, force=False)
frame_order.num_int_pts(num=2000)
value.set(val=-21.269217407269576, param='ave_pos_x', index=0, spin_id=None, error=False)
value.set(val=-3.122610661328414, param='ave_pos_y', index=0, spin_id=None, error=False)
value.set(val=-2.400652421655998, param='ave_pos_z', index=0, spin_id=None, error=False)
value.set(val=0.19740471457956135, param='ave_pos_beta', index=0, spin_id=None, error=False)
value.set(val=4.662231310426542, param='ave_pos_gamma', index=0, spin_id=None, error=False)
value.set(val=-0.6109933365884923, param='axis_alpha', index=0, spin_id=None, error=False)


# Set up the target function for direct calculation.
model, param_vector, scaling_matrix = target_fn_setup(sim_index=None, verbosity=1)

# Make repeated function calls.
N = 100
print("Function calls.")
for i in range(N):
    print(i)
    chi2 = model.func(param_vector)
