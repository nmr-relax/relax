###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""Module for the manipulation of relaxation data."""

# Python module imports.
from numpy import float64, zeros
from numpy.linalg import norm
import sys
from warnings import warn

# relax module imports.
from arg_check import is_float
from generic_fns.interatomic import create_interatom, exists_data, interatomic_loop, return_interatom
from generic_fns.mol_res_spin import Selection, return_spin, spin_loop
from generic_fns import pipes
from relax_errors import RelaxError, RelaxNoInteratomError
from relax_io import extract_data, write_data
from relax_warnings import RelaxZeroVectorWarning


def define(spin_id1=None, spin_id2=None, direct_bond=False, verbose=True):
    """Set up the magnetic dipole-dipole interaction.

    @keyword spin_id1:      The spin identifier string of the first spin of the pair.
    @type spin_id1:         str
    @keyword spin_id2:      The spin identifier string of the second spin of the pair.
    @type spin_id2:         str
    @keyword direct_bond:   A flag specifying if the two spins are directly bonded.
    @type direct_bond:      bool
    @keyword verbose:       A flag which if True will result in printouts of the created interatomoic data containers.
    @type verbose:          bool
    """

    # Loop over both spin selections.
    ids = []
    for spin1, mol_name1, res_num1, res_name1, id1 in spin_loop(spin_id1, full_info=True, return_id=True):
        for spin2, mol_name2, res_num2, res_name2, id2 in spin_loop(spin_id2, full_info=True, return_id=True):
            # Directly bonded atoms.
            if direct_bond:
                # From structural info.
                if hasattr(cdp, 'structure') and not cdp.structure.are_bonded(atom_id1=id1, atom_id2=id2):
                    continue

                # From the residue info.
                elif not hasattr(cdp, 'structure'):
                    # No element info.
                    if not hasattr(spin1, 'element'):
                        raise RelaxError("The spin '%s' does not have the element type set." % id1)
                    if not hasattr(spin2, 'element'):
                        raise RelaxError("The spin '%s' does not have the element type set." % id2)

                    # Backbone NH and CH pairs.
                    pair = False
                    if (spin1.element == 'N' and spin2.element == 'H') or (spin2.element == 'N' and spin1.element == 'H'):
                        pair = True
                    elif (spin1.element == 'C' and spin2.element == 'H') or (spin2.element == 'C' and spin1.element == 'H'):
                        pair = True

                    # Same residue, so skip.
                    if pair and res_num1 != None and res_num1 != res_num2:
                        continue
                    elif pair and res_num1 == None and res_name1 != res_name2:
                        continue

            # Get the interatomic data object, if it exists.
            interatom = return_interatom(id1, id2)

            # Create the container if needed.
            if interatom == None:
                interatom = create_interatom(spin_id1=id1, spin_id2=id2)

            # Check that this has not already been set up.
            if interatom.dipole_pair:
                raise RelaxError("The magnetic dipole-dipole interaction already exists between the spins '%s' and '%s'." % (id1, id2))

            # Set a flag indicating that a dipole-dipole interaction is present.
            interatom.dipole_pair = True

            # Store the IDs for the printout.
            ids.append([repr(id1), repr(id2)])

    # No matches, so fail!
    if not len(ids):
        # Find the problem.
        count1 = 0
        count2 = 0
        for spin in spin_loop(spin_id1):
            count1 += 1
        for spin in spin_loop(spin_id2):
            count2 += 1

        # Report the problem.
        if count1 == 0 and count2 == 0:
            raise RelaxError("Both spin IDs '%s' and '%s' match no spins." % (spin_id1, spin_id2))
        elif count1 == 0:
            raise RelaxError("The spin ID '%s' matches no spins." % spin_id1)
        elif count2 == 0:
            raise RelaxError("The spin ID '%s' matches no spins." % spin_id2)
        else:
            raise RelaxError("Unknown error.")

    # Print out.
    if verbose:
        print("Magnetic dipole-dipole interactions are now defined for the following spins:\n")
        write_data(out=sys.stdout, headings=["Spin_ID_1", "Spin_ID_2"], data=ids)


