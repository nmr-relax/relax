###############################################################################
#                                                                             #
# Copyright (C) 2006  Gary S Thompson (see https://gna.org/users for contact  #
#                                      details)                               #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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

# Module docstring.
"""ieeefloat a set of functions for dealing with IEEE-754 float objects.

On most platforms Python uses IEEE-754 double objects of length 64 bits to represent floats (some
architectures such as older Crays and Vaxes don't).  Thus an IEEE-754 double is the implementation
of a python float object on most platforms.

IEEE-74 uses special bit patterns to represent the following states or classes of IEEE floating
point numbers (IEEE-class):
    - +/- NaN:    Not a number (e.g. 0.0/0.0).
    - inf:        Positive or negative infinity (1.0/0.0).
    - +/- zero:   Zero maybe positive or negative under IEEE-754.

This module provides functions for working with python floats and their special values, if they
contain IEEE-754 formatted values.  Specifically:
    - Pack and unpack a list of bytes representing an IEEE-754 double to a python float (takes care
      of little endian/big endian issues).
    - Get the sign bit of a python float.
    - Check the ordering of python floats allowing for NaNs (NaNs cannot normally be compared).
    - Check if a value is finite (as opposed to NaN or inf).
    - Copy the sign of one float to another irrespective of if it's IEEE-class.
    - Check if a float is denormalised (and might be about to underflow).
    - Check the IEEE-class of a python float (NaN, pos-inf, neg-inf, pos-zero, neg-zero, ...).
    - Check that the current python float implementations uses IEEE-754 doubles.

It also provides constants containg specific bit patterns for NaN and +-inf as these values cannot
be generated from strings via the constructor float(x) with some compiler implementations (typically
older Microsoft Windows compilers).

As a convenience the names of functions and constants conform to those defined in the draft python
PEP 754 'IEEE 754 Floating Point Special Values'.

Notes:
    1.  Binary data is documented as binary strings e.g. 0xF0 = 0b11110000.
    2.  The module doesn't support all the functions recommended by IEEE-754, the following features
        are missing:
            - Control of exception and rounding modes.
            - scalb(y, N).
            - logb(x).
            - nextafter(x,y).
            - Next towards.
    3.  Division by zero currently (python 2.5) raises exception and the resulting inf/NaN cannot be
        propogated.
    4.  A second module ieeefloatcapabilities (currently incomplete) provides tests of the
        capabilities of a floating point implementation on a specific python platform.
    5.  Development and conventions on byte order come from a little endian (Intel) platform.
    6.  To reduce overheads all functions that take python float arguments do _no type_ conversion
        thus if other numeric types are passed the functions will raise exceptions, (I am not sure
        this is the best behaviour however, as python functions should be polymorphic...).
    7.  In most cases conversion to C code for performance reasons would be trivial.

IEEE-754 double format:
    - 63 sign bit.
    - 62-52 exponent (offset by 1023 value - field-1023).
    - 51-0 mantissa each bit n counts as 1/2^n, running from 1/2 which is the most significant bit
      to 1/2^51, The 1/0 bit is defined by the exponent field if it has any bits set if it has bits
      set then precede the mantissa with a 1 (normalised otherwise precede it by a 0 (denormalised).


Todo:
    - Unit test suite.
    - Test under Windows.
    - Test under a Solaris Sparc box (big endian).
    - Add example IEEE double.
    - Check byte/nibble attributions.
"""
from struct import pack, unpack
import sys


SIGNBIT = 0x80
"""Bit pattern for the sign bit in byte 8 0b00000001 of a IEEE-754 double."""


EXPONENT_ALL_ONES_BYTE_1 = 0x7F
"""Value of the first byte (byte 8) in the mantissa of a IEEE-754 double that is all ones
(0b11111110)."""

EXPONENT_ALL_ONES_BYTE_0 = 0xF << 4
"""Value of the second byte (byte 7) in the mantissa of a IEEE-754 double that is all ones
(0b00001111)."""


MANTISSA_NIBBLE_MASK=0x0F
"""Mask to select the bits from the first nibble of  byte 7 of an IEEE-754 which is part of the
mantissa (0b00001111)."""

