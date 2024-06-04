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
import locale
from math import pi
from numpy import array, cross, dot, eye, float64, tensordot, transpose, zeros
from lib.compat import norm
from os import getcwd, sep
import sys

# relax module imports.
from lib.check_types import float128, is_float
from lib.frame_order.format import print_frame_order_2nd_degree
from lib.geometry.angles import wrap_angles
from lib.geometry.coord_transform import cartesian_to_spherical
from lib.geometry.rotations import axis_angle_to_R, R_to_euler_zyz
from lib.io import open_write_file
from lib.linear_algebra.kronecker_product import kron_prod
from lib.periodic_table import periodic_table
from lib.physical_constants import dipolar_constant, pcs_constant
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import return_spin, spin_loop
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

        # Set up for the progress meter (commas between the thousands).
        try:
            locale.setlocale(locale.LC_ALL, 'en_US')
        except:
            pass

        # Build the axis system.
        self.build_axes()
        self.print_axis_system()
        self.axes_to_pdb()

        # Set up the system.
        self._multi_system()

        # Set up the data pipe.
        self._pipe_setup()

        # Calculate the RDC data.
        self._calculate_rdc()

        # Calculate the PCS data.
        self._calculate_pcs()

        # Create the distribution of structures.
        if self.DIST_PDB:
            self._create_distribution()

        # Save a state file for debugging.
        if self.SAVE_STATE:
            self.interpreter.state.save('generate_distribution', dir=self.save_path, force=True)


    def _calculate_pcs(self):
        """Calculate the averaged PCS for all states."""

        # Printout.
        sys.stdout.write("\n\nRotating %s states for the PCS:\n\n" % locale.format_string("%d", self.N**self.MODES, grouping=True))

        # Turn off the relax interpreter echoing to allow the progress meter to be shown correctly.
        self.interpreter.off()

        # Set up some data structures for faster calculations.
        spins = []
        spin_pos = []
        d = {}
        for tag in self._tensors:
            d[tag] = []
        for spin in spin_loop():
            # Nothing to do.
            if not hasattr(spin, 'pos'):
                continue

            # Initialise the PCS structure (as a 1D numpy.float128 array for speed and minimising truncation artifacts).
            spin.pcs = {}
            for tag in self._tensors:
                spin.pcs[tag] = zeros(1, float128)

            # Pack the spin containers and positions.
            spins.append(spin)
            spin_pos.append(spin.pos[0])

            # Calculate the partial PCS constant (with no vector length).
            for tag in self._tensors:
                d[tag].append(pcs_constant(cdp.temperature[tag], cdp.spectrometer_frq[tag] * 2.0 * pi / periodic_table.gyromagnetic_ratio('1H'), 1.0))

        # Repackage the data for speed.
        spin_pos = array(spin_pos, float64)
        num_spins = len(spin_pos)
        for tag in self._tensors:
            d[tag] = array(d[tag], float64)

        # Store the alignment tensors.
        A = []
        for i in range(len(self._tensors)):
            A.append(cdp.align_tensors[i].A)

        # Loop over each position.
        for global_index, mode_indices in self._state_loop():
            # The progress meter.
            self._progress(global_index)

            # Data initialisation.
            new_pos = spin_pos

            # Loop over each motional mode.
            for motion_index in range(self.MODES):
                # Generate the distribution specific rotation.
                self.rotation(mode_indices[motion_index], motion_index=motion_index)

                # Rotate the atomic positions.
                new_pos = transpose(tensordot(self.R, transpose(new_pos - self.PIVOT[motion_index]), axes=1)) + self.PIVOT[motion_index]

            # The vectors.
            vectors = new_pos - cdp.paramagnetic_centre

            # The lengths.
            r = norm(vectors, axis=1)

            # The scaling factor that includes the Angstrom to meter converted length cubed and the ppm conversion.
            fact = 1e6 / (r / 1e10)**3

            # Normalise.
            vectors = transpose(vectors) / r

            # Loop over each alignment.
            for i in range(len(self._tensors)):
                # Calculate the PCS as quickly as possible (the 1e36 is from the 1e10**3 Angstrom conversion and the 1e6 ppm conversion).
                pcss = d[self._tensors[i]] * fact * tensordot(transpose(vectors), tensordot(A[i], vectors, axes=1), axes=1)

                # Store the values.
                for j in range(len(spins)):
                    spins[j].pcs[self._tensors[i]][0] += pcss[j, j]

        # Print out.
        sys.stdout.write('\n\n')

        # Reactive the interpreter echoing.
        self.interpreter.on()

        # Average the PCS and write the data.
        for tag in self._tensors:
            # Average.
            for spin in spin_loop():
                spin.pcs[tag] = spin.pcs[tag][0] / self.N**self.MODES

            # Save.
            self.interpreter.pcs.write(align_id=tag, file='pcs_%s.txt'%tag, dir=self.save_path, force=True)


    def _calculate_rdc(self):
        """Calculate the averaged RDC for all states."""

        # Open the output files.
        if self.ROT_FILE:
            rot_file = open_write_file('rotations', dir=self.save_path, compress_type=1, force=True)

        # Printout.
        sys.stdout.write("\n\nRotating %s states for the RDC:\n\n" % locale.format_string("%d", self.N**self.MODES, grouping=True))

        # Turn off the relax interpreter echoing to allow the progress meter to be shown correctly.
        self.interpreter.off()

        # Set up some data structures for faster calculations.
        interatoms = []
        vectors = []
        d = []
        for interatom in interatomic_loop():
            # Nothing to do.
            if not hasattr(interatom, 'vector'):
                continue

            # Initialise the RDC structure (as a 1D numpy.float128 array for speed and minimising truncation artifacts).
            interatom.rdc = {}
            for tag in self._tensors:
                interatom.rdc[tag] = zeros(1, float128)

            # Pack the interatomic containers and vectors.
            interatoms.append(interatom)
            vectors.append(interatom.vector)

            # Get the spins.
            spin1 = return_spin(spin_id=interatom.spin_id1)
            spin2 = return_spin(spin_id=interatom.spin_id2)

            # Gyromagnetic ratios.
            g1 = periodic_table.gyromagnetic_ratio(spin1.isotope)
            g2 = periodic_table.gyromagnetic_ratio(spin2.isotope)

            # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
            d.append(3.0/(2.0*pi) * dipolar_constant(g1, g2, interatom.r))

        # Repackage the data for speed.
        vectors = transpose(array(vectors, float64))
        d = array(d, float64)
        num_interatoms = len(vectors)

        # Store the alignment tensors.
        A = []
        for i in range(len(self._tensors)):
            A.append(cdp.align_tensors[i].A)

        # Loop over each position.
        for global_index, mode_indices in self._state_loop():
            # The progress meter.
            self._progress(global_index)

            # Total rotation matrix (for construction of the frame order matrix).
            total_R = eye(3)

            # Data initialisation.
            new_vect = vectors

            # Loop over each motional mode.
            for motion_index in range(self.MODES):
                # Generate the distribution specific rotation.
                self.rotation(mode_indices[motion_index], motion_index=motion_index)

                # Rotate the NH vector.
                new_vect = dot(self.R, new_vect)

                # Decompose the rotation into Euler angles and store them.
                if self.ROT_FILE:
                    a, b, g = R_to_euler_zyz(self.R)
                    rot_file.write('Mode %i:  %10.7f %10.7f %10.7f\n' % (motion_index, a, b, g))

                # Contribution to the total rotation.
                total_R = dot(self.R, total_R)

            # Loop over each alignment.
            for i in range(len(self._tensors)):
                # Calculate the RDC as quickly as possible.
                rdcs = d * tensordot(transpose(new_vect), tensordot(A[i], new_vect, axes=1), axes=1)

                # Store the values.
                for j in range(len(interatoms)):
                    interatoms[j].rdc[self._tensors[i]][0] += rdcs[j, j]

            # The frame order matrix component.
            self.daeg += kron_prod(total_R, total_R)

        # Print out.
        sys.stdout.write('\n\n')

        # Frame order matrix averaging.
        self.daeg = self.daeg / self.N**self.MODES

        # Write out the frame order matrix.
        file = open(self.save_path+sep+'frame_order_matrix', 'w')
        print_frame_order_2nd_degree(self.daeg, file=file, places=8)

        # Reactive the interpreter echoing.
        self.interpreter.on()

        # Average the RDC and write the data.
        for tag in self._tensors:
            # Average.
            for interatom in interatomic_loop():
                interatom.rdc[tag] = interatom.rdc[tag][0] / self.N**self.MODES

            # Save.
            self.interpreter.rdc.write(align_id=tag, file='rdc_%s.txt'%tag, dir=self.save_path, force=True)


    def _create_distribution(self):
        """Generate the distribution of structures."""

        # Printout.
        sys.stdout.write("\n\nRotating %s states to create the PDB distribution:\n\n" % self.N**self.MODES)

        # Load N copies of the original C-domain for the distribution.
        for global_index, mode_indices in self._state_loop():
            self.interpreter.structure.read_pdb('1J7P_1st_NH.pdb', dir=self.path, set_mol_name='C-dom', set_model_num=global_index+1)

        # Turn off the relax interpreter echoing to allow the progress meter to be shown correctly.
        self.interpreter.off()

        # Loop over each position.
        for global_index, mode_indices in self._state_loop():
            # The progress meter.
            self._progress(global_index)

            # Loop over each motional mode.
            for motion_index in range(self.MODES):
                # Generate the distribution specific rotation.
                self.rotation(mode_indices[motion_index], motion_index=motion_index)

                # Rotate the structure for the PDB distribution.
                self.interpreter.structure.rotate(R=self.R, origin=self.PIVOT[motion_index], model=global_index+1)

        # Print out.
        sys.stdout.write('\n\n')

        # Reactive the interpreter echoing.
        self.interpreter.on()

        # Write out the PDB distribution.
        self.interpreter.structure.write_pdb('distribution.pdb', compress_type=2, force=True)


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


    def _pipe_setup(self):
        """Set up the main data pipe."""

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

        # Init a rotation matrix and the frame order matrix.
        self.R = zeros((3, 3), float64)
        self.daeg = zeros((9, 9), float64)

        # Load the tensors.
        self._tensors = ['dy', 'tb', 'tm', 'er']
        self.interpreter.script(self.path+'tensors.py')

        # The alignment specific data.
        for tag in self._tensors:
            # The temperature and field strength.
            self.interpreter.spectrometer.temperature(id=tag, temp=303)
            self.interpreter.spectrometer.frequency(id=tag, frq=900e6)

            # Set 1 Hz errors on all RDC data.
            for interatom in interatomic_loop():
                if not hasattr(interatom, 'rdc_err'):
                    interatom.rdc_err = {}
                interatom.rdc_err[tag] = 1.0

            # Set 0.1 ppm errors on all PCS data.
            for spin in spin_loop():
                if not hasattr(spin, 'pcs_err'):
                    spin.pcs_err = {}
                spin.pcs_err[tag] = 0.1

        # Set up the IDs.
        cdp.rdc_ids = self._tensors
        cdp.pcs_ids = self._tensors

        # Set up the model.
        self.interpreter.n_state_model.select_model(model='fixed')
        self.interpreter.n_state_model.number_of_states(self.N)

        # Set the paramagnetic centre.
        self.interpreter.paramag.centre(pos=[35.934, 12.194, -4.206])


    def _progress(self, i, a=250, b=10000):
        """A simple progress write out (which goes to the terminal STDERR)."""

        # The spinner characters.
        chars = ['-', '\\', '|', '/']

        # A spinner.
        if i % a == 0:
            sys.stderr.write('\b%s' % chars[i%4])
            sys.stderr.flush()

        # Dump the progress.
        if i % b == 0:
            num = locale.format_string("%d", i, grouping=True)
            sys.stderr.write('\b%12s\n' % num)


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

        # Printout.
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
        alpha, beta, gamma = R_to_euler_zyz(self.axes)

        # Printout.
        print("CoM-pivot axis: %s, norm = %s" % (repr(axis_z), norm(axis_z)))
        print("Rotation axis: %s, norm = %s" % (repr(self.axes[:, 2]), norm(self.axes[:, 2])))
        print("Full axis system:\n%s" % self.axes)
        print("Full axis system Euler angles:\n\talpha: %s\n\tbeta: %s\n\tgamma: %s" % (repr(alpha), repr(beta), repr(gamma)))
