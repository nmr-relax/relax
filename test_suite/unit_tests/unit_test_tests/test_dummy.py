#!/usr/bin/env python

import unittest

class Test_dummy(unittest.TestCase):
    # failure for testing 
    def test_dummy(self):
        assert(False)
    
    def test_dummy2(self):
        assert(True)

if __name__ == '__main__':
    unittest.main()