EXPONENT_NIBBLE_MASK=0xF0
"""Mask to select the bits from the second nibble of  byte 7 of an IEEE-754 which is part of the
exponent (0b11110000)."""


EXPONENT_SIGN_MASK= 0x7F
"""Mask to select only bits from byte 8 of an IEEE-754 double that are not part of the sign bit
(0b11111110)."""

"""Classes of floating point numbers."""
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
    """Get the IEEE-class (NaN, inf etc) of a python float.

    @param float:       Python float object.
    @type float:        float
    @return:            An IEEE class value.
    @rtype:             int
    @raise TypeError:   If float is not a python float object.
    """

    result = None

    # check finite
    if isFinite(float):
        # check and store is positive
        positive = isPositive(float)
        if isZero(float):
            if positive:
                result = CLASS_POS_ZERO
            else:
                result = CLASS_NEG_ZERO
        elif isDenormalised(float):
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
            # we don't currently test the type of NaN signalling vs quiet
            # so we always assume a quiet NaN
            result  = CLASS_QUIET_NAN
        elif isPosInf(float):
            result  = CLASS_POS_INF
        elif isNegInf(float):
            result  = CLASS_NEG_INF
    return result


def packBytesAsPyFloat(bytes):
    """Pack 8 bytes into a python float.

    The function is endian aware and the data should be input in little endian format. Thus byte 8
    contains the most significant bit of the exponent and the sign bit.

    @param bytes:       8 bytes to pack into a python (IEEE 754 double) float.
    @type bytes:        float
    @return:            A python float
    @rtype:             float
    @raise TypeError:   If bytes contains < 8 bytes type of exception not determined.
    """

    # pack bytes into binary string
    doubleString=pack('8B',*bytes)

    #change byte order to little endian by reversing string
    if sys.byteorder == 'big':
        doubleString = doubleString[::-1]

    # unpack binary string to a python float
    return unpack('d', doubleString)[0]


NAN_BYTES = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF8, 0x7F]
"""Bytes for an arbitary IEEE-754 not a number (NaN) in little endian format
0b00000000 00000000 00000000 00000000 00000000 00000000 00011111 11111110."""


INF_BYTES = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xF0, 0x7F]
"""Bytes for IEEE-754 positive infinity (inf) in little endian format
0b00000000 00000000 00000000 00000000 00000000 00000000 00001111 11111110."""


nan = packBytesAsPyFloat(NAN_BYTES)
"""One of a number of possible bit patterns used to represent an IEEE-754 double as a python float.
Do not use this value for comparisons of the form x==NaN as it will fail on some platforms use
function isNaN instead."""


pos_inf = packBytesAsPyFloat(INF_BYTES)
"""The value of a positive IEEE-754 double infinity as a python float."""


neg_inf = -1 * pos_inf
"""The value of a negative IEEE-754 double infinity as a python float."""


def floatToBinaryString(obj):
    """Pack a python float into a binary string.

    This function assumes that the python type float it represents a 64bit double of 8 bytes. This
    function reverses the resulting string if the current architecture is big endian.

    @param obj:         A python float to pack.
    @type obj:          float
    @return:            A string of 8 bytes.
    @rtype:             str
    @raise TypeError:   If the input object isn't a python float.
    """

    if not isinstance(obj, float):
        raise TypeError('the object recieved wasn\'t a float, type was: %s' % type(obj))

    # pack float into binary string
    packed =pack('d', obj)

    #change byte order to little endian by reversing string
    if sys.byteorder == 'big':
        packed = packed[::-1]

    return packed


def floatAsByteArray(obj):
    """Unpack a python float as a list of 8 bytes.

    This function assumes that the python type float it represents a 64bit double of 8 bytes.

    @param obj:         A python float to unpack.
    @type obj:          float
    @return:            A list of 7 bytes.
    @rtype:             list of str
    @raise TypeError:   If obj is not composed of 8 bytes.
    """

    # unpack bytes to a binary string (takes care of byte order)
    binaryString = floatToBinaryString(obj)

    # convert the binary string to an array of 8 bytes
    bytes = unpack('8B', binaryString)

    #convert bytes to a list for ease of editing
    return list(bytes)


