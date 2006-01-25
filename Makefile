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


# Includes.
###########

include version.py


# Variables.
############

sys = `echo -e \`uname -o\` | sed 's/\//-/g'`
mach = `uname -m`

# Distribution variables.
TAR_BIN_FILE = relax-$(version).$(sys).$(mach).tar.bz2
TAR_SRC_FILE = relax-$(version).src.tar.bz2

# Compilation subdirectories.
SUBDIRS = maths_fns

# Paths.
INSTALL_PATH = /usr/local
RELAX_PATH = $(INSTALL_PATH)/relax



# Rules.
########

# Rule which is run when `make' is typed.
.PHONY: relax $(SUBDIRS)
relax: $(SUBDIRS)

$(SUBDIRS):
	@echo -e "\n\n\n"
	@echo -e "###########################"
	@echo -e "# Compiling the C modules #"
	@echo -e "###########################\n\n"
	$(MAKE) -C $@



# Installation.
.PHONY: install
install:
	@echo -e "\n\n\n"
	@echo -e "####################"
	@echo -e "# Installing relax #"
	@echo -e "####################\n\n"
	@echo -e "Installing the program relax into $(INSTALL_PATH)\n\n"
	
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
.PHONY: uninstall
uninstall:
	@echo -e "\n\n\n"
	@echo -e "######################"
	@echo -e "# Uninstalling relax #"
	@echo -e "######################\n\n"
	@echo -e "\nUninstalling the program relax from $(INSTALL_PATH)\n\n"
	
	# Removing the directory.
	rm -rvf $(RELAX_PATH)
	
	@echo -e "\n\n"
	# Deleting the symbolic link.
	rm -vf $(INSTALL_PATH)/bin/relax



# Rules for compiling the manual.

.PHONY: manual
manual:
	@echo -e "\n\n\n"
	@echo -e "###########################"
	@echo -e "# Creating the PDF manual #"
	@echo -e "###########################\n\n"
	@cd docs/latex; make manual

.PHONY: manual_nofetch
manual_nofetch:
	@echo -e "\n\n\n"
	@echo -e "#############################################################"
	@echo -e "# Creating the PDF manual (without fetching the docstrings) #"
	@echo -e "#############################################################\n\n"
	@cd docs/latex; make manual_nofetch

.PHONY: manual_dist
manual_dist:
	@echo -e "\n\n\n"
	@echo -e "##############################################"
	@echo -e "# Creating the PDF manual (for distribution) #"
	@echo -e "##############################################\n\n"
	@cd docs/latex; make manual_dist

.PHONY: manual_html
manual_html:
	@echo -e "\n\n\n"
	@echo -e "############################"
	@echo -e "# Creating the HTML manual #"
	@echo -e "############################\n\n"
	@cd docs/latex; make manual_html



# Rule for creating the binary package distribution.
.PHONY: dist
binary_dist:
	@echo -e "\n"
	@echo -e "############################################"
	@echo -e "# Creating the binary distribution package #"
	@echo -e "############################################\n\n"
	make version
	make clean
	make
	make manual_dist
	make clean_temp
	make tar_bin
	make gpg_bin



# Rule for creating the source package distribution.
.PHONY: dist
source_dist:
	@echo -e "\n"
	@echo -e "############################################"
	@echo -e "# Creating the source distribution package #"
	@echo -e "############################################\n\n"
	make version
	make manual_dist
	make clean
	make tar_src
	make gpg_src



# Rule for version checking.
.PHONY: version
version:
	@echo -e "\n"
	@echo -e "#######################################"
	@echo -e "# Checking the program version number #"
	@echo -e "#######################################\n\n"
	@echo -e "Version number: " $(version)
	@if [ $(version) = "repository checkout" ]; then make error_version; fi;



# Rules for creating the tar files.

.PHONY: tar_bin
tar_bin:
	@echo -e "\n\n\n"
	@echo -e "#######################"
	@echo -e "# Packaging the files #"
	@echo -e "#######################\n\n"
	cd ..; tar jcv --exclude .svn -f $(TAR_BIN_FILE) relax/

.PHONY: tar_src
tar_src:
	@echo -e "\n\n\n"
	@echo -e "#######################"
	@echo -e "# Packaging the files #"
	@echo -e "#######################\n\n"
	cd ..; tar jcv --exclude .svn -f $(TAR_SRC_FILE) relax/



# Rules for creating the GPG signature of the file.

.PHONY: gpg_bin
gpg_bin:
	@echo -e "\n\n\n"
	@echo -e "############################"
	@echo -e "# GPG signing the tar file #"
	@echo -e "############################\n\n"
	gpg --detach-sign --default-key relax ../$(TAR_BIN_FILE)

gpg_src:
	@echo -e "\n\n\n"
	@echo -e "############################"
	@echo -e "# GPG signing the tar file #"
	@echo -e "############################\n\n"
	gpg --detach-sign --default-key relax ../$(TAR_SRC_FILE)



# Rule for raising the version number error.
error_version:
	$(error "The program version number has not been set")



# Clean up rules.

.PHONY: clean
clean:
	make clean_temp
	rm -f *.so */*.so */*/*.so */*/*/*.so

.PHONY: clean_temp
clean_temp:
	rm -f *.pyc */*.pyc */*/*.pyc */*/*/*.pyc
	rm -f *.bak */*.bak */*/*.bak */*/*/*.bak
	rm -f *.o */*.o */*/*.o */*/*/*.o
	rm -f *.os */*.os */*/*.os */*/*/*.os
	@cd docs/latex; make clean
