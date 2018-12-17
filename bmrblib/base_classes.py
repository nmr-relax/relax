#############################################################################
#                                                                           #
# The BMRB library.                                                         #
#                                                                           #
# Copyright (C) 2009-2013 Edward d'Auvergne                                 #
#                                                                           #
# This program is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################

# Module docstring.
"""The BMRB library base classes.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.
"""

# Python module imports.
from numpy import float64, ndarray, zeros
from warnings import warn

# Bmrblib module imports.
from bmrblib.misc import no_missing, translate
from bmrblib.pystarlib.SaveFrame import SaveFrame
from bmrblib.pystarlib.TagTable import TagTable
from bmrblib.version import Star_version; version = Star_version()


class BaseSaveframe:
    """The base class for the saveframe classes."""

    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # The saveframe counter.
        self.count = 0

        # Add the specific tag category objects.
        self.tag_categories = CategoryList()
        self.add_tag_categories()


    def add(self, **keywords):
        """Add data to the saveframe.

        If the keywords are within the tag dictionary structure as the variable name, then the data will be checked, translated and stored in that variable.  If not, then a warning will be given.

        @return:    The saveframe count.
        @rtype:     int
        """

        # Reset all data structures.
        self.reset()

        # First set default values.
        for cat in self.tag_categories:
            # Loop over the keys.
            for key in cat._key_list:
                # No variable or no default value.
                if not cat[key].var_name or not cat[key].default:
                    continue

                # Set the default.
                setattr(self, cat[key].var_name, translate(cat[key].default))

        # Loop over the keywords.
        for name, val in keywords.items():
            # Get the tag object.
            info = self.tag_categories.get_tag(name)

            # No corresponding tag, so set as a class instance variable and move to the next keyword.
            if not info:
                setattr(self, name, val)
                continue

            # Unpack.
            cat_index, key, obj = info

            # Check that a value has been supplied.
            if not obj.missing:
                no_missing(val, name)

            # Check that the value is allowed.
            if obj.allowed != None:
                # List argument.
                if not (isinstance(val, list) and not isinstance(val, ndarray)):
                    val_list = [val]
                else:
                    val_list = val

                # Loop over the list.
                for i in range(len(val_list)):
                    if val_list[i] not in obj.allowed:
                        raise NameError("The %s keyword argument of '%s' must be one of %s." % (name, val_list[i], obj.allowed))

            # Length check of the non-free tag category elements (must be the same).
            if (isinstance(val, list) or isinstance(val, ndarray)):
                # Get the reference length.
                N = self.tag_categories[cat_index]._N()

                # No length yet.
                if N == None:
                    pass

                # Mismatch.
                if N != None and len(val) != N:
                    raise NameError("The number of elements in the %s keyword argument should be N = %s." % (name, N))

            # Store the argument.
            setattr(self, name, translate(val))

        # Saveframe counter updating.
        self.count = self.count + 1
        self.count_str = str(self.count)

        # The data ID values.
        for i in range(len(self.tag_categories)):
            ids = self.tag_categories[i].generate_data_ids()
            if ids:
                self.data_ids = translate(ids)

        # If needed, perform some saveframe specific operations.
        self.pre_ops()

        # Initialise the save frame.
        self.frame = SaveFrame(title=self.create_title())

        # Create the tag categories.
        for i in range(len(self.tag_categories)):
            self.tag_categories[i].create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)

        # Return the saveframe count.
        return self.count


    def create_title(self):
        """Create the saveframe title.

        @return:    The title.
        @rtype:     str
        """

        # Build and return the title.
        if hasattr(self, 'label'):
            return self.label + '_' + self.count_str
        else:
            return self.sf_label + '_' + self.count_str


    def extract_data(self, datanode):
        """Read all the tags from the datanodes.

        @keyword datanode:  The datanode.
        @type datanode:     Datanode instance
        @return:            The data.
        @rtype:             tuple
        """

        # Find the mapping between the tag categories of the NMR-STAR file and the bmrblib class.
        mapping = self.find_mapping(datanode)

        # Loop over the mapping.
        for i in range(len(mapping)):
            # The tag category is not present in the file.
            if mapping[i] == None:
                continue

            # Extract the data.
            self.tag_categories[mapping[i]].extract_tag_data(datanode.tagtables[i])

        # Add the framecode for v2.1 files.
        if version.major == 2:
            self.sf_framecode = datanode.title


    def find_mapping(self, datanode):
        """Determine the mapping between the tag categories of the NMR-STAR file and the bmrblib class.

        @keyword datanode:  The datanode.
        @type datanode:     Datanode instance
        @return:            The mapping structure.
        @rtype:             list
        """

        # Init.
        N = len(self.tag_categories)
        M = len(datanode.tagtables)
        counts = zeros((M, N), float64)
        mapping = []

        # Count the tag name matches.
        for table_ind in range(M):
            for cat_ind in range(N):
                # Alias.
                cat = self.tag_categories[cat_ind]
                table = datanode.tagtables[table_ind]

                # Loop over the tags.
                for key in cat.keys():
                    for name in table.tagnames:
                        # Check for a match.
                        if name == cat[key].tag_name_full():
                            counts[table_ind, cat_ind] += 1

            # The index of the maximum count.
            if not counts[table_ind].sum():
                index = None
            else:
                index = counts[table_ind].tolist().index(counts[table_ind].max())
            mapping.append(index)

        # Return the mapping.
        return mapping


    def loop(self):
        """Loop over the saveframes, yielding the data.

        @return:    The saveframe data.
        @rtype:     tuple
        """

        # Set up the tag information.
        for i in range(len(self.tag_categories)):
            self.tag_categories[i].tag_setup()

        # Get the saveframe name.
        sf_name = getattr(self, 'sf_label')

        # Loop over all datanodes.
        for datanode in self.datanodes:
            # Find the saveframes via the SfCategory tag index.
            found = False
            for index in range(len(datanode.tagtables[0].tagnames)):
                # First match the tag names.
                if datanode.tagtables[0].tagnames[index] == self.tag_categories[0]['SfCategory'].tag_name_full():
                    # Then the tag value.
                    if datanode.tagtables[0].tagvalues[index][0] == sf_name:
                        found = True
                        break

            # Skip the datanode.
            if not found:
                continue

            # Extract the information.
            self.extract_data(datanode)

            # Return the saveframe info.
            yield self.read()


    def pre_ops(self):
        """A dummy method for performing no saveframe specific operations prior to XML creation."""


    def read(self):
        """Read all the data from the saveframe.

        @return:    A dictionary of all the data.
        @rtype:     dict
        """

        # Init.
        data = {}

        # Loop over the tag categories.
        for cat in self.tag_categories:
            # Loop over the keys.
            for key in cat._key_list:
                # No variable.
                if not cat[key].var_name:
                    continue

                # No object.
                if not hasattr(self, cat[key].var_name):
                    obj = None

                # Get the object.
                else:
                    obj = getattr(self, cat[key].var_name)

                # Package the translated data.
                data[cat[key].var_name] = translate(obj, format=cat[key].format, reverse=True)

        # Return the data.
        return data


    def reset(self):
        """Reset all data structures to None."""

        # Loop over the tag categories.
        for cat in self.tag_categories:
            # Loop over the keys.
            for key in cat._key_list:
                # No variable.
                if not cat[key].var_name or not hasattr(self, cat[key].var_name):
                    continue

                # Skip special variables.
                if cat[key].var_name in ['sf_label', 'count', 'count_str']:
                    continue

                # Set to None.
                setattr(self, cat[key].var_name, translate(None))


