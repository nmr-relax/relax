###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
"""Determination of relative stereochemistry in organic molecules.

The analysis is preformed by using multiple ensembles of structures, randomly sampled from a given
set of structures.  The discrimination is performed by comparing the sets of ensembles using NOE
violations and RDC Q-factors.

This script is split into multiple stages:

    1.  The random sampling of the snapshots to generate the N ensembles (NUM_ENS, usually 10,000 to
    100,000) of M members (NUM_MODELS, usually ~10).  The original snapshot files are expected to be
    named the SNAPSHOT_DIR + CONFIG + a number from SNAPSHOT_MIN to SNAPSHOT_MAX + ".pdb", e.g.
    "snapshots/R647.pdb".  The ensembles will be placed into the "ensembles" directory.

    2.  The NOE violation analysis.

    3.  The superimposition of ensembles.  For each ensemble, Molmol is used for superimposition
    using the fit to first algorithm.  The superimposed ensembles will be placed into the
    "ensembles_superimposed" directory.  This stage is not necessary for the NOE analysis.

    4.  The RDC Q-factor analysis.

    5.  Generation of Grace graphs.
"""

# Python module imports.
from os import F_OK, access, popen3, sep
from random import randint
from re import search
from string import split
import sys

# relax module imports.
from generic_fns import pipes
from generic_fns.selection import spin_loop
from physical_constants import dipolar_constant, g1H, g13C
from relax_io import mkdir_nofail