def getSignBit(obj):
    """Get the sign bit from a python float.

    @param obj:         A python float object.
    @type obj:          float
    @return:            The float's sign bit, this has the value 1 if the float is negative
                        otherwise 0 (positive).
    @rtype:             bit
    @raise TypeError:   If the input object isn't a python float.
    """

    # unpack float to bytes
    unpacked = floatAsByteArray(obj)

    # grab last byte and check if sign bit is set
    return unpacked[7]  & SIGNBIT


def isPositive(obj):
    """Test if a python float is positive.

    @param obj:         A python float object.
    @type obj:          float
    @return:            True if the float is positive otherwise False.
    @rtype:             bool
    @raise TypeError:   If the input object isn't a python float.
    """

    if getSignBit(obj):
        return False
    else:
        return True


def isNegative(obj):
    """Test if a python float 64 bit IEEE-74 double is negative.

    @param obj:         A python float object.
    @type obj:          float
    @return:            True if the float is negative.
    @rtype:             bool
    @raise TypeError:   If the input object isn't a python float.
    """

    return not isPositive(obj)


def areUnordered(obj1, obj2):
    """Test to see if two python float are unordered.

    Float comparison is unordered if either or both of the objects is 'not a number' (NaN).

    @param obj1:        A python float object
    @type obj1:         float
    @param obj2:        A python float object
    @type obj2:         float
    @return:            True if one of the args is a NaN.
    @rtype:             bool
    @raise TypeError:   If the input objects aren't python floats.
    """

    # check to see if objects are NaNs
    nanTest1 = isNaN(obj1)
    nanTest2 = isNaN(obj2)

    # if either object is a NaN we are unordered
    if nanTest1 or nanTest2:
        return True
    else:
        return False


def isFinite(obj):
    """Test to see if a python float is finite.

    To be finite a number mustn't be a NaN or +/- inf.  A result of True guarantees that the number
    is bounded by +/- inf, -inf < x < inf.

    @param obj:         A python float object.
    @type obj:          float
    @return:            True if the float is finite.
    @rtype:             bool
    @raise TypeError:   If the input object isn't a python float.
    """

    result = True
    if isNaN(obj):
        result = False
    if isInf(obj):
        result =  False


    return result


def copySign(fromNumber, toDouble):
    """Copy the sign bit from one python float to another.

    This function is class agnostic the sign bit can be copied freely between ordinary floats, NaNs
    and +/- inf.

    @param fromNumber:  The python float to copy the sign bit from.
    @type fromNumber:   float
    @param toDouble:    The python float to copy the sign bit to.
    @type toDouble:     float
    @raise TypeError:   If toDouble isn't a python float or if fromNumber can't be converted to a
                        float.
    """

    #convert first number to a float so as to use facilities
    fromNumber = float(fromNumber)

    # check signs of numbers
    fromIsPositive =  isPositive(fromNumber)
    toIsPositive = isPositive(toDouble)

    # convert the float to an array of 8 bytes
    toBytes = floatAsByteArray(toDouble)

    if  not toIsPositive  and  fromIsPositive:
        # unset the sign bit of the number
        toBytes[7] &= EXPONENT_SIGN_MASK

    elif toIsPositive and  not fromIsPositive:
        # set the sign bit
        toBytes[7] = toBytes[7] + 0x80

    #repack bytes to float
    return packBytesAsPyFloat(toBytes)


def isDenormalised(obj):
    """Check to see if a python float is denormalised.

    Denormalisation indicates that the number has no exponent set and all the precision is in the
    mantissa, this is an indication that the number is tending to towards underflow.

    @param obj:         Python float object to check.
    @type obj:          float
    @return:            True if the number is denormalised.
    @rtype:             bool
    @raise TypeError:   If toDouble isn't a python float or if obj isn't a float.
    """

    result = True
    # check to see if the exponent is all zeros (a denorm doesn't have a
    # finite exponent) Note we ignore the sign of the float
    if not isExpAllZeros(obj):
        result = False

        # check to see if this is zero (which is in some ways a special
        # class of denorm... but isn't counted in this case)
        # if it isn't zero it must be a 'general' denorm
        if isZero(obj):
            result = False

    return result


