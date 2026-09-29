from pathlib import Path
root = Path(__file__).resolve().parent.parent

backend = root / 'backend' / 'app.py'
s = backend.read_text()
s = s.replace('headers = ["No.", "DATE", "STOCK", "TYPE", "AVG. BUY PRICE", "AVG. SELL PRICE", "QTY", "EXIT", "BROKERAGE", "P/L"]', 'headers = ["No.", "DATE", "STOCK", "TYPE", "ENTRY", "QTY", "EXIT", "BROKERAGE", "P/L"]')
s = s.replace('rows.append([str(i), t["trade_date"], t["stock"], Paragraph(f\'<font color="{type_color}"><b>{t["trade_type"]}</b></font>\', styles["Tiny"]), money(t["avg_buy_price"]), money(t["avg_sell_price"]), f"{number(t[\'quantity\']):,.2f}", money(t["exit_price"]), money(t["brokerage"]), Paragraph(f\'<font color="{pl_color}"><b>{money(t["net_pl"])}</b></font>\', styles["Tiny"])])', 'entry_price = t["avg_sell_price"] if t["trade_type"] == "SELL" else t["avg_buy_price"]\n        rows.append([str(i), t["trade_date"], t["stock"], Paragraph(f\'<font color="{type_color}"><b>{t["trade_type"]}</b></font>\', styles["Tiny"]), money(entry_price), f"{number(t[\'quantity\']):,.2f}", money(t["exit_price"]), money(t["brokerage"]), Paragraph(f\'<font color="{pl_color}"><b>{money(t["net_pl"])}</b></font>\', styles["Tiny"])])')
s = s.replace('colWidths=[10*mm, 16*mm, 25*mm, 14*mm, 21*mm, 21*mm, 13*mm, 21*mm, 20*mm, 21*mm]', 'colWidths=[10*mm, 16*mm, 25*mm, 14*mm, 32*mm, 13*mm, 22*mm, 24*mm, 26*mm]')
s = s.replace('trade_style.add("TEXTCOLOR", (9, row_index), (9, row_index)', 'trade_style.add("TEXTCOLOR", (8, row_index), (8, row_index)')
backend.write_text(s)

frontend = root / 'frontend' / 'src' / 'App.tsx'
s = frontend.read_text()
s = s.replace('<th>AVG. BUY PRICE</th><th>AVG. SELL PRICE</th>', '<th>ENTRY</th>')
s = s.replace('<td><input type="number" value={t.avg_buy_price} onChange={e=>updateTrade(i,\'avg_buy_price\',e.target.value)}/></td><td><input type="number" value={t.avg_sell_price} onChange={e=>updateTrade(i,\'avg_sell_price\',e.target.value)}/></td>', '<td><input type="number" value={t.trade_type===\'SELL\'?t.avg_sell_price:t.avg_buy_price} onChange={e=>updateTrade(i,t.trade_type===\'SELL\'?\'avg_sell_price\':\'avg_buy_price\',e.target.value)}/></td>')
s = s.replace('<td>{money(t.avg_buy_price)}</td><td>{money(t.avg_sell_price)}</td>', '<td>{money(t.trade_type===\'SELL\'?t.avg_sell_price:t.avg_buy_price)}</td>')
frontend.write_text(s)
print('avg price columns replaced with Entry')
