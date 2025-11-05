import re

def normalize_arrows(s):
    if not s:
        return ""
    return (
        s.replace("â", "→")
        .replace("â†’", "→")
        .replace("->", "→")
        .replace("â", "↑")
        .replace("â", "↓")
        .strip()
    )

def classify_from_heading(text):
    t = (text or "").lower()
    if any(k in t for k in ["debilit", "nerf", "nerfs", "⬇"]):
        return "debilitación"
    if any(k in t for k in ["mejor", "buff", "buffs", "⬆", "potenci"]):
        return "mejora"
    if any(k in t for k in ["ajust", "cambio", "balance"]):
        return "ajuste"
    return None

def classify_from_text(text):
    t = normalize_arrows((text or "").lower())
    match = re.search(r"\(([+\-]\s*\d+%?)\)", t)
    if match:
        if match.group(1).strip().startswith("-"):
            return "debilitación"
        if match.group(1).strip().startswith("+"):
            return "mejora"

    arrow = re.search(r"([0-9]+(?:[.,][0-9]+)?)\s*[→]\s*([0-9]+(?:[.,][0-9]+)?)", t)
    if arrow:
        try:
            a = float(arrow.group(1).replace(",", "."))
            b = float(arrow.group(2).replace(",", "."))
            if b < a:
                return "debilitación"
            if b > a:
                return "mejora"
        except:
            pass

    nerf_keys = ["reduce", "reduc", "disminu", "decrease", "nerf", "lower"]
    buff_keys = ["increase", "aument", "mejor", "buff", "boost", "raise"]
    if any(k in t for k in nerf_keys):
        return "debilitación"
    if any(k in t for k in buff_keys):
        return "mejora"
    return "otro"
