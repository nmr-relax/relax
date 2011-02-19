from unittest import TestCase
import Utils,unittest


class AllChecks(TestCase):
    def test(self):
        """STAR Utils"""
        m1 = [ [1,2], [3,4] ]
        m2 = [ (1,3), (2,4) ]        
        m1t= Utils.transpose(m1)
        self.assertTrue(m1t==m2)
if __name__ == "__main__":
    unittest.main()
