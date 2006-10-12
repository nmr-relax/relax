###############################################################################
#                                                                             #
# Copyright (C) 2006  Gary S Thompson (see https://gna.org/users for contact  #
#                                      details)                               #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

''' ieeefloat a set of functions for dealing with ieee-754 float objects

    On most platforms Python uses ieee-754 double objects of length 64 bits to 
    represent floats (some architectures such as older crays and vaxes don't). 
    Thus an ieee-754 double is the implementation of a python float object on
    most platforms.
    
    ieee-74 uses special bit patterns to represent the following states or classes 
    of ieee floating point numbers (ieee-class)
      +-nan  - not a number (e.g. 0.0/0.0)
      inf    - positive or negative infinity (1.0/0.0)
      +-zero - zero maybe positive or negative under ieee-754
        
    this module provides functions for working with python floats and their 
    special values, if they contain ieee-754 formatted values. Specifically
     - pack and unpack a list of bytes representing an ieee-754 double to a python 
       float (takes care of little endian/big endian issues)
     - get the sign bit of a python float
     - check the ordering of python floats allowing for nans (nans cannot normally 
       be compared)
     - check if a value is finite (as opposed to nan or inf)
     - copy the sign of one float to another irrespective of if it's ieee-class 
     - check if a float is denormalised (and might be about to underflow)
     - check the ieee-class of a python float (nan, pos-inf, neg-inf,pos-zero, 
       neg-zero,...)
     - check that the current python float implmentations uses ieee-754 doubles
     
    It also provides constants containg specific bit patterns for nan and +-inf as 
    these values cannot be generated from strings via the constructor float(x) 
    with some compiler implementations (typically older microsoft windows compilers)
    
    As a convenience the names of functions and constants conform to those defined 
    in the draft python PEP 754 'IEEE 754 Floating Point Special Values'
    
    notes:
      1. binary data is docuemented as binary strings e.g. 0xF0 = 0b11110000
      2. the module doesn't support all the functions recommened by ieee-754, 
         the following features are missing
           a. control of exception and rounding modes
           b. scalb (y, N)
           c. logb (x)
           d. nextafter(x,y)
           e. next towards
      3. division by zero currently (python 2.5) raises excaption and the 
         resulting inf/nan cannot be propogated
      4. a second module ieeefloatcapabilities (currently incomplete) 
         provides tests of the capabilites of a floating point implementation
         on a specific python platform 
      5. development and conventions on byte order come from a little endian
         (intel) platform
      6. to reduce overheads all functions that take python float arguments do 
         _no type_ conversion thus if other numeric types are passed the functions
         will raise exceptions, (I am not sure this is the best behaviour however,
         as python functions should be polymorphic...)
      7. in most cases conversion to c code for performance reasons would be trivial
         
    ieee-754 double format:
        63 sign bit
        62-52 exponent (offset by 1023 value - field-1023
        51-0 mantissa each bit n counts as 1/2^n, running from 1/2 which is the
             most significant bit to 1/2^51, The 1/0 bit is defined by the 
             exponent field if it has any bits set if it has bits set then 
             precede the mantissa with a 1 (normalised otherwise procede it by 
             a 0 (denormalised)
        
        
    todo:
      unit test suite
      test under windows
      test under a solaris sparc box (big endian)
      add example ieee double
      check byte/nibble atributions
'''
from struct import pack,unpack
import sys


SIGNBIT = 0x80 
''' bit pattern for the sign bit in byte 8 0b00000001 of a ieee-754 double'''


EXPONENT_ALL_ONES_BYTE_1 = 0x7F      
''' value of the first byte (byte 8) in the mantisaa of a ieee-754 double that 
is all ones (0b11111110) '''

EXPONENT_ALL_ONES_BYTE_0 = 0xF << 4 
''' value of the second byte (byte 7) in the mantisaa of a ieee-754 double that 
is all ones (0b00001111) '''


MANTISSA_NIBBLE_MASK=0x0F
''' mask to select the bits from the first nibble of  byte 7 of an ieee-754
which is part of the mantissa (0b00001111)'''

EXPONENT_NIBBLE_MASK=0xF0
''' mask to select the bits from the second nibble of  byte 7 of an ieee-754
which is part of the exponent (0b11110000)'''


