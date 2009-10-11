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
        # The relax version.
        ver = version
        if ver == 'repository checkout':
            # Get the SVN revision and URL.
            rev = get_revision()
            url = get_url()

            # Change the version string.
            if rev:
                ver = version + " r" + rev
            if url:
                ver = ver + " " + url

        cdp.exp_info.software_setup(name='relax', version=ver, vendor_name='The relax development team', vendor_eaddress='http://nmr-relax.com', cite="d'Auvergne, E. J. and Gooley, P. R. (2008).  Optimisation of NMR dynamic models I.  Minimisation algorithms and their performance within the model-free and Brownian rotational diffusion spaces.  J. Biomol. NMR, 40(2), 107-119;  d'Auvergne, E. J. and Gooley, P. R. (2008).  Optimisation of NMR dynamic models II.  A new methodology for the dual optimisation of the model-free parameters and the Brownian rotational diffusion tensor.  J. Biomol. NMR, 40(2), 121-133.", task='data processing')

    # NMRPipe.
    if name == 'NMRPipe':
        cdp.exp_info.software_setup('NMRPipe', version=version, url="http://spin.niddk.nih.gov/NMRPipe/", vendor_name="Delaglio, F.", cite="Delaglio, F., Grzesiek, S., Vuister, G. W., Zhu, G., Pfeifer, J., and Bax, A. (1995).  NMRPipe: a multidimensional spectral processing system based on UNIX pipes.  J. Biomol. NMR. 6, 277-293.", tasks=["processing"])

    # Sparky.
    elif name == 'Sparky':
        # Check if the version information has been supplied.
        if not version:
            raise RelaxError("The Sparky version number has not been supplied.")

        # Add the data.
        cdp.exp_info.software_setup('Sparky', version=version, url="http://www.cgl.ucsf.edu/home/sparky/", vendor_name="Goddard, T. D.", cite="Goddard, T. D. and Kneller, D. G., SPARKY 3, University of California, San Francisco.", tasks=["spectral analysis"])
