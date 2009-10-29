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
"""The method saveframe category.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html_frame/frame_SaveFramePage.html#method
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory
from bmrblib.pystarlib.SaveFrame import SaveFrame
from bmrblib.pystarlib.TagTable import TagTable
from bmrblib.misc import no_missing, translate


class MethodSaveframe(BaseSaveframe):
    """The method saveframe class."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # The number of methods used.
        self.method_num = 0

        # Add the specific tag category objects.
        self.add_tag_categories()


    def add(self, name=None, details=None, cite_ids=None, file_name=None, file_text=None, param_file_name=None, param_file_text=None):
        """Add the method info to the data nodes.

        @keyword name:              The unique name describing this method.
        @type name:                 str
        @keyword details:           Text description providing additional information about the reported method.
        @type details:              None or str
        @keyword cite_ids:          The citation ID numbers.
        @type cite_ids:             None or list of int
        @keyword file_name:         The name of the file containing the source code or protocol for the reported method.
        @type file_name:            str
        @keyword file_text:         The method provided as an ASCII text document that is included in the NMR-STAR file.
        @type file_text:            str
        @keyword param_file_name:   The name of the file that contains parameters required to execute the method.
        @type param_file_name:      None or str
        @keyword param_file_text:   The text of the parameter file.
        @type param_file_text:      None or str
        """

        # Check that nothing is missing.
        no_missing(name, 'method name')
        no_missing(file_name, 'file name')
        no_missing(file_text, 'file text')

        # Check.
        if not isinstance(cite_ids, list):
            raise NameError, "The cite_ids argument '%s' should be a list." % cite_ids

        # Place the args into the namespace.
        self.method_name = name
        self.details = translate(details)
        self.cite_ids = translate(cite_ids)
        self.file_name = translate(file_name)
        self.file_text = translate(file_text)
        self.param_file_name = translate(param_file_name)
        self.param_file_text = translate(param_file_text)

        # The text format.
        self.text_format = '?'

        # Increment the ID number.
        self.method_num = self.method_num + 1
        self.method_id_num = [str(translate(self.method_num))]

        # The category name.
        self.cat_name = ['Method']

        # Initialise the save frame.
        self.frame = SaveFrame(title='method')

        # Create the tag categories.
        self.Method.create()
        self.Method_citation.create()
        self.Method_file.create()
        self.Method_parameter_file.create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)


    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.Method = Method(self)
        self.Method_citation = MethodCitation(self)
        self.Method_file = MethodFile(self)
        self.Method_parameter_file = MethodParam(self)



class Method(TagCategory):
    """Base class for the Method tag category."""

    def create(self):
        """Create the Method tag category."""

        # The tags.
        self.sf.frame.tagtables.append(self.create_tag_table([['SfCategory', 'cat_name']], free=True))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SfFramecode']], tagvalues=[[str(self.sf.method_name)]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['MethodID']], tagvalues=[[str(self.sf.method_num)]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['Details']], tagvalues=[[self.sf.details]]))


    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label='Method', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['SfCategory'] = 'Sf_category'
        self.tag_names['SfFramecode'] = 'Sf_framecode'
        self.tag_names['MethodID'] = 'ID'
        self.tag_names['Details'] = 'Details'


class MethodCitation(TagCategory):
    """Base class for the MethodCitation tag category."""


    def create(self):
        """Create the Method tag category."""

        # Skip this tag category if no citations are present.
        if not self.sf.cite_ids:
            return

        # Keys and objects.
        info = [
            ['CitationID',      'cite_ids'],
            ['MethodID',        'method_id_num']
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
            tag_category_label='Method_citation'

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label=tag_category_label, sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['CitationID'] = 'Citation_ID'
        self.tag_names['MethodID'] = 'Method_ID'


class MethodFile(TagCategory):
    """Base class for the MethodFile tag category."""

    def create(self):
        """Create the MethodFile tag category."""

        # Keys and objects.
        info = [
            ['Name',                'file_name'],
            ['TextFormat',          'text_format'],
            ['Text',                'file_text'],
            ['MethodID',            'method_id_num']
        ]

        # Get the TabTable.
        table = self.create_tag_table(info, free=True)

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
        TagCategory.tag_setup(self, tag_category_label='Method_file', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['Name'] =        'Name'
        self.tag_names['TextFormat'] =  'Text_format'
        self.tag_names['Text'] =        'Text'
        self.tag_names['MethodID'] =    'Method_ID'


class MethodParam(TagCategory):
    """Base class for the MethodParam tag category."""

    def create(self):
        """Create the MethodParam tag category."""

        # Keys and objects.
        info = [
            ['FileName',            'param_file_name'],
            ['TextFormat',          'text_format'],
            ['Text',                'param_file_text'],
            ['MethodID',            'method_id_num']
        ]

        # Get the TabTable.
        table = self.create_tag_table(info, free=True)

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
        TagCategory.tag_setup(self, tag_category_label='Method_param', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['FileName'] =    'File_name'
        self.tag_names['TextFormat'] =  'Text_format'
        self.tag_names['Text'] =        'Text'
        self.tag_names['MethodID'] =    'Method_ID'
