###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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

# Python module imports.
from data.diff_tensor import DiffTensorSimList
from math import pi
from numpy import float64, array, transpose
from re import search
from string import replace, split

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import diffusion_tensor
from generic_fns.mol_res_spin import spin_loop
from relax_errors import RelaxError, RelaxInvalidDataError



class Results:
    """Class containing methods specific to the model-free results files."""

    def __determine_version(self, file_data, verbosity):
        """Determine which relax version the results file belongs to.

        @param file_data:   The processed results file data.
        @type file_data:    list of lists of str
        @param verbosity:   A flag specifying the amount of information to print.  The higher the
                            value, the greater the verbosity.
        @type verbosity:    int
        @return:            The relax version number.
        @rtype:             str
        @raises RelaxError: If the relax version the model-free results file belongs to cannot be
                            determined.
        """

        # relax 1.2 results file (test for the 1.2 header line).
        if len(file_data[0]) == 54 and file_data[0][0:8] == ['Num', 'Name', 'Selected', 'Data_set', 'Nucleus', 'Model', 'Equation', 'Params']:
            version = '1.2'

        # Can't determine the file version.
        else:
            raise RelaxError, "Cannot determine the relax version the model-free results file belongs to."

        # Print out.
        if verbosity:
            print "relax " + version + " model-free results file."

        # Return the version.
        return version


    def read_columnar_col_numbers(self, header):
        """Function for sorting the column numbers from the columnar formatted results file."""

        # Initialise the hash.
        self.col = {}

        # Loop over the columns.
        for i in xrange(len(header)):
            # Residue info.
            if header[i] == 'Num':
                self.col['num'] = i
            elif header[i] == 'Name':
                self.col['name'] = i
            elif header[i] == 'Selected':
                self.col['select'] = i
            elif header[i] == 'Data_set':
                self.col['data_set'] = i
            elif header[i] == 'Nucleus':
                self.col['nucleus'] = i
            elif header[i] == 'Model':
                self.col['model'] = i
            elif header[i] == 'Equation':
                self.col['eqi'] = i
            elif header[i] == 'Params':
                self.col['params'] = i
            elif header[i] == 'Param_set':
                self.col['param_set'] = i

            # Parameters.
            elif header[i] == 'S2':
                self.col['s2'] = i
            elif header[i] == 'S2f':
                self.col['s2f'] = i
            elif header[i] == 'S2s':
                self.col['s2s'] = i
            elif search('^Local_tm', header[i]):
                self.col['local_tm'] = i
            elif search('^te', header[i]):
                self.col['te'] = i
            elif search('^tf', header[i]):
                self.col['tf'] = i
            elif search('^ts', header[i]):
                self.col['ts'] = i
            elif search('^Rex', header[i]):
                self.col['rex'] = i
            elif search('^Bond_length', header[i]):
                self.col['r'] = i
            elif search('^CSA', header[i]):
                self.col['csa'] = i

            # Minimisation info.
            elif header[i] == 'Chi-squared':
                self.col['chi2'] = i
            elif header[i] == 'Iter':
                self.col['iter'] = i
            elif header[i] == 'f_count':
                self.col['f_count'] = i
            elif header[i] == 'g_count':
                self.col['g_count'] = i
            elif header[i] == 'h_count':
                self.col['h_count'] = i
            elif header[i] == 'Warning':
                self.col['warn'] = i

            # Diffusion tensor.
            elif header[i] == 'Diff_type':
                self.col['diff_type'] = i
            elif header[i] == 'tm_(s)':
                self.col['tm'] = i
            elif header[i] == 'Da_(1/s)':
                self.col['da'] = i
            elif header[i] == 'theta_(deg)':
                self.col['theta'] = i
            elif header[i] == 'phi_(deg)':
                self.col['phi'] = i
            elif header[i] == 'Da_(1/s)':
                self.col['da'] = i
            elif header[i] == 'Dr_(1/s)':
                self.col['dr'] = i
            elif header[i] == 'alpha_(deg)':
                self.col['alpha'] = i
            elif header[i] == 'beta_(deg)':
                self.col['beta'] = i
            elif header[i] == 'gamma_(deg)':
                self.col['gamma'] = i

            # PDB and XH vector.
            elif header[i] == 'PDB':
                self.col['pdb'] = i
            elif header[i] == 'PDB_model':
                self.col['pdb_model'] = i
            elif header[i] == 'PDB_heteronuc':
                self.col['pdb_heteronuc'] = i
            elif header[i] == 'PDB_proton':
                self.col['pdb_proton'] = i
            elif header[i] == 'XH_vector':
                self.col['xh_vect'] = i

            # Relaxation data.
            elif header[i] == 'Ri_labels':
                self.col['ri_labels'] = i
            elif header[i] == 'Remap_table':
                self.col['remap_table'] = i
            elif header[i] == 'Frq_labels':
                self.col['frq_labels'] = i
            elif header[i] == 'Frequencies':
                self.col['frq'] = i


    def read_columnar_diff_tensor(self):
        """Function for setting up the diffusion tensor from the columnar formatted results file."""

        # The diffusion tensor type.
        diff_type = self.file_line[self.col['diff_type']]
        if diff_type == 'None':
            diff_type = None

        # Sphere.
        if diff_type == 'sphere':
            # Convert the parameters to floating point numbers.
            try:
                tm = float(self.file_line[self.col['tm']])
            except ValueError:
                # Errors or simulation values set to None.
                if self.data_set != 'value' and self.file_line[self.col['tm']] == 'None':
                    return

                # Genuine error.
                raise RelaxError, "The diffusion tensor parameters are not numbers."

            # Values.
            if self.data_set == 'value':
                diff_params = tm

            # Errors.
            elif self.data_set == 'error':
                ds.diff[self.run].tm_err = tm

            # Simulation values.
            else:
                # Create the data structure if it doesn't exist.
                if not hasattr(ds.diff[self.run], 'tm_sim'):
                    ds.diff[self.run].tm_sim = DiffTensorSimList('tm', ds.diff[self.run])

                # Append the value.
                ds.diff[self.run].tm_sim.append(tm)


        # Spheroid.
        elif diff_type == 'spheroid' or diff_type == 'oblate' or diff_type == 'prolate':
            # Convert the parameters to floating point numbers.
            try:
                tm = float(self.file_line[self.col['tm']])
                Da = float(self.file_line[self.col['da']])
                theta = float(self.file_line[self.col['theta']]) / 360.0 * 2.0 * pi
                phi = float(self.file_line[self.col['phi']]) / 360.0 * 2.0 * pi
            except ValueError:
                # Errors or simulation values set to None.
                if self.data_set != 'value' and self.file_line[self.col['tm']] == 'None':
                    return

                # Genuine error.
                raise RelaxError, "The diffusion tensor parameters are not numbers."

            # Values.
            if self.data_set == 'value':
                diff_params = [tm, Da, theta, phi]

            # Errors.
            elif self.data_set == 'error':
                ds.diff[self.run].tm_err = tm
                ds.diff[self.run].Da_err = Da
                ds.diff[self.run].theta_err = theta
                ds.diff[self.run].phi_err = phi

            # Simulation values.
            else:
                # Create the data structure if it doesn't exist.
                if not hasattr(ds.diff[self.run], 'tm_sim'):
                    ds.diff[self.run].tm_sim = DiffTensorSimList('tm', ds.diff[self.run])
                if not hasattr(ds.diff[self.run], 'Da_sim'):
                    ds.diff[self.run].Da_sim = DiffTensorSimList('Da', ds.diff[self.run])
                if not hasattr(ds.diff[self.run], 'theta_sim'):
                    ds.diff[self.run].theta_sim = DiffTensorSimList('theta', ds.diff[self.run])
                if not hasattr(ds.diff[self.run], 'phi_sim'):
                    ds.diff[self.run].phi_sim = DiffTensorSimList('phi', ds.diff[self.run])

                # Append the value.
                ds.diff[self.run].tm_sim.append(tm)
                ds.diff[self.run].Da_sim.append(Da)
                ds.diff[self.run].theta_sim.append(theta)
                ds.diff[self.run].phi_sim.append(phi)


        # Ellipsoid.
        elif diff_type == 'ellipsoid':
            # Convert the parameters to floating point numbers.
            try:
                tm = float(self.file_line[self.col['tm']])
                Da = float(self.file_line[self.col['da']])
                Dr = float(self.file_line[self.col['dr']])
                alpha = float(self.file_line[self.col['alpha']]) / 360.0 * 2.0 * pi
                beta = float(self.file_line[self.col['beta']]) / 360.0 * 2.0 * pi
                gamma = float(self.file_line[self.col['gamma']]) / 360.0 * 2.0 * pi
            except ValueError:
                # Errors or simulation values set to None.
                if self.data_set != 'value' and self.file_line[self.col['tm']] == 'None':
                    return

                # Genuine error.
                raise RelaxError, "The diffusion tensor parameters are not numbers."

            # Values.
            if self.data_set == 'value':
                diff_params = [tm, Da, Dr, alpha, beta, gamma]

            # Errors.
            elif self.data_set == 'error':
                ds.diff[self.run].tm_err = tm
                ds.diff[self.run].Da_err = Da
                ds.diff[self.run].Dr_err = Dr
                ds.diff[self.run].alpha_err = alpha
                ds.diff[self.run].beta_err = beta
                ds.diff[self.run].gamma_err = gamma

            # Simulation values.
            else:
                # Create the data structure if it doesn't exist.
                if not hasattr(ds.diff[self.run], 'tm_sim'):
                    ds.diff[self.run].tm_sim = DiffTensorSimList('tm', ds.diff[self.run])
                if not hasattr(ds.diff[self.run], 'Da_sim'):
                    ds.diff[self.run].Da_sim = DiffTensorSimList('Da', ds.diff[self.run])
                if not hasattr(ds.diff[self.run], 'Dr_sim'):
                    ds.diff[self.run].Dr_sim = DiffTensorSimList('Dr', ds.diff[self.run])
                if not hasattr(ds.diff[self.run], 'alpha_sim'):
                    ds.diff[self.run].alpha_sim = DiffTensorSimList('alpha', ds.diff[self.run])
                if not hasattr(ds.diff[self.run], 'beta_sim'):
                    ds.diff[self.run].beta_sim = DiffTensorSimList('beta', ds.diff[self.run])
                if not hasattr(ds.diff[self.run], 'gamma_sim'):
                    ds.diff[self.run].gamma_sim = DiffTensorSimList('gamma', ds.diff[self.run])

                # Append the value.
                ds.diff[self.run].tm_sim.append(tm)
                ds.diff[self.run].Da_sim.append(Da)
                ds.diff[self.run].Dr_sim.append(Dr)
                ds.diff[self.run].alpha_sim.append(alpha)
                ds.diff[self.run].beta_sim.append(beta)
                ds.diff[self.run].gamma_sim.append(gamma)


        # Set the diffusion tensor.
        if self.data_set == 'value' and diff_type:
            # Sort out the spheroid type.
            spheroid_type = None
            if diff_type == 'oblate' or diff_type == 'prolate':
                spheroid_type = diff_type

            # Set the diffusion tensor.
            self.relax.generic.diffusion_tensor.init(run=self.run, params=diff_params, angle_units='rad', spheroid_type=spheroid_type)


    def read_columnar_find_index(self):
        """Function for generating the sequence and or returning the residue index."""

        # Residue number and name.
        try:
            self.res_num = int(self.file_line[self.col['num']])
        except ValueError:
            raise RelaxError, "The residue number " + self.file_line[self.col['num']] + " is not an integer."
        self.res_name = self.file_line[self.col['name']]

        # Find the residue index.
        res_index = None
        for j in xrange(len(ds.res[self.run])):
            if ds.res[self.run][j].num == self.res_num and ds.res[self.run][j].name == self.res_name:
                res_index = j
                break
        if res_index == None:
            raise RelaxError, "Residue " + `self.res_num` + " " + self.res_name + " cannot be found in the sequence."

        # Return the index.
        return res_index


    def read_columnar_model_free_data(self):
        """Function for reading the model-free data."""

        # Reassign data structure.
        data = ds.res[self.run][self.res_index]

        # Set up the model-free models.
        if self.data_set == 'value':
            # Get the model-free model.
            model = self.file_line[self.col['model']]

            # Get the model-free equation.
            equation = self.file_line[self.col['eqi']]

            # Get the model-free parameters.
            params = eval(self.file_line[self.col['params']])

            # Fix for the 1.2 relax versions whereby the parameter 'tm' was renamed to 'local_tm' (which occurred in version 1.2.5).
            if params:
                for i in xrange(len(params)):
                    if params[i] == 'tm':
                        params[i] = 'local_tm'

            # Set up the model-free model.
            if model and equation:
                self.model_setup(self.run, model=model, equation=equation, params=params, res_num=self.res_num)

        # Values.
        if self.data_set == 'value':
            # S2.
            try:
                data.s2 = float(self.file_line[self.col['s2']]) * self.return_conversion_factor('s2')
            except ValueError:
                data.s2 = None

            # S2f.
            try:
                data.s2f = float(self.file_line[self.col['s2f']]) * self.return_conversion_factor('s2f')
            except ValueError:
                data.s2f = None

            # S2s.
            try:
                data.s2s = float(self.file_line[self.col['s2s']]) * self.return_conversion_factor('s2s')
            except ValueError:
                data.s2s = None

            # Local tm.
            try:
                data.local_tm = float(self.file_line[self.col['local_tm']]) * self.return_conversion_factor('local_tm')
            except ValueError:
                data.local_tm = None

            # te.
            try:
                data.te = float(self.file_line[self.col['te']]) * self.return_conversion_factor('te')
            except ValueError:
                data.te = None

            # tf.
            try:
                data.tf = float(self.file_line[self.col['tf']]) * self.return_conversion_factor('tf')
            except ValueError:
                data.tf = None

            # ts.
            try:
                data.ts = float(self.file_line[self.col['ts']]) * self.return_conversion_factor('ts')
            except ValueError:
                data.ts = None

            # Rex.
            try:
                data.rex = float(self.file_line[self.col['rex']]) * self.return_conversion_factor('rex')
            except ValueError:
                data.rex = None

            # Bond length.
            try:
                data.r = float(self.file_line[self.col['r']]) * self.return_conversion_factor('r')
            except ValueError:
                data.r = None

            # CSA.
            try:
                data.csa = float(self.file_line[self.col['csa']]) * self.return_conversion_factor('csa')
            except ValueError:
                data.csa = None

            # Minimisation details (global minimisation results).
            if self.param_set == 'diff' or self.param_set == 'all':
                ds.chi2[self.run] = eval(self.file_line[self.col['chi2']])
                ds.iter[self.run] = eval(self.file_line[self.col['iter']])
                ds.f_count[self.run] = eval(self.file_line[self.col['f_count']])
                ds.g_count[self.run] = eval(self.file_line[self.col['g_count']])
                ds.h_count[self.run] = eval(self.file_line[self.col['h_count']])
                if self.file_line[self.col['warn']] == 'None':
                    ds.warning[self.run] = None
                else:
                    ds.warning[self.run] = replace(self.file_line[self.col['warn']], '_', ' ')

            # Minimisation details (individual residue results).
            else:
                data.chi2 = eval(self.file_line[self.col['chi2']])
                data.iter = eval(self.file_line[self.col['iter']])
                data.f_count = eval(self.file_line[self.col['f_count']])
                data.g_count = eval(self.file_line[self.col['g_count']])
                data.h_count = eval(self.file_line[self.col['h_count']])
                if self.file_line[self.col['warn']] == 'None':
                    data.warning = None
                else:
                    data.warning = replace(self.file_line[self.col['warn']], '_', ' ')

        # Errors.
        if self.data_set == 'error':
            # S2.
            try:
                data.s2_err = float(self.file_line[self.col['s2']]) * self.return_conversion_factor('s2')
            except ValueError:
                data.s2_err = None

            # S2f.
            try:
                data.s2f_err = float(self.file_line[self.col['s2f']]) * self.return_conversion_factor('s2f')
            except ValueError:
                data.s2f_err = None

            # S2s.
            try:
                data.s2s_err = float(self.file_line[self.col['s2s']]) * self.return_conversion_factor('s2s')
            except ValueError:
                data.s2s_err = None

            # Local tm.
            try:
                data.local_tm_err = float(self.file_line[self.col['local_tm']]) * self.return_conversion_factor('local_tm')
            except ValueError:
                data.local_tm_err = None

            # te.
            try:
                data.te_err = float(self.file_line[self.col['te']]) * self.return_conversion_factor('te')
            except ValueError:
                data.te_err = None

            # tf.
            try:
                data.tf_err = float(self.file_line[self.col['tf']]) * self.return_conversion_factor('tf')
            except ValueError:
                data.tf_err = None

            # ts.
            try:
                data.ts_err = float(self.file_line[self.col['ts']]) * self.return_conversion_factor('ts')
            except ValueError:
                data.ts_err = None

            # Rex.
            try:
                data.rex_err = float(self.file_line[self.col['rex']]) * self.return_conversion_factor('rex')
            except ValueError:
                data.rex_err = None

            # Bond length.
            try:
                data.r_err = float(self.file_line[self.col['r']]) * self.return_conversion_factor('r')
            except ValueError:
                data.r_err = None

            # CSA.
            try:
                data.csa_err = float(self.file_line[self.col['csa']]) * self.return_conversion_factor('csa')
            except ValueError:
                data.csa_err = None


        # Construct the simulation data structures.
        if self.data_set == 'sim_0':
            # Get the parameter object names.
            param_names = self.data_names(set='params')

            # Get the minimisation statistic object names.
            min_names = self.data_names(set='min')

            # Loop over all the parameter names.
            for object_name in param_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(data, sim_object_name, [])

            # Loop over all the minimisation object names.
            for object_name in min_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                if self.param_set == 'diff' or self.param_set == 'all':
                    setattr(ds, sim_object_name, {})
                    object = getattr(ds, sim_object_name)
                    object[self.run] = []
                else:
                    setattr(data, sim_object_name, [])

        # Simulations.
        if self.data_set != 'value' and self.data_set != 'error':
            # S2.
            try:
                data.s2_sim.append(float(self.file_line[self.col['s2']]) * self.return_conversion_factor('s2'))
            except ValueError:
                data.s2_sim.append(None)

            # S2f.
            try:
                data.s2f_sim.append(float(self.file_line[self.col['s2f']]) * self.return_conversion_factor('s2f'))
            except ValueError:
                data.s2f_sim.append(None)

            # S2s.
            try:
                data.s2s_sim.append(float(self.file_line[self.col['s2s']]) * self.return_conversion_factor('s2s'))
            except ValueError:
                data.s2s_sim.append(None)

            # Local tm.
            try:
                data.local_tm_sim.append(float(self.file_line[self.col['local_tm']]) * self.return_conversion_factor('local_tm'))
            except ValueError:
                data.local_tm_sim.append(None)

            # te.
            try:
                data.te_sim.append(float(self.file_line[self.col['te']]) * self.return_conversion_factor('te'))
            except ValueError:
                data.te_sim.append(None)

            # tf.
            try:
                data.tf_sim.append(float(self.file_line[self.col['tf']]) * self.return_conversion_factor('tf'))
            except ValueError:
                data.tf_sim.append(None)

            # ts.
            try:
                data.ts_sim.append(float(self.file_line[self.col['ts']]) * self.return_conversion_factor('ts'))
            except ValueError:
                data.ts_sim.append(None)

            # Rex.
            try:
                data.rex_sim.append(float(self.file_line[self.col['rex']]) * self.return_conversion_factor('rex'))
            except ValueError:
                data.rex_sim.append(None)

            # Bond length.
            try:
                data.r_sim.append(float(self.file_line[self.col['r']]) * self.return_conversion_factor('r'))
            except ValueError:
                data.r_sim.append(None)

            # CSA.
            try:
                data.csa_sim.append(float(self.file_line[self.col['csa']]) * self.return_conversion_factor('csa'))
            except ValueError:
                data.csa_sim.append(None)

            # Minimisation details (global minimisation results).
            if self.param_set == 'diff' or self.param_set == 'all':
                ds.chi2_sim[self.run].append(eval(self.file_line[self.col['chi2']]))
                ds.iter_sim[self.run].append(eval(self.file_line[self.col['iter']]))
                ds.f_count_sim[self.run].append(eval(self.file_line[self.col['f_count']]))
                ds.g_count_sim[self.run].append(eval(self.file_line[self.col['g_count']]))
                ds.h_count_sim[self.run].append(eval(self.file_line[self.col['h_count']]))
                if self.file_line[self.col['warn']] == 'None':
                    ds.warning_sim[self.run].append(None)
                else:
                    ds.warning_sim[self.run].append(replace(self.file_line[self.col['warn']], '_', ' '))

            # Minimisation details (individual residue results).
            else:
                data.chi2_sim.append(eval(self.file_line[self.col['chi2']]))
                data.iter_sim.append(eval(self.file_line[self.col['iter']]))
                data.f_count_sim.append(eval(self.file_line[self.col['f_count']]))
                data.g_count_sim.append(eval(self.file_line[self.col['g_count']]))
                data.h_count_sim.append(eval(self.file_line[self.col['h_count']]))
                if self.file_line[self.col['warn']] == 'None':
                    data.warning_sim.append(None)
                else:
                    data.warning_sim.append(replace(self.file_line[self.col['warn']], '_', ' '))


    def read_columnar_param_set(self):
        """Function for reading the parameter set."""

        # Extract the parameter set if it exists, otherwise return.
        if self.file_line[self.col['param_set']] != 'None':
            self.param_set = self.file_line[self.col['param_set']]
        else:
            return

        # Local tm and model-free only parameter sets.
        if self.param_set == 'local_tm' or self.param_set == 'mf':
            diff_fixed = 1
            res_fixed = 0

        # Diffusion tensor parameter set.
        elif self.param_set == 'diff':
            diff_fixed = 0
            res_fixed = 1

        # 'all' parameter set.
        elif self.param_set == 'all':
            diff_fixed = 0
            res_fixed = 0

        # No parameter set.
        elif self.param_set == 'None':
            self.param_set = None
            diff_fixed = None
            res_fixed = None

        # Set the diffusion tensor fixed flag.
        if self.param_set != 'local_tm' and diff_fixed != None:
            ds.diff[self.run].fixed = diff_fixed

        # Set the residue specific fixed flag.
        for i in xrange(len(ds.res[self.run])):
            if res_fixed != None:
                ds.res[self.run][i].fixed = res_fixed


    def read_columnar_pdb(self, verbosity=1):
        """Function for reading the PDB file."""

        # File name.
        pdb = self.file_line[self.col['pdb']]

        # PDB model.
        pdb_model = eval(self.file_line[self.col['pdb_model']])

        # Read the PDB file (if it exists).
        if not pdb == 'None':
            self.relax.generic.structure.read_pdb(run=self.run, file=pdb, model=pdb_model, fail=0, verbosity=verbosity)
            return 1
        else:
            return 0


    def read_columnar_relax_data(self):
        """Function for reading the relaxation data."""

        # Skip the error 'data_set'.
        if self.data_set == 'error':
            return

        # Relaxation data structures.
        self.ri_labels = eval(self.file_line[self.col['ri_labels']])
        self.remap_table = eval(self.file_line[self.col['remap_table']])
        self.frq_labels = eval(self.file_line[self.col['frq_labels']])
        self.frq = eval(self.file_line[self.col['frq']])

        # No relaxation data.
        if not self.ri_labels:
            return

        # Initialise the value and error arrays.
        values = []
        errors = []

        # Loop over the relaxation data of the residue.
        for i in xrange(len(self.ri_labels)):
            # Determine the data and error columns for this relaxation data set.
            data_col = self.col['frq'] + i + 1
            error_col = self.col['frq'] + len(self.ri_labels) + i + 1

            # Append the value and error.
            values.append(eval(self.file_line[data_col]))
            errors.append(eval(self.file_line[error_col]))

        # Simulations.
        sim = 0
        if self.data_set != 'value' and self.data_set != 'error':
            sim = 1

        # Add the relaxation data.
        self.relax.specific.relax_data.add_residue(run=self.run, res_index=self.res_index, ri_labels=self.ri_labels, remap_table=self.remap_table, frq_labels=self.frq_labels, frq=self.frq, values=values, errors=errors, sim=sim)


    def read_columnar_results(self, file_data, verbosity=1):
        """Read the model-free results file.

        @param file_data:   The processed results file data.
        @type file_data:    list of lists of str
        @keyword verbosity: A flag specifying the amount of information to print.  The higher the
                            value, the greater the verbosity.
        @type verbosity:    int
        """

        # Determine the results file version.
        version = self.__determine_version(file_data, verbosity)

        # Execute the version specific methods.
        if version == '1.2':
            self.__read_1_2_results(file_data, verbosity)


    def read_1_2_results(self, file_data, verbosity=1):
        """Read the relax 1.2 model-free results file.

        @param file_data:   The processed results file data.
        @type file_data:    list of lists of str
        @keyword verbosity: A flag specifying the amount of information to print.  The higher the
                            value, the greater the verbosity.
        @type verbosity:    int
        """

        # Extract and remove the header.
        header = file_data[0]
        file_data = file_data[1:]

        # Sort the column numbers.
        self.read_columnar_col_numbers(header)

        # Test the file.
        if len(self.col) < 2:
            raise RelaxInvalidDataError

        # Initialise some data structures and flags.
        nucleus_set = 0
        sim_num = None
        sims = []
        all_select_sim = []
        diff_data_set = 0
        diff_error_set = 0
        diff_sim_set = None
        self.param_set = None
        pdb = 0
        pdb_model = None
        pdb_heteronuc = None
        pdb_proton = None
        self.ri_labels = None

        # Generate the sequence.
        for self.file_line in file_data:
            # The data set.
            self.data_set = self.file_line[self.col['data_set']]

            # Stop creating the sequence once the data_set is no longer 'value'.
            if self.data_set != 'value':
                break

            # Sequence.
            self.read_columnar_sequence()


        # Loop over the lines of the file data.
        for self.file_line in file_data:
            # The data set.
            self.data_set = self.file_line[self.col['data_set']]

            # Find the residue index.
            self.res_index = self.read_columnar_find_index()

            # Reassign data structure.
            data = ds.res[self.run][self.res_index]

            # Backwards compatibility for the reading of the results file from versions 1.2.0 to 1.2.9.
            if len(self.file_line) == 4:
                continue

            # Set the nucleus type.
            if not nucleus_set:
                if self.file_line[self.col['nucleus']] != 'None':
                    self.relax.generic.nuclei.set_values(self.file_line[self.col['nucleus']])
                    nucleus_set = 1

            # Simulation number.
            if self.data_set != 'value' and self.data_set != 'error':
                # Extract the number from the self.data_set string.
                sim_num = split(self.data_set, '_')
                try:
                    sim_num = int(sim_num[1])
                except:
                    raise RelaxError, "The simulation number '%s' is invalid." % sim_num

                # A new simulation number.
                if sim_num not in sims:
                    # Update the sims array and append an empty array to the selected sims array.
                    sims.append(sim_num)
                    all_select_sim.append([])

                # Selected simulations.
                all_select_sim[-1].append(int(self.file_line[self.col['select']]))

            # Diffusion tensor data.
            if self.data_set == 'value' and not diff_data_set:
                self.read_columnar_diff_tensor()
                diff_data_set = 1

            # Diffusion tensor errors.
            elif self.data_set == 'error' and not diff_error_set:
                self.read_columnar_diff_tensor()
                diff_error_set = 1

            # Diffusion tensor simulation data.
            elif self.data_set != 'value' and self.data_set != 'error' and sim_num != diff_sim_set:
                self.read_columnar_diff_tensor()
                diff_sim_set = sim_num

            # Parameter set.
            if self.param_set == None:
                self.read_columnar_param_set()

            # PDB.
            if not pdb:
                if self.read_columnar_pdb(verbosity):
                    pdb = 1

            # XH vector, heteronucleus, and proton.
            if self.data_set == 'value':
                self.read_columnar_xh_vect()

            # Relaxation data.
            self.read_columnar_relax_data()

            # Model-free data.
            self.read_columnar_model_free_data()

        # Set up the simulations.
        if len(sims):
            # Convert the selected simulation array of arrays into a Numeric matrix and transpose it.
            all_select_sim = transpose(array(all_select_sim))

            # Set up the Monte Carlo simulations.
            self.relax.generic.monte_carlo.setup(self.run, number=len(sims), all_select_sim=all_select_sim)

            # Turn the simulation state to off!
            ds.sim_state[self.run] = 0


    def read_columnar_sequence(self):
        """Function for generating the sequence."""

        # Residue number and name.
        try:
            res_num = int(self.file_line[self.col['num']])
        except ValueError:
            raise RelaxError, "The residue number " + self.file_line[self.col['num']] + " is not an integer."
        res_name = self.file_line[self.col['name']]

        # Generate the sequence.
        self.relax.generic.sequence.add(self.run, res_num, res_name, select=int(self.file_line[self.col['select']]))


    def read_columnar_xh_vect(self):
        """Function for reading the XH unit vectors."""

        # The vector.
        xh_vect = eval(self.file_line[self.col['xh_vect']])
        if xh_vect:
            # Numeric array format.
            try:
                xh_vect = array(xh_vect, float64)
            except:
                raise RelaxError, "The XH unit vector " + self.file_line[self.col['xh_vect']] + " is invalid."

            # Set the vector.
            self.relax.generic.structure.set_vector(run=self.run, res=self.res_index, xh_vect=xh_vect)

        # The heteronucleus and proton names.
        ds.res[self.run][self.res_index].heteronuc = self.file_line[self.col['pdb_heteronuc']]
        ds.res[self.run][self.res_index].proton = self.file_line[self.col['pdb_proton']]


    def write_columnar_line(self, file=None, num=None, name=None, select=None, select_sim=None, data_set=None, nucleus=None, model=None, equation=None, params=None, param_set=None, s2=None, s2f=None, s2s=None, local_tm=None, te=None, tf=None, ts=None, rex=None, r=None, csa=None, chi2=None, i=None, f=None, g=None, h=None, warn=None, diff_type=None, diff_params=None, pdb=None, pdb_model=None, pdb_heteronuc=None, pdb_proton=None, xh_vect=None, ri_labels=None, remap_table=None, frq_labels=None, frq=None, ri=None, ri_error=None):
        """Function for printing a single line of the columnar formatted results."""

        # Residue number and name.
        file.write("%-4s %-5s " % (num, name))

        # Selected flag.
        if select_sim != None:
            file.write("%-9s " % select_sim)
        else:
            file.write("%-9s " % select)

        # Data set.
        file.write("%-9s " % data_set)

        # Nucleus.
        file.write("%-7s " % nucleus)

        # Model details.
        file.write("%-5s %-9s %-35s " % (model, equation, params))

        # Parameter set.
        file.write("%-10s " % param_set)

        # Parameters.
        file.write("%-25s " % s2)
        file.write("%-25s " % s2f)
        file.write("%-25s " % s2s)
        file.write("%-25s " % local_tm)
        file.write("%-25s " % te)
        file.write("%-25s " % tf)
        file.write("%-25s " % ts)
        file.write("%-25s " % rex)
        file.write("%-25s " % r)
        file.write("%-25s " % csa)

        # Minimisation results.
        file.write("%-25s %-8s %-8s %-8s %-8s %-45s " % (chi2, i, f, g, h, warn))

        # Diffusion parameters.
        file.write("%-10s " % diff_type)
        if diff_params:
            for i in xrange(len(diff_params)):
                file.write("%-25s " % diff_params[i])

        # PDB.
        file.write("%-40s " % pdb)
        file.write("%-10s " % pdb_model)
        file.write("%-15s " % pdb_heteronuc)
        file.write("%-15s " % pdb_proton)

        # XH unit vector.
        file.write("%-70s " % xh_vect)

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

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()


        # Header.
        #########

        # Diffusion parameters.
        diff_params = None
        if self.param_set != 'local_tm' and hasattr(ds, 'diff') and ds.diff.has_key(self.run):
            # Sphere.
            if ds.diff[self.run].type == 'sphere':
                diff_params = ['tm_(s)']

            # Spheroid.
            elif ds.diff[self.run].type == 'spheroid':
                diff_params = ['tm_(s)', 'Da_(1/s)', 'theta_(deg)', 'phi_(deg)']

            # Ellipsoid.
            elif ds.diff[self.run].type == 'ellipsoid':
                diff_params = ['tm_(s)', 'Da_(1/s)', 'Dr_(1/s)', 'alpha_(deg)', 'beta_(deg)', 'gamma_(deg)']

        # Relaxation data and errors.
        ri = []
        ri_error = []
        if hasattr(ds, 'num_ri'):
            for i in xrange(ds.num_ri[self.run]):
                ri.append('Ri_(' + ds.ri_labels[self.run][i] + "_" + ds.frq_labels[self.run][ds.remap_table[self.run][i]] + ")")
                ri_error.append('Ri_error_(' + ds.ri_labels[self.run][i] + "_" + ds.frq_labels[self.run][ds.remap_table[self.run][i]] + ")")

        # Write the header line.
        self.write_columnar_line(file=file, num='Num', name='Name', select='Selected', data_set='Data_set', nucleus='Nucleus', model='Model', equation='Equation', params='Params', param_set='Param_set', s2='S2', s2f='S2f', s2s='S2s', local_tm='Local_tm_(' + self.return_units('local_tm') + ')', te='te_(' + self.return_units('te') + ')', tf='tf_(' + self.return_units('tf') + ')', ts='ts_(' + self.return_units('ts') + ')', rex='Rex_(' + replace(self.return_units('rex'), ' ', '_') + ')', r='Bond_length_(' + self.return_units('r') + ')', csa='CSA_(' + self.return_units('csa') + ')', chi2='Chi-squared', i='Iter', f='f_count', g='g_count', h='h_count', warn='Warning', diff_type='Diff_type', diff_params=diff_params, pdb='PDB', pdb_model='PDB_model', pdb_heteronuc='PDB_heteronuc', pdb_proton='PDB_proton', xh_vect='XH_vector', ri_labels='Ri_labels', remap_table='Remap_table', frq_labels='Frq_labels', frq='Frequencies', ri=ri, ri_error=ri_error)


        # Values.
        #########

        # Nucleus.
        nucleus = self.relax.generic.nuclei.find_nucleus()

        # Diffusion parameters.
        diff_type = None
        diff_params = None
        if self.param_set != 'local_tm' and hasattr(ds, 'diff') and ds.diff.has_key(self.run):
            # Sphere.
            if ds.diff[self.run].type == 'sphere':
                diff_type = 'sphere'
                diff_params = [`ds.diff[self.run].tm`]

            # Spheroid.
            elif ds.diff[self.run].type == 'spheroid':
                diff_type = ds.diff[self.run].spheroid_type
                if diff_type == None:
                    diff_type = 'spheroid'
                diff_params = [`ds.diff[self.run].tm`, `ds.diff[self.run].Da`, `ds.diff[self.run].theta * 360 / (2.0 * pi)`, `ds.diff[self.run].phi * 360 / (2.0 * pi)`]

            # Ellipsoid.
            elif ds.diff[self.run].type == 'ellipsoid':
                diff_type = 'ellipsoid'
                diff_params = [`ds.diff[self.run].tm`, `ds.diff[self.run].Da`, `ds.diff[self.run].Dr`, `ds.diff[self.run].alpha * 360 / (2.0 * pi)`, `ds.diff[self.run].beta * 360 / (2.0 * pi)`, `ds.diff[self.run].gamma * 360 / (2.0 * pi)`]

        # PDB.
        pdb = None
        pdb_model = None
        if ds.pdb.has_key(self.run):
            pdb = ds.pdb[self.run].file_name
            pdb_model = ds.pdb[self.run].model

        # Relaxation data setup.
        try:
            ri_labels = replace(`ds.ri_labels[self.run]`, ' ', '')
            remap_table = replace(`ds.remap_table[self.run]`, ' ', '')
            frq_labels = replace(`ds.frq_labels[self.run]`, ' ', '')
            frq = replace(`ds.frq[self.run]`, ' ', '')
        except AttributeError:
            ri_labels = `None`
            remap_table = `None`
            frq_labels = `None`
            frq = `None`

        # Loop over the sequence.
        for i in xrange(len(ds.res[self.run])):
            # Reassign data structure.
            data = ds.res[self.run][i]

            # Model details.
            model = None
            if hasattr(data, 'model'):
                model = data.model

            equation = None
            if hasattr(data, 'equation'):
                equation = data.equation

            params = None
            if hasattr(data, 'params'):
                params = replace(`data.params`, ' ', '')

            # S2.
            s2 = None
            if hasattr(data, 's2') and data.s2 != None:
                s2 = data.s2 / self.return_conversion_factor('s2')
            s2 = `s2`

            # S2f.
            s2f = None
            if hasattr(data, 's2f') and data.s2f != None:
                s2f = data.s2f / self.return_conversion_factor('s2f')
            s2f = `s2f`

            # S2s.
            s2s = None
            if hasattr(data, 's2s') and data.s2s != None:
                s2s = data.s2s / self.return_conversion_factor('s2s')
            s2s = `s2s`

            # Local tm.
            local_tm = None
            if hasattr(data, 'local_tm') and data.local_tm != None:
                local_tm = data.local_tm / self.return_conversion_factor('local_tm')
            local_tm = `local_tm`

            # te.
            te = None
            if hasattr(data, 'te') and data.te != None:
                te = data.te / self.return_conversion_factor('te')
            te = `te`

            # tf.
            tf = None
            if hasattr(data, 'tf') and data.tf != None:
                tf = data.tf / self.return_conversion_factor('tf')
            tf = `tf`

            # ts.
            ts = None
            if hasattr(data, 'ts') and data.ts != None:
                ts = data.ts / self.return_conversion_factor('ts')
            ts = `ts`

            # Rex.
            rex = None
            if hasattr(data, 'rex') and data.rex != None:
                rex = data.rex / self.return_conversion_factor('rex')
            rex = `rex`

            # Bond length.
            r = None
            if hasattr(data, 'r') and data.r != None:
                r = data.r / self.return_conversion_factor('r')
            r = `r`

            # CSA.
            csa = None
            if hasattr(data, 'csa') and data.csa != None:
                csa = data.csa / self.return_conversion_factor('csa')
            csa = `csa`

            # Minimisation details.
            try:
                # Global minimisation results.
                if self.param_set == 'diff' or self.param_set == 'all':
                    chi2 = `ds.chi2[self.run]`
                    iter = ds.iter[self.run]
                    f = ds.f_count[self.run]
                    g = ds.g_count[self.run]
                    h = ds.h_count[self.run]
                    if type(ds.warning[self.run]) == str:
                        warn = replace(ds.warning[self.run], ' ', '_')
                    else:
                        warn = ds.warning[self.run]

                # Individual residue results.
                else:
                    chi2 = `data.chi2`
                    iter = data.iter
                    f = data.f_count
                    g = data.g_count
                    h = data.h_count
                    if type(data.warning) == str:
                        warn = replace(data.warning, ' ', '_')
                    else:
                        warn = data.warning

            # No minimisation details.
            except:
                chi2 = None
                iter = None
                f = None
                g = None
                h = None
                warn = None

            # XH vector.
            xh_vect = None
            if hasattr(data, 'xh_vect'):
                xh_vect = replace(`data.xh_vect.tolist()`, ' ', '')

            # Heteronucleus and proton names.
            heteronuc = None
            proton = None
            if hasattr(data, 'heteronuc'):
                heteronuc = data.heteronuc
                proton = data.proton

            # Relaxation data and errors.
            ri = []
            ri_error = []
            if hasattr(ds, 'num_ri'):
                for i in xrange(ds.num_ri[self.run]):
                    try:
                        # Find the residue specific data corresponding to i.
                        index = None
                        for j in xrange(data.num_ri):
                            if data.ri_labels[j] == ds.ri_labels[self.run][i] and data.frq_labels[data.remap_table[j]] == ds.frq_labels[self.run][ds.remap_table[self.run][i]]:
                                index = j

                        # Data exists for this data type.
                        ri.append(`data.relax_data[index]`)
                        ri_error.append(`data.relax_error[index]`)

                    # No data exists for this data type.
                    except:
                        ri.append(None)
                        ri_error.append(None)

            # Write the line.
            self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='value', nucleus=nucleus, model=model, equation=equation, params=params, param_set=self.param_set, s2=s2, s2f=s2f, s2s=s2s, local_tm=local_tm, te=te, tf=tf, ts=ts, rex=rex, r=r, csa=csa, chi2=chi2, i=iter, f=f, g=g, h=h, warn=warn, diff_type=diff_type, diff_params=diff_params, pdb=pdb, pdb_model=pdb_model, pdb_heteronuc=heteronuc, pdb_proton=proton, xh_vect=xh_vect, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Errors.
        #########

        # Only invoke this section if errors exist.
        if self.has_errors():
            # Diffusion parameters.
            diff_params = None
            if self.param_set != 'local_tm' and hasattr(ds, 'diff') and ds.diff.has_key(self.run):
                # Sphere.
                if ds.diff[self.run].type == 'sphere':
                    diff_params = [None]

                # Spheroid.
                elif ds.diff[self.run].type == 'spheroid':
                    diff_params = [None, None, None, None]

                # Ellipsoid.
                elif ds.diff[self.run].type == 'ellipsoid':
                    diff_params = [None, None, None, None, None, None]

                # Diffusion parameter errors.
                if self.param_set == 'diff' or self.param_set == 'all':
                    # Sphere.
                    if ds.diff[self.run].type == 'sphere' and hasattr(ds.diff[self.run], 'tm_err'):
                        diff_params = [`ds.diff[self.run].tm_err`]

                    # Spheroid.
                    elif ds.diff[self.run].type == 'spheroid' and hasattr(ds.diff[self.run], 'tm_err'):
                        diff_params = [`ds.diff[self.run].tm_err`, `ds.diff[self.run].Da_err`, `ds.diff[self.run].theta_err * 360 / (2.0 * pi)`, `ds.diff[self.run].phi_err * 360 / (2.0 * pi)`]

                    # Ellipsoid.
                    elif ds.diff[self.run].type == 'ellipsoid' and hasattr(ds.diff[self.run], 'tm_err'):
                        diff_params = [`ds.diff[self.run].tm_err`, `ds.diff[self.run].Da_err`, `ds.diff[self.run].Dr_err`, `ds.diff[self.run].alpha_err * 360 / (2.0 * pi)`, `ds.diff[self.run].beta_err * 360 / (2.0 * pi)`, `ds.diff[self.run].gamma_err * 360 / (2.0 * pi)`]

            # Loop over the sequence.
            for i in xrange(len(ds.res[self.run])):
                # Reassign data structure.
                data = ds.res[self.run][i]

                # Model details.
                model = None
                if hasattr(data, 'model'):
                    model = data.model

                equation = None
                if hasattr(data, 'equation'):
                    equation = data.equation

                params = None
                if hasattr(data, 'params'):
                    params = replace(`data.params`, ' ', '')

                # S2.
                s2 = None
                if hasattr(data, 's2_err') and data.s2_err != None:
                    s2 = data.s2_err / self.return_conversion_factor('s2')
                s2 = `s2`

                # S2f.
                s2f = None
                if hasattr(data, 's2f_err') and data.s2f_err != None:
                    s2f = data.s2f_err / self.return_conversion_factor('s2f')
                s2f = `s2f`

                # S2s.
                s2s = None
                if hasattr(data, 's2s_err') and data.s2s_err != None:
                    s2s = data.s2s_err / self.return_conversion_factor('s2s')
                s2s = `s2s`

                # Local tm.
                local_tm = None
                if hasattr(data, 'local_tm_err') and data.local_tm_err != None:
                    local_tm = data.local_tm_err / self.return_conversion_factor('local_tm')
                local_tm = `local_tm`

                # te.
                te = None
                if hasattr(data, 'te_err') and data.te_err != None:
                    te = data.te_err / self.return_conversion_factor('te')
                te = `te`

                # tf.
                tf = None
                if hasattr(data, 'tf_err') and data.tf_err != None:
                    tf = data.tf_err / self.return_conversion_factor('tf')
                tf = `tf`

                # ts.
                ts = None
                if hasattr(data, 'ts_err') and data.ts_err != None:
                    ts = data.ts_err / self.return_conversion_factor('ts')
                ts = `ts`

                # Rex.
                rex = None
                if hasattr(data, 'rex_err') and data.rex_err != None:
                    rex = data.rex_err / self.return_conversion_factor('rex')
                rex = `rex`

                # Bond length.
                r = None
                if hasattr(data, 'r_err') and data.r_err != None:
                    r = data.r_err / self.return_conversion_factor('r')
                r = `r`

                # CSA.
                csa = None
                if hasattr(data, 'csa_err') and data.csa_err != None:
                    csa = data.csa_err / self.return_conversion_factor('csa')
                csa = `csa`

                # Relaxation data and errors.
                ri = []
                ri_error = []
                for i in xrange(ds.num_ri[self.run]):
                    ri.append(None)
                    ri_error.append(None)

                # XH vector.
                xh_vect = None
                if hasattr(data, 'xh_vect'):
                    xh_vect = replace(`data.xh_vect.tolist()`, ' ', '')

                # Write the line.
                self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='error', nucleus=nucleus, model=model, equation=equation, params=params, param_set=self.param_set, s2=s2, s2f=s2f, s2s=s2s, local_tm=local_tm, te=te, tf=tf, ts=ts, rex=rex, r=r, csa=csa, diff_type=diff_type, diff_params=diff_params, pdb=pdb, pdb_model=pdb_model, pdb_heteronuc=heteronuc, pdb_proton=proton, xh_vect=xh_vect, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Simulation values.
        ####################

        # Only invoke this section if simulations have been setup.
        if hasattr(ds, 'sim_state') and ds.sim_state[self.run]:
            # Loop over the simulations.
            for i in xrange(ds.sim_number[self.run]):
                # Diffusion parameters.
                diff_params = None
                if self.param_set != 'local_tm' and hasattr(ds, 'diff') and ds.diff.has_key(self.run):
                    # Diffusion parameter simulation values.
                    if self.param_set == 'diff' or self.param_set == 'all':
                        # Sphere.
                        if ds.diff[self.run].type == 'sphere':
                            diff_params = [`ds.diff[self.run].tm_sim[i]`]

                        # Spheroid.
                        elif ds.diff[self.run].type == 'spheroid':
                            diff_params = [`ds.diff[self.run].tm_sim[i]`, `ds.diff[self.run].Da_sim[i]`, `ds.diff[self.run].theta_sim[i] * 360 / (2.0 * pi)`, `ds.diff[self.run].phi_sim[i] * 360 / (2.0 * pi)`]

                        # Ellipsoid.
                        elif ds.diff[self.run].type == 'ellipsoid':
                            diff_params = [`ds.diff[self.run].tm_sim[i]`, `ds.diff[self.run].Da_sim[i]`, `ds.diff[self.run].Dr_sim[i]`, `ds.diff[self.run].alpha_sim[i] * 360 / (2.0 * pi)`, `ds.diff[self.run].beta_sim[i] * 360 / (2.0 * pi)`, `ds.diff[self.run].gamma_sim[i] * 360 / (2.0 * pi)`]

                    # No simulation values.
                    else:
                        # Sphere.
                        if ds.diff[self.run].type == 'sphere':
                            diff_params = [None]

                        # Spheroid.
                        elif ds.diff[self.run].type == 'spheroid':
                            diff_params = [None, None, None, None]

                        # Ellipsoid.
                        elif ds.diff[self.run].type == 'ellipsoid':
                            diff_params = [None, None, None, None, None, None]

                # Loop over the sequence.
                for j in xrange(len(ds.res[self.run])):
                    # Reassign data structure.
                    data = ds.res[self.run][j]

                    # Model details.
                    model = None
                    if hasattr(data, 'model'):
                        model = data.model

                    equation = None
                    if hasattr(data, 'equation'):
                        equation = data.equation

                    params = None
                    if hasattr(data, 'params'):
                        params = replace(`data.params`, ' ', '')

                    # Selected simulation.
                    if self.param_set == 'diff' or self.param_set == 'all':
                        select_sim = ds.select_sim[self.run][i]
                    else:
                        select_sim = data.select_sim[i]

                    # S2.
                    s2 = None
                    if hasattr(data, 's2_sim') and data.s2_sim[i] != None:
                        s2 = data.s2_sim[i] / self.return_conversion_factor('s2')
                    s2 = `s2`

                    # S2f.
                    s2f = None
                    if hasattr(data, 's2f_sim') and data.s2f_sim[i] != None:
                        s2f = data.s2f_sim[i] / self.return_conversion_factor('s2f')
                    s2f = `s2f`

                    # S2s.
                    s2s = None
                    if hasattr(data, 's2s_sim') and data.s2s_sim[i] != None:
                        s2s = data.s2s_sim[i] / self.return_conversion_factor('s2s')
                    s2s = `s2s`

                    # Local tm.
                    local_tm = None
                    if hasattr(data, 'local_tm_sim') and data.local_tm_sim[i] != None:
                        local_tm = data.local_tm_sim[i] / self.return_conversion_factor('local_tm')
                    local_tm = `local_tm`

                    # te.
                    te = None
                    if hasattr(data, 'te_sim') and data.te_sim[i] != None:
                        te = data.te_sim[i] / self.return_conversion_factor('te')
                    te = `te`

                    # tf.
                    tf = None
                    if hasattr(data, 'tf_sim') and data.tf_sim[i] != None:
                        tf = data.tf_sim[i] / self.return_conversion_factor('tf')
                    tf = `tf`

                    # ts.
                    ts = None
                    if hasattr(data, 'ts_sim') and data.ts_sim[i] != None:
                        ts = data.ts_sim[i] / self.return_conversion_factor('ts')
                    ts = `ts`

                    # Rex.
                    rex = None
                    if hasattr(data, 'rex_sim') and data.rex_sim[i] != None:
                        rex = data.rex_sim[i] / self.return_conversion_factor('rex')
                    rex = `rex`

                    # Bond length.
                    r = None
                    if hasattr(data, 'r_sim') and data.r_sim[i] != None:
                        r = data.r_sim[i] / self.return_conversion_factor('r')
                    r = `r`

                    # CSA.
                    csa = None
                    if hasattr(data, 'csa_sim') and data.csa_sim[i] != None:
                        csa = data.csa_sim[i] / self.return_conversion_factor('csa')
                    csa = `csa`

                    # Minimisation details.
                    try:
                        # Global minimisation results.
                        if self.param_set == 'diff' or self.param_set == 'all':
                            chi2 = `ds.chi2_sim[self.run][i]`
                            iter = ds.iter_sim[self.run][i]
                            f = ds.f_count_sim[self.run][i]
                            g = ds.g_count_sim[self.run][i]
                            h = ds.h_count_sim[self.run][i]
                            if type(ds.warning_sim[self.run][i]) == str:
                                warn = replace(ds.warning_sim[self.run][i], ' ', '_')
                            else:
                                warn = ds.warning_sim[self.run][i]

                        # Individual residue results.
                        else:
                            chi2 = `data.chi2_sim[i]`
                            iter = data.iter_sim[i]
                            f = data.f_count_sim[i]
                            g = data.g_count_sim[i]
                            h = data.h_count_sim[i]
                            if type(data.warning_sim[i]) == str:
                                warn = replace(data.warning_sim[i], ' ', '_')
                            else:
                                warn = data.warning_sim[i]

                    # No minimisation details.
                    except AttributeError:
                        chi2 = None
                        iter = None
                        f = None
                        g = None
                        h = None
                        warn = None

                    # Relaxation data and errors.
                    ri = []
                    ri_error = []
                    if hasattr(ds, 'num_ri'):
                        for k in xrange(ds.num_ri[self.run]):
                            try:
                                # Find the residue specific data corresponding to k.
                                index = None
                                for l in xrange(data.num_ri):
                                    if data.ri_labels[l] == ds.ri_labels[self.run][k] and data.frq_labels[data.remap_table[l]] == ds.frq_labels[self.run][ds.remap_table[self.run][k]]:
                                        index = l

                                # Data exists for this data type.
                                ri.append(`data.relax_sim_data[i][index]`)
                                ri_error.append(`data.relax_error[index]`)

                            # No data exists for this data type.
                            except:
                                ri.append(None)
                                ri_error.append(None)

                    # XH vector.
                    xh_vect = None
                    if hasattr(data, 'xh_vect'):
                        xh_vect = replace(`data.xh_vect.tolist()`, ' ', '')

                    # Write the line.
                    self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, select_sim=select_sim, data_set='sim_'+`i`, nucleus=nucleus, model=model, equation=equation, params=params, param_set=self.param_set, s2=s2, s2f=s2f, s2s=s2s, local_tm=local_tm, te=te, tf=tf, ts=ts, rex=rex, r=r, csa=csa, chi2=chi2, i=iter, f=f, g=g, h=h, warn=warn, diff_type=diff_type, diff_params=diff_params, pdb=pdb, pdb_model=pdb_model, pdb_heteronuc=heteronuc, pdb_proton=proton, xh_vect=xh_vect, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)
