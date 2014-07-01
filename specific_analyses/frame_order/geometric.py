###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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
"""Module for handling the geometric representation of the frame order motions."""

# Python module imports.
from copy import deepcopy
from math import pi
from numpy import array, dot, eye, float64, transpose, zeros
import sys

# relax module imports.
from lib.frame_order.rotor_axis import create_rotor_axis_alpha, create_rotor_axis_euler, create_rotor_axis_spherical
from lib.geometry.rotations import euler_to_R_zyz, two_vect_to_R
from lib.io import open_write_file
from lib.order import order_parameters
from lib.structure.cones import Iso_cone, Pseudo_elliptic
from lib.structure.geometric import generate_vector_residues
from lib.structure.internal.object import Internal
from lib.structure.represent.cone import cone
from lib.structure.represent.rotor import rotor
from lib.text.sectioning import subsection
from pipe_control.structure.mass import pipe_centre_of_mass
from specific_analyses.frame_order.data import domain_moving, generate_pivot


def add_axes(structure=None, size=None):
    """Add the axis system for the current frame order model to the structural object.

    @keyword structure: The internal structural object to add the rotor objects to.
    @type structure:    lib.structure.internal.object.Internal instance
    @keyword size:      The size of the geometric object in Angstroms.
    @type size:         float
    """

    # Create the molecule.
    mol_name = 'axes'
    structure.add_molecule(name=mol_name)

    # The pivot points.
    pivot1 = generate_pivot(order=1)
    pivot2 = generate_pivot(order=2)

    # Alias the molecules.
    mol = structure.get_molecule(mol_name, model=1)
    mol_neg = None
    if structure.num_models() == 2:
        mol_neg = structure.get_molecule(mol_name, model=2)

    # The inversion matrix.
    inv_mat = -eye(3)

    # A single z-axis, when no rotor object is present.
    if cdp.model in ['iso cone, torsionless']:
        # Print out.
        print("\nGenerating the z-axis system.")

        # The axis.
        axis = create_rotor_axis_spherical(theta=cdp.axis_theta, phi=cdp.axis_phi)
        print(("Central axis: %s." % axis))

        # Rotations and inversions.
        axis_pos = axis
        axis_neg = dot(inv_mat, axis)

        # Simulation central axis.
        axis_sim_pos = None
        axis_sim_neg = None
        if hasattr(cdp, 'sim_number'):
            # Init.
            axis_sim = zeros((cdp.sim_number, 3), float64)

            # Fill the structure.
            for i in range(cdp.sim_number):
                if cdp.model in ['rotor', 'free rotor']:
                    axis_sim[i] = create_rotor_axis_alpha(alpha=cdp.axis_alpha_sim[i], pivot=pivot1, point=com)
                else:
                    axis_sim[i] = create_rotor_axis_spherical(theta=cdp.axis_theta_sim[i], phi=cdp.axis_phi_sim[i])

            # Inversion.
            axis_sim_pos = axis_sim
            axis_sim_neg = transpose(dot(inv_mat, transpose(axis_sim_pos)))

        # Generate the axis vectors.
        print("\nGenerating the axis vectors.")
        res_num = generate_vector_residues(mol=mol, vector=axis_pos, atom_name='z-ax', res_name_vect='AXE', sim_vectors=axis_sim_pos, res_num=2, origin=pivot1, scale=size)

        # The negative.
        if mol_neg != None:
            res_num = generate_vector_residues(mol=mol_neg, vector=axis_neg, atom_name='z-ax', res_name_vect='AXE', sim_vectors=axis_sim_neg, res_num=2, origin=pivot1, scale=size)

    # The z-axis connecting two motional modes.
    elif cdp.model in ['double rotor']:
        # Printout.
        print("\nGenerating the z-axis linking the two pivot points.")

        # The axis.
        axis = pivot1 - pivot2
        print(("Interconnecting axis: %s." % axis))

        # Generate the axis vectors.
        print("\nGenerating the axis vectors.")
        res_num = generate_vector_residues(mol=mol, vector=axis, atom_name='z-ax', res_name_vect='AXE', res_num=1, origin=pivot2)

    # The full axis system.
    elif cdp.model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
        # Print out.
        print("\nGenerating the full axis system.")

        # Add the pivot point.
        structure.add_atom(mol_name=mol_name, pdb_record='HETATM', atom_num=1, atom_name='R', res_name='AXE', res_num=1, pos=pivot1, element='C')

        # The axis system.
        axes = zeros((3, 3), float64)
        euler_to_R_zyz(cdp.eigen_alpha, cdp.eigen_beta, cdp.eigen_gamma, axes)
        print(("Axis system:\n%s" % axes))

        # Rotations and inversions.
        axes_pos = axes
        axes_neg = dot(inv_mat, axes)

        # Simulations
        axes_sim_pos = None
        axes_sim_neg = None
        if hasattr(cdp, 'sim_number'):
            # Init.
            axes_sim_pos = zeros((cdp.sim_number, 3, 3), float64)
            axes_sim_neg = zeros((cdp.sim_number, 3, 3), float64)

            # Fill the structure.
            for i in range(cdp.sim_number):
                # The positive system.
                euler_to_R_zyz(cdp.eigen_alpha_sim[i], cdp.eigen_beta_sim[i], cdp.eigen_gamma_sim[i], axes_sim_pos[i])

                # The negative system.
                euler_to_R_zyz(cdp.eigen_alpha_sim[i], cdp.eigen_beta_sim[i], cdp.eigen_gamma_sim[i], axes_sim_neg[i])
                axes_sim_neg[i] = dot(inv_mat, axes_sim_neg[i])

        # The axes to create.
        label = ['x', 'y']
        if cdp.model in ['pseudo-ellipse, torsionless']:
            label = ['x', 'y', 'z']

        # Generate the axis vectors.
        print("\nGenerating the axis vectors.")
        for j in range(len(label)):
            # The simulation data.
            axis_sim_pos = None
            axis_sim_neg = None
            if hasattr(cdp, 'sim_number'):
                axis_sim_pos = axes_sim_pos[:,:, j]
                axis_sim_neg = axes_sim_neg[:,:, j]

            # The vectors.
            res_num = generate_vector_residues(mol=mol, vector=axes_pos[:, j], atom_name='%s-ax'%label[j], res_name_vect='AXE', sim_vectors=axis_sim_pos, res_num=2, origin=pivot1, scale=size)
            if mol_neg != None:
                res_num = generate_vector_residues(mol=mol_neg, vector=axes_neg[:, j], atom_name='%s-ax'%label[j], res_name_vect='AXE', sim_vectors=axis_sim_neg, res_num=2, origin=pivot1, scale=size)


