###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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

# Graphical User Interface for relax

homedir = ''

# Python module imports.
from os import getcwd, listdir
from re import search
from string import lower
import wx
import time
import res
from res.easygui import *
from res.about import *
from res.settings import *
from string import replace
from string import lowercase
from os import getcwd
import sys
import os
import webbrowser

# relax module imports.
from float import floatAsByteArray
from generic_fns.mol_res_spin import generate_spin_id, spin_index_loop, spin_loop
from generic_fns import pipes
from relax_errors import RelaxError

# Start
print '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n'
print '##############################################'
print '#                                            #'
print '#  relaxGUI - graphical interface for relax  #'
print '#        (C) 2009 Michael Bieri              #'
print '#                                            #'
print '##############################################'
print '\n\n\n\n'

# show about panel
about_relax(homedir)

#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

# Variables

# Define Global Variables
structure_file_pdb = "please insert .pdb file"
unresolved = ""
results_noe = []
results_tx = []
results_model_free = []
runrelax = 'sleeping'

#NOE3 variables 
noeref = ["","",""]
noesat = ["","",""]
noerefrmsd = [1000, 1000, 1000]
noesatrmsd = [1000, 1000, 1000]
nmrfreq = [600, 800, 900]
noe_sourcedir = [getcwd(),getcwd(),getcwd()]
noe_savedir = [getcwd(),getcwd(),getcwd()]

#T1 variables 
t1_num = 0
t1_list = []
t1_list2 = []
t1_list3 = []
t1_time = []
t1_time2 = []
t1_time3 = []
t1_sourcedir = [getcwd(),getcwd(),getcwd()]
t1_savedir = [getcwd(),getcwd(),getcwd()]

#T2 variables 
t2_num = 0
t2_list = []
t2_list2 = []
t2_list3 = []
t2_time = []
t2_time2 = []
t2_time3 = []
t2_sourcedir = [getcwd(),getcwd(),getcwd()]
t2_savedir = [getcwd(),getcwd(),getcwd()]

#Model-free variables 
model_source = getcwd()
model_save = getcwd()
selection = "AIC"
models = ["m0","m1","m2","m3","m4","m5","m6","m7","m8","m9"]
nmrfreq1 = 600
nmrfreq2 = 800
nmrfreq3 = 900
paramfiles1 = ["","",""]
paramfiles2 = ["","",""]
paramfiles3 = ["","",""]
results_dir_model = getcwd()


#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

# global definitions


#create list from string

def stringtolist(string):
    entrynum = 1
    string = string[2:(len(string)-2)]
    string = replace(string, "'", "")
    string = replace(string, "[", "")
    string = replace(string, "]", "")
    returnlist = (replace(string, ' ', '')).split(',')
    return(returnlist)

#Results

def see_results(openfile):
       if '.agr' in openfile:
            os.system('xmgrace ' + openfile + ' &')

       if '.txt' in openfile:
            os.system('gedit ' + openfile + ' &')
         
       if '.pml' in openfile:
            os.system('pymol ' + openfile + ' &')


# create model-free results

def model_free_results(self):
        directory = str(self.resultsdir_t21_copy_2.GetValue()) + '/final'
        pdbfile = str(self.structure_noe1.GetValue())

        #Read results
	pipename = 'Data_extraction ' + str(time.asctime(time.localtime()))
	pipe.create(pipename ,'mf')
	results.read()

	#create a table file

	#create file
	self.file = open(str(directory) + '/Model-free_Results.txt', 'w')
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
		
	value.write(param='rex', file='rex.txt', dir=str(directory) +' /final_results', force=True)
	value.write(param='s2', file='s2.txt', dir=str(directory) +' /final_results', force=True)
	value.write(param='s2f', file='s2f.txt', dir=str(directory) +' /final_results', force=True)
	value.write(param='s2s', file='s2s.txt', dir=str(directory) +' /final_results', force=True)
	value.write(param='te', file='te.txt', dir=str(directory) +' /final_results', force=True)
	value.write(param='tf', file='tf.txt', dir=str(directory) +' /final_results',  force=True)
	value.write(param='ts', file='ts.txt', dir=str(directory) +' /final_results', force=True)
	value.write(param='rex', file='rex.txt', dir=str(directory) +' /final_results', force=True)
	value.write(param='r', file='r.txt', dir=str(directory) +' /final_results', force=True)
	value.write(param='rex', file='rex.txt', dir=str(directory) +' /final_results', force=True)
	value.write(param='csa', file='csa.txt', dir=str(directory) +' /final_results', force=True)
	value.write(param='rex', file='rex.txt', dir=str(directory) +' /final_results', force=True)
	value.write(param='local_tm', file='local_tm.txt', dir=str(directory) +' /final_results', force=True)
	
	##################################################################################################
	
	#Create Grace Plots
	
	grace.write(x_data_type='spin', y_data_type='s2', file='s2.agr', dir=str(directory) +' /grace', force=True)
	grace.write(x_data_type='spin', y_data_type='te', file='te.agr', dir=str(directory) +' /grace', force=True)
	grace.write(x_data_type='spin', y_data_type='s2f', file='s2f.agr', dir=str(directory) +' /grace', force=True)
	grace.write(x_data_type='spin', y_data_type='s2s', file='s2s.agr', dir=str(directory) +' /grace', force=True)
	grace.write(x_data_type='spin', y_data_type='ts', file='ts.agr', dir=str(directory) +' /grace', force=True)
	grace.write(x_data_type='spin', y_data_type='tf', file='tf.agr', dir=str(directory) +' /grace', force=True)
	grace.write(x_data_type='spin', y_data_type='csa', file='csa.agr', dir=str(directory) +' /grace', force=True)
	grace.write(x_data_type='te', y_data_type='s2', file='s2-te.agr', dir=str(directory) +' /grace', force=True)
	
	##################################################################################################
	
	#Create Diffusion Tensor
	
	# Display the diffusion tensor.
	diffusion_tensor.display()
	
	# Create the tensor PDB file.
	tensor_file = 'tensor.pdb'
	structure.create_diff_tensor_pdb(file=tensor_file, dir=str(directory) + '/', force=True)
	
	##################################################################################################
	
	# Create S2 Macro for PyMol
	
	#create file
	
	self.file = open(str(directory) +'/s2.pml', 'w')
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
	
	self.file = open(str(directory) +'/rex.pml', 'w')
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

	self.list_modelfree.Append(directory + '/grace/s2.agr')
	self.list_modelfree.Append(directory + '/Model-free_Results.txt')
	self.list_modelfree.Append(directory + '/s2.pml')
	self.list_modelfree.Append(directory + '/rex.pml')


## Create PyMol Macro for NOE colouring

def color_code_noe(self, target_dir):
        pdbfile = str(self.structure_t21_copy_1_copy.GetValue())
        directory = target_dir

	#create file
	file = open(directory + '/noe.pml', 'w')
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
	self.list_noe.Append(directory + '/noe.pml')



## save relaxGUI project

def create_save_file(self, filename):

           #global definitions 
           globalsave = [str(self.structure_noe1.GetValue())]
         
           # NOE
           savenoe1 = [str(self.nmrfreq_value_noe1.GetValue()), str(self.noe_sat_1.GetValue()), str(self.noe_sat_err_1.GetValue()), str(self.noe_ref_1.GetValue()), str(self.noe_ref_err_1.GetValue()), str(self.structure_noe1.GetValue()), replace(str(self.unres_noe1.GetValue()), ',',';'), str(self.res_noe1.GetValue())]
           savenoe2 = [str(self.nmrfreq_value_noe1_copy.GetValue()), str(self.noe_sat_1_copy.GetValue()), str(self.noe_sat_err_1_copy.GetValue()), str(self.noe_ref_1_copy.GetValue()), str(self.noe_ref_err_1_copy.GetValue()), str(self.structure_noe1_copy.GetValue()), str(self.unres_noe1_copy.GetValue()), str(self.res_noe1_copy.GetValue())]
           savenoe3 = [str(self.nmrfreq_value_noe1_copy_1.GetValue()), str(self.noe_sat_1_copy_1.GetValue()), str(self.noe_sat_err_1_copy_1.GetValue()), str(self.noe_ref_1_copy_1.GetValue()), str(self.noe_ref_err_1_copy_1.GetValue()), str(self.structure_noe1_copy_1.GetValue()), str(self.unres_noe1_copy_1.GetValue()), str(self.res_noe1_copy_1.GetValue())]

           #T1
           t1_list_1 = str(self.t1_list_1.GetLabel()) + ', ' + str(self.t1_list_2.GetLabel()) + ', ' + str(self.t1_list_3.GetLabel()) + ', ' + str(self.t1_list_4.GetLabel()) + ', ' + str(self.t1_list_5.GetLabel()) + ', ' + str(self.t1_list_6.GetLabel()) + ', ' + str(self.t1_list_7.GetLabel()) + ', ' + str(self.t1_list_8.GetLabel()) + ', ' + str(self.t1_list_9.GetLabel()) + ', ' + str(self.t1_list_10.GetLabel()) + ', ' + str(self.t1_list_11.GetLabel()) + ', ' + str(self.t1_list_12.GetLabel()) + ', ' + str(self.t1_list_1_copy_11.GetLabel()) + ', ' + str(self.t1_list_14.GetLabel())
           t1_time_1 = str(self.t1_time_1.GetValue()) + ', ' + str(self.t1_time_2.GetValue()) + ', ' + str(self.t1_time_3.GetValue()) + ', ' + str(self.t1_time_4.GetValue()) + ', ' + str(self.t1_time_5.GetValue()) + ', ' + str(self.t1_time_6.GetValue()) + ', ' + str(self.t1_time_7.GetValue()) + ', ' + str(self.t1_time_8.GetValue()) + ', ' + str(self.t1_time_9.GetValue()) + ', ' + str(self.t1_time_10.GetValue()) + ', ' + str(self.t1_time_11.GetValue()) + ', ' + str(self.t1_time_12.GetValue()) + ', ' + str(self.t1_time_13.GetValue()) + ', ' + str(self.t1_time_1_4.GetValue()) 

           t1_list_2 = str(self.t1_list_1_copy.GetLabel()) + ', ' + str(self.t1_list_2_copy.GetLabel()) + ', ' + str(self.t1_list_3_copy.GetLabel()) + ', ' + str(self.t1_list_4_copy.GetLabel()) + ', ' + str(self.t1_list_5_copy.GetLabel()) + ', ' + str(self.t1_list_6_copy.GetLabel()) + ', ' + str(self.t1_list_7_copy.GetLabel()) + ', ' + str(self.t1_list_8_copy.GetLabel()) + ', ' + str(self.t1_list_9_copy.GetLabel()) + ', ' + str(self.t1_list_10_copy.GetLabel()) + ', ' + str(self.t1_list_11_copy.GetLabel()) + ', ' + str(self.t1_list_12_copy.GetLabel()) + ', ' + str(self.t1_list_1_copy_11_copy.GetLabel()) + ', ' + str(self.t1_list_14_copy.GetLabel())
           t1_time_2 = str(self.t1_time_1_copy.GetValue()) + ', ' + str(self.t1_time_2_copy.GetValue()) + ', ' + str(self.t1_time_3_copy.GetValue()) + ', ' + str(self.t1_time_4_copy.GetValue()) + ', ' + str(self.t1_time_5_copy.GetValue()) + ', ' + str(self.t1_time_6_copy.GetValue()) + ', ' + str(self.t1_time_7_copy.GetValue()) + ', ' + str(self.t1_time_8_copy.GetValue()) + ', ' + str(self.t1_time_9_copy.GetValue()) + ', ' + str(self.t1_time_10_copy.GetValue()) + ', ' + str(self.t1_time_11_copy.GetValue()) + ', ' + str(self.t1_time_12_copy.GetValue()) + ', ' + str(self.t1_time_13_copy.GetValue()) + ', ' + str(self.t1_time_1_4_copy.GetValue()) 

           t1_list_3 = str(self.t1_list_1_copy_1.GetLabel()) + ', ' + str(self.t1_list_2_copy_1.GetLabel()) + ', ' + str(self.t1_list_3_copy_1.GetLabel()) + ', ' + str(self.t1_list_4_copy_1.GetLabel()) + ', ' + str(self.t1_list_5_copy_1.GetLabel()) + ', ' + str(self.t1_list_6_copy_1.GetLabel()) + ', ' + str(self.t1_list_7_copy_1.GetLabel()) + ', ' + str(self.t1_list_8_copy_1.GetLabel()) + ', ' + str(self.t1_list_9_copy_1.GetLabel()) + ', ' + str(self.t1_list_10_copy_1.GetLabel()) + ', ' + str(self.t1_list_11_copy_1.GetLabel()) + ', ' + str(self.t1_list_12_copy_1.GetLabel()) + ', ' + str(self.t1_list_1_copy_11_copy_1.GetLabel()) + ', ' + str(self.t1_list_14_copy_1.GetLabel())
           t1_time_3 = str(self.t1_time_1_copy_1.GetValue()) + ', ' + str(self.t1_time_2_copy_1.GetValue()) + ', ' + str(self.t1_time_3_copy_1.GetValue()) + ', ' + str(self.t1_time_4_copy_1.GetValue()) + ', ' + str(self.t1_time_5_copy_1.GetValue()) + ', ' + str(self.t1_time_6_copy_1.GetValue()) + ', ' + str(self.t1_time_7_copy_1.GetValue()) + ', ' + str(self.t1_time_8_copy_1.GetValue()) + ', ' + str(self.t1_time_9_copy_1.GetValue()) + ', ' + str(self.t1_time_10_copy_1.GetValue()) + ', ' + str(self.t1_time_11_copy_1.GetValue()) + ', ' + str(self.t1_time_12_copy_1.GetValue()) + ', ' + str(self.t1_time_13_copy_1.GetValue()) + ', ' + str(self.t1_time_1_4_copy_1.GetValue()) 

           savet11 = [str(self.nmrfreq_value_t11.GetValue()), str(self.resultsdir_t11.GetValue()), replace(str(self.unresolved_t11.GetValue()),',',';'), t1_list_1, t1_time_1]
           savet12 = [str(self.nmrfreq_value_t11_copy.GetValue()), str(self.resultsdir_t11_copy.GetValue()), replace(str(self.unresolved_t11_copy.GetValue()),',',';'), t1_list_2, t1_time_2]
           savet13 = [str(self.nmrfreq_value_t11_copy_1.GetValue()), str(self.resultsdir_t11_copy_1.GetValue()), replace(str(self.unresolved_t11_copy_1.GetValue()),',',';'), t1_list_3, t1_time_3]

           #T2
           t2_list_1 = str(self.t2_list_1.GetLabel()) + ', ' + str(self.t2_list_2.GetLabel()) + ', ' + str(self.t2_list_3.GetLabel()) + ', ' + str(self.t2_list_4.GetLabel()) + ', ' + str(self.t2_list_5.GetLabel()) + ', ' + str(self.t2_list_6.GetLabel()) + ', ' + str(self.t2_list_7.GetLabel()) + ', ' + str(self.t2_list_8.GetLabel()) + ', ' + str(self.t2_list_9.GetLabel()) + ', ' + str(self.t2_list_10.GetLabel()) + ', ' + str(self.t2_list_11.GetLabel()) + ', ' + str(self.t2_list_12.GetLabel()) + ', ' + str(self.t2_list_13.GetLabel()) + ', ' + str(self.t2_list_14.GetLabel())
           t2_time_1 = str(self.t2_time_1.GetValue()) + ', ' + str(self.t2_time_2.GetValue()) + ', ' + str(self.t2_time_3.GetValue()) + ', ' + str(self.t2_time_4.GetValue()) + ', ' + str(self.t2_time_5.GetValue()) + ', ' + str(self.t2_time_6.GetValue()) + ', ' + str(self.t2_time_7.GetValue()) + ', ' + str(self.t2_time_8.GetValue()) + ', ' + str(self.t2_time_9.GetValue()) + ', ' + str(self.t2_time_10.GetValue()) + ', ' + str(self.t2_time_11.GetValue()) + ', ' + str(self.t2_time_12.GetValue()) + ', ' + str(self.t2_time_13.GetValue()) + ', ' + str(self.t2_time_14.GetValue()) 

           t2_list_2 = str(self.t2_list_1_copy.GetLabel()) + ', ' + str(self.t2_list_2_copy.GetLabel()) + ', ' + str(self.t2_list_3_copy.GetLabel()) + ', ' + str(self.t2_list_4_copy.GetLabel()) + ', ' + str(self.t2_list_5_copy.GetLabel()) + ', ' + str(self.t2_list_6_copy.GetLabel()) + ', ' + str(self.t2_list_7_copy.GetLabel()) + ', ' + str(self.t2_list_8_copy.GetLabel()) + ', ' + str(self.t2_list_9_copy.GetLabel()) + ', ' + str(self.t2_list_10_copy.GetLabel()) + ', ' + str(self.t2_list_11_copy.GetLabel()) + ', ' + str(self.t2_list_12_copy.GetLabel()) + ', ' + str(self.t2_list_13_copy.GetLabel()) + ', ' + str(self.t2_list_14_copy.GetLabel())
           t2_time_2 = str(self.t2_time_1_copy.GetValue()) + ', ' + str(self.t2_time_2_copy.GetValue()) + ', ' + str(self.t2_time_3_copy.GetValue()) + ', ' + str(self.t2_time_4_copy.GetValue()) + ', ' + str(self.t2_time_5_copy.GetValue()) + ', ' + str(self.t2_time_6_copy.GetValue()) + ', ' + str(self.t2_time_7_copy.GetValue()) + ', ' + str(self.t2_time_8_copy.GetValue()) + ', ' + str(self.t2_time_9_copy.GetValue()) + ', ' + str(self.t2_time_10_copy.GetValue()) + ', ' + str(self.t2_time_11_copy.GetValue()) + ', ' + str(self.t2_time_12_copy.GetValue()) + ', ' + str(self.t2_time_13_copy.GetValue()) + ', ' + str(self.t2_time_14_copy.GetValue()) 

           t2_list_3 = str(self.t2_list_1_copy_1.GetLabel()) + ', ' + str(self.t2_list_2_copy_1.GetLabel()) + ', ' + str(self.t2_list_3_copy_1.GetLabel()) + ', ' + str(self.t2_list_4_copy_1.GetLabel()) + ', ' + str(self.t2_list_5_copy_1.GetLabel()) + ', ' + str(self.t2_list_6_copy_1.GetLabel()) + ', ' + str(self.t2_list_7_copy_1.GetLabel()) + ', ' + str(self.t2_list_8_copy_1.GetLabel()) + ', ' + str(self.t2_list_9_copy_1.GetLabel()) + ', ' + str(self.t2_list_10_copy_1.GetLabel()) + ', ' + str(self.t2_list_11_copy_1.GetLabel()) + ', ' + str(self.t2_list_12_copy_1.GetLabel()) + ', ' + str(self.t2_list_13_copy_1.GetLabel()) + ', ' + str(self.t2_list_14_copy_1.GetLabel())
           t2_time_3 = str(self.t2_time_1_copy_1.GetValue()) + ', ' + str(self.t2_time_2_copy_1.GetValue()) + ', ' + str(self.t2_time_3_copy_1.GetValue()) + ', ' + str(self.t2_time_4_copy_1.GetValue()) + ', ' + str(self.t2_time_5_copy_1.GetValue()) + ', ' + str(self.t2_time_6_copy_1.GetValue()) + ', ' + str(self.t2_time_7_copy_1.GetValue()) + ', ' + str(self.t2_time_8_copy_1.GetValue()) + ', ' + str(self.t2_time_9_copy_1.GetValue()) + ', ' + str(self.t2_time_10_copy_1.GetValue()) + ', ' + str(self.t2_time_11_copy_1.GetValue()) + ', ' + str(self.t2_time_12_copy_1.GetValue()) + ', ' + str(self.t2_time_13_copy_1.GetValue()) + ', ' + str(self.t2_time_14_copy_1.GetValue()) 

           savet21 = [str(self.nmrfreq_value_t21.GetValue()), str(self.resultsdir_t21.GetValue()), replace(str(self.unresolved_t21.GetValue()),',',';'), t2_list_1, t2_time_1]
           savet22 = [str(self.nmrfreq_value_t21_copy.GetValue()), str(self.resultsdir_t21_copy.GetValue()), replace(str(self.unresolved_t21_copy.GetValue()),',',';'), t2_list_2, t2_time_2]
           savet23 = [str(self.nmrfreq_value_t21_copy_1.GetValue()), str(self.resultsdir_t21_copy_1.GetValue()), replace(str(self.unresolved_t21_copy_1.GetValue()),',',';'), t2_list_3, t2_time_3]
           

           #model-free
           savemodel = [str(self.modelfreefreq1.GetValue()), str(self.m_noe_1.GetValue()), str(self.m_r1_1.GetValue()), str(self.m_r2_1.GetValue()), str(self.modelfreefreq2.GetValue()), str(self.m_noe_2.GetValue()), str(self.m_r1_2.GetValue()), str(self.m_r2_2.GetValue()), str(self.modelfreefreq3.GetValue()), str(self.m_noe_3.GetValue()), str(self.m_r1_3.GetValue()), str(self.m_r2_3.GetValue()), str(self. unresolved_t21_copy_1_copy.GetValue()), str(self.resultsdir_t21_copy_2.GetValue())]

           #results
           noeresult = []
           for i in range(0,self.list_noe.GetCount()):
              noeresult.append(str(self.list_noe.GetString(i)))
           txresult = []
           for i in range(0,self.list_tx.GetCount()):
              txresult.append(str(self.list_tx.GetString(i)))
           modelresult = []
           for i in range(0,self.list_modelfree.GetCount()):
              modelresult.append(str(self.list_modelfree.GetString(i)))

           #write file
           file = open(filename, 'w')
           file.write('relaxGUI save file\n\n')
           file.write('Global\n')
           file.write(str(globalsave) + '\n')
           file.write('NOE\n')
           file.write(str(savenoe1) + '\n')
           file.write(str(savenoe2) + '\n')
           file.write(str(savenoe3) + '\n')
           file.write('T1\n')
           file.write(str(savet11) + '\n')
           file.write(str(savet12) + '\n')
           file.write(str(savet13) + '\n')
           file.write('T2\n')
           file.write(str(savet21) + '\n')
           file.write(str(savet22) + '\n')
           file.write(str(savet23) + '\n')
           file.write('Model-free\n')
           file.write(str(savemodel) + '\n')
           file.write('Results\n')
           file.write(str(noeresult) +'\n')
           file.write(str(txresult) +'\n')
           file.write(str(modelresult) +'\n')
           file.close()

           print '\n\nProject successfully saved in ' + filename + '\n\n'

## open relaxGUI project

