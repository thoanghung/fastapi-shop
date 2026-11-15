"""
Generate synthetic e-commerce products (Vietnamese + English) as CSV for PostgreSQL COPY.

Usage:
    python generate_products.py --count 1000000 --out products.csv
    python generate_products.py --count 5000 --out products_5k.csv --seed 7

Only uses the Python standard library. Brands are invented, so no real product data is used.
"""

import argparse
import csv
import json
import random
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Catalog definition: category -> product types
# Each type: vi name, en name, price range (VND), attribute options, features
# ---------------------------------------------------------------------------

COLORS = [
    ("Đen", "Black"), ("Trắng", "White"), ("Xanh navy", "Navy"), ("Xám", "Grey"),
    ("Be", "Beige"), ("Đỏ", "Red"), ("Xanh rêu", "Olive"), ("Hồng", "Pink"),
    ("Nâu", "Brown"), ("Xanh dương", "Blue"),
]
CLOTHING_SIZES = ["S", "M", "L", "XL", "XXL"]
SHOE_SIZES = [str(s) for s in range(36, 45)]
GENDERS = [("nam", "men's"), ("nữ", "women's"), ("unisex", "unisex")]

CATALOG = {
    "Thời trang": [
        {
            "vi": "Áo khoác", "en": "Jacket", "price": (250_000, 1_800_000),
            "variants": [("chống nước", "waterproof"), ("gió", "windbreaker"), ("phao", "puffer"),
                         ("bomber", "bomber"), ("dù", "parachute"), ("nỉ", "fleece")],
            "features": [("chống nước tốt, phù hợp đi mưa", "water-resistant, good for rainy days"),
                         ("giữ ấm, thích hợp đi Đà Lạt, Sa Pa", "keeps you warm for cold trips"),
                         ("nhẹ, gấp gọn bỏ balo", "lightweight and packable"),
                         ("có mũ tháo rời", "detachable hood")],
            "sizes": CLOTHING_SIZES, "gender": True, "color": True,
        },
        {
            "vi": "Áo thun", "en": "T-shirt", "price": (79_000, 450_000),
            "variants": [("cotton", "cotton"), ("cổ tròn", "crew neck"), ("oversize", "oversized"),
                         ("polo", "polo"), ("thể thao", "sports")],
            "features": [("100% cotton thoáng mát", "100% breathable cotton"),
                         ("thấm hút mồ hôi", "sweat-wicking"),
                         ("không nhăn, dễ giặt", "wrinkle-free, easy to wash"),
                         ("form rộng thoải mái", "relaxed fit")],
            "sizes": CLOTHING_SIZES, "gender": True, "color": True,
        },
        {
            "vi": "Quần jean", "en": "Jeans", "price": (199_000, 990_000),
            "variants": [("slim fit", "slim fit"), ("ống suông", "straight leg"),
                         ("ống rộng", "wide leg"), ("rách gối", "ripped")],
            "features": [("vải co giãn 4 chiều", "4-way stretch denim"),
                         ("không phai màu", "colorfast"),
                         ("lưng cao tôn dáng", "high-rise, flattering fit")],
            "sizes": ["28", "29", "30", "31", "32", "33", "34"], "gender": True, "color": True,
        },
        {
            "vi": "Váy", "en": "Dress", "price": (159_000, 1_200_000),
            "variants": [("maxi", "maxi"), ("công sở", "office"), ("hoa nhí", "floral"),
                         ("babydoll", "babydoll"), ("dự tiệc", "party")],
            "features": [("chất voan mềm mại", "soft chiffon"),
                         ("phù hợp đi biển", "great for the beach"),
                         ("thanh lịch đi làm", "elegant for work")],
            "sizes": CLOTHING_SIZES, "gender": False, "color": True,
        },
        {
            "vi": "Giày thể thao", "en": "Sneakers", "price": (299_000, 2_900_000),
            "variants": [("chạy bộ", "running"), ("đi bộ", "walking"), ("tập gym", "training"),
                         ("cổ cao", "high-top"), ("đế bằng", "flat sole")],
            "features": [("đế êm, giảm chấn tốt", "cushioned sole with good shock absorption"),
                         ("thoáng khí", "breathable mesh"),
                         ("chống trơn trượt", "anti-slip outsole"),
                         ("siêu nhẹ", "ultra lightweight")],
            "sizes": SHOE_SIZES, "gender": True, "color": True,
        },
    ],
    "Điện tử": [
        {
            "vi": "Tai nghe", "en": "Headphones", "price": (149_000, 6_500_000),
            "variants": [("bluetooth", "bluetooth"), ("chống ồn", "noise-cancelling"),
                         ("true wireless", "true wireless"), ("gaming", "gaming"), ("thể thao", "sports")],
            "features": [("pin 30 giờ", "30-hour battery"),
                         ("chống ồn chủ động ANC", "active noise cancellation"),
                         ("chống nước IPX5", "IPX5 water resistance"),
                         ("micro đàm thoại rõ", "clear call microphone")],
            "sizes": None, "gender": False, "color": True,
        },
        {
            "vi": "Điện thoại", "en": "Smartphone", "price": (2_490_000, 32_990_000),
            "variants": [("128GB", "128GB"), ("256GB", "256GB"), ("512GB", "512GB")],
            "features": [("camera 50MP", "50MP camera"), ("pin 5000mAh", "5000mAh battery"),
                         ("màn hình AMOLED 120Hz", "120Hz AMOLED display"),
                         ("sạc nhanh 67W", "67W fast charging")],
            "sizes": None, "gender": False, "color": True,
        },
        {
            "vi": "Laptop", "en": "Laptop", "price": (8_990_000, 45_990_000),
            "variants": [("văn phòng", "office"), ("gaming", "gaming"), ("mỏng nhẹ", "ultrabook"),
                         ("đồ họa", "creator")],
            "features": [("RAM 16GB", "16GB RAM"), ("SSD 512GB", "512GB SSD"),
                         ("màn hình 14 inch", "14-inch display"),
                         ("pin 10 tiếng", "10-hour battery"), ("card RTX", "RTX graphics")],
            "sizes": None, "gender": False, "color": False,
        },
        {
            "vi": "Sạc dự phòng", "en": "Power bank", "price": (199_000, 1_490_000),
            "variants": [("10000mAh", "10000mAh"), ("20000mAh", "20000mAh"), ("không dây", "wireless")],
            "features": [("sạc nhanh PD 20W", "20W PD fast charging"),
                         ("2 cổng USB-C", "dual USB-C ports"),
                         ("nhỏ gọn bỏ túi", "pocket-sized")],
            "sizes": None, "gender": False, "color": True,
        },
        {
            "vi": "Đồng hồ thông minh", "en": "Smartwatch", "price": (590_000, 9_990_000),
            "variants": [("thể thao", "sports"), ("GPS", "GPS"), ("màn hình AMOLED", "AMOLED")],
            "features": [("đo nhịp tim, SpO2", "heart rate and SpO2 tracking"),
                         ("chống nước 5ATM", "5ATM water resistance"),
                         ("pin 14 ngày", "14-day battery")],
            "sizes": None, "gender": False, "color": True,
        },
    ],
    "Gia dụng": [
        {
            "vi": "Nồi chiên không dầu", "en": "Air fryer", "price": (790_000, 4_500_000),
            "variants": [("4L", "4L"), ("6L", "6L"), ("8L", "8L"), ("điện tử", "digital")],
            "features": [("tiết kiệm 80% dầu mỡ", "uses 80% less oil"),
                         ("lòng nồi chống dính", "non-stick basket"),
                         ("hẹn giờ thông minh", "smart timer")],
            "sizes": None, "gender": False, "color": False,
        },
        {
            "vi": "Nồi cơm điện", "en": "Rice cooker", "price": (390_000, 3_990_000),
            "variants": [("1.2L", "1.2L"), ("1.8L", "1.8L"), ("cao tần", "induction")],
            "features": [("nấu cơm ngon, giữ ấm 24h", "keeps rice warm for 24 hours"),
                         ("lòng nồi phủ chống dính", "non-stick inner pot"),
                         ("nhiều chế độ nấu", "multiple cooking modes")],
            "sizes": None, "gender": False, "color": False,
        },
        {
            "vi": "Máy xay sinh tố", "en": "Blender", "price": (299_000, 2_490_000),
            "variants": [("cầm tay", "handheld"), ("cối thủy tinh", "glass jar"), ("đa năng", "multi-function")],
            "features": [("công suất 600W", "600W motor"), ("lưỡi dao inox 6 cánh", "6 stainless steel blades"),
                         ("xay đá nhuyễn", "crushes ice")],
            "sizes": None, "gender": False, "color": True,
        },
        {
            "vi": "Quạt điện", "en": "Electric fan", "price": (249_000, 2_990_000),
            "variants": [("đứng", "standing"), ("tích điện", "rechargeable"), ("hơi nước", "mist"),
                         ("không cánh", "bladeless")],
            "features": [("chạy êm", "quiet operation"), ("có remote", "remote control"),
                         ("tiết kiệm điện", "energy saving")],
            "sizes": None, "gender": False, "color": True,
        },
    ],
    "Làm đẹp": [
        {
            "vi": "Kem chống nắng", "en": "Sunscreen", "price": (99_000, 690_000),
            "variants": [("SPF50+", "SPF50+"), ("da dầu", "for oily skin"), ("nâng tông", "tone-up")],
            "features": [("không bết dính", "non-greasy"), ("chống nước", "water-resistant"),
                         ("phù hợp da nhạy cảm", "suitable for sensitive skin")],
            "sizes": ["50ml", "100ml"], "gender": False, "color": False,
        },
        {
            "vi": "Sữa rửa mặt", "en": "Facial cleanser", "price": (79_000, 450_000),
            "variants": [("dịu nhẹ", "gentle"), ("trị mụn", "acne care"), ("tạo bọt", "foaming")],
            "features": [("pH cân bằng", "pH balanced"), ("chiết xuất trà xanh", "green tea extract"),
                         ("không chứa xà phòng", "soap-free")],
            "sizes": ["100ml", "150ml", "200ml"], "gender": False, "color": False,
        },
        {
            "vi": "Son môi", "en": "Lipstick", "price": (89_000, 590_000),
            "variants": [("lì", "matte"), ("bóng", "glossy"), ("dưỡng", "tinted balm")],
            "features": [("lâu trôi", "long-lasting"), ("không khô môi", "non-drying"),
                         ("màu chuẩn", "true-to-shade color")],
            "sizes": None, "gender": False, "color": True,
        },
    ],
    "Thể thao & Du lịch": [
        {
            "vi": "Balo", "en": "Backpack", "price": (199_000, 1_990_000),
            "variants": [("laptop", "laptop"), ("du lịch", "travel"), ("leo núi", "hiking"),
                         ("chống nước", "waterproof")],
            "features": [("ngăn laptop 15.6 inch", "fits a 15.6-inch laptop"),
                         ("vải chống thấm", "water-repellent fabric"),
                         ("quai đeo trợ lực", "ergonomic straps"), ("dung tích 30L", "30L capacity")],
            "sizes": None, "gender": False, "color": True,
        },
        {
            "vi": "Lều cắm trại", "en": "Camping tent", "price": (390_000, 4_990_000),
            "variants": [("2 người", "2-person"), ("4 người", "4-person"), ("tự bung", "pop-up")],
            "features": [("chống mưa", "rainproof"), ("dựng trong 5 phút", "sets up in 5 minutes"),
                         ("thoáng khí 2 lớp", "double-layer ventilation")],
            "sizes": None, "gender": False, "color": True,
        },
        {
            "vi": "Bình giữ nhiệt", "en": "Insulated bottle", "price": (129_000, 890_000),
            "variants": [("500ml", "500ml"), ("750ml", "750ml"), ("1L", "1L")],
            "features": [("giữ lạnh 24h", "keeps cold for 24 hours"), ("inox 304", "304 stainless steel"),
                         ("không chứa BPA", "BPA-free")],
            "sizes": None, "gender": False, "color": True,
        },
        {
            "vi": "Thảm tập yoga", "en": "Yoga mat", "price": (149_000, 1_290_000),
            "variants": [("TPE", "TPE"), ("cao su", "natural rubber"), ("định tuyến", "alignment")],
            "features": [("chống trượt 2 mặt", "non-slip on both sides"), ("dày 6mm", "6mm thick"),
                         ("kèm túi đựng", "comes with a carry bag")],
            "sizes": None, "gender": False, "color": True,
        },
    ],
    "Thực phẩm & Đồ uống": [
        {
            "vi": "Cà phê", "en": "Coffee", "price": (59_000, 650_000),
            "variants": [("rang xay", "ground"), ("hạt", "whole bean"), ("hòa tan", "instant"),
                         ("phin giấy", "drip bag")],
            "features": [("Robusta Buôn Ma Thuột", "Buon Ma Thuot Robusta"),
                         ("Arabica Cầu Đất", "Cau Dat Arabica"),
                         ("rang mộc", "pure roast, no additives"), ("vị đậm", "bold flavor")],
            "sizes": ["250g", "500g", "1kg"], "gender": False, "color": False,
        },
        {
            "vi": "Trà", "en": "Tea", "price": (45_000, 590_000),
            "variants": [("xanh Thái Nguyên", "Thai Nguyen green"), ("ô long", "oolong"),
                         ("thảo mộc", "herbal"), ("túi lọc", "tea bags")],
            "features": [("hương thơm tự nhiên", "natural aroma"), ("thu hoạch thủ công", "hand-picked"),
                         ("đóng gói hút chân không", "vacuum sealed")],
            "sizes": ["100g", "200g", "500g"], "gender": False, "color": False,
        },
    ],
}

