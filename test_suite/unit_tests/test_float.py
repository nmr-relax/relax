#!/usr/bin/python

import unittest
from float  import *
FLOAT_EPSILON=float(4.94065645841247e-324) # replace a a later date

class Test_float(unittest.TestCase):
    def test_GetFloatClass(self):
        tests = ( CLASS_POS_INF, pos_inf,
                  CLASS_NEG_INF, neg_inf,
                  CLASS_POS_NORMAL, float(1e6),
                  CLASS_NEG_NORMAL, -float(1e6),
                  CLASS_POS_DENORMAL,  FLOAT_EPSILON,
                  CLASS_NEG_DENORMAL,  -FLOAT_EPSILON,
                  CLASS_QUIET_NAN,     nan,
                  # WE DON'T USE SIGNAL NANS CLASS_SIGNAL_NAN,
                  CLASS_POS_ZERO,    float(0),
                  CLASS_NEG_ZERO,    -float(0))

        i=iter(tests)
        for (fpClass, value) in zip(i,i):
            self.assertEqual(fpClass, getFloatClass(value))
        
    
if __name__ == '__main__':
    unittest.main()