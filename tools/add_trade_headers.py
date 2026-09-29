from pathlib import Path

root = Path(__file__).resolve().parent.parent
backend = root / 'backend' / 'app.py'
s = backend.read_text()
s = s.replace('stock TEXT NOT NULL,\n          trade_date TEXT NOT NULL,', 'stock TEXT NOT NULL,\n          trade_date TEXT NOT NULL,\n          avg_sell_price REAL DEFAULT 0,')
s = s.replace('        """)\n\n\ndef number', '        """)\n        existing = {row[1] for row in conn.execute("PRAGMA table_info(trades)").fetchall()}\n        if "avg_sell_price" not in existing:\n            conn.execute("ALTER TABLE trades ADD COLUMN avg_sell_price REAL DEFAULT 0")\n\n\ndef number')
s = s.replace('return {**trade, "avg_buy_price": avg, "quantity": qty, "exit_price": exit_price,', 'return {**trade, "avg_buy_price": avg, "avg_sell_price": number(trade.get("avg_sell_price", exit_price)), "quantity": qty, "exit_price": exit_price,')
s = s.replace('stock, trade_date, trade_type, avg_buy_price, quantity,\n              exit_price, brokerage', 'stock, trade_date, trade_type, avg_buy_price, avg_sell_price, quantity,\n              exit_price, brokerage')
s = s.replace('(invoice_id, trade["stock"], trade["trade_date"], trade["trade_type"], trade["avg_buy_price"], trade["quantity"],\n               trade["exit_price"]', '(invoice_id, trade["stock"], trade["trade_date"], trade["trade_type"], trade["avg_buy_price"], trade["avg_sell_price"], trade["quantity"],\n               trade["exit_price"]')
s = s.replace('headers = ["No.", "DATE", "STOCK", "TYPE", "AVG. BUY PRICE", "QTY", "EXIT PRICE", "BROKERAGE", "P/L"]\n    rows = [[Paragraph(h, styles["Tiny"]) for h in headers]]', 'headers = ["No.", "DATE", "STOCK", "TYPE", "AVG. BUY", "AVG. SELL", "QTY", "EXIT", "BROKERAGE", "P/L"]\n    rows = [headers]')
s = s.replace('rows.append([str(i), t["trade_date"], Paragraph(t["stock"], styles["Tiny"]), t["trade_type"], money(t["avg_buy_price"]), f"{number(t[\'quantity\']):,.2f}", money(t["exit_price"]), money(t["brokerage"]), money(t["net_pl"])])', 'rows.append([str(i), t["trade_date"], t["stock"], t["trade_type"], money(t["avg_buy_price"]), money(t["avg_sell_price"]), f"{number(t[\'quantity\']):,.2f}", money(t["exit_price"]), money(t["brokerage"]), money(t["net_pl"])])')
s = s.replace('colWidths=[8*mm, 18*mm, 28*mm, 14*mm, 24*mm, 14*mm, 24*mm, 25*mm, 27*mm]', 'colWidths=[7*mm, 16*mm, 25*mm, 13*mm, 22*mm, 22*mm, 13*mm, 22*mm, 24*mm, 25*mm]')
s = s.replace('("TEXTCOLOR", (0,0), (-1,0), colors.white), ("ALIGN",', '("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,0), 6.5), ("ALIGN",')
backend.write_text(s)

frontend = root / 'frontend' / 'src' / 'App.tsx'
s = frontend.read_text()
s = s.replace("type Trade = { stock: string; trade_date: string; trade_type: 'BUY' | 'SELL'; avg_buy_price: number; quantity:", "type Trade = { stock: string; trade_date: string; trade_type: 'BUY' | 'SELL'; avg_buy_price: number; avg_sell_price: number; quantity:")
s = s.replace("trade_type:'BUY', avg_buy_price:0, quantity:0", "trade_type:'BUY', avg_buy_price:0, avg_sell_price:0, quantity:0")
s = s.replace("['avg_buy_price','quantity','exit_price','brokerage']", "['avg_buy_price','avg_sell_price','quantity','exit_price','brokerage']")
s = s.replace('<th>AVG. BUY PRICE</th><th>QTY</th><th>EXIT PRICE</th>', '<th>AVG. BUY</th><th>AVG. SELL</th><th>QTY</th><th>EXIT</th>')
s = s.replace('<td><input type="number" value={t.avg_buy_price} onChange={e=>updateTrade(i,\'avg_buy_price\',e.target.value)}/></td><td><input type="number" value={t.quantity}', '<td><input type="number" value={t.avg_buy_price} onChange={e=>updateTrade(i,\'avg_buy_price\',e.target.value)}/></td><td><input type="number" value={t.avg_sell_price} onChange={e=>updateTrade(i,\'avg_sell_price\',e.target.value)}/></td><td><input type="number" value={t.quantity}')
s = s.replace('<th>AVG. BUY PRICE</th><th>QTY</th><th>EXIT PRICE</th>', '<th>AVG. BUY</th><th>AVG. SELL</th><th>QTY</th><th>EXIT</th>')
s = s.replace('<td>{money(t.avg_buy_price)}</td><td>{t.quantity}</td><td>{money(t.exit_price)}</td>', '<td>{money(t.avg_buy_price)}</td><td>{money(t.avg_sell_price)}</td><td>{t.quantity}</td><td>{money(t.exit_price)}</td>')
frontend.write_text(s)
print('trade headers and avg sell field patched')
