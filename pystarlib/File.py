"""
Classes for dealing with STAR syntax
"""
import Utils
from Utils import Lister
from TagTable import TagTable
from Text import comments_strip
from Text import semicolon_block_collapse
from Text import nmrView_compress
from Text import pattern_save_begin
from Text import pattern_save_end
from Text import pattern_tagtable_loop
from Text import pattern_save_begin_nws
from Text import pattern_save_end_nws
from Text import pattern_tag_name_nws
from Text import pattern_tagtable_loop_nws
from SaveFrame import SaveFrame
import os
import re
#import profile

__author__    = "$Author: jurgenfd $" 
___revision__ = "$Revision: 13 $"
___date__     = "$Date: 2007-08-22 20:59:28 +0200 (Wed, 22 Aug 2007) $"



"""
STAR file
Only methods for reading and writing are currently implemented.
datanodes is a list of possibly mixed saveframes and tagtables
"""
class File (Lister):
    def __init__(self, 
                    title                   = 'general_star_file_title', 
                    filename                = '', 
                    datanodes               = None, 
                    flavor                  = None, # Call set_flavor when changing
#                    preferred_quote         = '"', # Put somewhere else?
                    verbosity   = 2
                  ):
        self.title      = title
        self.filename   = filename
        
        if datanodes:
          self.datanodes  = datanodes
        else:
          self.datanodes = []
          
        self.flavor     = flavor
        self.verbosity  = verbosity
        
    "Simple checks on integrity"
    def check_integrity(self, recursive = 1):
        if recursive:
            for datanode in self.datanodes:
                if datanode.check_integrity(recursive = 1):
                    print("ERROR: integrity check failed for Saveframe")
                    return 1
        if self.verbosity >= 9:
            print('Checked integrity of File    (%2s datanodes,  recurs.=%s)  : OK [%s]' % (
                len(self.datanodes), recursive, self.title))

    "Returns the STAR text representation"
    def star_text(self, flavor = None):
        if flavor == None:
            flavor = self.flavor
        str = 'data_%s\n' % self.title
        # Data node objects can be of type SaveFrame OR TagTable only
        # Data node object can now also contain comment information
        #      these comments are printed before the saveframe (Wim 2003/08/05)
        for datanode in self.datanodes:
            str = str + datanode.comment
            str = str + datanode.star_text(flavor = flavor)
        return str


    """
    Reads a NMR-STAR formatted file using
    the filename attribute.
    """
    def read (self, nmrView_type = 0):

        if not self.filename:
            print('ERROR: no filename in STARFile with title:', self.title)
            return 1
#        print "DEBUG: Current directory", os.listdir(os.curdir)
        text = open(self.filename, 'r').read()
        if self.parse(text=text, nmrView_type = nmrView_type):
            print("ERROR: couldn't parse file")
            return 1
         
        return 0

    
    """
    - Parses text into save frames and tagtables.
    - Input text should start at position given with non-white space character
    - Appends a list of datanodes(save frames or tagtables)
    """
    def parse (self, text='', nmrView_type = 0):

        if self.verbosity > 2:        
            print('DEBUG: Parsing STAR file:', self.filename)

        """
        '"Begin at the beginning," the King said, gravely,
        "and go on till you come to the end; then stop."' (LC)
        """
