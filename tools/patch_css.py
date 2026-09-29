from pathlib import Path
p = Path(__file__).resolve().parent.parent / 'frontend' / 'src' / 'styles.css'
s = p.read_text()
s = s.replace('.paper-top img{width:145px;height:65px;', '.paper-top img{width:175px;height:72px;')
s = s.replace('.paper-table{width:100%;border-collapse:collapse}', '.paper-table{width:100%;border-collapse:collapse;table-layout:fixed}')
s = s.replace('.paper-table td{text-align:center;border:1px solid #e3e8ee;padding:8px 4px;font-size:9px;color:#38455a}', '.paper-table td{text-align:center;border:1px solid #e3e8ee;padding:8px 4px;font-size:9px;color:#38455a;overflow-wrap:anywhere}')
s = s.replace('.paper-box-title{font-size:10px;color:#1967ba;font-weight:700;margin-bottom:8px}', '.paper-box-title{background:#1457a6;color:#fff;font-size:10px;letter-spacing:.04em;font-weight:700;margin:-12px -12px 8px;padding:8px 12px;border-radius:6px 6px 0 0}')
p.write_text(s)
print('css patched')
