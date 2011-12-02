###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""The full frame order analysis."""


# Python module imports.
from math import pi
from os import sep
from random import gauss, uniform
from time import localtime

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.angles import wrap_angles
from prompt.interpreter import Interpreter


class Frame_order_analysis:
    def __init__(self, pipe_name, grid_incs=11, random_samples=100):
        """Perform the full frame order analysis.

        @param pipe_name:           The name of the data pipe containing all of the alignment data.
        @type pipe_name:            str
        @keyword grid_incs:         The number of grid increments to use in the grid search of certain models.
        @type grid_incs:            int
        @keyword random_samples:    The number of randomisations to perform to search for the global minimum.
        @type random_samples:       int
        """

        # Store the args.
        ds.orig_pipe = pipe_name
        ds.N = random_samples

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)


        # First block, cone-less.
        #########################

        # Start with the rigid frame order model grid search and simplex optimisation.
        self.model_opt(model='rigid', var_name='rigid', grid_incs=grid_incs)

        # Free rotor model optimisation.
        self.model_opt(model='free rotor', var_name='free_rotor', grid_incs=[grid_incs, grid_incs, grid_incs, grid_incs])

        # Rotor model optimisation.
        self.model_opt(model='rotor', var_name='rotor', grid_incs=[6, 6, 6, 6, 6, 6, 10])


        # Second block, isotropic cones.
        ################################

        # Torsionless isotropic cone model optimisation.
        self.model_opt(model='iso cone, torsionless', var_name='iso_cone_torsionless', grid_incs=[None, None, grid_incs, grid_incs, grid_incs])

        # Free rotor isotropic cone model optimisation.
        self.model_opt(model='iso cone, free rotor', var_name='iso_cone_free_rotor', grid_incs=[None, None, grid_incs, grid_incs, grid_incs])

        # Isotropic cone model optimisation.
        self.model_opt(model='iso cone', var_name='iso_cone', grid_incs=[None, None, None, None, None, None, grid_incs, grid_incs])


        # Third block, pseudo-ellipses.
        ###############################

        # Free rotor isotropic cone model optimisation.
        self.model_opt(model='pseudo-ellipse, free rotor', var_name='pseudo_ellipse_free_rotor')

        # Torsionless isotropic cone model optimisation.
        self.model_opt(model='pseudo-ellipse, torsionless', var_name='pseudo_ellipse_torsionless')

        # Isotropic cone model optimisation.
        self.model_opt(model='pseudo-ellipse', var_name='pseudo_ellipse')


        # Save the program state.
        self.interpreter.state.save('frame_order', force=True)


    def copy_params(self, model=None):
        """Copy the parameters over from a simpler model."""

        # The free rotor isotropic cone model.
        if model == 'iso cone, free rotor':
            # The average position Euler angles from the free rotor model.
            cdp.ave_pos_beta  = ds[ds.pipe_free_rotor_best].ave_pos_beta
            cdp.ave_pos_gamma = ds[ds.pipe_free_rotor_best].ave_pos_gamma

            # Rotation axis from the free rotor model.
            cdp.axis_theta    = ds[ds.pipe_free_rotor_best].axis_theta
            cdp.axis_phi      = ds[ds.pipe_free_rotor_best].axis_phi

        # The torsionless isotropic cone model.
        elif model == 'iso cone, torsionless':
            # The average position Euler angles from the rotor model.
            cdp.ave_pos_beta  = ds[ds.pipe_rotor_best].ave_pos_beta
            cdp.ave_pos_gamma = ds[ds.pipe_rotor_best].ave_pos_gamma

        # The isotropic cone model.
        elif model == 'iso cone':
            # The average position Euler angles from the rotor model.
            cdp.ave_pos_alpha = ds[ds.pipe_rotor_best].ave_pos_alpha
            cdp.ave_pos_beta  = ds[ds.pipe_rotor_best].ave_pos_beta
            cdp.ave_pos_gamma = ds[ds.pipe_rotor_best].ave_pos_gamma

            # The eigenframe from the rotor model.
            cdp.eigen_alpha   = ds[ds.pipe_rotor_best].eigen_alpha
            cdp.eigen_beta    = ds[ds.pipe_rotor_best].eigen_beta
            cdp.eigen_gamma   = ds[ds.pipe_rotor_best].eigen_gamma

        # The pseudo-ellipse cone model.
        elif model == 'pseudo-ellipse, free rotor':
            # The average position Euler angles from the rotor model.
            cdp.ave_pos_alpha = ds[ds.pipe_iso_cone_free_rotor_best].ave_pos_alpha
            cdp.ave_pos_beta  = ds[ds.pipe_iso_cone_free_rotor_best].ave_pos_beta
            cdp.ave_pos_gamma = ds[ds.pipe_iso_cone_free_rotor_best].ave_pos_gamma

            # The eigenframe from the rotor model.
            cdp.eigen_beta    = ds[ds.pipe_iso_cone_free_rotor_best].axis_theta
            cdp.eigen_gamma   = ds[ds.pipe_iso_cone_free_rotor_best].axis_phi

            # The x and y cone angles from the free rotor isotropic cone angle.
            if ds[ds.pipe_iso_cone_free_rotor_best].cone_theta < 0.2:
                cdp.cone_theta_x = 1.0
                cdp.cone_theta_y = 1.0
            else:
                cdp.cone_theta_x = ds[ds.pipe_iso_cone_free_rotor_best].cone_theta
                cdp.cone_theta_y = ds[ds.pipe_iso_cone_free_rotor_best].cone_theta

        # The torsionless pseudo-ellipse cone model.
        elif model == 'pseudo-ellipse, torsionless':
            # The average position Euler angles from the rotor model.
            cdp.ave_pos_alpha = ds[ds.pipe_iso_cone_torsionless_best].ave_pos_alpha
            cdp.ave_pos_beta  = ds[ds.pipe_iso_cone_torsionless_best].ave_pos_beta
            cdp.ave_pos_gamma = ds[ds.pipe_iso_cone_torsionless_best].ave_pos_gamma

            # The eigenframe from the rotor model.
            cdp.eigen_beta    = ds[ds.pipe_iso_cone_torsionless_best].axis_theta
            cdp.eigen_gamma   = ds[ds.pipe_iso_cone_torsionless_best].axis_phi

            # The x and y cone angles from the torsionless isotropic cone angle.
            if ds[ds.pipe_iso_cone_torsionless_best].cone_theta < 0.2:
                cdp.cone_theta_x = 1.0
                cdp.cone_theta_y = 1.0
            else:
                cdp.cone_theta_x = ds[ds.pipe_iso_cone_torsionless_best].cone_theta
                cdp.cone_theta_y = ds[ds.pipe_iso_cone_torsionless_best].cone_theta

        # The pseudo-ellipse cone model.
        elif model == 'pseudo-ellipse':
            # The average position Euler angles from the rotor model.
            cdp.ave_pos_alpha = ds[ds.pipe_iso_cone_best].ave_pos_alpha
            cdp.ave_pos_beta  = ds[ds.pipe_iso_cone_best].ave_pos_beta
            cdp.ave_pos_gamma = ds[ds.pipe_iso_cone_best].ave_pos_gamma

            # The eigenframe from the rotor model.
            cdp.eigen_alpha   = ds[ds.pipe_iso_cone_best].eigen_alpha
            cdp.eigen_beta    = ds[ds.pipe_iso_cone_best].eigen_beta
            cdp.eigen_gamma   = ds[ds.pipe_iso_cone_best].eigen_gamma

            # The x and y cone angles from the isotropic cone angle.
            if ds[ds.pipe_iso_cone_best].cone_theta < 0.2:
                cdp.cone_theta_x = 1.0
                cdp.cone_theta_y = 1.0
            else:
                cdp.cone_theta_x = ds[ds.pipe_iso_cone_best].cone_theta
                cdp.cone_theta_y = ds[ds.pipe_iso_cone_best].cone_theta

            # The torsion angle restriction from the rotor model.
            cdp.cone_sigma_max     = ds[ds.pipe_rotor_best].cone_sigma_max


    def model_failure(self):
        """Check if the model has failed."""

        # Isotropic order parameter out of range.
        if hasattr(cdp, 'cone_s1') and (cdp.cone_s1 > 1.0 or cdp.cone_s1 < -0.125):
            return True

        # Isotropic cone angle out of range.
        if hasattr(cdp, 'cone_theta') and (cdp.cone_theta >= pi or cdp.cone_theta < 0.0):
            return True

        # Pseudo-ellipse cone angles out of range (0.001 instead of 0.0 because of truncation in the numerical integration).
        if hasattr(cdp, 'cone_theta_x') and (cdp.cone_theta_x >= pi or cdp.cone_theta_x < 0.001):
            return True
        if hasattr(cdp, 'cone_theta_y') and (cdp.cone_theta_y >= pi or cdp.cone_theta_y < 0.001):
            return True

        # Torsion angle out of range.
        if hasattr(cdp, 'cone_sigma_max') and (cdp.cone_sigma_max >= pi or cdp.cone_sigma_max < 0.0):
            return True

        # No failure.
        return False


    def model_opt(self, model=None, var_name=None, grid_incs=None):
        """Model optimisation."""

        # Print out.
        text = "# %s model #" % model
        print("\n\n\n\n\n" + "#"*len(text))
        print("%s" % text)
        print("#"*len(text) + "\n")

        # The pipe name.
        now = localtime()
        name = '%s (%i%02i%02i_%02i%02i%02i)' % (model, now[0], now[1], now[2], now[3], now[4], now[5])
        setattr(ds, 'pipe_%s' % var_name, name)

        # Create the data pipe by copying, and switch to it.
        self.interpreter.pipe.copy(ds.orig_pipe, name)
        self.interpreter.pipe.switch(name)

        # Select the Frame Order model.
        self.interpreter.frame_order.select_model(model=model)
        print("\nModel parameters:")
        for i in range(len(cdp.params)):
            print("    %s" % cdp.params[i])
        print

        # Copy parameters over from the other models.
        self.copy_params(model)

        # Grid search.
        if grid_incs:
            self.interpreter.grid_search(inc=grid_incs, constraints=False)

        # Minimise.
        self.interpreter.minimise('simplex', constraints=False)

        # Save the result.
        self.interpreter.results.write(dir=var_name, force=True)

        # Random sampling to better locate the minimum (skipping the rigid model).
        if model != 'rigid':
            self.random_sampling(model=model, var_name=var_name, parent_pipe=name)


    def random_sampling(self, model=None, var_name=None, parent_pipe=None):
        """Duplicate the model data, randomise certain parameters, and then re-optimise."""

        # Init the random pipe storage.
        name = 'pipe_' + var_name + '_rand'
        setattr(ds, name, [])
        pipe_list = getattr(ds, name)

        # Init the best data pipe info.
        best_chi2 = ds[parent_pipe].chi2
        best_pipe = parent_pipe

        # Loop over the samples.
        for i in range(ds.N):
            # Print out.
            text = "# Random sample %s." % i
            print("\n\n%s" % text)
            print("#"*len(text) + "\n")

            # A new data pipe.
            now = localtime()
            pipe_name = '%s, random sample %s (%i%02i%02i_%02i%02i%02i)' % (model, i, now[0], now[1], now[2], now[3], now[4], now[5])
            pipe_list.append(pipe_name)

            # Create the data pipe by copying the best one, and switch to it.
            self.interpreter.pipe.copy(best_pipe, pipe_name)
            self.interpreter.pipe.switch(pipe_name)

            # Average position randomisation (Gaussian).
            sigma = pi / 2.0
            cdp.ave_pos_alpha = wrap_angles(gauss(ds[parent_pipe].ave_pos_alpha, sigma), 0.0, 2.0*pi)
            cdp.ave_pos_beta  = wrap_angles(gauss(ds[parent_pipe].ave_pos_beta,  sigma), 0.0, 2.0*pi)
            cdp.ave_pos_gamma = wrap_angles(gauss(ds[parent_pipe].ave_pos_gamma, sigma), 0.0, 2.0*pi)

            # Eigenframe randomisation (Gaussian).
            sigma = pi
            if hasattr(cdp, 'eigen_alpha'):
                cdp.eigen_alpha = wrap_angles(gauss(ds[parent_pipe].eigen_alpha, sigma), 0.0, 2.0*pi)
                cdp.eigen_beta  = wrap_angles(gauss(ds[parent_pipe].eigen_beta,  sigma), 0.0, 2.0*pi)
                cdp.eigen_gamma = wrap_angles(gauss(ds[parent_pipe].eigen_gamma, sigma), 0.0, 2.0*pi)
            elif hasattr(cdp, 'axis_theta'):
                cdp.axis_theta  = wrap_angles(gauss(ds[parent_pipe].axis_theta,  sigma), 0.0, 2.0*pi)
                cdp.axis_phi    = wrap_angles(gauss(ds[parent_pipe].axis_phi,    sigma), 0.0, 2.0*pi)

            # Cone randomisation (uniform).
            if hasattr(cdp, 'cone_theta'):
                cdp.cone_theta     = uniform(0.0, pi)
            elif hasattr(cdp, 'cone_theta_x'):
                cdp.cone_theta_x   = uniform(0.0, pi)
                cdp.cone_theta_y   = uniform(0.0, pi)
            elif hasattr(cdp, 'cone_s1'):
                cdp.cone_s1        = uniform(-0.125, 1.0)
            if hasattr(cdp, 'cone_sigma_max'):
                cdp.cone_sigma_max = uniform(0.0, pi)

            # Minimise.
            self.interpreter.minimise('simplex', constraints=False)

            # Save the result.
            self.interpreter.results.write(dir=var_name+sep+'random_sample_%s'%i, force=True)

            # Model failure, so do no check for a better minimum.
            if self.model_failure():
                continue

            # Better minimum?
            if cdp.chi2 < best_chi2:
                best_chi2 = cdp.chi2
                best_pipe = pipe_name

        # Print out.
        print("\n\nThe original minimum is at:")
        print("    chi2: %s" % ds[parent_pipe].chi2)

        print("\nThe best minimum is:")
        print("    pipe_name: %s" % best_pipe)
        print("    chi2: %s" % best_chi2)

        # Set the best pipe.
        setattr(ds, 'pipe_' + var_name + '_best', best_pipe)
