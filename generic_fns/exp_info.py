###############################################################################
#                                                                             #
# Copyright (C) 2008-2009 Edward d'Auvergne                                   #
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
"""Module containing functions for specifying the experimental details."""

# relax module imports.
from data.exp_info import ExpInfo
from relax_errors import RelaxError
from version import version_full


# relax fixed info.
RELAX_NAME = "relax"
RELAX_AUTHORS = "The relax development team"
RELAX_REF = "d'Auvergne, E. J. and Gooley, P. R. (2008).  Optimisation of NMR dynamic models I.  Minimisation algorithms and their performance within the model-free and Brownian rotational diffusion spaces.  J. Biomol. NMR, 40(2), 107-119;  d'Auvergne, E. J. and Gooley, P. R. (2008).  Optimisation of NMR dynamic models II.  A new methodology for the dual optimisation of the model-free parameters and the Brownian rotational diffusion tensor.  J. Biomol. NMR, 40(2), 121-133."
RELAX_URL = "http://nmr-relax.com"
RELAX_TASKS = ["data processing"]

# NMRPipe fixed info.
NMRPIPE_NAME = "NMRPipe"
NMRPIPE_AUTHORS = "Delaglio, F."
NMRPIPE_REF = "Delaglio, F., Grzesiek, S., Vuister, G. W., Zhu, G., Pfeifer, J., and Bax, A. (1995).  NMRPipe: a multidimensional spectral processing system based on UNIX pipes.  J. Biomol. NMR. 6, 277-293."
NMRPIPE_URL = "http://spin.niddk.nih.gov/NMRPipe/"
NMRPIPE_TASKS = ["processing"]

# Sparky fixed info.
SPARKY_NAME = "Sparky"
SPARKY_AUTHORS = "Goddard, T. D."
SPARKY_REF = "Goddard, T. D. and Kneller, D. G., SPARKY 3, University of California, San Francisco."
SPARKY_URL = "http://www.cgl.ucsf.edu/home/sparky/"
SPARKY_TASKS = ["spectral analysis"]



def bmrb_write_software(star):
    """Generate the Software saveframe records.

    @param star:        The NMR-STAR dictionary object.
    @type star:         NMR_STAR instance
    """

    # First add relax.
    star.software.add(name=RELAX_NAME, version=version_full(), vendor_name=RELAX_AUTHORS, vendor_eaddress=RELAX_URL, task=RELAX_TASKS)

    # Loop over the software.
    if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'software'):
        for software in cdp.exp_info.software:
            # The program info.
            star.software.add(name=software.name, version=software.version, vendor_name=software.vendor_name, vendor_eaddress=software.url, task=software.tasks)

    # Throw a warning.
    else:


def software(name=None, version=None, url=None, vendor_name=None, cite=None, tasks=None):
    """Select by name the software used in the analysis.

    @param name:            The name of the software program.
    @type name:             str
    @keyword version:       The program version.
    @type version:          None or str
    @keyword url:           The program's URL.
    @type url:              None or str
    @keyword vendor_name:   The name of the company or person behind the program.
    @type vendor_name:      str
    @keyword cite:          The literature citation.
    @type cite:             None or str
    @keyword tasks:         The tasks performed by the program.
    @type tasks:            list of str
    """

    # Set up the experimental info data container, if needed.
    if not hasattr(cdp, 'exp_info'):
        cdp.exp_info = ExpInfo()

    # Place the data in the container.
    cdp.exp_info.software_setup(name=name, version=version, url=url, vendor_name=vendor_name, cite=cite, tasks=tasks)


def software_select(name, version=None):
    """Select by name the software used in the analysis.

    @param name:        The name of the software program.
    @type name:         str
    @keyword version:   The program version.
    @type version:      None or str
    """

    # Unknown program.
    if name not in ['relax', 'NMRPipe', 'Sparky']:
        raise RelaxError("The software '%s' is unknown.  Please use the user function for manually specifying software details instead." % name)

    # Set up the experimental info data container, if needed.
    if not hasattr(cdp, 'exp_info'):
        cdp.exp_info = ExpInfo()

    # relax.
    if name == 'relax':
        cdp.exp_info.software_setup(name=RELAX_NAME, version=version_full(), vendor_name=RELAX_AUTHORS, url=RELAX_URL, cite=RELAX_REF, tasks=RELAX_TASKS)

    # NMRPipe.
    if name == 'NMRPipe':
        cdp.exp_info.software_setup(name=NMRPIPE_NAME, version=version, vendor_name=NMRPIPE_AUTHORS, url=NMRPIPE_URL, cite=NMRPIPE_REF, tasks=NMRPIPE_TASKS)

    # Sparky.
    elif name == 'Sparky':
        # Check if the version information has been supplied.
        if not version:
            raise RelaxError("The Sparky version number has not been supplied.")

        # Add the data.
        cdp.exp_info.software_setup(name=SPARKY_NAME, version=version, vendor_name=SPARKY_AUTHORS, url=SPARKY_URL, cite=SPARKY_REF, tasks=SPARKY_TASKS)
