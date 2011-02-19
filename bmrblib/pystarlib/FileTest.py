"""Unit test
"""
from File import File
import Utils
import __init__

import os   
import zipfile
import urllib.request, urllib.parse, urllib.error
from unittest import TestCase


class AllChecks(TestCase):
        strf           = File(verbosity=2)        
        
        def testparse(self):
            """STAR parse"""
            text = """data_no_comments_here

save_comment
   _Saveframe_category  comment
   loop_
        _comment
        _every_flag
        _category

'#It has very upfield-shifted H5', H5" @ 3.935,4.012 ppm'
;
#######################
#  BOGUS              #
#######################

;
        
    BOGUS_CATEGORY

     stop_
save_
"""
            self.assertFalse(self.strf.parse(text=text))                                    
            st = self.strf.star_text()
#            print "unparsed text:[" +st+ "]"

            exp = """data_no_comments_here
save_comment   _Saveframe_category  comment   loop_
        _comment
        _every_flag
        _category
;
#It has very upfield-shifted H5', H5" @ 3.935,4.012 ppm
;
;
#######################
#  BOGUS              #
#######################

;    BOGUS_CATEGORY     stop_ save_
"""
            self.assertTrue(Utils.equalIgnoringWhiteSpace(exp, st))

        def testread2(self):
            """STAR File read"""
            testEntry('1edp')
              
"""
Extra Test Routine going over some entries in the NMR Restraints Grid
"""
def testEntry(entry):
    print("Testing Entry")
    strf = File() 
    __init__.verbosity = 2
    # Freely available on the web so not included in package.
    stage = "2-parsed"
#    stage = "3-converted-DOCR"
    urlLocation = ("http://www.bmrb.wisc.edu/WebModule/MRGridServlet?"+
    "block_text_type=%s&file_detail=%s&pdb_id=%s"+
    "&program=STAR&request_type=archive&subtype=full&type=entry") % (stage, stage, entry)
    fnamezip = entry+".zip"
#    print "DEBUG: downloading url:", urlLocation
    urllib.request.urlretrieve(urlLocation, fnamezip)
#    print "DEBUG: opening local zip file:", fnamezip
    zfobj = zipfile.ZipFile(fnamezip)
    fname = None
    for name in zfobj.namelist():    
        if name.endswith('.str'):
            fname = name            
    orgWattosWrittenFile     = entry+"_org.str"
    pystarlibWrittenFile     = entry+"_pystar.str"
    wattosWrittenFile        = entry+"_wattos.str"
    diffOrgPystarFile        = entry+"_diff_org_pystar.str"
    diffPystarWattosFile     = entry+"_diff_pystar_wattos.str"
    diffOrgWattosWattosFile  = entry+"_diff_org_wattos_wattos.str"

    outfile = open(orgWattosWrittenFile, 'w')
    outfile.write(zfobj.read(fname))
    outfile.close()      
    zfobj.close()          
    strf.filename  = orgWattosWrittenFile   
        
    strf.read()
    strf.filename  = pystarlibWrittenFile
    strf.write()

    if False:
        # In order to make the tests below work you'll first need to install Wattos
        #  which is why this test is not standard.
        try:
    #        print "Most likely the below diff will fail because it depends on diff being installed"
            cmd = "diff --ignore-all-space --ignore-blank-lines %s %s > %s" % ( orgWattosWrittenFile, pystarlibWrittenFile, diffOrgPystarFile)
            os.system(cmd)
            if not os.path.exists(diffOrgPystarFile):
                print("WARNING: failed to diff files: ", orgWattosWrittenFile, pystarlibWrittenFile)
            
    #        print "Most likely the below check will fail because it depends on Wattos being installed"
            print("DEBUG: rewrite to Java formating for comparison")
            cmd = "java -Xmx256m Wattos.Star.STARFilter %s %s ." % ( pystarlibWrittenFile, wattosWrittenFile)
            os.system(cmd)
            if not os.path.exists(wattosWrittenFile):
                print("WARNING: failed to rewrite file: " + pystarlibWrittenFile)
            else:
    #            print "Most likely the below diff will fail because it depends on diff being installed"
                cmd = "diff --ignore-all-space --ignore-blank-lines %s %s > %s" % ( pystarlibWrittenFile, wattosWrittenFile, diffPystarWattosFile)
                os.system(cmd)
                if not os.path.exists(diffPystarWattosFile):
                    print("WARNING: failed to diff file: ", pystarlibWrittenFile, wattosWrittenFile)
    #            print "Most likely the below diff will fail because it depends on diff being installed"
                cmd = "diff --ignore-all-space --ignore-blank-lines %s %s > %s" % ( orgWattosWrittenFile, wattosWrittenFile, diffOrgWattosWattosFile)
                os.system(cmd)
                if not os.path.exists(diffOrgWattosWattosFile):
                    print("WARNING: failed to diff file: ", orgWattosWrittenFile, wattosWrittenFile)
        except:
    #        print "DEBUG: failed the rewrite or diff but as mentioned that's totally understandable."
            pass
    
    try:
        os.unlink(entry+".zip")
        os.unlink(orgWattosWrittenFile)
        os.unlink(pystarlibWrittenFile)
    except:
        pass
    
    
def testAllEntries():
    """ No need to test all entries for the unit testing frame work"""
#    pdbList = ('1edp', '1q56', '1brv', '2hgh')
    pdbList = ('1edp')
    try:
        from Wattos.Utils import PDBEntryLists #@UnresolvedImport
        print("Imported Wattos.Utils; but it's not essential")
        pdbList = PDBEntryLists.getBmrbNmrGridEntries()[0:1] # Decide on the range yourself.
    except:
        print("Skipping import of Wattos.Utils; it's not needed")
    
    for entry in pdbList:
        print(entry)
        testEntry(entry)
#        entry = '1edp' # 57 kb
    #    entry = '1q56' # 10 Mb takes 27 s to parse on 2GHz PIV CPU
    #    entry = '1brv' # 1 Mb 
    #    entry = '1hue' # 6 Mb takes 26 s to parse on 2GHz PIV CPU
    #    entry = '2ihx' # ? Mb has weird quoted values
     
"""
Extra Test Routine going over some entries in the NMR Restraints Grid
"""
def testSingleFile( filename ):
    strf = File() 
    strf.filename  = filename   
    print("DEBUG: reading file ", strf.filename)
    strf.read()
    strf.filename  = strf.filename + "_new.str"
    print("DEBUG: writing file ", strf.filename)
    strf.write()
    
        
if __name__ == "__main__":
    testAllEntries()
#    testSingleFile("S:\\jurgen\\2hgh_small_new_google.str")
#    unittest.main()
    print("Done with STAR.FileTest")
