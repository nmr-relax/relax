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
RELAX_URL = "http://nmr-relax.com"
RELAX_TASKS = ["data processing"]
RELAX_CITE1_AUTHORS = [["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]]
RELAX_CITE1_DOI = "10.1007/s10858-007-9214-2"
RELAX_CITE1_PUBMED_ID = "18085410"
RELAX_CITE1_FULL_CITATION = "d'Auvergne, E. J. and Gooley, P. R. (2008).  Optimisation of NMR dynamic models I.  Minimisation algorithms and their performance within the model-free and Brownian rotational diffusion spaces.  J. Biomol. NMR, 40(2), 107-119."
RELAX_CITE1_TITLE = "Optimisation of NMR dynamic models I.  Minimisation algorithms and their performance within the model-free and Brownian rotational diffusion spaces."
RELAX_CITE1_STATUS = "published"
RELAX_CITE1_TYPE = "journal"
RELAX_CITE1_JOURNAL_ABBREV = "J. Biomol. NMR"
RELAX_CITE1_JOURNAL_FULL = "Journal of Biomolecular NMR"
RELAX_CITE1_VOLUME = 40
RELAX_CITE1_ISSUE = 2
RELAX_CITE1_PAGE_FIRST = 107
RELAX_CITE1_PAGE_LAST = 119
RELAX_CITE1_YEAR = 2008
RELAX_CITE2_AUTHORS = [["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]]
RELAX_CITE2_DOI = "10.1007/s10858-007-9213-3"
RELAX_CITE2_PUBMED_ID = "18085411"
RELAX_CITE2_FULL_CITATION = "d'Auvergne, E. J. and Gooley, P. R. (2008).  Optimisation of NMR dynamic models II.  A new methodology for the dual optimisation of the model-free parameters and the Brownian rotational diffusion tensor.  J. Biomol. NMR, 40(2), 121-133."
RELAX_CITE2_TITLE = "Optimisation of NMR dynamic models II.  A new methodology for the dual optimisation of the model-free parameters and the Brownian rotational diffusion tensor."
RELAX_CITE2_STATUS = "published"
RELAX_CITE2_TYPE = "journal"
RELAX_CITE2_JOURNAL_ABBREV = "J. Biomol. NMR"
RELAX_CITE2_JOURNAL_FULL = "Journal of Biomolecular NMR"
RELAX_CITE2_VOLUME = 40
RELAX_CITE2_ISSUE = 2
RELAX_CITE2_PAGE_FIRST = 121
RELAX_CITE2_PAGE_LAST = 133
RELAX_CITE2_YEAR = 2008


# NMRPipe fixed info.
NMRPIPE_NAME = "NMRPipe"
NMRPIPE_AUTHORS = "Delaglio, F., Grzesiek, S., Vuister, G. W., Zhu, G., Pfeifer, J., and Bax, A"
NMRPIPE_URL = "http://spin.niddk.nih.gov/NMRPipe/"
NMRPIPE_TASKS = ["processing"]
NMRPIPE_CITE_AUTHORS = [["Frank", "Delaglio", "F.", None], ["Stephan", "Grzesiek", "S.", None], ["Geerten", "Vuister", "G.", "W."], ["Guang", "Zhu", "G.", None], ["John", "Pfeifer", "J.", None], ["Ad", "Bax", "A.", None]]
NMRPIPE_CITE_DOI = "10.1007/BF00197809"
NMRPIPE_CITE_PUBMED_ID = "8520220"
NMRPIPE_CITE_FULL_CITATION = "Delaglio, F., Grzesiek, S., Vuister, G. W., Zhu, G., Pfeifer, J., and Bax, A. (1995).  NMRPipe: a multidimensional spectral processing system based on UNIX pipes.  J. Biomol. NMR. 6, 277-293."
NMRPIPE_CITE_TITLE = "NMRPipe: a multidimensional spectral processing system based on UNIX pipes." 
NMRPIPE_CITE_STATUS = "published"
NMRPIPE_CITE_TYPE = "journal"
NMRPIPE_CITE_JOURNAL_ABBREV = "J. Biomol. NMR"
NMRPIPE_CITE_JOURNAL_FULL = "Journal of Biomolecular NMR"
NMRPIPE_CITE_VOLUME = 6
NMRPIPE_CITE_PAGE_FIRST = 277
NMRPIPE_CITE_PAGE_LAST = 293
NMRPIPE_CITE_YEAR = 1995


# Sparky fixed info.
SPARKY_NAME = "Sparky"
SPARKY_AUTHORS = "Goddard, T. D. and Kneller, D. G."
SPARKY_REF = "Goddard, T. D. and Kneller, D. G., SPARKY 3, University of California, San Francisco."
SPARKY_URL = "http://www.cgl.ucsf.edu/home/sparky/"
SPARKY_TASKS = ["spectral analysis"]
SPARKY_CITE_AUTHORS = [["Tom", "Goddard", "T.", "D."], ["Donald", "Kneller", "D.", "G."]]
SPARKY_CITE_FULL_CITATION = "Goddard, T. D. and Kneller, D. G., SPARKY 3, University of California, San Francisco."
SPARKY_CITE_STATUS = "unpublished"
SPARKY_CITE_TYPE = "internet"




def bmrb_write_citations(star):
    """Generate the Citations saveframe records.

    @param star:        The NMR-STAR dictionary object.
    @type star:         NMR_STAR instance
    """

    # Loop over the citations.
    if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'citations'):
        for citations in cdp.exp_info.citations:
            star.citations.add(authors=citations.authors, doi=citations.doi, pubmed_id=citations.pubmed_id, full_citation=citations.full_citation, title=citations.title, status=citations.status, type=citations.type, journal_abbrev=citations.journal_abbrev, journal_full=citations.journal_full, volume=citations.volume, issue=citations.issue, page_first=citations.page_first, page_last=citations.page_last, year=citations.year)


def bmrb_write_software(star):
    """Generate the Software saveframe records.

    @param star:        The NMR-STAR dictionary object.
    @type star:         NMR_STAR instance
    @return:            A list BMRB software IDs and a list of software labels.
    @rtype:             tuple of list of int and list of str
    """

    # Loop over the software.
    software_ids = []
    software_labels = []
    if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'software'):
        for software in cdp.exp_info.software:
            # Get the citation ID numbers.
            cite_id_nums = []
            for cite in software.cite_ids:
                cite_id_nums.append(cdp.exp_info.get_cite_id_num(cite))

            # The program info.
            id = star.software.add(name=software.name, version=software.version, vendor_name=software.vendor_name, vendor_eaddress=software.url, task=software.tasks, cite_ids=cite_id_nums)

            # Append the software info.
            software_ids.append(id)
            software_labels.append(software.name)

    # relax cannot be the only program used!
    else:
        raise RelaxError("relax cannot be the only program used in the analysis - spectral analysis programs, etc. must also have been used.  Please use the relevant BMRB user functions to specify these.")

    # Return the software info.
    return software_ids, software_labels


def citation(cite_id=None, authors=None, doi=None, pubmed_id=None, full_citation=None, title=None, status=None, type=None, journal_abbrev=None, journal_full=None, volume=None, issue=None, page_first=None, page_last=None, year=None):
    """Store a citation.

    @keyword cite_id:           The citation ID string.
    @type cite_id:              str
    @keyword authors:           The list of authors.  Each author element is a list of four elements: the first name, last name, first initial, and middle initials.
    @type authors:              list of lists of str
    @keyword doi:               The DOI number, e.g. "10.1000/182".
    @type doi:                  None or str
    @keyword pubmed_id:         The identification code assigned to the publication by PubMed.
    @type pubmed_id:            None or int
    @keyword full_citation:     A full citation in a format similar to that used in a journal article by either cutting and pasting from another document or by typing. Please include author names, title, journal, page numbers, and year or equivalent information for the type of publication given.
    @type full_citation:        str
    @keyword title:             The title of the publication.
    @type title:                str
    @keyword status:            The publication status.  Can be one of in "preparation", "in press", "published", "retracted", or "submitted".
    @type status:               str
    @keyword type:              The publication type.  Can be one of "abstract", "BMRB only", "book", "book chapter", "internet", "journal", "personal communication", or "thesis".
    @type type:                 str
    @keyword journal_abbrev:    A standard journal abbreviation as defined by the Chemical Abstract Services for the journal where the data are or will be published.  If the data in the deposition are related to a J. Biomol. NMR paper, the value must be 'J. Biomol. NMR' to alert the BMRB annotators so that the deposition is properly processed.  If the depositor truly does not know the journal, a value of 'not known' or 'na' is acceptable.
    @type journal_abbrev:       str
    @keyword journal_full:      The full journal name.
    @type journal_full:         str
    @keyword volume:            The volume number.
    @type volume:               int
    @keyword issue:             The issue number.
    @type issue:                int
    @keyword page_first:        The first page number.
    @type page_first:           int
    @keyword page_last:         The last page number.
    @type page_last:            int
    @keyword year:              The publication year.
    @type year:                 int
    """

    # Set up the experimental info data container, if needed.
    if not hasattr(cdp, 'exp_info'):
        cdp.exp_info = ExpInfo()

    # Place the data in the container.
    cdp.exp_info.add_citation(cite_id=cite_id, authors=authors, doi=doi, pubmed_id=pubmed_id, full_citation=full_citation, title=title, status=status, type=type, journal_abbrev=journal_abbrev, journal_full=journal_full, volume=volume, issue=issue, page_first=page_first, page_last=page_last, year=year)


def software(name=None, version=None, url=None, vendor_name=None, cite_ids=None, tasks=None):
    """Select by name the software used in the analysis.

    @param name:            The name of the software program.
    @type name:             str
    @keyword version:       The program version.
    @type version:          None or str
    @keyword url:           The program's URL.
    @type url:              None or str
    @keyword vendor_name:   The name of the company or person behind the program.
    @type vendor_name:      str
    @keyword cite_ids:      The citation ID numbers.
    @type cite:_ids         None or str
    @keyword tasks:         The tasks performed by the program.
    @type tasks:            list of str
    """

    # Set up the experimental info data container, if needed.
    if not hasattr(cdp, 'exp_info'):
        cdp.exp_info = ExpInfo()

    # Place the data in the container.
    cdp.exp_info.software_setup(name=name, version=version, url=url, vendor_name=vendor_name, cite_ids=cite_ids, tasks=tasks)


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
        # Add the citations.
        cdp.exp_info.add_citation(cite_id='relax_ref1', authors=RELAX_CITE1_AUTHORS, doi=RELAX_CITE1_DOI, pubmed_id=RELAX_CITE1_PUBMED_ID, full_citation=RELAX_CITE1_FULL_CITATION, title=RELAX_CITE1_TITLE, status=RELAX_CITE1_STATUS, type=RELAX_CITE1_TYPE, journal_abbrev=RELAX_CITE1_JOURNAL_ABBREV, journal_full=RELAX_CITE1_JOURNAL_FULL, volume=RELAX_CITE1_VOLUME, issue=RELAX_CITE1_ISSUE, page_first=RELAX_CITE1_PAGE_FIRST, page_last=RELAX_CITE1_PAGE_LAST, year=RELAX_CITE1_YEAR)
        cdp.exp_info.add_citation(cite_id='relax_ref2', authors=RELAX_CITE2_AUTHORS, doi=RELAX_CITE2_DOI, pubmed_id=RELAX_CITE2_PUBMED_ID, full_citation=RELAX_CITE2_FULL_CITATION, title=RELAX_CITE2_TITLE, status=RELAX_CITE2_STATUS, type=RELAX_CITE2_TYPE, journal_abbrev=RELAX_CITE2_JOURNAL_ABBREV, journal_full=RELAX_CITE2_JOURNAL_FULL, volume=RELAX_CITE2_VOLUME, issue=RELAX_CITE2_ISSUE, page_first=RELAX_CITE2_PAGE_FIRST, page_last=RELAX_CITE2_PAGE_LAST, year=RELAX_CITE2_YEAR)

        # Add the software info.
        cdp.exp_info.software_setup(name=RELAX_NAME, version=version_full(), vendor_name=RELAX_AUTHORS, url=RELAX_URL, cite_ids=['relax_ref1', 'relax_ref2'], tasks=RELAX_TASKS)

    # NMRPipe.
    if name == 'NMRPipe':
        # Add the citations.
        cdp.exp_info.add_citation(cite_id='nmrpipe_ref', authors=NMRPIPE_CITE_AUTHORS, doi=NMRPIPE_CITE_DOI, pubmed_id=NMRPIPE_CITE_PUBMED_ID, full_citation=NMRPIPE_CITE_FULL_CITATION, title=NMRPIPE_CITE_TITLE, status=NMRPIPE_CITE_STATUS, type=NMRPIPE_CITE_TYPE, journal_abbrev=NMRPIPE_CITE_JOURNAL_ABBREV, journal_full=NMRPIPE_CITE_JOURNAL_FULL, volume=NMRPIPE_CITE_VOLUME, page_first=NMRPIPE_CITE_PAGE_FIRST, page_last=NMRPIPE_CITE_PAGE_LAST, year=NMRPIPE_CITE_YEAR)

        # Add the software info.
        cdp.exp_info.software_setup(name=NMRPIPE_NAME, version=version, vendor_name=NMRPIPE_AUTHORS, url=NMRPIPE_URL, cite_ids=['nmrpipe_ref'], tasks=NMRPIPE_TASKS)

    # Sparky.
    elif name == 'Sparky':
        # Check if the version information has been supplied.
        if not version:
            raise RelaxError("The Sparky version number has not been supplied.")

        # Add the citations.
        cite_index = cdp.exp_info.add_citation(cite_id='sparky_ref', authors=SPARKY_CITE_AUTHORS, full_citation=SPARKY_CITE_FULL_CITATION, status=SPARKY_CITE_STATUS, type=SPARKY_CITE_TYPE)

        # Add the software info.
        cdp.exp_info.software_setup(name=SPARKY_NAME, version=version, vendor_name=SPARKY_AUTHORS, url=SPARKY_URL, cite_ids=['sparky_ref'], tasks=SPARKY_TASKS)
