###############################################################################
#                                                                             #
# Copyright (C) 2012-2014 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module containing the base class for the distribution and alignment data generation."""

# Python module imports.
from math import pi
from numpy import array, cross, dot, eye, float64, transpose, zeros
from numpy.linalg import norm
from os import getcwd, sep
import sys

# relax module imports.
from lib.check_types import float16, is_float
from lib.frame_order.format import print_frame_order_2nd_degree
from lib.geometry.angles import wrap_angles
from lib.geometry.coord_transform import cartesian_to_spherical
from lib.geometry.rotations import axis_angle_to_R, R_to_euler_zyz
from lib.io import open_write_file
from lib.linear_algebra.kronecker_product import kron_prod
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import spin_loop
from prompt.interpreter import Interpreter
from status import Status; status = Status()


class Main:
    # The pivot and CoM for the CaM system.
    PIVOT = array([ 37.254, 0.5, 16.7465])
    COM = array([ 26.83678091, -12.37906417,  28.34154128])
    
    # The number of rotation modes.
    MODES = 1
    
    # The number of states for each rotation mode.
    N = 100
    
    # The tilt angles.
    TILT_ANGLE = 0
    INC = 0
    
    # The PDB distribution flag.
    DIST_PDB = False

    # The rotations file.
    ROT_FILE = True

    # The state file.
    SAVE_STATE = True

    def run(self, save_path=None):
        """Generate the distribution and alignment data.
        
        @keyword save_path: The path to place the files into.  If set to None, then the current path will be used.
        @type save_path:    None or str
        """

        # The paths to the files.
        self.path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'+sep
        self.save_path = save_path
        if self.save_path == None:
            self.save_path = getcwd()
    
        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)
    
        # Build the axis system.
        self.build_axes()
        self.print_axis_system()
        self.axes_to_pdb()
    
        # Create the distribution.
        self._multi_system()
        self._create_distribution()
    
        # Back-calculate the RDCs and PCSs.
        self._back_calc()

        # Save a state file for debugging.
        if self.SAVE_STATE:
            self.interpreter.state.save('generate_distribution', dir=self.save_path, force=True)


    def _back_calc(self):
        """Calculate the RDCs and PCSs expected for the structural distribution."""
    
        # Load the tensors.
        self.interpreter.script(self.path+'tensors.py')
    
        # Set up the model.
        self.interpreter.n_state_model.select_model(model='fixed')
        self.interpreter.n_state_model.number_of_states(self.N)
    
        # Set the paramagnetic centre.
        self.interpreter.paramag.centre(pos=[35.934, 12.194, -4.206])
    
        # Loop over the alignments.
        tensors = ['dy', 'tb', 'tm', 'er']
        for i in range(len(tensors)):
            # The tag.
            tag = tensors[i]
    
            # The temperature and field strength.
            self.interpreter.spectrometer.temperature(id=tag, temp=303)
            self.interpreter.spectrometer.frequency(id=tag, frq=900e6)
    
            # Back-calculate the data.
            self.interpreter.rdc.back_calc(tag)
            self.interpreter.pcs.back_calc(tag)
    
            # Set 1 Hz and 0.1 ppm errors on all data.
            for spin in spin_loop():
                # Init.
                if not hasattr(spin, 'rdc_err'):
                    spin.rdc_err = {}
                if not hasattr(spin, 'pcs_err'):
                    spin.pcs_err = {}
    
                # Set the errors.
                spin.rdc_err[tag] = 1.0
                spin.pcs_err[tag] = 0.1
    
            # Write the data.
            self.interpreter.rdc.write(align_id=tag, file='rdc_%s.txt'%tensors[i], dir=self.save_path, bc=True, force=True)
            self.interpreter.pcs.write(align_id=tag, file='pcs_%s.txt'%tensors[i], dir=self.save_path, bc=True, force=True)


    def _backup_pos(self):
        """Back up the positional data prior to the rotations."""
    
        # Store and then reinitalise the atomic position.
        for spin in spin_loop():
            if hasattr(spin, 'pos'):
                spin.orig_pos = array(spin.pos, float16)
                spin.pos = zeros((self.N**self.MODES, 3), float16)
    
        # Store and then reinitalise the bond vector.
        for interatom in interatomic_loop():
            if hasattr(interatom, 'vector'):
                interatom.orig_vect = array(interatom.vector, float16)
                interatom.vector = zeros((self.N**self.MODES, 3), float16)


    def _create_distribution(self):
        """Generate the distribution of structures."""

        # Create a data pipe.
        self.interpreter.pipe.create('distribution', 'N-state')

        # Load the original PDB.
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=self.path, set_mol_name='C-dom')

        # Set up the 15N and 1H spins.
        self.interpreter.structure.load_spins(spin_id='@N', ave_pos=False)
        self.interpreter.structure.load_spins(spin_id='@H', ave_pos=False)
        self.interpreter.spin.isotope(isotope='15N', spin_id='@N')
        self.interpreter.spin.isotope(isotope='1H', spin_id='@H')

        # Define the magnetic dipole-dipole relaxation interaction.
        self.interpreter.interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
        self.interpreter.interatom.set_dist(spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
        self.interpreter.interatom.unit_vectors()

        # Back up the original positional data.
        self._backup_pos()

        # Init a rotation matrix and the frame order matrix.
        self.R = zeros((3, 3), float16)
        self.daeg = zeros((9, 9), float64)

        # Open the output files.
        if self.ROT_FILE:
            rot_file = open_write_file('rotations', dir=self.save_path, compress_type=1, force=True)

        # Printout.
        sys.stdout.write("\n\nRotating %s states:\n\n" % self.N)

        # Load N copies of the original C-domain.
        for global_index, mode_indices in self._state_loop():
            self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=self.path, set_mol_name='C-dom', set_model_num=global_index+1)

        # Turn off the relax interpreter echoing to allow the progress meter to be shown correctly.
        self.interpreter.off()

        # Loop over each position.
        for global_index, mode_indices in self._state_loop():
            # The progress meter.
            self._progress(global_index)

            # Total rotation matrix (for construction of the frame order matrix).
            total_R = eye(3)

            # Loop over each motional mode.
            for motion_index in range(self.MODES):
                # Generate the distribution specific rotation.
                self.rotation(mode_indices[motion_index], motion_index=motion_index)

                # Rotate the atomic position.
                for spin in spin_loop():
                    if hasattr(spin, 'pos'):
                        spin.pos[global_index] = dot(self.R, (spin.orig_pos[0] - self.PIVOT[motion_index])) + self.PIVOT[motion_index]

                # Rotate the NH vector.
                for interatom in interatomic_loop():
                    if hasattr(interatom, 'vector'):
                        interatom.vector[global_index] = dot(self.R, interatom.orig_vect)

                # Decompose the rotation into Euler angles and store them.
                if self.ROT_FILE:
                    a, b, g = R_to_euler_zyz(self.R)
                    rot_file.write('Mode %i:  %10.7f %10.7f %10.7f\n' % (motion_index, a, b, g))

                # Rotate the structure for the PDB distribution.
                if self.DIST_PDB:
                    self.interpreter.structure.rotate(R=self.R, origin=self.PIVOT[motion_index], model=global_index+1)

                # Contribution to the total rotation.
                total_R = dot(self.R, total_R)

            # The frame order matrix component.
            self.daeg += kron_prod(total_R, total_R)

        # Print out.
        sys.stdout.write('\n\n')

        # Frame order matrix averaging.
        self.daeg = self.daeg / self.N**self.MODES

        # Write out the frame order matrix.
        file = open(self.save_path+sep+'frame_order_matrix', 'w')
        print_frame_order_2nd_degree(self.daeg, file=file, places=8)

        # Write out the PDB distribution.
        self.interpreter.on()
        if self.DIST_PDB:
            self.interpreter.structure.write_pdb('distribution.pdb', compress_type=2, force=True)


    def print_axis_system(self):
        """Dummy base method for printing out the axis system to a file."""


    def print_axis_system_full(self):
        """Print out of the full system to file."""

        # Open the file.
        file = open(self.save_path+sep+'axis_system', 'w')

        # Header.
        file.write("\n")
        file.write("The motional axis system\n")
        file.write("========================\n")

        # The full axis system.
        file.write("\nThe full axis system:\n")
        string = ''
        for i in range(3):
            string += '['
            for j in range(3):
                string += "%24.20f" % self.axes[i, j]
            string += ']\n'
        file.write(string)

        # The Euler angles.
        a, b, g = R_to_euler_zyz(self.axes)
        file.write("\nEuler angles of the system:\n")
        file.write("    alpha: %.20f\n" % a)
        file.write("    beta:  %.20f\n" % b)
        file.write("    gamma: %.20f\n" % g)

        # The spherical angle system.
        r, t, p = cartesian_to_spherical(self.axes[:, 2])
        file.write("\nSpherical angles of the z-axis:\n")
        file.write("    theta: %.20f\n" % t)
        file.write("    phi:   %.20f\n" % wrap_angles(p, 0, 2*pi))


    def _multi_system(self):
        """Convert the angle, pivot and axis data structures for handling multiple motional modes."""

        # The tilt angle.
        if is_float(self.TILT_ANGLE):
            self.TILT_ANGLE = [self.TILT_ANGLE]

        # The increment value.
        if is_float(self.INC):
            self.INC = [self.INC]

        # The pivot.
        if is_float(self.PIVOT[0]):
            self.PIVOT = [self.PIVOT]

        # The axis.
        if is_float(self.axes[0]):
            self.axes = [self.axes]


    def _progress(self, i, a=5, b=100):
        """A simple progress write out (which goes to the terminal STDERR)."""

        # The spinner characters.
        chars = ['-', '\\', '|', '/']

        # A spinner.
        if i % a == 0:
            sys.stderr.write('\b%s' % chars[i%4])
            sys.stderr.flush()

        # Dump the progress.
        if i % b == 0:
            sys.stderr.write('\b%i\n' % i)


    def _state_loop(self):
        """Generator method for looping over all states of all motional modes.

        @return:    The global index, the list of indices for each mode
        @rtype:     int, list of int
        """

        # Single mode.
        if self.MODES == 1:
            for i in range(self.N):
                yield i, [i]

        # Double mode.
        if self.MODES == 2:
            global_index = -1
            for i in range(self.N):
                for j in range(self.N):
                    global_index += 1
                    yield global_index, [i, j]

    def axes_to_pdb(self):
        """Dummy base method for creating a PDB for the motional axis system."""


    def axes_to_pdb_full(self):
        """Create a PDB for the motional axis system."""

        # Create a data pipe for the data.
        self.interpreter.pipe.create('axes', 'N-state')

        # The end points of the vectors.
        end_pt_x = self.axes[:, 0] * norm(self.COM - self.PIVOT) + self.PIVOT
        end_pt_y = self.axes[:, 1] * norm(self.COM - self.PIVOT) + self.PIVOT
        end_pt_z = self.axes[:, 2] * norm(self.COM - self.PIVOT) + self.PIVOT

        # Add atoms for the system.
        self.interpreter.structure.add_atom(atom_name='C', res_name='AXE', res_num=1, pos=self.PIVOT, element='C')
        self.interpreter.structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt_x, element='N')
        self.interpreter.structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt_y, element='N')
        self.interpreter.structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt_z, element='N')

        # Connect the atoms to form the vectors.
        self.interpreter.structure.connect_atom(index1=0, index2=1)
        self.interpreter.structure.connect_atom(index1=0, index2=2)
        self.interpreter.structure.connect_atom(index1=0, index2=3)

        # Write out the PDB.
        self.interpreter.structure.write_pdb('axis.pdb', dir=self.save_path, compress_type=0, force=True)


    def axes_to_pdb_main_axis(self):
        """Create a PDB for the major axis of the motional axis system."""

        # Create a data pipe for the data.
        self.interpreter.pipe.create('axes', 'N-state')

        # The end points of the vectors.
        end_pt = self.axes[:, 2] * norm(self.COM - self.PIVOT) + self.PIVOT

        # Add atoms for the system.
        self.interpreter.structure.add_atom(atom_name='C', res_name='AXE', res_num=1, pos=self.PIVOT, element='C')
        self.interpreter.structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt, element='N')

        # Connect the atoms to form the vectors.
        self.interpreter.structure.connect_atom(index1=0, index2=1)

        # Write out the PDB.
        self.interpreter.structure.write_pdb('axis.pdb', dir=self.save_path, compress_type=0, force=True)


    def build_axes(self):
        """Dummy base method for creating the axis system."""


    def build_axes_alt(self):
        """An alternative axis system for the CaM system."""

        # The z-axis for the rotations (the pivot point to CoM axis).
        axis_z = self.COM - self.PIVOT
        axis_z = axis_z / norm(axis_z)

        # The y-axis (to check the torsion angle).
        axis_y = cross(axis_z, array([0, 0, 1]))
        axis_y = axis_y / norm(axis_y)

        # The x-axis.
        axis_x = cross(axis_y, axis_z)
        axis_x = axis_x / norm(axis_x)

        # The eigenframe.
        axes = transpose(array([axis_x, axis_y, axis_z]))

        # Init a rotation matrix.
        R = zeros((3, 3), float64)

        # Tilt the axes system by x degrees.
        tilt_axis = cross(axis_z, array([0, 0, 1]))
        tilt_axis = tilt_axis / norm(tilt_axis)
        axis_angle_to_R(tilt_axis, self.TILT_ANGLE * 2.0 * pi / 360.0, R)

        # Rotate the eigenframe.
        self.axes = dot(R, axes)
        alpha, beta, gamma = R_to_euler_zyz(self.axes)

        # Print out.
        print("Tilt axis: %s, norm = %s" % (repr(tilt_axis), norm(tilt_axis)))
        print("CoM-pivot axis: %s, norm = %s" % (repr(axis_z), norm(axis_z)))
        print("Rotation axis: %s, norm = %s" % (repr(self.axes[:, 2]), norm(self.axes[:, 2])))
        print("Full axis system:\n%s" % self.axes)
        print("Full axis system Euler angles:\n\talpha: %s\n\tbeta: %s\n\tgamma: %s" % (repr(alpha), repr(beta), repr(gamma)))


    def build_axes_pivot_com(self):
        """A standard axis system for the CaM system with the z-axis along the pivot-com axis."""

        # The z-axis for the rotations (the pivot point to CoM axis).
        axis_z = self.COM - self.PIVOT
        axis_z = axis_z / norm(axis_z)

        # The y-axis (to check the torsion angle).
        axis_y = cross(axis_z, array([0, 0, 1]))
        axis_y = axis_y / norm(axis_y)

        # The x-axis.
        axis_x = cross(axis_y, axis_z)
        axis_x = axis_x / norm(axis_x)

        # The eigenframe.
        self.axes = transpose(array([axis_x, axis_y, axis_z]))
