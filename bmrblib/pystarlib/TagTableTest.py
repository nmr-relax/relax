from unittest import TestCase
from TagTable import TagTable
import __init__
#from TagTable import *
#from SaveFrame import *
import unittest


class AllChecks(TestCase):
    def testcheck_integrity(self):
        """TagTable"""
        __init__.verbosity = 2
    ##    text = """_A a _B "b'" """; free = 1
        text = """_A a b c d e"""; free = None
        tt = TagTable(  free      = free,
                        tagnames  = [],
                        tagvalues = [],
                        verbosity = __init__.verbosity)
        pos = tt.parse( text = text, pos = 0)
        self.assertEqual(pos, len(text))
        
        tt.tagvalues[0][0] = "A"
        tt.tagvalues[0][1] = "B\nC\n"
        tt.tagvalues[0][2] = "H1'"
        tt.tagvalues[0][3] = "H1'H2\""
        tt.tagvalues[0].append( 'H2"' )
        tt.tagvalues[0].append( "_a" ) # invalid without quotes.
        
#        print tt
        exp = """   loop_
      _A

A

;
B
C
;
 
"H1'" 

;
H1'H2"
;
 
e
'H2"' 
"_a" 

   stop_
"""        
#        print exp
#        print tt.star_text()
        self.assertEqual(exp, tt.star_text())
    

if __name__ == "__main__":
    unittest.main()
