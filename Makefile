###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
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


# Variables.
sys = uname -o
mach = uname -m

SUBDIRS = maths_fns

INSTALL_PATH = /usr/local
RELAX_PATH = $(INSTALL_PATH)/relax


# Rule which is run when `make' is typed.
.PHONY : relax $(SUBDIRS)
relax : $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@


# Installation.
.PHONY : install
install :
	@echo -e "\nInstalling the program relax into $(INSTALL_PATH)\n\n"
	
	# Creating the directory.
	mkdir $(RELAX_PATH)
	
	@echo -e "\n\n"
	# Coping the files.
	cp -urvp * $(RELAX_PATH)
	
	@echo -e "\n\n"
	# Creating the symbolic link.
	ln -s $(RELAX_PATH)/relax $(INSTALL_PATH)/bin/relax
	
	@echo -e "\n\n"
	# Running relax to create the *.pyc files.
	@cd $(RELAX_PATH)
	relax --test


# Deinstallation.
.PHONY : uninstall
uninstall :
	@echo -e "\nUninstalling the program relax from $(INSTALL_PATH)\n\n"
	
	# Removing the directory.
	rm -rvf $(RELAX_PATH)
	
	@echo -e "\n\n"
	# Deleting the symbolic link.
	rm -vf $(INSTALL_PATH)/bin/relax


# Rule for compiling the manual.

.PHONY : manual
manual :
	@cd docs/latex; make manual

.PHONY : manual_nofetch
manual_nofetch :
	@cd docs/latex; make manual_nofetch

.PHONY : manual_html
manual_html :
	@cd docs/latex; make manual_html


# Rule for creating the package distribution.

.PHONY : dist
dist : relax
	@echo $(sys).$(mach)


# Clean up rule.

.PHONY : clean
clean :
	rm -f *.pyc */*.pyc */*/*.pyc */*/*/*.pyc
	rm -f *.bak */*.bak */*/*.bak */*/*/*.bak
	rm -f *.o */*.o */*/*.o */*/*/*.o
	rm -f *.so */*.so */*/*.so */*/*/*.so
	@cd docs/latex; make clean
