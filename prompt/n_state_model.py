###############################################################################
#                                                                             #
# Copyright (C) 2008-2010 Edward d'Auvergne                                   #
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
"""Module containing the 'n_state_model' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
from specific_fns.setup import n_state_model_obj


class N_state_model(User_fn_class):
    """Class for the N-state models."""

    def CoM(self, pivot_point=[0.0, 0.0, 0.0], centre=None):
        """Centre of mass (CoM) analysis.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pivot_point:  The pivot point of the motions between the two domains.

        centre:  The optional argument for manually specifying the CoM of the initial position prior
                 to the N rotations to the positions of the N states.


        Description
        ~~~~~~~~~~~

        This function is used for analysing the domain motion information content of the N states
        from the N-state model.  The states do not correspond to physical states, hence nothing can
        be extracted from the individual states.  This analysis involves the calculation of the
        pivot to centre of mass (pivot-CoM) order parameter and subsequent cone of motions.

        For the analysis, both the pivot point and centre of mass must be specified.  The supplied
        pivot point must be a vector of floating point numbers of length 3.  If the centre keyword
        argument is supplied, it must also be a vector of floating point numbers (of length 3).  If
        the centre argument is not supplied, then the CoM will be calulcated from the selected parts
        of a previously loaded structure.


        Examples
        ~~~~~~~~

        To perform an analysis where the pivot is at the origin and the CoM is set to the N-terminal
        domain of a previously loaded PDB file (the C-terminal domain has been deselected), type:

        relax> n_state_model.CoM()


        To perform an analysis where the pivot is at the origin (because the real pivot has been
        shifted to this position) and the CoM is at the position [0, 0, 1], type one of:

        relax> n_state_model.CoM(centre=[0, 0, 1])
        relax> n_state_model.CoM(centre=[0.0, 0.0, 1.0])
        relax> n_state_model.CoM(pivot_point=[0.0, 0.0, 0.0], centre=[0.0, 0.0, 1.0])
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "n_state_model.CoM("
            text = text + "pivot_point=" + repr(pivot_point)
            text = text + ", centre=" + repr(centre) + ")"
            print(text)

        # The argument checks.
        arg_check.is_num_list(pivot_point, 'pivot point', size=3)
        arg_check.is_num_list(centre, 'centre of mass', size=3, can_be_none=True)

        # Execute the functional code.
        n_state_model_obj._CoM(pivot_point=pivot_point, centre=centre)


    def cone_pdb(self, cone_type=None, scale=1.0, file='cone.pdb', dir=None, force=False):
        """Create a PDB file representing the cone models from the centre of mass (CoM) analysis.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        cone_type:  The type of cone model to represent.

        scale:  Value for scaling the pivot-CoM distance which the size of the cone defaults to.

        file:  The name of the PDB file.

        dir:  The directory where the file is located.

        force:  A flag which, if set to True, will overwrite the any pre-existing file.


        Description
        ~~~~~~~~~~~

        This function creates a PDB file containing an artificial geometric structure to represent
        the various cone models.  These models include:

            'diff in cone'
            'diff on cone'

        The model can be selected by setting the cone_type argument to one of these strings.  The
        cone is represented as an isotropic cone with its axis parallel to the average pivot-CoM
        vector, the vertex placed at the pivot point of the domain motions, and the length of the
        edge of the cone equal to the pivot-CoM distance multipled by the scaling argument.  The
        resultant PDB file can subsequently read into any molecular viewer.

        There are four different types of residue within the PDB.  The pivot point is represented as
        as a single carbon atom of the residue 'PIV'.  The cone consists of numerous H atoms of the
        residue 'CON'.  The average pivot-CoM vector is presented as the residue 'AVE' with one
        carbon atom positioned at the pivot and the other at the head of the vector (after scaling
        by the scale argument).  Finally, if Monte Carlo have been performed, there will be multiple
        'MCC' residues representing the cone for each simulation, and multiple 'MCA' residues
        representing the varying average pivot-CoM vector for each simulation.

        To create the diffusion in a cone PDB representation, a uniform distribution of vectors on a
        sphere is generated using spherical coordinates with the polar angle defined from the
        average pivot-CoM vector.  By incrementing the polar angle using an arccos distribution, a
        radial array of vectors representing latitude are created while incrementing the azimuthal
        angle evenly creates the longitudinal vectors.  These are all placed into the PDB file as H
        atoms and are all connected using PDB CONECT records.  Each H atom is connected to its two
        neighbours on the both the longitude and latitude.  This creates a geometric PDB object with
        longitudinal and latitudinal lines representing the filled cone.
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "n_state_model.cone_pdb("
            text = text + "cone_type=" + repr(cone_type)
            text = text + ", scale=" + repr(scale)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(cone_type, 'cone type')
        arg_check.is_num(scale, 'scaling factor')
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        n_state_model_obj._cone_pdb(cone_type=cone_type, scale=scale, file=file, dir=dir, force=force)


    def number_of_states(self, N=None):
        """Set the number of states in the N-state model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        N:  The number of states.


        Description
        ~~~~~~~~~~~

        Prior to optimisation, the number of states in the N-state model can be specified.  If the
        number of states is not set, then this parameter will be equal to the number of loaded
        structures.


        Examples
        ~~~~~~~~

        To set up an 8-state model, type:

        relax> n_state_model.number_of_states(N=8)
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "n_state_model.number_of_states("
            text = text + "N=" + repr(N) + ")"
            print(text)

        # The argument checks.
        arg_check.is_int(N, 'number of states N')

        # Execute the functional code.
        n_state_model_obj._number_of_states(N=N)


    def ref_domain(self, ref=None):
        """Set the reference domain for the '2-domain' N-state model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        ref:  The domain which will act as the frame of reference.  This is only valid for the
        '2-domain' N-state model.


        Description
        ~~~~~~~~~~~

        Prior to optimisation of the '2-domain' N-state model, which of the two domains will act as
        the frame of reference must be specified.  The N-states will be rotations of the other
        domain, so to switch the frame of reference to the other domain simply transpose the
        rotation matrices.


        Examples
        ~~~~~~~~

        To set up a 5-state model with 'C' domain being the frame of reference, type:

        relax> n_state_model.ref_domain(ref='C')
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "n_state_model.ref_domain("
            text = text + "ref=" + repr(ref) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(ref, 'reference frame')

        # Execute the functional code.
        n_state_model_obj._ref_domain(ref=ref)


    def select_model(self, model=None):
        """Select the N-state model type and set up the model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the preset N-state model.


        Description
        ~~~~~~~~~~~

        Prior to optimisation, the N-state model type should be selected.  The preset models are:

        '2-domain' - The N-state model for a system of two domains, where one domain experiences a
        a reduced tensor.

        'population' - The N-state model whereby only populations are optimised.  The structures
        loaded into relax are assumed to be fixed.  I.e. if two domains are present, the Euler
        angles for each state are fixed.  The parameters of the model include the weight or
        probability for each state and the alignment tensor - {p0, p1, ..., pN, Axx, Ayy, Axy, Axz,
        Ayz}.

        'fixed' - The N-state model whereby all motions are fixed and all populations are fixed to
        the set probabilities.  The parameters of the model are simply the alignment tensor, {Axx,
        Ayy, Axy, Axz, Ayz}.


        Examples
        ~~~~~~~~

        To analyse populations of states, type:

        relax> n_state_model.select_model(model='populations')
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "n_state_model.select_model("
            text = text + "model=" + repr(model) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(model, 'model')

        # Execute the functional code.
        n_state_model_obj._select_model(model=model)
