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
from os import sep, system
import time
import wx
import wx.grid

# relax module imports.
from prompt.interpreter import Interpreter
from generic_fns.mol_res_spin import spin_loop

# relax GUI module imports.
from gui_bieri.paths import IMAGE_PATH


def color_code_noe(self, target_dir, pdb_file):
    """Create PyMol Macro for NOE colouring."""

    directory = target_dir

    #create file
    file = open(directory + sep + 'noe.pml', 'w')
    if pdb_file:
        file.write("load " + pdb_file + '\n')
    file.write("bg_color white\n")
    file.write("color gray90\n")
    file.write("hide all\n")
    file.write("show ribbon\n")

    for spin, spin_id in spin_loop(return_id=True):
        #select residue
        spin_no = spin_id[spin_id.index(':')+1:spin_id.index('&')]

        #ribbon color
        if hasattr(spin, 'noe'):
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


def model_free_results(self, directory, pdbfile):
    """Create the model-free results."""

    # Load the interpreter.
    interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
    interpreter.populate_self()
    interpreter.on(verbose=False)

    directory = directory + sep + 'final'

    #Read results
    pipename = 'Data_extraction ' + str(time.asctime(time.localtime()))
    interpreter.pipe.create(pipename, 'mf')
    interpreter.results.read(directory+sep+'results')

    #create a table file and variables for results table

    residue = []
    model = []
    s2 = []
    rex = []
    te = []

    #create file
    file = open(str(directory) + sep + 'Model-free_Results.csv', 'w')
    file.write('Data Extraction by relaxGUI, (C) 2009 Michael Bieri')
    file.write("\n")
    file.write("\n")
    file.write("Residue;Model;S2;Rex [1/s];Te;Relaxation Parameters\n")
    file.write("\n")

    #loop over residues
    for spin, spin_id in spin_loop(return_id=True):
        # The spin ID string.
        spin_no = spin_id[spin_id.index(':')+1:spin_id.index('&')]
        spin_res = spin_id[spin_id.index('&')+2:spin_id.index('@')]
        file.write((spin_res) + " " + (spin_no))
        residue.append(spin_res)
        # The spin is not selected.
        if not spin.select:
            file.write("\n")
            continue

        # The model-free model.
        if hasattr(spin, 'model'):
            spin.model = spin.model[1:2]
            file.write(";" + spin.model)
            model.append(spin.model)

        # S2.
        if hasattr(spin, 's2'):
            s2_value = str(spin.s2)
            s2_err = str(spin.s2_err)
            if spin.s2 == None:
                file.write(";")
                s2.append('')
            else:
                file.write(";" + s2_value[0:5]+ " +/- " + s2_err[0:4])
                s2.append(s2_value[0:5]+ " +/- " + s2_err[0:4])

        # Rex.
        if hasattr(spin, 'rex'):
            rex_value = str(spin.rex)
            rex_err = str(spin.rex_err)
            if spin.rex == None:
                file.write(";")
                rex.append('')
            else:
                rex_eff = float(spin.rex) * (int(spin.frq_labels[1]) * 1000000 * 2 * 3.14159)**2
                rex_value = str(rex_eff)
                rex_err_eff = float(spin.rex_err) * (int(spin.frq_labels[1]) * 1000000 * 2 * 3.14159)**2
                rex_err = str(rex_err_eff)
                file.write(";" + rex_value[0:5]+ " +/- " + rex_err[0:4])
                rex.append(rex_value[0:5]+ " +/- " + rex_err[0:4])

        # Te
        if hasattr(spin, 'te'):
            if spin.te == None:
                file.write(";")
                te.append('')
            else:
                te_ps = spin.te * 1e-12
                te_value = str(te_ps)
                te_err = str(spin.te_err)
                file.write(";" + te_value[0:5]+ " +/- " + te_err[0:4])
                te.append(te_value[0:5]+ " +/- " + te_err[0:4])

        # Parameters.
        if hasattr(spin, 'params'):
            file.write(";" + str(spin.params[0:len(spin.params)]))
        else:
            file.write(";\n")
            continue

        # Start a new line.
        file.write("\n")

    file.close()

    ##################################################################################################

    #Create Single Data Files
    print 'here'
    interpreter.value.write(param='rex', file='rex.txt', dir=str(directory) + sep + 'final_results', force=True)
    interpreter.value.write(param='s2', file='s2.txt', dir=str(directory) + sep + 'final_results', force=True)
    interpreter.value.write(param='s2f', file='s2f.txt', dir=str(directory) + sep + 'final_results', force=True)
    interpreter.value.write(param='s2s', file='s2s.txt', dir=str(directory) + sep + 'final_results', force=True)
    interpreter.value.write(param='te', file='te.txt', dir=str(directory) + sep + 'final_results', force=True)
    interpreter.value.write(param='tf', file='tf.txt', dir=str(directory) + sep + 'final_results', force=True)
    interpreter.value.write(param='ts', file='ts.txt', dir=str(directory) + sep + 'final_results', force=True)
    interpreter.value.write(param='rex', file='rex.txt', dir=str(directory) + sep + 'final_results', force=True)
    interpreter.value.write(param='r', file='r.txt', dir=str(directory) + sep + 'final_results', force=True)
    interpreter.value.write(param='rex', file='rex.txt', dir=str(directory) + sep + 'final_results', force=True)
    interpreter.value.write(param='csa', file='csa.txt', dir=str(directory) + sep + 'final_results', force=True)
    interpreter.value.write(param='rex', file='rex.txt', dir=str(directory) + sep + 'final_results', force=True)
    interpreter.value.write(param='local_tm', file='local_tm.txt', dir=str(directory) + sep + 'final_results', force=True)

    ##################################################################################################

    #Create Grace Plots

    interpreter.grace.write(x_data_type='spin', y_data_type='s2', file='s2.agr', dir=str(directory) + sep + 'grace', force=True)
    interpreter.grace.write(x_data_type='spin', y_data_type='te', file='te.agr', dir=str(directory) + sep + 'grace', force=True)
    interpreter.grace.write(x_data_type='spin', y_data_type='s2f', file='s2f.agr', dir=str(directory) + sep + 'grace', force=True)
    interpreter.grace.write(x_data_type='spin', y_data_type='s2s', file='s2s.agr', dir=str(directory) + sep + 'grace', force=True)
    interpreter.grace.write(x_data_type='spin', y_data_type='ts', file='ts.agr', dir=str(directory) + sep + 'grace', force=True)
    interpreter.grace.write(x_data_type='spin', y_data_type='tf', file='tf.agr', dir=str(directory) + sep + 'grace', force=True)
    interpreter.grace.write(x_data_type='spin', y_data_type='csa', file='csa.agr', dir=str(directory) + sep + 'grace', force=True)
    interpreter.grace.write(x_data_type='te', y_data_type='s2', file='s2-te.agr', dir=str(directory) + sep + 'grace', force=True)

    ##################################################################################################

    #Create Diffusion Tensor

    # Display the diffusion tensor.
    interpreter.diffusion_tensor.display()

    # Create the tensor PDB file.
    tensor_file = 'tensor.pdb'
    interpreter.structure.create_diff_tensor_pdb(file=tensor_file, dir=str(directory) + sep, force=True)

    # create diffusion tensor macro
    file = open(str(directory) + sep + 'diffusion_tensor.pml', 'w')
    file.write('load ' + pdbfile + '\n')
    file.write('color red, ss h\n')
    file.write('color yellow, ss s\n')
    file.write('color green, ss l+''\n')
    file.write('set cartoon_discrete_colors, 1\n')
    file.write('hide all\n')
    file.write('show cartoon\n')
    file.write('load ' + str(directory) + sep + 'tensor.pdb' + '\n')
    file.close()

    ##################################################################################################

    # Create S2 Macro for PyMol

    #create file

    file = open(str(directory) +sep + 's2.pml', 'w')
    if pdbfile:
        file.write("load " + pdbfile + '\n')
    file.write("bg_color white\n")
    file.write("color gray90\n")
    file.write("hide all\n")
    file.write("show ribbon\n")

    for spin, spin_id in spin_loop(return_id=True):
        #select residue
        spin_no = spin_id[spin_id.index(':')+1:spin_id.index('&')]

        #ribbon color
        if hasattr(spin, 's2'):
            s2 = str(spin.s2)
            if spin.s2 == None:
                file.write("")
            else:
                width = ((1-spin.s2) * 2)
                green = 1 - ((spin.s2)**3)
                green = green * green * green #* green * green
                green = 1 - green
                file.write("set_color resicolor" + spin_no + ", [1," + str(green) + ",0]\n")
                file.write("color resicolor" + spin_no + ", resi " + spin_no + "\n")
                file.write("set_bond stick_radius, " + str(width) + ", resi " + spin_no + "\n")

    file.write("hide all\n")
    file.write("show sticks, name C+N+CA\n")
    file.write("set stick_quality, 10\n")
    file.write("ray\n")
    file.close()

    ##################################################################################################

    # Create Rex Macro for PyMol

    #create file

    file = open(str(directory) + sep + 'rex.pml', 'w')
    if pdbfile:
        file.write("load " + pdbfile + '\n')
    file.write("bg_color white\n")
    file.write("color gray90\n")
    file.write("hide all\n")
    file.write("show ribbon\n")

    max_rex = 0

    #find max Rex
    for spin, spin_id in spin_loop(return_id=True):
        if hasattr(spin, 'rex'):
            if not spin.rex == None:
                if spin.rex > max_rex:
                    max_rex = spin.rex


    for spin, spin_id in spin_loop(return_id=True):
        #select residue
        spin_no = spin_id[spin_id.index(':')+1:spin_id.index('&')]

        #ribbon color
        if hasattr(spin, 'rex'):
            rex = str(spin.rex)
            if spin.rex == None:
                file.write("")
            else:
                rel_rex = spin.rex / max_rex
                width = ((rel_rex) * 2)
                green = ((rel_rex))
                green = green * green * green #* green * green
                green = 1 - green
                file.write("set_color resicolor" + spin_no + ", [1," + str(green) + ",0]\n")
                file.write("color resicolor" + spin_no + ", resi " + spin_no + "\n")
                file.write("set_bond stick_radius, " + str(width) + ", resi " + spin_no + "\n")

    file.write("hide all\n")
    file.write("show sticks, name C+N+CA\n")
    file.write("set stick_quality, 10\n")
    file.write("ray\n")
    file.close()

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
    print "@diffusion_tensor.pml, @rex.pml and @s2.pml"

    returnstring = [residue, model, s2, rex, te]
    return returnstring # return data for results table dialog


