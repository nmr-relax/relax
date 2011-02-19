"""
Classes for dealing with STAR syntax
"""

__author__    = "$Author: jurgenfd $"
___revision__ = "$Revision: 13 $"
___date__     = "$Date: 2007-08-22 20:59:28 +0200 (Wed, 22 Aug 2007) $"

## Standard modules
import string, re

## BMRB modules
import __init__ # Actually the current package

"""
Some handy patterns and functions for dealing with text in the STAR syntax.
Some are complicated because in Python the none-greedy pattern matching
gets too recursive and will actually bomb on larger strings. Like the
following code causes a bomb:
re.search( 'a.*?c', 'a' + 99999*'b' + 'c' )
Produces: 'RuntimeError: maximum recursion limit exceeded'
"""

## Since there are only functions and no classes in this module
## the verbosity may be changed by changing the variable directly.
## I know that's vague but I don't know how to do it yet... todo.
verbosity           = 2

## When not sure if text can have a ; at start of line use
## this string prepended to each line.
prepending_string   = '[raw] '

FREE = 0
SINGLE = 1
DOUBLE = 2
singleq = "'"
doubleq = '"'
sharp   = '#'
space   = ' '
## Following string will be replacing the eol in a semicolon block where needed
## It may not contain any funny characters and shouldn't have underscores
## because it will make parsing slower. Parentheses, if used, should be of the
## square type.
eol_string = '<eol-string>'
eol_string_length = len(eol_string)
# Redefined below curiously found this bug with code analysis from pydev extensions
# changing the wild import to specific import; that sounds like bad python if it matters.
#pattern_tagtable_loop = re.compile(r"""
#^\s*  loop_  \s*                                  # Begin of loop
#(   ^\s*     (?P<tagname>_\S+) \s*\n  )+          # Tag names with some spaces
#       (?P<rawtext>.+?)                           # Tag table raw text
#^\s*  stop_  \s*\n                                # End of loop
#     """, re.DOTALL | re.MULTILINE | re.VERBOSE )

pattern_semicolon_block = re.compile(r"""
    ^;                                          # semicolon at begin, any text and then eol
    .+?                                         # Raw text for match object but not greedy
    ^;                                          # semicolon at begin, that's it
     """, re.DOTALL | re.MULTILINE | re.VERBOSE )

pattern_eol_string     = re.compile( eol_string, re.MULTILINE )

## Next pattern tells when search for on ONE tagvalue if it needs quotes
pattern_quotes_needed  = re.compile( r'[\s\'\"]|^_|^\#' ) 

## Next pattern tells when search for on MANY tagvalues if it needs quotes
## The values should be joined by a comma. A value: 'bla,_bla' will be
## mentioned as needing quotes unnecessarily but that's dealt with in the code by further checking
pattern_quotes_needed_2= re.compile( r'[\s\'\"]|^_|,_|,\#' ) 

pattern_eoline_etcet   = re.compile( r'[\n\r\v\f]' )
# If the quote character is at the end of the word then it is falsely considered to need a 
# different quote style; this happens frequently for e.g. H1' and all nucleic acid sugar atoms.
pattern_single_qoute   = re.compile( r"'" )
pattern_double_qoute   = re.compile( r'"' )

pattern_save_begin      = re.compile('save_(\S+)\s+')
pattern_save_end        = re.compile('save_\s*')
pattern_tagtable_loop   = re.compile("loop_\s*" )
pattern_tagtable_stop   = re.compile("stop_\s*" )
# Same thing but not eating all white space chars, just a minimal match
pattern_save_begin_nws      = re.compile('save_\S')
# Pattern extended to include matches to "save_" as the last characters in a file.
# in other words; without a end of line.
pattern_save_end_nws        = re.compile('(?:save_\s)|(?:save_$)')
#pattern_save_end_nws        = re.compile('save_\s')
pattern_tagtable_loop_nws   = re.compile('loop_\s')
pattern_tag_name_nws        = re.compile('_\S')
# Same thing but requiring a prefixed white space char:
##pattern_sf_begin_or_end = re.compile('\ssave_')
pattern_tagtable_loop_2 = re.compile('\sloop_\s+' )
pattern_tagtable_stop_2 = re.compile('\sstop_\s+' )
pattern_tagname_2       = re.compile('\s_\S+\s+' )