# Invented brand names (no real brands)
BRANDS = [
    "Lumora", "Vexa", "Sao Mai", "Kito", "Nava", "Bamboo Lane", "Orivo", "Tâm An", "Zenko",
    "Hanaro", "Mekora", "Phương Nam", "Trivo", "Aurel", "Song Viet", "Kaida", "Nimbo", "Lotus Home",
    "Ruby Lane", "Vinta", "Eclo", "Hoa Sen", "Mirae Vina", "Solix", "Takumi Viet", "Bến Thành Co",
    "Northpeak", "Coralis", "Halo Living", "Indigo Street",
]

SUFFIXES_VI = ["chính hãng", "cao cấp", "2026", "mẫu mới", "bản giới hạn", "phiên bản Pro", "", "", ""]
SUFFIXES_EN = ["", "Pro", "Plus", "2026 Edition", "Lite", "", ""]


def cap(text: str) -> str:
    """Uppercase the first letter only (keeps '1.8L', 'GPS' intact)."""
    return text[:1].upper() + text[1:]


def round_price(value: int) -> int:
    """Round to a retail-looking VND price, e.g. 349,000 or 1,290,000."""
    if value < 1_000_000:
        return max(9_000, (value // 10_000) * 10_000 + 9_000)
    return (value // 100_000) * 100_000 + 90_000


def make_product(rng: random.Random, idx: int, start: datetime):
    category = rng.choice(list(CATALOG))
    ptype = rng.choice(CATALOG[category])
    brand = rng.choice(BRANDS)
    variant_vi, variant_en = rng.choice(ptype["variants"])
    color = rng.choice(COLORS) if ptype["color"] else None
    gender = rng.choice(GENDERS) if ptype["gender"] else None
    size = rng.choice(ptype["sizes"]) if ptype["sizes"] else None
    feats = rng.sample(ptype["features"], k=min(len(ptype["features"]), rng.randint(2, 3)))
    lang = "vi" if rng.random() < 0.7 else "en"

    # Name
    if lang == "vi":
        parts = [ptype["vi"], variant_vi]
        if gender:
            parts.append(gender[0])
        parts.append(brand)
        suffix = rng.choice(SUFFIXES_VI)
        if suffix:
            parts.append(suffix)
        name = " ".join(parts)
        if color:
            name += f" - {color[0]}"
        if size:
            name += f", size {size}" if ptype["gender"] or ptype["vi"] == "Váy" else f", {size}"
    else:
        parts = [brand]
        if gender:
            parts.append(gender[1].capitalize())
        parts += [cap(variant_en), ptype["en"]]
        suffix = rng.choice(SUFFIXES_EN)
        if suffix:
            parts.append(suffix)
        name = " ".join(parts)
        if color:
            name += f" - {color[1]}"
        if size:
            name += f", size {size}" if ptype["gender"] or ptype["en"] == "Dress" else f", {size}"

    # Description
    if lang == "vi":
        feat_text = ", ".join(f[0] for f in feats)
        desc = f"{ptype['vi']} {variant_vi} của {brand}: {feat_text}."
        if color:
            desc += f" Màu {color[0].lower()}."
        desc += rng.choice([
            " Bảo hành 12 tháng.", " Đổi trả trong 7 ngày.", " Giao hàng toàn quốc.",
            " Hàng có sẵn, giao nhanh 2h tại TP.HCM và Hà Nội.", "",
        ])
    else:
        feat_text = ", ".join(f[1] for f in feats)
        desc = f"{cap(variant_en)} {ptype['en'].lower()} by {brand}: {feat_text}."
        if color:
            desc += f" Color: {color[1].lower()}."
        desc += rng.choice([
            " 12-month warranty.", " 7-day free returns.", " Ships nationwide.", "",
        ])

    lo, hi = ptype["price"]
    price = round_price(int(rng.triangular(lo, hi, lo + (hi - lo) * 0.3)))
    stock = 0 if rng.random() < 0.08 else rng.randint(1, 500)
    rating = round(rng.triangular(3.0, 5.0, 4.6), 1)
    created_at = start + timedelta(seconds=rng.randint(0, 365 * 24 * 3600))

    attributes = {"variant": variant_en, "language": lang}
    if color:
        attributes["color"] = color[1]
    if gender:
        attributes["gender"] = gender[1].rstrip("'s") if gender[1] != "unisex" else "unisex"
    if size:
        attributes["size"] = size

    # Index-based suffix guarantees unique SKUs; ASCII-only prefix
    prefix = "".join(c for c in brand.upper() if c.isascii() and c.isalpha())[:3] or "GEN"
    sku = f"{prefix}-{idx:07d}"

    return [
        sku, name, category, ptype["en"], brand, price, stock, rating, desc,
        json.dumps(attributes, ensure_ascii=False), created_at.isoformat(sep=" ", timespec="seconds"),
    ]


HEADER = ["sku", "name", "category", "product_type", "brand", "price", "stock", "rating",
          "description", "attributes", "created_at"]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--count", type=int, default=1_000_000)
    parser.add_argument("--out", default="products.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    start = datetime(2025, 11, 1)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)
        for i in range(args.count):
            writer.writerow(make_product(rng, i, start))
            if (i + 1) % 100_000 == 0:
                print(f"  {i + 1:,} rows")
    print(f"Wrote {args.count:,} products to {args.out}")


if __name__ == "__main__":
    main()