def open_file(self, filename):
        file = open(filename, 'r')
        saved = []
        fileformat = False
        for line in file:    
              line_a = str(line.strip().split('\n'))   
              line_a = line_a[2:(len(line_a)-2)]
              if 'relaxGUI save file' in line_a:
                   fileformat = True
              saved.append(line_a)
        file.close()

        if fileformat == False:
           msgbox(msg = 'This is not a relaxGUI save file!', title = 'Error')

        if fileformat == True:

           #global
           param = stringtolist(saved[3])
           structure_file_pdb = param[0]
           self.structure_noe1.SetValue(structure_file_pdb)
           self.structure_t11.SetValue(structure_file_pdb)
           self.structure_t21.SetValue(structure_file_pdb)
           self.structure_noe1_copy.SetValue(structure_file_pdb)
           self.structure_t11_copy.SetValue(structure_file_pdb)
           self.structure_t21_copy.SetValue(structure_file_pdb)
           self.structure_noe1_copy_1.SetValue(structure_file_pdb)
           self.structure_t11_copy_1.SetValue(structure_file_pdb)
           self.structure_t21_copy_1.SetValue(structure_file_pdb)
           self.structure_t21_copy_1_copy.SetValue(structure_file_pdb)

           # load NOE 1
           noes = stringtolist(saved[5])
           self.nmrfreq_value_noe1.SetValue(noes[0])
           self.noe_sat_1.SetValue(noes[1])
           self.noe_sat_err_1.SetValue(noes[2])
           self.noe_ref_1.SetValue(noes[3])
           self.noe_ref_err_1.SetValue(noes[4])
           self.structure_noe1.SetValue(noes[5])
           self.unres_noe1.SetValue(noes[6])
           self.res_noe1.SetValue(noes[7])

           # load NOE 2
           noes = stringtolist(saved[6])
           self.nmrfreq_value_noe1_copy.SetValue(noes[0])
           self.noe_sat_1_copy.SetValue(noes[1])
           self.noe_sat_err_1_copy.SetValue(noes[2])
           self.noe_ref_1_copy.SetValue(noes[3])
           self.noe_ref_err_1_copy.SetValue(noes[4])
           self.structure_noe1_copy.SetValue(noes[5])
           self.unres_noe1_copy.SetValue(noes[6])
           self.res_noe1_copy.SetValue(noes[7])

           # load NOE 3
           noes = stringtolist(saved[7])
           self.nmrfreq_value_noe1_copy_1.SetValue(noes[0])
           self.noe_sat_1_copy_1.SetValue(noes[1])
           self.noe_sat_err_1_copy_1.SetValue(noes[2])
           self.noe_ref_1_copy_1.SetValue(noes[3])
           self.noe_ref_err_1_copy_1.SetValue(noes[4])
           self.structure_noe1_copy_1.SetValue(noes[5])
           self.unres_noe1_copy_1.SetValue(noes[6])
           self.res_noe1_copy_1.SetValue(noes[7])

           #load T1
           tx = stringtolist(saved[9])
           self.nmrfreq_value_t11.SetValue(tx[0])
           self.resultsdir_t11.SetValue(tx[1])
           self.unresolved_t11.SetValue(tx[2])

           #load T1 2
           tx = stringtolist(saved[10])
           self.nmrfreq_value_t11_copy.SetValue(tx[0])
           self.resultsdir_t11_copy.SetValue(tx[1])
           self.unresolved_t11_copy.SetValue(tx[2])

           #load T1 3
           tx = stringtolist(saved[11])
           self.nmrfreq_value_t21_copy_1.SetValue(tx[0])
           self.resultsdir_t21_copy_1.SetValue(tx[1])
           self.unresolved_t21_copy_1.SetValue(tx[2])

           #load T1
           tx = stringtolist(saved[13])
           self.nmrfreq_value_t21.SetValue(tx[0])
           self.resultsdir_t21.SetValue(tx[1])
           self.unresolved_t21.SetValue(tx[2])

           #load T1 2
           tx = stringtolist(saved[14])
           self.nmrfreq_value_t21_copy.SetValue(tx[0])
           self.resultsdir_t21_copy.SetValue(tx[1])
           self.unresolved_t21_copy.SetValue(tx[2])

           #load T1 3
           tx = stringtolist(saved[15])
           self.nmrfreq_value_t21_copy_1.SetValue(tx[0])
           self.resultsdir_t21_copy_1.SetValue(tx[1])
           self.unresolved_t21_copy_1.SetValue(tx[2])

           #model-free
           openmodel = stringtolist(saved[17])
           self.modelfreefreq1.SetValue(openmodel[0])
           self.m_noe_1.SetValue(openmodel[1])
           self.m_r1_1.SetValue(openmodel[2])
           self.m_r2_1.SetValue(openmodel[3])
           self.modelfreefreq2.SetValue(openmodel[4])
           self.m_noe_2.SetValue(openmodel[5])
           self.m_r1_2.SetValue(openmodel[6])
           self.m_r2_2.SetValue(openmodel[7])
           self.modelfreefreq3.SetValue(openmodel[8])
           self.m_noe_3.SetValue(openmodel[9])
           self.m_r1_3.SetValue(openmodel[10])
           self.m_r2_3.SetValue(openmodel[11])
           self.unresolved_t21_copy_1_copy.SetValue(openmodel[12])
           self.resultsdir_t21_copy_2.SetValue(openmodel[13])

           #results
           self.list_noe.Clear()  
           self.list_tx.Clear()  
           self.list_modelfree.Clear()  

           results = stringtolist(saved[19])
           for i in range(0,len(results)):
              self.list_noe.Append(str(results[i]))

           results = stringtolist(saved[20])
           for i in range(0,len(results)):
              self.list_tx.Append(str(results[i]))

           results = stringtolist(saved[21])
           for i in range(0,len(results)):
              self.list_modelfree.Append(str(results[i]))

           print '\n\nSuccessfully opened Project ' + filename + '\n\n' 


#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

# Start Calculations

#NOE

