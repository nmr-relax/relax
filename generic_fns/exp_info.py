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
from relax_io import open_read_file
from version import version_full


# Storage container.
class Cite_store:
    """Citation storage container."""

    def __init__(self):
        """Initialise all variables."""

        self.name = None
        self.authors = None
        self.url = None
        self.tasks = None
        self.cite_authors = None
        self.cite_doi = None
        self.cite_pubmed_id = None
        self.cite_full_citation = None
        self.cite_title = None
        self.cite_status = None
        self.cite_type = None
        self.cite_journal_abbrev = None
        self.cite_journal_full = None
        self.cite_volume = None
        self.cite_issue = None
        self.cite_page_first = None
        self.cite_page_last = None
        self.cite_year = None


# Citation data structure.
CITE = {}

# relax citations.
CITE['relax 1'] = Cite_store()
CITE['relax 1'].name = "relax"
CITE['relax 1'].authors = "The relax development team"
CITE['relax 1'].url = "http://nmr-relax.com"
CITE['relax 1'].tasks = ["data processing"]
CITE['relax 1'].cite_authors = [["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]]
CITE['relax 1'].cite_doi = "10.1007/s10858-007-9214-2"
CITE['relax 1'].cite_pubmed_id = "18085410"
CITE['relax 1'].cite_full_citation = "d'Auvergne, E. J. and Gooley, P. R. (2008).  Optimisation of NMR dynamic models I.  Minimisation algorithms and their performance within the model-free and Brownian rotational diffusion spaces.  J. Biomol. NMR, 40(2), 107-119."
CITE['relax 1'].cite_title = "Optimisation of NMR dynamic models I.  Minimisation algorithms and their performance within the model-free and Brownian rotational diffusion spaces."
CITE['relax 1'].cite_status = "published"
CITE['relax 1'].cite_type = "journal"
CITE['relax 1'].cite_journal_abbrev = "J. Biomol. NMR"
CITE['relax 1'].cite_journal_full = "Journal of Biomolecular NMR"
CITE['relax 1'].cite_volume = 40
CITE['relax 1'].cite_issue = 2
CITE['relax 1'].cite_page_first = 107
CITE['relax 1'].cite_page_last = 119
CITE['relax 1'].cite_year = 2008

CITE['relax 2'] = Cite_store()
CITE['relax 1'].name = "relax"
CITE['relax 1'].authors = "The relax development team"
CITE['relax 1'].url = "http://nmr-relax.com"
CITE['relax 1'].tasks = ["data processing"]
CITE['relax 2'].cite_authors = [["Edward", "d'Auvergne", "E.", "J."], ["Paul", "Gooley", "P.", "R."]]
CITE['relax 2'].cite_doi = "10.1007/s10858-007-9213-3"
CITE['relax 2'].cite_pubmed_id = "18085411"
CITE['relax 2'].cite_full_citation = "d'Auvergne, E. J. and Gooley, P. R. (2008).  Optimisation of NMR dynamic models II.  A new methodology for the dual optimisation of the model-free parameters and the Brownian rotational diffusion tensor.  J. Biomol. NMR, 40(2), 121-133."
CITE['relax 2'].cite_title = "Optimisation of NMR dynamic models II.  A new methodology for the dual optimisation of the model-free parameters and the Brownian rotational diffusion tensor."
CITE['relax 2'].cite_status = "published"
CITE['relax 2'].cite_type = "journal"
CITE['relax 2'].cite_journal_abbrev = "J. Biomol. NMR"
CITE['relax 2'].cite_journal_full = "Journal of Biomolecular NMR"
CITE['relax 2'].cite_volume = 40
CITE['relax 2'].cite_issue = 2
CITE['relax 2'].cite_page_first = 121
CITE['relax 2'].cite_page_last = 133
CITE['relax 2'].cite_year = 2008

# NMRPipe citation.
CITE['NMRPipe'] = Cite_store()
CITE['NMRPipe'].name = "NMRPipe"
CITE['NMRPipe'].authors = "Delaglio, F., Grzesiek, S., Vuister, G. W., Zhu, G., Pfeifer, J., and Bax, A"
CITE['NMRPipe'].url = "http://spin.niddk.nih.gov/NMRPipe/"
CITE['NMRPipe'].tasks = ["processing"]
CITE['NMRPipe'].cite_authors = [["Frank", "Delaglio", "F.", None], ["Stephan", "Grzesiek", "S.", None], ["Geerten", "Vuister", "G.", "W."], ["Guang", "Zhu", "G.", None], ["John", "Pfeifer", "J.", None], ["Ad", "Bax", "A.", None]]
CITE['NMRPipe'].cite_doi = "10.1007/BF00197809"
CITE['NMRPipe'].cite_pubmed_id = "8520220"
CITE['NMRPipe'].cite_full_citation = "Delaglio, F., Grzesiek, S., Vuister, G. W., Zhu, G., Pfeifer, J., and Bax, A. (1995).  NMRPipe: a multidimensional spectral processing system based on UNIX pipes.  J. Biomol. NMR. 6, 277-293."
CITE['NMRPipe'].cite_title = "NMRPipe: a multidimensional spectral processing system based on UNIX pipes." 
CITE['NMRPipe'].cite_status = "published"
CITE['NMRPipe'].cite_type = "journal"
CITE['NMRPipe'].cite_journal_abbrev = "J. Biomol. NMR"
CITE['NMRPipe'].cite_journal_full = "Journal of Biomolecular NMR"
CITE['NMRPipe'].cite_volume = 6
CITE['NMRPipe'].cite_page_first = 277
CITE['NMRPipe'].cite_page_last = 293
CITE['NMRPipe'].cite_year = 1995

# Sparky citation.
CITE['Sparky'] = Cite_store()
CITE['Sparky'].name = "Sparky"
CITE['Sparky'].authors = "Goddard, T. D. and Kneller, D. G."
CITE['Sparky'].ref = "Goddard, T. D. and Kneller, D. G., SPARKY 3, University of California, San Francisco."
CITE['Sparky'].url = "http://www.cgl.ucsf.edu/home/sparky/"
CITE['Sparky'].tasks = ["spectral analysis"]
CITE['Sparky'].cite_authors = [["Tom", "Goddard", "T.", "D."], ["Donald", "Kneller", "D.", "G."]]
CITE['Sparky'].cite_full_citation = "Goddard, T. D. and Kneller, D. G., SPARKY 3, University of California, San Francisco."
CITE['Sparky'].cite_title = "Sparky."
CITE['Sparky'].cite_status = "unpublished"
CITE['Sparky'].cite_type = "internet"




def bmrb_write_citations(star):
    """Generate the Citations saveframe records.

    @param star:        The NMR-STAR dictionary object.
    @type star:         NMR_STAR instance
    """

    # Loop over the citations.
    if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'citations'):
        for citations in cdp.exp_info.citations:
            star.citations.add(citation_label=citations.cite_id, authors=citations.authors, doi=citations.doi, pubmed_id=citations.pubmed_id, full_citation=citations.full_citation, title=citations.title, status=citations.status, type=citations.type, journal_abbrev=citations.journal_abbrev, journal_full=citations.journal_full, volume=citations.volume, issue=citations.issue, page_first=citations.page_first, page_last=citations.page_last, year=citations.year)


def bmrb_write_methods(star):
    """Generate the Software saveframe records.

    @param star:        The NMR-STAR dictionary object.
    @type star:         NMR_STAR instance
    @return:            A list BMRB software IDs and a list of software labels.
    @rtype:             tuple of list of int and list of str
    """

    # The scripts.
    if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'scripts'):
        for script in cdp.exp_info.scripts:
            # Get the citation ID numbers.
            cite_id_nums = []
            if script.cite_ids:
                for cite in script.cite_ids:
                    cite_id_nums.append(cdp.exp_info.get_cite_id_num(cite))

            # The method info.
            star.method.add(name=script.file, details=None, cite_ids=cite_id_nums, file_name=script.file, file_text=script.text)


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


