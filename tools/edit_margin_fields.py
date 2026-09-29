from pathlib import Path
root = Path(__file__).resolve().parent.parent

frontend = root / 'frontend' / 'src' / 'App.tsx'
s = frontend.read_text()
s = s.replace("free_margin:0, hold_margin:0, trades:[emptyTrade()]", "free_margin:0, hold_margin:0, total_margin:0, trades:[emptyTrade()]")
s = s.replace("return {...x,trades,total_margin:Number(x.free_margin||0)+Number(x.hold_margin||0),total_profit:profit", "return {...x,trades,total_margin:Number(x.total_margin||0),total_profit:profit")
s = s.replace('<h3>Margin details</h3>', '<h3>Deposit/Margin Details</h3>')
s = s.replace('<span className="required-note">Free and hold margin are editable</span>', '<span className="required-note">All three values are editable</span>')
s = s.replace('<Field label="Free margin" type="number" value={invoice.free_margin} onChange={v=>update(\'free_margin\',Number(v))}/><Field label="Hold margin" type="number" value={invoice.hold_margin} onChange={v=>update(\'hold_margin\',Number(v))}/><label><span>Total margin (automatic)</span><input value={money(invoice.total_margin)} readOnly/></label>', '<Field label="Deposit" type="number" value={invoice.free_margin} onChange={v=>update(\'free_margin\',Number(v))}/><Field label="Hold margin" type="number" value={invoice.hold_margin} onChange={v=>update(\'hold_margin\',Number(v))}/><Field label="Total" type="number" value={invoice.total_margin||0} onChange={v=>update(\'total_margin\',Number(v))}/>')
s = s.replace('<span className="eyebrow">MARGIN DETAILS</span><div className="summary-line"><span>Free margin</span>', '<span className="eyebrow">DEPOSIT/MARGIN DETAILS</span><div className="summary-line"><span>Deposit</span>')
s = s.replace('<span>Hold margin</span><b>{money(invoice.hold_margin)}</b></div><div className="summary-line"><span>Total margin</span><b>{money(invoice.total_margin)}</b>', '<span>Hold margin</span><b>{money(invoice.hold_margin)}</b></div><div className="summary-line"><span>Total</span><b>{money(invoice.total_margin)}</b>')
s = s.replace('<div className="paper-box-title">MARGIN DETAILS</div><p><span>Free Margin</span>', '<div className="paper-box-title">DEPOSIT/MARGIN DETAILS</div><p><span>Deposit</span>')
s = s.replace('<p><span>Hold Margin</span><b>{money(invoice.hold_margin)}</b></p><p><span>Total Margin</span><b>{money(invoice.total_margin)}</b>', '<p><span>Hold Margin</span><b>{money(invoice.hold_margin)}</b></p><p><span>Total</span><b>{money(invoice.total_margin)}</b>')
frontend.write_text(s)

backend = root / 'backend' / 'app.py'
s = backend.read_text()
s = s.replace('total_margin": free + hold, "total_profit"', 'total_margin": number(payload.get("total_margin")), "total_profit"')
s = s.replace('Paragraph("<b>MARGIN DETAILS</b>", styles["BoxTitle"])', 'Paragraph("<b>DEPOSIT/MARGIN DETAILS</b>", styles["BoxTitle"])')
s = s.replace('["Free Margin", Paragraph(money(invoice["free_margin"]), styles["BoxValue"])]', '["Deposit", Paragraph(money(invoice["free_margin"]), styles["BoxValue"])]')
s = s.replace('["Total Margin", Paragraph(money(invoice["total_margin"]), styles["BoxValue"])]', '["Total", Paragraph(money(invoice["total_margin"]), styles["BoxValue"])]')
backend.write_text(s)
print('margin fields are now independent and relabeled')