def results_table(import_results):
    global residue
    global model
    global s2
    global rex
    global te
    residue = import_results[0]
    model = import_results[1]
    s2 = import_results[2]
    rex = import_results[3]
    te = import_results[4]

    frame_3 = final_results(None, -1, "")
    frame_3.ShowModal()


def see_results(openfile, import_results):
    """Open results."""

    if '.agr' in openfile:
        system('xmgrace ' + openfile + ' &')

    if '.txt' in openfile:
        system('gedit ' + openfile + ' &')

    if '.pml' in openfile:
        system('pymol ' + openfile + ' &')

    if 'Table_of_Results' in openfile:
        results_table(import_results)



class Final_results(wx.Dialog):        # Dialog that displays relax results in window
    def __init__(self, *args, **kwds):
        # begin final_results.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_1 = wx.StaticText(self, -1, "Results of relax Analysis")
        self.grid_1 = wx.grid.Grid(self, -1, size=(1, 1))
        self.close_button = wx.Button(self, -1, "Close")

        self.__set_properties()
        self.__do_layout()
        self._fill_values()

        self.Bind(wx.EVT_BUTTON, self.close_table, self.close_button)


    def __do_layout(self):
        # begin final_results.__do_layout
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.label_1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)
        sizer_2.Add(self.grid_1, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_2.Add(self.close_button, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_2)
        self.Layout()


    def __set_properties(self):
        # begin final_results.__set_properties
        self.SetTitle("relaxGUI")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.SetSize((700, 600))
        self.label_1.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.grid_1.CreateGrid(len(residue), 5)
        self.grid_1.SetColLabelValue(0, "Residue")
        self.grid_1.SetColSize(0, 80)
        self.grid_1.SetColLabelValue(1, "Model")
        self.grid_1.SetColSize(1, 70)
        self.grid_1.SetColLabelValue(2, "S2")
        self.grid_1.SetColSize(2, 150)
        self.grid_1.SetColLabelValue(3, "Rex [1/s]")
        self.grid_1.SetColSize(3, 150)
        self.grid_1.SetColLabelValue(4, "te")
        self.grid_1.SetColSize(4, 150)


    def _fill_values(self):  # fill entries in table
        for i in range(0, len(residue)):
            self.grid_1.SetCellValue(i, 0, residue[i])
            self.grid_1.SetCellValue(i, 1, model[i])
            self.grid_1.SetCellValue(i, 2, s2[i])
            self.grid_1.SetCellValue(i, 3, rex[i])
            self.grid_1.SetCellValue(i, 4, te[i])


    def close_table(self, event): # close
        self.Destroy()
        event.Skip()