pattern_tag_name = re.compile(r"""(_\S+) \s+
     """, re.DOTALL | re.MULTILINE | re.VERBOSE )
pattern_tags_loop       = re.compile(r"""(?: (_\S+) \s* )+
     """, re.MULTILINE | re.VERBOSE )
pattern_tags_loop_2     = re.compile(r"""    (_\S+) \s*
     """, re.MULTILINE | re.VERBOSE )

## Get any number of non-white space characters followed by any white space
pattern_word            = re.compile(r"""(\S+)\s*""", re.MULTILINE )

pattern_quoted = re.compile(r"""
        ['"] |                          # single or double quote
    (?: ^ ; )                           # semicolon at the beginning of a line
     """, re.MULTILINE | re.VERBOSE )

pattern_quoted_2 = re.compile(r"""(?: \b [\'\"] ) | (?: ^  \;     )""", re.MULTILINE | re.VERBOSE )

pattern_s_quote        = re.compile(r"""\'\s+""", re.MULTILINE )
pattern_d_quote        = re.compile(r"""\"\s+""", re.MULTILINE )
pattern_e_semicolon    = re.compile( eol_string + r"""\;\s*""", re.MULTILINE ) # Added \n for better parsing Wim 01/11/05

# Set beginning of line BEFORE whitespace - Wim 06/03/2003
#pattern_comment_begin  = re.compile (r"""^\s*\#.*\n           # A string starting a line with a sharp
#                                   """, re.MULTILINE | re.VERBOSE)
                   
pattern_nmrView_compress_empty = re.compile(r""" \{(\s+)\}
                                             """, re.MULTILINE | re.VERBOSE)
pattern_nmrView_compress_questionmark = re.compile(r""" \{(\s+\?)\}
                                                    """, re.MULTILINE | re.VERBOSE)
# JFD old's
#pattern_comment_middle = re.compile (r"""(^[^;^\n] .*? )   # Any string beginning a line other than with a semicolon
#                                         (\s \#  .* $  )   # Any string ending a line and starting with a sharp
#                                   """, re.MULTILINE | re.VERBOSE)

# Wim's:                   
#pattern_comment_middle = re.compile (
#     r""" (                                             # start group 1 that will be captured for replay.
#             ^[^;^\n]                                   # not a what?
#             (?:                                        # start a non-capturing group
#                 (                                      # start group 2 (capturing?)
#                  [\'][^\']*\#[^\']*[\'] |              # get '<text>#<text>' 
#                  [\"][^\"]*\#[^\"]*[\"]                # get "<text>#<text>"
#                 ) |                
#                 [^\#.]                                 
#             )*? 
#           )  
#          # Any string beginning a line other than with a semicolon and with no quotes in it
#          (\s+\#.*)?    $                                                         # the comment to be deleted.
#          # Any string ending a line and starting with a sharp
#   """, re.MULTILINE | re.VERBOSE)
#    # Hashes in quotes don't count!
#    # (?:[\'\"][^\'^\".]*\#[^\'^\".]*[\'\"]|[^\#.])*? ) expression gets '<text>#<text>' blocks,
#    # is now built into multiline search, seems to be working... (Wim 11/02)
#    # Changed \s* to \s+ - comments can only start with a ' ' before the '#' (Wim 05/03)
#    # Removed . from [^\'^\".] in regular expression described above: more generic (Wim 05/03)
# doesn't catch"""H# # comment""" see testcomments_strip3a
# doesn't catch"""
#;
#foo # comment
#;"""


"""
Searches for a regular expression in text.
The text may not be STAR quoted and must have semicolon blocks collapsed
such that the semicolon starts at the beginning of the line.
Returns the start position of the match or -1 if it was not found or
None if there was an error.

The function will search the text from given position onwards
and checks the chars preceding (up to the line it's in) for quote style.

WARNINGS:
- Don't call it for a text that has no \n and at least 1 other
character in it before pos (not fully tested; perhaps possible).
- I have not put in extra checks because of needed speed.
- No requirements set on what follows the pattern.
"""

