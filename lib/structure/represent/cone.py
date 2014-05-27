###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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

# Python module imports.
from math import cos, pi, sin
from numpy import array, dot, eye, float64, zeros

# relax module imports.
from lib.geometry.rotations import two_vect_to_R
from lib.structure.angles import angles_regular, angles_uniform
from lib.structure.conversion import get_proton_name
from lib.structure.geometric import generate_vector_dist


def cone_edge(mol=None, cone_obj=None, res_name='CON', res_num=None, chain_id='', apex=None, axis=None, R=None, scale=None, inc=None, distribution='uniform', debug=False):
    """Add a residue to the atomic data representing a cone of the given angle.

    A series of vectors totalling the number of increments and starting at the origin are equally spaced around the cone axis.  The atoms representing neighbouring vectors will be directly bonded together.  This will generate an object representing the outer edge of a cone.


    @keyword mol:           The molecule container.
    @type mol:              MolContainer instance
    @keyword cone_obj:      The cone object.  This should provide the limit_check() method with determines the limits of the distribution accepting two arguments, the polar angle phi and the azimuthal angle theta, and return True if the point is in the limits or False if outside.  It should also provide the phi_max() method for returning the phi value for the given theta.
    @type cone_obj:         class instance
    @keyword res_name:      The residue name.
    @type res_name:         str
    @keyword res_num:       The residue number.
    @type res_num:          int
    @keyword chain_id:      The chain identifier.
    @type chain_id:         str
    @keyword apex:          The apex of the cone.
    @type apex:             numpy array, len 3
    @keyword axis:          The central axis of the cone.  If supplied, then this arg will be used to construct the rotation matrix.
    @type axis:             numpy array, len 3
    @keyword R:             A 3x3 rotation matrix.  If the axis arg supplied, then this matrix will be ignored.
    @type R:                3x3 numpy array
    @keyword scale:         The scaling factor to stretch all points by.
    @type scale:            float
    @keyword inc:           The number of increments or number of vectors used to generate the outer edge of the cone.
    @type inc:              int
    @keyword distribution:  The type of point distribution to use.  This can be 'uniform' or 'regular'.
    @type distribution:     str
    """

    # The atom numbers (and indices).
    atom_num = mol.atom_num[-1]+1

    # Add an atom for the cone apex.
    mol.atom_add(pdb_record='HETATM', atom_num=atom_num, atom_name='APX', res_name=res_name, res_num=res_num, pos=apex, segment_id=None, element='H')
    origin_atom = atom_num

    # Get the polar and azimuthal angles for the distribution.
    if distribution == 'uniform':
        phi, theta = angles_uniform(inc)
    else:
        phi, theta = angles_regular(inc)

    # Initialise the rotation matrix.
    if R == None:
        R = eye(3)

    # Get the rotation matrix.
    if axis != None:
        two_vect_to_R(array([0, 0, 1], float64), axis, R)

    # Determine the maximum phi values and the indices of the point just above the edge.
    phi_max = zeros(len(theta), float64)
    edge_index = zeros(len(theta), int)
    for i in range(len(theta)):
        # Get the polar angle for the longitude edge atom.
        phi_max[i] = cone_obj.phi_max(theta[i])

        # The index.
        for j in range(len(phi)):
            if phi[j] <= phi_max[i]:
                edge_index[i] = j
                break

    # Reverse edge index.
    edge_index_rev = len(phi) - 1 - edge_index

    # Move around the azimuth.
    atom_num = atom_num + 1
    for i in range(len(theta)):
        # The vector in the unrotated frame.
        x = cos(theta[i]) * sin(phi_max[i])
        y = sin(theta[i])* sin(phi_max[i])
        z = cos(phi_max[i])
        vector = array([x, y, z], float64)

        # Rotate the vector.
        vector = dot(R, vector)

        # The atom id.
        atom_id = 'T' + repr(i)

        # The atom position.
        pos = apex+vector*scale

        # Debugging.
        if debug:
            print("i: %s; theta: %s" % (i, theta[i]))
            print("%sAdding atom %s." % (" "*4, get_proton_name(atom_num)))

        # Add the vector as a H atom of the cone residue.
        mol.atom_add(pdb_record='HETATM', atom_num=atom_num, atom_name=get_proton_name(atom_num), res_name=res_name, res_num=res_num, pos=pos, segment_id=None, element='H')

        # Join the longitude atom to the cone apex.
        mol.atom_connect(index1=origin_atom-1, index2=atom_num-1)

        # Increment the atom number.
        atom_num = atom_num + 1

        # Add latitude atoms for a smoother cone edge and better stitching to the cap.
        for j in range(len(phi)):
            # The index for the direction top to bottom!
            k = len(phi) - 1 - j

            # Debugging.
            if debug:
                print("%sj: %s; phi: %-20s; k: %s; phi: %-20s; phi_max: %-20s" % (" "*4, j, phi[j], k, phi[k], phi_max[i]))

            # No edge.
            skip = True

            # Forward edge (skip when the latitude is phi max).
            fwd_index = i+1
            if i == len(theta)-1:
                fwd_index = 0
            if j >= edge_index[i] and j < edge_index[fwd_index] and not abs(phi_max[fwd_index] - phi[j]) < 1e-6:
                # Debugging.
                if debug:
                    print("%sForward edge." % (" "*8))

                # Edge found.
                skip = False

                # Find the theta value for this polar angle phi.
                phi_val = phi[j]
                if fwd_index == 0:
                    theta_max = theta[fwd_index] + 2*pi
                else:
                    theta_max = theta[fwd_index]
                theta_max = cone_obj.theta_max(phi_val, theta_min=theta[i], theta_max=theta_max-1e-7)

            # Back edge (skip when the latitude is phi max).
            rev_index = i-1
            if i == 0:
                rev_index = len(theta)-1
            if i < len(theta)-1 and j > edge_index_rev[i] and j <= edge_index_rev[i+1] and not abs(phi_max[fwd_index] - phi[k]) < 1e-6:
                # Debugging.
                if debug:
                    print("%sBack edge." % (" "*8))

                # Edge found.
                skip = False

                # Find the theta value for this polar angle phi.
                phi_val = phi[k]
                theta_max = cone_obj.theta_max(phi_val, theta_min=theta[i-1], theta_max=theta[i])

            # Skipping.
            if skip:
                continue

            # Debugging.
            if debug:
                print("%sAdding atom %s." % (" "*8, get_proton_name(atom_num)))

            # The coordinates.
            x = cos(theta_max) * sin(phi_val)
            y = sin(theta_max) * sin(phi_val)
            z = cos(phi_val)
            pos = array([x, y, z], float64) * scale

            # Rotate and shift.
            pos = apex + dot(R, pos)

            # Add the atom.
            mol.atom_add(pdb_record='HETATM', atom_num=atom_num, atom_name=get_proton_name(atom_num), res_name=res_name, chain_id=chain_id, res_num=res_num, pos=pos, segment_id=None, element='H')

            # Increment the atom number.
            atom_num = atom_num + 1

    # Debugging.
    if debug:
        print("\nBuilding the edge.")

    # Build the cone edge.
    for i in range(origin_atom, atom_num-2):
        # Debugging.
        if debug:
            print("%sCone edge, connecting %s to %s" % (" "*4, get_proton_name(i), get_proton_name(i+1)))

        # Connect.
        mol.atom_connect(index1=i, index2=i+1)

    # Connect the last radial array to the first (to zip up the circle).
    mol.atom_connect(index1=atom_num-2, index2=origin_atom)


