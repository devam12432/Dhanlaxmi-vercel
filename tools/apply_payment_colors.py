from pathlib import Path
root = Path(__file__).resolve().parent.parent
app = root / 'frontend' / 'src' / 'App.tsx'
s = app.read_text()
s = s.replace('/assets/dhanlaxmi-logo-clean.png', '/assets/dhanlaxmi-logo-hd.png')
s = s.replace('/assets/dhanlaxmi-stamp-clean.png', '/assets/dhanlaxmi-stamp-hd.png')
s = s.replace('<p><span>Total Profit</span><b className="positive">{money(invoice.total_profit)}</b></p><p><span>Total Loss</span><b className="positive">{money(invoice.total_loss)}</b></p>', '<p><span>Total Profit</span><b>{money(invoice.total_profit)}</b></p><p><span>Total Loss</span><b>{money(invoice.total_loss)}</b></p>')
s = s.replace('<p className="paper-total"><span>{(invoice.net_amount||0)>0?\'Total Receivable\':(invoice.net_amount||0)<0?\'Total Payable\':\'Zero Balance\'}</span><b>{money(invoice.net_amount)}</b></p>', '<p className="paper-total"><span>{(invoice.net_amount||0)>0?\'Total Receivable\':(invoice.net_amount||0)<0?\'Total Payable\':\'Zero Balance\'}</span><b className={(invoice.net_amount||0)>=0?\'positive\':\'negative\'}>{money(invoice.net_amount)}</b></p>')
app.write_text(s)

backend = root / 'backend' / 'app.py'
s = backend.read_text()
s = s.replace('ASSET_DIR / "dhanlaxmi-logo-pdf.png"', 'ASSET_DIR / "dhanlaxmi-logo-hd.png"')
s = s.replace('ASSET_DIR / "dhanlaxmi-stamp-pdf.png"', 'ASSET_DIR / "dhanlaxmi-stamp-hd.png"')
s = s.replace('summary = [[Paragraph("<b>PAYMENT SUMMARY</b>", styles["BoxTitle"]), ""], ["Total Profit", Paragraph(f\'<font color="#168a58"><b>{money(invoice["total_profit"])}</b></font>\', styles["BoxValue"])], ["Total Loss", Paragraph(f\'<font color="#168a58"><b>{money(invoice["total_loss"])}</b></font>\', styles["BoxValue"])], ["BROKERAGE Charges", Paragraph(money(invoice["brokerage"]), styles["BoxValue"])], ["Total Payable / Receivable", Paragraph(money(invoice["net_amount"]), styles["BoxValue"])]]', 'payable_color = "#168a58" if number(invoice["net_amount"]) >= 0 else "#d9575f"\n    summary = [[Paragraph("<b>PAYMENT SUMMARY</b>", styles["BoxTitle"]), ""], ["Total Profit", Paragraph(money(invoice["total_profit"]), styles["BoxValue"])], ["Total Loss", Paragraph(money(invoice["total_loss"]), styles["BoxValue"])], ["BROKERAGE Charges", Paragraph(money(invoice["brokerage"]), styles["BoxValue"])], ["Total Payable / Receivable", Paragraph(f\'<font color="{payable_color}"><b>{money(invoice["net_amount"])}</b></font>\', styles["BoxValue"])]]')
backend.write_text(s)
print('HD paths and payment colors updated')