def pattern_unquoted_find(text, pattern, pos=0):    
    while 1:
        match = pattern.search( text, pos)
        if not match:
            ## No match at all
            return -1
        
        pos = match.start()

        ## Is it the beginning of the string
        if pos == 0:
            return 0

        ## Is the first character matched an eol it self
        if text[pos]=='\n':
            if verbosity >= 9:
                print 'Found pattern: [%s] at the beginning of a line' % pattern.pattern
            return pos
            
        ## I hope the rfind is optimized to stroll backwards from pos
        pos_end_of_previous_line = text.rfind('\n', 0, pos)
        if pos_end_of_previous_line == -1:
            pos_end_of_previous_line = -1 ## Dangerous rewind?
        
        line = text[pos_end_of_previous_line+1:pos]
        # Some dummy value but continue with the test below.
        if line == '':
            line = ' '
            
        # Not the one
        if line[0] == ';': 
            if verbosity > 1:
                print 'WARNING: (1) found pattern: [%s] preceded by: [%s]' % (
                    pattern.pattern, line )
            pos = pos + 1
            continue

        squoted = None
        dquoted = None
        for i in line:
            if      i == "'":
                if not dquoted:
                    squoted = not squoted
            elif    i == '"':
                if not squoted:
                    dquoted = not dquoted
        if squoted or dquoted:
##            if squoted and dquoted:
##                ## Should not be possible to occur, delete when confident
##                print "ERROR: code error, mixing of quote styles in line:"
##                print "ERROR: [%s]" % line
##                return None
            if verbosity > 1:
                print 'WARNING: (2) found pattern: [%s] preceded by: [%s]' % (
                    pattern.pattern, line )

            # Not the one
            pos = pos + 1 
            continue

        return pos

    
"""
Parse one quoted tag value beginning from position: pos
Return the value and the position of the 'cursor' behind the
value for the first non white space char.
In case of error the position value of None will signal failure.
"""
def tag_value_quoted_parse( text, pos ):
#    print 'text: [%s]' % text[pos:pos+80]
#    print 'pos:  [%s]' % pos
    if text[ pos ] == '"':
        match_d_quote = pattern_d_quote.search( text, pos+1)
        if not match_d_quote:
            print "ERROR: No matching double quote char found for double quote char at offset:", 0
            print "ERROR: Next 70 chars are: [%s]" % text[ pos:pos+70 ]
            return None, None
    ##            if verbosity >= 9:
    ##                print "pos, span():", pos, match_d_quote.span()
    ##                print 'Found Q tag value: [%s]' % text[ pos+1:match_d_quote.start() ]
        return text[ pos+1:match_d_quote.start() ], match_d_quote.end()

    if text[ pos ] == "'":
        match_s_quote = pattern_s_quote.search( text, pos+1)
        if not match_s_quote:
            print "ERROR: No matching single quote char found for single quote char at offset:", 0
            print "ERROR: Next 70 chars are: [%s]" % text[ pos:pos+70 ]
            return None, None
        value = text[ pos+1:match_s_quote.start() ]
    ##            if verbosity >= 9:
    ##                print "pos, span():", pos, match_s_quote.span()
    ##                print 'Found Q tag value: [%s]' % value
        return value, match_s_quote.end()

    ## Remove check for speed if you want
    ## This should always be true
    if text[ pos ] == ";":
        match_e_semicolon = pattern_e_semicolon.search( text, pos+1)
        if not match_e_semicolon:
            print "ERROR: No matching semicolon found for semicolon char at offset:", 0
            print "ERROR: Next 70 chars are: [%s]" % text[ pos:pos+70 ]
            return None, None
    ##            print "pos, span():", pos, match_e_semicolon.span()
        ## Include the first eol and the eol before the semicolon
        value = text[ pos+1:match_e_semicolon.start()+eol_string_length ]
        ## Expansion relatively cheap here and harmless if unique string as defined in
        ## eol_string is indeed unique
        ## print 'Found Q (semicolon) tag value: unexpanded [%s]' % value
        ## print '-----------'
        ## print text[ match_e_semicolon.start()+eol_string_length : match_e_semicolon.start()+eol_string_length + 20]
        ## print '-----------'
        value = semicolon_block_expand( value )
        ## print 'Found Q (semicolon) tag value: expanded   [%s]' % value
        
        return value, match_e_semicolon.end() 

    print   "ERROR: Position in text:", pos
    print """ERROR: should contain a ', ", or a ; but was not found:"""
    print   "ERROR: Next 70 chars are: [%s]" % text[ pos:pos+70 ]
    return None, None