def read_dist(file=None, dir=None, spin_id1_col=None, spin_id2_col=None, data_col=None, sep=None):
    """Set up the magnetic dipole-dipole interaction.

    @keyword file:          The name of the file to open.
    @type file:             str
    @keyword dir:           The directory containing the file (defaults to the current directory if None).
    @type dir:              str or None
    @keyword spin_id1_col:  The column containing the spin ID strings of the first spin.
    @type spin_id1_col:     int
    @keyword spin_id2_col:  The column containing the spin ID strings of the second spin.
    @type spin_id2_col:     int
    @keyword data_col:      The column containing the averaged distances in meters.
    @type data_col:         int or None
    @keyword sep:           The column separator which, if None, defaults to whitespace.
    @type sep:              str or None
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Extract the data from the file.
    file_data = extract_data(file, dir, sep=sep)

    # Loop over the RDC data.
    data = []
    for line in file_data:
        # Invalid columns.
        if spin_id1_col > len(line):
            warn(RelaxWarning("The data %s is invalid, no first spin ID column can be found." % line))
            continue
        if spin_id2_col > len(line):
            warn(RelaxWarning("The data %s is invalid, no second spin ID column can be found." % line))
            continue
        if data_col and data_col > len(line):
            warn(RelaxWarning("The data %s is invalid, no data column can be found." % line))
            continue

        # Unpack.
        spin_id1 = line[spin_id1_col-1]
        spin_id2 = line[spin_id2_col-1]
        ave_dist = None
        if data_col:
            ave_dist = line[data_col-1]

        # Convert and check the value.
        if ave_dist != None:
            try:
                ave_dist = float(ave_dist)
            except ValueError:
                warn(RelaxWarning("The averaged distance of '%s' from the line %s is invalid." % (ave_dist, line)))
                continue

        # Get the interatomic data container.
        interatom = return_interatom(spin_id1, spin_id2)

        # Store the averaged distance.
        interatom.r = ave_dist

        # Store the data for the printout.
        data.append([repr(interatom.spin_id1), repr(interatom.spin_id2), repr(ave_dist)])

    # No data, so fail!
    if not len(data):
        raise RelaxError("No data could be extracted from the file.")

    # Print out.
    print("The following averaged distances have been read:\n")
    write_data(out=sys.stdout, headings=["Spin_ID_1", "Spin_ID_2", "Ave_distance"], data=data)


def set_dist(spin_id1=None, spin_id2=None, ave_dist=None):
    """Set up the magnetic dipole-dipole interaction.

    @keyword spin_id1:      The spin identifier string of the first spin of the pair.
    @type spin_id1:         str
    @keyword spin_id2:      The spin identifier string of the second spin of the pair.
    @type spin_id2:         str
    @keyword ave_dist:      The r^-3 averaged interatomic distance.
    @type ave_dist:         float
    """

    # Generate the selection objects.
    sel_obj1 = Selection(spin_id1)
    sel_obj2 = Selection(spin_id2)

    # Loop over the interatomic containers.
    data = []
    for interatom in interatomic_loop():
        # Get the spin info.
        mol_name1, res_num1, res_name1, spin1 = return_spin(interatom.spin_id1, full_info=True)
        mol_name2, res_num2, res_name2, spin2 = return_spin(interatom.spin_id2, full_info=True)

        # No match, either way.
        if not (sel_obj1.contains_spin(spin_num=spin1.num, spin_name=spin1.name, res_num=res_num1, res_name=res_name1, mol=mol_name1) and sel_obj2.contains_spin(spin_num=spin2.num, spin_name=spin2.name, res_num=res_num2, res_name=res_name2, mol=mol_name2)) and not (sel_obj2.contains_spin(spin_num=spin1.num, spin_name=spin1.name, res_num=res_num1, res_name=res_name1, mol=mol_name1) and sel_obj1.contains_spin(spin_num=spin2.num, spin_name=spin2.name, res_num=res_num2, res_name=res_name2, mol=mol_name2)):
            continue

        # Store the averaged distance.
        interatom.r = ave_dist

        # Store the data for the printout.
        data.append([repr(interatom.spin_id1), repr(interatom.spin_id2), repr(ave_dist)])

    # No data, so fail!
    if not len(data):
        raise RelaxError("No data could be set.")

    # Print out.
    print("The following averaged distances have been set:\n")
    write_data(out=sys.stdout, headings=["Spin_ID_1", "Spin_ID_2", "Ave_distance"], data=data)


def unit_vectors(ave=True):
    """Extract the bond vectors from the loaded structures and store them in the spin container.

    @keyword ave:           A flag which if True will cause the average of all vectors to be calculated.
    @type ave:              bool
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if interatomic data exists.
    if not exists_data():
        raise RelaxNoInteratomError

    # Print out.
    if ave:
        print("Averaging all vectors.")
    else:
        print("No averaging of the vectors.")

    # Loop over the interatomic data containers.
    no_vectors = True
    pos_info = False
    for interatom in interatomic_loop():
        # Get the spin info.
        spin1 = return_spin(interatom.spin_id1)
        spin2 = return_spin(interatom.spin_id2)

        # No positional information.
        if not hasattr(spin1, 'pos'):
            continue
        if not hasattr(spin2, 'pos'):
            continue

        # Positional information flag.
        pos_info = True

        # Both single positions.
        if is_float(spin1.pos[0], raise_error=False) and is_float(spin2.pos[0], raise_error=False):
            # The vector.
            vector_list = [spin2.pos - spin1.pos]

        # A single and multiple position pair.
        elif is_float(spin1.pos[0], raise_error=False) or is_float(spin2.pos[0], raise_error=False):
            # The first spin has multiple positions.
            if is_float(spin2.pos[0], raise_error=False):
                vector_list = []
                for i in range(len(spin1.pos)):
                    vector_list.append(spin2.pos - spin1.pos[i])

            # The second spin has multiple positions.
            else:
                vector_list = []
                for i in range(len(spin2.pos)):
                    vector_list.append(spin2.pos[i] - spin1.pos)

        # Both spins have multiple positions.
        else:
            # Non-matching number of positions.
            if len(spin1.pos) != len(spin2.pos):
                raise RelaxError("The spin '%s' consists of %s positions whereas the spin '%s' consists of %s - these numbers must match." % (interatom.spin_id1, len(spin1.pos), interatom.spin_id1, len(spin1.pos)))

            # Calculate all vectors.
            vector_list = []
            for i in range(len(spin1.pos)):
                vector_list.append(spin2.pos[i] - spin1.pos[i])

        # Average.
        if ave:
            ave_vector = zeros(3, float64)
            for i in range(len(vector_list)):
                ave_vector += vector_list[i]
            vector_list = [ave_vector / len(vector_list)]

        # Unit vectors.
        for i in range(len(vector_list)):
            # Normalisation factor.
            norm_factor = norm(vector_list[i])

            # Test for zero length.
            if norm_factor == 0.0:
                warn(RelaxZeroVectorWarning(id))

            # Calculate the normalised vector.
            else:
                vector_list[i] = vector_list[i] / norm_factor

        # Convert to a single vector if needed.
        if len(vector_list) == 1:
            vector_list = vector_list[0]

        # Store the unit vector(s).
        setattr(interatom, 'vector', vector_list)

        # We have a vector!
        no_vectors = False

        # Print out.
        num = 1
        if not is_float(vector_list[0], raise_error=False):
            num = len(vector_list)
        plural = 's'
        if num == 1:
            plural = ''
        if spin1.name:
            spin1_str = spin1.name
        else:
            spin1_str = spin1.num
        if spin2.name:
            spin2_str = spin2.name
        else:
            spin2_str = spin2.num
        print("Calculated %s %s-%s unit vector%s between the spins '%s' and '%s'." % (num, spin1_str, spin2_str, plural, interatom.spin_id1, interatom.spin_id2))

    # Catch the problem of no positional information being present.
    if not pos_info:
        raise RelaxError("Positional information could not be found for any spins.")

    # Right, catch the problem of missing vectors to prevent massive user confusion!
    if no_vectors:
        raise RelaxError("No vectors could be extracted.")
