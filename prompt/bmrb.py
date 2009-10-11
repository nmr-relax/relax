###############################################################################
#                                                                             #
# Copyright (C) 2003-2005,2008-2009 Edward d'Auvergne                         #
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
"""Module containing the BMRB user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
from base_class import User_fn_class
import check
from generic_fns import bmrb, exp_info
from relax_errors import RelaxBoolError, RelaxIntError, RelaxNoneStrError, RelaxStrError, RelaxStrFileError


class BMRB(User_fn_class):
    """Class for interfacing with the BMRB (http://www.bmrb.wisc.edu/)."""

    def display(self, version='3.1'):
        """Display the BMRB data in NMR-STAR format."""

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "bmrb.display("
            text = text + "version=" + repr(version) + ")"
            print(text)

        # Execute the functional code.
        bmrb.display(version=version)


    def read(self, file=None, dir=None, version='3.1'):
        """Read BMRB files in the NMR-STAR format.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the BMRB STAR formatted file.

        dir:  The directory where the file is located.


        Description
        ~~~~~~~~~~~

        To search for the results file in the current working directory, set dir to None.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "bmrb.read("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", version=" + repr(version) + ")"
            print(text)

        # The argument checks.
        check.is_str(file, 'file name')
        check.is_str(dir, 'directory name', can_be_none=True)
        check.is_str(version, 'NMR-STAR dictionary version')

        # Execute the functional code.
        bmrb.read(file=file, directory=dir, version=version)


    def software(self, name=None, version=None, url=None, vendor_name=None, cite=None, tasks=None):
        """Specify the software used in the analysis.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        name:  The name of the software program utilised.

        version:  The version of the software, if applicable.

        url:  The web address of the software.

        vendor_name:  The name of the company or person behind the program.

        cite:  The literature citation for the software.

        tasks:  A list of all the tasks performed by the software.


        Description
        ~~~~~~~~~~~

        This user function allows the software used in the analysis to be specified in full detail.

        For the tasks list, this should be a python list of strings (eg. ['spectral processing']).
        Although not restricted to these, the values suggested by the BMRB are:

            'chemical shift assignment',
            'chemical shift calculation',
            'collection',
            'data analysis',
            'geometry optimization',
            'peak picking',
            'processing',
            'refinement',
            'structure solution'


        Examples
        ~~~~~~~~

        For BMRB deposition, to say that Sparky was used in the analysis, type:

        relax> bmrb.software('Sparky', version='3.110', url="http://www.cgl.ucsf.edu/home/sparky/",
                             vendor_name="Goddard, T. D.", cite="Goddard, T. D. and Kneller, D. G.,
                             SPARKY 3, University of California, San Francisco.",
                             tasks=["spectral analysis"])
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "bmrb.software_select("
            text = text + "name=" + repr(name)
            text = text + ", version=" + repr(version)
            text = text + ", url=" + repr(url)
            text = text + ", vendor_name=" + repr(vendor_name)
            text = text + ", cite=" + repr(cite)
            text = text + ", tasks=" + repr(tasks) + ")"
            print(text)

        # The argument checks.
        check.is_str(name, 'program name')
        check.is_str(version, 'version', can_be_none=True)
        check.is_str(url, 'url', can_be_none=True)
        check.is_str(vendor_name, 'vendor_name', can_be_none=True)
        check.is_str(cite, 'cite', can_be_none=True)
        check.is_str_list(tasks, 'tasks', can_be_none=True)

        # Execute the functional code.
        exp_info.software(name=name, version=version, url=url, vendor_name=vendor_name, cite=cite, tasks=tasks)


    def software_select(self, name=None, version=None):
        """Select the software used in the analysis.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        name:  The name of the software program utilised.

        version:  The version of the software, if applicable.


        Description
        ~~~~~~~~~~~

        Rather than specifying all the information directly, this user function allows the software
        packaged used in the analysis to be selected by name.  The programs currently supported are:

            'NMRPipe' - http://spin.niddk.nih.gov/NMRPipe/
            'Sparky' - http://www.cgl.ucsf.edu/home/sparky/

        More can be added if all relevant information (program name, description, website, original
        citation, purpose, etc.) is emailed to relax-users@gna.org.

        Note that relax is automatically added to the BMRB file.


        Examples
        ~~~~~~~~

        For BMRB deposition, to say that both NMRPipe and Sparky were used prior to relax, type:

        relax> bmrb.software_select('NMRPipe')
        relax> bmrb.software_select('Sparky', version='3.113')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "bmrb.software_select("
            text = text + "name=" + repr(name)
            text = text + ", version=" + repr(version) + ")"
            print(text)

        # The argument checks.
        check.is_str(name, 'program name')
        check.is_str(version, 'version', can_be_none=True)

        # Execute the functional code.
        exp_info.software_select(name=name, version=version)


    def write(self, file=None, dir='pipe_name', version='3.1', force=False):
        """Write the results to a BMRB NMR-STAR formatted file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the BMRB file to output results to.  Optionally this can be a file
        object, or any object with a write() method.

        dir:  The directory name.

        version:  The NMR-STAR dictionary format version to use.
.sconsign.dblite
        force:  A flag which if True will cause the any pre-existing file to be overwritten.


        Description
        ~~~~~~~~~~~

        To place the BMRB file in the current working directory, set dir to None.  If dir is set
        to the special name 'pipe_name', then the results file will be placed into a directory with
        the same name as the current data pipe.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "bmrb.write("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", version=" + repr(version)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        check.is_str(file, 'file name')
        check.is_str(dir, 'directory name', can_be_none=True)
        check.is_str(version, 'NMR-STAR dictionary version')
        check.is_bool(force, 'force flag')

        # Execute the functional code.
        bmrb.write(file=file, directory=dir, version=version, force=force)
