###############################################################################
#                                                                             #
# Copyright (C) 2004-2006 Edward d'Auvergne                                   #
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

from re import search
from string import replace

from base_class import Common_functions
from maths_fns.jw_mapping import Mapping


class Jw_mapping(Common_functions):
    def __init__(self, relax):
        """Class containing functions specific to reduced spectral density mapping."""

        self.relax = relax


    def calculate(self, run=None, print_flag=1, sim_index=None):
        """Calculation of the spectral density values."""

        # Run argument.
        self.run = run

        # Test if the frequency has been set.
        if not hasattr(self.relax.data, 'jw_frq') or not self.relax.data.jw_frq.has_key(self.run) or type(self.relax.data.jw_frq[self.run]) != float:
            raise RelaxError, "The frequency for the run " + `self.run` + " has not been set up."

        # Test if the nucleus type has been set.
        if not hasattr(self.relax.data, 'gx'):
            raise RelaxNucleusError

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if the CSA and bond length values have been set.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
                continue

            # CSA value.
            if not hasattr(self.relax.data.res[self.run][i], 'csa') or self.relax.data.res[self.run][i].csa == None:
                raise RelaxNoValueError, "CSA"

            # Bond length value.
            if not hasattr(self.relax.data.res[self.run][i], 'r') or self.relax.data.res[self.run][i].r == None:
                raise RelaxNoValueError, "bond length"

        # Frequency index.
        if self.relax.data.jw_frq[self.run] not in self.relax.data.frq[self.run]:
            raise RelaxError, "No relaxation data corresponding to the frequency " + `self.relax.data.jw_frq[self.run]` + " has been loaded."

        # Reduced spectral density mapping.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Reassign data structure.
            data = self.relax.data.res[self.run][i]

            # Skip unselected residues.
            if not data.select:
                continue

            # Residue specific frequency index.
            frq_index = None
            for j in xrange(data.num_frq):
                if data.frq[j] == self.relax.data.jw_frq[self.run]:
                    frq_index = j
            if frq_index == None:
                continue

            # Set the r1, r2, and NOE to None.
            r1 = None
            r2 = None
            noe = None

            # Get the R1, R2, and NOE values corresponding to the set frequency.
            for j in xrange(data.num_ri):
                # R1.
                if data.remap_table[j] == frq_index and data.ri_labels[j] == 'R1':
                    if sim_index == None:
                        r1 = data.relax_data[j]
                    else:
                        r1 = data.relax_sim_data[sim_index][j]

                # R2.
                if data.remap_table[j] == frq_index and data.ri_labels[j] == 'R2':
                    if sim_index == None:
                        r2 = data.relax_data[j]
                    else:
                        r2 = data.relax_sim_data[sim_index][j]

                # NOE.
                if data.remap_table[j] == frq_index and data.ri_labels[j] == 'NOE':
                    if sim_index == None:
                        noe = data.relax_data[j]
                    else:
                        noe = data.relax_sim_data[sim_index][j]

            # Skip the residue if not all of the three value exist.
            if r1 == None or r2 == None or noe == None:
                continue

            # Initialise the function to calculate.
            self.jw = Mapping(frq=self.relax.data.jw_frq[self.run], gx=self.relax.data.gx, gh=self.relax.data.gh, mu0=self.relax.data.mu0, h_bar=self.relax.data.h_bar)

            # Calculate the spectral density values.
            j0, jwx, jwh = self.jw.func(r=data.r, csa=data.csa, r1=r1, r2=r2, noe=noe)

            # Reduced spectral density values.
            if sim_index == None:
                data.j0 = j0
                data.jwx = jwx
                data.jwh = jwh

            # Monte Carlo simulated reduced spectral density values.
            else:
                # Initialise the simulation data structures.
                self.data_init(data, sim=1)
                if data.j0_sim == None:
                    data.j0_sim = []
                    data.jwx_sim = []
                    data.jwh_sim = []

                # Reduced spectral density values.
                data.j0_sim.append(j0)
                data.jwx_sim.append(jwx)
                data.jwh_sim.append(jwh)


    def data_init(self, data, sim=0):
        """Function for initialising the data structures."""

        # Get the data names.
        data_names = self.data_names()

        # Loop over the data structure names.
        for name in data_names:
            # Simulation data structures.
            if sim:
                # Add '_sim' to the names.
                name = name + '_sim'

            # If the name is not in 'data', add it.
            if not hasattr(data, name):
                # Set the attribute.
                setattr(data, name, None)


    def data_names(self):
        """Function for returning a list of names of data structures.

        Description
        ~~~~~~~~~~~

        r:  Bond length.

        csa:  CSA value.

        j0:  Spectral density value at 0 MHz.

        jwx:  Spectral density value at the frequency of the heteronucleus.

        jwh:  Spectral density value at the frequency of the heteronucleus.
        """

        # Initialise.
        names = []

        # Values.
        names.append('r')
        names.append('csa')

        # Spectral density values.
        names.append('j0')
        names.append('jwx')
        names.append('jwh')

        return names


    def default_value(self, param):
        """
        Reduced spectral density mapping default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        _______________________________________________________________________________________
        |                                       |              |                              |
        | Data type                             | Object name  | Value                        |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Bond length                           | 'r'          | 1.02 * 1e-10                 |
        |                                       |              |                              |
        | CSA                                   | 'csa'        | -172 * 1e-6                  |
        |_______________________________________|______________|______________________________|

        """

        # Bond length.
        if param == 'r':
            return 1.02 * 1e-10

        # CSA.
        if param == 'CSA':
            return -172 * 1e-6


    def num_instances(self, run=None):
        """Function for returning the number of instances."""

        # Arguments.
        self.run = run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            return 0

        # Return the number of residues.
        return len(self.relax.data.res[self.run])


    def overfit_deselect(self, run):
        """Function for deselecting residues without sufficient data to support calculation"""

        # Test the sequence data exists:
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Loop over residue data:
        for residue in self.relax.data.res[run]:

            # Check for sufficient data
            if not hasattr(residue, 'relax_data'):
                residue.select = 0
                continue

            # Require 3 or more data points
            if len(residue.relax_data) < 3:
                residue.select = 0
                continue


    def return_conversion_factor(self, stat_type):
        """Dummy function for returning 1.0."""

        return 1.0


    def return_data_name(self, name):
        """
        Reduced spectral density mapping data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |              |                                                  |
        | Data type              | Object name  | Patterns                                         |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | J(0)                   | 'j0'         | '^[Jj]0$' or '[Jj]\(0\)'                         |
        |                        |              |                                                  |
        | J(wX)                  | 'jwx'        | '^[Jj]w[Xx]$' or '[Jj]\(w[Xx]\)'                 |
        |                        |              |                                                  |
        | J(wH)                  | 'jwh'        | '^[Jj]w[Hh]$' or '[Jj]\(w[Hh]\)'                 |
        |                        |              |                                                  |
        | Bond length            | 'r'          | '^r$' or '[Bb]ond[ -_][Ll]ength'                 |
        |                        |              |                                                  |
        | CSA                    | 'csa'        | '^[Cc][Ss][Aa]$'                                 |
        |________________________|______________|__________________________________________________|

        """

        # J(0).
        if search('^[Jj]0$', name) or search('[Jj]\(0\)', name):
            return 'j0'

        # J(wX).
        if search('^[Jj]w[Xx]$', name) or search('[Jj]\(w[Xx]\)', name):
            return 'jwx'

        # J(wH).
        if search('^[Jj]w[Hh]$', name) or search('[Jj]\(w[Hh]\)', name):
            return 'jwh'

        # Bond length.
        if search('^r$', name) or search('[Bb]ond[ -_][Ll]ength', name):
            return 'r'

        # CSA.
        if search('^[Cc][Ss][Aa]$', name):
            return 'csa'


    def return_grace_string(self, data_type):
        """Function for returning the Grace string representing the data type for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(data_type)

        # J(0).
        if object_name == 'j0':
            return '\\qJ(0)\\Q'

        # J(wX).
        elif object_name == 'jwx':
            return '\\qJ(\\xw\\f{}\\sX\\N)\\Q'

        # J(wH).
        elif object_name == 'jwh':
            return '\\qJ(\\xw\\f{}\\sH\\N)\\Q'

        # Bond length.
        elif object_name == 'r':
            return 'Bond length'

        # CSA.
        elif object_name == 'csa':
            return '\\qCSA\\Q'


    def return_units(self, data_type):
        """Function for returning a string representing the parameters units.

        For example, the internal representation of te is in seconds, whereas the external
        representation is in picoseconds, therefore this function will return the string
        'picoseconds' for te.
        """

        # Get the object name.
        object_name = self.return_data_name(data_type)

        # Bond length (Angstrom).
        if object_name == 'r':
            return 'Angstrom'

        # CSA (ppm).
        elif object_name == 'csa':
            return 'ppm'


    def set(self, run=None, value=None, error=None, param=None, index=None):
        """
        Reduced spectral density mapping set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        In reduced spectral density mapping, only two values can be set, the bond length and CSA
        value.  These must be set prior to the calculation of spectral density values.

        """

        # Arguments.
        self.run = run

        # Setting the model parameters prior to calculation.
        ####################################################

        if param == None:
            # The values are supplied by the user:
            if value:
                # Test if the length of the value array is equal to 2.
                if len(value) != 2:
                    raise RelaxError, "The length of " + `len(value)` + " of the value array must be equal to two."

            # Default values.
            else:
                # Set 'value' to an empty array.
                value = []

                # CSA and Bond length.
                value.append(self.default_value('csa'))
                value.append(self.default_value('r'))

            # Initilise data.
            if not hasattr(self.relax.data.res[self.run][index], 'csa') or not hasattr(self.relax.data.res[self.run][index], 'r'):
                self.data_init(self.relax.data.res[self.run][index])

            # CSA and Bond length.
            setattr(self.relax.data.res[self.run][index], 'csa', float(value[0]))
            setattr(self.relax.data.res[self.run][index], 'r', float(value[1]))


        # Individual data type.
        #######################

        else:
            # Get the object.
            object_name = self.return_data_name(param)
            if not object_name:
                raise RelaxError, "The reduced spectral density mapping data type " + `param` + " does not exist."

            # Initialise all data if it doesn't exist.
            if not hasattr(self.relax.data.res[self.run][index], object_name):
                self.data_init(self.relax.data.res[self.run][index])

            # Default value.
            if value == None:
                value = self.default_value(object_name)

            # Set the value.
            setattr(self.relax.data.res[self.run][index], object_name, float(value))

            # Set the error.
            if error != None:
                setattr(self.relax.data.res[self.run][index], object_name+'_err', float(error))


    def set_frq(self, run=None, frq=None):
        """Function for selecting which relaxation data to use in the J(w) mapping."""

        # Run argument.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the run type is set to 'jw'.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]
        if function_type != 'jw':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if the frequency has been set.
        if hasattr(self.relax.data, 'jw_frq') and self.relax.data.jw_frq.has_key(self.run):
            raise RelaxError, "The frequency for the run " + `self.run` + " has already been set."

        # Create the data structure if it doesn't exist.
        if not hasattr(self.relax.data, 'jw_frq'):
            self.relax.data.jw_frq = {}

        # Set the frequency.
        self.relax.data.jw_frq[self.run] = frq


    def set_error(self, run, instance, index, error):
        """Function for setting parameter errors."""

        # Arguments.
        self.run = run

        # Return J(0) sim data.
        if index == 0:
            self.relax.data.res[self.run][instance].j0_err = error

        # Return J(wX) sim data.
        if index == 1:
            self.relax.data.res[self.run][instance].jwx_err = error

        # Return J(wH) sim data.
        if index == 2:
            self.relax.data.res[self.run][instance].jwh_err = error


    def sim_return_param(self, run, instance, index):
        """Function for returning the array of simulation parameter values."""

        # Arguments.
        self.run = run

        # Skip unselected residues.
        if not self.relax.data.res[self.run][instance].select:
                return

        # Return J(0) sim data.
        if index == 0:
            return self.relax.data.res[self.run][instance].j0_sim

        # Return J(wX) sim data.
        if index == 1:
            return self.relax.data.res[self.run][instance].jwx_sim

        # Return J(wH) sim data.
        if index == 2:
            return self.relax.data.res[self.run][instance].jwh_sim


    def sim_return_selected(self, run, instance):
        """Function for returning the array of selected simulation flags."""

        # Arguments.
        self.run = run

        # Multiple instances.
        return self.relax.data.res[self.run][instance].select_sim


    def set_selected_sim(self, run, instance, select_sim):
        """Function for returning the array of selected simulation flags."""

        # Arguments.
        self.run = run

        # Multiple instances.
        self.relax.data.res[self.run][instance].select_sim = select_sim


    def sim_pack_data(self, run, i, sim_data):
        """Function for packing Monte Carlo simulation data."""

        # Test if the simulation data already exists.
        if hasattr(self.relax.data.res[run][i], 'relax_sim_data'):
            raise RelaxError, "Monte Carlo simulation data already exists."

        # Create the data structure.
        self.relax.data.res[run][i].relax_sim_data = sim_data


    def write_columnar_line(self, file=None, num=None, name=None, select=None, data_set=None, nucleus=None, wH=None, j0=None, jwx=None, jwh=None, r=None, csa=None, ri_labels=None, remap_table=None, frq_labels=None, frq=None, ri=None, ri_error=None):
        """Function for printing a single line of the columnar formatted results."""

        # Residue number and name.
        file.write("%-4s %-5s " % (num, name))

        # Selected flag and data set.
        file.write("%-9s %-9s " % (select, data_set))

        # Nucleus.
        file.write("%-7s " % nucleus)

        # Proton frequency.
        file.write("%-25s " % wH)

        # Parameters.
        file.write("%-25s " % j0)
        file.write("%-25s " % jwx)
        file.write("%-25s " % jwh)
        file.write("%-25s " % r)
        file.write("%-25s " % csa)

        # Relaxation data setup.
        if ri_labels:
            file.write("%-40s " % ri_labels)
            file.write("%-25s " % remap_table)
            file.write("%-25s " % frq_labels)
            file.write("%-30s " % frq)

        # Relaxation data.
        if ri:
            for i in xrange(len(ri)):
                if ri[i] == None:
                    file.write("%-25s " % 'None')
                else:
                    file.write("%-25s " % ri[i])

        # Relaxation errors.
        if ri_error:
            for i in xrange(len(ri_error)):
                if ri_error[i] == None:
                    file.write("%-25s " % 'None')
                else:
                    file.write("%-25s " % ri_error[i])

        # End of the line.
        file.write("\n")


    def write_columnar_results(self, file, run):
        """Function for printing the results into a file."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run


        # Header.
        #########

        # Relaxation data and errors.
        ri = []
        ri_error = []
        if hasattr(self.relax.data, 'num_ri'):
            for i in xrange(self.relax.data.num_ri[self.run]):
                ri.append('Ri_(' + self.relax.data.ri_labels[self.run][i] + "_" + self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][i]] + ")")
                ri_error.append('Ri_error_(' + self.relax.data.ri_labels[self.run][i] + "_" + self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][i]] + ")")

        # Write the header line.
        self.write_columnar_line(file=file, num='Num', name='Name', select='Selected', data_set='Data_set', nucleus='Nucleus', wH='Proton_frq_(MHz)', j0='J(0)', jwx='J(wX)', jwh='J(wH)', r='Bond_length_(A)', csa='CSA_(ppm)', ri_labels='Ri_labels', remap_table='Remap_table', frq_labels='Frq_labels', frq='Frequencies', ri=ri, ri_error=ri_error)


        # Values.
        #########

        # Nucleus.
        nucleus = self.relax.generic.nuclei.find_nucleus()

        # The proton frequency in MHz.
        wH = self.relax.data.jw_frq[self.run] / 1e6

        # Relaxation data setup.
        try:
            ri_labels = replace(`self.relax.data.ri_labels[self.run]`, ' ', '')
            remap_table = replace(`self.relax.data.remap_table[self.run]`, ' ', '')
            frq_labels = replace(`self.relax.data.frq_labels[self.run]`, ' ', '')
            frq = replace(`self.relax.data.frq[self.run]`, ' ', '')
        except AttributeError:
            ri_labels = `None`
            remap_table = `None`
            frq_labels = `None`
            frq = `None`

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Reassign data structure.
            data = self.relax.data.res[self.run][i]

            # J(0).
            j0 = None
            if hasattr(data, 'j0'):
                j0 = data.j0

            # J(wX).
            jwx = None
            if hasattr(data, 'jwx'):
                jwx = data.jwx

            # J(wH).
            jwh = None
            if hasattr(data, 'jwh'):
                jwh = data.jwh

            # Bond length.
            r = None
            if hasattr(data, 'r') and data.r != None:
                r = data.r / 1e-10

            # CSA.
            csa = None
            if hasattr(data, 'csa') and data.csa != None:
                csa = data.csa / 1e-6

            # Relaxation data and errors.
            ri = []
            ri_error = []
            if hasattr(self.relax.data, 'num_ri'):
                for i in xrange(self.relax.data.num_ri[self.run]):
                    try:
                        # Find the residue specific data corresponding to i.
                        index = None
                        for j in xrange(data.num_ri):
                            if data.ri_labels[j] == self.relax.data.ri_labels[self.run][i] and data.frq_labels[data.remap_table[j]] == self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][i]]:
                                index = j

                        # Data exists for this data type.
                        ri.append(`data.relax_data[index]`)
                        ri_error.append(`data.relax_error[index]`)

                    # No data exists for this data type.
                    except:
                        ri.append(None)
                        ri_error.append(None)

            # Write the line.
            self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='value', nucleus=nucleus, wH=`wH`, j0=`j0`, jwx=`jwx`, jwh=`jwh`, r=`r`, csa=`csa`, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Errors.
        #########

        # Skip this section and the next if no simulations have been setup.
        if not hasattr(self.relax.data, 'sim_state'):
            return
        elif self.relax.data.sim_state[self.run] == 0:
            return

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Reassign data structure.
            data = self.relax.data.res[self.run][i]

            # J(0).
            j0 = None
            if hasattr(data, 'j0_err'):
                j0 = data.j0_err

            # J(wX).
            jwx = None
            if hasattr(data, 'jwx_err'):
                jwx = data.jwx_err

            # J(wH).
            jwh = None
            if hasattr(data, 'jwh_err'):
                jwh = data.jwh_err

            # Bond length.
            r = None
            if hasattr(data, 'r_err') and data.r_err != None:
                r = data.r_err / 1e-10

            # CSA.
            csa = None
            if hasattr(data, 'csa_err') and data.csa_err != None:
                csa = data.csa_err / 1e-6

            # Relaxation data and errors.
            ri = []
            ri_error = []
            for i in xrange(self.relax.data.num_ri[self.run]):
                ri.append(None)
                ri_error.append(None)

            # Write the line.
            self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='error', nucleus=nucleus, wH=`wH`, j0=`j0`, jwx=`jwx`, jwh=`jwh`, r=`r`, csa=`csa`, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Simulation values.
        ####################

        # Loop over the simulations.
        for i in xrange(self.relax.data.sim_number[self.run]):
            # Loop over the sequence.
            for j in xrange(len(self.relax.data.res[self.run])):
                # Reassign data structure.
                data = self.relax.data.res[self.run][j]

                # J(0).
                j0 = None
                if hasattr(data, 'j0_sim'):
                    j0 = data.j0_sim[i]

                # J(wX).
                jwx = None
                if hasattr(data, 'jwx_sim'):
                    jwx = data.jwx_sim[i]

                # J(wH).
                jwh = None
                if hasattr(data, 'jwh_sim'):
                    jwh = data.jwh_sim[i]

                # Bond length.
                r = None
                if hasattr(data, 'r_sim') and data.r_sim != None and data.r_sim[i] != None:
                    r = data.r_sim[i] / 1e-10

                # CSA.
                csa = None
                if hasattr(data, 'csa_sim') and data.csa_sim != None and data.csa_sim[i] != None:
                    csa = data.csa_sim[i] / 1e-6

                # Relaxation data and errors.
                ri = []
                ri_error = []
                if hasattr(self.relax.data, 'num_ri'):
                    for k in xrange(self.relax.data.num_ri[self.run]):
                        try:
                            # Find the residue specific data corresponding to k.
                            index = None
                            for l in xrange(data.num_ri):
                                if data.ri_labels[l] == self.relax.data.ri_labels[self.run][k] and data.frq_labels[data.remap_table[l]] == self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][k]]:
                                    index = l

                            # Data exists for this data type.
                            ri.append(`data.relax_sim_data[i][index]`)
                            ri_error.append(`data.relax_error[index]`)

                        # No data exists for this data type.
                        except:
                            ri.append(None)
                            ri_error.append(None)

                # Write the line.
                self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='sim_'+`i`, nucleus=nucleus, wH=`wH`, j0=`j0`, jwx=`jwx`, jwh=`jwh`, r=`r`, csa=`csa`, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)
