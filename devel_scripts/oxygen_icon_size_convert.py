"""Script to convert oxygen icons to different sizes, and copy to path in relax"""

# Python module imports.
from os import F_OK, access, getcwd, makedirs, path, sep
import shutil
import subprocess
from tempfile import mkdtemp

# relax module imports.
from status import Status; status = Status()

# Set the relax dir
rdir = status.install_path

# Set the path to the oxygen icon start dir.
# svn co svn://anonsvn.kde.org/home/kde/trunk/kdesupport/oxygen-icons
odir = status.install_path + sep + '..' + sep + 'oxygen-icons'

# Set the category for the icon
cat = 'actions'

# Set the icon filename
icon = 'document-preview-archive'

# Define sizes for relax
sizes = [[16,16], [22,22], [32,32], [48,48], [128,128], [200,'']]

# First make a conversion dir
cdir = rdir + sep + 'graphics' + sep + 'oxygen_icons' + sep + 'temp_conversion'

# Make the dir
if not path.exists(cdir):
    makedirs(cdir)

# Copy the scalable file.
filein = odir + sep + 'scalable' + sep + cat + sep + icon + '.svgz'
shutil.copy(filein, cdir)
filein = cdir + sep + icon + '.svgz'

# Define Call function.
def call_prog(list_args):
    Temp = subprocess.Popen(list_args, stdout=subprocess.PIPE)

    ## Communicate with program, and get outout and exitcode.
    (output, errput) = Temp.communicate()

    ## Wait for finish and get return code.
    return_value = Temp.wait()

    return return_value

# Now make the conversion
if True:
    for size in sizes:
        # Extract size.
        x, y = size

        fileout = cdir + sep + "%s_%sx%s.png" %(icon, x, y)
        if y != '':
            list_args = ['inkscape', '-z', '-e', fileout, '-w', str(x), '-h', str(y), filein]
        else:
            list_args = ['inkscape', '-z', '-e', fileout, '-w', str(x), filein]


        # Call the conversion
        return_value = call_prog(list_args)
        # Print the command
        str1 = ' '.join(list_args)
    
        print(return_value, str1)

# Check if the file already exist in 
if True:
    for size in sizes:
        # Extract size.
        x, y = size

        fileor = odir + sep + '%sx%s'%(x, y) + sep + cat + sep + icon + '.png'
        file_ex = path.isfile(fileor)

        print(file_ex, fileor)

        # It the file exists:
        if file_ex:
            fileout = cdir + sep + "%s_%sx%s_or.png" %(icon, x, y)
            shutil.copy(fileor, fileout)
