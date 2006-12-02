#!/usr/bin/env python

import unittest
from float  import *
from copy import copy

FLOAT_EPSILON=float(4.94065645841247e-324) # replace a a later date
FLOAT_NORMAL = float(1e6)
ZERO = float(+0.0)
NEG_ZERO = -ZERO
NEG_FLOAT_EPSILON = -FLOAT_EPSILON
NEG_FLOAT_NORMAL =  -FLOAT_NORMAL

def makeDictById(elements):
    result ={}
    for element in elements:
        result[id(element)]=element
    
    return result

def winnowDictToListById(dict,elements):
    resultDict = copy(dict)
    
    for element in elements:
        del(resultDict[id(element)])
        
    return resultDict.values()

class Test_float(unittest.TestCase):
    
    tests = makeDictById([pos_inf, neg_inf, FLOAT_NORMAL, 
                          NEG_FLOAT_NORMAL, FLOAT_EPSILON, 
                          NEG_FLOAT_EPSILON, nan, ZERO, NEG_ZERO])
    
   
    def test_getFloatClass(self):
        
        tests = ( CLASS_POS_INF, pos_inf,
                  CLASS_NEG_INF, neg_inf,
                  CLASS_POS_NORMAL, FLOAT_NORMAL,
                  CLASS_NEG_NORMAL, -FLOAT_NORMAL,
                  CLASS_POS_DENORMAL,  FLOAT_EPSILON,
                  CLASS_NEG_DENORMAL,  -FLOAT_EPSILON,
                  CLASS_QUIET_NAN,     nan,
                  # WE DON'T USE SIGNAL NANS CLASS_SIGNAL_NAN,
                  CLASS_POS_ZERO,    ZERO,
                  CLASS_NEG_ZERO,    -ZERO)

        i=iter(tests)
        for (fpClass, value) in zip(i,i):
            self.assertEqual(fpClass, getFloatClass(value))
            
    def test_isZero(self):
        positives = (ZERO,NEG_ZERO)
        negatives= winnowDictToListById(self.tests,positives)
            
        self.doTestSets(isZero,positives=positives, negatives=negatives)

    
    def test_isPositive(self):
        negatives = (neg_inf, NEG_FLOAT_NORMAL,NEG_FLOAT_EPSILON, NEG_ZERO)
        positives= winnowDictToListById(self.tests,negatives)
        
        self.doTestSets(isPositive,positives=positives, negatives=negatives)
    
    #todo add reporting of failed number class...
    def doTestSets(self,function,positives=[],negatives=[]):
        for positive in positives:
            self.assertEqual(function(positive),True)
            
        for negative in negatives:
            self.assertEqual(function(negative),False)
        
        
        
    
if __name__ == '__main__':
    unittest.main()
