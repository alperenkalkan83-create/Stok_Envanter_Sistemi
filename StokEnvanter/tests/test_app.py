import unittest,tempfile
from pathlib import Path
import app
class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.old=app.DB; app.DB=Path(self.tmp.name)/'test.db'; self.data=dict(code='A1',name='Fare',category='Elektronik',price='12.50',stock=3)
    def tearDown(self): app.DB=self.old; self.tmp.cleanup()
    def test_add_and_list(self):
        app.add_product(self.data); p=app.list_products()[0]; self.assertEqual((p['code'],p['price_cents'],p['stock']),('A1',1250,3))
    def test_empty(self): self.assertEqual(app.list_products(),[])
    def test_duplicate(self):
        app.add_product(self.data)
        with self.assertRaises(ValueError): app.add_product(dict(self.data,code='a1'))
    def test_negative_stock(self):
        with self.assertRaises(ValueError): app.add_product(dict(self.data,stock=-1))
    def test_blank_name(self):
        with self.assertRaises(ValueError): app.add_product(dict(self.data,name=' '))
    def test_invalid_price(self):
        with self.assertRaises(ValueError): app.add_product(dict(self.data,price='1.234'))
if __name__=='__main__': unittest.main()
