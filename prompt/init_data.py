from data import Data


class Init_data:
    def __init__(self, relax):
        """Class containing the macro for reinitialising self.relax.data"""

        self.relax = relax


    def init(self):
        """Macro for reinitialising self.relax.data"""

        self.relax.data = Data()