def script(file=None, dir=None, analysis_type=None, model_selection=None, engine=None, model_elim=False, universal_solution=False):
    """Specify the scripts used in the analysis.

    @param file:                    The name of the file to open.
    @type file:                     str
    @param dir:                     The directory containing the file (defaults to the current directory if None).
    @type dir:                      None or str
    @keyword analysis_type:         The type of analysis performed.
    @type analysis_type:            str
    @keyword model_selection:       The model selection technique used, if relevant.
    @type model_selection:          None or str
    @keyword engine:                The software engine used in the analysis.
    @type engine:                   str
    @keyword model_elim:            A model-free specific flag specifying if model elimination was performed.
    @type model_elim:               bool
    @keyword universal_solution:    A model-free specific flag specifying if the universal solution was sought after.
    @type universal_solution:       bool
    """

    # Check.
    allowed = ['frame order',
               'jw',
               'mf',
               'N-state',
               'noe',
               'relax_fit',
               'srls'
    ]
    if analysis_type not in allowed:
        raise RelaxError("The analysis type '%s' should be one of %s." % (analysis_type, allowed))

    # Set up the experimental info data container, if needed.
    if not hasattr(cdp, 'exp_info'):
        cdp.exp_info = ExpInfo()

    # Extract the text.
    f = open_read_file(file, dir)
    text = f.read()
    f.close()

    # Place the data in the container.
    cdp.exp_info.setup_script(file=file, text=text, analysis_type=analysis_type, model_selection=model_selection, engine=engine, model_elim=model_elim, universal_solution=universal_solution)


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

    # Init.
    cite_ids = []
    keys = []
    versions = []

    # relax.
    if name == 'relax':
        # The info.
        cite_ids.append(['relax_ref1', 'relax_ref2'])
        keys.append(['Relax 1', 'Relax 2'])
        versions.append(version_full())

    # NMRPipe.
    if name == 'NMRPipe':
        # The info.
        cite_ids.append(['nmrpipe_ref'])
        keys.append(['NMRPipe'])
        versions.append(version)

    # Sparky.
    elif name == 'Sparky':
        # Check if the version information has been supplied.
        if not version:
            raise RelaxError("The Sparky version number has not been supplied.")

        # The info.
        cite_ids.append(['sparky_ref'])
        keys.append(['Sparky'])
        versions.append(version)

    # Loop over the citations.
    for i in range(len(cite_ids)):
        for j in range(len(cite_ids[i])):
            # Add the citations.
            cdp.exp_info.add_citation(cite_id=cite_ids[i][j], authors=CITE[keys[i][j]].cite_authors, doi=CITE[keys[i][j]].cite_doi, pubmed_id=CITE[keys[i][j]].cite_pubmed_id, full_citation=CITE[keys[i][j]].cite_full_citation, title=CITE[keys[i][j]].cite_title, status=CITE[keys[i][j]].cite_status, type=CITE[keys[i][j]].cite_type, journal_abbrev=CITE[keys[i][j]].cite_journal_abbrev, journal_full=CITE[keys[i][j]].cite_journal_full, volume=CITE[keys[i][j]].cite_volume, page_first=CITE[keys[i][j]].cite_page_first, page_last=CITE[keys[i][j]].cite_page_last, year=CITE[keys[i][j]].cite_year)

        # Add the software info.
        cdp.exp_info.software_setup(name=CITE[keys[i][0]].name, version=versions[i], vendor_name=CITE[keys[i][0]].authors, url=CITE[keys[i][0]].url, cite_ids=cite_ids, tasks=CITE[keys[i][0]].tasks)


def thiol_state(state=None):
    """Set the thiol state of the system.

    @keyword state:         The thiol state of the molecule.
    @type state:            str
    """

    # Set up the experimental info data container, if needed.
    if not hasattr(cdp, 'exp_info'):
        cdp.exp_info = ExpInfo()

    # Place the data in the container.
    cdp.exp_info.setup_thiol(state=state)
