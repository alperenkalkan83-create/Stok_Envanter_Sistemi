import json, sqlite3, math
from contextlib import closing
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
ROOT=Path(__file__).resolve().parent
DB=ROOT/'inventory.db'
def connect():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, category TEXT NOT NULL, price_cents INTEGER NOT NULL CHECK(price_cents>=0), stock INTEGER NOT NULL CHECK(stock>=0))')
    return c

def add_product(data):
    if not isinstance(data,dict): raise ValueError('Geçersiz veri.')
    code,name,category=[str(data.get(k,'')).strip() if isinstance(data.get(k),str) else '' for k in ('code','name','category')]
    if not code or not name or not category or max(map(len,(code,name,category)))>120: raise ValueError('Ürün bilgilerini eksiksiz girin (en fazla 120 karakter).')
    from decimal import Decimal, InvalidOperation
    try:
        price=Decimal(str(data.get('price'))); stock=data.get('stock')
        if not price.is_finite() or price<0 or price>100000000 or price*100 != (price*100).to_integral_value() or type(stock) is not int or not 0<=stock<=100000000: raise ValueError()
    except (InvalidOperation,ValueError): raise ValueError('Fiyat en fazla iki ondalıklı, stok ise negatif olmayan tam sayı olmalıdır.')
    try:
        with closing(connect()) as c, c:
            cur=c.execute('INSERT INTO products(code,name,category,price_cents,stock) VALUES(?,?,?,?,?)',(code.upper(),name,category,int(price*100),stock)); return cur.lastrowid
    except sqlite3.IntegrityError: raise ValueError('Ürün kodu zaten kayıtlı.')

def list_products():
    with closing(connect()) as c, c: return [dict(r) for r in c.execute('SELECT * FROM products ORDER BY id DESC')]

class Handler(BaseHTTPRequestHandler):
    def send(self,status,body,kind='application/json; charset=utf-8'):
        self.send_response(status); self.send_header('Content-Type',kind); self.send_header('Content-Length',str(len(body))); self.send_header('X-Content-Type-Options','nosniff'); self.end_headers(); self.wfile.write(body)
    def json(self,status,obj): self.send(status,json.dumps(obj,ensure_ascii=False).encode())
    def do_GET(self):
        if self.path=='/api/products': return self.json(200,list_products())
        files={'/':('index.html','text/html'),'/style.css':('style.css','text/css'),'/app.js':('app.js','text/javascript')}
        if self.path not in files: return self.json(404,{'error':'Bulunamadı'})
        f,t=files[self.path]; self.send(200,(ROOT/'static'/f).read_bytes(),t+'; charset=utf-8')
    def do_POST(self):
        if self.path!='/api/products': return self.json(404,{'error':'Bulunamadı'})
        try:
            n=int(self.headers.get('Content-Length','0'))
            if not 0<n<=16384: raise ValueError('Geçersiz istek boyutu.')
            data=json.loads(self.rfile.read(n)); self.json(201,{'id':add_product(data)})
        except (ValueError,UnicodeError) as e: self.json(400,{'error':str(e)})
if __name__=='__main__':
    print('Stok Envanter: http://127.0.0.1:8000'); ThreadingHTTPServer(('127.0.0.1',8000),Handler).serve_forever()
