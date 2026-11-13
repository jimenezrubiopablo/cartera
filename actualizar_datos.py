# Descarga los datos de Yahoo Finance y genera datos.js (junto a mercados.html).
# Uso: python actualizar_datos.py   (solo usa la librería estándar)
import json, re, urllib.request, urllib.parse, datetime as dt

ACTIVOS = ['IWDA.AS', 'EQQQ.DE', 'EMIM.AS', '4GLD.DE', 'BTC-EUR', 'FR0000447823']  # mismos que en mercados.html
RANGO = '5y'
H = {'User-Agent': 'Mozilla/5.0'}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30) as r:
        return json.load(r)

def resolver(t):
    if not re.fullmatch(r'[A-Z]{2}[A-Z0-9]{10}', t):
        return t
    q = get('https://query1.finance.yahoo.com/v1/finance/search?q=' + t)['quotes']
    return q[0]['symbol']

series = {}
for t in ACTIVOS:
    try:
        r = get(f'https://query1.finance.yahoo.com/v8/finance/chart/{resolver(t)}?range={RANGO}&interval=1d')['chart']['result'][0]
        c = r['indicators']['quote'][0]['close']
        out = [{'d': dt.datetime.utcfromtimestamp(x).strftime('%Y-%m-%d'), 'p': p}
               for x, p in zip(r['timestamp'], c) if p is not None]
        last = r['meta'].get('regularMarketPrice')
        hoy = dt.date.today().isoformat()
        if last is not None:
            if out and out[-1]['d'] == hoy: out[-1]['p'] = last
            else: out.append({'d': hoy, 'p': last})
        series[t] = out
        print('OK ', t, len(out))
    except Exception as e:
        print('ERR', t, e)

with open('datos.js', 'w', encoding='utf-8') as f:
    f.write('window.DATOS=' + json.dumps({'fecha': dt.datetime.now().strftime('%d/%m/%Y %H:%M'), 'series': series}) + ';')
