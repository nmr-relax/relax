###############################################################################
#                                                                             #
# Copyright (C) 2007-2011 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Python module imports.
from math import pi

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import diffusion_tensor, pipes
from relax_errors import RelaxError, RelaxParamSetError, RelaxUnknownParamCombError
from test_suite.unit_tests.base_classes import UnitTestCase


class Value_base_class(UnitTestCase):
    """Base class for the tests of both the 'prompt.value' and 'generic_fns.value' modules.

    This base class also contains many shared unit tests.
    """

    def setUp(self):
        """Set up for all the value unit tests."""

        # Add a consistency tests data pipe to the data store for testing consistency tests parameters.
        ds.add(pipe_name='ct', pipe_type='ct')

        # Add a model-free data pipe to the data store for testing model-free and diffusion parameters.
        ds.add(pipe_name='mf', pipe_type='mf')

        # Add a second model-free data pipe for copying tests.
        ds.add(pipe_name='mf2', pipe_type='mf')

        # Add a reduced spectral density mapping data pipe to the data store for testing RSDM parameters.
        ds.add(pipe_name='jw', pipe_type='jw')

        # Add a relaxation curve fitting data pipe to the data store for testing the associated parameters.
        ds.add(pipe_name='relax_fit', pipe_type='relax_fit')

        # Add a N-state model data pipe to the data store for testing the associated parameters.
        ds.add(pipe_name='n_state', pipe_type='N-state')

        # Set up some spins.
        self.set_up_spins(pipe_name='ct')
        self.set_up_spins(pipe_name='mf')
        self.set_up_spins(pipe_name='jw')
        self.set_up_spins(pipe_name='relax_fit')

        # Set up the N-state model.
        N = 4
        ds['n_state'].N = N
        ds['n_state'].alpha = [0.0] * N
        ds['n_state'].beta = [0.0] * N
        ds['n_state'].gamma = [0.0] * N


    def set_up_spins(self, pipe_name=None):
        """Function for setting up a few spins for the given pipe."""

        # Alias the pipe.
        pipe = pipes.get_pipe(pipe_name)

        # Name the first molecule.
        pipe.mol[0].name = 'Test mol'

        # Create the first residue and add some data to its spin container.
        pipe.mol[0].res[0].num = 1
        pipe.mol[0].res[0].name = 'Met'
        pipe.mol[0].res[0].spin[0].num = 111
        pipe.mol[0].res[0].spin[0].name = 'NH'

        # Add some more spins.
        pipe.mol[0].res[0].spin.add_item('Ca', 114)

        # Create a second residue.
        pipe.mol[0].res.add_item('Trp', 2)
        pipe.mol[0].res[1].spin[0].num = 112
        pipe.mol[0].res[1].spin[0].name = 'NH'




    ##################################
    # Consistency testing parameters #
    ##################################


    def test_set_ct_all_spins_j0(self):
        """Set the consistency testing parameter J(0) for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='j0', val=4.5e-9)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].j0, 4.5e-9)
        self.assertEqual(cdp.mol[0].res[1].spin[0].j0, 4.5e-9)


    def test_set_ct_all_spins_f_eta(self):
        """Set the consistency testing parameter F_eta for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='f_eta', val=2.3e-10)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].f_eta, 2.3e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].f_eta, 2.3e-10)


    def test_set_ct_all_spins_f_r2(self):
        """Set the consistency testing parameter F_R2 for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='f_r2', val=1.7e-12)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].f_r2, 1.7e-12)
        self.assertEqual(cdp.mol[0].res[1].spin[0].f_r2, 1.7e-12)


    def test_set_ct_all_spins_r(self):
        """Set the consistency testing bond length parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='Bond_length', val=1.04e-10)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].r, 1.04e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, 1.04e-10)


    def test_set_ct_all_spins_csa(self):
        """Set the consistency testing CSA parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='csa', val=-160e-6)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].csa, -160e-6)
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, -160e-6)


    def test_set_ct_all_spins_heteronucleus(self):
        """Set the consistency testing heteronucleus type for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='heteronucleus', val='13C')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].heteronuc_type, '13C')
        self.assertEqual(cdp.mol[0].res[1].spin[0].heteronuc_type, '13C')


    def test_set_ct_all_spins_orientation(self):
        """Set the consistency testing theta angle for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='orientation', val=17)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].orientation, 17)
        self.assertEqual(cdp.mol[0].res[1].spin[0].orientation, 17)


    def test_set_ct_all_spins_tc(self):
        """Set the consistency testing approximate correlation time for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='tc', val=10)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].tc, 10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].tc, 10)


    def test_set_ct_all_spins_diff_j0_f_eta_f_r2(self):
        """Set different consistency tests parameters J(0), F_eta, F_R2 for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param=['j0', 'f_eta', 'f_r2'], val=[6.4e-9, 3.5e-10, 2.3e-12])

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].j0, 6.4e-9)
        self.assertEqual(cdp.mol[0].res[0].spin[0].f_eta, 3.5e-10)
        self.assertEqual(cdp.mol[0].res[0].spin[0].f_r2, 2.3e-12)
        self.assertEqual(cdp.mol[0].res[1].spin[0].j0, 6.4e-9)
        self.assertEqual(cdp.mol[0].res[1].spin[0].f_eta, 3.5e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].f_r2, 2.3e-12)


    def test_set_ct_all_spins_same_j0_f_eta_f_r2(self):
        """Set consistency tests parameters J(0), F_eta, F_R2 for all spins to the same value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param=['j0', 'f_eta', 'f_r2'], val=1.9e-10)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].j0, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[0].spin[0].f_eta, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[0].spin[0].f_r2, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].j0, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].f_eta, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].f_r2, 1.9e-10)


    def test_set_ct_defaults_j0(self):
        """Set the consistency testing parameter J(0) to the default value (there is none!).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.assertRaises(RelaxParamSetError, self.value_fns.set, param='j0')


    def test_set_ct_defaults_f_eta(self):
        """Set the consistency tests parameter F_eta to the default value (there is none!).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.assertRaises(RelaxParamSetError, self.value_fns.set, param='f_eta')


    def test_set_ct_defaults_f_r2(self):
        """Set the consistency tests parameter F_R2 to the default value (there is none!).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.assertRaises(RelaxParamSetError, self.value_fns.set, param='f_r2')


    def test_set_ct_defaults_r(self):
        """Set the consistency testing bond length parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='bond-Length')

        # Test the parameter.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].r, 1.02e-10)
        self.assertAlmostEqual(cdp.mol[0].res[1].spin[0].r, 1.02e-10)


    def test_set_ct_defaults_csa(self):
        """Set the consistency testing CSA parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='csa')

        # Test the parameter.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].csa, -172e-6)
        self.assertAlmostEqual(cdp.mol[0].res[1].spin[0].csa, -172e-6)


    def test_set_ct_defaults_heteronucleus(self):
        """Set the consistency testing heteronucleus type to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='heteronucleus')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].heteronuc_type, '15N')
        self.assertEqual(cdp.mol[0].res[1].spin[0].heteronuc_type, '15N')


    def test_set_ct_defaults_orientation(self):
        """Set the consistency testing theta angle parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='orientation')

        # Test the parameter.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].orientation, 15.7)
        self.assertAlmostEqual(cdp.mol[0].res[1].spin[0].orientation, 15.7)


    def test_set_ct_defaults_tc(self):
        """Set the consistency testing approximate correlation time parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='tc')

        # Test the parameter.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].tc, 13 * 1e-9)
        self.assertAlmostEqual(cdp.mol[0].res[1].spin[0].tc, 13 * 1e-9)


    def test_set_ct_defaults_j0_f_eta_f_r2(self):
        """Set different consistency testing parameters J(0), F_eta, F_R2 to the default values (there are none!).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.assertRaises(RelaxParamSetError, self.value_fns.set, param=['j0', 'f_eta', 'f_r2'])


    def test_set_ct_single_spin_j0(self):
        """Set the consistency tests parameter J(0) for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='j0', val=4.5e-9, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'j0'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].j0, 4.5e-9)


    def test_set_ct_single_spin_f_eta(self):
        """Set the consistency tests parameter F_eta for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='f_eta', val=2.3e-10, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'f_eta'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].f_eta, 2.3e-10)


    def test_set_ct_single_spin_f_r2(self):
        """Set the consistency tests parameter F_R2 for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='f_r2', val=1.7e-12, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'f_r2'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].f_r2, 1.7e-12)


    def test_set_ct_single_spin_r(self):
        """Set the consistency tests bond length parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='Bond_length', val=1.04e-10, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'r'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, 1.04e-10)


    def test_set_ct_single_spin_csa(self):
        """Set the consistency tests CSA parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='csa', val=-160e-6, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'csa'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, -160e-6)


    def test_set_ct_single_spin_heteronucleus(self):
        """Set the consistency testing heteronucleus type for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='heteronucleus', val='13C', spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'heteronuc_type'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].heteronuc_type, '13C')


    def test_set_ct_single_spin_orientation(self):
        """Set the consistency tests theta angle parameter for a single spin.
        
        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """
        
        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='orientation', val=17, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'orientation'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].orientation, 17)


    def test_set_ct_single_spin_tc(self):
        """Set the consistency tests approximate correlation time parameter for a single spin.
        
        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """
        
        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param='tc', val=10, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'tc'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].tc, 10)


    def test_set_ct_single_spin_diff_j0_f_eta_f_r2(self):
        """Set different consistency tests parameters J(0), F_eta, F_R2 for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param=['j0', 'f_eta', 'f_r2'], val=[6.4e-9, 3.5e-10, 2.3e-12], spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'j0'))
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'f_eta'))
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'f_r2'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].j0, 6.4e-9)
        self.assertEqual(cdp.mol[0].res[1].spin[0].f_eta, 3.5e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].f_r2, 2.3e-12)


    def test_set_ct_single_spin_same_j0_f_eta_f_r2(self):
        """Set consistency tests parameters J(0), F_eta, F_R2 for a single spin to the same value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'ct'.
        pipes.switch('ct')

        # Set the parameter.
        self.value_fns.set(param=['j0', 'f_eta', 'f_r2'], val=1.9e-10, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'j0'))
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'f_eta'))
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'f_r2'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].j0, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].f_eta, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].f_r2, 1.9e-10)




    #####################################################
    # Diffusion tensor parameters (Model-free analysis) #
    #####################################################


    def test_set_mf_diff_sphere_default_tm(self):
        """Set the spherical diffusion tensor tm parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.value_fns.set(param='tm')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1e-8)


    def test_set_mf_diff_sphere_default_Diso(self):
        """Set the spherical diffusion tensor Diso parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.value_fns.set(param='Diso')

        # Test the parameter.
        self.assertAlmostEqual(cdp.diff_tensor.Diso, 1.666e7)


    def test_set_mf_diff_sphere_default_Da(self):
        """Try to set the spherical diffusion tensor Da parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Da')


    def test_set_mf_diff_sphere_default_Dr(self):
        """Try to set the spherical diffusion tensor Dr parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dr')


    def test_set_mf_diff_sphere_default_Dx(self):
        """Try to set the spherical diffusion tensor Dx parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dx')


    def test_set_mf_diff_sphere_default_Dy(self):
        """Try to set the spherical diffusion tensor Dy parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dy')


    def test_set_mf_diff_sphere_default_Dz(self):
        """Try to set the spherical diffusion tensor Dz parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dz')


    def test_set_mf_diff_sphere_default_Dpar(self):
        """Try to set the spherical diffusion tensor Dpar parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dpar')


    def test_set_mf_diff_sphere_default_Dper(self):
        """Try to set the spherical diffusion tensor Dper parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dper')


    def test_set_mf_diff_sphere_default_Dratio(self):
        """Try to set the spherical diffusion tensor Dratio parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dratio')


    def test_set_mf_diff_sphere_default_alpha(self):
        """Try to set the spherical diffusion tensor alpha parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='alpha')


    def test_set_mf_diff_sphere_default_beta(self):
        """Try to set the spherical diffusion tensor beta parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='beta')


    def test_set_mf_diff_sphere_default_gamma(self):
        """Try to set the spherical diffusion tensor gamma parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='gamma')


    def test_set_mf_diff_sphere_default_theta(self):
        """Try to set the spherical diffusion tensor theta parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='theta')


    def test_set_mf_diff_sphere_default_phi(self):
        """Try to set the spherical diffusion tensor phi parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='phi')


    def test_set_mf_diff_spheroid_default_tm(self):
        """Set the spheroidal diffusion tensor tm parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='tm')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1e-8)


    def test_set_mf_diff_spheroid_default_Diso(self):
        """Set the spheroidal diffusion tensor Diso parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='Diso')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1./(6*1.666e7))


    def test_set_mf_diff_spheroid_default_Da(self):
        """Set the spheroidal diffusion tensor Da parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='Da')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.Da, 0.0)


    def test_set_mf_diff_spheroid_default_Dr(self):
        """Set the spheroidal diffusion tensor Dr parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dr')


    def test_set_mf_diff_spheroid_default_Dx(self):
        """Set the spheroidal diffusion tensor Dx parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dx')


    def test_set_mf_diff_spheroid_default_Dy(self):
        """Set the spheroidal diffusion tensor Dy parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dy')


    def test_set_mf_diff_spheroid_default_Dz(self):
        """Set the spheroidal diffusion tensor Dz parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dz')


    def test_set_mf_diff_spheroid_default_Dpar(self):
        """Try to set the spheroidal diffusion tensor Dpar parameter to the default value (this should not be possible).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dpar')


    def test_set_mf_diff_spheroid_default_Dper(self):
        """Try to set the spheroidal diffusion tensor Dper parameter to the default value (this should not be possible).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dper')


    def test_set_mf_diff_spheroid_default_Dratio(self):
        """Set the spheroidal diffusion tensor Dratio parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='Dratio')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.Dratio, 1.0)


    def test_set_mf_diff_spheroid_default_alpha(self):
        """Try to set the spheroidal diffusion tensor alpha parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='alpha')


    def test_set_mf_diff_spheroid_default_beta(self):
        """Try to set the spheroidal diffusion tensor beta parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='beta')


    def test_set_mf_diff_spheroid_default_gamma(self):
        """Try to set the spheroidal diffusion tensor gamma parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='gamma')


    def test_set_mf_diff_spheroid_default_theta(self):
        """Set the spheroidal diffusion tensor theta parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='theta')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.theta, 0.0)


    def test_set_mf_diff_spheroid_default_phi(self):
        """Set the spheroidal diffusion tensor phi parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='phi')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.phi, 0.0)


    def test_set_mf_diff_spheroid_default_tm_Da(self):
        """Set the spheroidal diffusion tensor parameters {tm, Da} to the default values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['tm', 'Da'])

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1e-8)
        self.assertEqual(cdp.diff_tensor.Da, 0.0)


    def test_set_mf_diff_spheroid_default_Diso_Da(self):
        """Set the spheroidal diffusion tensor parameters {Diso, Da} to the default values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['Diso', 'Da'])

        # Test the parameter.
        self.assertAlmostEqual(cdp.diff_tensor.Diso, 1.666e7)
        self.assertEqual(cdp.diff_tensor.Da, 0.0)


    def test_set_mf_diff_spheroid_default_tm_Dratio(self):
        """Set the spheroidal diffusion tensor parameters {tm, Dratio} to the default values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['tm', 'Dratio'])

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1e-8)
        self.assertEqual(cdp.diff_tensor.Dratio, 1.0)


    def test_set_mf_diff_spheroid_default_Dpar_Dper(self):
        """Set the spheroidal diffusion tensor parameters {Dpar, Dper} to the default values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['Dpar', 'Dper'])

        # Test the parameter.
        self.assertAlmostEqual(cdp.diff_tensor.Dpar, 1.666e7)
        self.assertAlmostEqual(cdp.diff_tensor.Dper, 1.666e7)


    def test_set_mf_diff_spheroid_default_Dper_Dpar(self):
        """Set the spheroidal diffusion tensor parameters {Dper, Dpar} to the default values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['Dper', 'Dpar'])

        # Test the parameter.
        self.assertAlmostEqual(cdp.diff_tensor.Dper, 1.666e7)
        self.assertAlmostEqual(cdp.diff_tensor.Dpar, 1.666e7)


    def test_set_mf_diff_spheroid_default_Diso_Dratio(self):
        """Set the spheroidal diffusion tensor parameters {Diso, Dratio} to the default values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['Diso', 'Dratio'])

        # Test the parameter.
        self.assertAlmostEqual(cdp.diff_tensor.Diso, 1.666e7)
        self.assertEqual(cdp.diff_tensor.Dratio, 1.0)


    def test_set_mf_diff_spheroid_default_Dpar_Dratio(self):
        """Set the spheroidal diffusion tensor parameters {Dpar, Dratio} to the default values (this should not be possible).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.assertRaises(RelaxUnknownParamCombError, self.value_fns.set, param=['Dpar', 'Dratio'])


    def test_set_mf_diff_ellipsoid_default_tm(self):
        """Set the ellipsoidal diffusion tensor tm parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='tm')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1e-8)


    def test_set_mf_diff_ellipsoid_default_Diso(self):
        """Set the ellipsoidal diffusion tensor Diso parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='Diso')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1./(6*1.666e7))


    def test_set_mf_diff_ellipsoid_default_Da(self):
        """Set the ellipsoidal diffusion tensor Da parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='Da')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.Da, 0.0)


    def test_set_mf_diff_ellipsoid_default_Dr(self):
        """Set the ellipsoidal diffusion tensor Dr parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='Dr')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.Dr, 0.0)


    def test_set_mf_diff_ellipsoid_default_Dx(self):
        """Set the ellipsoidal diffusion tensor Dx parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dx')


    def test_set_mf_diff_ellipsoid_default_Dy(self):
        """Set the ellipsoidal diffusion tensor Dy parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dy')


    def test_set_mf_diff_ellipsoid_default_Dz(self):
        """Set the ellipsoidal diffusion tensor Dz parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dz')


    def test_set_mf_diff_ellipsoid_default_Dpar(self):
        """Try to set the ellipsoidal diffusion tensor Dpar parameter to the default value (this should not be possible).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dpar')


    def test_set_mf_diff_ellipsoid_default_Dper(self):
        """Try to set the ellipsoidal diffusion tensor Dper parameter to the default value (this should not be possible).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dper')


    def test_set_mf_diff_ellipsoid_default_Dratio(self):
        """Set the ellipsoidal diffusion tensor Dratio parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dratio')


    def test_set_mf_diff_ellipsoid_default_alpha(self):
        """Try to set the ellipsoidal diffusion tensor alpha parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='alpha')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.alpha, 0.0)


    def test_set_mf_diff_ellipsoid_default_beta(self):
        """Try to set the ellipsoidal diffusion tensor beta parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='beta')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.beta, 0.0)


    def test_set_mf_diff_ellipsoid_default_gamma(self):
        """Try to set the ellipsoidal diffusion tensor gamma parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='gamma')

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.gamma, 0.0)


    def test_set_mf_diff_ellipsoid_default_theta(self):
        """Set the ellipsoidal diffusion tensor theta parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='theta')


    def test_set_mf_diff_ellipsoid_default_phi(self):
        """Set the ellipsoidal diffusion tensor phi parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='phi')


    def test_set_mf_diff_ellipsoid_default_diff_tm_Da_Dr(self):
        """Set the ellipsoidal diffusion tensor parameters {tm, Da, Dr} to the default values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.4, 0, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['tm', 'Da', 'Dr'])

        # Test the parameters.
        self.assertEqual(cdp.diff_tensor.tm, 1e-8)
        self.assertEqual(cdp.diff_tensor.Da, 0.0)
        self.assertEqual(cdp.diff_tensor.Dr, 0.0)


    def test_set_mf_diff_ellipsoid_default_Diso_Da_Dr(self):
        """Set the ellipsoidal diffusion tensor parameters {Diso, Da, Dr} to the default values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.4, 0, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['Diso', 'Da', 'Dr'])

        # Test the parameters.
        self.assertAlmostEqual(cdp.diff_tensor.Diso, 1.666e7)
        self.assertEqual(cdp.diff_tensor.Da, 0.0)
        self.assertEqual(cdp.diff_tensor.Dr, 0.0)


    def test_set_mf_diff_ellipsoid_default_Dx_Dy_Dz(self):
        """Set the ellipsoidal diffusion tensor parameters {Dx, Dy, Dz} to the default values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.4, 0, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['Dx', 'Dy', 'Dz'])

        # Test the parameters.
        self.assertAlmostEqual(cdp.diff_tensor.Dx, 1.666e7)
        self.assertAlmostEqual(cdp.diff_tensor.Dy, 1.666e7)
        self.assertAlmostEqual(cdp.diff_tensor.Dz, 1.666e7)


    def test_set_mf_diff_ellipsoid_default_tm_Diso_Dr(self):
        """Try to set the ellipsoidal diffusion tensor parameters {tm, Diso, Dr} to the default values (this should not be possible).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.4, 0, 0, 0))

        # Set the parameters.
        self.assertRaises(RelaxUnknownParamCombError, self.value_fns.set, param=['tm', 'Diso', 'Dr'])


    def test_set_mf_diff_sphere_set_tm(self):
        """Set the spherical diffusion tensor tm parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.value_fns.set(param='tm', val=1e-8)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1e-8)


    def test_set_mf_diff_sphere_set_Diso(self):
        """Set the spherical diffusion tensor Diso parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.value_fns.set(param='Diso', val=5e7)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.Diso, 5e7)


    def test_set_mf_diff_sphere_set_Da(self):
        """Try to set the spherical diffusion tensor Da parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Da', val=2e6)


    def test_set_mf_diff_sphere_set_Dr(self):
        """Try to set the spherical diffusion tensor Dr parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dr', val=2e6)


    def test_set_mf_diff_sphere_set_Dx(self):
        """Try to set the spherical diffusion tensor Dx parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dx', val=2e6)


    def test_set_mf_diff_sphere_set_Dy(self):
        """Try to set the spherical diffusion tensor Dy parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dy', val=2e6)


    def test_set_mf_diff_sphere_set_Dz(self):
        """Try to set the spherical diffusion tensor Dz parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dz', val=2e6)


    def test_set_mf_diff_sphere_set_Dpar(self):
        """Try to set the spherical diffusion tensor Dpar parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dpar', val=2e6)


    def test_set_mf_diff_sphere_set_Dper(self):
        """Try to set the spherical diffusion tensor Dper parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dper', val=2e6)


    def test_set_mf_diff_sphere_set_Dratio(self):
        """Try to set the spherical diffusion tensor Dratio parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dratio', val=1.2)


    def test_set_mf_diff_sphere_set_alpha(self):
        """Try to set the spherical diffusion tensor alpha parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='alpha', val=pi/2)


    def test_set_mf_diff_sphere_set_beta(self):
        """Try to set the spherical diffusion tensor beta parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='beta', val=pi/2)


    def test_set_mf_diff_sphere_set_gamma(self):
        """Try to set the spherical diffusion tensor gamma parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='gamma', val=pi/2)


    def test_set_mf_diff_sphere_set_theta(self):
        """Try to set the spherical diffusion tensor theta parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='theta', val=pi/2)


    def test_set_mf_diff_sphere_set_phi(self):
        """Try to set the spherical diffusion tensor phi parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init(1e-9)

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='phi', val=pi/2)


    def test_set_mf_diff_spheroid_set_tm(self):
        """Set the spheroidal diffusion tensor tm parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='tm', val=1e-8)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1e-8)


    def test_set_mf_diff_spheroid_set_Diso(self):
        """Set the spheroidal diffusion tensor Diso parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='Diso', val=5e7)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1./(6*5e7))


    def test_set_mf_diff_spheroid_set_Da(self):
        """Set the spheroidal diffusion tensor Da parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='Da', val=1e6)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.Da, 1e6)


    def test_set_mf_diff_spheroid_set_Dr(self):
        """Set the spheroidal diffusion tensor Dr parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dr', val=0.2)


    def test_set_mf_diff_spheroid_set_Dx(self):
        """Set the spheroidal diffusion tensor Dx parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dx', val=1e6)


    def test_set_mf_diff_spheroid_set_Dy(self):
        """Set the spheroidal diffusion tensor Dy parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dy', val=1e6)


    def test_set_mf_diff_spheroid_set_Dz(self):
        """Set the spheroidal diffusion tensor Dz parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dz', val=1e6)


    def test_set_mf_diff_spheroid_set_Dpar(self):
        """Try to set the spheroidal diffusion tensor Dpar parameter (this should not be possible).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dpar', val=1e6)


    def test_set_mf_diff_spheroid_set_Dper(self):
        """Try to set the spheroidal diffusion tensor Dper parameter (this should not be possible).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dper', val=1e6)


    def test_set_mf_diff_spheroid_set_Dratio(self):
        """Set the spheroidal diffusion tensor Dratio parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='Dratio', val=1.2)

        # Test the parameter.
        self.assertAlmostEqual(cdp.diff_tensor.Dratio, 1.2)


    def test_set_mf_diff_spheroid_set_alpha(self):
        """Try to set the spheroidal diffusion tensor alpha parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='alpha', val=pi/2)


    def test_set_mf_diff_spheroid_set_beta(self):
        """Try to set the spheroidal diffusion tensor beta parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='beta', val=pi/2)


    def test_set_mf_diff_spheroid_set_gamma(self):
        """Try to set the spheroidal diffusion tensor gamma parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='gamma', val=pi/2)


    def test_set_mf_diff_spheroid_set_theta(self):
        """Set the spheroidal diffusion tensor theta parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='theta', val=pi/2)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.theta, pi/2)


    def test_set_mf_diff_spheroid_set_phi(self):
        """Set the spheroidal diffusion tensor phi parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='phi', val=pi/2)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.phi, pi/2)


    def test_set_mf_diff_spheroid_set_diff_tm_Da(self):
        """Set the spheroidal diffusion tensor parameters {tm, Da}.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['tm', 'Da'], val=[1e-8, 1e6])

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1e-8)
        self.assertEqual(cdp.diff_tensor.Da, 1e6)


    def test_set_mf_diff_spheroid_set_diff_Diso_Da(self):
        """Set the spheroidal diffusion tensor parameters {Diso, Da}.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['Diso', 'Da'], val=[1e7, 1e6])

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.Diso, 1e7)
        self.assertEqual(cdp.diff_tensor.Da, 1e6)


    def test_set_mf_diff_spheroid_set_diff_tm_Dratio(self):
        """Set the spheroidal diffusion tensor parameters {tm, Dratio}.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['tm', 'Dratio'], val=[1e-8, 1.6])

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1e-8)
        self.assertEqual(cdp.diff_tensor.Dratio, 1.6)


    def test_set_mf_diff_spheroid_set_diff_Dpar_Dper(self):
        """Set the spheroidal diffusion tensor parameters {Dpar, Dper}.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['Dpar', 'Dper'], val=[1e7, 2e7])

        # Test the parameter.
        self.assertAlmostEqual(cdp.diff_tensor.Dpar, 1e7)
        self.assertAlmostEqual(cdp.diff_tensor.Dper, 2e7)


    def test_set_mf_diff_spheroid_set_diff_Dper_Dpar(self):
        """Set the spheroidal diffusion tensor parameters {Dper, Dpar}.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['Dper', 'Dpar'], val=[1e7, 2e7])

        # Test the parameter.
        self.assertAlmostEqual(cdp.diff_tensor.Dper, 1e7)
        self.assertAlmostEqual(cdp.diff_tensor.Dpar, 2e7)


    def test_set_mf_diff_spheroid_set_diff_Diso_Dratio(self):
        """Set the spheroidal diffusion tensor parameters {Diso, Dratio}.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['Diso', 'Dratio'], val=[1e7, 1.2])

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.Diso, 1e7)
        self.assertEqual(cdp.diff_tensor.Dratio, 1.2)


    def test_set_mf_diff_spheroid_set_diff_Dpar_Dratio(self):
        """Set the spheroidal diffusion tensor parameters {Dpar, Dratio} (this should not be possible).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0, 0))

        # Set the parameters.
        self.assertRaises(RelaxUnknownParamCombError, self.value_fns.set, param=['Dpar', 'Dratio'], val=[1e7, 1.2])


    def test_set_mf_diff_ellipsoid_set_tm(self):
        """Set the ellipsoidal diffusion tensor tm parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='tm', val=1e-8)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1e-8)


    def test_set_mf_diff_ellipsoid_set_Diso(self):
        """Set the ellipsoidal diffusion tensor Diso parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='Diso', val=5e7)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.tm, 1./(6*5e7))


    def test_set_mf_diff_ellipsoid_set_Da(self):
        """Set the ellipsoidal diffusion tensor Da parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='Da', val=1e6)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.Da, 1e6)


    def test_set_mf_diff_ellipsoid_set_Dr(self):
        """Set the ellipsoidal diffusion tensor Dr parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='Dr', val=0.3)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.Dr, 0.3)


    def test_set_mf_diff_ellipsoid_set_Dx(self):
        """Set the ellipsoidal diffusion tensor Dx parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dx', val=1e6)


    def test_set_mf_diff_ellipsoid_set_Dy(self):
        """Set the ellipsoidal diffusion tensor Dy parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dy', val=1e6)


    def test_set_mf_diff_ellipsoid_set_Dz(self):
        """Set the ellipsoidal diffusion tensor Dz parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dz', val=1e6)


    def test_set_mf_diff_ellipsoid_set_Dpar(self):
        """Try to set the ellipsoidal diffusion tensor Dpar parameter (this should not be possible).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dpar', val=1e6)


    def test_set_mf_diff_ellipsoid_set_Dper(self):
        """Try to set the ellipsoidal diffusion tensor Dper parameter (this should not be possible).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dper', val=1e6)


    def test_set_mf_diff_ellipsoid_set_Dratio(self):
        """Set the ellipsoidal diffusion tensor Dratio parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='Dratio', val=1.2)


    def test_set_mf_diff_ellipsoid_set_alpha(self):
        """Try to set the ellipsoidal diffusion tensor alpha parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='alpha', val=pi/2)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.alpha, pi/2)


    def test_set_mf_diff_ellipsoid_set_beta(self):
        """Try to set the ellipsoidal diffusion tensor beta parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='beta', val=pi/2)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.beta, pi/2)


    def test_set_mf_diff_ellipsoid_set_gamma(self):
        """Try to set the ellipsoidal diffusion tensor gamma parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.value_fns.set(param='gamma', val=pi/2)

        # Test the parameter.
        self.assertEqual(cdp.diff_tensor.gamma, pi/2)


    def test_set_mf_diff_ellipsoid_set_theta(self):
        """Set the ellipsoidal diffusion tensor theta parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='theta', val=pi/2)


    def test_set_mf_diff_ellipsoid_set_phi(self):
        """Set the ellipsoidal diffusion tensor phi parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.2, 0, 0, 0))

        # Set the parameter.
        self.assertRaises(RelaxError, self.value_fns.set, param='phi', val=pi/2)


    def test_set_mf_diff_ellipsoid_set_diff_tm_Da_Dr(self):
        """Set the ellipsoidal diffusion tensor parameters {tm, Da, Dr}.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.4, 0, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['tm', 'Da', 'Dr'], val=[1e-8, 1e6, 0.2])

        # Test the parameters.
        self.assertEqual(cdp.diff_tensor.tm, 1e-8)
        self.assertEqual(cdp.diff_tensor.Da, 1e6)
        self.assertEqual(cdp.diff_tensor.Dr, 0.2)


    def test_set_mf_diff_ellipsoid_set_diff_Diso_Da_Dr(self):
        """Set the ellipsoidal diffusion tensor parameters {Diso, Da, Dr}.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.4, 0, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['Diso', 'Da', 'Dr'], val=[1e7, 1e6, 0.2])

        # Test the parameters.
        self.assertEqual(cdp.diff_tensor.Diso, 1e7)
        self.assertEqual(cdp.diff_tensor.Da, 1e6)
        self.assertEqual(cdp.diff_tensor.Dr, 0.2)


    def test_set_mf_diff_ellipsoid_set_diff_Dx_Dy_Dz(self):
        """Set the ellipsoidal diffusion tensor parameters {Dx, Dy, Dz}.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.4, 0, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['Dx', 'Dy', 'Dz'], val=[1e7, 2e7, 3e7])

        # Test the parameters.
        self.assertEqual(cdp.diff_tensor.Dx, 1e7)
        self.assertEqual(cdp.diff_tensor.Dy, 2e7)
        self.assertEqual(cdp.diff_tensor.Dz, 3e7)


    def test_set_mf_diff_ellipsoid_set_same_Dx_Dy_Dz(self):
        """Set the ellipsoidal diffusion tensor parameters {Dx, Dy, Dz} all to the same value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.4, 0, 0, 0))

        # Set the parameters.
        self.value_fns.set(param=['Dx', 'Dy', 'Dz'], val=1e7)

        # Test the parameters.
        self.assertEqual(cdp.diff_tensor.Dx, 1e7)
        self.assertEqual(cdp.diff_tensor.Dy, 1e7)
        self.assertEqual(cdp.diff_tensor.Dz, 1e7)


    def test_set_mf_diff_ellipsoid_set_diff_tm_Diso_Dr(self):
        """Try to set the ellipsoidal diffusion tensor parameters {tm, Diso, Dr} (this should not be possible).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Initialise a diffusion tensor.
        diffusion_tensor.init((1e-9, 2e6, 0.4, 0, 0, 0))

        # Set the parameters.
        self.assertRaises(RelaxUnknownParamCombError, self.value_fns.set, param=['tm', 'Diso', 'Dr'], val=[1e-8, 1e6, 0.2])




    ###############################################
    # Reduced spectral density mapping parameters #
    ###############################################


    def test_set_jw_all_spins_j0(self):
        """Set the RSDM parameter J(0) for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='j0', val=4.5e-9)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].j0, 4.5e-9)
        self.assertEqual(cdp.mol[0].res[1].spin[0].j0, 4.5e-9)


    def test_set_jw_all_spins_jwx(self):
        """Set the RSDM parameter J(wX) for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='jwx', val=2.3e-10)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].jwx, 2.3e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].jwx, 2.3e-10)


    def test_set_jw_all_spins_jwh(self):
        """Set the RSDM parameter J(wH) for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='J(wH)', val=1.7e-12)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].jwh, 1.7e-12)
        self.assertEqual(cdp.mol[0].res[1].spin[0].jwh, 1.7e-12)


    def test_set_jw_all_spins_r(self):
        """Set the RSDM bond length parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='Bond_length', val=1.04e-10)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].r, 1.04e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, 1.04e-10)


    def test_set_jw_all_spins_csa(self):
        """Set the RSDM CSA parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='csa', val=-160e-6)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].csa, -160e-6)
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, -160e-6)


    def test_set_jw_all_spins_heteronucleus(self):
        """Set the RSDM heteronucleus type for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='heteronucleus', val='13C')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].heteronuc_type, '13C')
        self.assertEqual(cdp.mol[0].res[1].spin[0].heteronuc_type, '13C')


    def test_set_jw_all_spins_diff_j0_jwx_jwh(self):
        """Set different RSDM parameters J(0), J(wX), J(wH) for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param=['J(0)', 'jwx', 'J(wH)'], val=[6.4e-9, 3.5e-10, 2.3e-12])

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].j0, 6.4e-9)
        self.assertEqual(cdp.mol[0].res[0].spin[0].jwx, 3.5e-10)
        self.assertEqual(cdp.mol[0].res[0].spin[0].jwh, 2.3e-12)
        self.assertEqual(cdp.mol[0].res[1].spin[0].j0, 6.4e-9)
        self.assertEqual(cdp.mol[0].res[1].spin[0].jwx, 3.5e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].jwh, 2.3e-12)


    def test_set_jw_all_spins_same_j0_jwx_jwh(self):
        """Set RSDM parameters J(0), J(wX), J(wH) for all spins to the same value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param=['J(0)', 'jwx', 'J(wH)'], val=1.9e-10)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].j0, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[0].spin[0].jwx, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[0].spin[0].jwh, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].j0, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].jwx, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].jwh, 1.9e-10)


    def test_set_jw_defaults_j0(self):
        """Set the RSDM parameter J(0) to the default value (there is none!).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.assertRaises(RelaxParamSetError, self.value_fns.set, param='j0')


    def test_set_jw_defaults_jwx(self):
        """Set the RSDM parameter J(wX) to the default value (there is none!).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.assertRaises(RelaxParamSetError, self.value_fns.set, param='jwx')


    def test_set_jw_defaults_jwh(self):
        """Set the RSDM parameter J(wH) to the default value (there is none!).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.assertRaises(RelaxParamSetError, self.value_fns.set, param='J(wH)')


    def test_set_jw_defaults_r(self):
        """Set the RSDM bond length parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='bond-Length')

        # Test the parameter.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].r, 1.02e-10)
        self.assertAlmostEqual(cdp.mol[0].res[1].spin[0].r, 1.02e-10)


    def test_set_jw_defaults_csa(self):
        """Set the RSDM CSA parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='csa')

        # Test the parameter.
        self.assertAlmostEqual(cdp.mol[0].res[0].spin[0].csa, -172e-6)
        self.assertAlmostEqual(cdp.mol[0].res[1].spin[0].csa, -172e-6)


    def test_set_jw_defaults_heteronucleus(self):
        """Set the RSDM heteronucleus type to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='heteronucleus')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].heteronuc_type, '15N')
        self.assertEqual(cdp.mol[0].res[1].spin[0].heteronuc_type, '15N')


    def test_set_jw_defaults_j0_jwx_jwh(self):
        """Set different RSDM parameters J(0), J(wX), J(wH) to the default values (there are none!).

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.assertRaises(RelaxParamSetError, self.value_fns.set, param=['J(0)', 'jwx', 'J(wH)'])


    def test_set_jw_single_spin_j0(self):
        """Set the RSDM parameter J(0) for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='j0', val=4.5e-9, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'j0'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].j0, 4.5e-9)


    def test_set_jw_single_spin_jwx(self):
        """Set the RSDM parameter J(wX) for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='jwx', val=2.3e-10, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'jwx'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].jwx, 2.3e-10)


    def test_set_jw_single_spin_jwh(self):
        """Set the RSDM parameter J(wH) for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='J(wH)', val=1.7e-12, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'jwh'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].jwh, 1.7e-12)


    def test_set_jw_single_spin_r(self):
        """Set the RSDM bond length parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='Bond_length', val=1.04e-10, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'r'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, 1.04e-10)


    def test_set_jw_single_spin_csa(self):
        """Set the RSDM CSA parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='csa', val=-160e-6, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'csa'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, -160e-6)


    def test_set_jw_single_spin_heteronucleus(self):
        """Set the RSDM heteronucleus type for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param='heteronucleus', val='13C', spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'heteronuc_type'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].heteronuc_type, '13C')


    def test_set_jw_single_spin_diff_j0_jwx_jwh(self):
        """Set different RSDM parameters J(0), J(wX), J(wH) for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param=['J(0)', 'jwx', 'J(wH)'], val=[6.4e-9, 3.5e-10, 2.3e-12], spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'j0'))
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'jwx'))
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'jwh'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].j0, 6.4e-9)
        self.assertEqual(cdp.mol[0].res[1].spin[0].jwx, 3.5e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].jwh, 2.3e-12)


    def test_set_jw_single_spin_same_j0_jwx_jwh(self):
        """Set RSDM parameters J(0), J(wX), J(wH) for a single spin to the same value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'jw'.
        pipes.switch('jw')

        # Set the parameter.
        self.value_fns.set(param=['J(0)', 'jwx', 'J(wH)'], val=1.9e-10, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'j0'))
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'jwx'))
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'jwh'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].j0, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].jwx, 1.9e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].jwh, 1.9e-10)



    #########################
    # Model-free parameters #
    #########################


    def test_set_mf_all_spins_local_tm(self):
        """Set the model-free local tm parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='local tm', val=1e-8)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].local_tm, 1e-8)
        self.assertEqual(cdp.mol[0].res[1].spin[0].local_tm, 1e-8)


    def test_set_mf_all_spins_s2(self):
        """Set the model-free S2 parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='S2', val=0.8)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].s2, 0.8)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2, 0.8)


    def test_set_mf_all_spins_s2f(self):
        """Set the model-free S2f parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='S2f', val=0.45)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].s2f, 0.45)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2f, 0.45)


    def test_set_mf_all_spins_s2s(self):
        """Set the model-free S2s parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='S2s', val=0.1)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].s2s, 0.1)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2s, 0.1)


    def test_set_mf_all_spins_te(self):
        """Set the model-free te parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='te', val=12.5e-12)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].te, 12.5e-12)
        self.assertEqual(cdp.mol[0].res[1].spin[0].te, 12.5e-12)


    def test_set_mf_all_spins_tf(self):
        """Set the model-free tf parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='tf', val=20.1e-12)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].tf, 20.1e-12)
        self.assertEqual(cdp.mol[0].res[1].spin[0].tf, 20.1e-12)


    def test_set_mf_all_spins_ts(self):
        """Set the model-free ts parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='ts', val=1.23e-9)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].ts, 1.23e-9)
        self.assertEqual(cdp.mol[0].res[1].spin[0].ts, 1.23e-9)


    def test_set_mf_all_spins_rex(self):
        """Set the model-free Rex parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='Rex', val=2.34)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].rex, 2.34)
        self.assertEqual(cdp.mol[0].res[1].spin[0].rex, 2.34)


    def test_set_mf_all_spins_r(self):
        """Set the model-free bond length parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='Bond length', val=1.02e-10)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].r, 1.02e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, 1.02e-10)


    def test_set_mf_all_spins_csa(self):
        """Set the model-free CSA parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='CSA', val=-172e-6)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].csa, -172e-6)
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, -172e-6)


    def test_set_mf_all_spins_heteronucleus(self):
        """Set the model-free heteronucleus type for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='heteronucleus', val='13C')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].heteronuc_type, '13C')
        self.assertEqual(cdp.mol[0].res[1].spin[0].heteronuc_type, '13C')


    def test_set_mf_all_spins_diff_s2f_s2s(self):
        """Set the model-free S2f and S2s parameters for all spins to different values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param=['S2f', 'S2s'], val=[0.7, 0.9])

        # Test the parameters.
        self.assertEqual(cdp.mol[0].res[0].spin[0].s2f, 0.7)
        self.assertEqual(cdp.mol[0].res[0].spin[0].s2s, 0.9)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2f, 0.7)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2s, 0.9)


    def test_set_mf_all_spins_same_s2f_s2s(self):
        """Set the model-free S2f and S2s parameters for all spins to the same value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param=['S2f', 'S2s'], val=0.7)

        # Test the parameters.
        self.assertEqual(cdp.mol[0].res[0].spin[0].s2f, 0.7)
        self.assertEqual(cdp.mol[0].res[0].spin[0].s2s, 0.7)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2f, 0.7)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2s, 0.7)


    def test_set_mf_defaults_local_tm(self):
        """Set the model-free local tm parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='local tm')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].local_tm, 10 * 1e-9)
        self.assertEqual(cdp.mol[0].res[1].spin[0].local_tm, 10 * 1e-9)


    def test_set_mf_defaults_s2(self):
        """Set the model-free S2 parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='S2')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].s2, 0.8)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2, 0.8)


    def test_set_mf_defaults_s2f(self):
        """Set the model-free S2f parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='S2f')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].s2f, 0.8)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2f, 0.8)


    def test_set_mf_defaults_s2s(self):
        """Set the model-free S2s parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='S2s')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].s2s, 0.8)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2s, 0.8)


    def test_set_mf_defaults_te(self):
        """Set the model-free te parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='te')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].te, 100 * 1e-12)
        self.assertEqual(cdp.mol[0].res[1].spin[0].te, 100 * 1e-12)


    def test_set_mf_defaults_tf(self):
        """Set the model-free tf parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='tf')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].tf, 10 * 1e-12)
        self.assertEqual(cdp.mol[0].res[1].spin[0].tf, 10 * 1e-12)


    def test_set_mf_defaults_ts(self):
        """Set the model-free ts parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='ts')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].ts, 1000 * 1e-12)
        self.assertEqual(cdp.mol[0].res[1].spin[0].ts, 1000 * 1e-12)


    def test_set_mf_defaults_rex(self):
        """Set the model-free Rex parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='Rex')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].rex, 0.0)
        self.assertEqual(cdp.mol[0].res[1].spin[0].rex, 0.0)


    def test_set_mf_defaults_r(self):
        """Set the model-free bond length parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='Bond length')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].r, 1.02 * 1e-10)
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, 1.02 * 1e-10)


    def test_set_mf_defaults_csa(self):
        """Set the model-free CSA parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='CSA')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].csa, -172 * 1e-6)
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, -172 * 1e-6)


    def test_set_mf_defaults_heteronucleus(self):
        """Set the model-free heteronucleus type to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='heteronucleus')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].heteronuc_type, '15N')
        self.assertEqual(cdp.mol[0].res[1].spin[0].heteronuc_type, '15N')


    def test_set_mf_defaults_s2f_s2s(self):
        """Set the model-free S2f and S2s parameters to the default values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param=['S2f', 'S2s'])

        # Test the parameters.
        self.assertEqual(cdp.mol[0].res[0].spin[0].s2f, 0.8)
        self.assertEqual(cdp.mol[0].res[0].spin[0].s2s, 0.8)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2f, 0.8)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2s, 0.8)


    def test_set_mf_single_spin_local_tm(self):
        """Set the model-free local tm parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='local tm', val=1e-8, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'local_tm'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].local_tm, 1e-8)


    def test_set_mf_single_spin_s2(self):
        """Set the model-free S2 parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='S2', val=0.8, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 's2'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2, 0.8)


    def test_set_mf_single_spin_s2f(self):
        """Set the model-free S2f parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='S2f', val=0.45, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 's2f'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2f, 0.45)


    def test_set_mf_single_spin_s2s(self):
        """Set the model-free S2s parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='S2s', val=0.1, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 's2s'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2s, 0.1)


    def test_set_mf_single_spin_te(self):
        """Set the model-free te parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='te', val=12.5e-12, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'te'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].te, 12.5e-12)


    def test_set_mf_single_spin_tf(self):
        """Set the model-free tf parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='tf', val=20.1e-12, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'tf'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].tf, 20.1e-12)


    def test_set_mf_single_spin_ts(self):
        """Set the model-free ts parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='ts', val=1.23e-9, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'ts'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].ts, 1.23e-9)


    def test_set_mf_single_spin_rex(self):
        """Set the model-free Rex parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='Rex', val=2.34, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'rex'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].rex, 2.34)


    def test_set_mf_single_spin_r(self):
        """Set the model-free bond length parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='Bond length', val=1.02e-10, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'r'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, 1.02e-10)


    def test_set_mf_single_spin_csa(self):
        """Set the model-free CSA parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='CSA', val=-172e-6, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'csa'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, -172e-6)


    def test_set_mf_single_spin_heteronucleus(self):
        """Set the model-free heteronucleus type for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param='heteronucleus', val='13C', spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'heteronuc_type'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].heteronuc_type, '13C')


    def test_set_mf_single_spin_diff_s2f_s2s(self):
        """Set the model-free S2f and S2s parameters for a single spin to different values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param=['S2f', 'S2s'], val=[0.7, 0.9], spin_id='@112')

        # Test the parameters.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 's2f'))
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 's2s'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2f, 0.7)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2s, 0.9)


    def test_set_mf_single_spin_same_s2f_s2s(self):
        """Set the model-free S2f and S2s parameters for a single spin to the same value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        pipes.switch('mf')

        # Set the parameter.
        self.value_fns.set(param=['S2f', 'S2s'], val=0.7, spin_id='@112')

        # Test the parameters.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 's2f'))
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 's2s'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2f, 0.7)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2s, 0.7)



    ############################
    # N-state model parameters #
    ############################


    def test_set_n_state_model_rx(self):
        """Set the N-state model curve fitting alpha2 parameter.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'n_state'.
        pipes.switch('n_state')

        # Set the parameter.
        self.value_fns.set(param='alpha2', val=pi)

        # Test the parameter.
        self.assertEqual(cdp.alpha[0], 0.0)
        self.assertEqual(cdp.alpha[1], 0.0)
        self.assertEqual(cdp.alpha[2], pi)
        self.assertEqual(cdp.alpha[3], 0.0)



    #######################################
    # Relaxation curve fitting parameters #
    #######################################


    def test_set_relax_fit_all_spins_rx(self):
        """Set the relaxation curve fitting Rx parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param='rx', val=1.2)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].rx, 1.2)
        self.assertEqual(cdp.mol[0].res[1].spin[0].rx, 1.2)


    def test_set_relax_fit_all_spins_i0(self):
        """Set the relaxation curve fitting I0 parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param='i0', val=520)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].i0, 520)
        self.assertEqual(cdp.mol[0].res[1].spin[0].i0, 520)


    def test_set_relax_fit_all_spins_iinf(self):
        """Set the relaxation curve fitting Iinf parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param='Iinf', val=-1.7)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].iinf, -1.7)
        self.assertEqual(cdp.mol[0].res[1].spin[0].iinf, -1.7)


    def test_set_relax_fit_all_spins_diff_i0_iinf(self):
        """Set the relaxation curve fitting parameters {I0, Iinf} for all spins to different values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param=['I0', 'iinf'], val=[123456, -1.7])

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].i0, 123456)
        self.assertEqual(cdp.mol[0].res[0].spin[0].iinf, -1.7)
        self.assertEqual(cdp.mol[0].res[1].spin[0].i0, 123456)
        self.assertEqual(cdp.mol[0].res[1].spin[0].iinf, -1.7)


    def test_set_relax_fit_all_spins_same_i0_iinf(self):
        """Set the relaxation curve fitting parameters {I0, Iinf} for all spins to the same value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param=['I0', 'iinf'], val=0.0)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].i0, 0.0)
        self.assertEqual(cdp.mol[0].res[0].spin[0].iinf, 0.0)
        self.assertEqual(cdp.mol[0].res[1].spin[0].i0, 0.0)
        self.assertEqual(cdp.mol[0].res[1].spin[0].iinf, 0.0)


    def test_set_relax_fit_defaults_rx(self):
        """Set the relaxation curve fitting Rx parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param='rx')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].rx, 8.0)
        self.assertEqual(cdp.mol[0].res[1].spin[0].rx, 8.0)


    def test_set_relax_fit_defaults_i0(self):
        """Set the relaxation curve fitting I0 parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param='i0')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].i0, 10000.0)
        self.assertEqual(cdp.mol[0].res[1].spin[0].i0, 10000.0)


    def test_set_relax_fit_defaults_iinf(self):
        """Set the relaxation curve fitting Iinf parameter to the default value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param='Iinf')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].iinf, 0.0)
        self.assertEqual(cdp.mol[0].res[1].spin[0].iinf, 0.0)


    def test_set_relax_fit_defaults_i0_iinf(self):
        """Set the relaxation curve fitting parameters {I0, Iinf} to the default values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param=['I0', 'iinf'])

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].i0, 10000.0)
        self.assertEqual(cdp.mol[0].res[0].spin[0].iinf, 0.0)
        self.assertEqual(cdp.mol[0].res[1].spin[0].i0, 10000.0)
        self.assertEqual(cdp.mol[0].res[1].spin[0].iinf, 0.0)


    def test_set_relax_fit_single_spin_rx(self):
        """Set the relaxation curve fitting Rx parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param='rx', val=1.2, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'rx'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].rx, 1.2)


    def test_set_relax_fit_single_spin_i0(self):
        """Set the relaxation curve fitting I0 parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param='i0', val=520, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'i0'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].i0, 520)


    def test_set_relax_fit_single_spin_iinf(self):
        """Set the relaxation curve fitting Iinf parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param='Iinf', val=-1.7, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'iinf'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].iinf, -1.7)


    def test_set_relax_fit_single_spin_diff_i0_iinf(self):
        """Set the relaxation curve fitting parameters {I0, Iinf} for all spins to different values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param=['I0', 'iinf'], val=[123456, -1.7], spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'i0'))
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'iinf'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].i0, 123456)
        self.assertEqual(cdp.mol[0].res[1].spin[0].iinf, -1.7)


    def test_set_relax_fit_single_spin_same_i0_iinf(self):
        """Set the relaxation curve fitting parameters {I0, Iinf} for all spins to the same value.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'relax_fit'.
        pipes.switch('relax_fit')

        # Set the parameter.
        self.value_fns.set(param=['I0', 'iinf'], val=0.0, spin_id='@112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'i0'))
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'iinf'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].i0, 0.0)
        self.assertEqual(cdp.mol[0].res[1].spin[0].iinf, 0.0)
