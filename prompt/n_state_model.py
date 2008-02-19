###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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

# Python module imports.
import sys

# relax module imports.
import help
from specific_fns.setup import n_state_model_obj
from relax_errors import RelaxBoolError, RelaxIntError, RelaxLenError, RelaxListError, RelaxListNumError, RelaxNoneStrError, RelaxNumError, RelaxStrError


class N_state_model:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the alignment tensor."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


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
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "n_state_model.CoM("
            text = text + "pivot_point=" + `pivot_point`
            text = text + ", centre=" + `centre` + ")"
            print text

        # Pivot point argument.
        if type(pivot_point) != list:
            raise RelaxListError, ('pivot point', pivot_point)
        if len(pivot_point) != 3:
            raise RelaxLenError, ('pivot point', 3)
        for i in xrange(len(pivot_point)):
            if type(pivot_point[i]) != int and type(pivot_point[i]) != float:
                raise RelaxListNumError, ('pivot point', pivot_point)

        # CoM argument.
        if centre != None:
            if type(centre) != list:
                raise RelaxListError, ('centre of mass', centre)
            if len(centre) != 3:
                raise RelaxLenError, ('centre of mass', 3)
            for i in xrange(len(centre)):
                if type(centre[i]) != int and type(centre[i]) != float:
                    raise RelaxListNumError, ('centre of mass', centre)

        # Execute the functional code.
        n_state_model_obj.CoM(pivot_point=pivot_point, centre=centre)


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
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "n_state_model.cone_pdb("
            text = text + "cone_type=" + `cone_type`
            text = text + ", scale=" + `scale`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

        # Cone type.
        if type(cone_type) != str:
            raise RelaxStrError, ('cone type', cone_type)

        # Scaling.
        if type(scale) != float and type(scale) != int:
            raise RelaxNumError, ('scaling factor', scale)

        # File name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The force flag.
        if type(force) != bool:
            raise RelaxBoolError, ('force flag', force)

        # Execute the functional code.
        n_state_model.cone_pdb(cone_type=cone_type, scale=scale, file=file, dir=dir, force=force)


    def model(self, N=None, ref=None):
        """Set up the N-state model by specifying the number of states N and the reference domain.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        N:  The number of states.

        ref:  The domain which will act as the frame of reference.


        Description
        ~~~~~~~~~~~

        Prior to optimisation, the N-state model must be set up.  This simply involves the setting
        of the number of states N and which of the two domains will act as the frame of reference.
        The N-states will be rotations of the other domain.  To switch the frame of reference to the
        other domain, transpose the rotation matrices.


        Examples
        ~~~~~~~~

        To set up a 5-state model with 'C' domain being the frame of reference, type:

        relax> n_state_model.model(N=5, ref='C')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "n_state_model.model("
            text = text + "N=" + `N`
            text = text + ", ref=" + `ref` + ")"
            print text

        # Number of states argument.
        if type(N) != int:
            raise RelaxIntError, ('the number of states N', N)

        # Ref frame argument.
        if type(ref) != str:
            raise RelaxStrError, ('reference frame', ref)

        # Execute the functional code.
        n_state_model_obj.model_setup(N=N, ref=ref)


    def set_domain(self, tensor=None, domain=None):
        """Set the domain label for the alignment tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        tensor:  The alignment tensor to assign the domain label to.

        domain:  The domain label.


        Description
        ~~~~~~~~~~~

        Prior to optimisation of the N-state model, the domain to which each alignment tensor
        belongs must be specified.


        Examples
        ~~~~~~~~

        To link the alignment tensor loaded as 'chi3 C-dom' to the C-terminal domain 'C', type:

        relax> n_state_model.set_domain(tensor='chi3 C-dom', domain='C')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "n_state_model.set_domain("
            text = text + "tensor=" + `tensor`
            text = text + ", domain=" + `domain` + ")"
            print text

        # Tensor argument.
        if type(tensor) != str:
            raise RelaxStrError, ('tensor', tensor)

        # Domain argument.
        if type(domain) != str:
            raise RelaxStrError, ('domain', domain)

        # Execute the functional code.
        n_state_model_obj.set_domain(tensor=tensor, domain=domain)


    def set_type(self, tensor=None, red=False):
        """Set whether the alignment tensor is the full or reduced tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        tensor:  The alignment tensor identification string.

        red:  The state of the alignment tensor.  If True, then it is labelled as the full tensor.
        If False, then it is labelled as the tensor reduced because of domain motions.


        Description
        ~~~~~~~~~~~

        Prior to optimisation of the N-state model the state of alignment tensor, whether it is the
        full or reduced tensor, must be set using this user function.


        Examples
        ~~~~~~~~

        To state that the alignment tensor loaded as 'chi3 C-dom' is the reduced tensor, type:

        relax> n_state_model.set_type(tensor='chi3 C-dom', red=True)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "n_state_model.set_type("
            text = text + "tensor=" + `tensor`
            text = text + ", red=" + `red` + ")"
            print text

        # Tensor argument.
        if type(tensor) != str:
            raise RelaxStrError, ('tensor', tensor)

        # Red argument.
        if type(red) != bool:
            raise RelaxBoolError, ('red', red)

        # Execute the functional code.
        n_state_model_obj.set_type(tensor=tensor, red=red)
