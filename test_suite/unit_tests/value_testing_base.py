###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
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

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError



class Value_base_class:
    """Base class for the tests of both the 'prompt.value' and 'generic_fns.value' modules.

    This base class also contains many shared unit tests.
    """


    def setUp(self):
        """Set up for all the value unit tests."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Add a model-free data pipe to the data store for testing model-free and diffusion parameters.
        relax_data_store.add(pipe_name='mf', pipe_type='mf')

        # Add a second model-free data pipe for copying tests.
        relax_data_store.add(pipe_name='mf2', pipe_type='mf')

        # Set up some spins.
        self.set_up_spins(pipe_name='mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def set_up_spins(self, pipe_name=None):
        """Function for setting up a few spins for the given pipe."""

        # Alias the pipe.
        pipe = relax_data_store[pipe_name]

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


    def test_set_mf_all_spins_local_tm(self):
        """Set the model-free local tm parameter for all spins.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param='CSA', val=-172e-6)

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].csa, -172e-6)
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, -172e-6)


    def test_set_mf_all_spins_diff_s2f_s2s(self):
        """Set the model-free S2f and S2s parameters for all spins to different values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param='CSA')

        # Test the parameter.
        self.assertEqual(cdp.mol[0].res[0].spin[0].csa, -172 * 1e-6)
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, -172 * 1e-6)


    def test_set_mf_defaults_s2f_s2s(self):
        """Set the model-free S2f and S2s parameters to the default values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param='local tm', val=1e-8, spin_id=':112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'local_tm'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].local_tm, 1e-8)


    def test_set_mf_single_spin_s2(self):
        """Set the model-free S2 parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param='S2', val=0.8, spin_id=':112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 's2'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2, 0.8)


    def test_set_mf_single_spin_s2f(self):
        """Set the model-free S2f parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param='S2f', val=0.45, spin_id=':112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 's2f'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2f, 0.45)


    def test_set_mf_single_spin_s2s(self):
        """Set the model-free S2s parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param='S2s', val=0.1, spin_id=':112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 's2s'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2s, 0.1)


    def test_set_mf_single_spin_te(self):
        """Set the model-free te parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param='te', val=12.5e-12, spin_id=':112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'te'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].te, 12.5e-12)


    def test_set_mf_single_spin_tf(self):
        """Set the model-free tf parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param='tf', val=20.1e-12, spin_id=':112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'tf'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].tf, 20.1e-12)


    def test_set_mf_single_spin_ts(self):
        """Set the model-free ts parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param='ts', val=1.23e-9, spin_id=':112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'ts'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].ts, 1.23e-9)


    def test_set_mf_single_spin_rex(self):
        """Set the model-free Rex parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param='Rex', val=2.34, spin_id=':112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'rex'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].rex, 2.34)


    def test_set_mf_single_spin_r(self):
        """Set the model-free bond length parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param='Bond length', val=1.02e-10, spin_id=':112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'r'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].r, 1.02e-10)


    def test_set_mf_single_spin_csa(self):
        """Set the model-free CSA parameter for a single spin.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param='CSA', val=-172e-6, spin_id=':112')

        # Test the parameter.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 'csa'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].csa, -172e-6)


    def test_set_mf_single_spin_diff_s2f_s2s(self):
        """Set the model-free S2f and S2s parameters for a single spin to different values.

        The functions tested are both generic_fns.value.set() and prompt.value.set().
        """

        # Set the current data pipe to 'mf'.
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param=['S2f', 'S2s'], val=[0.7, 0.9], spin_id=':112')

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
        relax_data_store.current_pipe = 'mf'

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the parameter.
        self.value_fns.set(param=['S2f', 'S2s'], val=0.7, spin_id=':112')

        # Test the parameters.
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 's2f'))
        self.assert_(not hasattr(cdp.mol[0].res[0].spin[0], 's2s'))
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2f, 0.7)
        self.assertEqual(cdp.mol[0].res[1].spin[0].s2s, 0.7)
