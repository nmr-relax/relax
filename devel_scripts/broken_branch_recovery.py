# Script to help with the manual merger of broken branches (when svnmerge.py no longer works).

from os import system


# Create the log file (must be in the checked out copy of the branch.
system("svn log --stop-on-copy  > svn_log")

# Read the log file.
file = open('svn_log')
lines = file.readlines()
file.close()

# Init.
revisions = []

# Loop over the lines, extracting all revision numbers which were not created by svnmerge.
index = 0
while 1:
    # All done.
    if index == len(lines) - 1:
        break

    # The start of a commit.
    if lines[index][:10] == '----------': 
        # Get the revision as an integer, if not from svnmerge.
        if lines[index+3][:15] != 'Merged revision':
            rev = lines[index+1].split()[0]
            revisions.append(int(rev[1:]))

    # Move to the next line.
    index += 1

# Reverse the order.
revisions.reverse()

# List of revisions to avoid (for example merge tracking commits).
block_list = [15013, 15014, 16829, 16830]

# Create and print out the merge command.
for i in range(len(revisions)):
    if revisions[i] in block_list:
        continue
    cmd = "svn merge -r%i:%i svn+ssh://bugman@svn.gna.org/svn/relax/branches/frame_order_testing ." % (revisions[i]-1, revisions[i])
    print(cmd)
