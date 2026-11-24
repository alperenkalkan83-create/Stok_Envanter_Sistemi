const $ = id => document.getElementById(id);
const money = n => new Intl.NumberFormat('tr-TR', {style:'currency',currency:'TRY'}).format(n/100);
let changing = false;
async function changeStock(productId, operation) {
    if (changing) return;
    const action = operation === 'in' ? 'giriş' : 'çıkış';
    const input = prompt(`Stok ${action} miktarını giriniz:`);
    if (input === null) return;
    const quantity = Number(input);
    if (!Number.isSafeInteger(quantity) || quantity <= 0 || quantity > 100000000) {
        alert('Geçerli bir pozitif tam sayı giriniz.'); return;
    }
    changing = true;
    try {
        const r = await fetch('/api/stock', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({product_id:productId,quantity,operation})});
        const result = await r.json();
        if (!r.ok) throw Error(result.error);
        try { await load(); alert(`Stok ${action} işlemi başarılı.`); }
        catch { alert('Stok güncellendi ancak liste yenilenemedi.'); }
    } catch (err) { alert(err.message); }
    finally { changing = false; }
}
async function load() {
    const r = await fetch('/api/products');
    if (!r.ok) throw Error('Liste alınamadı.');
    const data = await r.json();
    $('rows').replaceChildren();
    for (const p of data) {
        const tr = document.createElement('tr');
        for (const v of [p.code,p.name,p.category,money(p.price_cents),p.stock]) {
            const td = document.createElement('td'); td.textContent = v; tr.append(td);
        }
        const actions = document.createElement('td');
        for (const [operation,label] of [['in','+ Giriş'],['out','− Çıkış']]) {
            const b = document.createElement('button'); b.type='button'; b.textContent=label;
            if (operation === 'out') { b.style.backgroundColor='#b91c1c'; b.style.marginLeft='6px'; }
            b.onclick = () => changeStock(p.id,operation); actions.append(b);
        }
        tr.append(actions); $('rows').append(tr);
    }
    $('empty').textContent = data.length ? '' : 'Henüz ürün kaydı yok.';
    $('count').textContent = data.length;
    $('stock').textContent = data.reduce((s,p)=>s+p.stock,0);
    $('value').textContent = money(data.reduce((s,p)=>s+p.stock*p.price_cents,0));
}
$('form').addEventListener('submit',async e=>{
    e.preventDefault(); const f=e.currentTarget,b=f.querySelector('button'),d=Object.fromEntries(new FormData(f));
    d.stock=Number(d.stock); b.disabled=true;
    try {
        const r=await fetch('/api/products',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
        const result=await r.json(); if(!r.ok)throw Error(result.error);
        f.reset(); $('message').textContent='Ürün kaydedildi.';
        try {await load();} catch { $('message').textContent='Ürün kaydedildi ancak liste yenilenemedi.'; }
    } catch(err){$('message').textContent=err.message;} finally{b.disabled=false;}
});
load().catch(e=>$('message').textContent=e.message);