class MissingSaveframe:
    """Special class for when BMRB saveframes are non-existent in certain NMR-STAR versions."""

    def __init__(self, name):
        """Initialise the special class.

        @param name:    The name of the missing Saveframe.
        @type name:     str
        """

        # Store the arg.
        self.name = name


    def add(self, *args, **keywords):
        """Special function for giving a warning."""

        # The warning.
        warn(Warning("The %s saveframe does not exist in this NMR-STAR version." % self.name))


    def loop(self):
        """Special function for giving a warning."""

        # The warning.
        warn(Warning("The %s saveframe does not exist in this NMR-STAR version." % self.name))

        # Yield nothing.
        yield None




class CategoryList(list):
    """A special lits object for holding the different saveframe tag categories."""

    def get_tag(self, var_name):
        """Return the tag object possessing the given variable name.

        @param var_name:    The variable name.
        @type var_name:     str
        @return:            The key and tag objects.
        @rtype:             str, TagObject instance
        """

        # Loop over the categories.
        for i in range(len(self)):
            # Loop over the keys.
            for key, obj in self[i].items():
                if var_name == obj.var_name:
                    return i, key, obj



class TagTranslationTable(dict):
    """A special dictionary object for creating the tag translation tables."""

    def __init__(self):
        """Set up the table."""

        # Initialise the baseclass.
        super(TagTranslationTable, self).__init__()

        # The length of the list variables.
        self.N = None

        # The key ordering.
        self._key_list = []


    def add(self, key, var_name=None, tag_name=None, allowed=None, default=None, format='str', missing=True):
        """Add an entry to the translation table.

        @keyword key:       The dictionary key.  This is also the BMRB NMR-STAR database table name.
        @type key:          str
        @keyword var_name:  The saveframe variable name corresponding to the key.
        @type var_name:     None or str
        @keyword tag_name:  The BMRB NMR-STAR tag name corresponding to the key.
        @type tag_name:     None or str
        @keyword allowed:   A list of allowable values for the data.
        @type allowed:      None or list
        @keyword default:   The default value.
        @type default:      anything
        @keyword format:    The original python format of the data.
        @type format:       str
        @keyword missing:   A flag which if True will allow the data to be set to None.
        @type missing:      bool
        """

        # The key already exists.
        if key in self._key_list:
            # Overwrite the variables.
            self[key].allowed = allowed
            self[key].missing = missing
            self[key].tag_name = tag_name
            self[key].var_name = var_name
            self[key].default = default
            self[key].format = format

            # Change the key ordering.
            self._key_list.remove(key)
            self._key_list.append(key)

        # Otherwise add a new object.
        else:
            # Add the tag object.
            self[key] = TagObject(self, var_name=var_name, tag_name=tag_name, allowed=allowed, default=default, format=format, missing=missing)

            # Add the key to the ordered list.
            self._key_list.append(key)