class Stereochem_analysis:
    """Class for performing the relative stereochemistry analysis."""

    def __init__(self, stage=1, num_ens=10000, num_models=10, configs=None, snapshot_dir='snapshots', snapshot_min=None, snapshot_max=None, pseudo=None, noe_file=None, rdc_name=None, rdc_file=None, rdc_spin_id_col=None, rdc_mol_name_col=None, rdc_res_num_col=None, rdc_res_name_col=None, rdc_spin_num_col=None, rdc_spin_name_col=None, rdc_data_col=None, rdc_error_col=None, bond_length=None, log=None, bucket_num=200, lower_lim_noe=0.0, upper_lim_noe=600.0, lower_lim_rdc=0.0, upper_lim_rdc=1.0):
        """Set up the analysis."""

        # Store all the args.
        self.stage=stage
        self.num_ens=num_ens
        self.num_models=num_models
        self.configs=configs
        self.snapshot_dir=snapshot_dir
        self.snapshot_min=snapshot_min
        self.snapshot_max=snapshot_max
        self.pseudo=pseudo
        self.noe_file=noe_file
        self.rdc_name=rdc_name
        self.rdc_file=rdc_file
        self.rdc_spin_id_col=rdc_spin_id_col
        self.rdc_mol_name_col=rdc_mol_name_col
        self.rdc_res_num_col=rdc_res_num_col
        self.rdc_res_name_col=rdc_res_name_col
        self.rdc_spin_num_col=rdc_spin_num_col
        self.rdc_spin_name_col=rdc_spin_name_col
        self.rdc_data_col=rdc_data_col
        self.rdc_error_col=rdc_error_col
        self.bond_length=bond_length
        self.log=log
        self.bucket_num=bucket_num
        self.lower_lim_noe=lower_lim_noe
        self.upper_lim_noe=upper_lim_noe
        self.lower_lim_rdc=lower_lim_rdc
        self.upper_lim_rdc=upper_lim_rdc

        # Create a directory for log files.
        if LOG:
            mkdir_nofail("logs")


    def run(self):
        """Execute the given stage of the analysis."""

        # Sampling of snapshots.
        if STAGE == 1:
            self.sample()

        # NOE violation analysis.
        elif STAGE == 2:
            self.noe_viol()

        # Ensemble superimposition.
        elif STAGE == 3:
            self.superimpose()

        # RDC Q-factor analysis.
        elif STAGE == 4:
            self.rdc_analysis()

        # Grace plot creation.
        elif STAGE == 5:
            self.grace_plots()


    def generate_distribution(self, values, lower=0.0, upper=200.0, inc=None):
        """Create the distribution data structure."""

        # The bin width.
        bin_width = (upper - lower)/float(inc)

        # Init the dist object.
        dist = []
        for i in range(inc):
            dist.append([bin_width*i+lower, 0])

        # Loop over the values.
        for val in values:
            # The bin.
            bin = int((val - lower)/bin_width)

            # Outside of the limits.
            if bin < 0 or bin >= inc:
                print("Outside of the limits: '%s'" % val)
                continue

            # Increment the count.
            dist[bin][1] = dist[bin][1] + 1

        # Convert the counts to frequencies.
        total_pr = 0.0
        for i in range(inc):
            dist[i][1] = dist[i][1] / float(len(values))
            total_pr = total_pr + dist[i][1]

        print("Total Pr: %s" % total_pr)

        # Return the dist.
        return dist


    def grace_plots(self):
        """Generate grace plots of the results."""

        # NOE violations.
        if access("NOE_viol_" + CONFIGS[0] + "_sorted", F_OK):
            # Print out.
            print("Generating NOE violation Grace plots.")

            # Open the output files.
            grace_curve = open("NOE_viol_curve.agr", 'w')
            grace_dist = open("NOE_viol_dist.agr", 'w')

            # S-curve header.
            colours = [4, 2]    # Blue and red.
            grace_curve.write("@version 50121\n")
            grace_curve.write("@page size 842, 595\n")    # A4.
            grace_curve.write("@with g0\n")
            grace_curve.write("@    world 0, 0, %s, 200\n" % NUM_ENS)
            grace_curve.write("@    view 0.150000, 0.150000, 1.28, 0.85\n")
            grace_curve.write("@    title \"NOE violation comparison\"\n")
            grace_curve.write("@    subtitle \"%s ensembles of %s\"\n" % (NUM_ENS, NUM_MODELS))
            grace_curve.write("@    xaxis  label \"Ensemble (sorted)\"\n")
            grace_curve.write("@    yaxis  label \"NOE violation (Angstrom\S2\N)\"\n")
            grace_curve.write("@    legend 0.3, 0.8\n")
            for i in range(len(CONFIGS)):
                grace_curve.write("@    s%s line color %s\n" % (i, colours[i]))
                grace_curve.write("@    s%s legend \"%s\"\n" % (i, CONFIGS[i]))

            # Distribution header.
            colours = [4, 2]    # Blue and red.
            grace_dist.write("@version 50121\n")
            grace_dist.write("@page size 842, 595\n")    # A4.
            grace_dist.write("@with g0\n")
            grace_dist.write("@    world 0, 0, 200, 0.2\n")
            grace_dist.write("@    view 0.150000, 0.150000, 1.28, 0.85\n")
            grace_dist.write("@    title \"NOE violation comparison\"\n")
            grace_dist.write("@    subtitle \"%s ensembles of %s\"\n" % (NUM_ENS, NUM_MODELS))
            grace_dist.write("@    xaxis  label \"NOE violation (Angstrom\S2\N)\"\n")
            grace_dist.write("@    yaxis  label \"Frequency\"\n")
            grace_dist.write("@    legend 1.1, 0.8\n")
            for i in range(len(CONFIGS)):
                grace_dist.write("@    s%s symbol 1\n" % i)
                grace_dist.write("@    s%s symbol size 0.5\n" % i)
                grace_dist.write("@    s%s symbol color %s\n" % (i, colours[i]))
                grace_dist.write("@    s%s line linestyle 3\n" % i)
                grace_dist.write("@    s%s line color %s\n" % (i, colours[i]))
                grace_dist.write("@    s%s legend \"%s\"\n" % (i, CONFIGS[i]))

            # Loop over the configurations.
            for i in range(len(CONFIGS)):
                # Header.
                grace_curve.write("@target G0.S"+repr(i)+"\n@type xy\n")
                grace_dist.write("@target G0.S"+repr(i)+"\n@type xy\n")

                # Open the results file and read the data.
                file = open("NOE_viol_" + CONFIGS[i] + "_sorted")
                lines = file.readlines()
                file.close()

                # Loop over the ensembles and extract the NOE violation.
                noe_viols = []
                for i in range(1, len(lines)):
                    # Extract the violation.
                    viol = float(split(lines[i])[1])
                    noe_viols.append(viol)

                    # Write the data.
                    grace_curve.write("%-8s%-30s\n" % (i, viol))

                # Calculate the R distribution.
                dist = self.generate_distribution(noe_viols, inc=BUCKET_NUM, upper=UPPER_LIM_NOE, lower=LOWER_LIM_NOE)

                # Loop over the distribution bins.
                for i in range(len(dist)):
                    # Write the data.
                    grace_dist.write("%s %s\n" % (dist[i][0], dist[i][1]))

                # End of data.
                grace_curve.write("&\n")
                grace_dist.write("&\n")

            # Close the files.
            grace_curve.close()
            grace_dist.close()

        # RDC Q-factors.
        if access("Q_factors_" + CONFIGS[0] + "_sorted", F_OK):
            # Print out.
            print("Generating RDC Q-factor Grace plots.")

            # Open the Grace output files.
            grace_curve = open("RDC_%s_curve.agr" % RDC_NAME, 'w')
            grace_dist = open("RDC_%s_dist.agr" % RDC_NAME, 'w')

            # S-curve header.
            colours = [4, 2]    # Blue and red.
            grace_curve.write("@version 50121\n")
            grace_curve.write("@page size 842, 595\n")    # A4.
            grace_curve.write("@with g0\n")
            grace_curve.write("@    world 0, 0, %s, 2\n" % NUM_ENS)
            grace_curve.write("@    view 0.150000, 0.150000, 1.28, 0.85\n")
            grace_curve.write("@    title \"%s RDC Q-factor comparison\"\n" % RDC_NAME)
            grace_curve.write("@    subtitle \"%s ensembles of %s\"\n" % (NUM_ENS, NUM_MODELS))
            grace_curve.write("@    xaxis  label \"Ensemble (sorted)\"\n")
            grace_curve.write("@    yaxis  label \"%s RDC Q-factor (pales format)\"\n" % RDC_NAME)
            grace_curve.write("@    legend 0.3, 0.8\n")
            for i in range(len(CONFIGS)):
                grace_curve.write("@    s%s line color %s\n" % (i, colours[i]))
                grace_curve.write("@    s%s legend \"%s\"\n" % (i, CONFIGS[i]))

            # Distribution header.
            colours = [4, 2]    # Blue and red.
            grace_dist.write("@version 50121\n")
            grace_dist.write("@page size 842, 595\n")    # A4.
            grace_dist.write("@with g0\n")
            grace_dist.write("@    world 0, 0, 2, 0.2\n")
            grace_dist.write("@    view 0.150000, 0.150000, 1.28, 0.85\n")
            grace_dist.write("@    title \"%s RDC Q-factor comparison\"\n" % RDC_NAME)
            grace_dist.write("@    subtitle \"%s ensembles of %s\"\n" % (NUM_ENS, NUM_MODELS))
            grace_dist.write("@    xaxis  label \"%s RDC Q-factor (pales format)\"\n" % RDC_NAME)
            grace_dist.write("@    yaxis  label \"Frequency\"\n")
            grace_dist.write("@    legend 1.1, 0.8\n")
            for i in range(len(CONFIGS)):
                grace_dist.write("@    s%s symbol 1\n" % i)
                grace_dist.write("@    s%s symbol size 0.5\n" % i)
                grace_dist.write("@    s%s symbol color %s\n" % (i, colours[i]))
                grace_dist.write("@    s%s line linestyle 3\n" % i)
                grace_dist.write("@    s%s line color %s\n" % (i, colours[i]))
                grace_dist.write("@    s%s legend \"%s\"\n" % (i, CONFIGS[i]))

            # Loop over the configurations.
            for i in range(len(CONFIGS)):
                # Grace headers.
                grace_curve.write("@target G0.S%s\n@type xy\n" % i)
                grace_dist.write("@target G0.S%s\n@type xy\n" % i)

                # Open the results file and read the data.
                file = open("Q_factors_" + CONFIGS[i] + "_sorted")
                lines = file.readlines()
                file.close()

                # Loop over the Q-factors.
                values = []
                for i in range(1, len(lines)):
                    # Extract the violation.
                    value = float(split(lines[i])[1])
                    values.append(value)

                    # Write the data.
                    grace_curve.write("%-8s%-30s\n" % (i, value))

                # Calculate the R distribution.
                dist = self.generate_distribution(values, inc=BUCKET_NUM, upper=UPPER_LIM_RDC, lower=LOWER_LIM_RDC)

                # Loop over the distribution bins.
                for i in range(len(dist)):
                    # Write the data.
                    grace_dist.write("%s %s\n" % (dist[i][0], dist[i][1]))

                # End of data.
                grace_curve.write("&\n")
                grace_dist.write("&\n")

            # Close the files.
            grace_curve.close()
            grace_dist.close()


        # NOE-RDC correlation plot.
        if access("NOE_viol_" + CONFIGS[0] + "_sorted", F_OK) and access("Q_factors_" + CONFIGS[0] + "_sorted", F_OK):
            # Print out.
            print("Generating NOE-RDC correlation Grace plots.")

            # Open the Grace output files.
            grace_file = open("correlation_plot.agr", 'w')

            # Grace header.
            colours = [4, 2]    # Blue and red.
            grace_file.write("@version 50121\n")
            grace_file.write("@page size 842, 595\n")    # A4.
            grace_file.write("@with g0\n")
            grace_file.write("@    world 0, 0, %s, %s\n" % (noe_viols[-1]+10, values[-1]+0.1))
            grace_file.write("@    view 0.150000, 0.150000, 1.28, 0.85\n")
            grace_file.write("@    title \"Correlation plot - RDC vs. NOE\"\n")
            grace_file.write("@    subtitle \"%s ensembles of %s\"\n" % (NUM_ENS, NUM_MODELS))
            grace_file.write("@    xaxis  label \"NOE violation (Angstrom\S2\N)\"\n")
            grace_file.write("@    yaxis  label \"%s RDC Q-factors (pales format)\"\n" % RDC_NAME)
            grace_file.write("@    legend 1.1, 0.8\n")
            for i in range(len(CONFIGS)):
                grace_file.write("@    s%s symbol 9\n" % i)
                grace_file.write("@    s%s symbol size 0.24\n" % i)
                grace_file.write("@    s%s symbol color %s\n" % (i, colours[i]))
                grace_file.write("@    s%s symbol linewidth 0.5\n" % i)
                grace_file.write("@    s%s line type 0\n" % i)
                grace_file.write("@    s%s legend \"%s\"\n" % (i, CONFIGS[i]))

            # Grace data.
            for i in range(len(CONFIGS)):
                # Grace header.
                grace_file.write("@target G0.S%s\n@type xy\n" % i)

                # Open the NOE results file and read the data.
                file = open("NOE_viol_" + CONFIGS[i])
                noe_lines = file.readlines()
                file.close()

                # Open the RDC results file and read the data.
                file = open("Q_factors_" + CONFIGS[i])
                rdc_lines = file.readlines()
                file.close()

                # Loop over the data.
                for j in range(1, len(noe_lines)):
                    # Split the lines.
                    noe_viol = float(split(noe_lines[j])[1])
                    q_factor = float(split(rdc_lines[j])[1])

                    # Write the xy pair.
                    grace_file.write("%s %s\n" % (noe_viol, q_factor))

                # End of data.
                grace_file.write('&\n')


    def noe_viol(self):
        """NOE violation calculations."""

        # Redirect STDOUT to a log file.
        if LOG:
            sys.stdout = open("logs" + sep + "NOE_viol.log", 'w')

        # Create a directory for the save files.
        dir = "NOE_results"
        mkdir_nofail(dir=dir)

        # Loop over the configurations.
        for config in CONFIGS:
            # Print out.
            print("\n"*10 + "# Set up for config " + config + " #" + "\n")

            # Open the results file.
            out = open("NOE_viol_" + config, 'w')
            out_sorted = open("NOE_viol_" + config + "_sorted", 'w')
            out.write("%-20s%20s\n" % ("# Ensemble", "NOE_volation"))
            out_sorted.write("%-20s%20s\n" % ("# Ensemble", "NOE_volation"))

            # Create the data pipe.
            pipe.create("noe_viol_%s" % config, "N-state")

            # Read the first structure.
            structure.read_pdb("ensembles" + sep + config + "0.pdb", set_mol_name=config, set_model_num=range(1, NUM_MODELS+1), parser="internal")

            # Load all protons as the sequence.
            structure.load_spins("@H*", ave_pos=False)

            # Create the pseudo-atoms.
            for i in range(len(PSEUDO)):
                spin.create_pseudo(spin_name=PSEUDO[i][0], members=PSEUDO[i][1], averaging="linear")
            sequence.display()

            # Read the NOE list.
            noe.read_restraints(file=NOE_FILE)

            # Set up the N-state model.
            n_state_model.select_model(model="fixed")

            # Print out.
            print("\n"*2 + "# Set up complete #" + "\n"*10)

            # Loop over each ensemble.
            noe_viol = []
            for ens in range(NUM_ENS):
                # Print out the ensemble to both the log and screen.
                if LOG:
                    sys.stdout.write(config + repr(ens) + "\n")
                sys.stderr.write(config + repr(ens) + "\n")

                # Delete the old structures and rename the molecule.
                structure.delete()

                # Read the ensemble.
                structure.read_pdb("ensembles" + sep + config + repr(ens) + ".pdb", set_mol_name=config, set_model_num=range(1, NUM_MODELS+1), parser="internal")

                # Get the atomic positions.
                structure.get_pos(ave_pos=False)

                # Calculate the average NOE potential.
                calc()

                # Sum the violations.
                cdp.sum_viol = 0.0
                for i in range(len(cdp.ave_dist)):
                    if cdp.quad_pot[i][2]:
                        cdp.sum_viol = cdp.sum_viol + cdp.quad_pot[i][2]

                # Write out the NOE violation.
                noe_viol.append([cdp.sum_viol, ens])
                out.write("%-20i%30.15f\n" % (ens, cdp.sum_viol))

                # Save the state.
                results.write(file="%s_results_%s" % (config, ens), dir=dir, force=True)

            # Sort the NOE violations.
            noe_viol.sort()

            # Write the data.
            for i in range(len(noe_viol)):
                out_sorted.write("%-20i%20.15f\n" % (noe_viol[i][1], noe_viol[i][0]))


    def rdc_analysis(self):
        """Perform the RDC part of the analysis."""

        # Redirect STDOUT to a log file.
        if LOG:
            sys.stdout = open("logs" + sep + "RDC_%s_analysis.log" % RDC_NAME, 'w')

        # The dipolar constant.
        d = 3.0 / (2.0*pi) * dipolar_constant(g13C, g1H, BOND_LENGTH)

        # Create a directory for the save files.
        dir = "RDC_%s_results" % RDC_NAME
        mkdir_nofail(dir=dir)

        # Loop over the configurations.
        for config in CONFIGS:
            # Print out.
            print("\n"*10 + "# Set up for config " + config + " #" + "\n")

            # Open the results files.
            out = open("Q_factors_" + config, 'w')
            out_sorted = open("Q_factors_" + config + "_sorted", 'w')
            out.write("%-20s%20s%20s\n" % ("# Ensemble", "RDC_Q_factor(pales)", "RDC_Q_factor(standard)"))
            out_sorted.write("%-20s%20s\n" % ("# Ensemble", "RDC_Q_factor(pales)"))

            # Create the data pipe.
            pipe.create("rdc_analysis_%s" % config, "N-state")

            # Read the first structure.
            structure.read_pdb("ensembles_superimposed" + sep + config + "0.pdb", set_mol_name=config, set_model_num=range(1, NUM_MODELS+1), parser="internal")

            # Load all protons as the sequence.
            structure.load_spins("@H*", ave_pos=False)

            # Create the pseudo-atoms.
            for i in range(len(PSEUDO)):
                spin.create_pseudo(spin_name=PSEUDO[i][0], members=PSEUDO[i][1], averaging="linear")
            sequence.display()

            # Read the RDC data.
            rdc.read(align_id=RDC_FILE, file=RDC_FILE, spin_id_col=RDC_SPIN_ID_COL, mol_name_col=RDC_MOL_NAME_COL, res_num_col=RDC_RES_NUM_COL, res_name_col=RDC_RES_NAME_COL, spin_num_col=RDC_SPIN_NUM_COL, spin_name_col=RDC_SPIN_NAME_COL, data_col=RDC_DATA_COL, error_col=RDC_ERROR_COL)

            # Set the values needed to calculate the dipolar constant.
            value.set(BOND_LENGTH, "bond_length", spin_id="@H*")
            value.set(BOND_LENGTH, "bond_length", spin_id="@Q*")
            value.set("13C", "heteronucleus", spin_id="@H*")
            value.set("13C", "heteronucleus", spin_id="@Q*")
            value.set("1H", "proton", spin_id="@H*")
            value.set("1H", "proton", spin_id="@Q*")

            # Set up the model.
            n_state_model.select_model(model="fixed")

            # Print out.
            print("\n"*2 + "# Set up complete #" + "\n"*10)

            # Loop over each ensemble.
            q_factors = []
            for ens in range(NUM_ENS):
                # Print out the ensemble to both the log and screen.
                if LOG:
                    sys.stdout.write(config + repr(ens) + "\n")
                sys.stderr.write(config + repr(ens) + "\n")

                # Delete the old structures.
                structure.delete()

                # Read the ensemble.
                structure.read_pdb("ensembles_superimposed" + sep + config + repr(ens) + ".pdb", set_mol_name=config, set_model_num=range(1, NUM_MODELS+1), parser="internal")

                # Load the CH vectors for the H atoms.
                structure.vectors(spin_id="@H*", attached="*C*", ave=False)

                # Minimisation.
                #grid_search(inc=4)
                minimise("simplex", constraints=False)

                # Store and write out the Q-factors.
                q_factors.append([cdp.q_rdc, ens])
                out.write("%-20i%20.15f%20.15f\n" % (ens, cdp.q_rdc, cdp.q_rdc_norm2))

                # Calculate the alignment tensor in Hz, and store it for reference.
                cdp.align_tensor_Hz = d * cdp.align_tensors[0].A
                cdp.align_tensor_Hz_5D = d * cdp.align_tensors[0].A_5D

                # Save the state.
                results.write(file="%s_results_%s" % (config, ens), dir=dir, force=True)

            # Sort the NOE violations.
            q_factors.sort()

            # Write the data.
            for i in range(len(q_factors)):
                out_sorted.write("%-20i%20.15f\n" % (q_factors[i][1], q_factors[i][0]))


    def sample(self):
        """Generate the ensembles by random sampling of the snapshots."""

        # Create the directory for the ensembles, if needed.
        mkdir_nofail(dir="ensembles")

        # Loop over the configurations.
        for conf_index in range(len(CONFIGS)):
            # Loop over each ensemble.
            for ens in range(NUM_ENS):
                # Random sampling.
                rand = []
                for j in range(NUM_MODELS):
                    rand.append(randint(SNAPSHOT_MIN[conf_index], SNAPSHOT_MAX[conf_index]))

                # Print out.
                print("Generating ensemble %s%s from structures %s." % (CONFIGS[conf_index], ens, rand))

                # The file name.
                file_name = "ensembles" + sep + CONFIGS[conf_index] + repr(ens) + ".pdb"

                # Open the output file.
                out = open(file_name, 'w')

                # Header.
                out.write("REM Structures: " + repr(rand) + "\n")

                # Concatenation the files.
                for j in range(NUM_MODELS):
                    # The random file.
                    rand_name = SNAPSHOT_DIR[conf_index] + sep + CONFIGS[conf_index] + repr(rand[j]) + ".pdb"

                    # Append the file.
                    out.write(open(rand_name).read())

                # Close the file.
                out.close()


    def superimpose(self):
        """Superimpose the ensembles using fit to first in Molmol."""

        # Create the output directory.
        mkdir_nofail("ensembles_superimposed")

        # Logging turned on.
        if LOG:
            log = open("logs" + sep + "superimpose_molmol.stderr", 'w')
            sys.stdout = open("logs" + sep + "superimpose.log", 'w')

        # Loop over S and R.
        for config in ["R", "S"]:
            # Loop over each ensemble.
            for ens in range(NUM_ENS):
                # The file names.
                file_in = "ensembles" + sep + config + repr(ens) + ".pdb"
                file_out = "ensembles_superimposed" + sep + config + repr(ens) + ".pdb"

                # Print out.
                sys.stderr.write("Superimposing %s with Molmol, output to %s.\n" % (file_in, file_out))
                if LOG:
                    log.write("\n\n\nSuperimposing %s with Molmol, output to %s.\n" % (file_in, file_out))

                # Failure handling (if a failure occurred and this is rerun, skip all existing files).
                if access(file_out, F_OK):
                    continue

                # Open the Molmol pipe.
                stdin, stdout, stderr = popen3("molmol -t -f -", 'w', 0)

                # Init all.
                stdin.write("InitAll yes\n")

                # Read the PDB.
                stdin.write("ReadPdb " + file_in + "\n")

                # Fitting to mean.
                stdin.write("Fit to_first 'selected'\n")
                stdin.write("Fit to_mean 'selected'\n")

                # Write the result.
                stdin.write("WritePdb " + file_out + "\n")

                # End Molmol.
                stdin.close()

                # Get STDOUT and STDERR.
                sys.stdout.write(stdout.read())
                if LOG:
                    log.write(stderr.read())

                # Close the pipe.
                stdout.close()
                stderr.close()

                # Open the superimposed file in relax.
                reset()
                pipe.create('out', 'N-state')
                structure.read_pdb(file_out, parser="internal")

                # Fix the retarded MOLMOL proton naming.
                for model in cdp.structure.structural_data:
                    # Alias.
                    mol = model.mol[0]

                    # Loop over all atoms.
                    for i in range(len(mol.atom_name)):
                        # A proton.
                        if search('H', mol.atom_name[i]):
                            mol.atom_name[i] = mol.atom_name[i][1:] + mol.atom_name[i][0]

                # Replace the superimposed file.
                structure.write_pdb(config + repr(ens) + ".pdb", dir="ensembles_superimposed", force=True)
