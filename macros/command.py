import os


def ls():
	"Function which executes the Unix command 'ls -alh'"

	stat = os.system('ls -alh')


def system(command):
	"Function which executes the user supplied shell command."

	if not type(command) == str:
		print "The argument 'command' must be a string."
		return
	stat = os.system(command)