class TagObject(object):
    """An object for filling the translation table."""

    def __init__(self, category, var_name=None, tag_name=None, allowed=None, default=None, format='str', missing=True):
        """Setup the internal variables.

        This stores the variable name, BMRB NMR-STAR tag name, a list of allowable values, the missing flag, and any other tag specific information corresponding to the key.

        @param category:    The parent tag category class object.
        @type category:     TagTranslationTable instance
        @keyword var_name:  The saveframe variable name corresponding to the key.
        @type var_name:     None or str
        @keyword tag_name:  The BMRB NMR-STAR tag name corresponding to the key.
        @type tag_name:     None or str
        @keyword allowed:   A list of allowable values for the data.
        @type allowed:      None or list
        @keyword default:   The default value.
        @type default:      anything
        @keyword format:    The original python format of the data.
        @type format:       str
        @keyword missing:   A flag which if True will allow the data to be set to None.
        @type missing:      bool
        """

        # Store the tag category object.
        self.category = category

        # The default values.
        self.allowed = allowed
        self.missing = missing
        self.tag_name = tag_name
        self.var_name = var_name
        self.default = default
        self.format = format


    def tag_name_full(self):
        """Add the prefix to the tag name and return the full tag name.

        @return:    The full tag name with prefix.
        @rtype:     str
        """

        # Return the name.
        if not self.tag_name:
            return None
        else:
            return self.category.tag_prefix + self.tag_name



