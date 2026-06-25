# seed_data.py
# Sample data for Myntra For Bharat — Wardrobe Planner

# Occasions supported by the system
OCCASIONS = {
    "festive": {
        "name": "Festive Celebrations (Diwali, Eid, Puja)",
        "vibe": "Vibrant, traditional, elegant, and celebratory.",
        "preferred_colors": ["Mustard", "Red", "Emerald Green", "Royal Blue", "Gold", "Ivory", "Maroon"],
        "formula": ["kurta", "bottom", "dupatta", "footwear", "accessory"]
    },
    "wedding": {
        "name": "Wedding Functions (Haldi, Mehendi, Sangeet, Reception)",
        "vibe": "Heavy ethnic, rich fabrics, and high embellishment.",
        "preferred_colors": ["Yellow", "Pink", "Red", "Gold", "Orange", "Emerald Green"],
        "formula": ["kurta", "bottom", "dupatta", "footwear", "accessory"]
    },
    "office": {
        "name": "Office & Smart Casuals",
        "vibe": "Sober, comfortable, fusion, and structured.",
        "preferred_colors": ["Ivory", "Indigo", "Beige", "Olive", "Black", "Grey", "Blue"],
        "formula": ["kurta", "bottom", "footwear", "accessory"]
    },
    "daily": {
        "name": "Daily Wear & Market Runs",
        "vibe": "Breathable, casual, minimalist, and practical.",
        "preferred_colors": ["Blue", "White", "Peach", "Mint Green", "Beige", "Pink"],
        "formula": ["kurta", "bottom", "footwear"]
    }
}

