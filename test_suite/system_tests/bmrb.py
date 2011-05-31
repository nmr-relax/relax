###############################################################################
#                                                                             #
# Copyright (C) 2008-2011 Edward d'Auvergne                                   #
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
from copy import deepcopy
import inspect
from numpy import ndarray
from os import remove, sep
from re import search
import sys
from tempfile import mktemp

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
import dep_check
from status import Status; status = Status()


class Bmrb(SystemTestCase):
    """TestCase class for functional tests of the reading and writing of BMRB STAR formatted files."""

    def __init__(self, methodName='runTest'):
        """Skip the tests if scipy is not installed.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Missing module.
        if not dep_check.bmrblib_module:
            # Store in the status object. 
            status.skipped_tests.append([methodName, 'Bmrblib', 'system'])

        # Execute the base class method.
        super(Bmrb, self).__init__(methodName)


    def setUp(self):
        """Common set up for these system tests."""

        # Create a temporary file name.
        ds.tmpfile = mktemp()


    def tearDown(self):
        """Reset the relax data storage object."""

        # Delete the temporary file.
        try:
            remove(ds.tmpfile)
        except OSError:
            pass

        # Reset the relax data storage object.
        ds.__reset__()


    def data_check(self, old_pipe_name='results', new_pipe_name='new', version=None):
        """Check that all data has been successfully restored from the BMRB files."""

        # Print out.
        print("\n\nComparing data pipe contents:")

        # Blacklists (data that is not restored, and relaxation data which has been reordered and will be checked in data_ri_comp()).
        blacklist_spin = ['attached_proton', 'fixed', 'nucleus', 'proton_type', 'relax_sim_data', 'select', 'xh_vect'] + ['r_err', 'csa_err'] + ['chi2_sim', 'f_count', 'g_count', 'h_count', 'iter', 'warning'] + ['frq', 'frq_labels', 'noe_r1_table', 'remap_table', 'ri_labels', 'relax_data', 'relax_error']
        if version == '3.0':
            blacklist_spin = blacklist_spin + ['r', 'local_tm', 'local_tm_err']
        blacklist_diff = []
        blacklist_global = ['diff_tensor', 'exp_info', 'hybrid_pipes', 'mol', 'sim_number', 'sim_state'] + ['ri_ids', 'frq', 'ri_type']

        # The data pipes.
        old_pipe = ds[old_pipe_name]
        new_pipe = ds[new_pipe_name]

        # The molecule data structure.
        self.assertEqual(len(old_pipe.mol), len(new_pipe.mol))
        for i in range(len(old_pipe.mol)):
            # Check the attributes.
            self.assertEqual(old_pipe.mol[i].name, old_pipe.mol[i].name)
            self.assertEqual(old_pipe.mol[i].type, old_pipe.mol[i].type)

            # The residue data structure.
            self.assertEqual(len(old_pipe.mol[i].res), len(new_pipe.mol[i].res))
            for j in range(len(old_pipe.mol[i].res)):
                # Check the attributes.
                self.assertEqual(old_pipe.mol[i].res[j].name, old_pipe.mol[i].res[j].name)
                self.assertEqual(old_pipe.mol[i].res[j].num, old_pipe.mol[i].res[j].num)

                # The spin data structure.
                self.assertEqual(len(old_pipe.mol[i].res[j].spin), len(new_pipe.mol[i].res[j].spin))
                for k in range(len(old_pipe.mol[i].res[j].spin)):
                    # Skip deselected spins.
                    if not old_pipe.mol[i].res[j].spin[k].select:
                        continue

                    # Check the containers.
                    self.data_cont_comp(label='Spin', cont_old=old_pipe.mol[i].res[j].spin[k], cont_new=new_pipe.mol[i].res[j].spin[k], blacklist=blacklist_spin)
                    if hasattr(old_pipe.mol[i].res[j].spin[k], 'ri_labels'):
                        self.data_ri_comp_spin(cont_old=old_pipe.mol[i].res[j].spin[k], cont_new=new_pipe.mol[i].res[j].spin[k])

        # The diffusion tensor.
        if version != '3.0':
            self.assert_(hasattr(new_pipe, 'diff_tensor'))
            self.data_cont_comp(label='Diff tensor', cont_old=old_pipe.diff_tensor, cont_new=new_pipe.diff_tensor, prec=4, blacklist=blacklist_diff)

        # The global data structures.
        self.data_cont_comp(label='Global', cont_old=old_pipe, cont_new=new_pipe, blacklist=blacklist_global)
        if hasattr(old_pipe, 'ri_ids'):
            self.data_ri_comp_pipe(cont_old=old_pipe, cont_new=new_pipe)


    def data_cont_comp(self, label=None, cont_old=None, cont_new=None, prec=7, blacklist=[]):
        """Compare the contents of the two data containers."""

        # Print a new line.
        print('')

        # Check the attributes.
        names = dir(cont_old)
        for name in names:
            # Skip special names.
            if search('^__', name):
                continue

            # Skip the data store methods.
            if name in list(cont_old.__class__.__dict__.keys()):
                continue

            # Simulation data.
            if search('_sim$', name):
                continue

            # Blacklisting.
            if name in blacklist:
                continue

            # Print out.
            print("%s object: '%s'" % (label, name))

            # Get the objects.
            obj_old = getattr(cont_old, name)
            obj_new = getattr(cont_new, name)

            # Functions and methods.
            if inspect.isfunction(obj_old) or inspect.ismethod(obj_old):
                continue

            # Does it exist?
            self.assert_(hasattr(cont_new, name))

            # Compare lists.
            if (isinstance(obj_old, list) or isinstance(obj_old, ndarray)):
                self.assertEqual(len(obj_old), len(obj_new))

                # List of lists (or rank-2 array).
                if (isinstance(obj_old[0], list) or isinstance(obj_old[0], ndarray)):
                    for i in range(len(obj_old)):
                        for j in range(len(obj_old[i])):
                            if isinstance(obj_old[i][j], float):
                                self.assertAlmostEqual(obj_old[i][j], obj_new[i][j], prec)
                            else:
                                self.assertEqual(obj_old[i][j], obj_new[i][j])

                # Standard list.
                else:
                    for i in range(len(obj_old)):
                        if isinstance(obj_old[i], float):
                            self.assertAlmostEqual(obj_old[i], obj_new[i], prec)
                        else:
                            self.assertEqual(obj_old[i], obj_new[i])

            # Compare floats.
            elif isinstance(obj_old, float):
                self.assertAlmostEqual(obj_old, obj_new, prec)

            # Compare ints and strings.
            else:
                self.assertEqual(obj_old, obj_new)


    def data_ri_comp_pipe(self, cont_old=None, cont_new=None):
        """Compare the contents of the two pipe data containers."""

        # Check that the new container has relaxation data.
        for name in ['frq', 'ri_ids', 'ri_type']:
            self.assert_(hasattr(cont_new, name))

        # Check the IDs.
        old_ids = deepcopy(cont_old.ri_ids)
        new_ids = deepcopy(cont_new.ri_ids)
        old_ids.sort()
        new_ids.sort()
        self.assertEqual(old_ids, new_ids)

        # Check the frequencies and types.
        for ri_id in old_ids:
            self.assertEqual(cont_old.frq[ri_id], cont_new.frq[ri_id])
            self.assertEqual(cont_old.ri_type[ri_id], cont_new.ri_type[ri_id])


    def data_ri_comp_spin(self, cont_old=None, cont_new=None):
        """Compare the contents of the two spin data containers."""

        # Check that the new container has relaxation data.
        for name in ['ri_data', 'ri_data_err']:
            self.assert_(hasattr(cont_new, name))

        # Check the IDs.
        old_ids = cont_old.ri_data.keys()
        new_ids = cont_new.ri_data.keys()
        old_ids.sort()
        new_ids.sort()
        self.assertEqual(old_ids, new_ids)

        # Check the data and errors.
        for ri_id in old_ids:
            self.assertEqual(cont_old.ri_data[ri_id], cont_new.ri_data[ri_id])
            self.assertEqual(cont_old.ri_data_err[ri_id], cont_new.ri_data_err[ri_id])


    def test_rw_bmrb_3_0_model_free(self):
        """Write and then read a BRMB STAR formatted file containing model-free results."""

        # Set the NMR-STAR version.
        ds.version = '3.0'

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'bmrb_rw.py')

        # Test the data.
        self.data_check(version='3.0')


    def test_rw_bmrb_3_1_model_free(self):
        """Write and then read a BRMB STAR formatted file containing model-free results."""

        # Set the NMR-STAR version.
        ds.version = '3.1'

        # Execute the script.
        self.interpreter.run(script_file=status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'bmrb_rw.py')

        # Test the data.
        self.data_check(version='3.1')
