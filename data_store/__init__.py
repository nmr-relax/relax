###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Package containing the relax data storage object."""


# Python module imports.
from re import search
from sys import stderr
from time import asctime
import xml.dom.minidom

# relax module imports.
from compat import builtins
from data_store.gui import Gui
from data_store.pipe_container import PipeContainer
from data_store.relax_xml import fill_object_contents, xml_to_object
import pipe_control
from lib.errors import RelaxError, RelaxPipeError, RelaxNoPipeError
from status import Status; status = Status()
import version


__all__ = [ 'align_tensor',
            'data_classes',
            'diff_tensor',
            'exp_info',
            'gui',
            'interatomic',
            'mol_res_spin',
            'pipe_container',
            'prototype',
            'relax_xml'
]


class Relax_data_store(dict):
    """The relax data storage object."""

    # The current data pipe.
    current_pipe = None
    builtins.cdp = None

    # Class variable for storing the class instance.
    instance = None

    def __new__(self, *args, **kargs):
        """Replacement function for implementing the singleton design pattern."""

        # First initialisation.
        if self.instance is None:
            # Create a new instance.
            self.instance = dict.__new__(self, *args, **kargs)

            # Add some initial structures.
            self.instance.pipe_bundles = {}
            self.instance.relax_gui = Gui()

        # Already initialised, so return the instance.
        return self.instance


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro text.
        text = "The relax data storage object.\n"

        # The data pipes.
        text = text + "\n"
        text = text + "Data pipes:\n"
        pipes = list(self.instance.keys())
        if pipes:
            for pipe in pipes:
                text = text + "  %s\n" % repr(pipe)
        else:
            text = text + "  None\n"

        # Data store objects.
        text = text + "\n"
        text = text + "Data store objects:\n"
        names = sorted(self.__class__.__dict__.keys())
        for name in names:
            # The object.
            obj = getattr(self, name)

            # The text.
            if obj == None or isinstance(obj, str):
                text = text + "  %s %s: %s\n" % (name, type(obj), obj)
            else:
                text = text + "  %s %s: %s\n" % (name, type(obj), obj.__doc__.split('\n')[0])

        # dict methods.
        text = text + "\n"
        text = text + "Inherited dictionary methods:\n"
        for name in dir(dict):
            # Skip special methods.
            if search("^_", name):
                continue

            # Skip overwritten methods.
            if name in list(self.__class__.__dict__.keys()):
                continue

            # The object.
            obj = getattr(self, name)

            # The text.
            text = text + "  %s %s: %s\n" % (name, type(obj), obj.__doc__.split('\n')[0])

        # All other objects.
        text = text + "\n"
        text = text + "All other objects:\n"
        for name in dir(self):
            # Skip special methods.
            if search("^_", name):
                continue

            # Skip overwritten methods.
            if name in list(self.__class__.__dict__.keys()):
                continue

            # Skip dictionary methods.
            if name in dir(dict):
                continue

            # The object.
            obj = getattr(self, name)

            # The text.
            text = text + "  %s %s: %s\n" % (name, type(obj), obj)

        # Return the text.
        return text


    def __reset__(self):
        """Delete all the data from the relax data storage object.

        This method is to make the current single instance of the Data object identical to a newly
        created instance of Data, hence resetting the relax program state.
        """

        # Loop over the keys of self.__dict__ and delete the corresponding object.
        for key in list(self.__dict__.keys()):
            # Delete the object.
            del self.__dict__[key]

        # Remove all items from the dictionary.
        self.instance.clear()

        # Reset the current data pipe.
        builtins.cdp = None

        # Recreate the pipe bundle object.
        self.instance.pipe_bundles = {}

        # Re-add the GUI object.
        self.instance.relax_gui = Gui()

        # Signal the change.
        status.observers.reset.notify()
        status.observers.pipe_alteration.notify()


    def _back_compat_hook(self, file_version=None, pipes=None):
        """Method for converting the old data structures to the new ones.

        @keyword file_version:  The relax XML version of the XML file.
        @type file_version:     int
        @keyword pipes:         The list of new pipe names to update.
        @type pipes:            list of str
        """

        # Loop over the new data pipes.
        for pipe_name in pipes:
            # The data pipe object.
            dp = self[pipe_name]

            # Convert the molecule-residue-spin data.
            for mol in dp.mol:
                # Loop over the residues.
                for res in mol.res:
                    # Loop over the spins.
                    for spin in res.spin:
                        # The current spin ID.
                        spin_id = pipe_control.mol_res_spin.generate_spin_id_unique(pipe_cont=dp, mol=mol, res=res, spin=spin)

                        # Convert proton spins (the 'heteronuc_type' variable indicates a pre-interatomic container design state).
                        if hasattr(spin, 'heteronuc_type') and hasattr(spin, 'element') and spin.element == 'H':
                            # Rename the nuclear isotope.
                            spin.isotope = spin.proton_type

                        # Convert heteronuclear spins (the 'heteronuc_type' variable indicates a pre-interatomic container design state).
                        elif hasattr(spin, 'heteronuc_type'):
                            # Rename the nuclear isotope.
                            spin.isotope = spin.heteronuc_type

                            # Name the spin if needed.
                            if spin.name == None:
                                if search('N', spin.isotope):
                                    pipe_control.mol_res_spin.name_spin(spin_id=spin_id, name='N', pipe=pipe_name)
                                elif search('C', spin.isotope):
                                    pipe_control.mol_res_spin.name_spin(spin_id=spin_id, name='C', pipe=pipe_name)

                            # An attached proton - convert into a spin container.
                            if (hasattr(spin, 'attached_proton') and spin.attached_proton != None) or (hasattr(spin, 'proton_type') and spin.proton_type != None):
                                # The proton name.
                                if hasattr(spin, 'attached_proton') and spin.attached_proton != None:
                                    proton_name = spin.attached_proton
                                else:
                                    proton_name = 'H'

                                # The two spin IDs (newly regenerated due to the above renaming).
                                spin_id1 = pipe_control.mol_res_spin.generate_spin_id_unique(pipe_cont=dp, mol=mol, res=res, spin=spin)
                                spin_id2 = pipe_control.mol_res_spin.generate_spin_id_unique(pipe_cont=dp, mol=mol, res=res, spin_name=proton_name)

                                # Fetch the proton spin if it exists.
                                h_spin = pipe_control.mol_res_spin.return_spin(spin_id2, pipe=pipe_name)
                                if h_spin:
                                    spin_id2 = pipe_control.mol_res_spin.generate_spin_id_unique(pipe_cont=dp, mol=mol, res=res, spin_name=proton_name, spin_num=h_spin.num)

                                # Create a new spin container for the proton if needed.
                                if not h_spin:
                                    h_spin = pipe_control.mol_res_spin.create_spin(mol_name=mol.name, res_num=res.num, res_name=res.name, spin_name=proton_name, pipe=pipe_name)
                                    h_spin.select = False

                                # Set up a dipole interaction between the two spins if needed.
                                if not hasattr(h_spin, 'element'):
                                    pipe_control.mol_res_spin.set_spin_element(spin_id=spin_id2, element='H', pipe=pipe_name)
                                if not hasattr(h_spin, 'isotope'):
                                    pipe_control.mol_res_spin.set_spin_isotope(spin_id=spin_id2, isotope='1H', pipe=pipe_name)
                                pipe_control.interatomic.define(spin_id1, spin_id2, verbose=False, pipe=pipe_name)

                                # Get the interatomic data container.
                                interatom = pipe_control.interatomic.return_interatom(spin_id1=spin_id1, spin_id2=spin_id2, pipe=pipe_name)

                                # Set the interatomic distance.
                                if hasattr(spin, 'r'):
                                    interatom.r = spin.r

                                # Set the interatomic unit vectors.
                                if hasattr(spin, 'xh_vect'):
                                    interatom.vector = spin.xh_vect

                                # Set the RDC values.
                                if hasattr(spin, 'rdc'):
                                    interatom.rdc = spin.rdc
                                if hasattr(spin, 'rdc_err'):
                                    interatom.rdc_err = spin.rdc_err
                                if hasattr(spin, 'rdc_sim'):
                                    interatom.rdc_sim = spin.rdc_sim
                                if hasattr(spin, 'rdc_bc'):
                                    interatom.rdc_bc = spin.rdc_bc

                        # Delete the old structures.
                        eliminate = ['heteronuc_type', 'proton_type', 'attached_proton', 'r', 'r_err', 'r_sim', 'rdc', 'rdc_err', 'rdc_sim', 'rdc_bc', 'xh_vect']
                        for name in eliminate:
                            if hasattr(spin, name):
                                delattr(spin, name)

            # Convert the alignment tensors.
            if hasattr(dp, 'align_tensors'):
                for i in range(len(dp.align_tensors)):
                    # Fix for the addition of the alignment ID structure as opposed to the tensor name or tag.
                    if not hasattr(dp.align_tensors[i], 'align_id'):
                        dp.align_tensors[i].set('align_id', dp.align_tensors[i].name)

            # Convert spectrometer frequency information.
            if hasattr(dp, 'frq'):
                # Convert to the new structure.
                dp.spectrometer_frq = dp.frq
                del dp.frq

                # Build the new frequency list structure.
                dp.spectrometer_frq_list = []
                for frq in dp.spectrometer_frq.values():
                    if frq not in dp.spectrometer_frq_list:
                        dp.spectrometer_frq_list.append(frq)

                # And finally count the elements.
                dp.spectrometer_frq_count = len(dp.spectrometer_frq_list)


    def add(self, pipe_name, pipe_type, bundle=None, switch=True):
        """Method for adding a new data pipe container to the dictionary.

        This method should be used rather than importing the PipeContainer class and using the statement 'D[pipe] = PipeContainer()', where D is the relax data storage object and pipe is the name of the data pipe.

        @param pipe_name:   The name of the new data pipe.
        @type pipe_name:    str
        @param pipe_type:   The data pipe type.
        @type pipe_type:    str
        @keyword bundle:    The optional data pipe bundle to associate the data pipe with.
        @type bundle:       str or None
        @keyword switch:    A flag which if True will cause the new data pipe to be set to the current data pipe.
        @type switch:       bool
        """

        # Test if the pipe already exists.
        if pipe_name in list(self.instance.keys()):
            raise RelaxPipeError(pipe_name)

        # Create a new container.
        self[pipe_name] = PipeContainer()

        # Add the data pipe type string to the container.
        self[pipe_name].pipe_type = pipe_type

        # The pipe bundle.
        if bundle:
            # A new bundle.
            if bundle not in list(self.pipe_bundles.keys()):
                self.pipe_bundles[bundle] = []

            # Add the pipe to the bundle.
            self.pipe_bundles[bundle].append(pipe_name)

        # Change the current data pipe.
        if switch:
            # Set the current data pipe.
            self.instance.current_pipe = pipe_name
            builtins.cdp = self[pipe_name]

            # Signal the switch.
            status.observers.pipe_alteration.notify()


    def is_empty(self, verbosity=False):
        """Method for testing if the relax data store is empty.

        @keyword verbosity: A flag which if True will cause messages to be printed to STDERR.
        @type verbosity:    bool
        @return:            True if the data store is empty, False otherwise.
        @rtype:             bool
        """

        # No pipes should exist.
        if not list(self.keys()) == []:
            if verbosity:
                stderr.write("The relax data store contains the data pipes %s.\n" % list(self.keys()))
            return False

        # Objects which should be in here.
        blacklist = [
                'pipe_bundles',
                'relax_gui'
        ]

        # An object has been added to the data store.
        for name in dir(self):
            # Skip the data store methods.
            if name in list(self.__class__.__dict__.keys()):
                continue

            # Skip the dict methods.
            if name in list(dict.__dict__.keys()):
                continue

            # Skip special objects.
            if search("^__", name):
                continue

            # Blacklisted objects to skip.
            if name in blacklist:
                continue

            # An object has been added.
            if verbosity:
                stderr.write("The relax data store contains the object %s.\n" % name)
            return False

        # The data store is empty.
        return True


    def from_xml(self, file, dir=None, pipe_to=None, verbosity=1):
        """Parse a XML document representation of a data pipe, and load it into the relax data store.

        @param file:                The open file object.
        @type file:                 file
        @keyword dir:               The name of the directory containing the results file (needed
                                    for loading external files).
        @type dir:                  str
        @keyword pipe_to:           The data pipe to load the XML data pipe into (the file must only
                                    contain one data pipe).
        @type pipe_to:              str
        @keyword verbosity:         A flag specifying the amount of information to print.  The
                                    higher the value, the greater the verbosity.
        @type verbosity:            int
        @raises RelaxError:         If pipe_to is given and the file contains multiple pipe
                                    elements;  or if the data pipes in the XML file already exist in
                                    the relax data store;  or if the data pipe type is invalid;  or
                                    if the target data pipe is not empty.
        @raises RelaxNoPipeError:   If pipe_to is given but the data pipe does not exist.
        @raises RelaxError:         If the data pipes in the XML file already exist in the relax
                                    data store, or if the data pipe type is invalid.
        @raises RelaxPipeError:     If the data pipes of the XML file are already present in the
                                    relax data store.
        """

        # Create the XML document from the file.
        doc = xml.dom.minidom.parse(file)

        # Get the relax node.
        relax_node = doc.childNodes[0]

        # Get the relax version of the XML file.
        file_version = relax_node.getAttribute('file_version')
        if file_version == '':
            file_version = 1
        else:
            file_version = int(file_version)

        # Get the GUI nodes.
        gui_nodes = relax_node.getElementsByTagName('relax_gui')
        if gui_nodes:
            self.relax_gui.from_xml(gui_nodes[0], file_version=file_version)

        # Recreate all the data store data structures.
        xml_to_object(relax_node, self, file_version=file_version, blacklist=['pipe', 'relax_gui'])

        # Get the pipe nodes.
        pipe_nodes = relax_node.getElementsByTagName('pipe')

        # Structure for the names of the new pipes.
        pipes = []

        # Target loading to a specific pipe (for pipe results reading).
        if pipe_to:
            # Check if there are multiple pipes in the XML file.
            if len(pipe_nodes) > 1:
                raise RelaxError("The pipe_to target pipe argument '%s' cannot be given as the file contains multiple pipe elements." % pipe_to)

            # The pipe type.
            pipe_type = pipe_nodes[0].getAttribute('type')

            # Check that the pipe already exists.
            if not pipe_to in self:
                raise RelaxNoPipeError(pipe_to)

            # Check if the pipe type matches.
            if pipe_type != self[pipe_to].pipe_type:
                raise RelaxError("The XML file pipe type '%s' does not match the pipe type '%s'" % (pipe_type, self[pipe_to].pipe_type))

            # Check if the pipe is empty.
            if not self[pipe_to].is_empty():
                raise RelaxError("The data pipe '%s' is not empty." % pipe_to)

            # Load the data.
            self[pipe_to].from_xml(pipe_nodes[0], dir=dir, file_version=file_version)

            # Store the pipe name.
            pipes.append(pipe_to)

        # Load the state.
        else:
            # Checks.
            for pipe_node in pipe_nodes:
                # The pipe name and type.
                pipe_name = str(pipe_node.getAttribute('name'))
                pipe_type = pipe_node.getAttribute('type')

                # Existence check.
                if pipe_name in self:
                    raise RelaxPipeError(pipe_name)

                # Valid type check.
                if not pipe_type in pipe_control.pipes.VALID_TYPES:
                    raise RelaxError("The data pipe type '%s' is invalid and must be one of the strings in the list %s." % (pipe_type, pipe_control.pipes.VALID_TYPES))

            # Load the data pipes.
            for pipe_node in pipe_nodes:
                # The pipe name and type.
                pipe_name = str(pipe_node.getAttribute('name'))
                pipe_type = pipe_node.getAttribute('type')

                # Add the data pipe.
                switch = False
                if self.current_pipe == None:
                    switch = True
                self.add(pipe_name, pipe_type, switch=switch)

                # Fill the pipe.
                self[pipe_name].from_xml(pipe_node, file_version=file_version, dir=dir)

                # Store the pipe name.
                pipes.append(pipe_name)

            # Set the current pipe.
            if self.current_pipe in list(self.keys()):
                builtins.cdp = self[self.current_pipe]

        # Finally update the molecule, residue, and spin metadata for each data pipe.
        for pipe in pipes:
            pipe_control.mol_res_spin.metadata_update(pipe=pipe)

        # Backwards compatibility transformations.
        self._back_compat_hook(file_version, pipes=pipes)


    def to_xml(self, file, pipes=None):
        """Create a XML document representation of the current data pipe.

        This method creates the top level XML document including all the information needed
        about relax, calls the PipeContainer.xml_write() method to fill in the document contents,
        and writes the XML into the file object.

        @param file:        The open file object.
        @type file:         file
        @param pipes:       The name of the pipe, or list of pipes to place in the XML file.
        @type pipes:        str or list of str
        """

        # The pipes to include in the XML file.
        all = False
        if not pipes:
            all = True
            pipes = list(self.keys())
        elif isinstance(pipes, str):
            pipes = [pipes]

        # Sort the pipes.
        pipes.sort()

        # Create the XML document object.
        xmldoc = xml.dom.minidom.Document()

        # Create the top level element, including the relax URL.
        top_element = xmldoc.createElementNS('http://www.nmr-relax.com', 'relax')
        top_element.setAttribute("xmlns", "http://www.nmr-relax.com")

        # Append the element.
        xmldoc.appendChild(top_element)

        # Set the relax version number, and add a creation time.
        top_element.setAttribute('version', version.version)
        top_element.setAttribute('time', asctime())
        top_element.setAttribute('file_version', "2")
        rev = version.revision()
        if rev:
            top_element.setAttribute('revision', rev)
        url = version.url()
        if url:
            top_element.setAttribute('url', url)

        # Add all objects in the data store base object to the XML element.
        if all:
            blacklist = list(list(self.__class__.__dict__.keys()) + list(dict.__dict__.keys()))
            for name in dir(self):
                # Skip blacklisted objects.
                if name in blacklist:
                    continue

                # Skip special objects.
                if search('^_', name):
                    continue

                # Execute any to_xml() methods, and add that object to the blacklist.
                obj = getattr(self, name)
                if hasattr(obj, 'to_xml'):
                    obj.to_xml(xmldoc, top_element)
                    blacklist = blacklist + [name]

            # Remove the current data pipe from the blacklist!
            blacklist.remove('current_pipe')

            # Add all simple python objects within the store.
            fill_object_contents(xmldoc, top_element, object=self, blacklist=blacklist)

        # Loop over the pipes.
        for pipe in pipes:
            # Create the pipe XML element and add it to the top level XML element.
            pipe_element = xmldoc.createElement('pipe')
            top_element.appendChild(pipe_element)

            # Set the data pipe attributes.
            pipe_element.setAttribute('desc', 'The contents of a relax data pipe')
            pipe_element.setAttribute('name', pipe)
            pipe_element.setAttribute('type', self[pipe].pipe_type)

            # Fill the data pipe XML element.
            self[pipe].to_xml(xmldoc, pipe_element)

        # Write out the XML file.
        file.write(xmldoc.toprettyxml(indent='    '))
