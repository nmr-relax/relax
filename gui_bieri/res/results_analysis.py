###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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

# Python module imports.
from os import getcwd, listdir, sep
from re import search
from string import lower
import wx
import time
from string import replace
import sys
import os

# relax module imports.
from generic_fns.mol_res_spin import spin_loop



# create model-free results

def model_free_results(self):
        directory = str(self.resultsdir_r21_copy_2.GetValue()) + sep + 'final'
        pdbfile = str(self.structure_noe1.GetValue())

        #Read results
        pipename = 'Data_extraction ' + str(time.asctime(time.localtime()))
        pipe.create(pipename ,'mf')
        results.read()

        #create a table file

        #create file
        self.file = open(str(directory) + sep + 'Model-free_Results.txt', 'w')
        self.file.write('Data Extraction by relaxGUI, (C) 2009 Michael Bieri')
        self.file.write("\n")
        self.file.write("\n")
        "self.file.write(""Residue		Model	S2			Rex [1/s]		Te			Relaxation Parameters\n"")"
        self.file.write("\n")

        #loop over residues
        for spin, spin_id in spin_loop(return_id=True):
                    # The spin ID string.
                    spin_no = spin_id[spin_id.index(':')+1:spin_id.index('&')]
                    spin_res = spin_id[spin_id.index('&')+2:spin_id.index('@')]
                    self.file.write((spin_res) + " " + (spin_no))
                    # The spin is not selected.
                    if not spin.select:
                        self.file.write("\n")
                        continue
        
        
        # The model-free model.
                    if hasattr(spin, 'model'):
                        spin.model = spin.model[1:2]
                        self.file.write(""		"" + spin.model)
        
        
        # S2.
                    if  hasattr(spin, 's2'):
                        s2 = str(spin.s2)
                        s2_err = str(spin.s2_err)
                        if spin.s2 == None:
                                self.file.write("")
                        else:
                                self.file.write("	" + s2[0:5]+ " +/- " + s2_err[0:4])
        
        
        # Rex.
                    if hasattr(spin, 'rex'):
                        rex = str(spin.rex)
                        rex_err = str(spin.rex_err)
                        if spin.rex == None:
                                self.file.write("			")
                        else:
                                rex_eff = spin.rex * (int(spin.frq_labels[1]) * 1000000 * 2 * 3.14159)**2
                                rex = str(rex_eff)
                                rex_err_eff = spin.rex_err * (int(spin.frq_labels[1]) * 1000000 * 2 * 3.14159)**2
                                rex_err = str(rex_err_eff)
                                self.file.write("		" + rex[0:5]+ " +/- " + rex_err[0:4])
        
        
        # Te
                    if  hasattr(spin, 'te'):
                        if spin.te == None:
                                self.file.write("		")
                        else:
                                te_ps = spin.te * 1e-12
                                te = str(te_ps)
                                te_err = str(spin.te_err)
                                self.file.write("		" + te[0:5]+ " +/- " + te_err[0:4])
        
        
        
        # Parameters.
                    if hasattr(spin, 'params'):
                        self.file.write("			" + str(spin.params[0:len(spin.params)]))
                    else:
                        self.file.write("\\n")
                        continue
        
        
        
        # Start a new line.
                    self.file.write("\n")
        
        ##################################################################################################
        
        #Create Single Data Files
        	
        value.write(param='rex', file='rex.txt', dir=str(directory) + sep + 'final_results', force=True)
        value.write(param='s2', file='s2.txt', dir=str(directory) + sep + 'final_results', force=True)
        value.write(param='s2f', file='s2f.txt', dir=str(directory) + sep + 'final_results', force=True)
        value.write(param='s2s', file='s2s.txt', dir=str(directory) + sep + 'final_results', force=True)
        value.write(param='te', file='te.txt', dir=str(directory) + sep + 'final_results', force=True)
        value.write(param='tf', file='tf.txt', dir=str(directory) + sep + 'final_results',  force=True)
        value.write(param='ts', file='ts.txt', dir=str(directory) + sep + 'final_results', force=True)
        value.write(param='rex', file='rex.txt', dir=str(directory) + sep + 'final_results', force=True)
        value.write(param='r', file='r.txt', dir=str(directory) + sep + 'final_results', force=True)
        value.write(param='rex', file='rex.txt', dir=str(directory) + sep + 'final_results', force=True)
        value.write(param='csa', file='csa.txt', dir=str(directory) + sep + 'final_results', force=True)
        value.write(param='rex', file='rex.txt', dir=str(directory) + sep + 'final_results', force=True)
        value.write(param='local_tm', file='local_tm.txt', dir=str(directory) + sep + 'final_results', force=True)
        
        ##################################################################################################
        
        #Create Grace Plots
        
        grace.write(x_data_type='spin', y_data_type='s2', file='s2.agr', dir=str(directory) + sep + 'grace', force=True)
        grace.write(x_data_type='spin', y_data_type='te', file='te.agr', dir=str(directory) + sep + 'grace', force=True)
        grace.write(x_data_type='spin', y_data_type='s2f', file='s2f.agr', dir=str(directory) + sep + 'grace', force=True)
        grace.write(x_data_type='spin', y_data_type='s2s', file='s2s.agr', dir=str(directory) + sep + 'grace', force=True)
        grace.write(x_data_type='spin', y_data_type='ts', file='ts.agr', dir=str(directory) + sep + 'grace', force=True)
        grace.write(x_data_type='spin', y_data_type='tf', file='tf.agr', dir=str(directory) + sep + 'grace', force=True)
        grace.write(x_data_type='spin', y_data_type='csa', file='csa.agr', dir=str(directory) + sep + 'grace', force=True)
        grace.write(x_data_type='te', y_data_type='s2', file='s2-te.agr', dir=str(directory) + sep + 'grace', force=True)
        
        ##################################################################################################
        
        #Create Diffusion Tensor
        
        # Display the diffusion tensor.
        diffusion_tensor.display()
        
        # Create the tensor PDB file.
        tensor_file = 'tensor.pdb'
        structure.create_diff_tensor_pdb(file=tensor_file, dir=str(directory) + sep, force=True)
        
        ##################################################################################################
        
        # Create S2 Macro for PyMol
        
        #create file
        
        self.file = open(str(directory) +sep + 's2.pml', 'w')
        self.file.write("load " + pdbfile + '\n')
        self.file.write("bg_color white\n")
        self.file.write("color gray90\n")
        self.file.write("hide all\n")
        self.file.write("show ribbon\n")
        
        for spin, spin_id in spin_loop(return_id=True):
        
        #select residue
                    spin_no = spin_id[spin_id.index(':')+1:spin_id.index('&')]
        
        
        #ribbon color
                    if  hasattr(spin, 's2'):
                        s2 = str(spin.s2)
                        if spin.s2 == None:
                                self.file.write("")
                        else:
                                width = ((1-spin.s2) * 2)
                                green = 1 - ((spin.s2)**3)
                                green = green * green * green #* green * green
                                green = 1 - green
                                self.file.write("set_color resicolor" + spin_no + ", [1," + str(green) + ",0]\n")
                                self.file.write("color resicolor" + spin_no + ", resi " + spin_no + "\n")
                                self.file.write("set_bond stick_radius, " + str(width) + ", resi " + spin_no + "\n")
        
        
        
        self.file.write("hide all\n")
        self.file.write("show sticks, name C+N+CA\n")
        self.file.write("set stick_quality, 10\n")
        self.file.write("ray\n")
        
        
        ##################################################################################################
        
        # Create Rex Macro for PyMol
        
        #create file
        
        self.file = open(str(directory) + sep + 'rex.pml', 'w')
        self.file.write("load " + pdbfile + '\n')
        self.file.write("bg_color white\n")
        self.file.write("color gray90\n")
        self.file.write("hide all\n")
        self.file.write("show ribbon\n")
        
        max_rex = 0
        
        #find max Rex
        for spin, spin_id in spin_loop(return_id=True):
        
                    if  hasattr(spin, 'rex'):
        
                          if not spin.rex == None:
                               if spin.rex > max_rex:
                                     max_rex = spin.rex
        
        
        for spin, spin_id in spin_loop(return_id=True):
        
        #select residue
                    spin_no = spin_id[spin_id.index(':')+1:spin_id.index('&')]
        #ribbon color
                    if  hasattr(spin, 'rex'):
                        rex = str(spin.rex)
                        if spin.rex == None:
                                self.file.write("")
                        else:
                                rel_rex = spin.rex / max_rex
                                width = ((rel_rex) * 2)
                                green = ((rel_rex))
                                green = green * green * green #* green * green
                                green = 1 - green
                                self.file.write("set_color resicolor" + spin_no + ", [1," + str(green) + ",0]\n")
                                self.file.write("color resicolor" + spin_no + ", resi " + spin_no + "\n")
                                self.file.write("set_bond stick_radius, " + str(width) + ", resi " + spin_no + "\n")
        
        
        
        self.file.write("hide all\n")
        self.file.write("show sticks, name C+N+CA\n")
        self.file.write("set stick_quality, 10\n")
        self.file.write("ray\n")
        
        ##################################################################################################
        
        print ""
        print ""
        print " ---------- done ----------------"
        print ""
        print ""
        print "Grace Plots are in Folder /grace/"
        print ""
        print "Signle Text Files for Relaxation Parameters are in Folder /final_results/"
        print ""
        print "Diffusion Tensor is in current Folder"
        print ""
        print "PyMol Macros are in current Folder - execute in PyMol with Command:"
        print "@rex.pml and @s2.pml"

        self.list_modelfree.Append(directory + sep + 'grace' + sep + 's2.agr')
        self.list_modelfree.Append(directory + sep + 'Model-free_Results.txt')
        self.list_modelfree.Append(directory + sep + 's2.pml')
        self.list_modelfree.Append(directory + sep + 'rex.pml')


