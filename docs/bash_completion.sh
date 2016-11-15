###############################################################################
#                                                                             #
# Copyright (C) 2016 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Bash completion support for relax.
#
# To use this script, copy it to /etc/bash_completion.d/relax.

_relax() {
    # Define the variables.
    local cur prev dir py_scripts opts

    # Initialise the COMPREPLY array.
    COMPREPLY=()

    # Set the current and previous comp words.
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Handle options.
    if [[ ${cur} == -* ]] ; then
        # The help options.
        opts="--help"

        # UI options.
        opts="${opts} --prompt --gui --info --version --licence --test"

        # Multi-processor options.
        opts="${opts} --multi --processors"

        # IO redirection options.
        opts="${opts} --log --tee"

        # Test suite options.
        opts="${opts} --test-suite --system-tests --unit-tests --gui-tests --verification-tests --time --no-skip"

        # Debugging options.
        opts="${opts} --debug --error-state --traceback --escalate --numpy-raise"

        # Set COMPREPLY.
        COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )

        # Success.
        return 0
    fi

    # Multi-processor option values.
    case "${prev}" in
        --multi)
            COMPREPLY=( $(compgen -W "mpi4py" -- ${cur}) )
            return 0
            ;;
        --processors)
            COMPREPLY=( $(compgen -W "$(seq 2 257)" -- ${cur}) )
            return 0
            ;;
        *)
        ;;
    esac

    # Handle relax scripts which must end in *.py.
    COMPREPLY=( $(compgen -f -X '!*.py' -- ${cur}) )

    # Defer to _filedir for directory completion.
    if [[ -z "${CDPATH:-}" || "$cur" == ?(.)?(.)/* ]]; then
        _filedir -d
        return 0
    fi

    # Append a trailing '/' for unique directory names, if missing.
    if [[ ${#COMPREPLY[@]} -eq 1 ]]; then
        i=${COMPREPLY[0]}
        if [[ "$i" == "${cur}" && $i != "*/" ]]; then
            COMPREPLY[0]="${i}/"
        fi
        return 0
    fi

    return 0
}

# Set up the completion for relax, avoiding trailing spaces for better subdirectory completion.
complete -o nospace -F _relax relax
