import os


class lh:
	def __repr__(self):
		"Function which executes the Unix command 'ls -alh'"

		stat = os.system('ls -alh')
		return "ls -alh"


class ll:
	def __repr__(self):
		"Function which executes the Unix command 'ls -l'"

		stat = os.system('ls -l')
		return "ls -l"


class ls:
	def __repr__(self):
		"Function which executes the Unix command 'ls'"

		stat = os.system('ls')
		return "ls"


def system(command):
	"Function which executes the user supplied shell command."

	if not type(command) == str:
		print "The argument 'command' must be a string."
		return
	stat = os.system(command)
