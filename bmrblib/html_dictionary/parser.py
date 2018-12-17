# Python module imports.
try:
    from html.parser import HTMLParser    # Python 3 import.
except ImportError:
    from HTMLParser import HTMLParser    # Python 2 import.
from os import sep
from string import ascii_uppercase


class Create:
    def __init__(self):
        """Parse and create."""

        # The base directory.
        self.base_dir = '3.1html'

        # The data structure.
        self.supergroups = Super_groups()

        # The supergroups.
        self._read_supergroups()

        # print out.
        self._print_out()

        # The saveframe categories.
        self._read_saveframe_categories()


    def _print_out(self):
        for key in self.supergroups.ordered_keys:
            sg = self.supergroups[key]
            print "\n\nSuper group: %s" % key
            #print dir(sg)
            print "dir name: %s" % sg.dir_name

            for key2 in sg.sf_cats.ordered_keys:
                module = "%s%s%s.py" % (sg.dir_name, sep, sg.sf_cats[key2].name)
                print "\tSaveframe category: %s (%s)" % (module, key2)


    def _read_saveframe_categories(self):
        """Read and convert the HTML saveframe categories into Python objects."""

        # Open the saveframe categories page.
        file = open("%s%sSaveFramePage.html" % (self.base_dir, sep))
        lines = file.readlines()
        file.close()

        # Parse the HTML.
        parser = Sf_parser(self.supergroups)
        for line in lines:
            parser.feed(line)


    def _read_supergroups(self):
        """Read and convert the HTML supergroups into Python objects."""

        # Open the super group page.
        file = open("%s%sSuperGroupPage.html" % (self.base_dir, sep))
        lines = file.readlines()
        file.close()

        # Parse the HTML.
        parser = Super_parser(self.supergroups)
        for line in lines:
            parser.feed(line)



class Sf_cat:
    """Saveframe category container class."""

    def __init__(self):
        """Initialise the container."""



class Sf_cats(dict):
    """Dictionary object for all the saveframe categories."""

    def __init__(self):
        """Initialise the container."""

        # The ordered list of keys.
        self.ordered_keys = []


class Sf_parser(HTMLParser):
    def __init__(self, supergroups):
        """Initialise the saveframe category HTML parser."""

        # Store the supergroup structure.
        self.supergroups = supergroups

        # Execute the base class method.
        HTMLParser.__init__(self)

        # Status.
        self.status = None
        self.status_list = False


    def _process_supergroup(self, data):
        """Handle the supergroup title data."""

        # Process the name.
        self.supergroup_name = data.strip()


    def _process_tag_cats(self, data):
        """Handle the saveframe category title data."""

        # The name.
        name = data.split('(')[1][:-1]

        # Add the container.
        self.supergroups[self.supergroup_name].sf_cats.ordered_keys.append(name)
        self.supergroups[self.supergroup_name].sf_cats[name] = Sf_cat()

        # The name.
        var_name = data.split()[0]
        self.supergroups[self.supergroup_name].sf_cats[name].name = var_name


    def _process_title(self, data):
        """Handle the saveframe category data."""

        # Process the name.
        self.sf_cat_name = data.split(':')[1].strip()


    def handle_starttag(self, tag, attrs):
        """Replacement method for handling the start of a HTML tag."""

        print tag, attrs
        # The saveframe categories.
        if tag == 'h3':
            print tag, attrs
            self.status = 'sf_cat'

        # The lists.
        elif tag == 'ul':
            self.status_list = True

        # The saveframe categories.
        elif tag == 'a':
            # Inside the list.
            if self.status_list:
                print tag, attrs
                self.status = 'tag_cats'

            # Outside of the list.
            else:
                self.status = 'supergroup'

        # Nothing interesting.
        else:
            self.status = None


    def handle_endtag(self, tag):
        """Replacement method for handling the end of a HTML tag."""

        # Reset the status.
        self.status = None

        # End of the list.
        if tag == 'ul':
            self.status_list = False


    def handle_data(self, data):
        """Handling of the HTML data."""

        # Strip the data.
        data = data.strip()

        # No data.
        if not data:
            return

        # The saveframe categories.
        if self.status == 'sf_cat':
            self._process_title(data)

        # The super group.
        elif self.status == 'supergroup':
            self._process_supergroup(data)

        # The tag categories.
        elif self.status == 'tag_cats':
            self._process_tag_cats(data)


class Super_group:
    """Super group container class."""

    def __init__(self):
        """Initialise the container."""

        # Add the saveframe category structures.
        self.sf_cats = Sf_cats()



class Super_groups(dict):
    """Dictionary object for all the super groups."""

    def __init__(self):
        """Initialise the container."""

        # The ordered list of keys.
        self.ordered_keys = []



class Super_parser(HTMLParser):
    def __init__(self, supergroups):
        """Initialise the super group HTML parser."""

        # Store the supergroup structure.
        self.supergroups = supergroups

        # Execute the base class method.
        HTMLParser.__init__(self)

        # Status.
        self.status = None
        self.status_list = False


    def _process_sf_cat(self, data):
        """Handle the saveframe category title data."""

        # Strip the data.
        data = data.strip()

        # No data.
        if not data:
            return

        # The name.
        name = data.split('(')[1][:-1]

        # Add the container.
        self.supergroups[self.supergroup_name].sf_cats.ordered_keys.append(name)
        self.supergroups[self.supergroup_name].sf_cats[name] = Sf_cat()

        # The name.
        var_name = data.split()[0]
        self.supergroups[self.supergroup_name].sf_cats[name].name = var_name


    def _process_title(self, data):
        """Handle the supergroup title data."""

        # Process the name.
        self.supergroup_name = data.split(':')[1].strip()

        # Add a supergroup container.
        self.supergroups.ordered_keys.append(self.supergroup_name)
        self.supergroups[self.supergroup_name] = Super_group()

        # The directory name.
        dir_name = self.supergroup_name
        if not self.supergroup_name[2] in ascii_uppercase:
            dir_name = dir_name.lower()
        dir_name = dir_name.replace(' ', '_')
        self.supergroups[self.supergroup_name].dir_name = dir_name


    def handle_starttag(self, tag, attrs):
        """Replacement method for handling the start of a HTML tag."""

        # The supergroups.
        if tag == 'h3':
            self.status = 'group'

        # The lists.
        elif tag == 'ul':
            self.status_list = True

        # The saveframe categories.
        elif tag == 'a':
            if self.status_list:
                self.status = 'sf_cat'

        # Nothing interesting.
        else:
            self.status = None


    def handle_endtag(self, tag):
        """Replacement method for handling the end of a HTML tag."""

        # Reset the status.
        self.status = None

        # End of the list.
        if tag == 'ul':
            self.status_list = False


    def handle_data(self, data):
        """Handling of the HTML data."""

        # The supergroups.
        if self.status == 'group':
            self._process_title(data)

        if self.status == 'sf_cat':
            self._process_sf_cat(data)



if __name__ == "__main__":
    Create()