def add_cones(structure=None, size=None, inc=None):
    """Add the cone geometric object for the current frame order model to the structural object.

    @keyword structure: The internal structural object to add the rotor objects to.
    @type structure:    lib.structure.internal.object.Internal instance
    @keyword size:      The size of the geometric object in Angstroms.
    @type size:         float
    @keyword inc:       The number of increments for the filling of the cone objects.
    @type inc:          int
    """

    # Create the molecule.
    structure.add_molecule(name='cones')

    # Alias the molecules.
    mol = structure.get_molecule('cones', model=1)
    mol_neg = None
    if structure.num_models() == 2:
        mol_neg = structure.get_molecule('cones', model=2)

    # The 1st pivot point.
    pivot = generate_pivot(order=1)

    # The inversion matrix.
    inv_mat = -eye(3)

    # The axis.
    if cdp.model in ['rotor', 'free rotor']:
        axis = create_rotor_axis_alpha(alpha=cdp.axis_alpha, pivot=pivot, point=com)
    else:
        axis = create_rotor_axis_spherical(theta=cdp.axis_theta, phi=cdp.axis_phi)
    print(("Central axis: %s." % axis))

    # The rotation matrix (rotation from the z-axis to the cone axis).
    if cdp.model not in ['iso cone', 'iso cone, torsionless', 'iso cone, free rotor']:
        R = axes
    else:
        R = zeros((3, 3), float64)
        two_vect_to_R(array([0, 0, 1], float64), axis, R)

    # Average position rotation.
    R_pos = R
    R_neg = dot(inv_mat, R)

    # The pseudo-ellipse cone object.
    if cdp.model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
        cone_obj = Pseudo_elliptic(cdp.cone_theta_x, cdp.cone_theta_y)

    # The isotropic cone object.
    else:
        # The angle.
        if hasattr(cdp, 'cone_theta'):
            cone_theta = cdp.cone_theta
        elif hasattr(cdp, 'cone_s1'):
            cone_theta = order_parameters.iso_cone_S_to_theta(cdp.cone_s1)

        # The object.
        cone_obj = Iso_cone(cone_theta)

    # Create the positive and negative cones.
    cone(mol=mol, cone_obj=cone_obj, start_res=1, apex=pivot, R=R_pos, inc=inc, distribution='regular', axis_flag=False)

    # The negative.
    if mol_neg != None:
        cone(mol=mol_neg, cone_obj=cone_obj, start_res=1, apex=pivot, R=R_neg, inc=inc, distribution='regular', axis_flag=False)