#        print "DEBUG taking care of EOL variations"
        text = Utils.dos2unix(text)# \r\n -> \n
        text = Utils.mac2unix(text)# \r   -> \n

        text = comments_strip(text)

        ## Collapse the semicolon block for ease of parsing
        text = semicolon_block_collapse(text)
        
        
        ## For nmrView 'nmrStar' also compress {  } into {}
        ## Wim 05/03/2003        
        if nmrView_type:
            text = nmrView_compress(text) 
        
        ## TITLE
        match_data_tag = re.search(r'\s*data_(\S+)\s+', text, 0)
        if not match_data_tag:
            print("ERROR: found no 'data_title' string in ")
            print("ERROR: file's text (first 100 chars):[%s] " % text[0:100])
            return 1
        self.title = match_data_tag.group(1)
        pos = match_data_tag.end()


        ## Four quick searches for possible continuations
        next_sf_begin   = None      # SAVE FRAME BEGIN
        next_sf_end     = None      # SAVE FRAME END
        next_free_tt    = None      # FREE TAGTABLE
        next_loop_tt    = None      # LOOP TAGTABLE
        sf_open         = None      # When a saveframe is open
        text_length     = len(text)

        ## Only break when parsed to the eof
        while pos < text_length:
            if self.verbosity >= 9:
                print('Parse text from position:%s : [%s]' % (
                    pos, text[pos:pos+10]))
            
            match_save_begin_nws = pattern_save_begin_nws.search(text, pos, pos+len('save_1'))
            if match_save_begin_nws:
                if match_save_begin_nws.start() == pos:
                    next_sf_begin = 1
            if not next_sf_begin:
                match_save_end_nws = pattern_save_end_nws.search(text, pos, pos+len('save_ '))
                if match_save_end_nws:
                    if match_save_end_nws.start() == pos:
                        next_sf_end = 1
            if not (next_sf_begin or next_sf_end):
                match_tag_name_nws = pattern_tag_name_nws.search(text, pos, pos+len(' _X'))
                if match_tag_name_nws:
                    if match_tag_name_nws.start() == pos:
                        next_free_tt = 1
            if not (next_sf_begin or next_sf_end or next_free_tt):
                match_tagtable_loop_nws = pattern_tagtable_loop_nws.search(text, pos, pos+len('loop_ '))
                if match_tagtable_loop_nws:
                    if match_tagtable_loop_nws.start() == pos:
                        next_loop_tt = 1

            ## Just checking
            if not (next_sf_begin or next_sf_end or next_free_tt or next_loop_tt):
                print('ERROR: No new item found in data_nodes_parse.')
                print('Items looked for are a begin or end of a saveframe, or')
                print('a begin of a tagtable(free or looped).')
                print() 
                print("At text (before pos=", pos, "):")
                start = pos-70
                if start < 0:
                    start = 0
                print("[" + text[start:pos] + "]")
                print("At text (starting pos=", pos, "):")
                print("[" + text[pos:pos+70]+ "]")
                return None
            
            ## SAVE FRAME BEGIN
            if next_sf_begin:
                if sf_open:
                    print("ERROR: Found the beginning of a saveframe but")
                    print("ERROR: saveframe before is still open(not closed;-)")
                    return None
                match_save_begin = pattern_save_begin.search(text, pos)
                if not match_save_begin:
                    print("ERROR: Code error (no second match on sf begin)");
                    return None
                if match_save_begin.start() != pos:
                    print("ERROR: Code error (wrong second match on sf begin)");
                    return None
                self.datanodes.append(SaveFrame(tagtables    = [])) # Need resetting ?
                self.datanodes[-1].title = match_save_begin.group(1)
                sf_open         = 1
                next_sf_begin   = None
                pos             = match_save_begin.end()
                continue

            ## SAVE FRAME END
            if next_sf_end:
                if not sf_open:
                    print("ERROR: Found the end of a saveframe but")
                    print("ERROR: saveframe was not open")
                    return None
                match_save_end = pattern_save_end.search(text, pos)
                if not match_save_end:
                    print("ERROR: Code error (no second match on sf end)");
                    return None
                if match_save_end.start() != pos:
                    print("ERROR: Code error (wrong second match on sf end)");
                    return None
                sf_open     = None
                next_sf_end = None
                pos         = match_save_end.end()
                continue

            ## FREE or LOOP TAGTABLE
            if next_free_tt:
                free            = 1
                next_free_tt    = None
            else: # next_loop_tt must be true as this was checked before
                if not next_loop_tt:
                    print('ERROR: code bug in File.parse()')
                    return None
                free            = None
                next_loop_tt    = None

                match_tagtable_loop = pattern_tagtable_loop.search(text, pos)
                if not match_tagtable_loop:
                    print('ERROR: Code error, no second match on tagtable_loop')
                    return None
                if match_tagtable_loop.start() != pos:
                    print("ERROR: Code error (wrong second match on tagtable_loop)")
                    return None
                pos = match_tagtable_loop.end()

            if sf_open:
                dn = self.datanodes[-1].tagtables # Insert in last saveframes' tagtables
            else:
                dn = self.datanodes
                
            dn.append(
                    TagTable(free      = free, 
                                tagnames  = [], 
                                tagvalues = [], 
                                verbosity = self.verbosity))
            tt = dn[-1] # Just to be verbose for the beloved reader
            pos = tt.parse(text=text, pos=pos)
            
            if pos ==  None:
                print("ERROR: In parsing tagtable")
                return None
            if self.verbosity >=9:                
                print('Parsed tagtable up to pos: [%s]' % pos)
            
        if self.verbosity > 2:
            print('DEBUG Parsed: [%s] datanodes (top level count only)' % \
                  len(self.datanodes))
            
        if self.check_integrity(recursive = 0):
            print("ERROR: integrity not ok")
            return 1

        # Save some memory
        text = ''
        return 0



    """
    Writes the object to a STAR formatted file using
    the filename attribute.
    """
    def write (self):
        if not self.filename:
            print('ERROR: no filename in STARFile with title:', self.title)
            return 1
        f = open(self.filename, 'w')
        f.write(self.star_text())
        f.close()
        if self.verbosity > 2:
            print('DEBUG: Written STAR file:', self.filename)

    """
    Reads only the top part of a file up to but excluding the line
    on which any given regexp matches.
    Returns None on success.
    """
    def getHeader( self, matchStrList, inputFN, outputFN ):
        matchList = []
        for str in matchStrList:
            m = re.compile(str)
            if m is None:
                print("ERROR: failed to compile pattern: ", str)
                return 1
