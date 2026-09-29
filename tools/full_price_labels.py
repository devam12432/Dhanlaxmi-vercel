from pathlib import Path
root = Path(__file__).resolve().parent.parent
for rel in ['frontend/src/App.tsx', 'backend/app.py']:
    p = root / rel
    s = p.read_text()
    s = s.replace('AVG. BUY</th><th>AVG. SELL</th>', 'AVG. BUY PRICE</th><th>AVG. SELL PRICE</th>')
    s = s.replace('"AVG. BUY", "AVG. SELL"', '"AVG. BUY PRICE", "AVG. SELL PRICE"')
    p.write_text(s)
print('full price labels updated')