def add_pivots(structure=None):
    """Add the pivots for the current frame order model to the structural object.

    @keyword structure: The internal structural object to add the rotor objects to.
    @type structure:    lib.structure.internal.object.Internal instance
    """

    # The pivot point.
    pivot1 = generate_pivot(order=1)
    pivot2 = generate_pivot(order=2)

    # Create the molecule.
    mol_name = 'pivots'
    structure.add_molecule(name=mol_name)

    # Add the pivots for the double motion models.
    if cdp.model in ['double rotor']:
        structure.add_atom(mol_name=mol_name, pdb_record='HETATM', atom_num=1, atom_name='Piv1', res_name='PIV', res_num=1, pos=pivot1, element='C')
        structure.add_atom(mol_name=mol_name, pdb_record='HETATM', atom_num=2, atom_name='Piv2', res_name='PIV', res_num=1, pos=pivot2, element='C')

    # Add the pivot for the single motion models.
    else:
        structure.add_atom(mol_name=mol_name, pdb_record='HETATM', atom_num=1, atom_name='Piv', res_name='PIV', res_num=1, pos=pivot1, element='C')


def add_rotors(structure=None):
    """Add all rotor objects for the current frame order model to the structural object.

    @keyword structure: The internal structural object to add the rotor objects to.
    @type structure:    lib.structure.internal.object.Internal instance
    """

    # Initialise the list structures for the rotor data.
    axis = []
    span = []
    staggered = []
    pivot = []
    rotor_angle = []
    com = []
    label = []

    # The pivot points.
    pivot1 = generate_pivot(order=1)
    pivot2 = generate_pivot(order=2)

    # The single rotor models.
    if cdp.model in ['rotor', 'free rotor', 'iso cone', 'iso cone, free rotor', 'pseudo-ellipse', 'pseudo-ellipse, free rotor']:
        # The rotor angle.
        if cdp.model in ['free rotor', 'iso cone, free rotor', 'pseudo-ellipse, free rotor']:
            rotor_angle.append(pi)
        else:
            rotor_angle.append(cdp.cone_sigma_max)

        # Get the CoM of the entire molecule to use as the centre of the rotor.
        if cdp.model in ['rotor', 'free rotor']:
            com.append(pipe_centre_of_mass(verbosity=0))
        else:
            com.append(pivot1)

        # Generate the rotor axis.
        if cdp.model in ['rotor', 'free rotor']:
            axis.append(create_rotor_axis_alpha(alpha=cdp.axis_alpha, pivot=pivot, point=com))
        elif cdp.model in ['iso cone', 'iso cone, free rotor']:
            axis.append(create_rotor_axis_spherical(theta=cdp.axis_theta, phi=cdp.axis_phi))
        else:
            axis.append(create_rotor_axis_euler(alpha=cdp.eigen_alpha, beta=cdp.eigen_beta, gamma=cdp.eigen_gamma))

        # The size of the rotor, taking the 30 Angstrom cone representation into account.
        if cdp.model in ['rotor', 'free rotor']:
            span.append(20e-10)
        else:
            span.append(35e-10)

        # Stagger the propeller blades.
        if cdp.model in ['free rotor', 'iso cone, free rotor', 'pseudo-ellipse, free rotor']:
            staggered.append(False)
        else:
            staggered.append(True)

        # The pivot.
        pivot.append(pivot1)

        # The label.
        label.append('z-ax')

    # The double rotor models.
    elif cdp.model in ['double rotor']:
        # Add both rotor angles (the 2nd must come first).
        rotor_angle.append(cdp.cone_sigma_max_2)
        rotor_angle.append(cdp.cone_sigma_max)

        # Set the com to the pivot points.
        com.append(pivot2)
        com.append(pivot1)

        # Generate the eigenframe of the motion.
        frame = zeros((3, 3), float64)
        euler_to_R_zyz(cdp.eigen_alpha, cdp.eigen_beta, cdp.eigen_gamma, frame)

        # Add the x and y axes.
        axis.append(frame[:,0])
        axis.append(frame[:,1])

        # The rotor size.
        span.append(20e-10)
        span.append(20e-10)

        # Stagger the propeller blades.
        staggered.append(True)
        staggered.append(True)

        # The pivot points.
        pivot.append(pivot2)
        pivot.append(pivot1)

        # The labels.
        label.append('x-ax')
        label.append('y-ax')

    # Add each rotor to the structure as a new molecule.
    for i in range(len(axis)):
        rotor(structure=structure, rotor_angle=rotor_angle[i], axis=axis[i], axis_pt=pivot[i], label=label[i], centre=com[i], span=span[i], blade_length=5e-10, staggered=staggered[i])