def getMantissaBytes(obj):
    """Get the 7 bytes that makeup the mantissa of float.

    The mantissa is returned as the 7 bytes in the mantissa in little endian order in the 7th byte
    the 2nd nibble of the byte is masked off as it contains part of the exponent. The second nibble
    of the 7th byte is therefore always has the value 0x0.

    @param obj:         Float object to extract the mantissa from.
    @type obj:          float
    @return:            A list of 7 bytes in little endian order.
    @rtype:             list of 7 bytes
    @raise TypeError:   If obj isn't a python float.
    """

    # unpack float to bytes
    bytes = floatAsByteArray(obj)

    # mask out overlap from exponent
    bytes[6] = bytes[6] & MANTISSA_NIBBLE_MASK

    # remove the exponent bytes that can be removed
    return bytes[:7]


def getExponentBytes(obj):
    """Get the 2 bytes that makeup the exponent of a float.

    The exponent is returned as the 2 bytes in the exponent in little endian order in the 2nd byte
    the last bit is masked off as this is the sign bit. Therefore all values have the last bit set
    to zero. In the first byte the first nibble of the byte is also masked off as it contains part
    of the mantissa and thus always has the value 0x0.

    @param obj:         Float object to extract the exponent from.
    @type obj:          float
    @return:            A list of 2 bytes in little endian order.
    @rtype:             list of 2 bytes
    @raise TypeError:   If obj isn't a python float.
    """

    # unpack float to bytes
    bytes = floatAsByteArray(obj)

    # mask out the ovberlap with the mantissa
    bytes[6] = bytes[6] & EXPONENT_NIBBLE_MASK

    # mask out the sign bit
    bytes[7] = bytes[7] & EXPONENT_SIGN_MASK

    # remove the mantissa bytes that can be removed
    return bytes[6:]


def isExpAllZeros(obj):
    """Check if the bits of the exponent of a float is zero.

    @param obj:         Float object to check exponent for zero value.
    @type obj:          float
    @return:            True if the exponent is zero.
    @rtype:             bool
    @raise TypeError:   If obj isn't a python float.
    """

    result = True

    # get the exponent as a byte array porperly masked
    expBytes = getExponentBytes(obj)

    # check to see if any of the bytes in the exponent are not zero
    if expBytes[0] > 0 or  expBytes[1] > 0:
        result = False

    return result


def isMantissaAllZeros(obj):
    """Check if the bits of the mantissa of a float is zero.

    @param obj:         Float object to check mantissa for zero value.
    @type obj:          float
    @return:            True if the mantissa is zero.
    @rtype:             bool
    @raise TypeError:   If obj isn't a python float.
    """

    result = True

    # get the mantissa as a byte array properly masked
    mantissaBytes = getMantissaBytes(obj)

    # check if any of the mantissa bytes are greater than zero
    for byte in mantissaBytes:
        if byte != 0:
            result = False
            break

    return result


def isExpAllOnes(obj):
    """Check if the bits of the exponent of a float is all 1 bits.

    @param obj:         Float object to check exponent for 1 bits.
    @type obj:          float
    @return:            True if all the bits in the exponent are one.
    @rtype:             bool
    @raise TypeError:   If obj isn't a python float.
    """

    result = False

    # get the exponent as a byte array properly masked
    expBytes = getExponentBytes(obj)

    # check against masks to see if all the correct bits are set
    if expBytes[0] == EXPONENT_ALL_ONES_BYTE_0 and  expBytes[1] == EXPONENT_ALL_ONES_BYTE_1:
        result  =  True

    return result


