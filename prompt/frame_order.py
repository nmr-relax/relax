###############################################################################
#                                                                             #
# Copyright (C) 2009-2010 Edward d'Auvergne                                   #
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
"""Module containing the user function class of the Frame Order theories."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
from specific_fns.setup import frame_order_obj


class Frame_order(User_fn_class):
    """Class containing the user functions of the Frame Order theories."""

    def cone_pdb(self, size=30.0, inc=40, file='cone.pdb', dir=None, force=False):
        """Create a PDB file representing the Frame Order cone models.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        size:  The size of the geometric object in Angstroms.

        inc:  The number of increments used to create the geometric object.

        file:  The name of the PDB file to create.

        dir:  The directory where the file is to be located.

        force:  A flag which, if set to True, will overwrite the any pre-existing file.


        Description
        ~~~~~~~~~~~

        This function creates a PDB file containing an artificial geometric structure representing
        the Frame Order cone models.

        There are four different types of residue within the PDB.  The pivot point is represented as
        as a single carbon atom of the residue 'PIV'.  The cone consists of numerous H atoms of the
        residue 'CON'.  The cone axis vector is presented as the residue 'AXE' with one carbon atom
        positioned at the pivot and the other x Angstroms away on the cone axis (set by the size
        argument).  Finally, if Monte Carlo have been performed, there will be multiple 'MCC'
        residues representing the cone for each simulation, and multiple 'MCA' residues representing
        the multiple cone axes.

        To create the diffusion in a cone PDB representation, a uniform distribution of vectors on a
        sphere is generated using spherical coordinates with the polar angle defined by the cone
        axis.  By incrementing the polar angle using an arccos distribution, a radial array of
        vectors representing latitude are created while incrementing the azimuthal angle evenly
        creates the longitudinal vectors.  These are all placed into the PDB file as H atoms and are
        all connected using PDB CONECT records.  Each H atom is connected to its two neighbours on
        the both the longitude and latitude.  This creates a geometric PDB object with longitudinal
        and latitudinal lines representing the filled cone.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "frame_order.cone_pdb("
            text = text + "size=" + repr(size)
            text = text + ", inc=" + repr(inc)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_num(size, 'geometric object size')
        arg_check.is_int(inc, 'increment number')
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        frame_order_obj._cone_pdb(size=size, inc=inc, file=file, dir=dir, force=force)


    def pivot(self, pivot=None):
        """Set the pivot point for the two body motion in the structural coordinate system.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pivot:  The pivot point for the motion (e.g. the position between the 2 domains in PDB
            coordinates).


        Examples
        ~~~~~~~~

        To set the pivot point, type one of:

        relax> frame_order.pivot([12.067, 14.313, -3.2675])
        relax> frame_order.pivot(pivot=[12.067, 14.313, -3.2675])
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "frame_order.pivot("
            text = text + "pivot=" + repr(pivot) + ")"
            print(text)

        # The argument checks.
        arg_check.is_num_list(pivot_point, 'pivot point', size=3)

        # Execute the functional code.
        frame_order_obj._pivot(pivot=pivot)


    def ref_domain(self, ref=None):
        """Set the reference domain for the '2-domain' Frame Order theories.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        ref:  The domain which will act as the frame of reference.  This is only valid for the
        '2-domain' Frame Order theories.


        Description
        ~~~~~~~~~~~

        Prior to optimisation of the '2-domain' Frame Order theories, which of the two domains will
        act as the frame of reference must be specified.  This is important for the attachment of
        cones to domains, etc.


        Examples
        ~~~~~~~~

        To set up the isotropic cone frame order model with 'centre' domain being the frame of reference, type:

        relax> frame_order.ref_domain(ref='centre')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "frame_order.ref_domain("
            text = text + "ref=" + repr(ref) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(ref, 'reference frame')

        # Execute the functional code.
        frame_order_obj._ref_domain(ref=ref)


    def select_model(self, model=None):
        """Select and set up the Frame Order model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the preset Frame Order model.


        Description
        ~~~~~~~~~~~

        Prior to optimisation, the Frame Order model should be selected.  The list of available
        models are:

        'iso cone' - The isotropic cone model.


        Examples
        ~~~~~~~~

        To select the isotropic cone model, type:

        relax> frame_order.select_model(model='iso cone')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "frame_order.select_model("
            text = text + "model=" + repr(model) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(model, 'Frame Order model')

        # Execute the functional code.
        frame_order_obj._select_model(model=model)
