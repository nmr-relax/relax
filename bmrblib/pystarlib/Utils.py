"""
Just a few utilities that can be of more general use.
"""
import re

__author__    = "$Author: jurgenfd $"
___revision__ = "$Revision: 10 $"
___date__     = "$Date: 2007-01-23 19:08:11 +0100 (Tue, 23 Jan 2007) $"

"""
$Log$
Revision 1.2  2007/01/23 18:08:11  jurgenfd
The below quoted value wasn't parsed correctly.
Occurs in the MR file for entry 2ihx.

'#It has very upfield-shifted H5', H5" @ 3.935,4.012 ppm'

Fixed with this update.

Revision 1.1.1.1  2007/01/09 22:10:15  jurgenfd
initial import

Revision 1.1  2007/01/08 20:49:41  jurgen
Merged improvements from Wim Vranken (EBI) back in.

Revision 1.1.1.1  2001/11/02 20:16:40  jurgen
Initial package capable of read/write access to STAR files without nested loops

"""

class Lister:
    """Example from 'Learning Python from O'Reilly publisher'"""
    def __repr__(self):
        return ("<Instance of %s, address %s:\n%s>" %
           (self.__class__.__name__, id(self), self.attrnames()))

    def attrnames(self):
        result=''
        keys = sorted(self.__dict__.keys())
        for attr in keys:
            if attr[:2] == "__":
                result = result + "\tname %s=<built-in>\n" % attr
            else:
                result = result + "\tname %s=%s\n" % (attr, self.__dict__[attr])
        return result        


"""
A fast transposing algorithm from the python mailing list
Used in TagTable.

This algorithm fails in Python 3, so has been replaced!
"""
def transpose ( matrix ):
    if len( matrix ) < 1:
        print('ERROR: trying to transpose an empty matrix')
        return 1
    elif len( matrix ) == 1:
        if len(matrix[0]) == 0:
            print('ERROR: trying to transpose an empty matrix, shape would be lost')
            print('ERROR: [[]] would become []')
            return 1
        else:
            return [(y,) for y in matrix[0]]
    else:
        # Init the transposed list of tuples (mxn) (the original matrix has dimensions nxm).
        result = []

        # Find the maximum length of the original second dimension.
        max_len = 0
        for i in range(len(matrix)):
            max_len = max(max_len, len(matrix[i]))

        # Loop over the second dimension.
        for j in range(max_len):
            # Initialise a new list to be later converted to a tuple.
            row = []

            # Loop over the first dimension.
            for i in range(len(matrix)):
                # Extend the row, padding with None.
                if j > len(matrix[i]) - 1:
                    row.append(None)
                else:
                    row.append(matrix[i][j])

            # Append the row as a tuple.
            result.append(tuple(row))

        return result


"""
Collapses all whitespace to a single regular space
before comparing. Doesn't remove final eol space.
"""
def equalIgnoringWhiteSpace( a, b):
    pattern   = re.compile("\s+" )
    a = re.sub(pattern, ' ', a)
    b = re.sub(pattern, ' ', b)
#    print "a["+a+"]"
#    print "b["+b+"]"
    return a == b

def dos2unix(text):
    return re.sub('\r\n', '\n', text)
def unix2dos(text):
    return re.sub('([^\r])(\n)', '\1\r\n', text)
def mac2unix(text):
    return re.sub('\r', '\n', text)