"""
From text on position pos, read a tag value and return the value and
position of the next non-space char. This is the slow parsing method
that should only be used for free tags.
"""
def tag_value_parse( text, pos):

    match_quoted = pattern_quoted.search( text, pos )
    if match_quoted:      
        if match_quoted.start() == pos:
            
            return tag_value_quoted_parse( text, pos ) # Better speed with this code
                
    match_word = pattern_word.search( text, pos )
    if not match_word:
        print "ERROR: No match for a 'word' at offset:", pos
        print "ERROR: Next 70 chars are:", text[ pos:pos+70 ]
        return None, None
    if match_word.start() != pos:
        print "ERROR: Match for a 'word' at wrong offset:", match_word.start() - pos
        print "ERROR: Next 70 chars are:", text[ pos:pos+70 ]
        return None, None

    ## Include the first eol and the eol before the semicolon
    return  match_word.group(1), match_word.end()



"""
See function semicolon_block_collapse that calls this one
"""
def semicolon_block_replace( matchobj ):
    #print len(matchobj.group())
    return re.sub(  '\n', eol_string, matchobj.group() )


"""
This function should be called (not semicolon_block_replace)
Putting all semicolon separated values on one line
by replacing the eol within with a unique key value
that is to be remove later on by it's sibling method:
semicolon_block_expand.
SPEED:  0.6 cpu seconds for a 5 Mb file with 31 blocks and
        1.3 "                10 "            64 ".
"""
def semicolon_block_collapse( text ):
    
    count = 0
    startpos = 0
    
    # TODO: this is not good - since text[startpos:] is used it's always the start of a line, so if string starts with ;...
    pattern_semicolon_only = re.compile("^\;", re.MULTILINE)
    # Added special _end pattern with $ for better pattern matching - Wim 31/10/2005
    pattern_semicolon_only_end = re.compile("(^\;\s*$)", re.MULTILINE)
    
    semicolon_start = pattern_semicolon_only.search(text[startpos:])
    
    while(semicolon_start):

      count += 1
      
      startpos = startpos + semicolon_start.start()
      semicolon_end = pattern_semicolon_only_end.search(text[startpos+1:])
      try:
        endpos = startpos + 1 + semicolon_end.end() - len(semicolon_end.group(1)) + 1
      except:
        print "ERROR in semicolon_block_collapse for text starting at: ["+ text[startpos:startpos+100]+ "]"            
        raise
    
      text_replace = re.sub("\n", eol_string,text[startpos:endpos])

      # This is bulky and not very elegant but works
      text= text[0:startpos] + text_replace + text[endpos:]
    
      startpos = startpos + len(text_replace)
    
      semicolon_start = pattern_semicolon_only.search(text[startpos:])
   
    # Original code: can't handle re matches that are too long
    #text, count = pattern_semicolon_block.subn( semicolon_block_replace, text )
    if __init__.verbosity >= 9:
        print 'Done [%s] subs with semicolon blocks' % count
    return text

def semicolon_block_expand( text ):        
    return pattern_eol_string.sub('\n', text )

"""
Adds semicolons, single quotes or double quotes depending on
need according to star syntax.
Does not assume that no quotes exist initially and will strip them if
present in pairs only.

If the possible_bad_char parameter is set (to 1 or higher) then
strings that would normally end up in a semicolon delimited blob will
have a string inserted at the beginning to it. The string can be the 'p'
argument to this function. [TODO]
"""
def quotes_add( text ):

    preferred_quote='"' # This info should be in a more central spot
    
    if pattern_eoline_etcet.search( text ):
        return semicolons_add( text )

    if pattern_single_qoute.search( text ):
        single_qoute_match = 1
    else:
        single_qoute_match = 0

    if pattern_double_qoute.search( text ):
        double_qoute_match = 1
    else:
        double_qoute_match = 0

    if single_qoute_match and double_qoute_match:
        return semicolons_add( text )

    if single_qoute_match:
        return '"' + text + '"'
    # Commented out because it leads to the same behaviour
    if double_qoute_match:
        return "'" + text + "'"

    ## Space other than end of line, or # sign etc.
    return preferred_quote + text + preferred_quote