EXPONENT_SIGN_MASK= 0x7F   
'''' mask to select only bits from byte 8 of an ieee-754 double that are 
not part of the sign bit (0b11111110)'''

''' classes of floating point numbers'''
CLASS_POS_INF = 1
CLASS_NEG_INF = 2
CLASS_POS_NORMAL = 4
CLASS_NEG_NORMAL = 8
CLASS_POS_DENORMAL = 16
CLASS_NEG_DENORMAL = 32
CLASS_QUIET_NAN =  64
CLASS_SIGNAL_NAN = 128
CLASS_POS_ZERO =  256
CLASS_NEG_ZERO = 512

def isZero(float):
    return isMantissaAllZeros(float) and isExpAllZeros(float)  
                                            
def getFloatClass(float):
    ''' get the ieee-class (nan,inf etc) of apython float
    
        float  - python float object
        
        result - a ieee class value
        throws - an exception if float is not a python float object
    '''
    
    result = None
    if isFinite(float):
      positive = isPositive(float)
      denormalised = isDenormalised(float)
      if denormalised(float):
        if isZero():
          if positive:
            result  = CLASS_POS_ZERO
          else:
            result = CLASS_NEG_ZERO
        else:
          if positive:
            result = CLASS_POS_DENORMAL
          else:
            result = CLASS_NEG_DENORMAL
      else:
        if positive:
          result  = CLASS_POS_NORMAL
        else:
          result = CLASS_NEG_NORMAL
    else:    
      if isNaN(float):
        # we don't currently test the type of nan signalling vs quiet
        result  = CLASS_QUIET_NAN
      elif isPosInf(float):
        result  = CLASS_POS_INF
      elif isNegInf(float):
        result  = CLASS_NEG_INF

      

def packBytesAsPyFloat(bytes):
    ''' pack 8 bytes into a python float 
    
        the function is endian aware and the data should be input in little 
        endian format. Thus byte 8 contains the most significant bit of the 
        exponent and the sign bit
        
        bytes -- 8 bytes to pack into a python (ieee 754 double) float
        
        returns -- a python float
        
        throws -- an Exception if bytes contains < 8 bytes
                  type of exception not determined
    '''
     
    doubleString=pack('8B',*bytes)
    if sys.byteorder == 'big':
        doubleString = doubleString[::-1]
    return unpack('d',doubleString)[0]


NAN_BYTES = [0x00,0x00,0x00,0x00,0x00,0x00,0xF8,0x7F]
''' bytes for an arbitary ieee-754 not a number (nan) in little endian format
0b00000000 00000000 00000000 00000000 00000000 00000000 00011111 11111110 '''


INF_BYTES = [0x00,0x00,0x00,0x00,0x00,0x00,0xF0,0x7F]
''' bytes for ieee-754 positive infinity (inf) in little endian format
0b00000000 00000000 00000000 00000000 00000000 00000000 00001111 11111110 '''


nan = packBytesAsPyFloat(NAN_BYTES)
''' one of a number of possible bit patterns used to represent an ieee-754 double
as a python float. Do not use this value for comparisons of the form x==nan as it
will fail on some platforms use function isNaN instead'''


pos_inf = packBytesAsPyFloat(INF_BYTES)
''' the value of a positive  ieee-754 double infinity as a python float '''


neg_inf = -1 * pos_inf
''' the value of a negative  ieee-754 double infinity as a python float'''


def floatToBinaryString(obj):
    ''' pack a python float into a binary string.
        
        This function assumes that the python type float it represents a 
        64bit double of 8 bytes. This function reverses the resulting string if 
        the current architecture is big endian.
        
        obj -- a python float to pack
        
        returns -- a string of 8 bytes
        
        throws --  throws a TypeError if the the input object isn't a python float
                    
    '''
    if not isinstance(obj,float):
        raise TypeError('the object recieved wasn\'t a float, type was: %s' % type(obj))
    
    packed =pack('d',obj)
    if sys.byteorder == 'big':
       packed = packed[::-1]
    return packed
     
