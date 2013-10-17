#!/usr/bin/env python

import glob, os, sys
import shlex, subprocess
import argparse
from itertools import chain

# Add functioning for argument parsing
parser = argparse.ArgumentParser(description='Process grace files to images')
# Add argument type. Destination instance is set to types.
parser.add_argument('-g', action='store_true', dest='relax_gui', help='Make it possible to run script through relax GUI. Run by using User-functions -> script')
parser.add_argument('-l', nargs='+', action='append', dest='l', help='Make in possible to run scriptif relax has logfile turned on. Run by using User-functions -> script')
parser.add_argument('-t', nargs='+', action='append', dest='types', help='List image types for conversion. Execute script with: python %s -t PNG EPS ...'%(sys.argv[0]), default=[])

# Lets stop the execution and print help if no arguments are passed
if len(sys.argv)==1:
    print('system argument is:', sys.argv)
    parser.print_help()
    print('Performing a default PNG conversion')

# Parse the arguments to a Class instance object
args = parser.parse_args()
# If we run through the GUI, we cannot pass input arguments, so we make a default PNG option
if args.relax_gui:
    args.types = [['PNG']]
# If no input arguments, we make a default PNG option
if len(args.types) == 0:
    args.types = [['PNG']]

# The instance object will contain a list of lists. We convert this to one list.
types = list(chain.from_iterable(args.types))

# A easy search for files with *.agr, is to use glob, which is pathnames matching a specified pattern according to the rules used by the Unix shell, not opening a shell
gracefiles = glob.glob("*.agr")

# For png conversion, several parameters can be passed to xmgrace. These can be altered later afterwards, and the script rerun. 
# The option for transparent is good for poster or insertion in color backgrounds. The ability for this, still depends on xmgrace compilation
if "PNG" in types:
    pngpar = "png.par"
    if not os.path.isfile(pngpar):
        wpngpar = open(pngpar, "w")
        wpngpar.write("DEVICE \"PNG\" FONT ANTIALIASING on\n")
        wpngpar.write("DEVICE \"PNG\" OP \"transparent:on\"\n")
        wpngpar.write("DEVICE \"PNG\" OP \"compression:9\"\n")
        wpngpar.close()

# Now loop over the grace files
for grace in gracefiles:
    # Get the filename without extension
    fname = grace.split(".agr")[0]
    if "PNG" in types:
        # Produce the argument string
        im_args = r"xmgrace -hdevice PNG -hardcopy -param %s -printfile %s.png %s"%(pngpar, fname, grace)
        # Split the arguments the right way, to call xmgrace
        im_args = shlex.split(im_args)
        return_code = subprocess.call(im_args)
    if "EPS" in types:
        im_args = r"xmgrace -hdevice EPS -hardcopy -printfile %s.eps %s"%(fname, grace)
        im_args = shlex.split(im_args)
        return_code = subprocess.call(im_args)
    if ("JPG" or "JPEG") in types:
        im_args = r"xmgrace -hdevice JPEG -hardcopy -printfile %s.jpg %s"%(fname, grace)
        im_args = shlex.split(im_args)
        return_code = subprocess.call(im_args)
    if "SVG" in types:
        im_args = r"xmgrace -hdevice SVG -hardcopy -printfile %s.svg %s"%(fname, grace)
        im_args = shlex.split(im_args)
        return_code = subprocess.call(im_args)
