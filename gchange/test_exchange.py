import unittest
from .exchange.btcc.btcc import Btcc

class ExchangeTestCase(unittest.TestCase):
    
    def testBtcc(self):
        b = Btcc()
        pass

if __name__ == '__main__': unittest.main()