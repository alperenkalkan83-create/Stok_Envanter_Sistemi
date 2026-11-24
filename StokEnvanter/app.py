import json
import sqlite3
from contextlib import closing
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from decimal import Decimal, InvalidOperation

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'inventory.db'
LIMIT = 100000000
LOW_STOCK_LIMIT = 10

def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, category TEXT NOT NULL, price_cents INTEGER NOT NULL CHECK(price_cents>=0), stock INTEGER NOT NULL CHECK(stock>=0))')
    return c

def validate_product(data):
    if not isinstance(data, dict):
        raise ValueError('Geçersiz veri.')
    code, name, category = [data.get(k, '').strip() if isinstance(data.get(k), str) else '' for k in ('code', 'name', 'category')]
    if not code or not name or not category or max(map(len, (code, name, category))) > 120:
        raise ValueError('Ürün bilgilerini eksiksiz girin (en fazla 120 karakter).')
    try:
        price = Decimal(str(data.get('price')))
        if not price.is_finite() or price < 0 or price > LIMIT or price * 100 != (price * 100).to_integral_value():
            raise ValueError()
    except (InvalidOperation, ValueError):
        raise ValueError('Fiyat negatif olmayan ve en fazla iki ondalıklı sayı olmalıdır.')
    return code.upper(), name, category, int(price*100)

def add_product(data):
    code, name, category, price_cents = validate_product(data)
    stock = data.get("stock")
    if type(stock) is not int or not 0 <= stock <= LIMIT:
        raise ValueError("Geçersiz stok miktarı.")
    try:
        with closing(connect()) as c, c:
            cur = c.execute('INSERT INTO products(code,name,category,price_cents,stock) VALUES(?,?,?,?,?)', (code, name, category, price_cents, stock))
            return cur.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError('Ürün kodu zaten kayıtlı.')

def update_product(data):
    code, name, category, price_cents = validate_product(data)
    product_id = data.get('product_id')
    if type(product_id) is not int or not 0 < product_id <= 2**63-1:
        raise ValueError('Geçersiz ürün.')
    try:
        with closing(connect()) as c, c:
            cur = c.execute('UPDATE products SET code=?, name=?, category=?, price_cents=? WHERE id=?', (code, name, category, price_cents, product_id))
            if cur.rowcount != 1:
                raise ValueError('Ürün bulunamadı.')
    except sqlite3.IntegrityError:
        raise ValueError('Ürün kodu zaten kayıtlı.')
    return product_id

def delete_product(data):
    if not isinstance(data, dict):
        raise ValueError('Geçersiz veri.')
    product_id = data.get('product_id')
    if type(product_id) is not int or not 0 < product_id <= 2**63-1:
        raise ValueError('Geçersiz ürün.')
    with closing(connect()) as c, c:
        cur = c.execute('DELETE FROM products WHERE id=?', (product_id,))
        if cur.rowcount != 1:
            raise ValueError('Ürün bulunamadı.')
    return product_id

def list_products():
    with closing(connect()) as c, c:
        products = [dict(r) for r in c.execute('SELECT * FROM products ORDER BY id DESC')]
        for product in products:
            product['stock_status'] = 'empty' if product['stock'] == 0 else 'low' if product['stock'] <= LOW_STOCK_LIMIT else 'ok'
        return products

def update_stock(data):
    if not isinstance(data, dict):
        raise ValueError('Geçersiz veri.')
    product_id, quantity, operation = (data.get(k) for k in ('product_id', 'quantity', 'operation'))
    if type(product_id) is not int or not 0 < product_id <= 2**63-1:
        raise ValueError('Geçersiz ürün.')
    if type(quantity) is not int or not 0 < quantity <= LIMIT:
        raise ValueError('Miktar pozitif tam sayı olmalıdır.')
    if operation not in ('in', 'out'):
        raise ValueError('Geçersiz stok işlemi.')
    with closing(connect()) as c, c:
        c.execute('BEGIN IMMEDIATE')
        product = c.execute('SELECT stock FROM products WHERE id=?', (product_id,)).fetchone()
        if product is None:
            raise ValueError('Ürün bulunamadı.')
        new_stock = product['stock'] + (quantity if operation == 'in' else -quantity)
        if new_stock < 0:
            raise ValueError('Yetersiz stok.')
        if new_stock > LIMIT:
            raise ValueError('Maksimum stok sınırı aşıldı.')
        c.execute('UPDATE products SET stock=? WHERE id=?', (new_stock, product_id))
        return new_stock

class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, kind='application/json; charset=utf-8'):
        self.send_response(status)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(body)

    def json(self, status, obj):
        self.send(status, json.dumps(obj, ensure_ascii=False).encode())

    def do_GET(self):
        if self.path == '/api/products':
            return self.json(200, list_products())
        files = {'/': ('index.html', 'text/html'), '/style.css': ('style.css', 'text/css'), '/app.js': ('app.js', 'text/javascript')}
        if self.path not in files:
            return self.json(404, {'error': 'Bulunamadı'})
        f, t = files[self.path]
        self.send(200, (ROOT/'static'/f).read_bytes(), t+'; charset=utf-8')

    def do_POST(self):
        if self.path not in ('/api/products', '/api/stock', '/api/products/update', '/api/products/delete'):
            return self.json(404, {'error': 'Bulunamadı'})
        try:
            n = int(self.headers.get('Content-Length', '0'))
            if not 0 < n <= 16384:
                raise ValueError('Geçersiz istek boyutu.')
            data = json.loads(self.rfile.read(n))
            if self.path == '/api/products':
                self.json(201, {'id': add_product(data)})
            elif self.path == '/api/products/update':
                self.json(200, {'id': update_product(data)})
            elif self.path == '/api/products/delete':
                self.json(200, {'id': delete_product(data)})
            else:
                self.json(200, {'stock': update_stock(data)})
        except (ValueError, UnicodeError) as e:
            self.json(400, {'error': str(e)})

if __name__ == '__main__':
    print('Stok Envanter: http://127.0.0.1:8000')
    ThreadingHTTPServer(('127.0.0.1', 8000), Handler).serve_forever()
