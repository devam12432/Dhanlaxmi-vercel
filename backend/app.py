from __future__ import annotations

import io
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, Image, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent if (BACKEND_DIR.parent / "frontend").exists() else BACKEND_DIR
IS_VERCEL = bool(os.getenv("VERCEL"))
# Vercel Functions have a read-only deployment filesystem. Use /tmp for SQLite at runtime.
# Local development continues to use the project's database/invoices.db.
DB_PATH = Path("/tmp/invoices.db") if IS_VERCEL else PROJECT_ROOT / "database" / "invoices.db"
PUBLIC_DIR = PROJECT_ROOT / "public"

# Resolve PDF assets from both the monorepo layout and the Vercel Flask service.
# Vercel Services can package the backend separately, so keep a local backend/assets
# fallback to guarantee the logo, stamp, and signature are available at runtime.
ASSET_DIRS = [
    BACKEND_DIR / "assets",
    PROJECT_ROOT / "frontend" / "public" / "assets",
    PROJECT_ROOT / "public" / "assets",
]

def asset_path(filename: str):
    for directory in ASSET_DIRS:
        candidate = directory / filename
        if candidate.is_file():
            return candidate
    return None

app = Flask(__name__)
CORS(app)


def db_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with db_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS invoices (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          invoice_number TEXT NOT NULL UNIQUE,
          invoice_date TEXT NOT NULL,
          client_name TEXT NOT NULL,
          client_id TEXT NOT NULL,
          address TEXT,
          free_margin REAL DEFAULT 0,
          hold_margin REAL DEFAULT 0,
          total_margin REAL DEFAULT 0,
          total_profit REAL DEFAULT 0,
          total_loss REAL DEFAULT 0,
          brokerage REAL DEFAULT 0,
          net_amount REAL DEFAULT 0,
          created_at TEXT,
          updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS trades (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          invoice_id INTEGER NOT NULL,
          stock TEXT NOT NULL,
          trade_date TEXT NOT NULL,
          avg_sell_price REAL DEFAULT 0,
          trade_type TEXT NOT NULL CHECK(trade_type IN ('BUY','SELL')),
          avg_buy_price REAL NOT NULL,
          quantity REAL NOT NULL,
          exit_price REAL NOT NULL,
          brokerage REAL DEFAULT 0,
          gross_pl REAL DEFAULT 0,
          net_pl REAL DEFAULT 0,
          created_at TEXT,
          FOREIGN KEY(invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
        );
        """)
        existing = {row[1] for row in conn.execute("PRAGMA table_info(trades)").fetchall()}
        if "avg_sell_price" not in existing:
            conn.execute("ALTER TABLE trades ADD COLUMN avg_sell_price REAL DEFAULT 0")


def number(value, default=0.0):
    try:
        result = float(value)
        return result if result == result else default
    except (TypeError, ValueError):
        return default


def calculate_trade(trade):
    buy_entry = number(trade.get("avg_buy_price"))
    sell_entry = number(trade.get("avg_sell_price"))
    qty = number(trade.get("quantity"))
    exit_price = number(trade.get("exit_price"))
    brokerage = number(trade.get("brokerage"))
    trade_type = trade.get("trade_type", "BUY")
    entry_price = (sell_entry if sell_entry > 0 else buy_entry) if trade_type == "SELL" else buy_entry
    gross = (entry_price - exit_price) * qty if trade_type == "SELL" else (exit_price - entry_price) * qty
    return {**trade, "avg_buy_price": buy_entry, "avg_sell_price": sell_entry, "quantity": qty, "exit_price": exit_price,
            "brokerage": brokerage, "gross_pl": gross, "net_pl": gross - brokerage}


def calculate_invoice(payload):
    trades = [calculate_trade(t) for t in payload.get("trades", [])]
    total_profit = sum(t["gross_pl"] for t in trades if t["gross_pl"] > 0)
    total_loss = sum(abs(t["gross_pl"]) for t in trades if t["gross_pl"] < 0)
    brokerage = sum(t["brokerage"] for t in trades)
    free = number(payload.get("free_margin"))
    hold = number(payload.get("hold_margin"))
    return {**payload, "trades": trades, "free_margin": free, "hold_margin": hold,
            "total_margin": number(payload.get("total_margin")), "total_profit": total_profit,
            "total_loss": total_loss, "brokerage": brokerage,
            "net_amount": total_profit - total_loss - brokerage}


def serialize_invoice(row, trades):
    data = dict(row)
    data["trades"] = [dict(t) for t in trades]
    return data


def validate(payload):
    missing = [field for field in ("invoice_number", "invoice_date", "client_name", "client_id") if not str(payload.get(field, "")).strip()]
    if missing:
        return "Required fields missing: " + ", ".join(missing)
    for trade in payload.get("trades", []):
        if not str(trade.get("stock", "")).strip() or not str(trade.get("trade_date", "")).strip():
            return "Every trade requires a stock and date."
        if trade.get("trade_type") not in ("BUY", "SELL"):
            return "Trade type must be BUY or SELL."
    return None


def save_invoice(payload, invoice_id=None):
    payload = calculate_invoice(payload)
    now = datetime.utcnow().isoformat(timespec="seconds")
    with db_conn() as conn:
        if invoice_id is None:
            cur = conn.execute("""INSERT INTO invoices
              (invoice_number, invoice_date, client_name, client_id, address, free_margin, hold_margin,
               total_margin, total_profit, total_loss, brokerage, net_amount, created_at, updated_at)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (payload["invoice_number"], payload["invoice_date"], payload["client_name"], payload["client_id"],
               payload.get("address", ""), payload["free_margin"], payload["hold_margin"], payload["total_margin"],
               payload["total_profit"], payload["total_loss"], payload["brokerage"], payload["net_amount"], now, now))
            invoice_id = cur.lastrowid
        else:
            conn.execute("""UPDATE invoices SET invoice_number=?, invoice_date=?, client_name=?, client_id=?, address=?,
              free_margin=?, hold_margin=?, total_margin=?, total_profit=?, total_loss=?, brokerage=?, net_amount=?, updated_at=?
              WHERE id=?""", (payload["invoice_number"], payload["invoice_date"], payload["client_name"], payload["client_id"],
              payload.get("address", ""), payload["free_margin"], payload["hold_margin"], payload["total_margin"],
              payload["total_profit"], payload["total_loss"], payload["brokerage"], payload["net_amount"], now, invoice_id))
            conn.execute("DELETE FROM trades WHERE invoice_id=?", (invoice_id,))
        for trade in payload["trades"]:
            conn.execute("""INSERT INTO trades (invoice_id, stock, trade_date, trade_type, avg_buy_price, avg_sell_price, quantity,
              exit_price, brokerage, gross_pl, net_pl, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (invoice_id, trade["stock"], trade["trade_date"], trade["trade_type"], trade["avg_buy_price"], trade["avg_sell_price"], trade["quantity"],
               trade["exit_price"], trade["brokerage"], trade["gross_pl"], trade["net_pl"], now))
        row = conn.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone()
        trades = conn.execute("SELECT * FROM trades WHERE invoice_id=? ORDER BY id", (invoice_id,)).fetchall()
        return serialize_invoice(row, trades)


@app.get("/")
def frontend_home():
    index = PUBLIC_DIR / "index.html"
    if index.exists():
        return send_file(index)
    return jsonify({"status": "ok", "message": "Angel One Invoice API is running"})


@app.get("/<path:path>")
def frontend_assets(path):
    # Keep API routes under /api; serve the built Vite application for all other paths.
    if path.startswith("api/"):
        return jsonify({"error": "API route not found"}), 404
    requested = PUBLIC_DIR / path
    if requested.is_file():
        return send_file(requested)
    index = PUBLIC_DIR / "index.html"
    if index.exists():
        return send_file(index)
    return jsonify({"error": "Not found"}), 404


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/invoices")
def list_invoices():
    query = request.args.get("search", "").strip()
    with db_conn() as conn:
        if query:
            rows = conn.execute("SELECT * FROM invoices WHERE invoice_number LIKE ? OR client_name LIKE ? ORDER BY id DESC", (f"%{query}%", f"%{query}%")).fetchall()
        else:
            rows = conn.execute("SELECT * FROM invoices ORDER BY id DESC").fetchall()
        return jsonify([dict(r) for r in rows])


@app.get("/api/invoices/<int:invoice_id>")
def get_invoice(invoice_id):
    with db_conn() as conn:
        row = conn.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone()
        if not row:
            return jsonify({"error": "Invoice not found"}), 404
        trades = conn.execute("SELECT * FROM trades WHERE invoice_id=? ORDER BY id", (invoice_id,)).fetchall()
        return jsonify(serialize_invoice(row, trades))


@app.post("/api/invoices")
def create_invoice():
    payload = request.get_json(silent=True) or {}
    error = validate(payload)
    if error:
        return jsonify({"error": error}), 400
    try:
        return jsonify(save_invoice(payload)), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Invoice number must be unique."}), 409
    except Exception:
        app.logger.exception("create invoice failed")
        return jsonify({"error": "Unable to save invoice."}), 500


@app.put("/api/invoices/<int:invoice_id>")
def update_invoice(invoice_id):
    payload = request.get_json(silent=True) or {}
    error = validate(payload)
    if error:
        return jsonify({"error": error}), 400
    try:
        with db_conn() as conn:
            if not conn.execute("SELECT id FROM invoices WHERE id=?", (invoice_id,)).fetchone():
                return jsonify({"error": "Invoice not found"}), 404
        return jsonify(save_invoice(payload, invoice_id))
    except sqlite3.IntegrityError:
        return jsonify({"error": "Invoice number must be unique."}), 409
    except Exception:
        app.logger.exception("update invoice failed")
        return jsonify({"error": "Unable to update invoice."}), 500


@app.delete("/api/invoices/<int:invoice_id>")
def delete_invoice(invoice_id):
    with db_conn() as conn:
        cur = conn.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))
        if cur.rowcount == 0:
            return jsonify({"error": "Invoice not found"}), 404
    return jsonify({"message": "Invoice deleted"})


def money(value):
    return f"Rs. {number(value):,.2f}"


def build_pdf(invoice):
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Small", parent=styles["Normal"], fontSize=7.5, leading=10, textColor=colors.HexColor("#4b5563")))
    styles.add(ParagraphStyle(name="Tiny", parent=styles["Normal"], fontSize=6.5, leading=8, textColor=colors.HexColor("#4b5563")))
    styles.add(ParagraphStyle(name="Section", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.white, alignment=TA_CENTER, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="BoxTitle", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.white, alignment=TA_LEFT, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="ClientTitle", parent=styles["Normal"], fontSize=7.5, leading=10, textColor=colors.HexColor("#1d68bd"), fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="BoxValue", parent=styles["Normal"], fontSize=7.5, leading=9, textColor=colors.HexColor("#26364f"), alignment=TA_RIGHT))
    styles.add(ParagraphStyle(name="Right", parent=styles["Normal"], fontSize=8, leading=10, alignment=TA_RIGHT))
    doc = BaseDocTemplate(buffer, pagesize=A4, rightMargin=14*mm, leftMargin=14*mm, topMargin=13*mm, bottomMargin=15*mm)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    def footer(canvas, _doc):
        canvas.saveState(); canvas.setStrokeColor(colors.HexColor("#d7dde8")); canvas.line(14*mm, 12*mm, A4[0]-14*mm, 12*mm)
        canvas.setFont("Helvetica-Bold", 8); canvas.setFillColor(colors.HexColor("#111827")); canvas.drawRightString(A4[0]-14*mm, 7*mm, "THANK YOU FOR TRADING WITH US!")
        canvas.restoreState()
    doc.addPageTemplates([PageTemplate(id="invoice", frames=frame, onPage=footer)])
    story = []
    logo = asset_path("dhanlaxmi-logo-hd.png") or asset_path("dhanlaxmi-logo-pdf.png")
    if logo:
        logo_table = Table([[Image(str(logo), width=55*mm, height=27*mm, kind="proportional")]], colWidths=[doc.width], style=TableStyle([("ALIGN", (0,0), (-1,-1), "LEFT"), ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0), ("TOPPADDING", (0,0), (-1,-1), 0), ("BOTTOMPADDING", (0,0), (-1,-1), 0)]))
        story.append(logo_table)
    story.append(Table([["STOCK TRADING INVOICE"]], colWidths=[doc.width], style=TableStyle([("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#0c1426")), ("TEXTCOLOR", (0,0), (-1,-1), colors.white), ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8), ("ALIGN", (0,0), (-1,-1), "LEFT"), ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)])))
    story.append(Spacer(1, 7))
    details = [[Paragraph("Invoice No.:", styles["Small"]), Paragraph(str(invoice["invoice_number"]), styles["Small"]), Paragraph("CLIENT DETAILS", styles["ClientTitle"]), ""],
               [Paragraph("Invoice Date:", styles["Small"]), Paragraph(str(invoice["invoice_date"]), styles["Small"]), Paragraph("Client Name:", styles["Small"]), Paragraph(invoice["client_name"], styles["Small"])],
               ["", "", Paragraph("Client ID:", styles["Small"]), Paragraph(invoice["client_id"], styles["Small"])],
               ["", "", Paragraph("Address:", styles["Small"]), Paragraph(invoice.get("address") or "—", styles["Small"])]]
    story.append(Table(details, colWidths=[24*mm, 55*mm, 30*mm, doc.width-109*mm], style=TableStyle([("BACKGROUND", (2,0), (-1,-1), colors.HexColor("#f4f7fb")), ("TEXTCOLOR", (2,0), (2,0), colors.HexColor("#1457a6")), ("FONTNAME", (2,0), (2,0), "Helvetica-Bold"), ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5), ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4)])))
    story.append(Spacer(1, 9))
    headers = ["No.", "DATE", "STOCK", "TYPE", "ENTRY", "QTY", "EXIT", "BROKERAGE", "P/L"]
    rows = [headers]
    for i, t in enumerate(invoice.get("trades", []), 1):
        type_color = "#168a58" if t["trade_type"] == "BUY" else "#d9575f"
        pl_color = "#168a58" if number(t["net_pl"]) >= 0 else "#d9575f"
        entry_price = t["avg_sell_price"] if t["trade_type"] == "SELL" else t["avg_buy_price"]
        rows.append([str(i), t["trade_date"], t["stock"], Paragraph(f'<font color="{type_color}"><b>{t["trade_type"]}</b></font>', styles["Tiny"]), money(entry_price), f"{number(t['quantity']):,.2f}", money(t["exit_price"]), money(t["brokerage"]), Paragraph(f'<font color="{pl_color}"><b>{money(t["net_pl"])}</b></font>', styles["Tiny"])])
    trade_table = Table(rows, colWidths=[10*mm, 16*mm, 25*mm, 14*mm, 32*mm, 13*mm, 22*mm, 24*mm, 26*mm], repeatRows=1, hAlign="LEFT")
    trade_style = TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0c1426")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,0), 6.2), ("ALIGN", (0,0), (-1,-1), "CENTER"), ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("GRID", (0,0), (-1,-1), .25, colors.HexColor("#d9e0ea")), ("FONTSIZE", (0,1), (-1,-1), 6.5), ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)])
    for row_index, trade in enumerate(invoice.get("trades", []), 1):
        trade_style.add("TEXTCOLOR", (8, row_index), (8, row_index), colors.HexColor("#0f9d68" if number(trade.get("net_pl")) >= 0 else "#d9575f"))
    trade_table.setStyle(trade_style)
    trade_title = Table([["TRADE DETAILS"]], colWidths=[doc.width], hAlign="LEFT", style=TableStyle([("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#0c1426")), ("TEXTCOLOR", (0,0), (-1,-1), colors.white), ("FONTNAME", (0,0), (-1,-1), "Helvetica-Bold"), ("FONTSIZE", (0,0), (-1,-1), 8), ("ALIGN", (0,0), (-1,-1), "CENTER"), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
    story += [trade_title, Spacer(1, 6), trade_table, Spacer(1, 12)]
    box_width = doc.width/2 - 8
    inner_widths = [box_width*0.58, box_width*0.42]
    margin = [[Paragraph("<b>DEPOSIT / MARGIN DETAILS</b>", styles["BoxTitle"]), ""], ["Deposit", Paragraph(money(invoice["free_margin"]), styles["BoxValue"])], ["Hold Margin", Paragraph(money(invoice["hold_margin"]), styles["BoxValue"])], ["Total", Paragraph(money(invoice["total_margin"]), styles["BoxValue"])]]
    payable_color = "#168a58" if number(invoice["net_amount"]) >= 0 else "#d9575f"
    summary = [[Paragraph("<b>PAYMENT SUMMARY</b>", styles["BoxTitle"]), ""], ["Total Profit", Paragraph(money(invoice["total_profit"]), styles["BoxValue"])], ["Total Loss", Paragraph(money(invoice["total_loss"]), styles["BoxValue"])], ["BROKERAGE Charges", Paragraph(money(invoice["brokerage"]), styles["BoxValue"])], ["Total Payable / Receivable", Paragraph(f'<font color="{payable_color}"><b>{money(invoice["net_amount"])}</b></font>', styles["BoxValue"])]]
    inner_style = TableStyle([("SPAN", (0,0), (-1,0)), ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1457a6")), ("GRID", (0,1), (-1,-1), .25, colors.HexColor("#e1e7f0")), ("ALIGN", (1,1), (-1,-1), "RIGHT"), ("FONTSIZE", (0,0), (-1,-1), 7.5), ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6), ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6)])
    margin_table = Table(margin, colWidths=inner_widths, style=inner_style)
    summary_table = Table(summary, colWidths=inner_widths, style=inner_style)
    boxes = Table([[margin_table, summary_table]], colWidths=[doc.width/2, doc.width/2], style=TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 8)]))
    story.append(boxes); story.append(Spacer(1, 14))
    sig = asset_path("authorized-signature-clean.png") or asset_path("authorized-signature.png")
    stamp = asset_path("dhanlaxmi-stamp-house-hd.png") or asset_path("dhanlaxmi-stamp-pdf.png")
    sign_img = Image(str(sig), width=42*mm, height=12*mm, kind="proportional") if sig else ""
    stamp_img = Image(str(stamp), width=27*mm, height=19*mm, kind="proportional") if stamp else ""
    story.append(Table([[stamp_img, "", sign_img], [Paragraph("", styles["Tiny"]), "", Paragraph("Authorized Signatory", styles["Tiny"])]], colWidths=[35*mm, doc.width-80*mm, 45*mm], style=TableStyle([("ALIGN", (0,0), (0,0), "LEFT"), ("ALIGN", (2,0), (2,0), "CENTER"), ("ALIGN", (2,1), (2,1), "CENTER"), ("LINEABOVE", (2,1), (2,1), .4, colors.HexColor("#9ca3af")), ("VALIGN", (0,0), (-1,-1), "BOTTOM")])) )
    story.append(Spacer(1, 8)); story.append(Paragraph("<b>Notes:</b><br/>1. Brokerage charged as per agreed terms.<br/>2. Payment within T+1 settlement cycle.<br/>3. Computer generated invoice, no physical signature required.", styles["Tiny"]))
    doc.build(story)
    buffer.seek(0)
    return buffer


@app.post("/api/invoices/<int:invoice_id>/generate-pdf")
def generate_pdf(invoice_id):
    with db_conn() as conn:
        row = conn.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,)).fetchone()
        if not row: return jsonify({"error": "Invoice not found"}), 404
        trades = conn.execute("SELECT * FROM trades WHERE invoice_id=? ORDER BY id", (invoice_id,)).fetchall()
    pdf = build_pdf(serialize_invoice(row, trades))
    return send_file(pdf, mimetype="application/pdf", as_attachment=False, download_name=f"invoice-{row['invoice_number']}.pdf")


@app.get("/api/invoices/<int:invoice_id>/pdf")
def view_pdf(invoice_id):
    return generate_pdf(invoice_id)



init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
