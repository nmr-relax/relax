###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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
from data_classes import ContainerList, Element


class ExpInfo(Element):
    """The experimental information data container."""

    def __init__(self):
        """Initialise the data container."""

        # The name of the container.
        self.element_name = "exp_info"

        # The description of the container.
        self.element_desc = "Experimental information"

        # Blacklisted objects.
        self.blacklist = ["citations", "software"]


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
            self.citations = ContainerList()

            # The name of the container.
            self.citations.container_name = "citation_list"

            # The description of the container.
            self.citations.container_desc = "List of citations"

        # Init the container.
        cite = Element()

        # The name of the container.
        cite.element_name = "citation"

        # The description of the container.
        cite.element_desc = "Literature citation"

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
            self.software = ContainerList()

            # The name of the container.
            self.software.container_name = "software_list"

            # The description of the container.
            self.software.container_desc = "List of software programs used in the analysis"

        # Init the container.
        software = Element()

        # The name of the container.
        software.element_name = "software"

        # The description of the container.
        software.element_desc = "Software program used in the analysis"

        # Set the attributes.
        software.name = name
        software.url = url
        software.version = version
        software.vendor_name = vendor_name
        software.cite_ids = cite_ids
        software.tasks = tasks

        # Append the container.
        self.software.append(software)
