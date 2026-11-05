"""Draw fictional transfer receipts that resemble popular Nigerian wallet UIs
without copying any real logo, wordmark, or trademark.

Styles (color and layout only):
  horizonpay   — green wallet UI, inspired by OPay-like receipts
  gulftrust    — orange bank UI, inspired by GTBank-like receipts
  harbormfb    — purple MFB UI, inspired by Kuda-like receipts
  pointbridge  — teal agent UI, inspired by Moniepoint-like receipts

Every image carries a fictional disclaimer. Do not add real brand assets.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

DISCLAIMER = (
    "FICTIONAL RECEIPT — generated for an AI evaluation. "
    "Not a real bank document. No real logos, accounts, or customers."
)

STYLES: dict[str, dict[str, Any]] = {
    "horizonpay": {
        "brand": "HorizonPay",
        "subtitle": "Wallet transfer",
        "header": (18, 140, 78),
        "accent": (18, 140, 78),
        "bg": (245, 252, 247),
    },
    "gulftrust": {
        "brand": "GulfTrust Bank",
        "subtitle": "Internet banking",
        "header": (230, 126, 34),
        "accent": (192, 86, 12),
        "bg": (255, 249, 243),
    },
    "harbormfb": {
        "brand": "Harbor MFB",
        "subtitle": "Mobile banking",
        "header": (102, 51, 153),
        "accent": (88, 40, 140),
        "bg": (248, 244, 252),
    },
    "pointbridge": {
        "brand": "PointBridge",
        "subtitle": "Agent transfer",
        "header": (10, 130, 140),
        "accent": (8, 110, 118),
        "bg": (242, 251, 252),
    },
}


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    # DejaVu is present on this Linux box and on most Windows Python installs.
    candidates = [
        "C:\\\\Windows\\\\Fonts\\\\arialbd.ttf" if bold else "C:\\\\Windows\\\\Fonts\\\\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fmt_naira(amount: int) -> str:
    return f"NGN {amount:,}"


def generate_receipt(spec: dict[str, Any], dest: Path) -> Path:
    """Render one receipt PNG from a task image_spec and write it to dest."""
    style_key = spec.get("style", "horizonpay")
    style = STYLES[style_key]
    width, height = 720, 1120
    img = Image.new("RGB", (width, height), style["bg"])
    draw = ImageDraw.Draw(img)

    draw.rectangle([(0, 0), (width, 170)], fill=style["header"])
    draw.text((40, 36), style["brand"], fill="white", font=_font(36, bold=True))
    draw.text((40, 86), style["subtitle"], fill=(230, 230, 230), font=_font(20))
    draw.text((40, 122), spec.get("title", "Transfer receipt"), fill="white", font=_font(22, bold=True))

    # Status pill
    status = str(spec.get("status", "SUCCESS")).upper()
    pill_color = (18, 140, 78) if status == "SUCCESS" else (180, 120, 20) if status == "PENDING" else (170, 40, 40)
    draw.rounded_rectangle([(40, 200), (280, 250)], radius=18, fill=pill_color)
    draw.text((58, 212), status, fill="white", font=_font(22, bold=True))

    amount = int(spec["display_amount_ngn"])
    draw.text((40, 280), "Amount", fill=(90, 90, 90), font=_font(18))
    draw.text((40, 312), _fmt_naira(amount), fill=(20, 20, 20), font=_font(44, bold=True))

    rows = [
        ("Sender", spec.get("payer_name", "")),
        ("Beneficiary", spec.get("beneficiary_name", "")),
        ("Beneficiary bank", spec.get("beneficiary_bank", "")),
        ("Reference / session ID", spec.get("reference", "")),
        ("Date / time", spec.get("timestamp", "")),
        ("Narration", spec.get("narration", "")),
    ]
    y = 400
    for label, value in rows:
        draw.text((40, y), label, fill=(110, 110, 110), font=_font(16))
        draw.text((40, y + 26), str(value), fill=(25, 25, 25), font=_font(22, bold=True))
        y += 78

    extras = spec.get("extras") or []
    for extra in extras:
        draw.text((40, y), str(extra), fill=(80, 40, 40), font=_font(16))
        y += 28

    # Footer disclaimer band
    draw.rectangle([(0, height - 140), (width, height)], fill=(30, 30, 30))
    # word-wrap disclaimer
    words = DISCLAIMER.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if len(trial) > 52:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    fy = height - 120
    for line in lines:
        draw.text((36, fy), line, fill=(230, 230, 230), font=_font(16))
        fy += 24

    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest)
    return dest


def write_task_receipts(tasks: list[dict[str, Any]], assets_dir: Path) -> list[Path]:
    written: list[Path] = []
    for task in tasks:
        spec = task.get("image_spec")
        if not spec:
            continue
        path = assets_dir / f"{task['id']}.png"
        write_path = generate_receipt(spec, path)
        written.append(write_path)
    return written