def isNaN(obj):
    """Check to see if a python float is an IEEE-754 double not a number (NaN).

    @param obj:         Float object to check for not a number.
    @type obj:          float
    @return:            True if object is not a number.
    @rtype:             bool
    @raise TypeError:   If obj isn't a python float.
    """

    # bad result for code checking
    result = None

    # check to see if exponent is all ones (excluding sign bit)
    # if exponent is not all ones this can't be a NaN
    if not isExpAllOnes(obj):
        result =  False
    else:
        # get the mantissa as a byte array properly masked
        manBytes = getMantissaBytes(obj)

        # check if any of the unmasked mantissa bytes are not zero
        # to be a NaN the mantissa must be non zero
        for byte in manBytes:
            if byte > 0:
                result = True
                break
        # todo NOT NEEDED, UNITTEST!!!!
        # check to see if the mantissa nibble that overlaps with the
        #if (manBytes[6] & MANTISSA_NIBBLE_MASK) > 0:
        #    result = True
    return result


def isInf(obj):
    """Check to see if a python float is an infinity.

    The check returns true for either positive or negative infinities.

    @param obj:         Float object to check for infinity.
    @type obj:          float
    @return:            True if object is an infinity.
    @rtype:             bool
    @raise TypeError:   If obj isn't a python float.
    """

    # bad result for code checking
    result = None

    # check to see if exponent is all ones (excluding sign bit)
    # if exponent is not all ones this can't be a Inf
    if not isExpAllOnes(obj):
        result =  False
    else:
        # get the mantissa as a byte array properly masked
        manBytes = getMantissaBytes(obj)

        for byte in manBytes:
            #check if any of the unmasked mantissa bytes are zero
            # to be a NaN the mantissa must be zero
            if byte > 0:
                result = False
                break
            result = True

    return result


def isPosInf(obj):
    """Check to see if a python float is positive infinity.

    @param obj:         Float object to check for positive infinity.
    @type obj:          float
    @return:            True if object is a positive infinity.
    @rtype:             bool
    @raise TypeError:   If obj isn't a python float.
    """

    return isInf(obj) and isPositive(obj)


def isNegInf(obj):
    """Check to see if a python float is negative infinity.

    @param obj:         Float object to check for negative infinity.
    @type obj:          float
    @return:            True if object is a negative infinity.
    @rtype:             bool
    @raise TypeError:   If obj isn't a python float.
    """

    return isInf(obj) and not isPositive(obj)


def bitpatternToFloat(string, endian='big'):
    """Convert a 64 bit IEEE-754 ascii bit pattern into a 64 bit Python float.

    @param string:      The ascii bit pattern repesenting the IEEE-754 float.
    @type string:       str
    @param endian:      The endianness of the bit pattern (can be 'big' or 'little').
    @type endian:       str
    @return:            The 64 bit float corresponding to the IEEE-754 bit pattern.
    @returntype:        float
    @raise TypeError:   If 'string' is not a string, the length of the 'string' is not 64, or if
                        'string' does not consist solely of the characters '0' and '1'.
    """

    # Test that the bit pattern is a string.
    if not isinstance(string, str):
        raise TypeError("The string argument '%s' is not a string." % string)

    # Test the length of the bit pattern.
    if len(string) != 64:
        raise TypeError("The string '%s' is not 64 characters long." % string)

    # Test that the string consists solely of zeros and ones.
    for char in string:
        if char not in ['0', '1']:
            raise TypeError("The string '%s' should be composed solely of the characters '0' and '1'." % string)

    # Reverse the byte order as neccessary.
    if endian == 'big' and sys.byteorder == 'little':
        string = string[::-1]
    elif endian == 'little' and sys.byteorder == 'big':
        string = string[::-1]

    # Convert the bit pattern into a byte array (of integers).
    bytes = []
    for i in xrange(8):
        bytes.append(bitpatternToInt(string[i*8:i*8+8], endian=sys.byteorder))

    # Pack the byte array into a float and return it.
    return packBytesAsPyFloat(bytes)


def bitpatternToInt(string, endian='big'):
    """Convert a bit pattern into its integer representation.

    @param string:  The ascii string repesenting binary data.
    @type string:   str
    @param endian:  The endianness of the bit pattern (can be 'big' or 'little').
    @type endian:   str
    @return:        The integer value.
    @returntype:    int
    """

    # Test that the bit pattern is a string.
    if not isinstance(string, str):
        raise TypeError("The string argument '%s' is not a string." % string)

    # Test that the string consists solely of zeros and ones.
    for char in string:
        if char not in ['0', '1']:
            raise TypeError("The string '%s' should be composed solely of the characters '0' and '1'." % string)

    # Reverse the byte order as neccessary.
    if endian == 'big' and sys.byteorder == 'little':
        string = string[::-1]
    elif endian == 'little' and sys.byteorder == 'big':
        string = string[::-1]

    # Calculate the integer corresponding to the string.
    int_val = 0
    for i in xrange(len(string)):
        if int(string[i]):
            int_val = int_val + 2**i

    # Return the integer value.
    return int_val


