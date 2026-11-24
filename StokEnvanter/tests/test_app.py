import unittest, tempfile
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
    def test_stock_in(self):
        p=app.add_product(self.data)
        self.assertEqual(app.update_stock(dict(product_id=p,quantity=5,operation='in')),8)
        self.assertEqual(app.list_products()[0]['stock'],8)
    def test_stock_out(self):
        p=app.add_product(self.data)
        self.assertEqual(app.update_stock(dict(product_id=p,quantity=2,operation='out')),1)
        self.assertEqual(app.list_products()[0]['stock'],1)
    def test_insufficient_stock(self):
        p=app.add_product(self.data)
        with self.assertRaises(ValueError): app.update_stock(dict(product_id=p,quantity=10,operation='out'))
        self.assertEqual(app.list_products()[0]['stock'],3)
    def test_invalid_quantity(self):
        p=app.add_product(self.data)
        for quantity in (0,-5,1.5,True):
            with self.subTest(quantity=quantity):
                with self.assertRaises(ValueError): app.update_stock(dict(product_id=p,quantity=quantity,operation='in'))
        self.assertEqual(app.list_products()[0]['stock'],3)
    def test_stock_persistence(self):
        p=app.add_product(self.data)
        app.update_stock(dict(product_id=p,quantity=7,operation='in'))
        self.assertEqual(app.list_products()[0]['stock'],10)
    def test_product_not_found(self):
        with self.assertRaises(ValueError): app.update_stock(dict(product_id=999,quantity=5,operation='in'))

    def test_stock_status_boundaries(self):
        for stock, expected in ((0,'empty'),(1,'low'),(10,'low'),(11,'ok')):
            with self.subTest(stock=stock):
                product_id=app.add_product(dict(self.data,code=f'B{stock}',stock=stock))
                product=next(p for p in app.list_products() if p['id']==product_id)
                self.assertEqual(product['stock_status'],expected)
    def test_stock_status_after_movement(self):
        p=app.add_product(dict(self.data,stock=11))
        app.update_stock(dict(product_id=p,quantity=1,operation='out'))
        self.assertEqual(app.list_products()[0]['stock_status'],'low')
        app.update_stock(dict(product_id=p,quantity=10,operation='out'))
        self.assertEqual(app.list_products()[0]['stock_status'],'empty')
        app.update_stock(dict(product_id=p,quantity=11,operation='in'))
        self.assertEqual(app.list_products()[0]['stock_status'],'ok')

if __name__=='__main__': unittest.main()
