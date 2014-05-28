###############################################################################
#                                                                             #
# Copyright (C) 2007-2014 Edward d'Auvergne                                   #
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
"""The N-state model or structural ensemble analysis user functions."""

# Python module imports.
from math import acos, cos, pi
from numpy import array, dot, float64, zeros
from numpy.linalg import norm

# relax module imports.
from lib.errors import RelaxError
from lib.geometry.rotations import euler_to_R_zyz, two_vect_to_R
from lib.io import open_write_file
from lib.structure.cones import Iso_cone
from lib.structure.internal.object import Internal
from lib.structure.geometric import generate_vector_dist, generate_vector_residues
from lib.structure.represent.cone import cone_edge, stitch_cone_to_edge
from pipe_control import pipes
from pipe_control.structure.mass import centre_of_mass


def CoM(pivot_point=None, centre=None):
    """Centre of mass analysis.

    This function does an analysis of the centre of mass (CoM) of the N states.  This includes
    calculating the order parameter associated with the pivot-CoM vector, and the associated
    cone of motions.  The pivot_point argument must be supplied.  If centre is None, then the
    CoM will be calculated from the selected parts of the loaded structure.  Otherwise it will
    be set to the centre arg.

    @param pivot_point: The pivot point in the structural file(s).
    @type pivot_point:  list of float of length 3
    @param centre:      The optional centre of mass vector.
    @type centre:       list of float of length 3
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Set the pivot point.
    cdp.pivot_point = pivot_point

    # The centre has been supplied.
    if centre:
        cdp.CoM = centre

    # Calculate from the structure file.
    else:
        cdp.CoM = centre_of_mass()

    # Calculate the vector between the pivot and CoM points.
    cdp.pivot_CoM = array(cdp.CoM, float64) - array(cdp.pivot_point, float64)

    # Calculate the unit vector between the pivot and CoM points.
    unit_vect = cdp.pivot_CoM / norm(cdp.pivot_CoM)

    # Initilise some data structures.
    R = zeros((3, 3), float64)
    vectors = zeros((cdp.N, 3), float64)

    # Loop over the N states.
    for c in range(cdp.N):
        # Generate the rotation matrix.
        euler_to_R_zyz(cdp.alpha[c], cdp.beta[c], cdp.gamma[c], R)

        # Rotate the unit vector.
        vectors[c] = dot(R, unit_vect)

        # Multiply by the probability.
        vectors[c] = vectors[c] * cdp.probs[c]

    # Average of the unit vectors.
    cdp.ave_unit_pivot_CoM = sum(vectors)

    # The length reduction.
    cdp.ave_pivot_CoM_red = norm(cdp.ave_unit_pivot_CoM)

    # The aveage pivot-CoM vector.
    cdp.ave_pivot_CoM = norm(cdp.pivot_CoM) * cdp.ave_unit_pivot_CoM

    # The full length rotated pivot-CoM vector.
    cdp.full_ave_pivot_CoM = cdp.ave_pivot_CoM / cdp.ave_pivot_CoM_red

    # The cone angle for diffusion on an axially symmetric cone.
    cdp.theta_diff_on_cone = acos(cdp.ave_pivot_CoM_red)
    cdp.S_diff_on_cone = (3.0*cos(cdp.theta_diff_on_cone)**2 - 1.0) / 2.0

    # The cone angle and order parameter for diffusion in an axially symmetric cone.
    cdp.theta_diff_in_cone = acos(2.*cdp.ave_pivot_CoM_red - 1.)
    cdp.S_diff_in_cone = cos(cdp.theta_diff_in_cone) * (1 + cos(cdp.theta_diff_in_cone)) / 2.0

    # Print out.
    print("\n%-40s %-20s" % ("Pivot point:", repr(cdp.pivot_point)))
    print("%-40s %-20s" % ("Moving domain CoM (prior to rotation):", repr(cdp.CoM)))
    print("%-40s %-20s" % ("Pivot-CoM vector", repr(cdp.pivot_CoM)))
    print("%-40s %-20s" % ("Pivot-CoM unit vector:", repr(unit_vect)))
    print("%-40s %-20s" % ("Average of the unit pivot-CoM vectors:", repr(cdp.ave_unit_pivot_CoM)))
    print("%-40s %-20s" % ("Average of the pivot-CoM vector:", repr(cdp.ave_pivot_CoM)))
    print("%-40s %-20s" % ("Full length rotated pivot-CoM vector:", repr(cdp.full_ave_pivot_CoM)))
    print("%-40s %-20s" % ("Length reduction from unity:", repr(cdp.ave_pivot_CoM_red)))
    print("%-40s %.5f rad (%.5f deg)" % ("Cone angle (diffusion on a cone)", cdp.theta_diff_on_cone, cdp.theta_diff_on_cone / (2*pi) *360.))
    print("%-40s S_cone = %.5f (S^2 = %.5f)" % ("S_cone (diffusion on a cone)", cdp.S_diff_on_cone, cdp.S_diff_on_cone**2))
    print("%-40s %.5f rad (%.5f deg)" % ("Cone angle (diffusion in a cone)", cdp.theta_diff_in_cone, cdp.theta_diff_in_cone / (2*pi) *360.))
    print("%-40s S_cone = %.5f (S^2 = %.5f)" % ("S_cone (diffusion in a cone)", cdp.S_diff_in_cone, cdp.S_diff_in_cone**2))
    print("\n\n")


def cone_pdb(cone_type=None, scale=1.0, file=None, dir=None, force=False):
    """Create a PDB file containing a geometric object representing the various cone models.

    Currently the only cone types supported are 'diff in cone' and 'diff on cone'.


    @param cone_type:   The type of cone model to represent.
    @type cone_type:    str
    @param scale:       The size of the geometric object is eqaul to the average pivot-CoM
                        vector length multiplied by this scaling factor.
    @type scale:        float
    @param file:        The name of the PDB file to create.
    @type file:         str
    @param dir:         The name of the directory to place the PDB file into.
    @type dir:          str
    @param force:       Flag which if set to True will cause any pre-existing file to be
                        overwritten.
    @type force:        int
    """

    # Test if the cone models have been determined.
    if cone_type == 'diff in cone':
        if not hasattr(cdp, 'S_diff_in_cone'):
            raise RelaxError("The diffusion in a cone model has not yet been determined.")
    elif cone_type == 'diff on cone':
        if not hasattr(cdp, 'S_diff_on_cone'):
            raise RelaxError("The diffusion on a cone model has not yet been determined.")
    else:
        raise RelaxError("The cone type " + repr(cone_type) + " is unknown.")

    # The number of increments for the filling of the cone objects.
    inc = 20

    # The rotation matrix.
    R = zeros((3, 3), float64)
    two_vect_to_R(array([0, 0, 1], float64), cdp.ave_pivot_CoM/norm(cdp.ave_pivot_CoM), R)

    # The isotropic cone object.
    if cone_type == 'diff in cone':
        angle = cdp.theta_diff_in_cone
    elif cone_type == 'diff on cone':
        angle = cdp.theta_diff_on_cone
    cone_obj = Iso_cone(angle)

    # Create the structural object.
    structure = Internal()

    # Add a structure.
    structure.add_molecule(name='cone')

    # Alias the single molecule from the single model.
    mol = structure.structural_data[0].mol[0]

    # Add the pivot point.
    mol.atom_add(pdb_record='HETATM', atom_num=1, atom_name='R', res_name='PIV', res_num=1, pos=cdp.pivot_point, element='C')

    # Generate the average pivot-CoM vectors.
    print("\nGenerating the average pivot-CoM vectors.")
    sim_vectors = None
    if hasattr(cdp, 'ave_pivot_CoM_sim'):
        sim_vectors = cdp.ave_pivot_CoM_sim
    res_num = generate_vector_residues(mol=mol, vector=cdp.ave_pivot_CoM, atom_name='Ave', res_name_vect='AVE', sim_vectors=sim_vectors, res_num=2, origin=cdp.pivot_point, scale=scale)

    # Generate the cone outer edge.
    print("\nGenerating the cone outer edge.")
    cap_start_atom = mol.atom_num[-1]+1
    cone_edge(mol=mol, cone_obj=cone_obj, res_name='CON', res_num=3, apex=cdp.pivot_point, R=R, scale=norm(cdp.pivot_CoM), inc=inc)

    # Generate the cone cap, and stitch it to the cone edge.
    if cone_type == 'diff in cone':
        print("\nGenerating the cone cap.")
        cone_start_atom = mol.atom_num[-1]+1
        generate_vector_dist(mol=mol, res_name='CON', res_num=3, centre=cdp.pivot_point, R=R, limit_check=cone_obj.limit_check, scale=norm(cdp.pivot_CoM), inc=inc)
        stitch_cone_to_edge(mol=mol, cone_obj=cone_obj, dome_start=cone_start_atom, edge_start=cap_start_atom+1, inc=inc)

    # Create the PDB file.
    print("\nGenerating the PDB file.")
    pdb_file = open_write_file(file, dir, force=force)
    structure.write_pdb(pdb_file)
    pdb_file.close()
