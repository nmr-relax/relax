#!/usr/bin/env python


class Uni_processor(object):
	def __init__(self,relax_instance):
		self.relax_instance= relax_instance

	def run(self):
		self.relax_instance.run()


if __name__ == '__main__':
    test =Uni_processor(None)
    print test