def floatAsByteArray(obj):
    ''' unpack a python float as a list of 8 bytes
        
        This function assumes that the python type float it represents a 
        64bit double of 8 bytes
        
        obj -- a python float to unpack
        
        returns -- a list of 8 bytes
        
        throws --  throws an exception if obj is not composed of 8 bytes
                    
    '''
    return list(unpack('8B',floatToBinaryString(obj)))
  

    
def getSignBit(obj):
    ''' get the sign bit from a python float
        
        obj -- a python float object
        
        returns -- the floats sign bit, this has the value 1 if the float is 
                   negative otherwise 0 (positive)
        
        throws -- throws a TypeError if the the input object isn't a python float
                   
    ''' 
    unpacked = floatAsByteArray(obj) 
    return unpacked[7]  & SIGNBIT

def isPositive(obj):
    ''' test if a a pyhton float is positive
        
        obj -- a python float object
        
        returns -- True if the float is positive otherwise False
        
        throws -- throws a TypeError if the the input object isn't a python float
                   
    ''' 
    unpacked = floatAsByteArray(obj) 
    if getSignBit(obj):
        return False
    else:
        return True
      
def isNegative(obj):
    ''' test if a a pyhton float 64 bit ieee-74 double is negative
        
        obj -- a python float object
        
        returns -- True if the float is negative
        
        throws -- tthrows a TypeError if the the input object isn't a python float
    ''' 
    return not isPositive(obj)      



def areUnordered(obj1,obj2):
    ''' test to see if two python float  are unordered
    
        float comparison is unordered if either or both of the objects is 'not a 
        number' (nan)
        
        obj1 -- a python float object
        obj2 -- a python float object
        
        throws -- throws a TypeError if the the input objects aren't a python floats
                    
    '''
    nanTest1 = isNaN(obj1)
    nanTest2 = isNaN(obj2)
    if nanTest1 or nanTest2:
        return True
    else:
        return False
    

def isFinite(obj):
    ''' test to see if a python float is finite
    
        to be finite a number mustn't be a nan or + or - inf a result of True 
        guarantees that the number is bounded by +- inf -inf < x < inf
        
        obj -- a python float object
        
        throws -- throws a TypeError if the the input object isn't a python float
                    
    '''
    result = True
    if isNaN(obj):
      result = False
    if isInf(obj):
        result =  False

    
    return result

def copySign(fromNumber,toDouble):
    ''' copy the sign bit from one python float  to another
        
        this function is class agnostic the sign bit can be copied freely between 
        ordinarys floats nans and +/-inf
        
        fromDouble --  the python float to copy the sign bit from
        toDouble --  the python float to copy the sign bit to
        
        throws -- throws a TypeError if toDouble isn't a python float or if
                  fromNumber can't be converted to a float
        
    '''
    fromNumber = float(fromNumber)
    fromIsPositive =  isPositive(fromNumber)
    toIsPositive = isPositive(toDouble)
    toBytes = floatAsByteArray(toDouble)
    if  not toIsPositive  and  fromIsPositive:
        toBytes[7] &= 0x7F
    elif toIsPositive and  not fromIsPositive:
         toBytes[7] = toBytes[7] + 128
    return packBytesAsPyFloat(toBytes)
    
    
 




  
def isDenormalised(obj):
    ''' check to see if a python float is denormalised
    
        denormalisation indicates that the number has no exponent set and all the 
        precision is in the mantissa, this is an indication that the number is 
        tending to towards underflow
    
        obj -- python float object to check
        
        result -- True if the number is denormalised
        
        throws -- throws a TypeError if toDouble isn't a python float or if
                  obj isn't a float
    '''
    if not isExpAllZeros(obj):
        return False
    manBytes = getMantissaBytes(obj)
    for byte in manBytes:
        if byte > 0:
            return True
    return False






def getMantissaBytes(obj):
    ''' get the 7 bytes that makeup the mantissa of float
    
        the mantissa is returned as the 7 bytes in the mantissa in little endian order
        in the 7th byte the 2nd nibble of the byte is masked off as it contains 
        part of the exponent. The second nibble of the 7th byte is therefore always 
        has the value 0x0
        
        obj -- float object to extract the mantissa from
        
        returns -- a list of 7 bytes in little endian order
        
        throws -- throws a TypeError if obj isn't a python float 
        
    '''
    unpacked = floatToBinaryString(obj)
    bytes = list(unpack('8B',unpacked))
    bytes[6] = bytes[6] & MANTISSA_NIBBLE_MASK
    bytes=bytes[:7]
    return bytes

