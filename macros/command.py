from os import listdir


def ls():
	print "\nExecuting macro ls."
	print `listdir('.')`
	return
