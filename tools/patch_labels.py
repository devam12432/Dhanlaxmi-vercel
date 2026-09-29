from pathlib import Path
app = Path(__file__).resolve().parent.parent / 'frontend' / 'src' / 'App.tsx'
s = app.read_text()
for old, new in [
    ('<b>Invoice No.</b>', '<b>Invoice No.:</b>'),
    ('<b>Invoice Date</b>', '<b>Invoice Date:</b>'),
    ('<b>Client Name</b>', '<b>Client Name:</b>'),
    ('<b>Client ID</b>', '<b>Client ID:</b>'),
    ('<b>Address</b>', '<b>Address:</b>'),
    ('/assets/angel-one-logo-clean.png', '/assets/angel-one-logo-pdf.png'),
    ('/assets/angel-one-stamp-clean.png', '/assets/angel-one-stamp-pdf.png'),
]:
    s = s.replace(old, new)
app.write_text(s)

backend = Path(__file__).resolve().parent.parent / 'backend' / 'app.py'
s = backend.read_text()
for old, new in [
    ('angel-one-logo-clean.png', 'angel-one-logo-pdf.png'),
    ('angel-one-stamp-clean.png', 'angel-one-stamp-pdf.png'),
    ('Paragraph("TRADE DETAILS", styles["Section"])', 'Paragraph("<b>TRADE DETAILS</b>", styles["Section"])'),
    ('Paragraph("STOCK TRADING INVOICE", styles["Section"])', 'Paragraph("<b>STOCK TRADING INVOICE</b>", styles["Section"])'),
    ('Paragraph("MARGIN DETAILS", styles["BoxTitle"])', 'Paragraph("<b>MARGIN DETAILS</b>", styles["BoxTitle"])'),
    ('Paragraph("PAYMENT SUMMARY", styles["BoxTitle"])', 'Paragraph("<b>PAYMENT SUMMARY</b>", styles["BoxTitle"])'),
    ('"Invoice No.", styles["Small"]', '"Invoice No.:", styles["Small"]'),
    ('"Invoice Date", styles["Small"]', '"Invoice Date:", styles["Small"]'),
    ('"Client Name", styles["Small"]', '"Client Name:", styles["Small"]'),
    ('"Client ID", styles["Small"]', '"Client ID:", styles["Small"]'),
    ('"Address", styles["Small"]', '"Address:", styles["Small"]'),
]:
    s = s.replace(old, new)
backend.write_text(s)
print('labels and white PDF paths patched')