# IEEE-754 Constants.
#####################

# The following bit patterns are to be read from right to left (big-endian).
# Hence bit positions 0 and 63 are to the far right and far left respectively.
PosZero             = bitpatternToFloat('0000000000000000000000000000000000000000000000000000000000000000', endian='big')
NegZero             = bitpatternToFloat('1000000000000000000000000000000000000000000000000000000000000000', endian='big')
PosEpsilonDenorm    = bitpatternToFloat('0000000000000000000000000000000000000000000000000000000000000001', endian='big')
NegEpsilonDenorm    = bitpatternToFloat('1000000000000000000000000000000000000000000000000000000000000001', endian='big')
PosEpsilonNorm      = bitpatternToFloat('0000000000010000000000000000000000000000000000000000000000000001', endian='big')
NegEpsilonNorm      = bitpatternToFloat('1000000000010000000000000000000000000000000000000000000000000001', endian='big')
PosMax              = bitpatternToFloat('0111111111101111111111111111111111111111111111111111111111111111', endian='big')
NegMin              = bitpatternToFloat('1111111111101111111111111111111111111111111111111111111111111111', endian='big')
PosInf              = bitpatternToFloat('0111111111110000000000000000000000000000000000000000000000000000', endian='big')
NegInf              = bitpatternToFloat('1111111111110000000000000000000000000000000000000000000000000000', endian='big')
PosNaN_A            = bitpatternToFloat('0111111111110000000000000000000000000000001000000000000000000000', endian='big')
NegNaN_A            = bitpatternToFloat('1111111111110000000000000000000000000000001000000000000000000000', endian='big')
PosNaN_B            = bitpatternToFloat('0111111111110000000000000000011111111111111111111110000000000000', endian='big')
NegNaN_B            = bitpatternToFloat('1111111111110000000000000000011111111111111111111110000000000000', endian='big')
PosNaN_C            = bitpatternToFloat('0111111111110101010101010101010101010101010101010101010101010101', endian='big')
NegNaN_C            = bitpatternToFloat('1111111111110101010101010101010101010101010101010101010101010101', endian='big')
PosNaN = PosNaN_C
NegNaN = NegNaN_C

#print "%-30s%-20.40g" % ("Pos zero: ", PosZero)
#print "%-30s%-20.40g" % ("Neg zero: ", NegZero)
#print "%-30s%-20.40g" % ("Pos epsilon denorm: ", PosEpsilonDenorm)
#print "%-30s%-20.40g" % ("Neg epsilon denorm: ", NegEpsilonDenorm)
#print "%-30s%-20.40g" % ("Pos epsilon norm: ", PosEpsilonNorm)
#print "%-30s%-20.40g" % ("Neg epsilon norm: ", NegEpsilonNorm)
#print "%-30s%-20.40g" % ("Max: ", PosMax)
#print "%-30s%-20.40g" % ("Min: ", NegMin)
#print "%-30s%-20.40g" % ("Pos inf: ", PosInf)
#print "%-30s%-20.40g" % ("Neg inf: ", NegInf)
#print "%-30s%-20.40g" % ("Pos NaN (A): ", PosNaN_A)
#print "%-30s%-20.40g" % ("Neg NaN (A): ", NegNaN_A)
#print "%-30s%-20.40g" % ("Pos NaN (B): ", PosNaN_B)
#print "%-30s%-20.40g" % ("Neg NaN (B): ", NegNaN_B)
#print "%-30s%-20.40g" % ("Pos NaN (C): ", PosNaN_C)
#print "%-30s%-20.40g" % ("Neg NaN (C): ", NegNaN_C)