def make_noe(target_dir, noe_ref, noe_sat, rmsd_ref, rmsd_sat, nmr_freq, struct_pdb, unres, execute, self, freqno):
        success = False
        resultsdir = str(target_dir)
        gracedir = str(target_dir) + '/grace'
        save_file = str(target_dir) + '/noe.' + str(nmr_freq)  + '.out'
        noe_ref_1 = noe_ref
        noe_sat_1 = noe_sat
        unres = str(unres)

        #create unresolved file
        unres = replace(unres, ",","\n")
        unres = replace(unres, " ","")
        filename3 = target_dir + '/unresolved'
        unresolved = open(filename3, 'w')
        unresolved.write(unres)
        unresolved.close()

        pipename = 'NOE ' + str(time.asctime(time.localtime()))

	# Create the NOE data pipe.
	pipe.create(pipename, 'noe')
	
	# Load the backbone amide 15N spins from a PDB file.
	structure.read_pdb(str(struct_pdb))
	structure.load_spins(spin_id='@N')
	
	# Load the reference spectrum and saturated spectrum peak intensities.
	spectrum.read_intensities(file=str(noe_ref), spectrum_id='ref_ave')
	spectrum.read_intensities(file=str(noe_sat), spectrum_id='sat_ave')
	
	# Set the spectrum types.
	noe.spectrum_type('ref', 'ref_ave')
	noe.spectrum_type('sat', 'sat_ave')
	
	# Set the errors.
	spectrum.baseplane_rmsd(error=int(rmsd_ref), spectrum_id='ref_ave')
	spectrum.baseplane_rmsd(error=int(rmsd_sat), spectrum_id='sat_ave')
	
	# Peak intensity error analysis.
	spectrum.error_analysis()
	
	# Deselect unresolved residues.
	deselect.read(file=resultsdir + '/unresolved')
	
	# Calculate the NOEs.
	calc()
	
	# Save the NOEs.
	value.write(param='noe', file=save_file, force=True)
	
	# Create grace files.
	grace.write(y_data_type='ref_ave', file='ref.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)
	grace.write(y_data_type='sat_ave', file='sat.' + str(nmr_freq) + '.agr', dir = gracedir,force=True)
	grace.write(y_data_type='noe', file='noe.' + str(nmr_freq) + '.agr', dir = gracedir,force=True)
	
	
	# Write the results.
	results.write(file='results', dir=resultsdir, force=True)
	
	# Save the program state.
	state.save('save', dir_name = resultsdir, force=True)
	
	print ""
	print ""
	print ""
	print "____________________________________________________________________________"
	print ""
	print "calculation finished"
	print ""
        if freqno == 1:
                     self.m_noe_1.SetValue(target_dir + '/noe.' + str(nmr_freq) + '.out')
        if freqno == 2:
                     self.m_noe_2.SetValue(target_dir + '/noe.' + str(nmr_freq) + '.out')
        if freqno == 3:
                     self.m_noe_3.SetValue(target_dir + '/noe.' + str(nmr_freq) + '.out')
        self.list_noe.Append(target_dir + '/grace/noe.' + str(nmr_freq) + '.agr')
        success = True

	# Create PyMol Macro
	color_code_noe(self, target_dir)

        msgbox(msg='NOE calculation was successfull !', title='relaxGUI ', ok_button='OK', image=homedir + 'res/pics/relax.gif', root=None)



#############################################################################################################
# Tx 

def make_tx(target_dir, relax_times, structure_pdb, nmr_freq, t1_t2, freq_no, unres, self, freqno):

        success = False
        resultsdir = str(target_dir)
        gracedir = str(target_dir) + '/grace'
        savefile = str(target_dir) + '/r' + str(t1_t2) + '.' + str(nmr_freq)  + '.out'


        # Select Peak Lists and Relaxation Times 
	if t1_t2 == 1:
            if freq_no == 1:
              peakfiles = t1_list
            if freq_no == 2:
              peakfiles = t1_list2
            if freq_no == 3:
              peakfiles = t1_list3

	if t1_t2 == 2:
            if freq_no == 1:
              peakfiles = t2_list
            if freq_no == 2:
              peakfiles = t2_list2
            if freq_no == 3:
              peakfiles = t2_list3

        #create unresolved file
        unres = replace(unres, ",","\n")
        filename2 = target_dir + '/unresolved'
        file = open(filename2, 'w')
        file.write(unres)
        file.close()

	pipename = 'Tx ' + str(time.asctime(time.localtime()))

	# Create the NOE data pipe.
	pipe.create(pipename, 'relax_fit')

	# Load the backbone amide 15N spins from a PDB file.
	structure.read_pdb(str(structure_pdb))
	structure.load_spins(spin_id='@N')

	# Spectrum names.
	names = peakfiles

	# Relaxation times (in seconds).
	times = relax_times

	# Loop over the spectra.
	for i in xrange(len(names)):
	    # Load the peak intensities.
	    spectrum.read_intensities(file=names[i], spectrum_id=names[i], int_method='height')

	    # Set the relaxation times.
	    relax_fit.relax_time(time=float(times[i]), spectrum_id=names[i])

	# Specify the duplicated spectra.
	for i in range(0,(len(names))):
            for j in range(i,(len(names))):
               if relax_times[i] == times[j]:
                  if not i == j:   
                     spectrum.replicated(spectrum_ids=[names[i], names[j]])


	# Peak intensity error analysis.
	spectrum.error_analysis()
	
	# Deselect unresolved spins.
	deselect.read(file=resultsdir + '/unresolved')
	
	# Set the relaxation curve type.
	relax_fit.select_model('exp')
	
	# Grid search.
	grid_search(inc=11)
	
	# Minimise.
	minimise('simplex', scaling=False, constraints=False)
	
	# Monte Carlo simulations.
	monte_carlo.setup(number=500)
	monte_carlo.create_data()
	monte_carlo.initial_values()
	minimise('simplex', scaling=False, constraints=False)
	monte_carlo.error_analysis()
	
	# Save the relaxation rates.
	value.write(param='rx', file= savefile, force=True)
	
	
	# Create Grace plots of the data.
	grace.write(y_data_type='chi2', file='chi2.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Minimised chi-squared value.
	grace.write(y_data_type='i0', file='i0.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Initial peak intensity.
	grace.write(y_data_type='rx', file='rx.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Relaxation rate.
	grace.write(x_data_type='relax_times', y_data_type='int', file='intensities.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Average peak intensities.
	grace.write(x_data_type='relax_times', y_data_type='int', norm=True, file='intensities_norm.' + str(nmr_freq) + '.agr', dir = gracedir, force=True)    # Average peak intensities (normalised).
	
	
	
	# Write the results.
	results.write(file='results', dir=resultsdir, force=True)
	
	# Save the program state.
	state.save('save', dir_name = resultsdir, force=True)
	
	print ""
	print ""
	print ""
	print "____________________________________________________________________________"
	print ""
	print "calculation finished"
	print ""

	msgbox(msg='T' + str(t1_t2) +' calculation was successfull !', title='relaxGUI ', ok_button='OK', image=homedir + 'res/pics/relax.gif', root=None)

        # list files to results
	self.list_tx.Append(target_dir + '/grace/rx.' + str(nmr_freq) + '.agr')
	self.list_tx.Append(target_dir + '/grace/intensities_norm.' + str(nmr_freq) + '.agr')

	# add files to model-free tab
	if t1_t2 == 1:
                    if freqno == 1:
                      self.m_r1_1.SetValue(target_dir + '/r1.' + str(nmr_freq) + '.out')
                    if freqno == 2:
                      self.m_r1_2.SetValue(target_dir + '/r1.' + str(nmr_freq) + '.out')
                    if freqno == 3:
                      self.m_r1_3.SetValue(target_dir + '/r1.' + str(nmr_freq) + '.out')
	if t1_t2 == 2:
                    if freqno == 1:
                      self.m_r2_1.SetValue(target_dir + '/r2.' + str(nmr_freq) + '.out')
                    if freqno == 2:
                      self.m_r2_2.SetValue(target_dir + '/r2.' + str(nmr_freq) + '.out')
                    if freqno == 3:
                      self.m_r2_3.SetValue(target_dir + '/r2.' + str(nmr_freq) + '.out')





#############################################################################################################
### Model-free

def start_model_free(self, model):

	target_dir = str(self.resultsdir_t21_copy_2.GetValue())
	unres = str(self.unresolved_t21_copy_1_copy.GetValue())
	nmr_freq1 = str(self.modelfreefreq1.GetValue())
	nmr_freq2 = str(self.modelfreefreq2.GetValue())
	nmr_freq3 = str(self.modelfreefreq3.GetValue())

	# detect 2 or 3 field strength
	num_field = 3
	if self.modelfreefreq3.GetValue() == '':
            num_field = 2
	if self.m_noe_3.GetValue() == '':
            num_field = 2
	if self.m_r1_3.GetValue() == '':
            num_field = 2
	if self.m_r1_3.GetValue() == '':
            num_field = 2

	if self.aic.GetValue() == True:
            selection = "AIC"
	if self.bic.GetValue() == True:
            selection = "BIC" 

	#create unresolved file
	filename2 =  target_dir + '/unresolved'
	file = open(filename2, 'w')
	unres = replace(unres, ",","\n")
	file.write(unres)
	file.close()

	#create models list
        models = []

	if self.m0.GetValue() == True:
            models.append('m0')
	if self.m1.GetValue() == True:
            models.append('m1')
	if self.m2.GetValue() == True:
            models.append('m2')
	if self.m3.GetValue() == True:
            models.append('m3')
	if self.m4.GetValue() == True:
            models.append('m4')
	if self.m5.GetValue() == True:
            models.append('m5')
	if self.m6.GetValue() == True:
            models.append('m6')
	if self.m7.GetValue() == True:
            models.append('m7')
	if self.m8.GetValue() == True:
            models.append('m8')
	if self.m9.GetValue() == True:
            models.append('m9')

	#create tm models list
        tmodels = []

	if self.m0.GetValue() == True:
            tmodels.append('tm0')
	if self.m1.GetValue() == True:
            tmodels.append('tm1')
	if self.m2.GetValue() == True:
            tmodels.append('tm2')
	if self.m3.GetValue() == True:
            tmodels.append('tm3')
	if self.m4.GetValue() == True:
            tmodels.append('tm4')
	if self.m5.GetValue() == True:
            tmodels.append('tm5')
	if self.m6.GetValue() == True:
            tmodels.append('tm6')
	if self.m7.GetValue() == True:
            tmodels.append('tm7')
	if self.m8.GetValue() == True:
            tmodels.append('tm8')
	if self.m9.GetValue() == True:
            tmodels.append('tm9')

	MF_MODELS = models
	LOCAL_TM_MODELS = tmodels

	# User variables.
	#################

	PDB_FILE = str(self.structure_t21_copy_1_copy.GetValue())
	gracedir = target_dir + '/grace'
	resultsdir = target_dir + '/'
	m_method = selection

	if selection == "AIC":
             msel = "aic"
	if selection == "BIC":
             msel = "bic"
        modelselection = msel

        #parameter files
	noe_1 = str(self.m_noe_1.GetValue())
	r1_1 = str(self.m_r1_1.GetValue())
	r2_1 = str(self.m_r2_1.GetValue())
	noe_2 = str(self.m_noe_2.GetValue())
	r1_2 = str(self.m_r1_2.GetValue())
	r2_2 = str(self.m_r2_2.GetValue())
	noe_3 = str(self.m_noe_3.GetValue())
	r1_3 = str(self.m_r1_3.GetValue())
	r2_3 = str(self.m_r2_3.GetValue())

	HETNUC = 'N'
	SEQ_ARGS = [noe_1, None, None, 1, 2, 3, 4, None]

	nmr_freq1 = int(self.modelfreefreq1.GetValue())
	nmr_freq2 = int(self.modelfreefreq2.GetValue())
        if num_field == 3:
	   nmr_freq3 = int(self.modelfreefreq3.GetValue())

        # The relaxation data (data type, frequency label, frequency, file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, data_col, error_col, sep).  These are the arguments to the relax_data.read() user function, please see the documentation for that function for more information.

	if num_field == 2:
	 RELAX_DATA = [['R1', str(nmr_freq1), nmr_freq1 * 1e6, r1_1,  None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq1), nmr_freq1 * 1e6, r2_1,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['NOE', str(nmr_freq1), nmr_freq1 * 1e6, noe_1,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['R1', str(nmr_freq2), nmr_freq2 * 1e6, r1_2,  None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq2), nmr_freq2 * 1e6, r2_2,  None, None, 1, 2, 3, 4, 5, 6, None]]

	if num_field == 3:
	 RELAX_DATA = [['R1', str(nmr_freq1), nmr_freq1 * 1e6, r1_1,  None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq1), nmr_freq1 * 1e6, r2_1,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['NOE', str(nmr_freq1), nmr_freq1 * 1e6, noe_1,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['R1', str(nmr_freq2), nmr_freq2 * 1e6, r1_2,  None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq2), nmr_freq2 * 1e6, r2_2,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['NOE', str(nmr_freq2), nmr_freq2 * 1e6, noe_2,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['R1', str(nmr_freq3), nmr_freq3 * 1e6, r1_3,  None, None, 1, 2, 3, 4, 5, 6, None],
                       ['R2', str(nmr_freq3), nmr_freq3 * 1e6, r2_3,  None, None, 1, 2, 3, 4, 5, 6, None], 
                       ['NOE', str(nmr_freq3), nmr_freq3 * 1e6, noe_3,  None, None, 1, 2, 3, 4, 5, 6, None]] 
	
	
	# The diffusion model.
	DIFF_MODEL = model
	
	
	# The file containing the list of unresolved spins to exclude from the analysis (set this to None if no spin is to be excluded).
	UNRES = resultsdir + 'unresolved'
	
	# A file containing a list of spins which can be dynamically excluded at any point within the analysis (when set to None, this variable is not used).
	EXCLUDE = None
	
	# The bond length, CSA values, heteronucleus type, and proton type.
	BOND_LENGTH = 1.02 * 1e-10
	CSA = -172 * 1e-6
	HETNUC = '15N'
	PROTON = '1H'
	
	# The grid search size (the number of increments per dimension).
	GRID_INC = 11
	
	# The optimisation technique.
	MIN_ALGOR = 'newton'
	
	# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
	MC_NUM = 500
	
	# Automatic looping over all rounds until convergence (must be a boolean value of True or False).
	CONV_LOOP = True
	
	
	class Model:
	    def __init__(self):
	        """Execute the model-free analysis."""
	
	        # Setup.
	        #self = relax
	
	
	        # MI - Local tm.
	        ################
	
	        if DIFF_MODEL == 'local_tm':
	            # Base directory to place files into.
	            self.base_dir = resultsdir + 'local_tm/'
	
	            # Sequential optimisation of all model-free models (function must be modified to suit).
	            self.multi_model(local_tm=True)
	
	            # Model selection.
	            self.model_selection(modsel_pipe=modelselection, dir=self.base_dir + modelselection)
	
	
	        # Diffusion models MII to MV.
	        #############################
	
	        elif DIFF_MODEL == 'sphere' or DIFF_MODEL == 'prolate' or DIFF_MODEL == 'oblate' or DIFF_MODEL == 'ellipsoid':
	            # Loop until convergence if CONV_LOOP is set, otherwise just loop once.
	            # This looping could be made much cleaner by removing the dependence on the determine_rnd() function.
	            while 1:
	                # Determine which round of optimisation to do (init, round_1, round_2, etc).
	                self.round = self.determine_rnd(model=DIFF_MODEL)
	
	                # Inital round of optimisation for diffusion models MII to MV.
	                if self.round == 0:
	                    # Base directory to place files into.
	                    self.base_dir = resultsdir + DIFF_MODEL + '/init/'
	
	                    # Run name.
	                    name = DIFF_MODEL
	
	                    # Create the data pipe.
	                    pipe.create(name, 'mf')
	
	                    # Load the local tm diffusion model MI results.
	                    results.read(file='results', dir=resultsdir + 'local_tm/'+modelselection)
	
	                    # Remove the tm parameter.
	                    model_free.remove_tm()
	
	                    # Deselect the spins in the EXCLUDE list.
	                    if EXCLUDE:
	                        deselect.read(file=EXCLUDE)
	
	                    # Load the PDB file and calculate the unit vectors parallel to the XH bond.
	                    if PDB_FILE:
	                        structure.read_pdb(PDB_FILE)
	                        structure.vectors(attached='H')
	
	                    # Add an arbitrary diffusion tensor which will be optimised.
	                    if DIFF_MODEL == 'sphere':
	                        diffusion_tensor.init(10e-9, fixed=False)
	                        inc = 11
	                    elif DIFF_MODEL == 'prolate':
	                        diffusion_tensor.init((10e-9, 0, 0, 0), spheroid_type='prolate', fixed=False)
	                        inc = 11
	                    elif DIFF_MODEL == 'oblate':
	                        diffusion_tensor.init((10e-9, 0, 0, 0), spheroid_type='oblate', fixed=False)
	                        inc = 11
	                    elif DIFF_MODEL == 'ellipsoid':
	                        diffusion_tensor.init((10e-09, 0, 0, 0, 0, 0), fixed=False)
	                        inc = 6
	
	                    # Minimise just the diffusion tensor.
	                    fix(element='all_spins')
	                    grid_search(inc=inc)
	                    minimise(MIN_ALGOR)
	
	                    # Write the results.
	                    results.write(file='results', dir=self.base_dir, force=True)
	
	
	                # Normal round of optimisation for diffusion models MII to MV.
	                else:
	                    # Base directory to place files into.
	                    self.base_dir = resultsdir + DIFF_MODEL + '/round_' + `self.round` + '/'
	
	                    # Load the optimised diffusion tensor from either the previous round.
	                    self.load_tensor()
	
	                    # Sequential optimisation of all model-free models (function must be modified to suit).
	                    self.multi_model()
	
	                    # Model selection.
	                    self.model_selection(modsel_pipe='final', dir=self.base_dir + modelselection)
	
	                    # Final optimisation of all diffusion and model-free parameters.
	                    fix('all', fixed=False)
	
	                    # Minimise all parameters.
	                    minimise(MIN_ALGOR)
	
	                    # Write the results.
	                    dir = self.base_dir + 'opt'
	                    results.write(file='results', dir=dir, force=True)
	
	                    # Test for convergence.
	                    converged = self.convergence()
	
	                    # Break out of the infinite while loop if automatic looping is not activated or if convergence has occurred.
	                    if converged or not CONV_LOOP:
	                        break
	
	
	        # Final run.
	        ############
	
	        elif DIFF_MODEL == 'final':
	            # Diffusion model selection.
	            ############################
	
	            # All the global diffusion models to be used in the model selection.
	            self.pipes = ['local_tm', 'sphere', 'prolate', 'oblate', 'ellipsoid']
	
	            # Create the local_tm data pipe.
	            pipe.create('local_tm', 'mf')
	
	            # Load the local tm diffusion model MI results.
	            results.read(file='results', dir=resultsdir + 'local_tm/'+modelselection)
	
	            # Loop over models MII to MV.
	            for model in ['sphere', 'prolate', 'oblate', 'ellipsoid']:
	                # Determine which was the last round of optimisation for each of the models.
	                self.round = self.determine_rnd(model=model) - 1
	
	                # If no directories begining with 'round_' exist, the script has not been properly utilised!
	                if self.round < 1:
	                    # Construct the name of the diffusion tensor.
	                    name = model
	                    if model == 'prolate' or model == 'oblate':
	                        name = name + ' spheroid'
	
	                    # Throw an error to prevent misuse of the script.
	                    raise RelaxError, "Multiple rounds of optimisation of the " + name + " (between 8 to 15) are required for the proper execution of this script."
	
	                # Create the data pipe.
	                pipe.create(model, 'mf')
	
	                # Load the diffusion model results.
	                results.read(file='results', dir=resultsdir + model + '/round_' + `self.round` + '/opt')
	
	            # Model selection between MI to MV.
	            self.model_selection(modsel_pipe='final', write_flag=False)
	
	
	            # Monte Carlo simulations.
	            ##########################
	
	            # Fix the diffusion tensor, if it exists.
	            if hasattr(pipes.get_pipe('final'), 'diff_tensor'):
	                fix('diff')
	
	            # Simulations.
	            monte_carlo.setup(number=MC_NUM)
	            monte_carlo.create_data()
	            monte_carlo.initial_values()
	            minimise(MIN_ALGOR)
	            eliminate()
	            monte_carlo.error_analysis()
	
	
	            # Write the final results.
	            ##########################
	
	            results.write(file='results', dir=resultsdir + 'final', force=True)
	
	
	        # Unknown script behaviour.
	        ###########################
	
	        else:
	            raise RelaxError, "Unknown diffusion model, change the value of 'DIFF_MODEL'"
	
	
	    def convergence(self):
	        """Test for the convergence of the global model."""
	
	        # Alias the data pipes.
	        cdp = pipes.get_pipe()
	        prev_pipe = pipes.get_pipe('previous')
	
	        # Print out.
	        print "\n\n\n"
	        print "#####################"
	        print "# Convergence tests #"
	        print "#####################\n\n"
	
	        # Convergence flags.
	        chi2_converged = True
	        models_converged = True
	        params_converged = True
	
	
	        # Chi-squared test.
	        ###################
	
	        print "Chi-squared test:"
	        print "    chi2 (k-1):          " + `prev_pipe.chi2`
	        print "        (as an IEEE-754 byte array: " + `floatAsByteArray(prev_pipe.chi2)` + ')'
	        print "    chi2 (k):            " + `cdp.chi2`
	        print "        (as an IEEE-754 byte array: " + `floatAsByteArray(cdp.chi2)` + ')'
	        print "    chi2 (difference):   " + `prev_pipe.chi2 - cdp.chi2`
	        if prev_pipe.chi2 == cdp.chi2:
	            print "    The chi-squared value has converged.\n"
	        else:
	            print "    The chi-squared value has not converged.\n"
	            chi2_converged = False
	
	
	        # Identical model-free model test.
	        ##################################
	
	        print "Identical model-free models test:"
	
	        # Create a string representation of the model-free models of the previous data pipe.
	        prev_models = ''
	        for spin in spin_loop(pipe='previous'):
	            if hasattr(spin, 'model'):
	                if not spin.model == 'None':
	                    prev_models = prev_models + spin.model
	
	        # Create a string representation of the model-free models of the current data pipe.
	        curr_models = ''
	        for spin in spin_loop():
	            if hasattr(spin, 'model'):
	                if not spin.model == 'None':
	                    curr_models = curr_models + spin.model
	
	        # The test.
	        if prev_models == curr_models:
	            print "    The model-free models have converged.\n"
	        else:
	            print "    The model-free models have not converged.\n"
	            models_converged = False
	
	
	        # Identical parameter value test.
	        #################################
	
	        print "Identical parameter test:"
	
	        # Only run the tests if the model-free models have converged.
	        if models_converged:
	            # Diffusion parameter array.
	            if DIFF_MODEL == 'sphere':
	                params = ['tm']
	            elif DIFF_MODEL == 'oblate' or DIFF_MODEL == 'prolate':
	                params = ['tm', 'Da', 'theta', 'phi']
	            elif DIFF_MODEL == 'ellipsoid':
	                params = ['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma']
	
	            # Tests.
	            for param in params:
	                # Get the parameter values.
	                prev_val = getattr(prev_pipe.diff_tensor, param)
	                curr_val = getattr(cdp.diff_tensor, param)
	
	                # Test if not identical.
	                if prev_val != curr_val:
	                    print "    Parameter:   " + param
	                    print "    Value (k-1): " + `prev_val`
	                    print "        (as an IEEE-754 byte array: " + `floatAsByteArray(prev_val)` + ')'
	                    print "    Value (k):   " + `curr_val`
	                    print "        (as an IEEE-754 byte array: " + `floatAsByteArray(curr_val)` + ')'
	                    print "    The diffusion parameters have not converged.\n"
	                    params_converged = False
	
	            # Skip the rest if the diffusion tensor parameters have not converged.
	            if params_converged:
	                # Loop over the spins.
	                for mol_index, res_index, spin_index in spin_index_loop():
	                    # Alias the spin containers.
	                    prev_spin = prev_pipe.mol[mol_index].res[res_index].spin[spin_index]
	                    curr_spin = cdp.mol[mol_index].res[res_index].spin[spin_index]
	
	                    # Skip if the parameters have not converged.
	                    if not params_converged:
	                        break
	
	                    # Skip spin systems with no 'params' object.
	                    if not hasattr(prev_spin, 'params') or not hasattr(curr_spin, 'params'):
	                        continue
	
	                    # The spin ID string.
	                    spin_id = generate_spin_id(mol_name=cdp.mol[mol_index].name, res_num=cdp.mol[mol_index].res[res_index].num, res_name=cdp.mol[mol_index].res[res_index].name, spin_num=cdp.mol[mol_index].res[res_index].spin[spin_index].num, spin_name=cdp.mol[mol_index].res[res_index].spin[spin_index].name)
	
	                    # Loop over the parameters.
	                    for j in xrange(len(curr_spin.params)):
	                        # Get the parameter values.
	                        prev_val = getattr(prev_spin, lower(prev_spin.params[j]))
	                        curr_val = getattr(curr_spin, lower(curr_spin.params[j]))
	
	                        # Test if not identical.
	                        if prev_val != curr_val:
	                            print "    Spin ID:     " + `spin_id`
	                            print "    Parameter:   " + curr_spin.params[j]
	                            print "    Value (k-1): " + `prev_val`
	                            print "        (as an IEEE-754 byte array: " + `floatAsByteArray(prev_val)` + ')'
	                            print "    Value (k):   " + `curr_val`
	                            print "        (as an IEEE-754 byte array: " + `floatAsByteArray(prev_val)` + ')'
	                            print "    The model-free parameters have not converged.\n"
	                            params_converged = False
	                            break
	
	        # The model-free models haven't converged hence the parameter values haven't converged.
	        else:
	            print "    The model-free models haven't converged hence the parameters haven't converged.\n"
	            params_converged = False
	
	        # Print out.
	        if params_converged:
	            print "    The diffusion tensor and model-free parameters have converged.\n"
	
	
	        # Final print out.
	        ##################
	
	        print "\nConvergence:"
	        if chi2_converged and models_converged and params_converged:
	            print "    [ Yes ]"
	            return True
	        else:
	            print "    [ No ]"
	            return False
	
	
	    def determine_rnd(self, model=None):
	        """Function for returning the name of next round of optimisation."""
	
	        # Get a list of all files in the directory model.  If no directory exists, set the round to 'init' or 0.
	        try:
	            dir_list = listdir(resultsdir + model)
	        except:
	            return 0
	
	        # Set the round to 'init' or 0 if there is no directory called 'init'.
	        if 'init' not in dir_list:
	            return 0
	
	        # Create a list of all files which begin with 'round_'.
	        rnd_dirs = []
	        for file in dir_list:
	            if search('^round_', file):
	                rnd_dirs.append(file)
	
	        # Create a sorted list of integer round numbers.
	        numbers = []
	        for dir in rnd_dirs:
	            try:
	                numbers.append(int(dir[6:]))
	            except:
	                pass
	        numbers.sort()
	
	        # No directories begining with 'round_' exist, set the round to 1.
	        if not len(numbers):
	            return 1
	
	        # Determine the number for the next round (add 1 to the highest number).
	        return numbers[-1] + 1
	
	
	    def load_tensor(self):
	        """Function for loading the optimised diffusion tensor."""
	
	        # Create the data pipe for the previous data (deleting the old data pipe first if necessary).
	        if pipes.has_pipe('previous'):
	            pipe.delete('previous')
	        pipe.create('previous', 'mf')
	
	        # Load the optimised diffusion tensor from the initial round.
	        if self.round == 1:
	            results.read('results', resultsdir + DIFF_MODEL + '/init')
	
	        # Load the optimised diffusion tensor from the previous round.
	        else:
	            results.read('results', resultsdir + DIFF_MODEL + '/round_' + `self.round - 1` + '/opt')
	
	
	    def model_selection(self, modsel_pipe=None, dir=None, write_flag=True):
	        """Model selection function."""
	
	        # Model elimination.
	        if modsel_pipe != 'final':
	            eliminate()
	
	        # Model selection (delete the model selection pipe if it already exists).
	        if pipes.has_pipe(modsel_pipe):
	            pipe.delete(modsel_pipe)
	        model_selection(method=m_method, modsel_pipe=modsel_pipe, pipes=self.pipes)
	
	        # Write the results.
	        if write_flag:
	            results.write(file='results', dir=dir, force=True)
	
	
	    def multi_model(self, local_tm=False):
	        """Function for optimisation of all model-free models."""
	
	        # Set the data pipe names (also the names of preset model-free models).
	        if local_tm:
	            self.pipes = LOCAL_TM_MODELS
	        else:
	            self.pipes = MF_MODELS
	
	        # Loop over the data pipes.
	        for name in self.pipes:
	            # Create the data pipe.
	            if pipes.has_pipe(name):
	                pipe.delete(name)
	            pipe.create(name, 'mf')
	
	            # Load the sequence.
	            sequence.read(SEQ_ARGS[0], SEQ_ARGS[1], SEQ_ARGS[2], SEQ_ARGS[3], SEQ_ARGS[4], SEQ_ARGS[5], SEQ_ARGS[6], SEQ_ARGS[7])
	
	            # Load the PDB file and calculate the unit vectors parallel to the XH bond.
	            if not local_tm and PDB_FILE:
	                structure.read_pdb(PDB_FILE)
	                structure.vectors(attached='H')
	
	            # Load the relaxation data.
	            for data in RELAX_DATA:
	                relax_data.read(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11], data[12])
	
	            # Deselect spins to be excluded (including unresolved and specifically excluded spins).
	            if UNRES:
	                deselect.read(file=UNRES)
	            if EXCLUDE:
	                deselect.read(file=EXCLUDE)
	
	            # Copy the diffusion tensor from the 'opt' data pipe and prevent it from being minimised.
	            if not local_tm:
	                diffusion_tensor.copy('previous')
	                fix('diff')
	
	            # Set all the necessary values.
	            value.set(BOND_LENGTH, 'bond_length')
	            value.set(CSA, 'csa')
	            value.set(HETNUC, 'heteronucleus')
	            value.set(PROTON, 'proton')
	
	            # Select the model-free model.
	            model_free.select_model(model=name)
	
	            # Minimise.
	            grid_search(inc=GRID_INC)
	            minimise(MIN_ALGOR)
	
	            # Write the results.
	            dir = self.base_dir + name
	            results.write(file='results', dir=dir, force=True)
	
	
	# The main class.
	Model()
	
	print ""
	print ""
	print "_____________________________________________________________________________"
	print ""
	print "calculation finished"
	print ""
	msgbox(msg='Model-free ' + str(model) + ' calculation was successfull !', title='relaxGUI ', ok_button='OK', image=homedir + 'res/pics/relax.gif', root=None)

	#create results file
	if model == 'final':
	   model_free_results(self, target_dir)
	   self.list_modelfree.Append(target_dir + '/final/grace/s2.agr')
           self.list_modelfree.Append(target_dir + '/final/Model-free_Results.txt')
           self.list_modelfree.Append(target_dir + '/final/s2.pml')
           self.list_modelfree.Append(target_dir + '/final/rex.pml')



#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

# GUI


class main(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: main.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        self.notebook_2 = wx.Notebook(self, -1, style=wx.NB_LEFT)
        self.results = wx.Panel(self.notebook_2, -1)
        self.modelfree = wx.Panel(self.notebook_2, -1)
        self.panel_4_copy_1 = wx.Panel(self.modelfree, -1)
        self.panel_4_copy = wx.Panel(self.modelfree, -1)
        self.panel_4 = wx.Panel(self.modelfree, -1)
        self.frq3 = wx.Panel(self.notebook_2, -1)
        self.notebook_3_copy_1 = wx.Notebook(self.frq3, -1, style=0)
        self.t2_1_copy_1 = wx.Panel(self.notebook_3_copy_1, -1)
        self.panel_1_copy_copy_1 = wx.Panel(self.t2_1_copy_1, -1)
        self.panel_3_copy_copy_1 = wx.Panel(self.panel_1_copy_copy_1, -1)
        self.t1_1_copy_1 = wx.Panel(self.notebook_3_copy_1, -1)
        self.panel_1_copy_2 = wx.Panel(self.t1_1_copy_1, -1)
        self.panel_3_copy_2 = wx.Panel(self.panel_1_copy_2, -1)
        self.noe1_copy_1 = wx.Panel(self.notebook_3_copy_1, -1)
        self.frq2 = wx.Panel(self.notebook_2, -1)
        self.notebook_3_copy = wx.Notebook(self.frq2, -1, style=0)
        self.t2_1_copy = wx.Panel(self.notebook_3_copy, -1)
        self.panel_1_copy_copy = wx.Panel(self.t2_1_copy, -1)
        self.panel_3_copy_copy = wx.Panel(self.panel_1_copy_copy, -1)
        self.t1_1_copy = wx.Panel(self.notebook_3_copy, -1)
        self.panel_1_copy_1 = wx.Panel(self.t1_1_copy, -1)
        self.panel_3_copy_1 = wx.Panel(self.panel_1_copy_1, -1)
        self.noe1_copy = wx.Panel(self.notebook_3_copy, -1)
        self.frq1 = wx.Panel(self.notebook_2, -1)
        self.notebook_3 = wx.Notebook(self.frq1, -1, style=0)
        self.t2_1 = wx.Panel(self.notebook_3, -1)
        self.panel_1_copy = wx.Panel(self.t2_1, -1)
        self.panel_3_copy = wx.Panel(self.panel_1_copy, -1)
        self.t1_1 = wx.Panel(self.notebook_3, -1)
        self.panel_1 = wx.Panel(self.t1_1, -1)
        self.panel_3 = wx.Panel(self.panel_1, -1)
        self.noe1 = wx.Panel(self.notebook_3, -1)
        
        # Menu Bar
        self.frame_1_menubar = wx.MenuBar()
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(1, "New", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(2, "Open", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(3, "Save as...", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(4, "Exit", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "File")
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(7, "Settings...", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(8, "Contact relaxGUI", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(9, "Reference", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "Extras")
        wxglade_tmp_menu = wx.Menu()
        wxglade_tmp_menu.Append(10, "Manual", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(5, "About relaxGUI", "", wx.ITEM_NORMAL)
        wxglade_tmp_menu.Append(6, "About relax", "", wx.ITEM_NORMAL)
        self.frame_1_menubar.Append(wxglade_tmp_menu, "Help")
        self.SetMenuBar(self.frame_1_menubar)
        # Menu Bar end


        # NOE 1 no. 1
        self.frame_1_statusbar = self.CreateStatusBar(3, 0)
        self.bitmap_1_copy_1 = wx.StaticBitmap(self.noe1, -1, wx.Bitmap(homedir + "res/pics/noe.gif", wx.BITMAP_TYPE_ANY))
        self.label_4_copy_1 = wx.StaticText(self.noe1, -1, "Set-up for steady-state NOE analysis:\n")
        self.label_2_copy_copy_copy_3 = wx.StaticText(self.noe1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_noe1 = wx.TextCtrl(self.noe1, -1, str(nmrfreq[0]) )
        self.label_2_copy_copy_5 = wx.StaticText(self.noe1, -1, "saturated NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_sat_1 = wx.TextCtrl(self.noe1, -1, noesat[0])
        self.sat_noe_copy_1 = wx.Button(self.noe1, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_2 = wx.StaticText(self.noe1, -1, "saturated NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_sat_err_1 = wx.TextCtrl(self.noe1, -1, str(noesatrmsd[0]))
        self.label_2_copy_copy_1_copy_1 = wx.StaticText(self.noe1, -1, "reference NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_ref_1 = wx.TextCtrl(self.noe1, -1, noeref[0])
        self.noe_ref_err_copy_1 = wx.Button(self.noe1, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_copy_1 = wx.StaticText(self.noe1, -1, "reference NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_ref_err_1 = wx.TextCtrl(self.noe1, -1, str(noerefrmsd[0]))
        self.label_2_copy_copy_2_copy_1 = wx.StaticText(self.noe1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_noe1 = wx.TextCtrl(self.noe1, -1, structure_file_pdb)
        self.structure_noe1.SetEditable(False)
        self.ref_noe_copy_1 = wx.Button(self.noe1, -1, "Add / Change")
        self.label_2_copy_copy_copy_1_copy_1 = wx.StaticText(self.noe1, -1, "Unresolved Residues\nseparated by comma:")
        self.unres_noe1 = wx.TextCtrl(self.noe1, -1, "")
        self.label_2_copy_copy_3_copy_1 = wx.StaticText(self.noe1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.res_noe1 = wx.TextCtrl(self.noe1, -1, noe_savedir[0])
        self.chandir_noe1 = wx.Button(self.noe1, -1, "Change")
        self.label_2_copy_2 = wx.StaticText(self.noe1, -1, "")
        self.label_5_copy_1 = wx.StaticText(self.noe1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_noe1 = wx.BitmapButton(self.noe1, -1, wx.Bitmap(homedir + "res/pics/relax_start.gif", wx.BITMAP_TYPE_ANY))


        # T1 no. 1
        self.bitmap_1_copy_copy = wx.StaticBitmap(self.t1_1, -1, wx.Bitmap(homedir + "res/pics/t1.png", wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy = wx.StaticText(self.t1_1, -1, "Set-up for T1 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy = wx.StaticText(self.t1_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_t11 = wx.TextCtrl(self.t1_1, -1, str(nmrfreq[0]))
        self.label_2_copy_copy_3_copy_copy = wx.StaticText(self.t1_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_t11 = wx.TextCtrl(self.t1_1, -1, t1_savedir[0])
        self.results_directory_copy_copy = wx.Button(self.t1_1, -1, "Change")
        self.structure_file = wx.StaticText(self.t1_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_t11 = wx.TextCtrl(self.t1_1, -1, structure_file_pdb)
        self.structure_t11.SetEditable(False)
        self.results_directory_copy_copy_copy = wx.Button(self.t1_1, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy = wx.StaticText(self.t1_1, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_t11 = wx.TextCtrl(self.t1_1, -1, "")
        self.panel_2 = wx.Panel(self.t1_1, -1)
        self.addt11 = wx.Button(self.panel_1, -1, "add")
        self.refresht11 = wx.Button(self.panel_1, -1, "refresh")
        self.label_3 = wx.StaticText(self.panel_3, -1, "T1 relaxation peak list                                                              ")
        self.label_6 = wx.StaticText(self.panel_3, -1, "Relaxation time [s]")
        self.t1_list_1 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_1 = wx.TextCtrl(self.panel_3, -1, "")
        self.t1_list_2 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_2 = wx.TextCtrl(self.panel_3, -1, "")
        self.t1_list_3 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_3 = wx.TextCtrl(self.panel_3, -1, "")
        self.t1_list_4 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_4 = wx.TextCtrl(self.panel_3, -1, "")
        self.t1_list_5 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_5 = wx.TextCtrl(self.panel_3, -1, "")
        self.t1_list_6 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_6 = wx.TextCtrl(self.panel_3, -1, "")
        self.t1_list_7 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_7 = wx.TextCtrl(self.panel_3, -1, "")
        self.t1_list_8 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_8 = wx.TextCtrl(self.panel_3, -1, "")
        self.t1_list_9 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_9 = wx.TextCtrl(self.panel_3, -1, "")
        self.t1_list_10 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_10 = wx.TextCtrl(self.panel_3, -1, "")
        self.t1_list_11 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_11 = wx.TextCtrl(self.panel_3, -1, "")
        self.t1_list_12 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_12 = wx.TextCtrl(self.panel_3, -1, "")
        self.t1_list_1_copy_11 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_13 = wx.TextCtrl(self.panel_3, -1, "")
        self.t1_list_14 = wx.StaticText(self.panel_3, -1, "")
        self.t1_time_1_4 = wx.TextCtrl(self.panel_3, -1, "")
        self.label_5_copy_1_copy = wx.StaticText(self.t1_1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_t1_1 = wx.BitmapButton(self.t1_1, -1, wx.Bitmap(homedir + "res/pics/relax_start.gif", wx.BITMAP_TYPE_ANY))


        #T2 no. 1
        self.bitmap_1_copy_copy_copy = wx.StaticBitmap(self.t2_1, -1, wx.Bitmap(homedir + "res/pics/t2.png", wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy = wx.StaticText(self.t2_1, -1, "Set-up for T2 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_1 = wx.StaticText(self.t2_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_t21 = wx.TextCtrl(self.t2_1, -1, str(nmrfreq[0]))
        self.label_2_copy_copy_3_copy_copy_copy = wx.StaticText(self.t2_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_t21 = wx.TextCtrl(self.t2_1, -1, t2_savedir[0])
        self.results_directory_t21 = wx.Button(self.t2_1, -1, "Change")
        self.structure_file_copy = wx.StaticText(self.t2_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_t21 = wx.TextCtrl(self.t2_1, -1, structure_file_pdb)
        self.structure_t21.SetEditable(False)
        self.chan_struc_t21 = wx.Button(self.t2_1, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy_copy = wx.StaticText(self.t2_1, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_t21 = wx.TextCtrl(self.t2_1, -1, "")
        self.panel_2_copy = wx.Panel(self.t2_1, -1)
        self.addt21 = wx.Button(self.panel_1_copy, -1, "add")
        self.refresht21 = wx.Button(self.panel_1_copy, -1, "refresh")
        self.label_3_copy = wx.StaticText(self.panel_3_copy, -1, "T2 relaxation peak list                                                              ")
        self.label_6_copy = wx.StaticText(self.panel_3_copy, -1, "Relaxation time [s]")
        self.t2_list_1 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_1 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.t2_list_2 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_2 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.t2_list_3 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_3 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.t2_list_4 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_4 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.t2_list_5 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_5 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.t2_list_6 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_6 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.t2_list_7 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_7 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.t2_list_8 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_8 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.t2_list_9 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_9 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.t2_list_10 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_10 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.t2_list_11 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_11 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.t2_list_12 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_12 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.t2_list_13 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_13 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.t2_list_14 = wx.StaticText(self.panel_3_copy, -1, "")
        self.t2_time_14 = wx.TextCtrl(self.panel_3_copy, -1, "")
        self.label_5_copy_1_copy_copy = wx.StaticText(self.t2_1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_t1_1_copy = wx.BitmapButton(self.t2_1, -1, wx.Bitmap(homedir + "res/pics/relax_start.gif", wx.BITMAP_TYPE_ANY))


        #Noe no.2
        self.bitmap_1_copy_1_copy = wx.StaticBitmap(self.noe1_copy, -1, wx.Bitmap(homedir + "res/pics/noe.gif", wx.BITMAP_TYPE_ANY))
        self.label_4_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "Set-up for steady-state NOE analysis:\n")
        self.label_2_copy_copy_copy_3_copy = wx.StaticText(self.noe1_copy, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_noe1_copy = wx.TextCtrl(self.noe1_copy, -1, str(nmrfreq[1]))
        self.label_2_copy_copy_5_copy = wx.StaticText(self.noe1_copy, -1, "saturated NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_sat_1_copy = wx.TextCtrl(self.noe1_copy, -1, "")
        self.sat_noe_copy_1_copy = wx.Button(self.noe1_copy, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_2_copy = wx.StaticText(self.noe1_copy, -1, "saturated NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_sat_err_1_copy = wx.TextCtrl(self.noe1_copy, -1, "1000")
        self.label_2_copy_copy_1_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "reference NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_ref_1_copy = wx.TextCtrl(self.noe1_copy, -1, "")
        self.noe_ref_err_copy_1_copy = wx.Button(self.noe1_copy, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "reference NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_ref_err_1_copy = wx.TextCtrl(self.noe1_copy, -1, "1000")
        self.label_2_copy_copy_2_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_noe1_copy = wx.TextCtrl(self.noe1_copy, -1, structure_file_pdb)
        self.structure_noe1_copy.SetEditable(False)
        self.ref_noe_copy_1_copy = wx.Button(self.noe1_copy, -1, "Add / Change")
        self.label_2_copy_copy_copy_1_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "Unresolved Residues\nseparated by comma:")
        self.unres_noe1_copy = wx.TextCtrl(self.noe1_copy, -1, "")
        self.label_2_copy_copy_3_copy_1_copy = wx.StaticText(self.noe1_copy, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.res_noe1_copy = wx.TextCtrl(self.noe1_copy, -1, noe_savedir[1])
        self.chandir_noe1_copy = wx.Button(self.noe1_copy, -1, "Change")
        self.label_2_copy_2_copy = wx.StaticText(self.noe1_copy, -1, "")
        self.label_5_copy_1_copy_1 = wx.StaticText(self.noe1_copy, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_noe1_copy = wx.BitmapButton(self.noe1_copy, -1, wx.Bitmap(homedir + "res/pics/relax_start.gif", wx.BITMAP_TYPE_ANY))


        #T1 no. 2
        self.bitmap_1_copy_copy_copy_1 = wx.StaticBitmap(self.t1_1_copy, -1, wx.Bitmap(homedir + "res/pics/t1.png", wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_1 = wx.StaticText(self.t1_1_copy, -1, "Set-up for T1 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_2 = wx.StaticText(self.t1_1_copy, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_t11_copy = wx.TextCtrl(self.t1_1_copy, -1, str(nmrfreq[1]))
        self.label_2_copy_copy_3_copy_copy_copy_1 = wx.StaticText(self.t1_1_copy, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_t11_copy = wx.TextCtrl(self.t1_1_copy, -1, t1_savedir[1])
        self.results_directory_copy_copy_copy_1 = wx.Button(self.t1_1_copy, -1, "Change")
        self.structure_file_copy_1 = wx.StaticText(self.t1_1_copy, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_t11_copy = wx.TextCtrl(self.t1_1_copy, -1, structure_file_pdb)
        self.results_directory_copy_copy_copy_copy = wx.Button(self.t1_1_copy, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy_copy_1 = wx.StaticText(self.t1_1_copy, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_t11_copy = wx.TextCtrl(self.t1_1_copy, -1, "")
        self.panel_2_copy_1 = wx.Panel(self.t1_1_copy, -1)
        self.addt11_copy = wx.Button(self.panel_1_copy_1, -1, "add")
        self.refresht11_copy = wx.Button(self.panel_1_copy_1, -1, "refresh")
        self.label_3_copy_1 = wx.StaticText(self.panel_3_copy_1, -1, "T1 relaxation peak list                                                              ")
        self.label_6_copy_1 = wx.StaticText(self.panel_3_copy_1, -1, "Relaxation time [s]")
        self.t1_list_1_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_1_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.t1_list_2_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_2_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.t1_list_3_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_3_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.t1_list_4_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_4_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.t1_list_5_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_5_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.t1_list_6_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_6_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.t1_list_7_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_7_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.t1_list_8_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_8_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.t1_list_9_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_9_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.t1_list_10_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_10_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.t1_list_11_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_11_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.t1_list_12_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_12_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.t1_list_1_copy_11_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_13_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.t1_list_14_copy = wx.StaticText(self.panel_3_copy_1, -1, "")
        self.t1_time_1_4_copy = wx.TextCtrl(self.panel_3_copy_1, -1, "")
        self.label_5_copy_1_copy_copy_1 = wx.StaticText(self.t1_1_copy, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_t1_1_copy_1 = wx.BitmapButton(self.t1_1_copy, -1, wx.Bitmap(homedir + "res/pics/relax_start.gif", wx.BITMAP_TYPE_ANY))

        #T2 no. 2
        self.bitmap_1_copy_copy_copy_copy = wx.StaticBitmap(self.t2_1_copy, -1, wx.Bitmap(homedir + "res/pics/t2.png", wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_copy = wx.StaticText(self.t2_1_copy, -1, "Set-up for T2 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_1_copy = wx.StaticText(self.t2_1_copy, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_t21_copy = wx.TextCtrl(self.t2_1_copy, -1, str(nmrfreq[1]))
        self.label_2_copy_copy_3_copy_copy_copy_copy = wx.StaticText(self.t2_1_copy, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_t21_copy = wx.TextCtrl(self.t2_1_copy, -1, t2_savedir[1])
        self.results_directory_t21_copy = wx.Button(self.t2_1_copy, -1, "Change")
        self.structure_file_copy_copy = wx.StaticText(self.t2_1_copy, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_t21_copy = wx.TextCtrl(self.t2_1_copy, -1, structure_file_pdb)
        self.structure_t21_copy.SetEditable(False)
        self.chan_struc_t21_copy = wx.Button(self.t2_1_copy, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy = wx.StaticText(self.t2_1_copy, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_t21_copy = wx.TextCtrl(self.t2_1_copy, -1, "")
        self.panel_2_copy_copy = wx.Panel(self.t2_1_copy, -1)
        self.addt21_copy = wx.Button(self.panel_1_copy_copy, -1, "add")
        self.refresht21_copy = wx.Button(self.panel_1_copy_copy, -1, "refresh")
        self.label_3_copy_copy = wx.StaticText(self.panel_3_copy_copy, -1, "T2 relaxation peak list                                                              ")
        self.label_6_copy_copy = wx.StaticText(self.panel_3_copy_copy, -1, "Relaxation time [s]")
        self.t2_list_1_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_1_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.t2_list_2_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_2_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.t2_list_3_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_3_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.t2_list_4_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_4_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.t2_list_5_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_5_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.t2_list_6_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_6_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.t2_list_7_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_7_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.t2_list_8_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_8_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.t2_list_9_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_9_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.t2_list_10_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_10_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.t2_list_11_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_11_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.t2_list_12_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_12_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.t2_list_13_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_13_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.t2_list_14_copy = wx.StaticText(self.panel_3_copy_copy, -1, "")
        self.t2_time_14_copy = wx.TextCtrl(self.panel_3_copy_copy, -1, "")
        self.label_5_copy_1_copy_copy_copy = wx.StaticText(self.t2_1_copy, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_t1_1_copy_copy = wx.BitmapButton(self.t2_1_copy, -1, wx.Bitmap(homedir + "res/pics/relax_start.gif", wx.BITMAP_TYPE_ANY))

        #NOE no. 3
        self.bitmap_1_copy_1_copy_1 = wx.StaticBitmap(self.noe1_copy_1, -1, wx.Bitmap(homedir + "res/pics/noe.gif", wx.BITMAP_TYPE_ANY))
        self.label_4_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "Set-up for steady-state NOE analysis:\n")
        self.label_2_copy_copy_copy_3_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_noe1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, str(nmrfreq[2]))
        self.label_2_copy_copy_5_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "saturated NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_sat_1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, "")
        self.sat_noe_copy_1_copy_1 = wx.Button(self.noe1_copy_1, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_2_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "saturated NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_sat_err_1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, "1000")
        self.label_2_copy_copy_1_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "reference NOE peak list", style=wx.ALIGN_RIGHT)
        self.noe_ref_1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, "")
        self.noe_ref_err_copy_1_copy_1 = wx.Button(self.noe1_copy_1, -1, "Add / Change")
        self.label_2_copy_copy_copy_copy_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "reference NOE background RMSD", style=wx.ALIGN_RIGHT)
        self.noe_ref_err_1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, "1000")
        self.label_2_copy_copy_2_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_noe1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, structure_file_pdb)
        self.structure_noe1_copy_1.SetEditable(False)
        self.ref_noe_copy_1_copy_1 = wx.Button(self.noe1_copy_1, -1, "Add / Change")
        self.label_2_copy_copy_copy_1_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "Unresolved Residues\nseparated by comma:")
        self.unres_noe1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, "")
        self.label_2_copy_copy_3_copy_1_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.res_noe1_copy_1 = wx.TextCtrl(self.noe1_copy_1, -1, noe_savedir[2])
        self.chandir_noe1_copy_1 = wx.Button(self.noe1_copy_1, -1, "Change")
        self.label_2_copy_2_copy_1 = wx.StaticText(self.noe1_copy_1, -1, "")
        self.label_5_copy_1_copy_2 = wx.StaticText(self.noe1_copy_1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_noe1_copy_1 = wx.BitmapButton(self.noe1_copy_1, -1, wx.Bitmap(homedir + "res/pics/relax_start.gif", wx.BITMAP_TYPE_ANY))


        #T1 no. 3
        self.bitmap_1_copy_copy_copy_2 = wx.StaticBitmap(self.t1_1_copy_1, -1, wx.Bitmap(homedir + "res/pics/t1.png", wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_2 = wx.StaticText(self.t1_1_copy_1, -1, "Set-up for T1 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_3 = wx.StaticText(self.t1_1_copy_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_t11_copy_1 = wx.TextCtrl(self.t1_1_copy_1, -1, str(nmrfreq[2]))
        self.label_2_copy_copy_3_copy_copy_copy_2 = wx.StaticText(self.t1_1_copy_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_t11_copy_1 = wx.TextCtrl(self.t1_1_copy_1, -1, t1_savedir[2])
        self.results_directory_copy_copy_copy_2 = wx.Button(self.t1_1_copy_1, -1, "Change")
        self.structure_file_copy_2 = wx.StaticText(self.t1_1_copy_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_t11_copy_1 = wx.TextCtrl(self.t1_1_copy_1, -1, structure_file_pdb)
        self.structure_t11_copy_1.SetEditable(False)
        self.results_directory_copy_copy_copy_copy_1 = wx.Button(self.t1_1_copy_1, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy_copy_2 = wx.StaticText(self.t1_1_copy_1, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_t11_copy_1 = wx.TextCtrl(self.t1_1_copy_1, -1, "")
        self.panel_2_copy_2 = wx.Panel(self.t1_1_copy_1, -1)
        self.addt11_copy_1 = wx.Button(self.panel_1_copy_2, -1, "add")
        self.refresht11_copy_1 = wx.Button(self.panel_1_copy_2, -1, "refresh")
        self.label_3_copy_2 = wx.StaticText(self.panel_3_copy_2, -1, "T1 relaxation peak list                                                              ")
        self.label_6_copy_2 = wx.StaticText(self.panel_3_copy_2, -1, "Relaxation time [s]")
        self.t1_list_1_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_1_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.t1_list_2_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_2_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.t1_list_3_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_3_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.t1_list_4_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_4_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.t1_list_5_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_5_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.t1_list_6_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_6_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.t1_list_7_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_7_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.t1_list_8_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_8_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.t1_list_9_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_9_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.t1_list_10_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_10_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.t1_list_11_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_11_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.t1_list_12_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_12_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.t1_list_1_copy_11_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_13_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.t1_list_14_copy_1 = wx.StaticText(self.panel_3_copy_2, -1, "")
        self.t1_time_1_4_copy_1 = wx.TextCtrl(self.panel_3_copy_2, -1, "")
        self.label_5_copy_1_copy_copy_2 = wx.StaticText(self.t1_1_copy_1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_t1_1_copy_2 = wx.BitmapButton(self.t1_1_copy_1, -1, wx.Bitmap(homedir + "res/pics/relax_start.gif", wx.BITMAP_TYPE_ANY))

        #T2 no. 3
        self.bitmap_1_copy_copy_copy_copy_1 = wx.StaticBitmap(self.t2_1_copy_1, -1, wx.Bitmap(homedir + "res/pics/t2.png", wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_copy_1 = wx.StaticText(self.t2_1_copy_1, -1, "Set-up for T2 relaxation analysis:")
        self.label_2_copy_copy_copy_2_copy_copy_1_copy_1 = wx.StaticText(self.t2_1_copy_1, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        self.nmrfreq_value_t21_copy_1 = wx.TextCtrl(self.t2_1_copy_1, -1, str(nmrfreq[2]))
        self.label_2_copy_copy_3_copy_copy_copy_copy_1 = wx.StaticText(self.t2_1_copy_1, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_t21_copy_1 = wx.TextCtrl(self.t2_1_copy_1, -1, t2_savedir[2])
        self.results_directory_t21_copy_1 = wx.Button(self.t2_1_copy_1, -1, "Change")
        self.structure_file_copy_copy_1 = wx.StaticText(self.t2_1_copy_1, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_t21_copy_1 = wx.TextCtrl(self.t2_1_copy_1, -1, structure_file_pdb)
        self.structure_t21_copy_1.SetEditable(False)
        self.chan_struc_t21_copy_1 = wx.Button(self.t2_1_copy_1, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1 = wx.StaticText(self.t2_1_copy_1, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_t21_copy_1 = wx.TextCtrl(self.t2_1_copy_1, -1, "")
        self.panel_2_copy_copy_1 = wx.Panel(self.t2_1_copy_1, -1)
        self.addt21_copy_1 = wx.Button(self.panel_1_copy_copy_1, -1, "add")
        self.refresht21_copy_1 = wx.Button(self.panel_1_copy_copy_1, -1, "refresh")
        self.label_3_copy_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "T2 relaxation peak list                                                              ")
        self.label_6_copy_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "Relaxation time [s]")
        self.t2_list_1_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_1_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.t2_list_2_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_2_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.t2_list_3_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_3_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.t2_list_4_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_4_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.t2_list_5_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_5_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.t2_list_6_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_6_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.t2_list_7_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_7_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.t2_list_8_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_8_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.t2_list_9_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_9_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.t2_list_10_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_10_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.t2_list_11_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_11_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.t2_list_12_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_12_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.t2_list_13_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_13_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.t2_list_14_copy_1 = wx.StaticText(self.panel_3_copy_copy_1, -1, "")
        self.t2_time_14_copy_1 = wx.TextCtrl(self.panel_3_copy_copy_1, -1, "")
        self.label_5_copy_1_copy_copy_copy_1 = wx.StaticText(self.t2_1_copy_1, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_t1_1_copy_copy_1 = wx.BitmapButton(self.t2_1_copy_1, -1, wx.Bitmap(homedir + "res/pics/relax_start.gif", wx.BITMAP_TYPE_ANY))


        #Model-free
        self.bitmap_2 = wx.StaticBitmap(self.modelfree, -1, wx.Bitmap(homedir + "res/pics/modelfree.png", wx.BITMAP_TYPE_ANY))
        self.label_4_copy_copy_copy_copy_1_copy = wx.StaticText(self.modelfree, -1, "Set-up for Model-free analysis:")
        self.label_7 = wx.StaticText(self.panel_4, -1, "NMR freq 1:")
        self.modelfreefreq1 = wx.TextCtrl(self.panel_4, -1, "")
        self.label_8 = wx.StaticText(self.panel_4, -1, "NOE")
        self.m_noe_1 = wx.TextCtrl(self.panel_4, -1, "")
        self.model_noe_1 = wx.Button(self.panel_4, -1, "+")
        self.label_8_copy = wx.StaticText(self.panel_4, -1, "R1")
        self.m_r1_1 = wx.TextCtrl(self.panel_4, -1, "")
        self.model_r1_1 = wx.Button(self.panel_4, -1, "+")
        self.label_8_copy_copy = wx.StaticText(self.panel_4, -1, "R2")
        self.m_r2_1 = wx.TextCtrl(self.panel_4, -1, "")
        self.model_r2_1 = wx.Button(self.panel_4, -1, "+")
        self.label_7_copy = wx.StaticText(self.panel_4_copy, -1, "NMR freq 2:")
        self.modelfreefreq2 = wx.TextCtrl(self.panel_4_copy, -1, "")
        self.label_8_copy_1 = wx.StaticText(self.panel_4_copy, -1, "NOE")
        self.m_noe_2 = wx.TextCtrl(self.panel_4_copy, -1, "")
        self.model_noe_2 = wx.Button(self.panel_4_copy, -1, "+")
        self.label_8_copy_copy_1 = wx.StaticText(self.panel_4_copy, -1, "R1")
        self.m_r1_2 = wx.TextCtrl(self.panel_4_copy, -1, "")
        self.model_r1_2 = wx.Button(self.panel_4_copy, -1, "+")
        self.label_8_copy_copy_copy = wx.StaticText(self.panel_4_copy, -1, "R2")
        self.m_r2_2 = wx.TextCtrl(self.panel_4_copy, -1, "")
        self.model_r2_2 = wx.Button(self.panel_4_copy, -1, "+")
        self.label_7_copy_copy = wx.StaticText(self.panel_4_copy_1, -1, "NMR freq 3:")
        self.modelfreefreq3 = wx.TextCtrl(self.panel_4_copy_1, -1, "")
        self.label_8_copy_1_copy = wx.StaticText(self.panel_4_copy_1, -1, "NOE")
        self.m_noe_3 = wx.TextCtrl(self.panel_4_copy_1, -1, "")
        self.model_noe_3 = wx.Button(self.panel_4_copy_1, -1, "+")
        self.label_8_copy_copy_1_copy = wx.StaticText(self.panel_4_copy_1, -1, "R1")
        self.m_r1_3 = wx.TextCtrl(self.panel_4_copy_1, -1, "")
        self.model_r1_3 = wx.Button(self.panel_4_copy_1, -1, "+")
        self.label_8_copy_copy_copy_copy = wx.StaticText(self.panel_4_copy_1, -1, "R2")
        self.m_r2_3 = wx.TextCtrl(self.panel_4_copy_1, -1, "")
        self.model_r2_3 = wx.Button(self.panel_4_copy_1, -1, "+")
        self.label_9 = wx.StaticText(self.modelfree, -1, "Select Model-free models (default = all):")
        self.m0 = wx.ToggleButton(self.modelfree, -1, "m0")
        self.m1 = wx.ToggleButton(self.modelfree, -1, "m1")
        self.m2 = wx.ToggleButton(self.modelfree, -1, "m2")
        self.m3 = wx.ToggleButton(self.modelfree, -1, "m3")
        self.m4 = wx.ToggleButton(self.modelfree, -1, "m4")
        self.m5 = wx.ToggleButton(self.modelfree, -1, "m5")
        self.m6 = wx.ToggleButton(self.modelfree, -1, "m6")
        self.m7 = wx.ToggleButton(self.modelfree, -1, "m7")
        self.m8 = wx.ToggleButton(self.modelfree, -1, "m8")
        self.m9 = wx.ToggleButton(self.modelfree, -1, "m9")
        self.label_10 = wx.StaticText(self.modelfree, -1, "Select Model-free selection mode:      ")
        self.aic = wx.RadioButton(self.modelfree, -1, "AIC")
        self.bic = wx.RadioButton(self.modelfree, -1, "BIC")
        self.structure_file_copy_copy_1_copy = wx.StaticText(self.modelfree, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_t21_copy_1_copy = wx.TextCtrl(self.modelfree, -1, structure_file_pdb)
        self.structure_t21_copy_1_copy.SetEditable(False)
        self.chan_struc_t21_copy_1_copy = wx.Button(self.modelfree, -1, "Change")
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1_copy = wx.StaticText(self.modelfree, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_t21_copy_1_copy = wx.TextCtrl(self.modelfree, -1, "")
        self.label_2_copy_copy_3_copy_copy_copy_copy_2 = wx.StaticText(self.modelfree, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_t21_copy_2 = wx.TextCtrl(self.modelfree, -1, results_dir_model)
        self.results_directory_t21_copy_2 = wx.Button(self.modelfree, -1, "Change")
        self.label_5_copy_1_copy_3 = wx.StaticText(self.modelfree, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_modelfree = wx.BitmapButton(self.modelfree, -1, wx.Bitmap(homedir + "res/pics/relax_start.gif", wx.BITMAP_TYPE_ANY))

        ## results
        self.label_11 = wx.StaticText(self.results, -1, "NOE analysis")
        self.list_noe = wx.ListBox(self.results, -1, choices=results_noe)
        self.open_noe_results = wx.Button(self.results, -1, "open")
        self.label_11_copy = wx.StaticText(self.results, -1, "T1 and T2 relaxation analysis")
        self.list_tx = wx.ListBox(self.results, -1, choices=results_tx)
        self.open_tx_results = wx.Button(self.results, -1, "open")
        self.label_11_copy_copy = wx.StaticText(self.results, -1, "Model-free analysis")
        self.list_modelfree = wx.ListBox(self.results, -1, choices=results_model_free)
        self.open_model_results = wx.Button(self.results, -1, "open")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_MENU, self.newGUI, id=1)
        self.Bind(wx.EVT_MENU, self.openGUI, id=2)
        self.Bind(wx.EVT_MENU, self.saveGUI, id=3)
        self.Bind(wx.EVT_MENU, self.exitGUI, id=4)
        self.Bind(wx.EVT_MENU, self.aboutGUI, id=5)
        self.Bind(wx.EVT_MENU, self.aboutrelax, id=6)
        self.Bind(wx.EVT_MENU, self.settings, id=7)
        self.Bind(wx.EVT_MENU, self.references, id=9)
        self.Bind(wx.EVT_BUTTON, self.sat_noe1, self.sat_noe_copy_1)
        self.Bind(wx.EVT_BUTTON, self.ref_noe, self.noe_ref_err_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.ref_noe_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_noe1, self.chandir_noe1)
        self.Bind(wx.EVT_BUTTON, self.exec_noe1, self.relax_start_noe1)
        self.Bind(wx.EVT_BUTTON, self.resdir_t1_1, self.results_directory_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.results_directory_copy_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.add_t1_1, self.addt11)
        self.Bind(wx.EVT_BUTTON, self.refresh_t1_1, self.refresht11)
        self.Bind(wx.EVT_BUTTON, self.exec_t2_1, self.relax_start_t1_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_t2_1, self.results_directory_t21)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.chan_struc_t21)
        self.Bind(wx.EVT_BUTTON, self.add_t2_1, self.addt21)
        self.Bind(wx.EVT_BUTTON, self.refresh_t2_1, self.refresht21)
        self.Bind(wx.EVT_BUTTON, self.exec_t1_1, self.relax_start_t1_1_copy)
        self.Bind(wx.EVT_BUTTON, self.sat_noe2, self.sat_noe_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.ref_noe2, self.noe_ref_err_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.ref_noe_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.resdir_noe2, self.chandir_noe1_copy)
        self.Bind(wx.EVT_BUTTON, self.exec_noe2, self.relax_start_noe1_copy)
        self.Bind(wx.EVT_BUTTON, self.resdir_t1_2, self.results_directory_copy_copy_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.results_directory_copy_copy_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.add_t1_2, self.addt11_copy)
        self.Bind(wx.EVT_BUTTON, self.refresh_t1_2, self.refresht11_copy)
        self.Bind(wx.EVT_BUTTON, self.exec_t1_2, self.relax_start_t1_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_t2_2, self.results_directory_t21_copy)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.chan_struc_t21_copy)
        self.Bind(wx.EVT_BUTTON, self.add_t2_2, self.addt21_copy)
        self.Bind(wx.EVT_BUTTON, self.refresh_t2_2, self.refresht21_copy)
        self.Bind(wx.EVT_BUTTON, self.exec_t2_2, self.relax_start_t1_1_copy_copy)
        self.Bind(wx.EVT_BUTTON, self.sat_noe3, self.sat_noe_copy_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.ref_noe3, self.noe_ref_err_copy_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.ref_noe_copy_1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_noe3, self.chandir_noe1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.exec_noe3, self.relax_start_noe1_copy_1)
        self.Bind(wx.EVT_BUTTON, self.resdir_t1_3, self.results_directory_copy_copy_copy_2)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.results_directory_copy_copy_copy_copy_1)
        self.Bind(wx.EVT_BUTTON, self.add_t1_3, self.addt11_copy_1)
        self.Bind(wx.EVT_BUTTON, self.refresh_t1_3, self.refresht11_copy_1)
        self.Bind(wx.EVT_BUTTON, self.exec_t1_3, self.relax_start_t1_1_copy_2)
        self.Bind(wx.EVT_BUTTON, self.resdir_t2_3, self.results_directory_t21_copy_1)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.chan_struc_t21_copy_1)
        self.Bind(wx.EVT_BUTTON, self.add_t2_3, self.addt21_copy_1)
        self.Bind(wx.EVT_BUTTON, self.refresh_t2_3, self.refresht21_copy_1)
        self.Bind(wx.EVT_BUTTON, self.exec_t2_3, self.relax_start_t1_1_copy_copy_1)
        self.Bind(wx.EVT_BUTTON, self.model_noe1, self.model_noe_1)
        self.Bind(wx.EVT_BUTTON, self.model_r11, self.model_r1_1)
        self.Bind(wx.EVT_BUTTON, self.model_r21, self.model_r2_1)
        self.Bind(wx.EVT_BUTTON, self.model_noe2, self.model_noe_2)
        self.Bind(wx.EVT_BUTTON, self.model_r12, self.model_r1_2)
        self.Bind(wx.EVT_BUTTON, self.model_r22, self.model_r2_2)
        self.Bind(wx.EVT_BUTTON, self.model_noe3, self.model_noe_3)
        self.Bind(wx.EVT_BUTTON, self.model_r13, self.model_r1_3)
        self.Bind(wx.EVT_BUTTON, self.model_r23, self.model_r2_3)
        self.Bind(wx.EVT_RADIOBUTTON, self.sel_aic, self.aic)
        self.Bind(wx.EVT_RADIOBUTTON, self.sel_bic, self.bic)
        self.Bind(wx.EVT_BUTTON, self.structure_pdb, self.chan_struc_t21_copy_1_copy)
        self.Bind(wx.EVT_BUTTON, self.resdir_modelfree, self.results_directory_t21_copy_2)
        self.Bind(wx.EVT_BUTTON, self.exec_model_free, self.relax_start_modelfree)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.open_noe_results_exe, self.list_noe)
        self.Bind(wx.EVT_BUTTON, self.open_noe_results_exe, self.open_noe_results)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.open_tx_results_exe, self.list_tx)
        self.Bind(wx.EVT_BUTTON, self.open_tx_results_exe, self.open_tx_results)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.open_model_results_exe, self.list_modelfree)
        self.Bind(wx.EVT_BUTTON, self.open_model_results_exe, self.open_model_results)
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: main.__set_properties
        self.SetTitle("relaxGUI")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(homedir + "res/pics/relax.gif", wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((1000, 600))
        self.frame_1_statusbar.SetStatusWidths([770, 50, -1])
        # statusbar fields
        frame_1_statusbar_fields = ["relaxGUI (C) by Michael Bieri 2009", "relax:", "waiting"]
        for i in range(len(frame_1_statusbar_fields)):
            self.frame_1_statusbar.SetStatusText(frame_1_statusbar_fields[i], i)
        self.label_4_copy_1.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_3.SetMinSize((230, 17))
        self.nmrfreq_value_noe1.SetMinSize((350, 27))
        self.label_2_copy_copy_5.SetMinSize((230, 17))
        self.noe_sat_1.SetMinSize((350, 27))
        self.sat_noe_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_copy_2.SetMinSize((230, 17))
        self.noe_sat_err_1.SetMinSize((350, 27))
        self.label_2_copy_copy_1_copy_1.SetMinSize((230, 17))
        self.noe_ref_1.SetMinSize((350, 27))
        self.noe_ref_err_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_copy_copy_1.SetMinSize((230, 17))
        self.noe_ref_err_1.SetMinSize((350, 27))
        self.label_2_copy_copy_2_copy_1.SetMinSize((230, 17))
        self.structure_noe1.SetMinSize((350, 27))
        self.ref_noe_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_1_copy_1.SetMinSize((230, 34))
        self.unres_noe1.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_1.SetMinSize((230, 17))
        self.res_noe1.SetMinSize((350, 27))
        self.chandir_noe1.SetMinSize((103, 27))
        self.label_5_copy_1.SetMinSize((118, 17))
        self.relax_start_noe1.SetName('hello')
        self.relax_start_noe1.SetSize(self.relax_start_noe1.GetBestSize())
        self.label_4_copy_copy.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_2_copy.SetMinSize((230, 17))
        self.nmrfreq_value_t11.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy.SetMinSize((230, 17))
        self.resultsdir_t11.SetMinSize((350, 27))
        self.results_directory_copy_copy.SetMinSize((103, 27))
        self.structure_file.SetMinSize((230, 17))
        self.structure_t11.SetMinSize((350, 27))
        self.results_directory_copy_copy_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy.SetMinSize((230, 17))
        self.unresolved_t11.SetMinSize((350, 27))
        self.panel_2.SetMinSize((688, 5))
        self.addt11.SetMinSize((60, 27))
        self.refresht11.SetMinSize((60, 27))
        self.label_3.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_6.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.t1_time_1.SetMinSize((80, 20))
        self.t1_time_2.SetMinSize((80, 20))
        self.t1_time_3.SetMinSize((80, 20))
        self.t1_time_4.SetMinSize((80, 20))
        self.t1_time_5.SetMinSize((80, 20))
        self.t1_time_6.SetMinSize((80, 20))
        self.t1_time_7.SetMinSize((80, 20))
        self.t1_time_8.SetMinSize((80, 20))
        self.t1_time_9.SetMinSize((80, 20))
        self.t1_time_10.SetMinSize((80, 20))
        self.t1_time_11.SetMinSize((80, 20))
        self.t1_time_12.SetMinSize((80, 20))
        self.t1_time_13.SetMinSize((80, 20))
        self.t1_time_1_4.SetMinSize((80, 20))
        self.panel_3.SetMinSize((620, 300))
        self.panel_3.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel_1.SetMinSize((688, 300))
        self.panel_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_5_copy_1_copy.SetMinSize((118, 17))
        self.relax_start_t1_1.SetName('hello')
        self.relax_start_t1_1.SetSize(self.relax_start_t1_1.GetBestSize())
        self.label_4_copy_copy_copy.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_2_copy_copy_1.SetMinSize((230, 17))
        self.nmrfreq_value_t21.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy_copy.SetMinSize((230, 17))
        self.resultsdir_t21.SetMinSize((350, 27))
        self.results_directory_t21.SetMinSize((103, 27))
        self.structure_file_copy.SetMinSize((230, 17))
        self.structure_t21.SetMinSize((350, 27))
        self.chan_struc_t21.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy_copy.SetMinSize((230, 17))
        self.unresolved_t21.SetMinSize((350, 27))
        self.panel_2_copy.SetMinSize((688, 5))
        self.addt21.SetMinSize((60, 27))
        self.refresht21.SetMinSize((60, 27))
        self.label_3_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_6_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.t2_time_1.SetMinSize((80, 20))
        self.t2_time_2.SetMinSize((80, 20))
        self.t2_time_3.SetMinSize((80, 20))
        self.t2_time_4.SetMinSize((80, 20))
        self.t2_time_5.SetMinSize((80, 20))
        self.t2_time_6.SetMinSize((80, 20))
        self.t2_time_7.SetMinSize((80, 20))
        self.t2_time_8.SetMinSize((80, 20))
        self.t2_time_9.SetMinSize((80, 20))
        self.t2_time_10.SetMinSize((80, 20))
        self.t2_time_11.SetMinSize((80, 20))
        self.t2_time_12.SetMinSize((80, 20))
        self.t2_time_13.SetMinSize((80, 20))
        self.t2_time_14.SetMinSize((80, 20))
        self.panel_3_copy.SetMinSize((620, 300))
        self.panel_3_copy.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel_1_copy.SetMinSize((688, 300))
        self.panel_1_copy.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_5_copy_1_copy_copy.SetMinSize((118, 17))
        self.relax_start_t1_1_copy.SetName('hello')
        self.relax_start_t1_1_copy.SetSize(self.relax_start_t1_1_copy.GetBestSize())
        self.label_4_copy_1_copy.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_3_copy.SetMinSize((230, 17))
        self.nmrfreq_value_noe1_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_5_copy.SetMinSize((230, 17))
        self.noe_sat_1_copy.SetMinSize((350, 27))
        self.sat_noe_copy_1_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_copy_2_copy.SetMinSize((230, 17))
        self.noe_sat_err_1_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_1_copy_1_copy.SetMinSize((230, 17))
        self.noe_ref_1_copy.SetMinSize((350, 27))
        self.noe_ref_err_copy_1_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_copy_copy_1_copy.SetMinSize((230, 17))
        self.noe_ref_err_1_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_2_copy_1_copy.SetMinSize((230, 17))
        self.structure_noe1_copy.SetMinSize((350, 27))
        self.ref_noe_copy_1_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_1_copy_1_copy.SetMinSize((230, 34))
        self.unres_noe1_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_1_copy.SetMinSize((230, 17))
        self.res_noe1_copy.SetMinSize((350, 27))
        self.chandir_noe1_copy.SetMinSize((103, 27))
        self.label_5_copy_1_copy_1.SetMinSize((118, 17))
        self.relax_start_noe1_copy.SetName('hello')
        self.relax_start_noe1_copy.SetSize(self.relax_start_noe1_copy.GetBestSize())
        self.label_4_copy_copy_copy_1.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_2_copy_copy_2.SetMinSize((230, 17))
        self.nmrfreq_value_t11_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy_copy_1.SetMinSize((230, 17))
        self.resultsdir_t11_copy.SetMinSize((350, 27))
        self.results_directory_copy_copy_copy_1.SetMinSize((103, 27))
        self.structure_file_copy_1.SetMinSize((230, 17))
        self.structure_t11_copy.SetMinSize((350, 27))
        self.results_directory_copy_copy_copy_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy_copy_1.SetMinSize((230, 17))
        self.unresolved_t11_copy.SetMinSize((350, 27))
        self.panel_2_copy_1.SetMinSize((688, 5))
        self.addt11_copy.SetMinSize((60, 27))
        self.refresht11_copy.SetMinSize((60, 27))
        self.label_3_copy_1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_6_copy_1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.t1_time_1_copy.SetMinSize((80, 20))
        self.t1_time_2_copy.SetMinSize((80, 20))
        self.t1_time_3_copy.SetMinSize((80, 20))
        self.t1_time_4_copy.SetMinSize((80, 20))
        self.t1_time_5_copy.SetMinSize((80, 20))
        self.t1_time_6_copy.SetMinSize((80, 20))
        self.t1_time_7_copy.SetMinSize((80, 20))
        self.t1_time_8_copy.SetMinSize((80, 20))
        self.t1_time_9_copy.SetMinSize((80, 20))
        self.t1_time_10_copy.SetMinSize((80, 20))
        self.t1_time_11_copy.SetMinSize((80, 20))
        self.t1_time_12_copy.SetMinSize((80, 20))
        self.t1_time_13_copy.SetMinSize((80, 20))
        self.t1_time_1_4_copy.SetMinSize((80, 20))
        self.panel_3_copy_1.SetMinSize((620, 300))
        self.panel_3_copy_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel_1_copy_1.SetMinSize((688, 300))
        self.panel_1_copy_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_5_copy_1_copy_copy_1.SetMinSize((118, 17))
        self.relax_start_t1_1_copy_1.SetName('hello')
        self.relax_start_t1_1_copy_1.SetSize(self.relax_start_t1_1_copy_1.GetBestSize())
        self.label_4_copy_copy_copy_copy.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_2_copy_copy_1_copy.SetMinSize((230, 17))
        self.nmrfreq_value_t21_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy_copy_copy.SetMinSize((230, 17))
        self.resultsdir_t21_copy.SetMinSize((350, 27))
        self.results_directory_t21_copy.SetMinSize((103, 27))
        self.structure_file_copy_copy.SetMinSize((230, 17))
        self.structure_t21_copy.SetMinSize((350, 27))
        self.chan_struc_t21_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy.SetMinSize((230, 17))
        self.unresolved_t21_copy.SetMinSize((350, 27))
        self.panel_2_copy_copy.SetMinSize((688, 5))
        self.addt21_copy.SetMinSize((60, 27))
        self.refresht21_copy.SetMinSize((60, 27))
        self.label_3_copy_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_6_copy_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.t2_time_1_copy.SetMinSize((80, 20))
        self.t2_time_2_copy.SetMinSize((80, 20))
        self.t2_time_3_copy.SetMinSize((80, 20))
        self.t2_time_4_copy.SetMinSize((80, 20))
        self.t2_time_5_copy.SetMinSize((80, 20))
        self.t2_time_6_copy.SetMinSize((80, 20))
        self.t2_time_7_copy.SetMinSize((80, 20))
        self.t2_time_8_copy.SetMinSize((80, 20))
        self.t2_time_9_copy.SetMinSize((80, 20))
        self.t2_time_10_copy.SetMinSize((80, 20))
        self.t2_time_11_copy.SetMinSize((80, 20))
        self.t2_time_12_copy.SetMinSize((80, 20))
        self.t2_time_13_copy.SetMinSize((80, 20))
        self.t2_time_14_copy.SetMinSize((80, 20))
        self.panel_3_copy_copy.SetMinSize((620, 300))
        self.panel_3_copy_copy.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel_1_copy_copy.SetMinSize((688, 300))
        self.panel_1_copy_copy.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_5_copy_1_copy_copy_copy.SetMinSize((118, 17))
        self.relax_start_t1_1_copy_copy.SetName('hello')
        self.relax_start_t1_1_copy_copy.SetSize(self.relax_start_t1_1_copy_copy.GetBestSize())
        self.label_4_copy_1_copy_1.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_3_copy_1.SetMinSize((230, 17))
        self.nmrfreq_value_noe1_copy_1.SetMinSize((350, 27))
        self.label_2_copy_copy_5_copy_1.SetMinSize((230, 17))
        self.noe_sat_1_copy_1.SetMinSize((350, 27))
        self.sat_noe_copy_1_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_copy_2_copy_1.SetMinSize((230, 17))
        self.noe_sat_err_1_copy_1.SetMinSize((350, 27))
        self.label_2_copy_copy_1_copy_1_copy_1.SetMinSize((230, 17))
        self.noe_ref_1_copy_1.SetMinSize((350, 27))
        self.noe_ref_err_copy_1_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_copy_copy_1_copy_1.SetMinSize((230, 17))
        self.noe_ref_err_1_copy_1.SetMinSize((350, 27))
        self.label_2_copy_copy_2_copy_1_copy_1.SetMinSize((230, 17))
        self.structure_noe1_copy_1.SetMinSize((350, 27))
        self.ref_noe_copy_1_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_1_copy_1_copy_1.SetMinSize((230, 34))
        self.unres_noe1_copy_1.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_1_copy_1.SetMinSize((230, 17))
        self.res_noe1_copy_1.SetMinSize((350, 27))
        self.chandir_noe1_copy_1.SetMinSize((103, 27))
        self.label_5_copy_1_copy_2.SetMinSize((118, 17))
        self.relax_start_noe1_copy_1.SetName('hello')
        self.relax_start_noe1_copy_1.SetSize(self.relax_start_noe1_copy_1.GetBestSize())
        self.label_4_copy_copy_copy_2.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_2_copy_copy_3.SetMinSize((230, 17))
        self.nmrfreq_value_t11_copy_1.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy_copy_2.SetMinSize((230, 17))
        self.resultsdir_t11_copy_1.SetMinSize((350, 27))
        self.results_directory_copy_copy_copy_2.SetMinSize((103, 27))
        self.structure_file_copy_2.SetMinSize((230, 17))
        self.structure_t11_copy_1.SetMinSize((350, 27))
        self.results_directory_copy_copy_copy_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy_copy_2.SetMinSize((230, 17))
        self.unresolved_t11_copy_1.SetMinSize((350, 27))
        self.panel_2_copy_2.SetMinSize((688, 5))
        self.addt11_copy_1.SetMinSize((60, 27))
        self.refresht11_copy_1.SetMinSize((60, 27))
        self.label_3_copy_2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_6_copy_2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.t1_time_1_copy_1.SetMinSize((80, 20))
        self.t1_time_2_copy_1.SetMinSize((80, 20))
        self.t1_time_3_copy_1.SetMinSize((80, 20))
        self.t1_time_4_copy_1.SetMinSize((80, 20))
        self.t1_time_5_copy_1.SetMinSize((80, 20))
        self.t1_time_6_copy_1.SetMinSize((80, 20))
        self.t1_time_7_copy_1.SetMinSize((80, 20))
        self.t1_time_8_copy_1.SetMinSize((80, 20))
        self.t1_time_9_copy_1.SetMinSize((80, 20))
        self.t1_time_10_copy_1.SetMinSize((80, 20))
        self.t1_time_11_copy_1.SetMinSize((80, 20))
        self.t1_time_12_copy_1.SetMinSize((80, 20))
        self.t1_time_13_copy_1.SetMinSize((80, 20))
        self.t1_time_1_4_copy_1.SetMinSize((80, 20))
        self.panel_3_copy_2.SetMinSize((620, 300))
        self.panel_3_copy_2.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel_1_copy_2.SetMinSize((688, 300))
        self.panel_1_copy_2.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_5_copy_1_copy_copy_2.SetMinSize((118, 17))
        self.relax_start_t1_1_copy_2.SetName('hello')
        self.relax_start_t1_1_copy_2.SetSize(self.relax_start_t1_1_copy_2.GetBestSize())
        self.label_4_copy_copy_copy_copy_1.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_2_copy_copy_copy_2_copy_copy_1_copy_1.SetMinSize((230, 17))
        self.nmrfreq_value_t21_copy_1.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy_copy_copy_1.SetMinSize((230, 17))
        self.resultsdir_t21_copy_1.SetMinSize((350, 27))
        self.results_directory_t21_copy_1.SetMinSize((103, 27))
        self.structure_file_copy_copy_1.SetMinSize((230, 17))
        self.structure_t21_copy_1.SetMinSize((350, 27))
        self.chan_struc_t21_copy_1.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1.SetMinSize((230, 17))
        self.unresolved_t21_copy_1.SetMinSize((350, 27))
        self.panel_2_copy_copy_1.SetMinSize((688, 5))
        self.addt21_copy_1.SetMinSize((60, 27))
        self.refresht21_copy_1.SetMinSize((60, 27))
        self.label_3_copy_copy_1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.label_6_copy_copy_1.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.t2_time_1_copy_1.SetMinSize((80, 20))
        self.t2_time_2_copy_1.SetMinSize((80, 20))
        self.t2_time_3_copy_1.SetMinSize((80, 20))
        self.t2_time_4_copy_1.SetMinSize((80, 20))
        self.t2_time_5_copy_1.SetMinSize((80, 20))
        self.t2_time_6_copy_1.SetMinSize((80, 20))
        self.t2_time_7_copy_1.SetMinSize((80, 20))
        self.t2_time_8_copy_1.SetMinSize((80, 20))
        self.t2_time_9_copy_1.SetMinSize((80, 20))
        self.t2_time_10_copy_1.SetMinSize((80, 20))
        self.t2_time_11_copy_1.SetMinSize((80, 20))
        self.t2_time_12_copy_1.SetMinSize((80, 20))
        self.t2_time_13_copy_1.SetMinSize((80, 20))
        self.t2_time_14_copy_1.SetMinSize((80, 20))
        self.panel_3_copy_copy_1.SetMinSize((620, 300))
        self.panel_3_copy_copy_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.panel_1_copy_copy_1.SetMinSize((688, 300))
        self.panel_1_copy_copy_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_5_copy_1_copy_copy_copy_1.SetMinSize((118, 17))
        self.relax_start_t1_1_copy_copy_1.SetName('hello')
        self.relax_start_t1_1_copy_copy_1.SetSize(self.relax_start_t1_1_copy_copy_1.GetBestSize())
        self.label_4_copy_copy_copy_copy_1_copy.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.label_7.SetMinSize((80, 17))
        self.modelfreefreq1.SetMinSize((80, 20))
        self.label_8.SetMinSize((80, 17))
        self.m_noe_1.SetMinSize((120, 20))
        self.model_noe_1.SetMinSize((20, 20))
        self.model_noe_1.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_8_copy.SetMinSize((80, 17))
        self.m_r1_1.SetMinSize((120, 20))
        self.model_r1_1.SetMinSize((20, 20))
        self.model_r1_1.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_8_copy_copy.SetMinSize((80, 17))
        self.m_r2_1.SetMinSize((120, 20))
        self.model_r2_1.SetMinSize((20, 20))
        self.model_r2_1.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.panel_4.SetMinSize((230, 85))
        self.panel_4.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.label_7_copy.SetMinSize((80, 17))
        self.modelfreefreq2.SetMinSize((80, 20))
        self.label_8_copy_1.SetMinSize((80, 17))
        self.m_noe_2.SetMinSize((120, 20))
        self.model_noe_2.SetMinSize((20, 20))
        self.model_noe_2.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_8_copy_copy_1.SetMinSize((80, 17))
        self.m_r1_2.SetMinSize((120, 20))
        self.model_r1_2.SetMinSize((20, 20))
        self.model_r1_2.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_8_copy_copy_copy.SetMinSize((80, 17))
        self.m_r2_2.SetMinSize((120, 20))
        self.model_r2_2.SetMinSize((20, 20))
        self.model_r2_2.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.panel_4_copy.SetMinSize((230, 85))
        self.panel_4_copy.SetBackgroundColour(wx.Colour(176, 176, 176))
        self.label_7_copy_copy.SetMinSize((80, 17))
        self.modelfreefreq3.SetMinSize((80, 20))
        self.label_8_copy_1_copy.SetMinSize((80, 17))
        self.m_noe_3.SetMinSize((120, 20))
        self.model_noe_3.SetMinSize((20, 20))
        self.model_noe_3.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_8_copy_copy_1_copy.SetMinSize((80, 17))
        self.m_r1_3.SetMinSize((120, 20))
        self.model_r1_3.SetMinSize((20, 20))
        self.model_r1_3.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_8_copy_copy_copy_copy.SetMinSize((80, 17))
        self.m_r2_3.SetMinSize((120, 20))
        self.model_r2_3.SetMinSize((20, 20))
        self.model_r2_3.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.panel_4_copy_1.SetMinSize((230, 85))
        self.panel_4_copy_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.m0.SetMinSize((70, 25))
        self.m0.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m0.SetToolTipString("{}")
        self.m0.SetValue(1)
        self.m1.SetMinSize((70, 25))
        self.m1.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m1.SetToolTipString("{S2}")
        self.m1.SetValue(1)
        self.m2.SetMinSize((70, 25))
        self.m2.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m2.SetToolTipString("{S2, te}")
        self.m2.SetValue(1)
        self.m3.SetMinSize((70, 25))
        self.m3.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m3.SetToolTipString("{S2, Rex}")
        self.m3.SetValue(1)
        self.m4.SetMinSize((70, 25))
        self.m4.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m4.SetToolTipString("{S2, te, Rex}")
        self.m4.SetValue(1)
        self.m5.SetMinSize((70, 25))
        self.m5.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m5.SetToolTipString("{S2, S2f, ts}")
        self.m5.SetValue(1)
        self.m6.SetMinSize((70, 25))
        self.m6.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m6.SetToolTipString("{S2, tf, S2f, t2}")
        self.m6.SetValue(1)
        self.m7.SetMinSize((70, 25))
        self.m7.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m7.SetToolTipString("{S2, S2f, ts, Rex}")
        self.m7.SetValue(1)
        self.m8.SetMinSize((70, 25))
        self.m8.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m8.SetToolTipString("{S2, tf, S2f, ts, Rex}")
        self.m8.SetValue(1)
        self.m9.SetMinSize((70, 25))
        self.m9.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m9.SetToolTipString("{Rex}")
        self.m9.SetValue(1)
        self.label_10.SetMinSize((240, 17))
        self.label_10.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.aic.SetMinSize((60, 22))
        self.structure_file_copy_copy_1_copy.SetMinSize((240, 17))
        self.structure_file_copy_copy_1_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.structure_t21_copy_1_copy.SetMinSize((350, 27))
        self.chan_struc_t21_copy_1_copy.SetMinSize((103, 27))
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1_copy.SetMinSize((240, 17))
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.unresolved_t21_copy_1_copy.SetMinSize((350, 27))
        self.label_2_copy_copy_3_copy_copy_copy_copy_2.SetMinSize((240, 17))
        self.label_2_copy_copy_3_copy_copy_copy_copy_2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.resultsdir_t21_copy_2.SetMinSize((350, 27))
        self.results_directory_t21_copy_2.SetMinSize((103, 27))
        self.label_5_copy_1_copy_3.SetMinSize((118, 17))
        self.label_5_copy_1_copy_3.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.relax_start_modelfree.SetName('hello')
        self.relax_start_modelfree.SetSize(self.relax_start_modelfree.GetBestSize())
        self.modelfree.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.label_11.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.list_noe.SetMinSize((800, 150))
        self.list_noe.SetSelection(0)
        self.open_noe_results.SetMinSize((80, 32))
        self.label_11_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.list_tx.SetMinSize((800, 150))
        self.list_tx.SetSelection(0)
        self.open_tx_results.SetMinSize((80, 32))
        self.label_11_copy_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.list_modelfree.SetMinSize((800, 150))
        self.list_modelfree.SetSelection(0)
        self.open_model_results.SetMinSize((80, 32))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: main.__do_layout
        sizer_8 = wx.BoxSizer(wx.VERTICAL)
        sizer_9 = wx.BoxSizer(wx.VERTICAL)
        sizer_22_copy_copy = wx.BoxSizer(wx.VERTICAL)
        sizer_23_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_22_copy = wx.BoxSizer(wx.VERTICAL)
        sizer_23_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_22 = wx.BoxSizer(wx.VERTICAL)
        sizer_23 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_14 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_15 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_3 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_1_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_21 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_20 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_16 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_17_copy_copy = wx.BoxSizer(wx.VERTICAL)
        sizer_19_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_18_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_17_copy = wx.BoxSizer(wx.VERTICAL)
        sizer_19_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_18_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_17 = wx.BoxSizer(wx.VERTICAL)
        sizer_19_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_18 = wx.BoxSizer(wx.HORIZONTAL)
        frq1sub_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11_copy_copy_1 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1_copy_copy_1 = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13_copy_copy_1 = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11_copy_2 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1_copy_2 = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13_copy_2 = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_3 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6_copy_1_copy_1 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        unresolved_resi_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        pdbfile_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8_copy_copy_copy_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        noe_ref_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_err_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        frq1sub_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11_copy_copy = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1_copy_copy = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13_copy_copy = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11_copy_1 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1_copy_1 = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13_copy_1 = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6_copy_1_copy = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        unresolved_resi_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        pdbfile_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8_copy_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        noe_ref_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_err_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        frq1sub = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11_copy = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12_copy = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1_copy = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13_copy = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_10 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_11 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1 = wx.FlexGridSizer(10, 2, 0, 0)
        sizer_13 = wx.BoxSizer(wx.VERTICAL)
        nmr_freq_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6_copy_1 = wx.BoxSizer(wx.VERTICAL)
        exec_relax_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        results_dir_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        unresolved_resi_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        pdbfile_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_8_copy_copy_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        noe_ref_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_err_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        noe_sat_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5_copy_1.Add(self.bitmap_1_copy_1, 0, wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1.Add(self.label_4_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_1.Add(self.label_2_copy_copy_copy_3, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_1.Add(self.nmrfreq_value_noe1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1.Add(nmr_freq_copy_1, 1, wx.EXPAND, 0)
        noe_sat_copy_1.Add(self.label_2_copy_copy_5, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_copy_1.Add(self.noe_sat_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_copy_1.Add(self.sat_noe_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1.Add(noe_sat_copy_1, 1, wx.EXPAND, 0)
        noe_sat_err_copy_1.Add(self.label_2_copy_copy_copy_copy_2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_err_copy_1.Add(self.noe_sat_err_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1.Add(noe_sat_err_copy_1, 1, wx.EXPAND, 0)
        noe_ref_copy_1.Add(self.label_2_copy_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_ref_copy_1.Add(self.noe_ref_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_ref_copy_1.Add(self.noe_ref_err_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1.Add(noe_ref_copy_1, 1, wx.EXPAND, 0)
        sizer_8_copy_copy_copy_copy_1.Add(self.label_2_copy_copy_copy_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_8_copy_copy_copy_copy_1.Add(self.noe_ref_err_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1.Add(sizer_8_copy_copy_copy_copy_1, 1, wx.EXPAND, 0)
        pdbfile_copy_1.Add(self.label_2_copy_copy_2_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        pdbfile_copy_1.Add(self.structure_noe1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        pdbfile_copy_1.Add(self.ref_noe_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1.Add(pdbfile_copy_1, 1, wx.EXPAND, 0)
        unresolved_resi_copy_1.Add(self.label_2_copy_copy_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        unresolved_resi_copy_1.Add(self.unres_noe1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1.Add(unresolved_resi_copy_1, 1, wx.EXPAND, 0)
        results_dir_copy_1.Add(self.label_2_copy_copy_3_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_1.Add(self.res_noe1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_1.Add(self.chandir_noe1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1.Add(results_dir_copy_1, 1, wx.EXPAND, 0)
        sizer_2_copy_1.Add(self.label_2_copy_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1.Add(sizer_2_copy_1, 1, wx.EXPAND, 0)
        exec_relax_copy_1.Add(self.label_5_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1.Add(self.relax_start_noe1, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1.Add(exec_relax_copy_1, 1, wx.ALIGN_RIGHT, 0)
        sizer_5_copy_1.Add(sizer_6_copy_1, 1, wx.EXPAND|wx.SHAPED, 0)
        self.noe1.SetSizer(sizer_5_copy_1)
        sizer_10.Add(self.bitmap_1_copy_copy, 0, wx.ADJUST_MINSIZE, 10)
        sizer_11.Add(self.label_4_copy_copy, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        nmr_freq_copy_copy.Add(self.label_2_copy_copy_copy_2_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy.Add(self.nmrfreq_value_t11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11.Add(nmr_freq_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy.Add(self.label_2_copy_copy_3_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy.Add(self.resultsdir_t11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy.Add(self.results_directory_copy_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11.Add(results_dir_copy_copy, 1, wx.EXPAND, 0)
        results_dir_copy_copy_copy.Add(self.structure_file, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy.Add(self.structure_t11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy.Add(self.results_directory_copy_copy_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11.Add(results_dir_copy_copy_copy, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy.Add(self.label_2_copy_copy_copy_2_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy.Add(self.unresolved_t11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11.Add(nmr_freq_copy_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_11.Add(self.panel_2, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_13.Add(self.addt11, 0, wx.ADJUST_MINSIZE, 0)
        sizer_13.Add(self.refresht11, 0, wx.ADJUST_MINSIZE, 0)
        sizer_12.Add(sizer_13, 1, wx.EXPAND, 0)
        grid_sizer_1.Add(self.label_3, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.label_6, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_2, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_2, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_3, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_3, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_4, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_4, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_5, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_5, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_6, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_6, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_7, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_7, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_8, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_8, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_9, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_9, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_10, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_10, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_11, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_11, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_12, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_12, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_1_copy_11, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_13, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_list_14, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1.Add(self.t1_time_1_4, 0, wx.ADJUST_MINSIZE, 0)
        self.panel_3.SetSizer(grid_sizer_1)
        sizer_12.Add(self.panel_3, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_1.SetSizer(sizer_12)
        sizer_11.Add(self.panel_1, 0, wx.EXPAND|wx.SHAPED, 0)
        exec_relax_copy_1_copy.Add(self.label_5_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy.Add(self.relax_start_t1_1, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_11.Add(exec_relax_copy_1_copy, 0, wx.ALIGN_RIGHT, 0)
        sizer_10.Add(sizer_11, 0, 0, 0)
        self.t1_1.SetSizer(sizer_10)
        sizer_10_copy.Add(self.bitmap_1_copy_copy_copy, 0, wx.ADJUST_MINSIZE, 10)
        sizer_11_copy.Add(self.label_4_copy_copy_copy, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        nmr_freq_copy_copy_copy_1.Add(self.label_2_copy_copy_copy_2_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_1.Add(self.nmrfreq_value_t21, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy.Add(nmr_freq_copy_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy_copy_1.Add(self.label_2_copy_copy_3_copy_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1.Add(self.resultsdir_t21, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1.Add(self.results_directory_t21, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy.Add(results_dir_copy_copy_copy_1, 1, wx.EXPAND, 0)
        results_dir_copy_copy_copy_copy.Add(self.structure_file_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy.Add(self.structure_t21, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy.Add(self.chan_struc_t21, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy.Add(results_dir_copy_copy_copy_copy, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy_copy.Add(self.label_2_copy_copy_copy_2_copy_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_copy.Add(self.unresolved_t21, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy.Add(nmr_freq_copy_copy_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_11_copy.Add(self.panel_2_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_13_copy.Add(self.addt21, 0, wx.ADJUST_MINSIZE, 0)
        sizer_13_copy.Add(self.refresht21, 0, wx.ADJUST_MINSIZE, 0)
        sizer_12_copy.Add(sizer_13_copy, 1, wx.EXPAND, 0)
        grid_sizer_1_copy.Add(self.label_3_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.label_6_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_2, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_2, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_3, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_3, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_4, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_4, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_5, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_5, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_6, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_6, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_7, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_7, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_8, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_8, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_9, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_9, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_10, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_10, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_11, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_11, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_12, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_12, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_13, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_13, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_list_14, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.t2_time_14, 0, wx.ADJUST_MINSIZE, 0)
        self.panel_3_copy.SetSizer(grid_sizer_1_copy)
        sizer_12_copy.Add(self.panel_3_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_1_copy.SetSizer(sizer_12_copy)
        sizer_11_copy.Add(self.panel_1_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        exec_relax_copy_1_copy_copy.Add(self.label_5_copy_1_copy_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_copy.Add(self.relax_start_t1_1_copy, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy.Add(exec_relax_copy_1_copy_copy, 0, wx.ALIGN_RIGHT, 0)
        sizer_10_copy.Add(sizer_11_copy, 0, 0, 0)
        self.t2_1.SetSizer(sizer_10_copy)
        self.notebook_3.AddPage(self.noe1, "steady-state NOE")
        self.notebook_3.AddPage(self.t1_1, "T1 relaxation")
        self.notebook_3.AddPage(self.t2_1, "T2 relaxation")
        frq1sub.Add(self.notebook_3, 1, wx.EXPAND, 0)
        self.frq1.SetSizer(frq1sub)
        sizer_5_copy_1_copy.Add(self.bitmap_1_copy_1_copy, 0, wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy.Add(self.label_4_copy_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_1_copy.Add(self.label_2_copy_copy_copy_3_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_1_copy.Add(self.nmrfreq_value_noe1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy.Add(nmr_freq_copy_1_copy, 1, wx.EXPAND, 0)
        noe_sat_copy_1_copy.Add(self.label_2_copy_copy_5_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_copy_1_copy.Add(self.noe_sat_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_copy_1_copy.Add(self.sat_noe_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy.Add(noe_sat_copy_1_copy, 1, wx.EXPAND, 0)
        noe_sat_err_copy_1_copy.Add(self.label_2_copy_copy_copy_copy_2_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_err_copy_1_copy.Add(self.noe_sat_err_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy.Add(noe_sat_err_copy_1_copy, 1, wx.EXPAND, 0)
        noe_ref_copy_1_copy.Add(self.label_2_copy_copy_1_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_ref_copy_1_copy.Add(self.noe_ref_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_ref_copy_1_copy.Add(self.noe_ref_err_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy.Add(noe_ref_copy_1_copy, 1, wx.EXPAND, 0)
        sizer_8_copy_copy_copy_copy_1_copy.Add(self.label_2_copy_copy_copy_copy_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_8_copy_copy_copy_copy_1_copy.Add(self.noe_ref_err_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy.Add(sizer_8_copy_copy_copy_copy_1_copy, 1, wx.EXPAND, 0)
        pdbfile_copy_1_copy.Add(self.label_2_copy_copy_2_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        pdbfile_copy_1_copy.Add(self.structure_noe1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        pdbfile_copy_1_copy.Add(self.ref_noe_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy.Add(pdbfile_copy_1_copy, 1, wx.EXPAND, 0)
        unresolved_resi_copy_1_copy.Add(self.label_2_copy_copy_copy_1_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        unresolved_resi_copy_1_copy.Add(self.unres_noe1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy.Add(unresolved_resi_copy_1_copy, 1, wx.EXPAND, 0)
        results_dir_copy_1_copy.Add(self.label_2_copy_copy_3_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_1_copy.Add(self.res_noe1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_1_copy.Add(self.chandir_noe1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy.Add(results_dir_copy_1_copy, 1, wx.EXPAND, 0)
        sizer_2_copy_1_copy.Add(self.label_2_copy_2_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy.Add(sizer_2_copy_1_copy, 1, wx.EXPAND, 0)
        exec_relax_copy_1_copy_1.Add(self.label_5_copy_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_1.Add(self.relax_start_noe1_copy, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy.Add(exec_relax_copy_1_copy_1, 1, wx.ALIGN_RIGHT, 0)
        sizer_5_copy_1_copy.Add(sizer_6_copy_1_copy, 1, wx.EXPAND|wx.SHAPED, 0)
        self.noe1_copy.SetSizer(sizer_5_copy_1_copy)
        sizer_10_copy_1.Add(self.bitmap_1_copy_copy_copy_1, 0, wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_1.Add(self.label_4_copy_copy_copy_1, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        nmr_freq_copy_copy_copy_2.Add(self.label_2_copy_copy_copy_2_copy_copy_2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_2.Add(self.nmrfreq_value_t11_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_1.Add(nmr_freq_copy_copy_copy_2, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy_copy_2.Add(self.label_2_copy_copy_3_copy_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_2.Add(self.resultsdir_t11_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_2.Add(self.results_directory_copy_copy_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_1.Add(results_dir_copy_copy_copy_2, 1, wx.EXPAND, 0)
        results_dir_copy_copy_copy_copy_1.Add(self.structure_file_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_1.Add(self.structure_t11_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_1.Add(self.results_directory_copy_copy_copy_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_1.Add(results_dir_copy_copy_copy_copy_1, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy_copy_1.Add(self.label_2_copy_copy_copy_2_copy_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_copy_1.Add(self.unresolved_t11_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_1.Add(nmr_freq_copy_copy_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_11_copy_1.Add(self.panel_2_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_13_copy_1.Add(self.addt11_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_13_copy_1.Add(self.refresht11_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_12_copy_1.Add(sizer_13_copy_1, 1, wx.EXPAND, 0)
        grid_sizer_1_copy_1.Add(self.label_3_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.label_6_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_2_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_2_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_3_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_3_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_4_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_4_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_5_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_5_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_6_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_6_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_7_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_7_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_8_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_8_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_9_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_9_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_10_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_10_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_11_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_11_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_12_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_12_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_1_copy_11_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_13_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_list_14_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_1.Add(self.t1_time_1_4_copy, 0, wx.ADJUST_MINSIZE, 0)
        self.panel_3_copy_1.SetSizer(grid_sizer_1_copy_1)
        sizer_12_copy_1.Add(self.panel_3_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_1_copy_1.SetSizer(sizer_12_copy_1)
        sizer_11_copy_1.Add(self.panel_1_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        exec_relax_copy_1_copy_copy_1.Add(self.label_5_copy_1_copy_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_copy_1.Add(self.relax_start_t1_1_copy_1, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_1.Add(exec_relax_copy_1_copy_copy_1, 0, wx.ALIGN_RIGHT, 0)
        sizer_10_copy_1.Add(sizer_11_copy_1, 0, 0, 0)
        self.t1_1_copy.SetSizer(sizer_10_copy_1)
        sizer_10_copy_copy.Add(self.bitmap_1_copy_copy_copy_copy, 0, wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_copy.Add(self.label_4_copy_copy_copy_copy, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        nmr_freq_copy_copy_copy_1_copy.Add(self.label_2_copy_copy_copy_2_copy_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_1_copy.Add(self.nmrfreq_value_t21_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_copy.Add(nmr_freq_copy_copy_copy_1_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy_copy_1_copy.Add(self.label_2_copy_copy_3_copy_copy_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy.Add(self.resultsdir_t21_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy.Add(self.results_directory_t21_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_copy.Add(results_dir_copy_copy_copy_1_copy, 1, wx.EXPAND, 0)
        results_dir_copy_copy_copy_copy_copy.Add(self.structure_file_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy.Add(self.structure_t21_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy.Add(self.chan_struc_t21_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_copy.Add(results_dir_copy_copy_copy_copy_copy, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy_copy_copy.Add(self.label_2_copy_copy_copy_2_copy_copy_copy_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_copy_copy.Add(self.unresolved_t21_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_copy.Add(nmr_freq_copy_copy_copy_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_11_copy_copy.Add(self.panel_2_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_13_copy_copy.Add(self.addt21_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_13_copy_copy.Add(self.refresht21_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_12_copy_copy.Add(sizer_13_copy_copy, 1, wx.EXPAND, 0)
        grid_sizer_1_copy_copy.Add(self.label_3_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.label_6_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_2_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_2_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_3_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_3_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_4_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_4_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_5_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_5_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_6_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_6_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_7_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_7_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_8_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_8_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_9_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_9_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_10_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_10_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_11_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_11_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_12_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_12_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_13_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_13_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_list_14_copy, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy.Add(self.t2_time_14_copy, 0, wx.ADJUST_MINSIZE, 0)
        self.panel_3_copy_copy.SetSizer(grid_sizer_1_copy_copy)
        sizer_12_copy_copy.Add(self.panel_3_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_1_copy_copy.SetSizer(sizer_12_copy_copy)
        sizer_11_copy_copy.Add(self.panel_1_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        exec_relax_copy_1_copy_copy_copy.Add(self.label_5_copy_1_copy_copy_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_copy_copy.Add(self.relax_start_t1_1_copy_copy, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_copy.Add(exec_relax_copy_1_copy_copy_copy, 0, wx.ALIGN_RIGHT, 0)
        sizer_10_copy_copy.Add(sizer_11_copy_copy, 0, 0, 0)
        self.t2_1_copy.SetSizer(sizer_10_copy_copy)
        self.notebook_3_copy.AddPage(self.noe1_copy, "steady-state NOE")
        self.notebook_3_copy.AddPage(self.t1_1_copy, "T1 relaxation")
        self.notebook_3_copy.AddPage(self.t2_1_copy, "T2 relaxation")
        frq1sub_copy.Add(self.notebook_3_copy, 1, wx.EXPAND, 0)
        self.frq2.SetSizer(frq1sub_copy)
        sizer_5_copy_1_copy_1.Add(self.bitmap_1_copy_1_copy_1, 0, wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy_1.Add(self.label_4_copy_1_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_1_copy_1.Add(self.label_2_copy_copy_copy_3_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_1_copy_1.Add(self.nmrfreq_value_noe1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy_1.Add(nmr_freq_copy_1_copy_1, 1, wx.EXPAND, 0)
        noe_sat_copy_1_copy_1.Add(self.label_2_copy_copy_5_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_copy_1_copy_1.Add(self.noe_sat_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_copy_1_copy_1.Add(self.sat_noe_copy_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy_1.Add(noe_sat_copy_1_copy_1, 1, wx.EXPAND, 0)
        noe_sat_err_copy_1_copy_1.Add(self.label_2_copy_copy_copy_copy_2_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_sat_err_copy_1_copy_1.Add(self.noe_sat_err_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy_1.Add(noe_sat_err_copy_1_copy_1, 1, wx.EXPAND, 0)
        noe_ref_copy_1_copy_1.Add(self.label_2_copy_copy_1_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_ref_copy_1_copy_1.Add(self.noe_ref_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        noe_ref_copy_1_copy_1.Add(self.noe_ref_err_copy_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy_1.Add(noe_ref_copy_1_copy_1, 1, wx.EXPAND, 0)
        sizer_8_copy_copy_copy_copy_1_copy_1.Add(self.label_2_copy_copy_copy_copy_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_8_copy_copy_copy_copy_1_copy_1.Add(self.noe_ref_err_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy_1.Add(sizer_8_copy_copy_copy_copy_1_copy_1, 1, wx.EXPAND, 0)
        pdbfile_copy_1_copy_1.Add(self.label_2_copy_copy_2_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        pdbfile_copy_1_copy_1.Add(self.structure_noe1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        pdbfile_copy_1_copy_1.Add(self.ref_noe_copy_1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy_1.Add(pdbfile_copy_1_copy_1, 1, wx.EXPAND, 0)
        unresolved_resi_copy_1_copy_1.Add(self.label_2_copy_copy_copy_1_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        unresolved_resi_copy_1_copy_1.Add(self.unres_noe1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy_1.Add(unresolved_resi_copy_1_copy_1, 1, wx.EXPAND, 0)
        results_dir_copy_1_copy_1.Add(self.label_2_copy_copy_3_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_1_copy_1.Add(self.res_noe1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_1_copy_1.Add(self.chandir_noe1_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_6_copy_1_copy_1.Add(results_dir_copy_1_copy_1, 1, wx.EXPAND, 0)
        sizer_2_copy_1_copy_1.Add(self.label_2_copy_2_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy_1.Add(sizer_2_copy_1_copy_1, 1, wx.EXPAND, 0)
        exec_relax_copy_1_copy_2.Add(self.label_5_copy_1_copy_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_2.Add(self.relax_start_noe1_copy_1, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_6_copy_1_copy_1.Add(exec_relax_copy_1_copy_2, 1, wx.ALIGN_RIGHT, 0)
        sizer_5_copy_1_copy_1.Add(sizer_6_copy_1_copy_1, 1, wx.EXPAND|wx.SHAPED, 0)
        self.noe1_copy_1.SetSizer(sizer_5_copy_1_copy_1)
        sizer_10_copy_2.Add(self.bitmap_1_copy_copy_copy_2, 0, wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_2.Add(self.label_4_copy_copy_copy_2, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        nmr_freq_copy_copy_copy_3.Add(self.label_2_copy_copy_copy_2_copy_copy_3, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_3.Add(self.nmrfreq_value_t11_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_2.Add(nmr_freq_copy_copy_copy_3, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy_copy_3.Add(self.label_2_copy_copy_3_copy_copy_copy_2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_3.Add(self.resultsdir_t11_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_3.Add(self.results_directory_copy_copy_copy_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_2.Add(results_dir_copy_copy_copy_3, 1, wx.EXPAND, 0)
        results_dir_copy_copy_copy_copy_2.Add(self.structure_file_copy_2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_2.Add(self.structure_t11_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_2.Add(self.results_directory_copy_copy_copy_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_2.Add(results_dir_copy_copy_copy_copy_2, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy_copy_2.Add(self.label_2_copy_copy_copy_2_copy_copy_copy_2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_copy_2.Add(self.unresolved_t11_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_2.Add(nmr_freq_copy_copy_copy_copy_2, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_11_copy_2.Add(self.panel_2_copy_2, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_13_copy_2.Add(self.addt11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_13_copy_2.Add(self.refresht11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_12_copy_2.Add(sizer_13_copy_2, 1, wx.EXPAND, 0)
        grid_sizer_1_copy_2.Add(self.label_3_copy_2, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.label_6_copy_2, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_1_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_1_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_2_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_2_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_3_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_3_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_4_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_4_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_5_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_5_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_6_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_6_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_7_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_7_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_8_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_8_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_9_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_9_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_10_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_10_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_12_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_12_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_1_copy_11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_13_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_list_14_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_2.Add(self.t1_time_1_4_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        self.panel_3_copy_2.SetSizer(grid_sizer_1_copy_2)
        sizer_12_copy_2.Add(self.panel_3_copy_2, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_1_copy_2.SetSizer(sizer_12_copy_2)
        sizer_11_copy_2.Add(self.panel_1_copy_2, 0, wx.EXPAND|wx.SHAPED, 0)
        exec_relax_copy_1_copy_copy_2.Add(self.label_5_copy_1_copy_copy_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_copy_2.Add(self.relax_start_t1_1_copy_2, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_2.Add(exec_relax_copy_1_copy_copy_2, 0, wx.ALIGN_RIGHT, 0)
        sizer_10_copy_2.Add(sizer_11_copy_2, 0, 0, 0)
        self.t1_1_copy_1.SetSizer(sizer_10_copy_2)
        sizer_10_copy_copy_1.Add(self.bitmap_1_copy_copy_copy_copy_1, 0, wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_copy_1.Add(self.label_4_copy_copy_copy_copy_1, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        nmr_freq_copy_copy_copy_1_copy_1.Add(self.label_2_copy_copy_copy_2_copy_copy_1_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_1_copy_1.Add(self.nmrfreq_value_t21_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_copy_1.Add(nmr_freq_copy_copy_copy_1_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy_copy_1_copy_1.Add(self.label_2_copy_copy_3_copy_copy_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy_1.Add(self.resultsdir_t21_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy_1.Add(self.results_directory_t21_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_copy_1.Add(results_dir_copy_copy_copy_1_copy_1, 1, wx.EXPAND, 0)
        results_dir_copy_copy_copy_copy_copy_1.Add(self.structure_file_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy_1.Add(self.structure_t21_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy_1.Add(self.chan_struc_t21_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_11_copy_copy_1.Add(results_dir_copy_copy_copy_copy_copy_1, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy_copy_copy_1.Add(self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_copy_copy_1.Add(self.unresolved_t21_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_copy_1.Add(nmr_freq_copy_copy_copy_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_11_copy_copy_1.Add(self.panel_2_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_13_copy_copy_1.Add(self.addt21_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_13_copy_copy_1.Add(self.refresht21_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_12_copy_copy_1.Add(sizer_13_copy_copy_1, 1, wx.EXPAND, 0)
        grid_sizer_1_copy_copy_1.Add(self.label_3_copy_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.label_6_copy_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_1_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_1_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_2_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_2_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_3_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_3_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_4_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_4_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_5_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_5_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_6_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_6_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_7_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_7_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_8_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_8_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_9_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_9_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_10_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_10_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_11_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_12_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_12_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_13_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_13_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_list_14_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        grid_sizer_1_copy_copy_1.Add(self.t2_time_14_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        self.panel_3_copy_copy_1.SetSizer(grid_sizer_1_copy_copy_1)
        sizer_12_copy_copy_1.Add(self.panel_3_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_1_copy_copy_1.SetSizer(sizer_12_copy_copy_1)
        sizer_11_copy_copy_1.Add(self.panel_1_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        exec_relax_copy_1_copy_copy_copy_1.Add(self.label_5_copy_1_copy_copy_copy_1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_copy_copy_1.Add(self.relax_start_t1_1_copy_copy_1, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_11_copy_copy_1.Add(exec_relax_copy_1_copy_copy_copy_1, 0, wx.ALIGN_RIGHT, 0)
        sizer_10_copy_copy_1.Add(sizer_11_copy_copy_1, 0, 0, 0)
        self.t2_1_copy_1.SetSizer(sizer_10_copy_copy_1)
        self.notebook_3_copy_1.AddPage(self.noe1_copy_1, "steady-state NOE")
        self.notebook_3_copy_1.AddPage(self.t1_1_copy_1, "T1 relaxation")
        self.notebook_3_copy_1.AddPage(self.t2_1_copy_1, "T2 relaxation")
        frq1sub_copy_1.Add(self.notebook_3_copy_1, 1, wx.EXPAND, 0)
        self.frq3.SetSizer(frq1sub_copy_1)
        sizer_14.Add(self.bitmap_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_15.Add(self.label_4_copy_copy_copy_copy_1_copy, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)
        sizer_18.Add(self.label_7, 0, wx.ADJUST_MINSIZE, 0)
        sizer_18.Add(self.modelfreefreq1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17.Add(sizer_18, 0, 0, 0)
        sizer_19.Add(self.label_8, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19.Add(self.m_noe_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19.Add(self.model_noe_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17.Add(sizer_19, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy.Add(self.label_8_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy.Add(self.m_r1_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy.Add(self.model_r1_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17.Add(sizer_19_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy.Add(self.label_8_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy.Add(self.m_r2_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy.Add(self.model_r2_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17.Add(sizer_19_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_4.SetSizer(sizer_17)
        sizer_16.Add(self.panel_4, 0, 0, 0)
        sizer_18_copy.Add(self.label_7_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_18_copy.Add(self.modelfreefreq2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy.Add(sizer_18_copy, 0, 0, 0)
        sizer_19_copy_1.Add(self.label_8_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_1.Add(self.m_noe_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_1.Add(self.model_noe_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy.Add(sizer_19_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy_1.Add(self.label_8_copy_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_1.Add(self.m_r1_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_1.Add(self.model_r1_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy.Add(sizer_19_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy_copy.Add(self.label_8_copy_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_copy.Add(self.m_r2_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_copy.Add(self.model_r2_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy.Add(sizer_19_copy_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_4_copy.SetSizer(sizer_17_copy)
        sizer_16.Add(self.panel_4_copy, 0, 0, 0)
        sizer_18_copy_copy.Add(self.label_7_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_18_copy_copy.Add(self.modelfreefreq3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy_copy.Add(sizer_18_copy_copy, 0, 0, 0)
        sizer_19_copy_1_copy.Add(self.label_8_copy_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_1_copy.Add(self.m_noe_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_1_copy.Add(self.model_noe_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy_copy.Add(sizer_19_copy_1_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy_1_copy.Add(self.label_8_copy_copy_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_1_copy.Add(self.m_r1_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_1_copy.Add(self.model_r1_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy_copy.Add(sizer_19_copy_copy_1_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy_copy_copy.Add(self.label_8_copy_copy_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_copy_copy.Add(self.m_r2_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_copy_copy.Add(self.model_r2_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy_copy.Add(sizer_19_copy_copy_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        self.panel_4_copy_1.SetSizer(sizer_17_copy_copy)
        sizer_16.Add(self.panel_4_copy_1, 0, 0, 0)
        sizer_15.Add(sizer_16, 0, 0, 0)
        sizer_15.Add(self.label_9, 0, wx.TOP|wx.ADJUST_MINSIZE, 10)
        sizer_20.Add(self.m0, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m4, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m5, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m6, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m7, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m8, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m9, 0, wx.ADJUST_MINSIZE, 0)
        sizer_15.Add(sizer_20, 1, wx.EXPAND, 0)
        sizer_21.Add(self.label_10, 0, wx.TOP|wx.ADJUST_MINSIZE, 1)
        sizer_21.Add(self.aic, 0, wx.ADJUST_MINSIZE, 0)
        sizer_21.Add(self.bic, 0, wx.ADJUST_MINSIZE, 0)
        sizer_15.Add(sizer_21, 1, wx.TOP|wx.EXPAND, 5)
        results_dir_copy_copy_copy_copy_copy_1_copy.Add(self.structure_file_copy_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy_1_copy.Add(self.structure_t21_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy_1_copy.Add(self.chan_struc_t21_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_15.Add(results_dir_copy_copy_copy_copy_copy_1_copy, 1, wx.EXPAND, 0)
        nmr_freq_copy_copy_copy_copy_copy_1_copy.Add(self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_copy_copy_1_copy.Add(self.unresolved_t21_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        sizer_15.Add(nmr_freq_copy_copy_copy_copy_copy_1_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        results_dir_copy_copy_copy_1_copy_2.Add(self.label_2_copy_copy_3_copy_copy_copy_copy_2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy_2.Add(self.resultsdir_t21_copy_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy_2.Add(self.results_directory_t21_copy_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)
        sizer_15.Add(results_dir_copy_copy_copy_1_copy_2, 1, wx.EXPAND, 0)
        exec_relax_copy_1_copy_3.Add(self.label_5_copy_1_copy_3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_3.Add(self.relax_start_modelfree, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)
        sizer_15.Add(exec_relax_copy_1_copy_3, 1, wx.ALIGN_RIGHT, 0)
        sizer_14.Add(sizer_15, 0, 0, 0)
        self.modelfree.SetSizer(sizer_14)
        sizer_22.Add(self.label_11, 0, wx.LEFT|wx.ADJUST_MINSIZE, 10)
        sizer_23.Add(self.list_noe, 0, wx.ADJUST_MINSIZE, 0)
        sizer_23.Add(self.open_noe_results, 0, wx.ADJUST_MINSIZE, 0)
        sizer_22.Add(sizer_23, 1, wx.LEFT|wx.EXPAND, 10)
        sizer_9.Add(sizer_22, 1, wx.EXPAND, 0)
        sizer_22_copy.Add(self.label_11_copy, 0, wx.LEFT|wx.ADJUST_MINSIZE, 10)
        sizer_23_copy.Add(self.list_tx, 0, wx.ADJUST_MINSIZE, 0)
        sizer_23_copy.Add(self.open_tx_results, 0, wx.ADJUST_MINSIZE, 0)
        sizer_22_copy.Add(sizer_23_copy, 1, wx.LEFT|wx.EXPAND, 10)
        sizer_9.Add(sizer_22_copy, 1, wx.EXPAND, 0)
        sizer_22_copy_copy.Add(self.label_11_copy_copy, 0, wx.LEFT|wx.ADJUST_MINSIZE, 10)
        sizer_23_copy_copy.Add(self.list_modelfree, 0, wx.ADJUST_MINSIZE, 0)
        sizer_23_copy_copy.Add(self.open_model_results, 0, wx.ADJUST_MINSIZE, 0)
        sizer_22_copy_copy.Add(sizer_23_copy_copy, 1, wx.LEFT|wx.EXPAND, 10)
        sizer_9.Add(sizer_22_copy_copy, 1, wx.EXPAND, 0)
        self.results.SetSizer(sizer_9)
        self.notebook_2.AddPage(self.frq1, "Frq. 1")
        self.notebook_2.AddPage(self.frq2, "Frq. 2")
        self.notebook_2.AddPage(self.frq3, "Frq. 3")
        self.notebook_2.AddPage(self.modelfree, "Model-free")
        self.notebook_2.AddPage(self.results, "Results")
        sizer_8.Add(self.notebook_2, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_8)
        self.Layout()
        self.SetSize((1000, 600))
        self.Centre()
        # end wxGlade


#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################
#####################################################################################################################

# GUI actions


#menu

    def newGUI(self, event): # New
        newdir = diropenbox(msg='Select results directory', title='relaxGUI', default='*')
        if not newdir == None:
            #create directories
            os.system('mkdir ' + newdir + '/NOE_1')
            os.system('mkdir ' + newdir + '/NOE_2')
            os.system('mkdir ' + newdir + '/NOE_3')
            os.system('mkdir ' + newdir + '/T1_1')
            os.system('mkdir ' + newdir + '/T1_2')
            os.system('mkdir ' + newdir + '/T1_3')
            os.system('mkdir ' + newdir + '/T2_1')
            os.system('mkdir ' + newdir + '/T2_2')
            os.system('mkdir ' + newdir + '/T2_3')
            os.system('mkdir ' + newdir + '/model_free')
            #insert directories in set up menu
            self.res_noe1.SetValue(newdir + '/NOE_1')
            self.res_noe1_copy.SetValue(newdir + '/NOE_2')
            self.res_noe1_copy_1.SetValue(newdir + '/NOE_3')
            self.resultsdir_t11.SetValue(newdir + '/T1_1')
            self.resultsdir_t11_copy.SetValue(newdir + '/T1_2')
            self.resultsdir_t11_copy_1.SetValue(newdir + '/T1_3')
            self.resultsdir_t21.SetValue(newdir + '/T2_1')
            self.resultsdir_t21_copy.SetValue(newdir + '/T2_2')
            self.resultsdir_t21_copy_1.SetValue(newdir + '/T2_3')
            self.resultsdir_t21_copy_2.SetValue(newdir + '/model_free')

            msgbox(msg = 'Folder structure created for Model-free analysis:\n\n\n' + newdir + '/NOE_1\n' + newdir + '/NOE_2\n' + newdir + '/NOE_3\n' + newdir + '/T1_1\n' + newdir + '/T1_2\n' + newdir + '/T1_3\n' + newdir + '/T2_1\n' + newdir + '/T2_2\n' + newdir + '/T2_3\n' + newdir + '/model-free', title = 'relaxGUI')
        event.Skip()


    def references(self, event):
        webbrowser.open_new('http://www.nmr-relax.com/refs.html')
        event.Skip()

    def settings(self, event):
        relax_settings(homedir)
        event.Skip()

    def openGUI(self, event): # Open
        filename = fileopenbox(msg=None, title='Open relaxGUI save file', default = "*.relaxGUI")
        if not filename == None:
           open_file(self, filename)
        event.Skip()

    def saveGUI(self, event): # Save
     filename = filesavebox(msg=None, title='Save File as', default = "*.relaxGUI")
     if not filename == None: 
        create_save_file(self, filename)
     event.Skip()

    def exitGUI(self, event): # Exit
        doexit = ynbox(msg='Do you wand to quit relaxGUI?', title='relaxGUI', choices=('Yes', 'No'), image=None)
        if doexit == True:
           print "\n\n\nExiting relaxGUI......\n\n\n"
           sys.exit(0)
        event.Skip()

    def aboutGUI(self, event): # About
        about_relax(homedir)
        event.Skip()

    def aboutrelax(self, event): # abour relax
        webbrowser.open_new('http://www.nmr-relax.com')
        event.Skip()

### NOE no. 1


    def sat_noe1(self, event): # saturated noe 1
        backup = self.noe_sat_1.GetValue()
        noesat[0] = fileopenbox(msg='Select saturated NOE file ('+ str(nmrfreq[0]) + ' MHz)', title='relaxGUI', default=self.res_noe1.GetValue() + '/', filetypes=None)
        if noesat[0] == None:
           noesat[0] = backup
        self.noe_sat_1.SetValue(noesat[0])
        event.Skip()

    def ref_noe(self, event): # reference noe 1
        backup = self.noe_ref_1.GetValue()
        noeref[0] = fileopenbox(msg='Select reference NOE file ('+ str(nmrfreq[0]) + ' MHz)', title='relaxGUI', default=self.res_noe1.GetValue() + '/', filetypes=None)
        if noeref[0] == None:
           noeref[0] = backup
        self.noe_ref_1.SetValue(noeref[0])
        event.Skip()

    def structure_pdb(self, event): # structure file
        backup = self.structure_noe1.GetValue()
        structure_file_pdb = fileopenbox(msg='Select PDB file', title='relaxGUI', default=self.res_noe1.GetValue() + '/', filetypes=None)
        if structure_file_pdb == None:
           structure_file_pdb = backup
        self.structure_noe1.SetValue(structure_file_pdb)
        self.structure_t11.SetValue(structure_file_pdb)
        self.structure_t21.SetValue(structure_file_pdb)
        self.structure_noe1_copy.SetValue(structure_file_pdb)
        self.structure_t11_copy.SetValue(structure_file_pdb)
        self.structure_t21_copy.SetValue(structure_file_pdb)
        self.structure_noe1_copy_1.SetValue(structure_file_pdb)
        self.structure_t11_copy_1.SetValue(structure_file_pdb)
        self.structure_t21_copy_1.SetValue(structure_file_pdb)
        self.structure_t21_copy_1_copy.SetValue(structure_file_pdb)
        event.Skip()

    def resdir_noe1(self, event): # noe 1 results dir
        backup = self.res_noe1.GetValue()
        noe_savedir[0] = diropenbox(msg='Select results directory', title='relaxGUI', default=self.res_noe1.GetValue() + '/')
        if noe_savedir[0] == None:
           noe_savedir[0] = backup
        self.res_noe1.SetValue(noe_savedir[0])
        event.Skip()

    def exec_noe1(self, event): # Start NOE calculation no. 1
        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= homedir + 'res/pics/relax.gif')

        if start_relax == True:
           make_noe(self.res_noe1.GetValue(), self.noe_ref_1.GetValue(), self.noe_sat_1.GetValue(), self.noe_ref_err_1.GetValue(), self.noe_sat_err_1.GetValue(), self.nmrfreq_value_noe1.GetValue(),self.structure_noe1.GetValue(), self.unres_noe1.GetValue(), start_relax, self, 1)
        event.Skip()

          

##### T1 no. 1

    def resdir_t1_1(self, event): # T1 results dir 1
        backup = self.resultsdir_t11.GetValue()
        t1_savedir[0] = diropenbox(msg='Select results directory)', title='relaxGUI', default=self.resultsdir_t11.GetValue() + '/')
        if t1_savedir[0] == None:
           t1_savedir[0] = backup
        self.resultsdir_t11.SetValue(t1_savedir[0])

        event.Skip()

    def add_t1_1(self, event): # add a t1 peak list

        if len(t1_list) < 14:
             t1_entry = fileopenbox(msg='Select T1 peak list file', title=None, default=self.resultsdir_t11.GetValue() + '/', filetypes=None)
             if not t1_entry == None:
                t1_list.append(t1_entry)

        if len(t1_list) == 1:
            self.t1_list_1.SetLabel(t1_list[0]) 
        if len(t1_list) == 2:
            self.t1_list_2.SetLabel(t1_list[1]) 
        if len(t1_list) == 3:
            self.t1_list_3.SetLabel(t1_list[2]) 
        if len(t1_list) == 4:
            self.t1_list_4.SetLabel(t1_list[3]) 
        if len(t1_list) == 5:
            self.t1_list_5.SetLabel(t1_list[4]) 
        if len(t1_list) == 6:
            self.t1_list_6.SetLabel(t1_list[5]) 
        if len(t1_list) == 7:
            self.t1_list_7.SetLabel(t1_list[6]) 
        if len(t1_list) == 8:
            self.t1_list_8.SetLabel(t1_list[7]) 
        if len(t1_list) == 9:
            self.t1_list_9.SetLabel(t1_list[8]) 
        if len(t1_list) == 10:
            self.t1_list_10.SetLabel(t1_list[9]) 
        if len(t1_list) == 11:
            self.t1_list_11.SetLabel(t1_list[10]) 
        if len(t1_list) == 12:
            self.t1_list_12.SetLabel(t1_list[11]) 
        if len(t1_list) == 13:
            self.t1_list_1_copy_11.SetLabel(t1_list[12]) 
        if len(t1_list) == 14:
            self.t1_list_14.SetLabel(t1_list[13])              
        event.Skip()

    def refresh_t1_1(self, event): # refresh t1 list no. 1
        self.t1_list_1.SetLabel('')
        self.t1_list_2.SetLabel('')
        self.t1_list_3.SetLabel('')
        self.t1_list_4.SetLabel('')
        self.t1_list_5.SetLabel('')
        self.t1_list_6.SetLabel('')
        self.t1_list_7.SetLabel('')
        self.t1_list_8.SetLabel('')
        self.t1_list_9.SetLabel('')
        self.t1_list_10.SetLabel('')
        self.t1_list_11.SetLabel('')
        self.t1_list_12.SetLabel('')
        self.t1_list_1_copy_11.SetLabel('')
        self.t1_list_14.SetLabel('')
        del t1_list[0:len(t1_list)]
        event.Skip()

    def exec_t2_1(self, event): # start t1 calculation no. 1
        relax_times_t1_1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #create relaxation time list
        relax_times_t1_1[0] = str(self.t1_time_1.GetValue()) 
        relax_times_t1_1[1] = str(self.t1_time_2.GetValue()) 
        relax_times_t1_1[2] = str(self.t1_time_3.GetValue()) 
        relax_times_t1_1[3] = str(self.t1_time_4.GetValue()) 
        relax_times_t1_1[4] = str(self.t1_time_5.GetValue()) 
        relax_times_t1_1[5] = str(self.t1_time_6.GetValue()) 
        relax_times_t1_1[6] = str(self.t1_time_7.GetValue()) 
        relax_times_t1_1[7] = str(self.t1_time_8.GetValue()) 
        relax_times_t1_1[8] = str(self.t1_time_9.GetValue()) 
        relax_times_t1_1[9] = str(self.t1_time_10.GetValue()) 
        relax_times_t1_1[10] = str(self.t1_time_11.GetValue()) 
        relax_times_t1_1[11] = str(self.t1_time_12.GetValue()) 
        relax_times_t1_1[12] = str(self.t1_time_13.GetValue()) 
        relax_times_t1_1[13] = str(self.t1_time_1_4.GetValue()) 
        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= homedir + 'res/pics/relax.gif')
        if start_relax == True:
           make_tx(self.resultsdir_t11.GetValue(), relax_times_t1_1, self.structure_t11.GetValue(), self.nmrfreq_value_t11.GetValue(), 1, 1, self.unresolved_t11.GetValue(), self, 1)
        event.Skip()

### Execute T2 no. 1

    def resdir_t2_1(self, event): # wxGlade: main.<event_handler>
        backup = self.resultsdir_t21.GetValue()
        t2_savedir[0] = diropenbox(msg='Select results directory)', title='relaxGUI', default=self.resultsdir_t21.GetValue() + '/')
        if t2_savedir[0] == None:
           t2_savedir[0] = backup
        self.resultsdir_t21.SetValue(t2_savedir[0])
        event.Skip()

    def add_t2_1(self, event): # add a t2 peak list
        if len(t2_list) < 14:
             t2_entry = fileopenbox(msg='Select T2 peak list file', title='relaxGUI', default=self.resultsdir_t21.GetValue() + '/', filetypes=None)
             if not t2_entry == None:
                t2_list.append(t2_entry)
        if len(t2_list) == 1:
            self.t2_list_1.SetLabel(t2_list[0]) 
        if len(t2_list) == 2:
            self.t2_list_2.SetLabel(t2_list[1]) 
        if len(t2_list) == 3:
            self.t2_list_3.SetLabel(t2_list[2]) 
        if len(t2_list) == 4:
            self.t2_list_4.SetLabel(t2_list[3]) 
        if len(t2_list) == 5:
            self.t2_list_5.SetLabel(t2_list[4]) 
        if len(t2_list) == 6:
            self.t2_list_6.SetLabel(t2_list[5]) 
        if len(t2_list) == 7:
            self.t2_list_7.SetLabel(t2_list[6]) 
        if len(t2_list) == 8:
            self.t2_list_8.SetLabel(t2_list[7]) 
        if len(t2_list) == 9:
            self.t2_list_9.SetLabel(t2_list[8]) 
        if len(t2_list) == 10:
            self.t2_list_10.SetLabel(t2_list[9]) 
        if len(t2_list) == 11:
            self.t2_list_11.SetLabel(t2_list[10]) 
        if len(t2_list) == 12:
            self.t2_list_12.SetLabel(t2_list[11]) 
        if len(t2_list) == 13:
            self.t2_list_13.SetLabel(t2_list[12]) 
        if len(t2_list) == 14:
            self.t2_list_14.SetLabel(t2_list[13])              
        event.Skip()

    def refresh_t2_1(self, event): # refresh t2 list no. 1
        self.t2_list_1.SetLabel('')
        self.t2_list_2.SetLabel('')
        self.t2_list_3.SetLabel('')
        self.t2_list_4.SetLabel('')
        self.t2_list_5.SetLabel('')
        self.t2_list_6.SetLabel('')
        self.t2_list_7.SetLabel('')
        self.t2_list_8.SetLabel('')
        self.t2_list_9.SetLabel('')
        self.t2_list_10.SetLabel('')
        self.t2_list_11.SetLabel('')
        self.t2_list_12.SetLabel('')
        self.t2_list_13.SetLabel('')
        self.t2_list_14.SetLabel('')
        del t2_list[0:len(t2_list)]
        event.Skip()

    def exec_t1_1(self, event): # start t2 calculation
        relax_times_t2_1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #create relaxation time list
        relax_times_t2_1[0] = str(self.t2_time_1.GetValue()) 
        relax_times_t2_1[1] = str(self.t2_time_2.GetValue()) 
        relax_times_t2_1[2] = str(self.t2_time_3.GetValue()) 
        relax_times_t2_1[3] = str(self.t2_time_4.GetValue()) 
        relax_times_t2_1[4] = str(self.t2_time_5.GetValue()) 
        relax_times_t2_1[5] = str(self.t2_time_6.GetValue()) 
        relax_times_t2_1[6] = str(self.t2_time_7.GetValue()) 
        relax_times_t2_1[7] = str(self.t2_time_8.GetValue()) 
        relax_times_t2_1[8] = str(self.t2_time_9.GetValue()) 
        relax_times_t2_1[9] = str(self.t2_time_10.GetValue()) 
        relax_times_t2_1[10] = str(self.t2_time_11.GetValue()) 
        relax_times_t2_1[11] = str(self.t2_time_12.GetValue()) 
        relax_times_t2_1[12] = str(self.t2_time_13.GetValue()) 
        relax_times_t2_1[13] = str(self.t2_time_14.GetValue()) 
        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= homedir + 'res/pics/relax.gif')
        if start_relax == True:
           make_tx(self.resultsdir_t21.GetValue(), relax_times_t2_1, self.structure_t11.GetValue(), self.nmrfreq_value_t11.GetValue(), 2, 1, self.unresolved_t11.GetValue(), self,1)
        event.Skip()

### NOE no. 2

    def sat_noe2(self, event): # saturated noe no. 2
        backup = self.noe_sat_1_copy.GetValue()
        noesat[1] = fileopenbox(msg='Select saturated NOE file ('+ str(nmrfreq[1]) + ' MHz)', title=None, default= self.res_noe1_copy.GetValue() + '/', filetypes=None)
        if noesat[1] == None:
           noesat[1] = backup
        self.noe_sat_1_copy.SetValue(noesat[1])
        event.Skip()

    def ref_noe2(self, event): # reference noe no. 2
        backup = self.noe_ref_1_copy.GetValue()
        noeref[1] = fileopenbox(msg='Select reference NOE file ('+ str(nmrfreq[1]) + ' MHz)', title=None, default=self.res_noe1_copy.GetValue() + '/', filetypes=None)
        if noeref[1] == None:
           noeref[1] = backup
        self.noe_ref_1_copy.SetValue(noeref[1])
        event.Skip()

    def resdir_noe2(self, event): # noe results dir no. 2
        backup = self.res_noe1_copy.GetValue()
        noe_savedir[1] = diropenbox(msg='Select results directory', title='relaxGUI', default = self.res_noe1_copy.GetValue() + '/')
        if noe_savedir[1] == None:
           noe_savedir[1] = backup
        self.res_noe1_copy.SetValue(noe_savedir[1])
        event.Skip()

    def exec_noe2(self, event): # start noe 2 calculation
        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= homedir + 'res/pics/relax.gif')
        if start_relax == True:
           make_noe(self.res_noe1_copy.GetValue(), self.noe_ref_1_copy.GetValue(), self.noe_sat_1_copy.GetValue(), self.noe_ref_err_1_copy.GetValue(), self.noe_sat_err_1_copy.GetValue(), self.nmrfreq_value_noe1_copy.GetValue(),self.structure_noe1_copy.GetValue(), self.unres_noe1_copy.GetValue(), start_relax, self, 2)
        event.Skip()

### T1 no. 2

    def resdir_t1_2(self, event): # wxGlade: main.<event_handler>
        backup = self.resultsdir_t11_copy.GetValue()
        t1_savedir[1] = diropenbox(msg='Select results directory', title='relaxGUI', default=self.resultsdir_t11_copy.GetValue() + '/')
        if t1_savedir[1] == None:
           t1_savedir[1] = backup
        self.resultsdir_t11_copy.SetValue(t1_savedir[1])
        event.Skip()

    def add_t1_2(self, event): # wxGlade: main.<event_handler>
        if len(t1_list2) < 14:
             t1_entry2 = fileopenbox(msg='Select T1 peak list file', title=None, default=self.resultsdir_t11_copy.GetValue() + '/', filetypes=None)
             if not t1_entry2 == None:
                t1_list2.append(t1_entry2)
        if len(t1_list2) == 1:
            self.t1_list_1_copy.SetLabel(t1_list2[0]) 
        if len(t1_list2) == 2:
            self.t1_list_2_copy.SetLabel(t1_list2[1]) 
        if len(t1_list2) == 3:
            self.t1_list_3_copy.SetLabel(t1_list2[2]) 
        if len(t1_list2) == 4:
            self.t1_list_4_copy.SetLabel(t1_list2[3]) 
        if len(t1_list2) == 5:
            self.t1_list_5_copy.SetLabel(t1_list2[4]) 
        if len(t1_list2) == 6:
            self.t1_list_6_copy.SetLabel(t1_list2[5]) 
        if len(t1_list2) == 7:
            self.t1_list_7_copy.SetLabel(t1_list2[6]) 
        if len(t1_list2) == 8:
            self.t1_list_8_copy.SetLabel(t1_list2[7]) 
        if len(t1_list2) == 9:
            self.t1_list_9_copy.SetLabel(t1_list2[8]) 
        if len(t1_list2) == 10:
            self.t1_list_10_copy.SetLabel(t1_list2[9]) 
        if len(t1_list2) == 11:
            self.t1_list_11_copy.SetLabel(t1_list2[10]) 
        if len(t1_list2) == 12:
            self.t1_list_12_copy.SetLabel(t1_list2[11]) 
        if len(t1_list2) == 13:
            self.t1_list_1_copy_11_copy.SetLabel(t1_list2[12]) 
        if len(t1_list2) == 14:
            self.t1_list_14_copy.SetLabel(t1_list2[13])              
        event.Skip()

    def refresh_t1_2(self, event): # refresh T1 no. 2
        self.t1_list_1_copy.SetLabel('')
        self.t1_list_2_copy.SetLabel('')
        self.t1_list_3_copy.SetLabel('')
        self.t1_list_4_copy.SetLabel('')
        self.t1_list_5_copy.SetLabel('')
        self.t1_list_6_copy.SetLabel('')
        self.t1_list_7_copy.SetLabel('')
        self.t1_list_8_copy.SetLabel('')
        self.t1_list_9_copy.SetLabel('')
        self.t1_list_10_copy.SetLabel('')
        self.t1_list_11_copy.SetLabel('')
        self.t1_list_12_copy.SetLabel('')
        self.t1_list_1_copy_11_copy.SetLabel('')
        self.t1_list_14_copy.SetLabel('')
        del t1_list2[0:len(t1_list2)]
        event.Skip()

    def exec_t1_2(self, event): # execute t1 calculation no. 2
        relax_times_t1_2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #create relaxation time list

        relax_times_t1_2[0] = str(self.t1_time_1_copy.GetValue()) 
        relax_times_t1_2[1] = str(self.t1_time_2_copy.GetValue()) 
        relax_times_t1_2[2] = str(self.t1_time_3_copy.GetValue()) 
        relax_times_t1_2[3] = str(self.t1_time_4_copy.GetValue()) 
        relax_times_t1_2[4] = str(self.t1_time_5_copy.GetValue()) 
        relax_times_t1_2[5] = str(self.t1_time_6_copy.GetValue()) 
        relax_times_t1_2[6] = str(self.t1_time_7_copy.GetValue()) 
        relax_times_t1_2[7] = str(self.t1_time_8_copy.GetValue()) 
        relax_times_t1_2[8] = str(self.t1_time_9_copy.GetValue()) 
        relax_times_t1_2[9] = str(self.t1_time_10_copy.GetValue()) 
        relax_times_t1_2[10] = str(self.t1_time_11_copy.GetValue()) 
        relax_times_t1_2[11] = str(self.t1_time_12_copy.GetValue()) 
        relax_times_t1_2[12] = str(self.t1_time_13_copy.GetValue()) 
        relax_times_t1_2[13] = str(self.t1_time_1_4_copy.GetValue()) 

        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= homedir + 'res/pics/relax.gif')
        if start_relax == True:
           make_tx(self.resultsdir_t11_copy.GetValue(), relax_times_t1_2, self.structure_t11_copy.GetValue(), self.nmrfreq_value_t11_copy.GetValue(), 1, 2, self.unresolved_t11_copy.GetValue(), self,2)
        event.Skip()

### T2 no. 2

    def resdir_t2_2(self, event): # wxGlade: main.<event_handler>
        backup = self.resultsdir_t21_copy.GetValue()
        t2_savedir[1] = diropenbox(msg='Select results directory)', title='relaxGUI', default=self.resultsdir_t21_copy.GetValue() + '/')
        if t2_savedir[1] == None:
           t2_savedir[1] = backup
        self.resultsdir_t21_copy.SetValue(t2_savedir[1])
        event.Skip()

    def add_t2_2(self, event): # add a t2 peak list
        if len(t2_list2) < 14:
             t2_entry2 = fileopenbox(msg='Select T2 peak list file', title='relaxGUI', default=self.resultsdir_t21_copy.GetValue() + '/', filetypes=None)
             if not t2_entry2 == None:
                t2_list2.append(t2_entry2)
        if len(t2_list2) == 1:
            self.t2_list_1_copy.SetLabel(t2_list2[0]) 
        if len(t2_list2) == 2:
            self.t2_list_2_copy.SetLabel(t2_list2[1]) 
        if len(t2_list2) == 3:
            self.t2_list_3_copy.SetLabel(t2_list2[2]) 
        if len(t2_list2) == 4:
            self.t2_list_4_copy.SetLabel(t2_list2[3]) 
        if len(t2_list2) == 5:
            self.t2_list_5_copy.SetLabel(t2_list2[4]) 
        if len(t2_list2) == 6:
            self.t2_list_6_copy.SetLabel(t2_list2[5]) 
        if len(t2_list2) == 7:
            self.t2_list_7_copy.SetLabel(t2_list2[6]) 
        if len(t2_list2) == 8:
            self.t2_list_8_copy.SetLabel(t2_list2[7]) 
        if len(t2_list2) == 9:
            self.t2_list_9_copy.SetLabel(t2_list2[8]) 
        if len(t2_list2) == 10:
            self.t2_list_10_copy.SetLabel(t2_list2[9]) 
        if len(t2_list2) == 11:
            self.t2_list_11_copy.SetLabel(t2_list2[10]) 
        if len(t2_list2) == 12:
            self.t2_list_12_copy.SetLabel(t2_list2[11]) 
        if len(t2_list2) == 13:
            self.t2_list_13_copy.SetLabel(t2_list2[12]) 
        if len(t2_list2) == 14:
            self.t2_list_14_copy.SetLabel(t2_list2[13])              
        event.Skip()

    def refresh_t2_2(self, event): # refresh t2 list no. 1
        self.t2_list_1_copy.SetLabel('')
        self.t2_list_2_copy.SetLabel('')
        self.t2_list_3_copy.SetLabel('')
        self.t2_list_4_copy.SetLabel('')
        self.t2_list_5_copy.SetLabel('')
        self.t2_list_6_copy.SetLabel('')
        self.t2_list_7_copy.SetLabel('')
        self.t2_list_8_copy.SetLabel('')
        self.t2_list_9_copy.SetLabel('')
        self.t2_list_10_copy.SetLabel('')
        self.t2_list_11_copy.SetLabel('')
        self.t2_list_12_copy.SetLabel('')
        self.t2_list_13_copy.SetLabel('')
        self.t2_list_14_copy.SetLabel('')
        del t2_list2[0:len(t2_list2)]
        event.Skip()


    def exec_t2_2(self, event): # wxGlade: main.<event_handler>
        relax_times_t2_2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #create relaxation time list
        relax_times_t2_2[0] = str(self.t2_time_1_copy.GetValue()) 
        relax_times_t2_2[1] = str(self.t2_time_2_copy.GetValue()) 
        relax_times_t2_2[2] = str(self.t2_time_3_copy.GetValue()) 
        relax_times_t2_2[3] = str(self.t2_time_4_copy.GetValue()) 
        relax_times_t2_2[4] = str(self.t2_time_5_copy.GetValue()) 
        relax_times_t2_2[5] = str(self.t2_time_6_copy.GetValue()) 
        relax_times_t2_2[6] = str(self.t2_time_7_copy.GetValue()) 
        relax_times_t2_2[7] = str(self.t2_time_8_copy.GetValue()) 
        relax_times_t2_2[8] = str(self.t2_time_9_copy.GetValue()) 
        relax_times_t2_2[9] = str(self.t2_time_10_copy.GetValue()) 
        relax_times_t2_2[10] = str(self.t2_time_11_copy.GetValue()) 
        relax_times_t2_2[11] = str(self.t2_time_12_copy.GetValue()) 
        relax_times_t2_2[12] = str(self.t2_time_13_copy.GetValue()) 
        relax_times_t2_2[13] = str(self.t2_time_14_copy.GetValue()) 

        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= homedir + 'res/pics/relax.gif')
        if start_relax == True:
           make_tx(self.resultsdir_t21_copy.GetValue(), relax_times_t2_2, self.structure_t11_copy.GetValue(), self.nmrfreq_value_t11_copy.GetValue(), 2, 2, self.unresolved_t11_copy.GetValue(), self,2)
        event.Skip()

### NOE no. 3

    def sat_noe3(self, event): # saturated noe no. 3
        backup = self.noe_sat_1_copy_1.GetValue()
        noesat[2] = fileopenbox(msg='Select saturated NOE file ('+ str(nmrfreq[2]) + ' MHz)', title='relaxGUI', default= self.res_noe1_copy_1.GetValue() + '/', filetypes=None)
        if noesat[2] == None:
           noesat[2] = backup
        self.noe_sat_1_copy_1.SetValue(noesat[2])
        event.Skip()

    def ref_noe3(self, event): # refererence noe 3
        backup = self.noe_ref_1_copy_1.GetValue()
        noeref[2] = fileopenbox(msg='Select reference NOE file ('+ str(nmrfreq[2]) + ' MHz)', title=None, default=self.res_noe1_copy_1.GetValue() + '/', filetypes=None)
        if noeref[2] == None:
           noeref[2] = backup
        self.noe_ref_1_copy_1.SetValue(noeref[2])
        event.Skip()

    def resdir_noe3(self, event): # noe 3 results dir
        backup = self.res_noe1_copy_1.GetValue()
        noe_savedir[2] = diropenbox(msg='Select results directory)', title='relaxGUI', default=self.res_noe1_copy_1.GetValue() + '/')
        if noe_savedir[2] == None:
           noe_savedir[2] = backup
        self.res_noe1_copy_1.SetValue(noe_savedir[2])
        event.Skip()

    def exec_noe3(self, event): # calculate noe 3
        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= homedir + 'res/pics/relax.gif')
        if start_relax == True:
           make_noe(self.res_noe1_copy_1.GetValue(), self.noe_ref_1_copy_1.GetValue(), self.noe_sat_1_copy_1.GetValue(), self.noe_ref_err_1_copy_1.GetValue(), self.noe_sat_err_1_copy_1.GetValue(), self.nmrfreq_value_noe1_copy_1.GetValue(),self.structure_noe1_copy_1.GetValue(), self.unres_noe1_copy_1.GetValue(), start_relax, self, 3)
        event.Skip()

### T1 no. 3

    def resdir_t1_3(self, event): # wxGlade: main.<event_handler>
        backup = self.resultsdir_t11_copy_1.GetValue()
        t1_savedir[2] = diropenbox(msg='Select results directory', title='relaxGUI', default=self.resultsdir_t11_copy_1.GetValue() + '/')
        if t1_savedir[2] == None:
           t1_savedir[2] = backup
        self.resultsdir_t11_copy_1.SetValue(t1_savedir[2])
        event.Skip()

    def add_t1_3(self, event): # wxGlade: main.<event_handler>
        if len(t1_list3) < 14:
             t1_entry3 = fileopenbox(msg='Select T1 peak list file', title=None, default=self.resultsdir_t11_copy_1.GetValue() + '/', filetypes=None)
             if not t1_entry3 == None:
                t1_list3.append(t1_entry3)

        if len(t1_list3) == 1:
            self.t1_list_1_copy_1.SetLabel(t1_list3[0]) 
        if len(t1_list3) == 2:
            self.t1_list_2_copy_1.SetLabel(t1_list3[1]) 
        if len(t1_list3) == 3:
            self.t1_list_3_copy_1.SetLabel(t1_list3[2]) 
        if len(t1_list3) == 4:
            self.t1_list_4_copy_1.SetLabel(t1_list3[3]) 
        if len(t1_list3) == 5:
            self.t1_list_5_copy_1.SetLabel(t1_list3[4]) 
        if len(t1_list3) == 6:
            self.t1_list_6_copy_1.SetLabel(t1_list3[5]) 
        if len(t1_list3) == 7:
            self.t1_list_7_copy_1.SetLabel(t1_list3[6]) 
        if len(t1_list3) == 8:
            self.t1_list_8_copy_1.SetLabel(t1_list3[7]) 
        if len(t1_list3) == 9:
            self.t1_list_9_copy_1.SetLabel(t1_list3[8]) 
        if len(t1_list3) == 10:
            self.t1_list_10_copy_1.SetLabel(t1_list3[9]) 
        if len(t1_list3) == 11:
            self.t1_list_11_copy_1.SetLabel(t1_list3[10]) 
        if len(t1_list3) == 12:
            self.t1_list_12_copy_1.SetLabel(t1_list3[11]) 
        if len(t1_list3) == 13:
            self.t1_list_1_copy_11_copy_1.SetLabel(t1_list3[12]) 
        if len(t1_list3) == 14:
            self.t1_list_14_copy_1.SetLabel(t1_list3[13])              
        event.Skip()

    def refresh_t1_3(self, event): # wxGlade: main.<event_handler>
        self.t1_list_1_copy_1.SetLabel('')
        self.t1_list_2_copy_1.SetLabel('')
        self.t1_list_3_copy_1.SetLabel('')
        self.t1_list_4_copy_1.SetLabel('')
        self.t1_list_5_copy_1.SetLabel('')
        self.t1_list_6_copy_1.SetLabel('')
        self.t1_list_7_copy_1.SetLabel('')
        self.t1_list_8_copy_1.SetLabel('')
        self.t1_list_9_copy_1.SetLabel('')
        self.t1_list_10_copy_1.SetLabel('')
        self.t1_list_11_copy_1.SetLabel('')
        self.t1_list_12_copy_1.SetLabel('')
        self.t1_list_1_copy_11_copy_1.SetLabel('')
        self.t1_list_14_copy_1.SetLabel('')
        del t1_list3[0:len(t1_list3)]
        event.Skip()

    def exec_t1_3(self, event): # wxGlade: main.<event_handler>
        relax_times_t1_3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #create relaxation time list
        relax_times_t1_3[0] = str(self.t1_time_1_copy_1.GetValue()) 
        relax_times_t1_3[1] = str(self.t1_time_2_copy_1.GetValue()) 
        relax_times_t1_3[2] = str(self.t1_time_3_copy_1.GetValue()) 
        relax_times_t1_3[3] = str(self.t1_time_4_copy_1.GetValue()) 
        relax_times_t1_3[4] = str(self.t1_time_5_copy_1.GetValue()) 
        relax_times_t1_3[5] = str(self.t1_time_6_copy_1.GetValue()) 
        relax_times_t1_3[6] = str(self.t1_time_7_copy_1.GetValue()) 
        relax_times_t1_3[7] = str(self.t1_time_8_copy_1.GetValue()) 
        relax_times_t1_3[8] = str(self.t1_time_9_copy_1.GetValue()) 
        relax_times_t1_3[9] = str(self.t1_time_10_copy_1.GetValue()) 
        relax_times_t1_3[10] = str(self.t1_time_11_copy_1.GetValue()) 
        relax_times_t1_3[11] = str(self.t1_time_12_copy_1.GetValue()) 
        relax_times_t1_3[12] = str(self.t1_time_13_copy_1.GetValue()) 
        relax_times_t1_3[13] = str(self.t1_time_1_4_copy_1.GetValue()) 
        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= homedir + 'res/pics/relax.gif')
        if start_relax == True:
           make_tx(self.resultsdir_t11_copy_1.GetValue(), relax_times_t1_3, self.structure_t11_copy_1.GetValue(), self.nmrfreq_value_t11_copy_1.GetValue(), 1, 3, self.unresolved_t11_copy_1.GetValue(), self,3)
        event.Skip()


### T2 no. 3

    def resdir_t2_3(self, event): # results dir T2 3
        backup = self.resultsdir_t21_copy_1.GetValue()
        t2_savedir[2] = diropenbox(msg='Select results directory', title='relaxGUI', default=self.resultsdir_t21_copy_1.GetValue() + '/')
        if t2_savedir[2] == None:
           t2_savedir[2] = backup
        self.resultsdir_t21_copy_1.SetValue(t2_savedir[2])
        event.Skip()

    def add_t2_3(self, event): # add T2 peakfile no. 3
        if len(t2_list3) < 14:
             t2_entry3 = fileopenbox(msg='Select T2 peak list file', title='relaxGUI', default=self.resultsdir_t21_copy_1.GetValue() + '/', filetypes=None)
             if not t2_entry3 == None:
                t2_list3.append(t2_entry3)
        if len(t2_list3) == 1:
            self.t2_list_1_copy_1.SetLabel(t2_list3[0]) 
        if len(t2_list3) == 2:
            self.t2_list_2_copy_1.SetLabel(t2_list3[1]) 
        if len(t2_list3) == 3:
            self.t2_list_3_copy_1.SetLabel(t2_list3[2]) 
        if len(t2_list3) == 4:
            self.t2_list_4_copy_1.SetLabel(t2_list3[3]) 
        if len(t2_list3) == 5:
            self.t2_list_5_copy_1.SetLabel(t2_list3[4]) 
        if len(t2_list3) == 6:
            self.t2_list_6_copy_1.SetLabel(t2_list3[5]) 
        if len(t2_list3) == 7:
            self.t2_list_7_copy_1.SetLabel(t2_list3[6]) 
        if len(t2_list3) == 8:
            self.t2_list_8_copy_1.SetLabel(t2_list3[7]) 
        if len(t2_list3) == 9:
            self.t2_list_9_copy_1.SetLabel(t2_list3[8]) 
        if len(t2_list3) == 10:
            self.t2_list_10_copy_1.SetLabel(t2_list3[9]) 
        if len(t2_list3) == 11:
            self.t2_list_11_copy_1.SetLabel(t2_list3[10]) 
        if len(t2_list3) == 12:
            self.t2_list_12_copy_1.SetLabel(t2_list3[11]) 
        if len(t2_list3) == 13:
            self.t2_list_13_copy_1.SetLabel(t2_list3[12]) 
        if len(t2_list3) == 14:
            self.t2_list_14_copy_1.SetLabel(t2_list3[13])              
        event.Skip()

    def refresh_t2_3(self, event): # refresh t2 list no. 3
        self.t2_list_1_copy_1.SetLabel('')
        self.t2_list_2_copy_1.SetLabel('')
        self.t2_list_3_copy_1.SetLabel('')
        self.t2_list_4_copy_1.SetLabel('')
        self.t2_list_5_copy_1.SetLabel('')
        self.t2_list_6_copy_1.SetLabel('')
        self.t2_list_7_copy_1.SetLabel('')
        self.t2_list_8_copy_1.SetLabel('')
        self.t2_list_9_copy_1.SetLabel('')
        self.t2_list_10_copy_1.SetLabel('')
        self.t2_list_11_copy_1.SetLabel('')
        self.t2_list_12_copy_1.SetLabel('')
        self.t2_list_13_copy_1.SetLabel('')
        self.t2_list_14_copy_1.SetLabel('')
        del t2_list3[0:len(t2_list3)]
        event.Skip()

    def exec_t2_3(self, event): # wxGlade: main.<event_handler>
        relax_times_t2_3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        #create relaxation time list
        relax_times_t2_3[0] = str(self.t2_time_1_copy_1.GetValue()) 
        relax_times_t2_3[1] = str(self.t2_time_2_copy_1.GetValue()) 
        relax_times_t2_3[2] = str(self.t2_time_3_copy_1.GetValue()) 
        relax_times_t2_3[3] = str(self.t2_time_4_copy_1.GetValue()) 
        relax_times_t2_3[4] = str(self.t2_time_5_copy_1.GetValue()) 
        relax_times_t2_3[5] = str(self.t2_time_6_copy_1.GetValue()) 
        relax_times_t2_3[6] = str(self.t2_time_7_copy_1.GetValue()) 
        relax_times_t2_3[7] = str(self.t2_time_8_copy_1.GetValue()) 
        relax_times_t2_3[8] = str(self.t2_time_9_copy_1.GetValue()) 
        relax_times_t2_3[9] = str(self.t2_time_10_copy_1.GetValue()) 
        relax_times_t2_3[10] = str(self.t2_time_11_copy_1.GetValue()) 
        relax_times_t2_3[11] = str(self.t2_time_12_copy_1.GetValue()) 
        relax_times_t2_3[12] = str(self.t2_time_13_copy_1.GetValue()) 
        relax_times_t2_3[13] = str(self.t2_time_14_copy_1.GetValue()) 

        start_relax = boolbox(msg='Start relax?', title='relaxGUI ', choices=('Yes', 'No'), image= homedir + 'res/pics/relax.gif')
        if start_relax == True:
           make_tx(self.resultsdir_t21_copy_1.GetValue(), relax_times_t2_3, self.structure_t11_copy_1.GetValue(), self.nmrfreq_value_t11_copy_1.GetValue(), 2, 3, self.unresolved_t11_copy_1.GetValue(), self,3)
        event.Skip()

### Model-free analysis

    def model_noe1(self, event): # load noe1
        backup = self.m_noe_1.GetValue() 
        paramfiles1[0] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_noe_1.GetValue() + '/', filetypes=None)
        if paramfiles1[0] == None:
           paramfiles1[0] = backup
        self.m_noe_1.SetValue(paramfiles1[0])
        event.Skip()

    def model_r11(self, event): # 
        backup = self.m_r1_1.GetValue() 
        paramfiles1[1] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_r1_1.GetValue() + '/', filetypes=None)
        if paramfiles1[1] == None:
           paramfiles1[1] = backup
        self.m_r1_1.SetValue(paramfiles1[1])
        event.Skip()

    def model_r21(self, event): # 
        backup = self.m_r2_1.GetValue() 
        paramfiles1[2] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_r2_1.GetValue() + '/', filetypes=None)
        if paramfiles1[2] == None:
           paramfiles1[2] = backup
        self.m_r2_1.SetValue(paramfiles1[2])
        event.Skip()

    def model_noe2(self, event): # load noe1
        backup = self.m_noe_2.GetValue() 
        paramfiles2[0] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_noe_2.GetValue() + '/', filetypes=None)
        if paramfiles2[0] == None:
           paramfiles2[0] = backup
        self.m_noe_2.SetValue(paramfiles2[0])
        event.Skip()

    def model_r12(self, event): # 
        backup = self.m_r1_2.GetValue() 
        paramfiles2[1] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_r1_2.GetValue() + '/', filetypes=None)
        if paramfiles2[1] == None:
           paramfiles2[1] = backup
        self.m_r1_2.SetValue(paramfiles2[1])
        event.Skip()

    def model_r22(self, event): # 
        backup = self.m_r2_2.GetValue() 
        paramfiles2[2] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_r2_2.GetValue() + '/', filetypes=None)
        if paramfiles2[2] == None:
           paramfiles2[2] = backup
        self.m_r2_2.SetValue(paramfiles2[2])
        event.Skip()

    def model_noe3(self, event): # load noe1
        backup = self.m_noe_3.GetValue() 
        paramfiles3[0] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_noe_3.GetValue() + '/', filetypes=None)
        if paramfiles3[0] == None:
           paramfiles3[0] = backup
        self.m_noe_3.SetValue(paramfiles3[0])
        event.Skip()

    def model_r13(self, event): 
        backup = self.m_r1_3.GetValue() 
        paramfiles3[1] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_r1_3.GetValue() + '/', filetypes=None)
        if paramfiles3[1] == None:
           paramfiles3[1] = backup
        self.m_r1_3.SetValue(paramfiles3[1])
        event.Skip()

    def model_r23(self, event): 
        backup = self.m_r2_3.GetValue() 
        paramfiles3[2] = fileopenbox(msg='Select NOE peak list file', title='relaxGUI', default=self.m_r2_3.GetValue() + '/', filetypes=None)
        if paramfiles3[2] == None:
           paramfiles3[2] = backup
        self.m_r2_3.SetValue(paramfiles3[2])
        event.Skip()

    def sel_aic(self, event): 
        selection = "AIC" 
        event.Skip()

    def sel_bic(self, event): 
        selection = "BIC"
        event.Skip()

    def resdir_modelfree(self, event): 
        backup = self.resultsdir_t21_copy_2.GetValue()
        results_dir_model = diropenbox(msg='Select results directory', title='relaxGUI', default=backup + '/')
        if results_dir_model == None:
           results_dir_model = backup
        self.resultsdir_t21_copy_2.SetValue(results_dir_model)
        event.Skip()

    def exec_model_free(self, event):
        which_model = buttonbox(msg='Start relax?', title='relaxGUI', choices=('local_tm', 'sphere', 'oblate', 'prolate', 'ellipsoid','final', 'cancel'), image=homedir + 'res/pics/relax.gif', root=None) 
        if not which_model == 'cancel':
           start_model_free(self, which_model)
        event.Skip()   

    def open_noe_results_exe(self, event): 
        choice = self.list_noe.GetStringSelection()
        see_results(choice)
        event.Skip()

    def open_tx_results_exe(self, event): 
        choice = self.list_tx.GetStringSelection()
        see_results(choice)
        event.Skip()

    def open_model_results_exe(self, event): 
        choice = self.list_modelfree.GetStringSelection()
        see_results(choice)
        event.Skip()
