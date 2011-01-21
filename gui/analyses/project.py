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

# script to organize project

# Python module imports.
from string import replace


#create list from string

def stringtolist(string):
    entrynum = 1
    string = string[2:(len(string)-2)]
    string = replace(string, "'", "")
    string = replace(string, "[", "")
    string = replace(string, "]", "")
    returnlist = (replace(string, ' ', '')).split(',')
    return(returnlist)

## save relaxGUI project

def create_save_file(self, filename, results_table, global_setting, file_setting, sequencefile):

           #global definitions 
           globalsave = [str(self.structure_noe1.GetValue())]
         
           # NOE
           savenoe1 = [str(self.nmrfreq_value_noe1.GetValue()), str(self.noe_sat_1.GetValue()), str(self.noe_sat_err_1.GetValue()), str(self.noe_ref_1.GetValue()), str(self.noe_ref_err_1.GetValue()), str(self.structure_noe1.GetValue()), replace(str(self.unres_noe1.GetValue()), ',',';'), str(self.res_noe1.GetValue())]
           savenoe2 = [str(self.nmrfreq_value_noe1_copy.GetValue()), str(self.noe_sat_1_copy.GetValue()), str(self.noe_sat_err_1_copy.GetValue()), str(self.noe_ref_1_copy.GetValue()), str(self.noe_ref_err_1_copy.GetValue()), str(self.structure_noe1_copy.GetValue()), str(self.unres_noe1_copy.GetValue()), str(self.res_noe1_copy.GetValue())]
           savenoe3 = [str(self.nmrfreq_value_noe1_copy_1.GetValue()), str(self.noe_sat_1_copy_1.GetValue()), str(self.noe_sat_err_1_copy_1.GetValue()), str(self.noe_ref_1_copy_1.GetValue()), str(self.noe_ref_err_1_copy_1.GetValue()), str(self.structure_noe1_copy_1.GetValue()), str(self.unres_noe1_copy_1.GetValue()), str(self.res_noe1_copy_1.GetValue())]

           #R1
           r1_list_1 = str(self.r1_list_1.GetLabel()) + ', ' + str(self.r1_list_2.GetLabel()) + ', ' + str(self.r1_list_3.GetLabel()) + ', ' + str(self.r1_list_4.GetLabel()) + ', ' + str(self.r1_list_5.GetLabel()) + ', ' + str(self.r1_list_6.GetLabel()) + ', ' + str(self.r1_list_7.GetLabel()) + ', ' + str(self.r1_list_8.GetLabel()) + ', ' + str(self.r1_list_9.GetLabel()) + ', ' + str(self.r1_list_10.GetLabel()) + ', ' + str(self.r1_list_11.GetLabel()) + ', ' + str(self.r1_list_12.GetLabel()) + ', ' + str(self.r1_list_1_copy_11.GetLabel()) + ', ' + str(self.r1_list_14.GetLabel())
           r1_time_1 = str(self.r1_time_1.GetValue()) + ', ' + str(self.r1_time_2.GetValue()) + ', ' + str(self.r1_time_3.GetValue()) + ', ' + str(self.r1_time_4.GetValue()) + ', ' + str(self.r1_time_5.GetValue()) + ', ' + str(self.r1_time_6.GetValue()) + ', ' + str(self.r1_time_7.GetValue()) + ', ' + str(self.r1_time_8.GetValue()) + ', ' + str(self.r1_time_9.GetValue()) + ', ' + str(self.r1_time_10.GetValue()) + ', ' + str(self.r1_time_11.GetValue()) + ', ' + str(self.r1_time_12.GetValue()) + ', ' + str(self.r1_time_13.GetValue()) + ', ' + str(self.r1_time_1_4.GetValue()) 

           r1_list_2 = str(self.r1_list_1_copy.GetLabel()) + ', ' + str(self.r1_list_2_copy.GetLabel()) + ', ' + str(self.r1_list_3_copy.GetLabel()) + ', ' + str(self.r1_list_4_copy.GetLabel()) + ', ' + str(self.r1_list_5_copy.GetLabel()) + ', ' + str(self.r1_list_6_copy.GetLabel()) + ', ' + str(self.r1_list_7_copy.GetLabel()) + ', ' + str(self.r1_list_8_copy.GetLabel()) + ', ' + str(self.r1_list_9_copy.GetLabel()) + ', ' + str(self.r1_list_10_copy.GetLabel()) + ', ' + str(self.r1_list_11_copy.GetLabel()) + ', ' + str(self.r1_list_12_copy.GetLabel()) + ', ' + str(self.r1_list_1_copy_11_copy.GetLabel()) + ', ' + str(self.r1_list_14_copy.GetLabel())
           r1_time_2 = str(self.r1_time_1_copy.GetValue()) + ', ' + str(self.r1_time_2_copy.GetValue()) + ', ' + str(self.r1_time_3_copy.GetValue()) + ', ' + str(self.r1_time_4_copy.GetValue()) + ', ' + str(self.r1_time_5_copy.GetValue()) + ', ' + str(self.r1_time_6_copy.GetValue()) + ', ' + str(self.r1_time_7_copy.GetValue()) + ', ' + str(self.r1_time_8_copy.GetValue()) + ', ' + str(self.r1_time_9_copy.GetValue()) + ', ' + str(self.r1_time_10_copy.GetValue()) + ', ' + str(self.r1_time_11_copy.GetValue()) + ', ' + str(self.r1_time_12_copy.GetValue()) + ', ' + str(self.r1_time_13_copy.GetValue()) + ', ' + str(self.r1_time_1_4_copy.GetValue()) 

           r1_list_3 = str(self.r1_list_1_copy_1.GetLabel()) + ', ' + str(self.r1_list_2_copy_1.GetLabel()) + ', ' + str(self.r1_list_3_copy_1.GetLabel()) + ', ' + str(self.r1_list_4_copy_1.GetLabel()) + ', ' + str(self.r1_list_5_copy_1.GetLabel()) + ', ' + str(self.r1_list_6_copy_1.GetLabel()) + ', ' + str(self.r1_list_7_copy_1.GetLabel()) + ', ' + str(self.r1_list_8_copy_1.GetLabel()) + ', ' + str(self.r1_list_9_copy_1.GetLabel()) + ', ' + str(self.r1_list_10_copy_1.GetLabel()) + ', ' + str(self.r1_list_11_copy_1.GetLabel()) + ', ' + str(self.r1_list_12_copy_1.GetLabel()) + ', ' + str(self.r1_list_1_copy_11_copy_1.GetLabel()) + ', ' + str(self.r1_list_14_copy_1.GetLabel())
           r1_time_3 = str(self.r1_time_1_copy_1.GetValue()) + ', ' + str(self.r1_time_2_copy_1.GetValue()) + ', ' + str(self.r1_time_3_copy_1.GetValue()) + ', ' + str(self.r1_time_4_copy_1.GetValue()) + ', ' + str(self.r1_time_5_copy_1.GetValue()) + ', ' + str(self.r1_time_6_copy_1.GetValue()) + ', ' + str(self.r1_time_7_copy_1.GetValue()) + ', ' + str(self.r1_time_8_copy_1.GetValue()) + ', ' + str(self.r1_time_9_copy_1.GetValue()) + ', ' + str(self.r1_time_10_copy_1.GetValue()) + ', ' + str(self.r1_time_11_copy_1.GetValue()) + ', ' + str(self.r1_time_12_copy_1.GetValue()) + ', ' + str(self.r1_time_13_copy_1.GetValue()) + ', ' + str(self.r1_time_1_4_copy_1.GetValue()) 

           saver11 = [str(self.nmrfreq_value_r11.GetValue()), str(self.resultsdir_r11.GetValue()), replace(str(self.unresolved_r11.GetValue()),',',';'), r1_list_1, r1_time_1]
           saver12 = [str(self.nmrfreq_value_r11_copy.GetValue()), str(self.resultsdir_r11_copy.GetValue()), replace(str(self.unresolved_r11_copy.GetValue()),',',';'), r1_list_2, r1_time_2]
           saver13 = [str(self.nmrfreq_value_r11_copy_1.GetValue()), str(self.resultsdir_r11_copy_1.GetValue()), replace(str(self.unresolved_r11_copy_1.GetValue()),',',';'), r1_list_3, r1_time_3]

           #R2
           r2_list_1 = str(self.r2_list_1.GetLabel()) + ', ' + str(self.r2_list_2.GetLabel()) + ', ' + str(self.r2_list_3.GetLabel()) + ', ' + str(self.r2_list_4.GetLabel()) + ', ' + str(self.r2_list_5.GetLabel()) + ', ' + str(self.r2_list_6.GetLabel()) + ', ' + str(self.r2_list_7.GetLabel()) + ', ' + str(self.r2_list_8.GetLabel()) + ', ' + str(self.r2_list_9.GetLabel()) + ', ' + str(self.r2_list_10.GetLabel()) + ', ' + str(self.r2_list_11.GetLabel()) + ', ' + str(self.r2_list_12.GetLabel()) + ', ' + str(self.r2_list_13.GetLabel()) + ', ' + str(self.r2_list_14.GetLabel())
           r2_time_1 = str(self.r2_time_1.GetValue()) + ', ' + str(self.r2_time_2.GetValue()) + ', ' + str(self.r2_time_3.GetValue()) + ', ' + str(self.r2_time_4.GetValue()) + ', ' + str(self.r2_time_5.GetValue()) + ', ' + str(self.r2_time_6.GetValue()) + ', ' + str(self.r2_time_7.GetValue()) + ', ' + str(self.r2_time_8.GetValue()) + ', ' + str(self.r2_time_9.GetValue()) + ', ' + str(self.r2_time_10.GetValue()) + ', ' + str(self.r2_time_11.GetValue()) + ', ' + str(self.r2_time_12.GetValue()) + ', ' + str(self.r2_time_13.GetValue()) + ', ' + str(self.r2_time_14.GetValue()) 

           r2_list_2 = str(self.r2_list_1_copy.GetLabel()) + ', ' + str(self.r2_list_2_copy.GetLabel()) + ', ' + str(self.r2_list_3_copy.GetLabel()) + ', ' + str(self.r2_list_4_copy.GetLabel()) + ', ' + str(self.r2_list_5_copy.GetLabel()) + ', ' + str(self.r2_list_6_copy.GetLabel()) + ', ' + str(self.r2_list_7_copy.GetLabel()) + ', ' + str(self.r2_list_8_copy.GetLabel()) + ', ' + str(self.r2_list_9_copy.GetLabel()) + ', ' + str(self.r2_list_10_copy.GetLabel()) + ', ' + str(self.r2_list_11_copy.GetLabel()) + ', ' + str(self.r2_list_12_copy.GetLabel()) + ', ' + str(self.r2_list_13_copy.GetLabel()) + ', ' + str(self.r2_list_14_copy.GetLabel())
           r2_time_2 = str(self.r2_time_1_copy.GetValue()) + ', ' + str(self.r2_time_2_copy.GetValue()) + ', ' + str(self.r2_time_3_copy.GetValue()) + ', ' + str(self.r2_time_4_copy.GetValue()) + ', ' + str(self.r2_time_5_copy.GetValue()) + ', ' + str(self.r2_time_6_copy.GetValue()) + ', ' + str(self.r2_time_7_copy.GetValue()) + ', ' + str(self.r2_time_8_copy.GetValue()) + ', ' + str(self.r2_time_9_copy.GetValue()) + ', ' + str(self.r2_time_10_copy.GetValue()) + ', ' + str(self.r2_time_11_copy.GetValue()) + ', ' + str(self.r2_time_12_copy.GetValue()) + ', ' + str(self.r2_time_13_copy.GetValue()) + ', ' + str(self.r2_time_14_copy.GetValue()) 

           r2_list_3 = str(self.r2_list_1_copy_1.GetLabel()) + ', ' + str(self.r2_list_2_copy_1.GetLabel()) + ', ' + str(self.r2_list_3_copy_1.GetLabel()) + ', ' + str(self.r2_list_4_copy_1.GetLabel()) + ', ' + str(self.r2_list_5_copy_1.GetLabel()) + ', ' + str(self.r2_list_6_copy_1.GetLabel()) + ', ' + str(self.r2_list_7_copy_1.GetLabel()) + ', ' + str(self.r2_list_8_copy_1.GetLabel()) + ', ' + str(self.r2_list_9_copy_1.GetLabel()) + ', ' + str(self.r2_list_10_copy_1.GetLabel()) + ', ' + str(self.r2_list_11_copy_1.GetLabel()) + ', ' + str(self.r2_list_12_copy_1.GetLabel()) + ', ' + str(self.r2_list_13_copy_1.GetLabel()) + ', ' + str(self.r2_list_14_copy_1.GetLabel())
           r2_time_3 = str(self.r2_time_1_copy_1.GetValue()) + ', ' + str(self.r2_time_2_copy_1.GetValue()) + ', ' + str(self.r2_time_3_copy_1.GetValue()) + ', ' + str(self.r2_time_4_copy_1.GetValue()) + ', ' + str(self.r2_time_5_copy_1.GetValue()) + ', ' + str(self.r2_time_6_copy_1.GetValue()) + ', ' + str(self.r2_time_7_copy_1.GetValue()) + ', ' + str(self.r2_time_8_copy_1.GetValue()) + ', ' + str(self.r2_time_9_copy_1.GetValue()) + ', ' + str(self.r2_time_10_copy_1.GetValue()) + ', ' + str(self.r2_time_11_copy_1.GetValue()) + ', ' + str(self.r2_time_12_copy_1.GetValue()) + ', ' + str(self.r2_time_13_copy_1.GetValue()) + ', ' + str(self.r2_time_14_copy_1.GetValue()) 

           saver21 = [str(self.nmrfreq_value_r21.GetValue()), str(self.resultsdir_r21.GetValue()), replace(str(self.unresolved_r21.GetValue()),',',';'), r2_list_1, r2_time_1]
           saver22 = [str(self.nmrfreq_value_r21_copy.GetValue()), str(self.resultsdir_r21_copy.GetValue()), replace(str(self.unresolved_r21_copy.GetValue()),',',';'), r2_list_2, r2_time_2]
           saver23 = [str(self.nmrfreq_value_r21_copy_1.GetValue()), str(self.resultsdir_r21_copy_1.GetValue()), replace(str(self.unresolved_r21_copy_1.GetValue()),',',';'), r2_list_3, r2_time_3]
           

           #model-free
           savemodel = [str(self.modelfreefreq1.GetValue()), str(self.m_noe_1.GetValue()), str(self.m_r1_1.GetValue()), str(self.m_r2_1.GetValue()), str(self.modelfreefreq2.GetValue()), str(self.m_noe_2.GetValue()), str(self.m_r1_2.GetValue()), str(self.m_r2_2.GetValue()), str(self.modelfreefreq3.GetValue()), str(self.m_noe_3.GetValue()), str(self.m_r1_3.GetValue()), str(self.m_r2_3.GetValue()), replace(str(self. unresolved_r21_copy_1_copy.GetValue()),',',';'), str(self.resultsdir_r21_copy_2.GetValue())]

           #results
           noeresult = []
           for i in range(0,self.list_noe.GetCount()):
              noeresult.append(str(self.list_noe.GetString(i)))
           rxresult = []
           for i in range(0,self.list_rx.GetCount()):
              rxresult.append(str(self.list_rx.GetString(i)))
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
           file.write('R1\n')
           file.write(str(saver11) + '\n')
           file.write(str(saver12) + '\n')
           file.write(str(saver13) + '\n')
           file.write('R2\n')
           file.write(str(saver21) + '\n')
           file.write(str(saver22) + '\n')
           file.write(str(saver23) + '\n')
           file.write('Model-free\n')
           file.write(str(savemodel) + '\n')
           file.write('Results\n')
           file.write(str(noeresult) +'\n')
           file.write(str(rxresult) +'\n')
           file.write(str(modelresult) +'\n')
           file.write('Settings\n')
           file.write(str(global_setting) + '\n')
           file.write(str(file_setting) + '\n')
           file.write(sequencefile + '\n')
           file.write('Results Table\n')
           file.write(str(results_table[0]) + '\n')
           file.write(str(results_table[1]) + '\n')
           file.write(str(results_table[2]) + '\n')
           file.write(str(results_table[3]) + '\n')
           file.write(str(results_table[4]) + '\n')
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
           self.structure_r11.SetValue(structure_file_pdb)
           self.structure_r21.SetValue(structure_file_pdb)
           self.structure_noe1_copy.SetValue(structure_file_pdb)
           self.structure_r11_copy.SetValue(structure_file_pdb)
           self.structure_r21_copy.SetValue(structure_file_pdb)
           self.structure_noe1_copy_1.SetValue(structure_file_pdb)
           self.structure_r11_copy_1.SetValue(structure_file_pdb)
           self.structure_r21_copy_1.SetValue(structure_file_pdb)
           self.structure_r21_copy_1_copy.SetValue(structure_file_pdb)

           # load NOE 1
           noes = stringtolist(saved[5])
           self.nmrfreq_value_noe1.SetValue(noes[0])
           self.noe_sat_1.SetValue(noes[1])
           self.noe_sat_err_1.SetValue(noes[2])
           self.noe_ref_1.SetValue(noes[3])
           self.noe_ref_err_1.SetValue(noes[4])
           self.structure_noe1.SetValue(noes[5])
           self.unres_noe1.SetValue(replace(noes[6],';',','))
           self.res_noe1.SetValue(noes[7])

           # load NOE 2
           noes = stringtolist(saved[6])
           self.nmrfreq_value_noe1_copy.SetValue(noes[0])
           self.noe_sat_1_copy.SetValue(noes[1])
           self.noe_sat_err_1_copy.SetValue(noes[2])
           self.noe_ref_1_copy.SetValue(noes[3])
           self.noe_ref_err_1_copy.SetValue(noes[4])
           self.structure_noe1_copy.SetValue(noes[5])
           self.unres_noe1_copy.SetValue(replace(noes[6],';',','))
           self.res_noe1_copy.SetValue(noes[7])

           # load NOE 3
           noes = stringtolist(saved[7])
           self.nmrfreq_value_noe1_copy_1.SetValue(noes[0])
           self.noe_sat_1_copy_1.SetValue(noes[1])
           self.noe_sat_err_1_copy_1.SetValue(noes[2])
           self.noe_ref_1_copy_1.SetValue(noes[3])
           self.noe_ref_err_1_copy_1.SetValue(noes[4])
           self.structure_noe1_copy_1.SetValue(noes[5])
           self.unres_noe1_copy_1.SetValue(replace(noes[6],';',','))
           self.res_noe1_copy_1.SetValue(noes[7])

           #load R1
           rx = stringtolist(saved[9])
           self.nmrfreq_value_r11.SetValue(rx[0])
           self.resultsdir_r11.SetValue(rx[1])
           self.unresolved_r11.SetValue(replace(rx[2],';',','))

           #load R1 2
           rx = stringtolist(saved[10])
           self.nmrfreq_value_r11_copy.SetValue(rx[0])
           self.resultsdir_r11_copy.SetValue(rx[1])
           self.unresolved_r11_copy.SetValue(replace(rx[2],';',','))

           #load R1 3
           rx = stringtolist(saved[11])
           self.nmrfreq_value_r21_copy_1.SetValue(rx[0])
           self.resultsdir_r21_copy_1.SetValue(rx[1])
           self.unresolved_r21_copy_1.SetValue(replace(rx[2],';',','))

           #load R1
           rx = stringtolist(saved[13])
           self.nmrfreq_value_r21.SetValue(rx[0])
           self.resultsdir_r21.SetValue(rx[1])
           self.unresolved_r21.SetValue(replace(rx[2],';',','))

           #load R1 2
           rx = stringtolist(saved[14])
           self.nmrfreq_value_r21_copy.SetValue(rx[0])
           self.resultsdir_r21_copy.SetValue(rx[1])
           self.unresolved_r21_copy.SetValue(replace(rx[2],';',','))

           #load R1 3
           rx = stringtolist(saved[15])
           self.nmrfreq_value_r21_copy_1.SetValue(rx[0])
           self.resultsdir_r21_copy_1.SetValue(rx[1])
           self.unresolved_r21_copy_1.SetValue(replace(rx[2],';',','))

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
           self.unresolved_r21_copy_1_copy.SetValue(replace(openmodel[12], ';',','))
           self.resultsdir_r21_copy_2.SetValue(openmodel[13])

           #results
           self.list_noe.Clear()  
           self.list_rx.Clear()  
           self.list_modelfree.Clear()  

           results = stringtolist(saved[19])
           for i in range(0,len(results)):
              self.list_noe.Append(str(results[i]))

           results = stringtolist(saved[20])
           for i in range(0,len(results)):
              self.list_rx.Append(str(results[i]))

           results = stringtolist(saved[21])
           for i in range(0,len(results)):
              self.list_modelfree.Append(str(results[i]))

           # relax and relaxGUI settings
           global_setting = stringtolist(saved[23])     
           file_setting = stringtolist(saved[24])
           sequencefile = saved[25]   
           resiude = stringtolist(saved[27])
           model = stringtolist(saved[28])
           s2 = stringtolist(saved[29])
           rex = stringtolist(saved[30])
           te = stringtolist(saved[31])

           print '\n\nSuccessfully opened Project ' + filename + '\n\n' 

           #create return list
           returnlist = [global_setting, file_setting, sequencefile, resiude, model, s2, rex, te]
           return returnlist