## Create PyMol Macro for NOE colouring

def color_code_noe(self, target_dir):
        pdbfile = str(self.structure_r21_copy_1_copy.GetValue())
        directory = target_dir

        #create file
        file = open(directory + sep + 'noe.pml', 'w')
        file.write("load " + pdbfile + '\n')
        file.write("bg_color white\n")
        file.write("color gray90\n")
        file.write("hide all\n")
        file.write("show ribbon\n")
        
        for spin, spin_id in spin_loop(return_id=True):
        
        #select residue
                    spin_no = spin_id[spin_id.index(':')+1:spin_id.index('&')]
        
        #ribbon color
                    if  hasattr(spin, 'noe'):
                        noe = str(spin.noe)
                        if spin.noe == None:
                                file.write("")
                        else:
                                width = ((1-spin.noe) * 2)
                                green = 1 - ((spin.noe)**3) 
                                green = green * green * green #* green * green
                                green = 1 - green
                                file.write("set_color resicolor" + spin_no + ", [0," + str(green) + ",1]\n")
                                file.write("color resicolor" + spin_no + ", resi " + spin_no + "\n")
                                file.write("set_bond stick_radius, " + str(width) + ", resi " + spin_no + "\n")
        
        file.write("hide all\n")
        file.write("show sticks, name C+N+CA\n")
        file.write("set stick_quality, 10\n")
        file.write("ray\n")
        file.close()

        # add macro to results tab
        self.list_noe.Append(directory + sep + 'noe.pml')
