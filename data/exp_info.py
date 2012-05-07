###############################################################################
#                                                                             #
# Copyright (C) 2009-2012 Edward d'Auvergne                                   #
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
"""Module holding the experimental information data container."""

# relax module imports.
from data_classes import RelaxListType, Element
from relax_errors import RelaxError


class ExpInfo(Element):
    """The experimental information data container."""

    def __init__(self):
        """Initialise the data container."""

        # The name of the container.
        self.name = "exp_info"

        # The description of the container.
        self.desc = "Experimental information"

        # Blacklisted objects.
        self.blacklist = ["citations", "software", "temp_calibration", "temp_control"]


    def add_citation(self, cite_id=None, authors=None, doi=None, pubmed_id=None, full_citation=None, title=None, status=None, type=None, journal_abbrev=None, journal_full=None, volume=None, issue=None, page_first=None, page_last=None, year=None):
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

        # Initialise the list container if needed.
        if not hasattr(self, "citations"):
            # The list.
            self.citations = RelaxListType()

            # The name of the container.
            self.citations.container_name = "citation_list"

            # The description of the container.
            self.citations.container_desc = "List of citations"

        # Init the container.
        cite = Element()

        # The name of the container.
        cite.name = "citation"

        # The description of the container.
        cite.desc = "Literature citation"

        # Set the attributes.
        cite.cite_id = cite_id
        cite.authors = authors
        cite.doi = doi
        cite.pubmed_id = pubmed_id
        cite.full_citation = full_citation
        cite.title = title
        cite.status = status
        cite.type = type
        cite.journal_abbrev = journal_abbrev
        cite.journal_full = journal_full
        cite.volume = volume
        cite.issue = issue
        cite.page_first = page_first
        cite.page_last = page_last
        cite.year = year

        # Append the container.
        self.citations.append(cite)


    def get_cite_id_num(self, cite_id):
        """Return the citation ID number for the given citation ID string.

        @param cite_id: The citation ID string.
        @type cite_id:  str
        @return:        The citation ID number.
        @rtype:         int
        """

        # Loop over the citations.
        for i in range(len(self.citations)):
            # Match.
            if self.citations[i].cite_id == cite_id:
                return i + 1


    def setup_peak_intensity_type(self, ri_id, type):
        """Store the peak intensity type.

        @param ri_id:       The relaxation data ID string.
        @type ri_id:        str
        @param type:        The peak intensity type, one of 'height' or 'volume'.
        @type type:         str
        """

        # Initialise the container if needed.
        if not hasattr(self, "peak_intensity_type"):
            self.peak_intensity_type = {}

        # Find if the type has already been set.
        if ri_id in self.peak_intensity_type.keys():
            raise RelaxError("The peak intensity type for the '%s' relaxation data ID string has already been set.")

        # Set the type.
        self.peak_intensity_type[ri_id] = type


    def setup_thiol(self, state):
        """Set up the thiol state of the system.

        @param state:   The thiol state of the molecule.
        @type state:    str
        """

        # Check.
        if hasattr(self, "thiol_state"):
            raise RelaxError("The thiol state has already been specified")

        # Set the attribute.
        self.thiol_state = state


    def setup_script(self, file=None, dir=None, cite_ids=None, text=None, analysis_type=None, model_selection=None, engine=None, model_elim=False, universal_solution=False):
        """Specify the scripts used in the analysis.

        @keyword file:                  The name of the script file.
        @type file:                     str
        @keyword dir:                   The directory containing the file (defaults to the current directory if None).
        @type dir:                      None or str
        @keyword cite_ids:              The citation ID numbers.
        @type cite_ids:                 None or str
        @param text:                    The script text.
        @type text:                     str
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

        # Initialise the container if needed.
        if not hasattr(self, "scripts"):
            # The list.
            self.scripts = RelaxListType()

            # The name of the container.
            self.scripts.container_name = "script_list"

            # The description of the container.
            self.scripts.container_desc = "List of scripts used for the analysis"

        # Init the container.
        script = Element()

        # The name of the container.
        script.name = "script"

        # The description of the container.
        script.desc = "Script used for the analysis"

        # Set the attributes.
        script.file = file
        script.dir = dir
        script.cite_ids = cite_ids
        script.text = text
        script.analysis_type = analysis_type
        script.model_selection = model_selection
        script.engine = engine
        script.model_elim = model_elim
        script.universal_solution = universal_solution

        # Append the container.
        self.scripts.append(script)


    def software_setup(self, name, version=None, url=None, vendor_name=None, cite_ids=None, tasks=None):
        """Set up the software information.

        @param name:            The name of the software program.
        @type name:             str
        @keyword version:       The program version.
        @type version:          None or str
        @keyword url:           The program's URL.
        @type url:              None or str
        @keyword vendor_name:   The name of the company or person behind the program.
        @type vendor_name:      str
        @keyword cite_ids:      The citation ID numbers.
        @type cite_ids:         None or str
        @keyword tasks:         The tasks performed by the program.
        @type tasks:            list of str
        """

        # Initialise the container if needed.
        if not hasattr(self, "software"):
            # The list.
            self.software = RelaxListType()

            # The name of the container.
            self.software.container_name = "software_list"

            # The description of the container.
            self.software.container_desc = "List of software programs used in the analysis"

        # Init the container.
        software = Element()

        # The name of the container.
        software.name = "software"

        # The description of the container.
        software.desc = "Software program used in the analysis"

        # Set the attributes.
        software.name = name
        software.url = url
        software.version = version
        software.vendor_name = vendor_name
        software.cite_ids = cite_ids
        software.tasks = tasks

        # Append the container.
        self.software.append(software)


    def temp_calibration_setup(self, ri_id, method):
        """Store the temperature calibration method.

        @param ri_id:       The relaxation data ID string.
        @type ri_id:        str
        @param method:      The temperature calibration method.
        @type method:       str
        """

        # Initialise the container if needed.
        if not hasattr(self, "temp_calibration"):
            self.temp_calibration = {}

        # Find if the method has already been set.
        if ri_id in self.temp_calibration.keys():
            raise RelaxError("The temperature calibration method for the '%s' relaxation data ID string has already been set.")

        # Set the method.
        self.temp_calibration[ri_id] = method


    def temp_control_setup(self, ri_id, method):
        """Store the temperature control method.

        @param ri_id:       The relaxation data ID string.
        @type ri_id:        str
        @param method:      The temperature control method.
        @type method:       str
        """

        # Initialise the container if needed.
        if not hasattr(self, "temp_control"):
            self.temp_control = {}

        # Find if the method has already been set.
        if ri_id in self.temp_control.keys():
            raise RelaxError("The temperature control method for the '%s' relaxation data ID string has already been set.")

        # Set the method.
        self.temp_control[ri_id] = method