def getExponentBytes(obj):
    ''' get the 2 bytes that makeup the exponent of a float 
    
        the exponent is returned as the 2 bytes in the exponent in little endian order
        in the 2nd byte the last bit is masked off as this is the sign bit. Ttherefore 
        all values have the last bit set to zero. In the first byte the first nibble of
        the byte is also masked off as it contains part of the mantissa and thus
        always has the value 0x0. 
        
        obj -- float object to extract the exponent from
        
        returns -- a list of 2 bytes in little endian order
        
        throws -- throws a TypeError if obj isn't a python float        
    '''
    
    unpacked = floatToBinaryString(obj)
    bytes = list(unpack('8B',unpacked))
    bytes[6] = bytes[6] & EXPONENT_NIBBLE_MASK
    bytes[7] = bytes[7] & EXPONENT_SIGN_MASK
    bytes=bytes[6:]
    
    return bytes 




def isExpAllZeros(obj):
    ''' check if the bits of the exponent of a float is zero
    
        obj -- float object to check exponent for zero value
        
        returns -- True if the exponent is zero
        
        throws -- throws a TypeError if obj isn't a python float 
    '''
    expBytes = getExponentBytes(obj)
    if expBytes[0] > 0 or  expBytes[1] > 0:
        return False
    return True

def isMantissaAllZeros(obj):
    ''' check if the bits of the mantissa of a float is zero

    obj -- float object to check mantissa for zero value
    
    returns -- True if the mantissa is zero
    
    throws -- throws a TypeError if obj isn't a python float 
    '''
    mantissaBytes = getMantissaBytes(obj)
    result  =  True
    for byte in mantissaBytes:
        if byte != 0:
            result = False 
            break
    return result
  
def isExpAllOnes(obj):
    ''' check if the bits of the exponent of a floatis all 1 bits
    
        obj -- float object to check exponent for 1 bits
        
        returns -- True if all the bits in the exponent are one
        
        throws -- throws a TypeError if obj isn't a python float 
    '''    
    expBytes = getExponentBytes(obj)
    if expBytes[0] == EXPONENT_ALL_ONES_BYTE_0 and  expBytes[1] == EXPONENT_ALL_ONES_BYTE_1:
        return True
    return False    

def isNaN(obj):
    ''' check to see if a python float is an ieee-754 double not a number (nan)
        
        obj -- float object to check for not a number
        
        returns -- True if object is not a number
        
        throws -- throws a TypeError if obj isn't a python float     
    '''

    if not isExpAllOnes(obj):
        return False
    manBytes = getMantissaBytes(obj)
    manNan = False
    for byte in manBytes[:6]:
        if byte > 0:
            manNan = True
    if (manBytes[6] & MANTISSA_NIBBLE_MASK) > 0:
        manNan = True
    return manNan

def isInf(obj): 
    ''' check to see if a python float is an infinity 
        
        the check returns true for either positive or negative infinities
        
        obj -- float object to check for infinity
        
        returns -- True if object is an infinity 
        
        throws -- throws a TypeError if obj isn't a python float     
    '''    
    if not isExpAllOnes(obj):
        return False
    manBytes = getMantissaBytes(obj)
    for i,byte in enumerate(manBytes):
        if byte > 0:
            return False
    return True
        
def isPosInf(obj):
    ''' check to see if a python float is positive infinity 
                
        obj -- float object to check for positive infinity
        
        returns -- True if object is a positive infinity 
        
        throws -- throws a TypeError if obj isn't a python float     
    '''        
    return isInf(obj) and isPositive(obj)

def isNegInf(obj):
    ''' check to see if a python float is negative infinity 
        
        
        obj -- float object to check for negative infinity
        
        returns -- True if object is a negative infinity 
        
        throws -- throws a TypeError if obj isn't a python float     
    '''
        
    return isInf(obj) and not isPositive(obj)   
  

    