def cone(mol=None, cone_obj=None, start_res=1, apex=None, axis=None, R=None, inc=None, scale=30.0, distribution='regular', axis_flag=True):
    """Create a structural representation of the given cone object.

    @keyword mol:           The molecule container.
    @type mol:              MolContainer instance
    @keyword cone_obj:      The cone object.  This should provide the limit_check() method with determines the limits of the distribution accepting two arguments, the polar angle phi and the azimuthal angle theta, and return True if the point is in the limits or False if outside.  It should also provide the theta_max() method for returning the theta value for the given phi, the phi_max() method for returning the phi value for the given theta.
    @type cone_obj:         class instance
    @keyword start_res:     The starting residue number.
    @type start_res:        str
    @keyword apex:          The apex of the cone.
    @type apex:             rank-1, 3D numpy array
    @keyword axis:          The central axis of the cone.  If not supplied, the z-axis will be used.
    @type axis:             rank-1, 3D numpy array
    @keyword R:             The rotation matrix.
    @type R:                rank-2, 3D numpy array
    @keyword inc:           The increment number used to determine the number of latitude and longitude lines.
    @type inc:              int
    @keyword scale:         The scaling factor to stretch the unit cone by.
    @type scale:            float
    @keyword distribution:  The type of point distribution to use.  This can be 'uniform' or 'regular'.
    @type distribution:     str
    @keyword axis_flag:     A flag which if True will create the cone's axis.
    @type axis_flag:        bool
    """

    # The cone axis default of the z-axis.
    if not axis:
        axis = array([0, 0, 1], float64)

    # No rotation.
    if R == None:
        R = eye(3)

    # The first atom number.
    start_atom = 1
    if hasattr(mol, 'atom_num'):
        start_atom = mol.atom_num[-1]+1

    # The axis.
    if axis_flag:
        # Add the apex.
        mol.atom_add(pdb_record='HETATM', atom_num=start_atom, atom_name='R', res_name='APX', res_num=start_res, pos=apex, element='C')

        # Generate the axis vectors.
        print("\nGenerating the axis vectors.")
        res_num = generate_vector_residues(mol=mol, vector=dot(R, axis), atom_name='Axis', res_name_vect='AXE', res_num=start_res+1, origin=apex, scale=scale)

    # Generate the cone outer edge.
    print("\nGenerating the cone outer edge.")
    edge_start_atom = mol.atom_num[-1]+1
    cone_edge(mol=mol, cone_obj=cone_obj, res_name='EDG', res_num=start_res+2, apex=apex, R=R, scale=scale, inc=inc, distribution=distribution)

    # Generate the cone cap, and stitch it to the cone edge.
    print("\nGenerating the cone cap.")
    cone_start_atom = mol.atom_num[-1]+1
    generate_vector_dist(mol=mol, res_name='CON', res_num=start_res+3, centre=apex, R=R, limit_check=cone_obj.limit_check, scale=scale, inc=inc, distribution=distribution)
    stitch_cone_to_edge(mol=mol, cone_obj=cone_obj, dome_start=cone_start_atom, edge_start=edge_start_atom+1, scale=scale, inc=inc, distribution=distribution)