class TagCategory(TagTranslationTable):
    """The base class for tag category classes."""

    # The category name.
    tag_category_label = None

    # The base category is not free.
    free = False

    def __init__(self, sf):
        """Initialise the tag category object, placing the saveframe into its namespace.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(TagCategory, self).__init__()

        # Place the saveframe and tag info into the namespace.
        self.sf = sf

        # The tag category name.
        self.tag_category_label = None


    def _N(self):
        """Determine the length of the variables.

        @return:    The length.
        @rtype:     int
        """

        # Loop over the objects until a variable is found in self.
        N = None
        for key in self.keys():
            # The variable exists.
            if self[key].var_name and hasattr(self.sf, self[key].var_name):
                # Get the object.
                obj = getattr(self.sf, self[key].var_name)

                # Is it a list?
                if not isinstance(obj, list) and not isinstance(obj, ndarray):
                    continue

                # The length.
                N = len(obj)
                break

        # Set the length in this class.
        if N:
            self.N = N

        # Return N.
        return N


    def create(self):
        """Create the tag category."""

        # Init.
        self.tag_setup()
        tag_names = []
        tag_values = []

        # Empty tag category.
        if self.is_empty():
            return

        # Loop over the keys of the class dictionary.
        for key in self._key_list:
            # The tag names and values (skipping entries with no corresponding tag name or variable).
            if self[key].tag_name != None and self[key].var_name != None:
                # The name (adding the tag prefix).
                tag_names.append(self[key].tag_name_full())

                # The value.
                if hasattr(self.sf, self[key].var_name):
                    val = getattr(self.sf, self[key].var_name)
                else:
                    val = translate(None)

                # Convert to a list, if necessary.
                if not isinstance(val, list):
                    val = [val]

                # Append the value list.
                tag_values.append(val)

        # No data, so don't add the table.
        if not len(tag_names):
            return

        # Check the input data to avoid cryptic pystarlib error messages.
        N = len(tag_values[0])
        for i in range(len(tag_values)):
            if len(tag_values[i]) > N:
                # Mismatch.
                if N != 1:
                    raise NameError("The tag values are not all the same length '%s'." % tag_values)

                # First element was single.
                N = len(tag_values[i])

        # Fix the single values if the other data are lists.
        for i in range(len(tag_values)):
            if len(tag_values[i]) == 1:
                tag_values[i] = tag_values[i] * N

        # Create the tagtable.
        table = TagTable(free=self.free, tagnames=tag_names, tagvalues=tag_values)

        # Add the tagtable to the save frame.
        self.sf.frame.tagtables.append(table)


    def extract_tag_data(self, tagtable):
        """Extract all of the tag data from the tagtable, placing it into the designated variable names.

        @param tagtable:    The tagtable.
        @type tagtable:     Tagtable instance
        """

        # Loop over the variables.
        for key in self._key_list:
            # No corresponding tag in the tagtable.
            if self[key].tag_name_full() not in tagtable.tagnames:
                continue

            # Currently no corresponding variable in the tag category.
            if self[key].var_name == None:
                continue

            # Find the index of the tag.
            index = tagtable.tagnames.index(self[key].tag_name_full())

            # The data.
            data = tagtable.tagvalues[index]

            # Free tagtable data (collapse the list).
            if self.free:
                data = data[0]

            # Set the data.
            setattr(self.sf, self[key].var_name, data)


    def generate_data_ids(self):
        """Generate the data ID structure.

        @keyword N: The number of data points.
        @type N:    int
        """

        # The length.
        N = self._N()

        # If not 
        if not N:
            return

        # The data ID values.
        return list(range(1, N+1))


    def is_empty(self):
        """Dummy method for check if the tag category is empty.

        @return:    The state of emptiness (False).
        @rtype:     bool
        """

        # Not empty.
        return False


    def tag_setup(self, tag_category_label=None, sep=None):
        """Setup the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Place the args into the class namespace.
        if tag_category_label:
            self.tag_category_label = tag_category_label
        if sep:
            self.sep = sep
        else:
            self.sep = '.'

        # Create the full tag label.
        self.tag_prefix = '_'
        if self.tag_category_label:
            self.tag_prefix = self.tag_prefix + self.tag_category_label + self.sep



class TagCategoryFree(TagCategory):
    """The free version of the TagCategory class."""

    # The base category is free.
    free = True

    def __init__(self, sf):
        """Setup the TagCategoryFree tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(TagCategoryFree, self).__init__(sf)

        # Add some generic saveframe category tag.
        self.add(key='SfCategory',  var_name='sf_label',        tag_name='Saveframe_category')
        self.add(key='SfFramecode', var_name='sf_framecode',    tag_name=None)
