from pathlib import Path
p = Path(__file__).resolve().parent.parent / 'frontend' / 'src' / 'styles.css'
s = p.read_text().replace('.paper-table td.buy{color:#1764c0;font-weight:700}', '.paper-table td.buy{color:#168a58;font-weight:700}')
p.write_text(s)
print('BUY preview color set to green')
