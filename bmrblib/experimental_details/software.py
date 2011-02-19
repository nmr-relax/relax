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
"""The software saveframe category.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html_frame/frame_SaveFramePage.html#software
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory
from bmrblib.pystarlib.SaveFrame import SaveFrame
from bmrblib.pystarlib.TagTable import TagTable
from bmrblib.misc import translate


class SoftwareSaveframe(BaseSaveframe):
    """The software saveframe class."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # The number of software programs used.
        self.software_num = 0

        # Add the specific tag category objects.
        self.add_tag_categories()


    def add(self, name, version=None, vendor_name=None, vendor_address=None, vendor_eaddress=None, task=None, cite_ids=None):
        """Add the software info to the data nodes.

        @param name:                The name of the software program.
        @type name:                 str
        @keyword version:           The software version.
        @type version:              None or str
        @keyword vendor_name:       The vendor or developers of the software.
        @type vendor_name:          None or str
        @keyword vendor_address:    The vendor address.
        @type vendor_address:       None or str
        @keyword vendor_eaddress:   The vendor electronic address.
        @type vendor_eaddress:      None or str
        @keyword task:              The task of the software.
        @type task:                 str
        @keyword cite_ids:          The citation ID numbers.
        @type cite_ids:             None or list of int
        @return:                    The software ID number.
        @rtype:                     int
        """

        # Check.
        if not isinstance(task, list):
            raise NameError, "The task argument '%s' is invalid." % task

        # Place the args into the namespace.
        self.program_name = name
        self.program_version = version
        self.vendor_name = translate(vendor_name)
        self.vendor_address = translate(vendor_address)
        self.vendor_eaddress = translate(vendor_eaddress)
        self.task = translate(task)
        self.cite_ids = translate(cite_ids)

        # Increment the ID number.
        self.software_num = self.software_num + 1
        self.software_id_num = [str(translate(self.software_num))]

        # The category name.
        self.cat_name = ['Software']

        # Initialise the save frame.
        self.frame = SaveFrame(title=self.program_name)

        # Create the tag categories.
        self.Software.create()
        self.Software_citation.create()
        self.Vendor.create()
        self.Task.create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)

        # Return the software ID number.
        return self.software_num


    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.Software = Software(self)
        self.Software_citation = SoftwareCitation(self)
        self.Task = Task(self)
        self.Vendor = Vendor(self)



class Software(TagCategory):
    """Base class for the Software tag category."""

    def create(self):
        """Create the Software tag category."""

        # The save frame category.
        self.sf.frame.tagtables.append(self.create_tag_table([['SfCategory', 'cat_name']], free=True))

        # Software ID number.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SoftwareID']], tagvalues=[[str(self.sf.software_num)]]))

        # The program name.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['Name']], tagvalues=[[self.sf.program_name]]))

        # The program version.
        if self.sf.program_version:
            self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['Version']], tagvalues=[[self.sf.program_version]]))


    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label='Software', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['SfCategory'] = 'Sf_category'
        self.tag_names['SoftwareID'] = 'ID'
        self.tag_names['Name'] = 'Name'
        self.tag_names['Version'] = 'Version'


class SoftwareCitation(TagCategory):
    """Base class for the SoftwareCitation tag category."""


    def create(self):
        """Create the Software tag category."""

        # Keys and objects.
        info = [
            ['CitationID',      'cite_ids'],
            ['SoftwareID',      'software_id_num']
        ]

        # Get the TabTable.
        table = self.create_tag_table(info)

        # Add the tagtable to the save frame.
        self.sf.frame.tagtables.append(table)


    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Category label.
        if not tag_category_label:
            tag_category_label='Software_citation'

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label=tag_category_label, sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['CitationID'] = 'Citation_ID'
        self.tag_names['SoftwareID'] = 'Software_ID'


class Task(TagCategory):
    """Base class for the Task tag category."""

    def create(self):
        """Create the Task tag category."""

        # Keys and objects.
        info = [
            ['Task',                'task'],
            ['SoftwareID',          'software_id_num']
        ]

        # Get the TabTable.
        table = self.create_tag_table(info)

        # Add the tagtable to the save frame.
        self.sf.frame.tagtables.append(table)


    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label='Task', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['Task'] = 'Task'
        self.tag_names['SoftwareID'] = 'SoftwareID'


class Vendor(TagCategory):
    """Base class for the Vendor tag category."""

    def create(self):
        """Create the Vendor tag category."""

        # Keys and objects.
        info = [
            ['Name',                'vendor_name'],
            ['Address',             'vendor_address'],
            ['ElectronicAddress',   'vendor_eaddress'],
            ['SoftwareID',          'software_id_num']
        ]

        # Get the TabTable.
        table = self.create_tag_table(info)

        # Add the tagtable to the save frame.
        self.sf.frame.tagtables.append(table)


    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label='Vendor', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['Name'] = 'Name'
        self.tag_names['Address'] = 'Address'
        self.tag_names['ElectronicAddress'] = 'ElectronicAddress'
        self.tag_names['SoftwareID'] = 'SoftwareID'
