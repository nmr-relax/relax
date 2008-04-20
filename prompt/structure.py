###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004, 2006-2008 Edward d'Auvergne                       #
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
import generic_fns.structure.geometric
import generic_fns.structure.main
import help
from relax_errors import RelaxBinError, RelaxBoolError, RelaxFloatError, RelaxIntError, RelaxNoneIntError, RelaxNoneStrError, RelaxNumError, RelaxStrError


class Structure:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class containing the structural related functions."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def create_diff_tensor_pdb(self, scale=1.8e-6, file='tensor.pdb', dir=None, force=False):
        """Create a PDB file to represent the diffusion tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        scale:  Value for scaling the diffusion rates.

        file:  The name of the PDB file.

        dir:  The directory where the file is located.

        force:  A flag which, if set to True, will overwrite the any pre-existing file.


        Description
        ~~~~~~~~~~~

        This function creates a PDB file containing an artificial geometric structure to represent
        the diffusion tensor.  A structure must have previously been read into relax.  The diffusion
        tensor is represented by an ellipsoidal, spheroidal, or spherical geometric object with its
        origin located at the centre of mass (of the selected residues).  This diffusion tensor PDB
        file can subsequently read into any molecular viewer.

        There are four different types of residue within the PDB.  The centre of mass of the
        selected residues is represented as a single carbon atom of the residue 'COM'.  The
        ellipsoidal geometric shape consists of numerous H atoms of the residue 'TNS'.  The axes
        of the tensor, when defined, are presented as the residue 'AXS' and consist of carbon atoms:
        one at the centre of mass and one at the end of each eigenvector.  Finally, if Monte Carlo
        simulations were run and the diffusion tensor parameters were allowed to vary then there
        will be multiple 'SIM' residues, one for each simulation.  These are essentially the same as
        the 'AXS' residue, representing the axes of the simulated tensors, and they will appear as a
        distribution.

        As the Brownian rotational diffusion tensor is a measure of the rate of rotation about
        different axes - the larger the geometric object, the faster the diffusion of a molecule.
        For example the diffusion tensor of a water molecule is much larger than that of a
        macromolecule.

        The effective global correlation time experienced by an XH bond vector, not to be confused
        with the Lipari and Szabo parameter tau_e, will be approximately proportional to the
        component of the diffusion tensor parallel to it.  The approximation is not exact due to the
        multiexponential form of the correlation function of Brownian rotational diffusion.  If an
        XH bond vector is parallel to the longest axis of the tensor, it will be unaffected by
        rotations about that axis, which are the fastest rotations of the molecule, and therefore
        its effective global correlation time will be maximal.

        To set the size of the diffusion tensor within the PDB frame the unit vectors used to
        generate the geometric object are first multiplied by the diffusion tensor (which has the
        units of inverse seconds) then by the scaling factor (which has the units of second
        Angstroms and has the default value of 1.8e-6 s.Angstrom).  Therefore the rotational
        diffusion rate per Angstrom is equal the inverse of the scale value (which defaults to
        5.56e5 s^-1.Angstrom^-1).  Using the default scaling value for spherical diffusion, the
        correspondence between global correlation time, Diso diffusion rate, and the radius of the
        sphere for a number of discrete cases will be:

        _________________________________________________
        |           |               |                   |
        | tm (ns)   | Diso (s^-1)   | Radius (Angstrom) |
        |___________|_______________|___________________|
        |           |               |                   |
        | 1         | 1.67e8        | 300               |
        |           |               |                   |
        | 3         | 5.56e7        | 100               |
        |           |               |                   |
        | 10        | 1.67e7        | 30                |
        |           |               |                   |
        | 30        | 5.56e6        | 10                |
        |___________|_______________|___________________|


        The scaling value has been fixed to facilitate comparisons within or between publications,
        but can be changed to vary the size of the tensor geometric object if necessary.  Reporting
        the rotational diffusion rate per Angstrom within figure legends would be useful.

        To create the tensor PDB representation, a number of algorithms are utilised.  Firstly the
        centre of mass is calculated for the selected residues and is represented in the PDB by a C
        atom.  Then the axes of the diffusion are calculated, as unit vectors scaled to the
        appropriate length (multiplied by the eigenvalue Dx, Dy, Dz, Dpar, Dper, or Diso as well as
        the scale value), and a C atom placed at the position of this vector plus the centre of
        mass.  Finally a uniform distribution of vectors on a sphere is generated using spherical
        coordinates.  By incrementing the polar angle using an arccos distribution, a radial array
        of vectors representing latitude are created while incrementing the azimuthal angle evenly
        creates the longitudinal vectors.  These unit vectors, which are distributed within the PDB
        frame and are of 1 Angstrom in length, are first rotated into the diffusion frame using a
        rotation matrix (the spherical diffusion tensor is not rotated).  Then they are multiplied
        by the diffusion tensor matrix to extend the vector out to the correct length, and finally
        multiplied by the scale value so that the vectors reasonably superimpose onto the
        macromolecular structure.  The last set of algorithms place all this information into a PDB
        file.  The distribution of vectors are represented by H atoms and are all connected using
        PDB CONECT records.  Each H atom is connected to its two neighbours on the both the
        longitude and latitude.  This creates a geometric PDB object with longitudinal and
        latitudinal lines.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "structure.create_diff_tensor_pdb("
            text = text + "scale=" + `scale`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", force=" + `force` + ")"
            print text

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
        generic_fns.structure.geometric.create_diff_tensor_pdb(scale=scale, file=file, dir=dir, force=force)


    def create_vector_dist(self, length=2e-9, file='XH_dist.pdb', dir=None, symmetry=True, force=False):
        """Create a PDB file representation of the distribution of XH bond vectors.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        length:  The length of the vectors in the PDB representation (meters).

        file:  The name of the PDB file.

        dir:  The directory to place the file into.

        symmetry:  A flag which if True will create a second chain with reversed XH bond
            orientations.

        force:  A flag which if True will overwrite the file if it already exists.


        Description
        ~~~~~~~~~~~

        This function creates a PDB file containing an artificial vectors, the length of which
        default to the length argument of 20 Angstrom.  A structure must have previously been read
        into relax.  The origin of the vector distribution is located at the centre of mass (of the
        selected residues).  This vector distribution PDB file can subsequently be read into any
        molecular viewer.

        Because of the symmetry of the diffusion tensor reversing the orientation of the XH bond
        vector has no effect.  Therefore by setting the symmetry flag two chains 'A' and 'B' will
        be added to the PDB file whereby chain 'B' is chain 'A' with the XH bonds reversed.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "structure.create_vector_dist("
            text = text + "length=" + `length`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", symmetry=" + `symmetry`
            text = text + ", force=" + `force` + ")"
            print text

        # Vector length.
        if type(length) != float:
            raise RelaxFloatError, ('vector length', length)

        # File name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The symmetry flag.
        if type(symmetry) != bool:
            raise RelaxBoolError, ('symmetry flag', symmetry)

        # The force flag.
        if type(force) != bool:
            raise RelaxBoolError, ('force flag', force)

        # Execute the functional code.
        generic_fns.structure.geometric.create_vector_dist(length=length, symmetry=symmetry, file=file, dir=dir, force=force)


    def load_spins(self, spin_id=None):
        """Load spins from the structure into the relax data store.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spin_id:  The spin identification string.


        Description
        ~~~~~~~~~~~

        This function allows a sequence to be generated within the relax data store using the atomic
        information from the structure already associated with this data pipe.  The spin_id string
        is used to select which molecules, which residues, and which atoms will be recognised as
        spin systems within relax.  If spin_id is left as None, then all molcules, residues, and
        atoms will be placed within the data store.


        Example
        ~~~~~~~

        For a model-free backbone amide nitrogen analysis, to load just the backbone N sequence from
        the file '1F3Y.pdb' (which is a single protein), type the follow two user functions:

        relax> structure.read_pdb('1F3Y.pdb')
        relax> structure.load_spins(spin_id='@N')


        For an RNA analysis of adenine C8 and C2, guanine C8 and N1, cytidine C5 and C6, and uracil
        N3, C5, and C6, type the following series of commands (assuming that the PDB file with this
        atom naming has already been read):

        relax> structure.load_spins(spin_id=':A@C8&@C2')
        relax> structure.load_spins(spin_id=':G@C8&@N1')
        relax> structure.load_spins(spin_id=':C@C5&@C6')
        relax> structure.load_spins(spin_id=':U@N3&@C5&@C6')

        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "structure.load_spins("
            text = text + "spin_id=" + `spin_id` + ")"
            print text

        # Spin identifier.
        if spin_id != None and type(spin_id) != str:
            raise RelaxNoneStrError, ('spin identifier', spin_id)

        # Execute the functional code.
        generic_fns.structure.main.load_spins(spin_id=spin_id)


    def read_pdb(self, file=None, dir=None, model=None, parser='scientific'):
        """The PDB loading function.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the PDB file.

        dir:  The directory where the file is located.

        model:  The PDB model number.

        parser:  The PDB parser used to read the file.


        Description
        ~~~~~~~~~~~

        To load a specific model from the PDB file, set the model flag to an integer i.  The
        structure beginning with the line 'MODEL i' in the PDB file will be loaded.  Otherwise all
        structures will be loaded starting from the model number 1.

        Currently only the Scientific Python PDB parser can be used to read structural data.
        Therefore the 'parser' argument should be set to the string 'scientific'.


        Example
        ~~~~~~~

        To load all structures from the PDB file 'test.pdb' in the directory '~/pdb', type:

        relax> structure.read_pdb('test.pdb', '~/pdb')
        relax> structure.read_pdb(file='test.pdb', dir='pdb')


        To load the 10th model from the file 'test.pdb', use:

        relax> structure.read_pdb('test.pdb', model=10)
        relax> structure.read_pdb(file='test.pdb', model=10)

        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "structure.read_pdb("
            text = text + "file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", model=" + `model`
            text = text + ", parser=" + `parser` + ")"
            print text

        # File name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The model argument.
        if model != None and type(model) != int:
            raise RelaxNoneIntError, ('model', model)

        # PDB parser.
        if type(parser) != str:
            raise RelaxStrError, ('PDB parser', parser)

        # Execute the functional code.
        generic_fns.structure.main.read_pdb(file=file, dir=dir, model=model, parser=parser)


    def vectors(self, proton='H', spin_id=None, verbosity=1):
        """Function for calculating/extracting XH vectors from the structure.

        Keyword arguments
        ~~~~~~~~~~~~~~~~~

        proton:  The name of the proton attached to the spin, as specified in the structural file.

        spin_id:  The spin identification string.

        verbosity:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.


        Description
        ~~~~~~~~~~~

        Once the structures have been loaded, the unit XH bond vectors must be extracted for the
        non-spherical diffusion models.  The vectors are calculated using the atomic coordinates
        of the atoms specified by spin itself and its singly attached proton.

        If more than one model structure is loaded, the unit XH vectors for each model will be
        calculated and the final unit XH vector will be taken as the average.


        Example
        ~~~~~~~

        To calculate the XH vectors of the backbone amide nitrogens where in the PDB file the
        backbone nitrogen is called 'N' and the attached proton is called 'H', assuming multiple
        types of spin have already been loaded, type one of:

        relax> structure.vectors(spin_id='@N')
        relax> structure.vectors('H', spin_id='@N')
        relax> structure.vectors(proton='H', spin_id='@N')

        If the attached proton is called 'HN', type:

        relax> structure.vectors(proton='HN', spin_id='@N')

        For the Ca, type:

        relax> structure.vectors(proton='HA', spin_id='@CA')


        If you are working with RNA, you can use the residue name identifier to calculate the
        vectors for each residue separately.  For example to calculate the vectors for all possible
        spins in the bases, type:

        relax> structure.vectors('H2', spin_id=':A')
        relax> structure.vectors('H8', spin_id=':A')
        relax> structure.vectors('H1', spin_id=':G')
        relax> structure.vectors('H8', spin_id=':G')
        relax> structure.vectors('H5', spin_id=':C')
        relax> structure.vectors('H6', spin_id=':C')
        relax> structure.vectors('H3', spin_id=':U')
        relax> structure.vectors('H5', spin_id=':U')
        relax> structure.vectors('H6', spin_id=':U')

        Alternatively, assuming the desired spins have been loaded, regular expression can be used:

        relax> structure.vectors('H*')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "structure.vectors("
            text = text + "proton=" + `proton`
            text = text + ", spin_id=" + `spin_id`
            text = text + ", verbosity=" + `verbosity` + ")"
            print text

        # The attached proton argument.
        if type(proton) != str:
            raise RelaxStrError, ('the attached proton', proton)

        # Spin identification string.
        if spin_id != None and type(spin_id) != str:
            raise RelaxNoneStrError, ('Spin identification string', spin_id)

        # The verbosity level.
        if type(verbosity) != int:
            raise RelaxIntError, ('verbosity level', verbosity)

        # Execute the functional code.
        generic_fns.structure.main.vectors(proton=proton, spin_id=spin_id, verbosity=verbosity)