def create_ave_pos(format='PDB', file=None, dir=None, force=False):
    """Create a PDB file of the molecule with the moving domains shifted to the average position.

    @keyword format:    The format for outputting the geometric representation.  Currently only the 'PDB' format is supported.
    @type format:       str
    @keyword file:      The name of the file for the average molecule structure.
    @type file:         str
    @keyword dir:       The name of the directory to place the PDB file into.
    @type dir:          str
    @keyword force:     Flag which if set to True will cause any pre-existing file to be overwritten.
    @type force:        bool
    """

    # Printout.
    subsection(file=sys.stdout, text="Creating a PDB file with the moving domains shifted to the average position.")

    # Make a copy of the structural object (so as to preserve the original structure).
    structure = deepcopy(cdp.structure)

    # First rotate the moving domain to the average position.
    R = zeros((3, 3), float64)
    if hasattr(cdp, 'ave_pos_alpha'):
        euler_to_R_zyz(cdp.ave_pos_alpha, cdp.ave_pos_beta, cdp.ave_pos_gamma, R)
    else:
        euler_to_R_zyz(0.0, cdp.ave_pos_beta, cdp.ave_pos_gamma, R)
    origin = pipe_centre_of_mass(atom_id=domain_moving(), verbosity=0)
    structure.rotate(R=R, origin=origin, atom_id=domain_moving())

    # Then translate the moving domain.
    structure.translate(T=[cdp.ave_pos_x, cdp.ave_pos_y, cdp.ave_pos_z], atom_id=domain_moving())

    # Output to PDB format.
    if format == 'PDB':
        file = open_write_file(file_name=file, dir=dir, force=force)
        structure.write_pdb(file=file)
        file.close()


def create_distribution(format='PDB', file=None, dir=None, force=False):
    """Create a PDB file of a distribution of positions coving the full dynamics of the moving domain.

    @keyword format:    The format for outputting the geometric representation.  Currently only the 'PDB' format is supported.
    @type format:       str
    @keyword file:      The name of the file which will contain multiple models spanning the full dynamics distribution of the frame order model.
    @type file:         str
    @keyword dir:       The name of the directory to place the PDB file into.
    @type dir:          str
    @keyword force:     Flag which if set to True will cause any pre-existing file to be overwritten.
    @type force:        bool
    """

    # Printout.
    subsection(file=sys.stdout, text="Creating a PDB file of a distribution of positions coving the full dynamics of the moving domain.")


def create_geometric_rep(format='PDB', file=None, dir=None, size=30.0, inc=36, force=False):
    """Create a PDB file containing a geometric object representing the frame order dynamics.

    @keyword format:    The format for outputting the geometric representation.  Currently only the 'PDB' format is supported.
    @type format:       str
    @keyword file:      The name of the file of the PDB representation of the frame order dynamics to create.
    @type file:         str
    @keyword dir:       The name of the directory to place the PDB file into.
    @type dir:          str
    @keyword size:      The size of the geometric object in Angstroms.
    @type size:         float
    @keyword inc:       The number of increments for the filling of the cone objects.
    @type inc:          int
    @keyword force:     Flag which if set to True will cause any pre-existing file to be overwritten.
    @type force:        bool
    """

    # Printout.
    subsection(file=sys.stdout, text="Creating a PDB file containing a geometric object representing the frame order dynamics.")

    # Create the structural object.
    structure = Internal()

    # Create model for the positive and negative images, and alias the molecules.
    model = structure.add_model(model=1)
    if cdp.model not in ['rotor', 'free rotor', 'double rotor']:
        model_neg = structure.add_model(model=2)

    # Add the pivots.
    add_pivots(structure=structure)

    # Add all rotor objects.
    add_rotors(structure=structure)

    # Add the axis systems.
    add_axes(structure=structure, size=size)

    # Add the cone objects.
    if cdp.model not in ['rotor', 'free rotor', 'double rotor']:
        add_cones(structure=structure, size=size, inc=inc)

    # Create the PDB file.
    if format == 'PDB':
        pdb_file = open_write_file(file, dir, force=force)
        structure.write_pdb(pdb_file)
        pdb_file.close()