def stitch_cone_to_edge(mol=None, cone_obj=None, chain_id='', dome_start=None, edge_start=None, scale=1.0, inc=None, distribution='uniform', debug=False):
    """Function for stitching the cone dome to its edge, in the PDB representations.

    @keyword mol:           The molecule container.
    @type mol:              MolContainer instance
    @keyword cone_obj:      The cone object.  This should provide the limit_check() method with determines the limits of the distribution accepting two arguments, the polar angle phi and the azimuthal angle theta, and return True if the point is in the limits or False if outside.  It should also provide the theta_max() method for returning the theta value for the given phi.
    @type cone_obj:         class instance
    @keyword chain_id:      The chain identifier.
    @type chain_id:         str
    @keyword dome_start:    The starting atom number of the cone dome residue.
    @type dome_start:       int
    @keyword edge_start:    The starting atom number of the cone edge residue.
    @type edge_start:       int
    @keyword scale:         The scaling factor to stretch all points by.
    @type scale:            float
    @keyword inc:           The number of increments or number of vectors used to generate the outer edge of the cone.
    @type inc:              int
    @keyword distribution:  The type of point distribution to use.  This can be 'uniform' or 'regular'.
    @type distribution:     str
    """

    # Get the polar and azimuthal angles for the distribution.
    if distribution == 'uniform':
        phi, theta = angles_uniform(inc)
    else:
        phi, theta = angles_regular(inc)

    # Determine the maximum phi values and the indices of the point just above the edge.
    phi_max = zeros(len(theta), float64)
    edge_index = zeros(len(theta), int)
    for i in range(len(theta)):
        # Get the polar angle for the longitude edge atom.
        phi_max[i] = cone_obj.phi_max(theta[i])

        # The index.
        for j in range(len(phi)):
            if phi[j] <= phi_max[i]:
                edge_index[i] = j
                break

    # Reverse edge index.
    edge_index_rev = len(phi) - 1 - edge_index

    # Debugging.
    if debug:
        print("\nDome start: %s" % dome_start)
        print("Edge start: %s" % edge_start)
        print("Edge indices:     %s" % edge_index)
        print("Edge indices rev: %s" % edge_index_rev)

    # Move around the azimuth.
    dome_atom = dome_start
    edge_atom = edge_start
    for i in range(len(theta)):
        # Debugging.
        if debug:
            print("i: %s; theta: %s" % (i, theta[i]))
            print("%sDome atom: %s" % (" "*4, get_proton_name(dome_atom)))
            print("%sStitching longitudinal line to edge - %s to %s." % (" "*4, get_proton_name(edge_atom), get_proton_name(dome_atom)))

        # Connect the two atoms (to stitch up the 2 objects).
        mol.atom_connect(index1=dome_atom-1, index2=edge_atom-1)

        # Update the edge atom.
        edge_atom = edge_atom + 1

        # Stitch up the latitude atoms.
        for j in range(len(phi)):
            # The index for the direction top to bottom!
            k = len(phi) - 1 - j

            # Debugging.
            if debug:
                print("%sj: %s; phi: %-20s; k: %s; phi: %-20s; phi_max: %-20s" % (" "*4, j, phi[j], k, phi[k], phi_max[i]))

            # No edge.
            skip = True

            # Forward edge (skip when the latitude is phi max).
            fwd_index = i+1
            if i == len(theta)-1:
                fwd_index = 0
            if j >= edge_index[i] and j < edge_index[fwd_index] and not abs(phi_max[fwd_index] - phi[j]) < 1e-6:
                # Debugging.
                if debug:
                    print("%sForward edge." % (" "*8))

                # Edge found.
                skip = False
                forward = True

            # Back edge (skip when the latitude is phi max).
            rev_index = i-1
            if i == 0:
                rev_index = len(theta)-1
            if i < len(theta)-1 and j > edge_index_rev[i] and j <= edge_index_rev[i+1] and not abs(phi_max[fwd_index] - phi[k]) < 1e-6:
                # Debugging.
                if debug:
                    print("%sBack edge." % (" "*8))

                # Edge found.
                skip = False
                forward = False

            # Skipping.
            if skip:
                continue

            # The dome atom to stitch to (current dome atom + one latitude line to shift across).
            if forward:
                atom = dome_atom + j - edge_index[i]
            else:
                atom = dome_atom + (edge_index_rev[i]+1) + k - edge_index[fwd_index]

            # Debugging.
            if debug:
                print("%sStitching latitude line to edge - %s to %s." % (" "*8, get_proton_name(edge_atom), get_proton_name(atom)))

            # Connect the two atoms (to stitch up the 2 objects).
            mol.atom_connect(index1=atom-1, index2=edge_atom-1)

            # Increment the cone edge atom number.
            edge_atom = edge_atom + 1

        # Update the cone dome atom.
        dome_atom = dome_atom + (len(phi) - edge_index[i])