#            print "Appended: ", str
            matchList.append( m )
        
        input  = open(inputFN,  'r')
        output = open(outputFN, 'w')
        L =[]
        line = input.readline()
        found = False
        while line:
            for m in matchList:
#                print "DEBUG: looking at line: ", line, " with ", m
                if m.search(line) != None:
                    found = True
                    break
            if found:
                break
            L.append(line)
            line = input.readline()

#        print "DEBUG: writing number of lines: ", len(L)
        output.writelines(L)                    
        output.close()
        if not os.path.exists(outputFN):
            print("WARNING: failed to materialize file: " + outputFN)
            return 1
        return None

    """
    Returns sfs that match the category, None for error and empty list
    for no matches.
    """
    def getSaveFrames(self, category = None):
        if not category:
            return None
        result = []
        for node in self.datanodes:
            if isinstance(node, SaveFrame): # redundant test for well behaved files
                if node.getSaveFrameCategory()==category:
                    result.append(node)
        return result


        
    """
    Tries to reformat a file on disk with the filename given in the
    attribute of this object.
    Running Steve Madings (BMRB) formatNMRSTAR program if available    
    NOTE: this does NOT do anything with the datanodes of this object!
    """
    def formatNMRSTAR(self, 
#                    comment_file_str_dir    = '/bmrb/lib', 
                    ):

        if self.verbosity >= 9:
            print("Attempting to reformat STAR file using external program if available")
        
        if os.name != 'posix':
            print("WARNING: No external program available on non-posix systems for reformatting STAR files")
            return 1

        ##  Try command and check for non-zero exit status
        ##  Note that these commands are only valid on Unix 
        ##  Standard error is thrown on the bit bucket.
        cmd = "%s < %s 2>/dev/null" % ('formatNMRSTAR', self.filename)
        pipe = os.popen(cmd)
        output = pipe.read()
        
        ##  The program exit status is available by the following construct
        ##  The status will be the exit number (in one of the bytes)
        ##  unless the program executed successfully in which case it will
        ##  be None.
        status = pipe.close()
        if self.verbosity >= 9:
            print("Got status:", status)

        ## Success
        if (status == None):
            try:
                open(self.filename, 'w').write(output)
            except IOError:
                print('ERROR: Could not open the file for writing', self.filename)
                return 1            
            if self.verbosity >= 9:
                print("Reformatted STAR file:", self.filename)
            return 0
        else:
            if self.verbosity :
                print("WARNING: Not pretty printing STAR file", self.filename)
            return 1
