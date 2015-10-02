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
from warnings import warn

# relax module imports.
from lib.arg_check import is_float_array
from lib.errors import RelaxError
from lib.frame_order.rotor_axis import create_rotor_axis_alpha, create_rotor_axis_euler, create_rotor_axis_spherical
from lib.geometry.rotations import euler_to_R_zyz, two_vect_to_R
from lib.io import open_write_file
from lib.order import order_parameters
from lib.structure.cones import Iso_cone, Pseudo_elliptic
from lib.structure.geometric import generate_vector_residues
from lib.structure.internal.object import Internal
from lib.structure.represent.cone import cone
from lib.structure.represent.rotor import rotor_pdb
from lib.text.sectioning import subsection
from lib.warnings import RelaxWarning
from pipe_control import pipes
from pipe_control.structure.mass import pipe_centre_of_mass
from specific_analyses.frame_order.data import domain_moving
from specific_analyses.frame_order.parameters import update_model


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


def create_geometric_rep(format='PDB', file=None, dir=None, size=30.0, inc=36, force=False, neg_cone=True):
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
    @keyword neg_cone:  A flag which if True will cause the negative cone to be added to the representation.  This is ignored for the rotor models.
    @type neg_cone:     bool
    """

    # Printout.
    subsection(file=sys.stdout, text="Creating a PDB file containing a geometric object representing the frame order dynamics.")

    # Monte Carlo simulation flag.
    sim = False
    num_sim = 0
    if hasattr(cdp, 'sim_number'):
        sim = True
        num_sim = cdp.sim_number

    # The inversion matrix.
    inv_mat = -eye(3)

    # Create the structural object.
    structure = Internal()

    # Create model for the positive and negative images.
    if cdp.model in ['rotor', 'free rotor']:
        neg_cone = False
    model = structure.add_model(model=1)
    model_num = 1
    if neg_cone:
        model_neg = structure.add_model(model=2)
        model_num = 2

    # The pivot point.
    pivot = array([cdp.pivot_x, cdp.pivot_y, cdp.pivot_z])

    # The rotor object.
    if cdp.model in ['rotor', 'free rotor', 'iso cone', 'iso cone, free rotor', 'pseudo-ellipse', 'pseudo-ellipse, free rotor']:
        # The rotor angle.
        if cdp.model in ['free rotor', 'iso cone, free rotor', 'pseudo-ellipse, free rotor']:
            rotor_angle = pi
        else:
            rotor_angle = cdp.cone_sigma_max

        # Get the CoM of the entire molecule to use as the centre of the rotor.
        com = pivot
        if cdp.model in ['rotor', 'free rotor']:
            com = pipe_centre_of_mass(verbosity=0)

        # Generate the rotor axis.
        if cdp.model in ['rotor', 'free rotor']:
            axis = create_rotor_axis_alpha(alpha=cdp.axis_alpha, pivot=pivot, point=com)
        elif cdp.model in ['iso cone', 'iso cone, free rotor']:
            axis = create_rotor_axis_spherical(theta=cdp.axis_theta, phi=cdp.axis_phi)
        else:
            axis = create_rotor_axis_euler(alpha=cdp.eigen_alpha, beta=cdp.eigen_beta, gamma=cdp.eigen_gamma)

        # The size of the rotor, taking the 30 Angstrom cone representation into account.
        if cdp.model in ['rotor', 'free rotor']:
            span = 20e-10
        else:
            span = 35e-10

        # Stagger the propeller blades.
        staggered = True
        if cdp.model in ['free rotor', 'iso cone, free rotor', 'pseudo-ellipse, free rotor']:
            staggered = False

        # Add the rotor object to the structure as a new molecule.
        rotor_pdb(structure=structure, rotor_angle=rotor_angle, axis=axis, axis_pt=pivot, centre=com, span=span, blade_length=5e-10, staggered=staggered)

    # Create the molecule.
    structure.add_molecule(name='rest')

    # Alias the molecules.
    mol = model.mol[0]
    if neg_cone:
        mol_neg = model_neg.mol[0]


    # The pivot point.
    ##################

    # Add the pivot point.
    structure.add_atom(mol_name=cdp.model, pdb_record='HETATM', atom_num=1, atom_name='R', res_name='PIV', res_num=1, pos=pivot, element='C')


    # The axes.
    ###########

    # The spherical angles.
    if cdp.model in ['iso cone', 'free rotor', 'iso cone, torsionless', 'iso cone, free rotor', 'rotor']:
        # Print out.
        print("\nGenerating the z-axis system.")

        # The axis.
        if cdp.model in ['rotor', 'free rotor']:
            axis = create_rotor_axis_alpha(alpha=cdp.axis_alpha, pivot=pivot, point=com)
        else:
            axis = create_rotor_axis_spherical(theta=cdp.axis_theta, phi=cdp.axis_phi)
        print(("Central axis: %s." % axis))

        # Rotations and inversions.
        axis_pos = axis
        axis_neg = dot(inv_mat, axis)

        # Simulation central axis.
        axis_sim_pos = None
        axis_sim_neg = None
        if sim:
            # Init.
            axis_sim = zeros((cdp.sim_number, 3), float64)

            # Fill the structure.
            for i in range(cdp.sim_number):
                if cdp.model in ['rotor', 'free rotor']:
                    axis_sim[i] = create_rotor_axis_alpha(alpha=cdp.axis_alpha_sim[i], pivot=pivot, point=com)
                else:
                    axis_sim[i] = create_rotor_axis_spherical(theta=cdp.axis_theta_sim[i], phi=cdp.axis_phi_sim[i])

            # Inversion.
            axis_sim_pos = axis_sim
            axis_sim_neg = transpose(dot(inv_mat, transpose(axis_sim_pos)))

        # Generate the axis vectors.
        print("\nGenerating the axis vectors.")
        res_num = generate_vector_residues(mol=mol, vector=axis_pos, atom_name='z-ax', res_name_vect='AXE', sim_vectors=axis_sim_pos, res_num=2, origin=pivot, scale=size)

        # The negative.
        if neg_cone:
            res_num = generate_vector_residues(mol=mol_neg, vector=axis_neg, atom_name='z-ax', res_name_vect='AXE', sim_vectors=axis_sim_neg, res_num=2, origin=pivot, scale=size)

    # The full axis system.
    else:
        # Print out.
        print("\nGenerating the full axis system.")

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
        if sim:
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

        # Generate the axis vectors.
        print("\nGenerating the axis vectors.")
        label = ['x', 'y', 'z']
        for j in range(len(label)):
            # The simulation data.
            axis_sim_pos = None
            axis_sim_neg = None
            if sim:
                axis_sim_pos = axes_sim_pos[:,:, j]
                axis_sim_neg = axes_sim_neg[:,:, j]

            # The vectors.
            res_num = generate_vector_residues(mol=mol, vector=axes_pos[:, j], atom_name='%s-ax'%label[j], res_name_vect='AXE', sim_vectors=axis_sim_pos, res_num=2, origin=pivot, scale=size)
            if neg_cone:
                res_num = generate_vector_residues(mol=mol_neg, vector=axes_neg[:, j], atom_name='%s-ax'%label[j], res_name_vect='AXE', sim_vectors=axis_sim_neg, res_num=2, origin=pivot, scale=size)


    # The cone object.
    ##################

    # Skip models missing a cone.
    if cdp.model not in ['rotor', 'free rotor', 'double rotor']:
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
        cone(mol=mol, cone_obj=cone_obj, start_res=mol.res_num[-1]+1, apex=pivot, R=R_pos, inc=inc, distribution='regular', axis_flag=False)

        # The negative.
        if neg_cone:
            cone(mol=mol_neg, cone_obj=cone_obj, start_res=mol_neg.res_num[-1]+1, apex=pivot, R=R_neg, inc=inc, distribution='regular', axis_flag=False)


    # Create the PDB file.
    ######################

    # Output to PDB format.
    if format == 'PDB':
        pdb_file = open_write_file(file, dir, force=force)
        structure.write_pdb(pdb_file)
        pdb_file.close()
