import __builtin__
from re import match


class tab_completion:
    def __init__(self, name_space={}, print_flag=0):
        """Function for tab completion.

        Some of this code is stolen from the python rlcompleter code.
        """

        self.name_space = name_space
        self.print_flag = print_flag


    def finish(self, input, state):
        """Return the next possible completion for 'text'"""

        if self.print_flag:
            "\n"
        self.input = input
        self.state = state

        # Create a list of all possible options.
        # Find a list of options by matching the input with self.list
        if not "." in self.input:
            if self.print_flag:
                print "Creating list."
            self.create_list()
            if self.print_flag:
                print "\tOk."
        else:
            if self.print_flag:
                print "Creating sublist."
            self.create_sublist()
            if self.print_flag:
                print "\tOk."


        # Return the options if self.options[state] exists, or return None otherwise.
        if self.print_flag:
            print "Returning options."
        if self.state < len(self.options):
            return self.options[self.state]
        else:
            return None


    def create_sublist(self):
        """Function to create the dictionary of options for tab completion."""

        string = match(r"(\w+(\.\w+)*)\.(\w*)", self.input)
        if not string:
            return
        module, text = string.group(1,3)
        object = eval(module, self.name_space)
        self.list = dir(object)
        if hasattr(object, '__class__'):
            self.list.append('__class__')
            self.list = self.list + self.get_class_members(object.__class__)

        self.options = []
        for name in self.list:
            if match(text, name) and name != "__builtins__":
                self.options.append(module + '.' + name)

        if self.print_flag:
            print "self.list: " + `self.list`
            print "self.options: " + `self.options`


    def create_list(self):
        """Function to create the dictionary of options for tab completion."""

        self.list = self.name_space.keys()

        self.options = []
        for name in self.list:
            if match(self.input, name) and name != "__builtins__":
                self.options.append(name)


    def get_class_members(self, temp_class):
        list = dir(temp_class)
        if hasattr(temp_class, '__bases__'):
            for base in temp_class.__bases__:
                list = list + self.get_class_members(base)
        return list