"Strips quotes in pairs and returns new/old string"
def quotes_strip( text ):

    ## Can it be containing quotes?
    if len(text) <= 1:
        return text
    for quote_symbol in [ "\'", '\"' ]:
        if ( text[0]  == quote_symbol and
             text[-1] == quote_symbol ):
            return text[1:-1]
    return text


"""
Returns the input with ; delimited, possibly with a string inserted at the beginning.
The string value should always be ended by a eol, otherwise
the second semicolon can not be the first char on a line.
"""
def semicolons_add( text, possible_bad_char=None ):
    if possible_bad_char:
        lines       = string.split(text,'\n')
        text   = ''
        for line in lines:
            text = text + prepending_string + line + '\n'
##        ## Code repeated for speed
##        return "\n;" + text + ";\n"
##    else:
##        return "\n;" + text + ";\n"
#JFD updates 5/23/2006; apparently the text does not always end with an eol.
    if not text.endswith('\n'):
       text = text + '\n'
    return "\n;\n" + text + ";\n"

"""
Strip the STAR comments new style
"""
def comments_strip( text ):
    lines = string.split(text, "\n" )
    i=0
    count = 0
    ls = len(lines)
#    print "DEBUG: processing lines: ", ls
    while i<ls:
#        print "DEBUG: processing A line: ", i
        line = lines[i]
        # Scan past semi colon blocks.
        l = len(line)
        if l < 1:
#            print "DEBUG: skipping empty line: "
            i += 1
            continue
        if line[0] == ';':                        # start a semicolon block
#            print "DEBUG: found start of semi colon block."
            i += 1
            line = lines[i]
#            print "DEBUG: processing B line: ", i
            while len(line)==0 or line[0] != ';':
                i += 1
                line = lines[i]
#                print "DEBUG: processing C line: ", i
                                                    # end a semicolon block
        else:
            line = _comments_strip_line(line)
            if len(line) != l:
                lines[i] = line
#                print "Changed from lenght",l,"to line: ["+line+"] at:", i
                count += 1
        i += 1

    if __init__.verbosity >= 9:
        print 'Done [%s] comment subs' % count
    text = string.join(lines,"\n")
    return text

"""
Strip the STAR comments for a single line.
"""
def _comments_strip_line( line ):
    c=0
    state = FREE # like to start out free which is possible after donning semicolon blocks.
    l = len(line)
    while c < l: # parse range [0,n> where n is length and exclusive.        
        ch=line[c]
#        print "DEBUG: Processing char '"+ch+"' at "+`c`+" in state:", state
        if ( ch == sharp and state == FREE and    # A sharp in FREE state
                (c==0 or line[c-1].isspace())):   # behind a space or at beginning of a line.
#            print "DEBUG: Found sharpie"
            if c==0:
                return ''
            return line[0:c] # this is fast.
        if c==l-1: # c is the last character; leave it alone if it's not a sharpie
            return line
        
        if ch == doubleq:
            if (state == FREE and                # new " behind space or at beginning of line
                (c==0 or line[c-1].isspace())):
                state = DOUBLE
            elif state == DOUBLE:
                if line[c+1].isspace(): # garanteed to exist now.                
                    state = FREE                
        elif ch == singleq:
            if (state == FREE and
                    (c==0 or line[c-1].isspace())):
                state = SINGLE
            elif state == SINGLE:
                if line[c+1].isspace():                    
                    state = FREE           
        c += 1
    return line

#def comments_stripOld( text ):
#    # split for profiling
#    text = _comments_strip1(text)
#    text = _comments_strip2(text)
#    return text
#
#def _comments_strip1( text ):
#    text, count = pattern_comment_begin.subn( '', text )
#    if verbosity >= 9:
#        print 'Done [%s] subs with comment at beginning of line' % count
#    return text
#
#def _comments_strip2( text ):
#    text, count = pattern_comment_middle.subn( '\g<1>', text )
#    if verbosity >= 9:
#        print 'Done [%s] subs with comment not at beginning of line' % count
#    return text
    
def nmrView_compress( text ):

    text, count = pattern_nmrView_compress_empty.subn( '{}', text )    
    print 'Compressed [%s] nmrView empty { } tags' % count

    text, count = pattern_nmrView_compress_questionmark.subn( '{?}', text )    
    print 'Compressed [%s] nmrView question mark { ?} tags' % count
    
    return text
