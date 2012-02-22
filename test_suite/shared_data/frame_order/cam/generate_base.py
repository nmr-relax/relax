###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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

# Module docstring.
"""Module containing the base class for the distribution and alignment data generation."""

# Python module imports.
from copy import deepcopy
from math import pi
from numpy import array, cross, dot, float16, float64, transpose, zeros
from numpy.linalg import norm
import sys

# relax module imports.
from generic_fns.angles import wrap_angles
from generic_fns.frame_order import print_frame_order_2nd_degree
from generic_fns.mol_res_spin import spin_loop
from maths_fns.coord_transform import cartesian_to_spherical
from maths_fns.kronecker_product import kron_prod
from maths_fns.rotation_matrix import axis_angle_to_R, R_to_euler_zyz
from prompt.interpreter import Interpreter
from relax_io import open_write_file


class Main:
    # The pivot and CoM for the CaM system.
    pivot = array([ 37.254, 0.5, 16.7465])
    com = array([ 26.83678091, -12.37906417,  28.34154128])

    def run(self):
        """Generate the distribution and alignment data."""

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Build the axis system.
        self.build_axes()
        self._print_axis_system()
        self.axes_to_pdb()

        # Create the distribution.
        self._create_distribution()

        # Back-calculate the RDCs and PCSs.
        self._back_calc()

        # Save a state file for debugging.
        self.interpreter.state.save('generate_distribution', force=True)


    def _back_calc(self):
        """Calculate the RDCs and PCSs expected for the structural distribution."""

        # Set the values needed to calculate the dipolar constant.
        self.interpreter.value.set(1.041 * 1e-10, 'r', spin_id="@N")
        self.interpreter.value.set('15N', 'heteronuc_type', spin_id="@N")
        self.interpreter.value.set('1H', 'proton_type', spin_id="@N")

        # Load the tensors.
        self.interpreter.script('../tensors.py')

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
            self.interpreter.temperature(id=tag, temp=303)
            self.interpreter.frq.set(id=tag, frq=900e6)

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
            self.interpreter.rdc.write(align_id=tag, file='rdc_%s.txt'%tensors[i], bc=True, force=True)
            self.interpreter.pcs.write(align_id=tag, file='pcs_%s.txt'%tensors[i], bc=True, force=True)

        # Store the state.
        self.interpreter.state.save('back_calc', force=True)


    def _backup_pos(self):
        """Back up the positional data prior to the rotations."""

        # Loop over the spins.
        for spin in spin_loop():
            # Store and then reinitalise the atomic position.
            if hasattr(spin, 'pos'):
                spin.orig_pos = array(spin.pos, float16)
                spin.pos = zeros((self.N, 3), float16)

            # Store and then reinitalise the bond vector.
            if hasattr(spin, 'xh_vect'):
                spin.orig_vect = array(spin.xh_vect[0], float16)
                spin.xh_vect = zeros((self.N, 3), float16)


    def _create_distribution(self):
        """Generate the distribution of structures."""

        # Create a data pipe.
        self.interpreter.pipe.create('distribution', 'N-state')

        # Load the original PDB.
        self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir='..')

        # Load the spins.
        self.interpreter.structure.load_spins('@N')
        self.interpreter.structure.load_spins('@H')

        # Load the NH vectors.
        self.interpreter.structure.vectors(spin_id='@N', attached='H', ave=False)

        # Back up the original positional data.
        self._backup_pos()

        # Init a rotation matrix and the frame order matrix.
        self.R = zeros((3, 3), float16)
        self.daeg = zeros((9, 9), float64)

        # Open the output files.
        rot_file = open_write_file('rotations', compress_type=1, force=True)

        # Print out.
        sys.stdout.write("\n\nRotating %s states:\n\n" % self.N)

        # Load N copies of the original C-domain.
        for i in range(self.N):
            # Print out.
            self._progress(i)

            # Generate the distribution specific rotation.
            self.rotation(i)

            # Loop over the spins to rotate the vectors and positions.
            for spin in spin_loop():
                # Rotate the atomic position.
                if hasattr(spin, 'pos'):
                    spin.pos[i] = dot(self.R, (spin.orig_pos - self.pivot)) + self.pivot

                # Rotate the NH vector.
                if hasattr(spin, 'xh_vect'):
                    spin.xh_vect[i] = dot(self.R, spin.orig_vect)

            # Decompose the rotation into Euler angles and store them.
            a, b, g = R_to_euler_zyz(self.R)
            rot_file.write('%10.7f %10.7f %10.7f\n' % (a, b, g))

            # The frame order matrix component.
            self.daeg += kron_prod(self.R, self.R)

        # Print out.
        sys.stdout.write('\n\n')

        # Frame order matrix averaging.
        self.daeg = self.daeg / self.N

        # Write out the frame order matrix.
        file = open('frame_order_matrix', 'w')
        print_frame_order_2nd_degree(self.daeg, file=file)


    def _print_axis_system(self):
        """Print out of the full system."""

        # Open the file.
        file = open('axis_system', 'w')

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
        r, t, p = cartesian_to_spherical(self.axes[:,2])
        file.write("\nSpherical angles of the z-axis:\n")
        file.write("    theta: %.20f\n" % t)
        file.write("    phi:   %.20f\n" % wrap_angles(p, 0, 2*pi))


    def _progress(self, i, a=5, b=100):
        """A simple progress write out."""

        # The spinner characters.
        chars = ['-', '\\', '|', '/']

        # A spinner.
        if i % a == 0:
            sys.stdout.write('\b%s' % chars[i%4])
            sys.stdout.flush()

        # Dump the progress.
        if i % b == 0:
            sys.stdout.write('\b%i\n' % i)


    def axes_to_pdb_full(self):
        """Create a PDB for the motional axis system."""

        # Create a data pipe for the data.
        self.interpreter.pipe.create('axes', 'N-state')

        # The end points of the vectors.
        end_pt_x = self.axes[:,0] * norm(self.com - self.pivot) + self.pivot
        end_pt_y = self.axes[:,1] * norm(self.com - self.pivot) + self.pivot
        end_pt_z = self.axes[:,2] * norm(self.com - self.pivot) + self.pivot

        # Add atoms for the system.
        self.interpreter.structure.add_atom(atom_name='C', res_name='AXE', res_num=1, pos=self.pivot, element='C')
        self.interpreter.structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt_x, element='N')
        self.interpreter.structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt_y, element='N')
        self.interpreter.structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt_z, element='N')

        # Connect the atoms to form the vectors.
        self.interpreter.structure.connect_atom(index1=0, index2=1)
        self.interpreter.structure.connect_atom(index1=0, index2=2)
        self.interpreter.structure.connect_atom(index1=0, index2=3)

        # Write out the PDB.
        self.interpreter.structure.write_pdb('axis.pdb', compress_type=0, force=True)


    def axes_to_pdb_main_axis(self):
        """Create a PDB for the major axis of the motional axis system."""

        # Create a data pipe for the data.
        self.interpreter.pipe.create('axes', 'N-state')

        # The end points of the vectors.
        end_pt = self.axes[:,2] * norm(self.com - self.pivot) + self.pivot

        # Add atoms for the system.
        self.interpreter.structure.add_atom(atom_name='C', res_name='AXE', res_num=1, pos=self.pivot, element='C')
        self.interpreter.structure.add_atom(atom_name='N', res_name='AXE', res_num=1, pos=end_pt, element='N')

        # Connect the atoms to form the vectors.
        self.interpreter.structure.connect_atom(index1=0, index2=1)

        # Write out the PDB.
        self.interpreter.structure.write_pdb('axis.pdb', compress_type=0, force=True)


    def build_axes_alt(self):
        """An alternative axis system for the CaM system."""

        # The z-axis for the rotations (the pivot point to CoM axis).
        axis_z = self.com - self.pivot
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

        # Print out.
        print("Tilt axis: %s, norm = %s" % (repr(tilt_axis), norm(tilt_axis)))
        print("CoM-pivot axis: %s, norm = %s" % (repr(axis_z), norm(axis_z)))
        print("Rotation axis: %s, norm = %s" % (repr(self.axes[:,2]), norm(self.axes[:,2])))


    def build_axes_pivot_com(self):
        """A standard axis system for the CaM system with the z-axis along the pivot-com axis."""

        # The z-axis for the rotations (the pivot point to CoM axis).
        axis_z = self.com - self.pivot
        axis_z = axis_z / norm(axis_z)

        # The y-axis (to check the torsion angle).
        axis_y = cross(axis_z, array([0, 0, 1]))
        axis_y = axis_y / norm(axis_y)

        # The x-axis.
        axis_x = cross(axis_y, axis_z)
        axis_x = axis_x / norm(axis_x)

        # The eigenframe.
        self.axes = transpose(array([axis_x, axis_y, axis_z]))