# The Myntra Catalog of items available for buying
CATALOG = [
    # Kurtas
    {
        "id": "cat_kurta_1",
        "name": "Anouk Mustard Embroidered Kurta",
        "category": "kurta",
        "color": "Mustard",
        "color_hex": "#E1AD01",
        "price": 799,
        "brand": "Anouk",
        "occasion_tags": ["festive", "wedding"],
        "description": "A straight cotton kurta in deep mustard yellow, featuring delicate gold zari embroidery around a keyhole neckline. Perfect for festive gatherings.",
        "sleeve_length": "3/4 sleeve",
        "neckline": "keyhole",
        "pattern": "embroidered",
        "fabric": "cotton",
        "image_url": "https://images.unsplash.com/photo-1608748010899-18f300247112?w=400&q=80"
    },
    {
        "id": "cat_kurta_2",
        "name": "Libas Ruby Red Anarkali Kurta",
        "category": "kurta",
        "color": "Red",
        "color_hex": "#990012",
        "price": 1499,
        "brand": "Libas",
        "occasion_tags": ["festive", "wedding"],
        "description": "Flared Anarkali kurta in premium viscose rayon, detailed with Gota Patti borders along the hem. Vibrant ruby red suitable for weddings and puja.",
        "sleeve_length": "long sleeve",
        "neckline": "round",
        "pattern": "solid with border",
        "fabric": "rayon",
        "image_url": "https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=400&q=80"
    },
    {
        "id": "cat_kurta_3",
        "name": "Roadster Indigo Printed A-Line Kurti",
        "category": "kurta",
        "color": "Indigo",
        "color_hex": "#1E3060",
        "price": 499,
        "brand": "Roadster",
        "occasion_tags": ["office", "daily"],
        "description": "A lightweight cotton A-line short kurti in indigo blue, hand-block print pattern with a round neck and three-quarter sleeves.",
        "sleeve_length": "3/4 sleeve",
        "neckline": "round",
        "pattern": "block-print",
        "fabric": "cotton",
        "image_url": "https://images.unsplash.com/photo-1610030469668-93535c17b6b3?w=400&q=80"
    },
    # Bottoms
    {
        "id": "cat_bottom_1",
        "name": "W White Cotton Palazzo Pants",
        "category": "bottom",
        "color": "White",
        "color_hex": "#F8F9FA",
        "price": 699,
        "brand": "W",
        "occasion_tags": ["daily", "office", "festive"],
        "description": "Wide-leg white cotton palazzos with delicate self-design lace trim at the hem. Highly breathable and pairs with any ethnic top.",
        "silhouette": "palazzo",
        "fabric": "cotton",
        "image_url": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&q=80"
    },
    {
        "id": "cat_bottom_2",
        "name": "Sangria Olive Patiala Salwar",
        "category": "bottom",
        "color": "Olive",
        "color_hex": "#556B2F",
        "price": 549,
        "brand": "Sangria",
        "occasion_tags": ["festive", "daily"],
        "description": "Pleated olive green Patiala salwar in soft cotton. Provides a traditional silhouette when paired with short kurtis or straight kurtas.",
        "silhouette": "patiala",
        "fabric": "cotton",
        "image_url": "https://images.unsplash.com/photo-1509551388413-e18d0ac5d495?w=400&q=80"
    },
    # Dupattas
    {
        "id": "cat_dupatta_1",
        "name": "Anouk Red Banarasi Silk Dupatta",
        "category": "dupatta",
        "color": "Red",
        "color_hex": "#B22222",
        "price": 899,
        "brand": "Anouk",
        "occasion_tags": ["festive", "wedding"],
        "description": "Rich Banarasi silk woven dupatta in scarlet red with intricate gold zari brocade motifs and tassel details. Adds immediate festive weight to simple kurtas.",
        "fabric": "silk",
        "image_url": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=400&q=80"
    },
    {
        "id": "cat_dupatta_2",
        "name": "Sangria Multicolored Bandhani Dupatta",
        "category": "dupatta",
        "color": "Multicolor",
        "color_hex": "linear-gradient(45deg, #FF5733, #FFC300, #C70039)",
        "price": 399,
        "brand": "Sangria",
        "occasion_tags": ["festive", "daily"],
        "description": "Tie-dye Bandhani art silk dupatta in traditional Rajasthani patterns featuring yellow, pink, and orange crushed textures with gold Gota laces.",
        "fabric": "art-silk",
        "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400&q=80"
    },
    # Footwear
    {
        "id": "cat_footwear_1",
        "name": "House of Pataudi Tan Handcrafted Juttis",
        "category": "footwear",
        "color": "Tan",
        "color_hex": "#B87333",
        "price": 1199,
        "brand": "House of Pataudi",
        "occasion_tags": ["festive", "wedding", "office"],
        "description": "Genuine leather ethnic juttis featuring hand-embroidered dabka work and comfortable cushioned sole. Perfect companion for traditional wear.",
        "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400&q=80"
    },
    {
        "id": "cat_footwear_2",
        "name": "Catwalk Black Embellished Block Heels",
        "category": "footwear",
        "color": "Black",
        "color_hex": "#1A1A1A",
        "price": 1599,
        "brand": "Catwalk",
        "occasion_tags": ["wedding", "office"],
        "description": "Slip-on block heels with black velvet upper and golden bead embellishments, comfortable for long events and pairs well with fusion wear.",
        "image_url": "https://images.unsplash.com/photo-1596702990263-94c6530669b3?w=400&q=80"
    },
    # Accessories
    {
        "id": "cat_accessory_1",
        "name": "Rubans Gold-Plated Ethnic Jhumkas",
        "category": "accessory",
        "color": "Gold",
        "color_hex": "#FFD700",
        "price": 399,
        "brand": "Rubans",
        "occasion_tags": ["festive", "wedding"],
        "description": "Traditional gold-plated bells with tiny pearl hangings and detailed floral carving. Adds a classic touch to Indian wear.",
        "image_url": "https://images.unsplash.com/photo-1535632066927-ab7c9ab60908?w=400&q=80"
    },
    {
        "id": "cat_accessory_2",
        "name": "Voylla Silver-Plated Oxidized Earrings",
        "category": "accessory",
        "color": "Silver",
        "color_hex": "#C0C0C0",
        "price": 299,
        "brand": "Voylla",
        "occasion_tags": ["office", "daily", "festive"],
        "description": "Boho-chic tribal style oxidized silver drop earrings with blue enamel beads and delicate ghungroos. Ideal for pairing with indigo or black outfits.",
        "image_url": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=400&q=80"
    },
    {
        "id": "cat_accessory_3",
        "name": "Baggit Jute Handcrafted Tote Bag",
        "category": "accessory",
        "color": "Beige",
        "color_hex": "#D2B48C",
        "price": 899,
        "brand": "Baggit",
        "occasion_tags": ["office", "daily"],
        "description": "Eco-friendly structured jute tote bag with brown vegan leather straps and spacious compartments, matching fusion and daily styles.",
        "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=400&q=80"
    }
]

