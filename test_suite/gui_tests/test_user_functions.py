###############################################################################
#                                                                             #
# Copyright (C) 2012,2014,2016,2019 Edward d'Auvergne                         #
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

"""Module for testing the special features of the user function GUI windows."""

# Python module imports.
from os import path, sep
import sys

# relax module imports.
import dep_check
from status import Status; status = Status()
from test_suite.gui_tests.base_classes import GuiTestCase

# relax GUI imports.
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.string_conv import float_to_gui, int_to_gui, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


class User_functions(GuiTestCase):
    """Class for testing special features of the user function GUI windows."""

    def exec_uf_pipe_create(self, pipe_name=None, pipe_type='mf'):
        """Execute the pipe.create user function via the GUI user function window.

        @keyword pipe_name:     The pipe_name argument of the pipe.create user function.
        @type pipe_name:        str
        @keyword pipe_type:     The pipe_type argument of the pipe.create user function.
        @type pipe_type:        str
        """

        # Open the pipe.create user function window.
        uf = uf_store['pipe.create']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)

        # Set the arguments.
        uf.page.SetValue('pipe_name', str_to_gui(pipe_name))
        uf.page.SetValue('pipe_type', str_to_gui(pipe_type))

        # Execute.
        uf.wizard._go_next(None)


    def test_bug_2_structure_read_pdb_failure(self):
        """Catch U{bug #2<https://sourceforge.net/p/nmr-relax/tickets/2/>}, the failure of the structure.read_pdb user function.

        This was reported by U{Stefano Ciurli<https://sourceforge.net/u/stefanociurli/>}.
        """

        # Create the data pipe.
        self.exec_uf_pipe_create(pipe_name='structure.read_pdb user function failure test')

        # Open the structure.read_pdb user function window.
        uf = uf_store['structure.read_pdb']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)

        # The PDB file.
        file = path.join(status.install_path, 'test_suite', 'shared_data', 'structures', '1J7O.pdb')

        # Manually set the PDB file on the first text element - as this is not attached to a uf_args dictionary element!
        uf.page.GetChildren()[6].SetValue(str_to_gui(file))

        # Execute the user function.
        uf.wizard._go_next(None)

        # Check the structural data.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 3)
        self.assertEqual(cdp.structure.structural_data[0].num, 1)
        self.assertEqual(cdp.structure.structural_data[1].num, 2)
        self.assertEqual(cdp.structure.structural_data[2].num, 3)


    def test_bug_3_no_argument_validation(self):
        """Catch U{bug #3<https://sourceforge.net/p/nmr-relax/tickets/3/>}, the absence of user function argument validation in the GUI.

        Without argument validation, the structure.read_pdb user function would fail with the error::

            relax> pipe.create(pipe_name='validation_test', pipe_type='mf', bundle=None)

            relax> structure.read_pdb(file=None, dir=None, read_mol=None, set_mol_name=None, read_model=None, set_model_num=None, alt_loc=None, verbosity=1, merge=False)
            Traceback (most recent call last):
              File "/data/relax/relax/gui/interpreter.py", line 306, in run
                fn(*args, **kwds)
              File "/data/relax/relax/pipe_control/structure/main.py", line 1277, in read_pdb
                if not access(file_path, F_OK):
            TypeError: coercing to Unicode: need string or buffer, NoneType found

        However with validation, a RelaxStrFileError error is raised.   This is caught by the GUI, presenting a pop up window for the error, printing out the error text, but not raising the error.  Hence an error cannot be caught.
        """

        # Create the data pipe.
        self.exec_uf_pipe_create(pipe_name='user function argument validation test')

        # Open the structure.read_pdb user function window.
        uf = uf_store['structure.read_pdb']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)

        # Execute the user function with no arguments set.
        uf.wizard._go_next(None)


    def test_dx_map(self):
        """Test the operation of the dx.map user function GUI window."""

        # Open the dx.map user function window.
        uf = uf_store['dx.map']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)

        # Set the y-value of a single point, and check.
        uf.page.uf_args['point'].selection_win_show()
        if dep_check.wx_classic:
            uf.page.uf_args['point'].sel_win.sequence.SetStringItem(0, 2, int_to_gui(2))
        else:
            uf.page.uf_args['point'].sel_win.sequence.SetItem(0, 2, int_to_gui(2))
        uf.page.uf_args['point'].selection_win_data()
        points = uf.page.uf_args['point'].GetValue()
        print("Points:  %s" % points)
        self.assertEqual(len(points), 1)
        self.assertEqual(len(points[0]), 3)
        self.assertEqual(points[0][0], None)
        self.assertEqual(points[0][1], 2.0)
        self.assertEqual(points[0][2], None)

        # Set the point to nothing in the wizard, open the Sequence_2D window, close the window, and check that None comes back.
        uf.page.uf_args['point'].SetValue(str_to_gui(''))
        uf.page.uf_args['point'].selection_win_show()
        uf.page.uf_args['point'].selection_win_data()
        points = uf.page.uf_args['point'].GetValue()
        print("Points:  %s" % points)
        self.assertEqual(points, None)

        # Set a valid point in the wizard, open and close the Sequence_2D window (twice), and check that the point comes back.
        uf.page.uf_args['point'].SetValue(str_to_gui('[[1, 2, -3.]]'))
        uf.page.uf_args['point'].selection_win_show()
        uf.page.uf_args['point'].selection_win_data()
        uf.page.uf_args['point'].selection_win_show()
        uf.page.uf_args['point'].selection_win_data()
        points = uf.page.uf_args['point'].GetValue()
        print("Points:  %s" % points)
        self.assertEqual(len(points), 1)
        self.assertEqual(len(points[0]), 3)
        self.assertEqual(points[0][0], 1.0)
        self.assertEqual(points[0][1], 2.0)
        self.assertEqual(points[0][2], -3.0)

        # Set 2 valid points in the wizard, open and close the Sequence_2D window (twice), and check that the points come back.
        uf.page.uf_args['point'].SetValue(str_to_gui('[[1, 2, 3], [-2, -3, -4]]'))
        uf.page.uf_args['point'].selection_win_show()
        uf.page.uf_args['point'].selection_win_data()
        uf.page.uf_args['point'].selection_win_show()
        uf.page.uf_args['point'].selection_win_data()
        points = uf.page.uf_args['point'].GetValue()
        print("Points:  %s" % points)
        self.assertEqual(len(points), 2)
        self.assertEqual(len(points[0]), 3)
        self.assertEqual(len(points[1]), 3)
        self.assertEqual(points[0][0], 1.0)
        self.assertEqual(points[0][1], 2.0)
        self.assertEqual(points[0][2], 3.0)
        self.assertEqual(points[1][0], -2.0)
        self.assertEqual(points[1][1], -3.0)
        self.assertEqual(points[1][2], -4.0)

        # Set the points to a number of invalid values, checking that they are ignored.
        for val in ['2', 'die', '[1, 2, 3', '[1]', '[[1, 2, 3], 1, 2, 3], [1, 2, 3]]']:
            uf.page.uf_args['point'].SetValue(str_to_gui(val))
            uf.page.uf_args['point'].selection_win_show()
            uf.page.uf_args['point'].selection_win_data()
            points = uf.page.uf_args['point'].GetValue()
            print("Points:  %s" % points)
            self.assertEqual(points, None)

        # Set the Sequence_2D elements to invalid values.
        for val in ['x']:
            uf.page.uf_args['point'].SetValue(str_to_gui(''))
            uf.page.uf_args['point'].selection_win_show()
            if dep_check.wx_classic:
                uf.page.uf_args['point'].sel_win.sequence.SetStringItem(0, 2, str_to_gui(val))
                uf.page.uf_args['point'].sel_win.sequence.SetStringItem(0, 1, int_to_gui(1))
            else:
                uf.page.uf_args['point'].sel_win.sequence.SetItem(0, 2, str_to_gui(val))
                uf.page.uf_args['point'].sel_win.sequence.SetItem(0, 1, int_to_gui(1))
            uf.page.uf_args['point'].selection_win_data()
            points = uf.page.uf_args['point'].GetValue()
            print("Points:  %s" % points)
            self.assertEqual(len(points), 1)
            self.assertEqual(len(points[0]), 3)
            self.assertEqual(points[0][0], 1.0)
            self.assertEqual(points[0][1], None)
            self.assertEqual(points[0][2], None)


    def test_spectrum_read_intensities(self):
        """Test the operation of the spectrum.read_intensities user function GUI window."""

        # Open the spectrum.read_intensities user function window.
        uf = uf_store['spectrum.read_intensities']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)

        # Set the y-value of a single pos, and check.
        uf.page.uf_args['file'].selection_win_show()
        uf.page.uf_args['file'].sel_win.SetValue('test_file')
        uf.page.uf_args['file'].selection_win_data()
        file = uf.page.uf_args['file'].GetValue()
        print("File names:  %s" % file)
        self.assertTrue(isinstance(file, str))
        self.assertEqual(file, 'test_file')

        # Set the file to nothing in the wizard, open the Sequence window, close the window, and check that None comes back.
        uf.page.uf_args['file'].SetValue(str_to_gui(''))
        uf.page.uf_args['file'].selection_win_show()
        uf.page.uf_args['file'].selection_win_data()
        file = uf.page.uf_args['file'].GetValue()
        print("File names:  %s" % file)
        self.assertEqual(file, None)

        # Set a valid file list in the wizard, open and close the Sequence window (twice), and check that the file comes back.
        uf.page.uf_args['file'].SetValue(str_to_gui("['test1', 'test2']"))
        uf.page.uf_args['file'].selection_win_show()
        uf.page.uf_args['file'].selection_win_data()
        uf.page.uf_args['file'].selection_win_show()
        uf.page.uf_args['file'].selection_win_data()
        file = uf.page.uf_args['file'].GetValue()
        print("File names:  %s" % file)
        self.assertEqual(len(file), 2)
        self.assertEqual(file[0], 'test1')
        self.assertEqual(file[1], 'test2')

        # Set the file to a number of invalid values, checking that they are ignored.
        for val in ["['1', '2', '3'", "['1'"]:
            uf.page.uf_args['file'].SetValue(str_to_gui(val))
            uf.page.uf_args['file'].selection_win_show()
            uf.page.uf_args['file'].selection_win_data()
            file = uf.page.uf_args['file'].GetValue()
            print("Invalid file: %s\nFile names:  %s" % (val, file))
            self.assertEqual(file, None)


    def test_structure_add_atom(self):
        """Test the operation of the structure.add_atom user function GUI window."""

        # Open the structure.add_atom user function window.
        uf = uf_store['structure.add_atom']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)

        # Set the y-value of a single pos, and check.
        #uf.page.uf_args['pos'].selection_win_show()
        #if dep_check.wx_classic:
        #    uf.page.uf_args['pos'].sel_win.sequence.SetStringItem(1, 1, int_to_gui(2))
        #else:
        #    uf.page.uf_args['pos'].sel_win.sequence.SetItem(1, 1, int_to_gui(2))
        #uf.page.uf_args['pos'].selection_win_data()
        #pos = uf.page.uf_args['pos'].GetValue()
        #print("Pos:  %s" % pos)
        #self.assertEqual(len(pos), 3)
        #self.assertEqual(pos[0], None)
        #self.assertEqual(pos[1], 2.0)
        #self.assertEqual(pos[2], None)

        # Set the pos to nothing in the wizard, open the Sequence window, close the window, and check that None comes back.
        val = ''
        sys.stdout.write("Value: %40s;  " % repr(val))
        uf.page.uf_args['pos'].SetValue(str_to_gui(val))
        uf.page.uf_args['pos'].selection_win_show()
        uf.page.uf_args['pos'].selection_win_data()
        pos = uf.page.uf_args['pos'].GetValue()
        sys.stdout.write("Return: %40s\n" % repr(pos))
        self.assertEqual(pos, None)

        # Set a valid pos in the wizard, open and close the Sequence window (twice), and check that the pos comes back.
        val = '[1, 2, -3.]'
        sys.stdout.write("Value: %40s;  " % repr(val))
        uf.page.uf_args['pos'].SetValue(str_to_gui(val))
        uf.page.uf_args['pos'].selection_win_show()
        uf.page.uf_args['pos'].selection_win_data()
        uf.page.uf_args['pos'].selection_win_show()
        uf.page.uf_args['pos'].selection_win_data()
        pos = uf.page.uf_args['pos'].GetValue()
        sys.stdout.write("Return: %40s\n" % repr(pos))
        self.assertEqual(len(pos), 1)
        self.assertEqual(len(pos[0]), 3)
        self.assertEqual(pos[0][0], 1.0)
        self.assertEqual(pos[0][1], 2.0)
        self.assertEqual(pos[0][2], -3.0)

        # Set the pos to a number of invalid values, checking that they are ignored.
        for val in ['die', '[1, 2, 3', '[[1, 2, 3], 1, 2, 3], [1, 2, 3]]']:
            sys.stdout.write("Value: %40s;  " % repr(val))
            uf.page.uf_args['pos'].SetValue(str_to_gui(val))
            uf.page.uf_args['pos'].selection_win_show()
            uf.page.uf_args['pos'].selection_win_data()
            pos = uf.page.uf_args['pos'].GetValue()
            sys.stdout.write("Return: %40s\n" % repr(pos))
            self.assertEqual(pos, None)

        # Set the Sequence elements to invalid values.
        for val in ['x']:
            sys.stdout.write("Value: %40s;  " % repr(val))
            uf.page.uf_args['pos'].SetValue(str_to_gui(''))
            uf.page.uf_args['pos'].selection_win_show()
            uf.page.uf_args['pos'].sel_win.add_element()
            if dep_check.wx_classic:
                uf.page.uf_args['pos'].sel_win.sequence.SetStringItem(1, 1, str_to_gui(val))
                uf.page.uf_args['pos'].sel_win.sequence.SetStringItem(0, 1, int_to_gui(1))
            else:
                uf.page.uf_args['pos'].sel_win.sequence.SetItem(1, 1, str_to_gui(val))
                uf.page.uf_args['pos'].sel_win.sequence.SetItem(0, 1, int_to_gui(1))
            uf.page.uf_args['pos'].selection_win_data()
            pos = uf.page.uf_args['pos'].GetValue()
            sys.stdout.write("Return: %40s\n" % repr(pos))
            #self.assertEqual(len(pos), 1)
            self.assertEqual(pos[0][0], 1.0)
            #self.assertEqual(pos[0][1], None)
            #self.assertEqual(pos[0][2], None)


    def test_structure_pdb_read(self):
        """Test the full operation of the structure.read_pdb user function GUI window."""

        # Create the data pipe.
        self.exec_uf_pipe_create(pipe_name='PDB reading test')

        # Open the structure.read_pdb user function window.
        uf = uf_store['structure.read_pdb']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)

        # The PDB file to operate on.
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'structures' + sep + 'trunc_ubi_pcs.pdb'
        uf.page.SetValue('file', str_to_gui(file))

        # Set the models to read.
        uf.page.SetValue('read_model', str_to_gui('6'))
        uf.page.uf_args['read_model'].selection_win_show()
        uf.page.uf_args['read_model'].sel_win.add_element(None)
        if dep_check.wx_classic:
            uf.page.uf_args['read_model'].sel_win.sequence.SetStringItem(0, 1, int_to_gui(2))
            uf.page.uf_args['read_model'].sel_win.sequence.SetStringItem(1, 1, int_to_gui(4))
        else:
            uf.page.uf_args['read_model'].sel_win.sequence.SetItem(0, 1, int_to_gui(2))
            uf.page.uf_args['read_model'].sel_win.sequence.SetItem(1, 1, int_to_gui(4))
        uf.page.uf_args['read_model'].selection_win_data()

        # Renumber the models.
        uf.page.uf_args['set_model_num'].selection_win_show()
        uf.page.uf_args['set_model_num'].sel_win.add_element(None)
        if dep_check.wx_classic:
            uf.page.uf_args['set_model_num'].sel_win.sequence.SetStringItem(0, 1, int_to_gui(1))
            uf.page.uf_args['set_model_num'].sel_win.sequence.SetStringItem(1, 1, int_to_gui(3))
        else:
            uf.page.uf_args['set_model_num'].sel_win.sequence.SetItem(0, 1, int_to_gui(1))
            uf.page.uf_args['set_model_num'].sel_win.sequence.SetItem(1, 1, int_to_gui(3))
        uf.page.uf_args['set_model_num'].selection_win_data()

        # GUI data checks.
        self.assertEqual(uf.page.uf_args['read_model'].GetValue(), [2, 4])
        self.assertEqual(uf.page.uf_args['set_model_num'].GetValue(), [1, 3])

        # Execute the user function.
        uf.wizard._go_next(None)

        # Check the structural data.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 2)
        self.assertEqual(cdp.structure.structural_data[0].num, 1)
        self.assertEqual(cdp.structure.structural_data[1].num, 3)


    def test_structure_rotate(self):
        """Test the operation of the structure.rotate user function GUI window."""

        # Create the data pipe.
        self.exec_uf_pipe_create(pipe_name='PDB rotation test')

        # Open the structure.read_pdb user function window.
        uf = uf_store['structure.read_pdb']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)

        # The PDB file to operate on.
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'structures' + sep + 'trunc_ubi_pcs.pdb'
        uf.page.SetValue('file', str_to_gui(file))

        # Set the models to read.
        uf.page.SetValue('read_model', str_to_gui('6'))
        uf.page.uf_args['read_model'].selection_win_show()
        uf.page.uf_args['read_model'].sel_win.add_element(None)
        if dep_check.wx_classic:
            uf.page.uf_args['read_model'].sel_win.sequence.SetStringItem(0, 1, int_to_gui(2))
            uf.page.uf_args['read_model'].sel_win.sequence.SetStringItem(1, 1, int_to_gui(4))
        else:
            uf.page.uf_args['read_model'].sel_win.sequence.SetItem(0, 1, int_to_gui(2))
            uf.page.uf_args['read_model'].sel_win.sequence.SetItem(1, 1, int_to_gui(4))
        uf.page.uf_args['read_model'].selection_win_data()

        # Renumber the models.
        uf.page.uf_args['set_model_num'].selection_win_show()
        uf.page.uf_args['set_model_num'].sel_win.add_element(None)
        if dep_check.wx_classic:
            uf.page.uf_args['set_model_num'].sel_win.sequence.SetStringItem(0, 1, int_to_gui(1))
            uf.page.uf_args['set_model_num'].sel_win.sequence.SetStringItem(1, 1, int_to_gui(3))
        else:
            uf.page.uf_args['set_model_num'].sel_win.sequence.SetItem(0, 1, int_to_gui(1))
            uf.page.uf_args['set_model_num'].sel_win.sequence.SetItem(1, 1, int_to_gui(3))
        uf.page.uf_args['set_model_num'].selection_win_data()

        # GUI data checks.
        self.assertEqual(uf.page.uf_args['read_model'].GetValue(), [2, 4])
        self.assertEqual(uf.page.uf_args['set_model_num'].GetValue(), [1, 3])

        # Execute the user function.
        uf.wizard._go_next(None)

        # Open the structure.rotate user function window.
        uf = uf_store['structure.rotate']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)

        # Change the rotation matrix in the Sequence_2D window, without changing anything, then check it.
        uf.page.uf_args['R'].selection_win_show()
        if dep_check.wx_classic:
            uf.page.uf_args['R'].sel_win.sequence.SetStringItem(1, 1, int_to_gui(2))
        else:
            uf.page.uf_args['R'].sel_win.sequence.SetItem(1, 1, int_to_gui(2))
        uf.page.uf_args['R'].selection_win_data()
        R = uf.page.uf_args['R'].GetValue()
        print("Rotation matrix:\n%s" % R)
        self.assertEqual(len(R), 3)
        self.assertEqual(len(R[0]), 3)
        self.assertEqual(R[0][0], 1)
        self.assertEqual(R[0][1], 0)
        self.assertEqual(R[0][2], 0)
        self.assertEqual(R[1][0], 0)
        self.assertEqual(R[1][1], 2)
        self.assertEqual(R[1][2], 0)
        self.assertEqual(R[2][0], 0)
        self.assertEqual(R[2][1], 0)
        self.assertEqual(R[2][2], 1)

        # Set the rotation matrix to nothing in the wizard, open the Sequence_2D window, set a value, close the window, and check what happens.
        uf.page.uf_args['R'].SetValue(str_to_gui(''))
        uf.page.uf_args['R'].selection_win_show()
        if dep_check.wx_classic:
            uf.page.uf_args['R'].sel_win.sequence.SetStringItem(1, 1, int_to_gui(2))
        else:
            uf.page.uf_args['R'].sel_win.sequence.SetItem(1, 1, int_to_gui(2))
        uf.page.uf_args['R'].selection_win_data()
        R = uf.page.uf_args['R'].GetValue()
        print("Rotation matrix:\n%s" % R)
        self.assertEqual(len(R), 3)
        self.assertEqual(len(R[0]), 3)
        self.assertEqual(R[0][0], None)
        self.assertEqual(R[0][1], None)
        self.assertEqual(R[0][2], None)
        self.assertEqual(R[1][0], None)
        self.assertEqual(R[1][1], 2)
        self.assertEqual(R[1][2], None)
        self.assertEqual(R[2][0], None)
        self.assertEqual(R[2][1], None)
        self.assertEqual(R[2][2], None)

        # Set the rotation matrix to nothing in the wizard, open the Sequence_2D window, close the window, and check that None comes back.
        uf.page.uf_args['R'].SetValue(str_to_gui(''))
        uf.page.uf_args['R'].selection_win_show()
        uf.page.uf_args['R'].selection_win_data()
        R = uf.page.uf_args['R'].GetValue()
        print("Rotation matrix:\n%s" % R)
        self.assertEqual(R, None)

        # Set the rotation matrix to a number of invalid values, checking that they are ignored.
        for val in ['2', 'die', '[1, 2, 3]', '[1]', '[[1, 2, 3], 1, 2, 3], [1, 2, 3]]']:
            uf.page.uf_args['R'].SetValue(str_to_gui(val))
            uf.page.uf_args['R'].selection_win_show()
            uf.page.uf_args['R'].selection_win_data()
            R = uf.page.uf_args['R'].GetValue()
            print("Rotation matrix:\n%s" % R)
            self.assertEqual(R, None)

        # Set the Sequence_2D elements to invalid values.
        for val in ['x']:
            uf.page.uf_args['R'].SetValue(str_to_gui(''))
            uf.page.uf_args['R'].selection_win_show()
            if dep_check.wx_classic:
                uf.page.uf_args['R'].sel_win.sequence.SetStringItem(1, 1, str_to_gui(val))
                uf.page.uf_args['R'].sel_win.sequence.SetStringItem(0, 0, int_to_gui(1))
            else:
                uf.page.uf_args['R'].sel_win.sequence.SetItem(1, 1, str_to_gui(val))
                uf.page.uf_args['R'].sel_win.sequence.SetItem(0, 0, int_to_gui(1))
            uf.page.uf_args['R'].selection_win_data()
            R = uf.page.uf_args['R'].GetValue()
            print("Rotation matrix:\n%s" % R)
            self.assertEqual(len(R), 3)
            self.assertEqual(len(R[0]), 3)
            self.assertEqual(R[0][0], 1.0)
            self.assertEqual(R[0][1], None)
            self.assertEqual(R[0][2], None)
            self.assertEqual(R[1][0], None)
            self.assertEqual(R[1][1], None)
            self.assertEqual(R[1][2], None)
            self.assertEqual(R[2][0], None)
            self.assertEqual(R[2][1], None)
            self.assertEqual(R[2][2], None)

        # Check the structural data.
        self.assertTrue(hasattr(cdp, 'structure'))
        self.assertTrue(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 2)
        self.assertEqual(cdp.structure.structural_data[0].num, 1)
        self.assertEqual(cdp.structure.structural_data[1].num, 3)


    def test_value_set(self):
        """Test the full operation of the value.set user function GUI window."""

        # Create the data pipe.
        self.exec_uf_pipe_create(pipe_name='value.set user function test')

        # Create a spin to add data to.
        uf = uf_store['spin.create']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)
        uf.page.SetValue('res_num', int_to_gui(1))
        uf.page.SetValue('res_name', str_to_gui('Gly'))
        uf.page.SetValue('spin_name', str_to_gui('N'))
        uf.wizard._go_next(None)

        # Open the value.set user function window.
        uf = uf_store['value.set']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)
        uf.page.SetValue('val', float_to_gui(-0.000172))
        uf.page.SetValue('param', str_to_gui('csa'))
        uf.wizard._go_next(None)
