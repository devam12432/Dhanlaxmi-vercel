from pathlib import Path
root = Path(__file__).resolve().parent.parent

app = root / 'frontend' / 'src' / 'App.tsx'
s = app.read_text()
s = s.replace('/assets/angel-one-logo-pdf.png', '/assets/dhanlaxmi-logo-clean.png')
s = s.replace('/assets/angel-one-stamp-pdf.png', '/assets/dhanlaxmi-stamp-clean.png')
s = s.replace('Angel One</b><span>Invoice Studio', 'Dhanlaxmi</b><span>Invoice Studio')
s = s.replace('ANGEL ONE PVT. LTD.</span><h2>', 'DHANLAXMI CAPITAL PVT. LTD.</span><h2>')
s = s.replace('<div className="paper-box-title">PAYMENT SUMMARY</div><p><span>Total Profit</span><b>{money(invoice.total_profit)}</b></p><p><span>Total Loss</span><b>{money(invoice.total_loss)}</b></p>', '<div className="paper-box-title">PAYMENT SUMMARY</div><p><span>Total Profit</span><b className="positive">{money(invoice.total_profit)}</b></p><p><span>Total Loss</span><b className="positive">{money(invoice.total_loss)}</b></p>')
app.write_text(s)

backend = root / 'backend' / 'app.py'
s = backend.read_text()
s = s.replace('styles.add(ParagraphStyle(name="BoxValue"', 'styles.add(ParagraphStyle(name="ClientTitle", parent=styles["Normal"], fontSize=7.5, leading=10, textColor=colors.HexColor("#1d68bd"), fontName="Helvetica-Bold"))\n    styles.add(ParagraphStyle(name="BoxValue"')
s = s.replace('ASSET_DIR / "angel-one-logo-pdf.png"', 'ASSET_DIR / "dhanlaxmi-logo-pdf.png"')
s = s.replace('ASSET_DIR / "angel-one-stamp-pdf.png"', 'ASSET_DIR / "dhanlaxmi-stamp-pdf.png"')
s = s.replace('Paragraph("CLIENT DETAILS", styles["Small"])', 'Paragraph("CLIENT DETAILS", styles["ClientTitle"])')
s = s.replace('rows.append([str(i), t["trade_date"], t["stock"], t["trade_type"], money(t["avg_buy_price"]), money(t["avg_sell_price"]), f"{number(t[\'quantity\']):,.2f}", money(t["exit_price"]), money(t["brokerage"]), money(t["net_pl"])])', 'type_color = "#168a58" if t["trade_type"] == "BUY" else "#d9575f"\n        pl_color = "#168a58" if number(t["net_pl"]) >= 0 else "#d9575f"\n        rows.append([str(i), t["trade_date"], t["stock"], Paragraph(f\'<font color="{type_color}"><b>{t["trade_type"]}</b></font>\', styles["Tiny"]), money(t["avg_buy_price"]), money(t["avg_sell_price"]), f"{number(t[\'quantity\']):,.2f}", money(t["exit_price"]), money(t["brokerage"]), Paragraph(f\'<font color="{pl_color}"><b>{money(t["net_pl"])}</b></font>\', styles["Tiny"])])')
s = s.replace('summary = [[Paragraph("<b>PAYMENT SUMMARY</b>", styles["BoxTitle"]), ""], ["Total Profit", Paragraph(money(invoice["total_profit"]), styles["BoxValue"])], ["Total Loss", Paragraph(money(invoice["total_loss"]), styles["BoxValue"])],', 'summary = [[Paragraph("<b>PAYMENT SUMMARY</b>", styles["BoxTitle"]), ""], ["Total Profit", Paragraph(f\'<font color="#168a58"><b>{money(invoice["total_profit"])}</b></font>\', styles["BoxValue"])], ["Total Loss", Paragraph(f\'<font color="#168a58"><b>{money(invoice["total_loss"])}</b></font>\', styles["BoxValue"])],')
backend.write_text(s)

css = root / 'frontend' / 'src' / 'styles.css'
s = css.read_text()
s = s.replace('.client-box strong{font-size:10px;color:#1d68bd}', '.client-box strong{font-size:10px;color:#1d68bd;letter-spacing:.03em}')
css.write_text(s)
print('Dhanlaxmi branding and requested colors applied')
