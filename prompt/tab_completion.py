import __builtin__
from re import match, split


class Tab_completion:
    def __init__(self, name_space={}, print_flag=0):
        """Function for tab completion."""

        self.name_space = name_space
        self.print_flag = print_flag


    def class_attributes(self, temp_class):
        list = dir(temp_class)
        if hasattr(temp_class, '__bases__'):
            for base in temp_class.__bases__:
                list = list + self.class_attributes(base)
        return list


    def create_list(self):
        """Function to create the dictionary of options for tab completion."""

        self.list = self.name_space.keys()

        self.options = []
        for name in self.list:
            if match(self.input, name) and name != "__builtins__":
                self.options.append(name)


    def create_sublist(self):
        """Function to create the dictionary of options for tab completion."""

        # Split the input.
        list = split('\.', self.input)
        if len(list) == 0:
            return

        # Construct the module and get the corresponding object.
        module = list[0]
        for i in range(1, len(list)-1):
            module = module + '.' + list[i]
        object = eval(module, self.name_space)

        # Get the object attributes.
        self.list = dir(object)

        # If the object is a class, get all the class attributes as well.
        if hasattr(object, '__class__'):
            self.list.append('__class__')
            self.list = self.list + self.class_attributes(object.__class__)

        # Possible completions.
        self.options = []
        for name in self.list:
            if match(list[-1], name) and name != "__builtins__":
                self.options.append(module + '.' + name)

        if self.print_flag:
            print "List: " + `list`
            print "Module: " + `module`
            print "self.list: " + `self.list`
            print "self.options: " + `self.options`


    def finish(self, input, state):
        """Return the next possible completion for 'input'"""

        self.input = input
        self.state = state

        # Create a list of all possible options.
        # Find a list of options by matching the input with self.list
        if self.print_flag:
            print "\nInput: " + `self.input`
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
