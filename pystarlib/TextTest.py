from unittest import TestCase
from Text import comments_strip
import unittest


class AllChecks(TestCase):
    def test(self):
        """Text"""
#        textExpectedAfterCollapse = ';<eol-string>mmy xie<eol-string>;\n_Test'
#        text = """;
#mmy xie
#;
#_Test"""
#        textCollapsed = semicolon_block_collapse( text )
#        self.assertEqual( textExpectedAfterCollapse, textCollapsed)
#
#        value, pos = tag_value_quoted_parse( textCollapsed, 0 )
#        valueExpected = '\nmmy xie\n'
#        posExpected = 34
#        self.assertEqual( valueExpected, value )
#        self.assertEqual( posExpected, pos)
        
        t2 = """
 # comment 1
"""
        t2noComment = """
 
"""
        self.assertEqual(t2noComment,comments_strip( t2 ))

    def testcomments_strip(self):
        """comments_strip"""
        text = """
# my comment exactly
foo # comment
value#stil a value
bar
; # actual data
;
"""
        textExpected = """

foo 
value#stil a value
bar
; # actual data
;
"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)
    
    def testcomments_strip2(self):
        """comments_strip 2"""
        text = """
H' # comment
H" # also
"""
        textExpected = """
H' 
H" 
"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def testcomments_strip3a(self):
        """comments_strip 3a"""
        text = """
H# # comment
"""
        textExpected = """
H# 
"""

        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def testcomments_strip3(self):
        """comments_strip 3"""
        text = """
H# 
"""
        textExpected = """
H# 
"""

        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def testcomments_strip4(self):
        """comments_strip 4"""
        text = """
;
test1 # no comment 1
;
;
test2 # no comment 2
;
"""
        textExpected = """
;
test1 # no comment 1
;
;
test2 # no comment 2
;
"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def testcomments_strip5(self):
        """comments_strip 5"""
        text = """
'quoted value with embedded # comment' # real comment
"""
        textExpected = """
'quoted value with embedded # comment' 
"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def testcomments_strip6(self):
        """comments_strip 6"""
        text = """
"quoted value with embedded # comment" # real comment
"""
        textExpected = """
"quoted value with embedded # comment" 
"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def testcomments_strip7(self):
        """comments_strip 7"""
        text = """
"quoted 'complications ; ' with embedded # comment" # real comment
"""
        textExpected = """
"quoted 'complications ; ' with embedded # comment" 
"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

    def testcomments_strip8(self):
        """comments_strip 8"""
        text = """
"quoted 'complications;' with embedded # comment" # real comment
"""
        textExpected = """
"quoted 'complications;' with embedded # comment" 
"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)
    
    def testcomments_strip9(self):
        """comments_strip 9"""
        text = """
;

;
"""
        textExpected = """
;

;
"""
        textNew = comments_strip( text )
        self.assertEqual( textNew, textExpected)

if __name__ == "__main__":
    unittest.main()
