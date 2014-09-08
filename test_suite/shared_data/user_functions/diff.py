# Python module imports.
from re import search
from subprocess import PIPE, Popen


# The versions to compare.
versions = [
    '1.3.16',
    '2.0.0',
    '2.1.0',
    '2.1.1',
    '2.1.2',
    '2.2.0',
    '2.2.1',
    '2.2.2',
    '2.2.3',
    '2.2.4',
    '2.2.5',
    '3.0.0',
    '3.0.1',
    '3.0.2',
    '3.1.0',
    '3.1.1',
    '3.1.2',
    '3.1.3',
    '3.1.4',
    '3.1.5',
    '3.1.6',
    '3.1.7',
    '3.2.0',
    '3.2.1',
    '3.2.2',
    '3.2.3',
    '3.3.0'
]

# Loop over all versions.
for i in range(len(versions)-1):
    text = "Comparing relax %s to %s" % (versions[i], versions[i+1])
    print("\n\n%s" % text)
    print("=" * len(text) + "\n")

    # The shell command.
    cmd = 'diff -u uf_list_%s uf_list_%s' % (versions[i], versions[i+1])

    # Execute the command.
    pipe = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=False)
    pipe.stdin.close()

    # The results.
    lines = pipe.stdout.readlines()

    # Loop over the lines.
    removed = []
    added = []
    for line in lines:
        # Only look at differences.
        if not line[0] in ['-', '+']:
            continue

        # Skip the file names.
        if search('uf_list_', line):
            continue

        # Skip "user_functions.initialise".
        if search('user_functions.initialise', line):
            continue

        # Skip empty lines.
        if len(line) <= 2:
            continue

        # Store the line.
        if line[0] == '-':
            removed.append(line[:-1])
        else:
            added.append(line[:-1])

    # Printout the removed, then added functions.
    for name in removed:
        print(name)
    for name in added:
        print(name)


