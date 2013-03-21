###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
"""Representations of a mechanical rotor."""

# Python module imports.
from math import pi
from numpy import array, cross, dot, float64, transpose, zeros
from numpy.linalg import norm

# relax module imports.
from lib.geometry.lines import closest_point_ax
from maths_fns.rotation_matrix import axis_angle_to_R


def rotor_pdb(structure=None, rotor_angle=None, axis=None, axis_pt=True, centre=None, span=2e-9, blade_length=5e-10, model=None, staggered=False):
    """Create a PDB representation of a rotor motional model.

    @keyword structure:     The internal structural object instance to add the rotor to as a molecule.
    @type structure:        generic_fns.structure.internal.Internal instance
    @keyword rotor_angle:   The angle of the rotor motion in radian.
    @type rotor_angle:      float
    @keyword axis:          The vector defining the rotor axis.
    @type axis:             numpy rank-1, 3D array
    @keyword axis_pt:       A point lying anywhere on the rotor axis.  This is used to define the position of the axis in 3D space.
    @type axis_pt:          numpy rank-1, 3D array
    @keyword centre:        The central point of the representation.  If this point is not on the rotor axis, then the closest point on the axis will be used for the centre.
    @type centre:           numpy rank-1, 3D array
    @keyword span:          The distance from the central point to the rotor blades (meters).
    @type span:             float
    @keyword blade_length:  The length of the representative rotor blades.
    @type blade_length:     float
    @keyword model:         The structural model number to add the rotor to.  If not supplied, the same rotor structure will be added to all models.
    @type model:            int or None
    @keyword staggered:     A flag which if True will cause the rotor blades to be staggered.  This is used to avoid blade overlap.
    @type staggered:        bool
    """

    # Convert the arguments to numpy arrays, radians and Angstrom.
    axis = array(axis, float64)
    axis_pt = array(axis_pt, float64)
    centre = array(centre, float64)
    span = span * 1e10
    blade_length = blade_length * 1e10

    # Normalise.
    axis_norm = axis / norm(axis)

    # Add a structure.
    structure.add_molecule(name='rotor')

    # Loop over the models.
    for model in structure.model_loop(model):
        print model

        # Alias the single molecule from the single model.
        mol = structure.get_molecule('rotor', model=model.num)

        # The central point.
        mid_point = closest_point_ax(line_pt=axis_pt, axis=axis, point=centre)
        mol.atom_add(pdb_record='HETATM', atom_num=1, atom_name='CTR', res_name='AX', res_num=1, pos=mid_point, element='PT')

        # Centre of the propellers.
        prop1 = mid_point + axis_norm * span
        prop1_index = 1
        mol.atom_add(pdb_record='HETATM', atom_num=2, atom_name='PRP', res_name='PRC', res_num=2, pos=prop1, element='O')
        mol.atom_connect(index1=0, index2=prop1_index)

        # Centre of the propellers.
        prop2 = mid_point - axis_norm * span
        prop2_index = 2
        mol.atom_add(pdb_record='HETATM', atom_num=3, atom_name='PRP', res_name='PRC', res_num=3, pos=prop2, element='O')
        mol.atom_connect(index1=0, index2=prop2_index)

        # Create the rotor propellers.
        rotor_propellers(mol=mol, rotor_angle=rotor_angle, centre=prop1, axis=axis, blade_length=blade_length, staggered=staggered)
        rotor_propellers(mol=mol, rotor_angle=rotor_angle, centre=prop2, axis=-axis, blade_length=blade_length, staggered=staggered)


def rotor_propellers(mol=None, rotor_angle=None, centre=None, axis=None, blade_length=5.0, staggered=False):
    """Create a PDB representation of a rotor motional model.

    @keyword mol:           The internal structural object molecule container to add the atoms to.
    @type mol:              MolContainer instance
    @keyword rotor_angle:   The angle of the rotor motion in radians.
    @type rotor_angle:      float
    @keyword centre:        The central point of the propeller.
    @type centre:           numpy rank-1, 3D array
    @keyword axis:          The vector defining the rotor axis.
    @type axis:             numpy rank-1, 3D array
    @keyword blade_length:  The length of the representative rotor blades in Angstrom.
    @type blade_length:     float
    @keyword staggered:     A flag which if True will cause the rotor blades to be staggered.  This is used to avoid blade overlap.
    @type staggered:        bool
    """

    # Init.
    step_angle = 2.0 / 360.0 * 2.0 * pi
    R = zeros((3, 3), float64)
    res_num = mol.last_residue() + 1

    # Blade vectors.
    blades = zeros((4, 3), float64)
    if abs(dot(axis, array([0, 0, 1], float64))) == 1.0:    # Avoid failures in artificial situations.
        blades[0] = cross(axis, array([1, 0, 0], float64))
    else:
        blades[0] = cross(axis, array([0, 0, 1], float64))
    blades[0] = blades[0] / norm(blades[0])
    blades[1] = cross(axis, blades[0])
    blades[1] = blades[1] / norm(blades[1])
    blades[2] = -blades[0]
    blades[3] = -blades[1]

    # Create the 4 blades.
    for i in range(len(blades)):
        # Staggering.
        if staggered and i % 2:
            blade_origin = centre - axis * 2

        # Non-staggered.
        else:
            blade_origin = centre

        # Add an atom for the blage origin.
        blade_origin_index = mol.atom_add(pdb_record='HETATM', atom_name='BLO', res_name='PRB', res_num=res_num, pos=blade_origin, element='O')

        # The centre edge point of the blade.
        mid_point = blade_origin + blades[i] * blade_length
        mid_pt_index = mol.atom_add(pdb_record='HETATM', atom_name='BLD', res_name='PRB', res_num=res_num, pos=mid_point, element='N')
        mol.atom_connect(index1=mid_pt_index, index2=blade_origin_index)

        # Build the blade.
        angle = 0.0
        pos_last_index = mid_pt_index
        neg_last_index = mid_pt_index
        while True:
            # Increase the angle.
            angle += step_angle

            # The edge rotation.
            if angle > rotor_angle:
                axis_angle_to_R(axis, rotor_angle, R)

            # The normal rotation matrix.
            else:
                axis_angle_to_R(axis, angle, R)

            # The positive edge.
            pos_point = dot(R, mid_point - blade_origin) + blade_origin
            pos_index = mol.atom_add(pdb_record='HETATM', atom_name='BLD', res_name='PRB', res_num=res_num, pos=pos_point, element='N')
            mol.atom_connect(index1=pos_index, index2=pos_last_index)
            mol.atom_connect(index1=pos_index, index2=blade_origin_index)

            # The negative edge.
            neg_point = dot(transpose(R), mid_point - blade_origin) + blade_origin
            neg_index = mol.atom_add(pdb_record='HETATM', atom_name='BLD', res_name='PRB', res_num=res_num, pos=neg_point, element='N')
            mol.atom_connect(index1=neg_index, index2=neg_last_index)
            mol.atom_connect(index1=neg_index, index2=blade_origin_index)

            # Update the indices.
            pos_last_index = pos_index
            neg_last_index = neg_index

            # Finish.
            if angle > rotor_angle:
                break

        # Increment the residue number.
        res_num += 1
