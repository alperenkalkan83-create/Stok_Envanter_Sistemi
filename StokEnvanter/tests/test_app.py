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

    def test_update_product(self):
        p=app.add_product(self.data)
        app.update_product(dict(self.data,product_id=p,code='B2',name='Yeni',category='Ofis',price='20.50',stock=99))
        row=app.list_products()[0]
        self.assertEqual((row['code'],row['name'],row['category'],row['price_cents'],row['stock']),('B2','Yeni','Ofis',2050,3))
    def test_update_same_code(self):
        p=app.add_product(self.data)
        app.update_product(dict(self.data,product_id=p,name='Yeni'))
        self.assertEqual(app.list_products()[0]['name'],'Yeni')
    def test_update_duplicate(self):
        p=app.add_product(self.data)
        app.add_product(dict(self.data,code='B2'))
        with self.assertRaises(ValueError): app.update_product(dict(self.data,product_id=p,code='b2'))
    def test_update_invalid_price(self):
        p=app.add_product(self.data)
        with self.assertRaises(ValueError): app.update_product(dict(self.data,product_id=p,price='-1'))
    def test_update_missing(self):
        with self.assertRaises(ValueError): app.update_product(dict(self.data,product_id=999))
    def test_update_blank_name(self):
        p=app.add_product(self.data)
        with self.assertRaises(ValueError): app.update_product(dict(self.data,product_id=p,name=' '))

    def test_delete_product(self):
        p=app.add_product(self.data)
        self.assertEqual(app.delete_product(dict(product_id=p)),p)
        self.assertEqual(app.list_products(),[])
    def test_delete_preserves_other_product(self):
        p=app.add_product(self.data)
        q=app.add_product(dict(self.data,code='B2'))
        app.delete_product(dict(product_id=p))
        self.assertEqual([r['id'] for r in app.list_products()],[q])
    def test_delete_missing(self):
        with self.assertRaises(ValueError): app.delete_product(dict(product_id=999))
    def test_delete_invalid(self):
        for value in (None,True,0,-1,'1',2**63):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): app.delete_product(dict(product_id=value))
    def test_delete_twice(self):
        p=app.add_product(self.data)
        app.delete_product(dict(product_id=p))
        with self.assertRaises(ValueError): app.delete_product(dict(product_id=p))

class FilterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = app.DB
        app.DB = Path(self.tmp.name) / 'filter.db'
        self.addCleanup(self.tmp.cleanup)
        self.addCleanup(setattr, app, 'DB', self.old)
        for code, name, category, stock in [('A1','Fare','Elektronik',20),('B2','Kalem','Ofis',5),('C3','Klavye','Elektronik',0)]:
            app.add_product(dict(code=code,name=name,category=category,stock=stock,price='10'))
        self.products = app.list_products()

    def test_search_name(self):
        self.assertEqual([p["code"] for p in app.filter_products(self.products, search='fare')], ['A1'])
    def test_search_code(self):
        self.assertEqual([p["code"] for p in app.filter_products(self.products, search='b2')], ['B2'])
    def test_category(self):
        self.assertEqual([p["code"] for p in app.filter_products(self.products, category='Elektronik')], ['C3', 'A1'])
    def test_low_stock(self):
        self.assertEqual([p["code"] for p in app.filter_products(self.products, status='low')], ['B2'])
    def test_empty_stock(self):
        self.assertEqual([p["code"] for p in app.filter_products(self.products, status='empty')], ['C3'])
    def test_combined(self):
        self.assertEqual([p["code"] for p in app.filter_products(self.products, category='Elektronik', status='ok')], ['A1'])
    def test_no_results(self):
        self.assertEqual([p["code"] for p in app.filter_products(self.products, search='olmayan')], [])
    def test_clear(self):
        self.assertEqual([p["code"] for p in app.filter_products(self.products)], ['C3', 'B2', 'A1'])
    def test_invalid_status(self):
        with self.assertRaises(ValueError):
            app.filter_products(self.products, status='invalid')

if __name__=='__main__': unittest.main()