# The user's active Wardrobe (items they already own)
WARDROBE = [
    {
        "id": "wardrobe_1",
        "name": "Myntra Brand Ivory Chikankari Kurta",
        "category": "kurta",
        "color": "Ivory",
        "color_hex": "#FFFFF0",
        "brand": "Anouk",
        "purchase_date": "March 2026",
        "purchase_price": 850,
        "occasion_tags": ["festive", "office", "daily"],
        "description": "A beautiful Georgette straight kurta in soft ivory cream, featuring extensive shadow-work Chikankari hand embroidery and internal lining.",
        "sleeve_length": "3/4 sleeve",
        "neckline": "round",
        "pattern": "embroidered",
        "fabric": "georgette",
        "image_url": "https://images.unsplash.com/photo-1583391265517-35bbadd0120a?w=400&q=80"
    },
    {
        "id": "wardrobe_2",
        "name": "Roadster Deep Blue Ankle-Length Jeans",
        "category": "bottom",
        "color": "Blue",
        "color_hex": "#2B3E5C",
        "brand": "Roadster",
        "purchase_date": "December 2025",
        "purchase_price": 999,
        "occasion_tags": ["office", "daily"],
        "description": "High-rise dark blue stretch denim jeans, ankle-length, slim fit. Versatile basic that pairs with both western tops and ethnic kurtis.",
        "silhouette": "slim-fit",
        "fabric": "denim",
        "image_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=400&q=80"
    },
    {
        "id": "wardrobe_3",
        "name": "W Mustard Cotton Palazzo Pants",
        "category": "bottom",
        "color": "Mustard",
        "color_hex": "#D4AF37",
        "brand": "W",
        "purchase_date": "January 2026",
        "purchase_price": 750,
        "occasion_tags": ["festive", "office", "daily"],
        "description": "Flared cropped palazzo pants in premium cotton, deep marigold mustard color, with elasticated back waist for all-day comfort.",
        "silhouette": "palazzo",
        "fabric": "cotton",
        "image_url": "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&q=80"
    },
    {
        "id": "wardrobe_4",
        "name": "Golden Zari Border Chiffon Dupatta",
        "category": "dupatta",
        "color": "Mustard",
        "color_hex": "#DAA520",
        "brand": "Local Craft",
        "purchase_date": "March 2026",
        "purchase_price": 250,
        "occasion_tags": ["festive"],
        "description": "A light flowing georgette dupatta in golden-mustard shade with a subtle gold zari lace lining the borders.",
        "fabric": "chiffon",
        "image_url": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=400&q=80"
    },
    {
        "id": "wardrobe_5",
        "name": "Handmade Kolhapuri Flat Leather Chappals",
        "category": "footwear",
        "color": "Tan",
        "color_hex": "#CD853F",
        "brand": "Crafts of India",
        "purchase_date": "February 2026",
        "purchase_price": 450,
        "occasion_tags": ["daily", "office", "festive"],
        "description": "Traditional tan-colored flat Kolhapuris made from genuine leather with punch-hole details and braids. Very comfortable for walking.",
        "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=400&q=80"
    }
]

# Purchase history list mapping items bought in the past 12 months
PURCHASE_HISTORY = [
    {
        "item_id": "wardrobe_1",
        "name": "Myntra Brand Ivory Chikankari Kurta",
        "category": "kurta",
        "purchase_date": "March 2026",
        "price": 850,
        "brand": "Anouk",
        "color": "Ivory"
    },
    {
        "item_id": "wardrobe_2",
        "name": "Roadster Deep Blue Ankle-Length Jeans",
        "category": "bottom",
        "purchase_date": "December 2025",
        "price": 999,
        "brand": "Roadster",
        "color": "Blue"
    },
    {
        "item_id": "wardrobe_3",
        "name": "W Mustard Cotton Palazzo Pants",
        "category": "bottom",
        "purchase_date": "January 2026",
        "price": 750,
        "brand": "W",
        "color": "Mustard"
    },
    {
        "item_id": "wardrobe_4",
        "name": "Golden Zari Border Chiffon Dupatta",
        "category": "dupatta",
        "purchase_date": "March 2026",
        "price": 250,
        "brand": "Local Craft",
        "color": "Mustard"
    },
    {
        "item_id": "wardrobe_5",
        "name": "Handmade Kolhapuri Flat Leather Chappals",
        "category": "footwear",
        "purchase_date": "February 2026",
        "price": 450,
        "brand": "Crafts of India",
        "color": "Tan"
    }
]
