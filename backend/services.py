# services.py
import os
import sqlite3
import shutil
import time
from typing import List, Dict, Any
import numpy as np

# Import ML components
from seed_data import WARDROBE, CATALOG, PURCHASE_HISTORY, OCCASIONS
from models_ml import Word2VecSimulator, BPRRecommender

# Initialize ML simulators
w2v = Word2VecSimulator()
bpr = BPRRecommender()

DB_PATH = "wardrobe_planner.db"
UPLOAD_DIR = os.path.join("..", "frontend", "uploads")

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ----------------------------------------------------
# 1. Database Service (Mocking Supabase PostgreSQL)
# ----------------------------------------------------
class SupabaseMockService:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        
        # Create Wardrobe table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wardrobe (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                color TEXT NOT NULL,
                color_hex TEXT NOT NULL,
                brand TEXT,
                purchase_date TEXT,
                purchase_price INTEGER,
                occasion_tags TEXT,
                description TEXT,
                sleeve_length TEXT,
                neckline TEXT,
                pattern TEXT,
                fabric TEXT,
                silhouette TEXT,
                image_url TEXT
            )
        """)
        
        # Create Catalog table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS catalog (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                color TEXT NOT NULL,
                color_hex TEXT NOT NULL,
                price INTEGER NOT NULL,
                brand TEXT NOT NULL,
                occasion_tags TEXT NOT NULL,
                description TEXT,
                sleeve_length TEXT,
                neckline TEXT,
                pattern TEXT,
                fabric TEXT,
                silhouette TEXT,
                image_url TEXT
            )
        """)
        
        # Create History table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchase_history (
                item_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                purchase_date TEXT NOT NULL,
                price INTEGER NOT NULL,
                brand TEXT NOT NULL,
                color TEXT NOT NULL
            )
        """)

        # Create Saved Outfits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_outfits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_ids TEXT NOT NULL,
                occasion TEXT NOT NULL,
                compatibility_score REAL NOT NULL,
                style_explanation TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        
        # Seed if empty
        if not self.get_wardrobe():
            self._seed_data()

    def _seed_data(self):
        cursor = self.conn.cursor()
        
        # Seed Wardrobe
        for item in WARDROBE:
            cursor.execute("""
                INSERT OR REPLACE INTO wardrobe VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                item["id"], item["name"], item["category"], item["color"], item["color_hex"],
                item.get("brand"), item.get("purchase_date"), item.get("purchase_price"),
                ",".join(item.get("occasion_tags", [])), item.get("description"),
                item.get("sleeve_length"), item.get("neckline"), item.get("pattern"),
                item.get("fabric"), item.get("silhouette"), item.get("image_url")
            ))
            
        # Seed Catalog
        for item in CATALOG:
            cursor.execute("""
                INSERT OR REPLACE INTO catalog VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                item["id"], item["name"], item["category"], item["color"], item["color_hex"],
                item["price"], item["brand"], ",".join(item.get("occasion_tags", [])),
                item.get("description"), item.get("sleeve_length"), item.get("neckline"),
                item.get("pattern"), item.get("fabric"), item.get("silhouette"), item.get("image_url")
            ))
            
        # Seed History
        for hist in PURCHASE_HISTORY:
            cursor.execute("""
                INSERT OR REPLACE INTO purchase_history VALUES (
                    ?, ?, ?, ?, ?, ?, ?
                )
            """, (
                hist["item_id"], hist["name"], hist["category"], hist["purchase_date"],
                hist["price"], hist["brand"], hist["color"]
            ))
            
        self.conn.commit()

    def get_wardrobe(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM wardrobe")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["occasion_tags"] = d["occasion_tags"].split(",") if d["occasion_tags"] else []
            result.append(d)
        return result

    def add_to_wardrobe(self, item: Dict):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO wardrobe VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            item["id"], item["name"], item["category"], item["color"], item["color_hex"],
            item.get("brand"), item.get("purchase_date"), item.get("purchase_price"),
            ",".join(item.get("occasion_tags", [])), item.get("description"),
            item.get("sleeve_length"), item.get("neckline"), item.get("pattern"),
            item.get("fabric"), item.get("silhouette"), item.get("image_url")
        ))
        self.conn.commit()

    def get_catalog(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM catalog")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["occasion_tags"] = d["occasion_tags"].split(",") if d["occasion_tags"] else []
            result.append(d)
        return result

    def get_purchase_history(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM purchase_history")
        return [dict(r) for r in cursor.fetchall()]

    def save_outfit(self, item_ids: List[str], occasion: str, score: float, explanation: str):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO saved_outfits (item_ids, occasion, compatibility_score, style_explanation)
            VALUES (?, ?, ?, ?)
        """, (",".join(item_ids), occasion, score, explanation))
        self.conn.commit()
        return cursor.lastrowid

    def get_saved_outfits(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM saved_outfits ORDER BY created_at DESC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["item_ids"] = d["item_ids"].split(",")
            result.append(d)
        return result


# ----------------------------------------------------
# 2. Vector DB Service (Mocking Pinecone)
# ----------------------------------------------------
class PineconeMockService:
    """Stores high-dimensional embeddings and performs quick similarity lookup."""
    def __init__(self, db_service: SupabaseMockService):
        self.db = db_service
        self.index = {} # Maps item_id -> list of float vector
        self._build_index()

    def _build_index(self):
        # Index all wardrobe and catalog items
        items = self.db.get_wardrobe() + self.db.get_catalog()
        for item in items:
            text = f"{item['name']} {item['color']} {item['category']} {item.get('description', '')}"
            vector = w2v.get_sentence_embedding(text)
            self.index[item["id"]] = vector

    def add_to_index(self, item_id: str, text: str):
        self.index[item_id] = w2v.get_sentence_embedding(text)

    def query_nearest(self, query_text: str, category: str = None, top_k: int = 3) -> List[Dict]:
        """Finds closest items in the vector database matching the description."""
        query_vector = w2v.get_sentence_embedding(query_text)
        
        candidates = []
        all_items = self.db.get_wardrobe() + self.db.get_catalog()
        
        # Filter duplicates by ID
        seen_ids = set()
        unique_items = []
        for item in all_items:
            if item["id"] not in seen_ids:
                seen_ids.add(item["id"])
                unique_items.append(item)

        for item in unique_items:
            # Check category filter
            if category and item["category"] != category:
                continue
                
            item_vec = self.index.get(item["id"])
            if item_vec is None:
                text = f"{item['name']} {item['color']} {item['category']} {item.get('description', '')}"
                item_vec = w2v.get_sentence_embedding(text)
                self.index[item["id"]] = item_vec
                
            similarity = w2v.cosine_similarity(query_vector, item_vec)
            candidates.append((item, similarity))
            
        # Sort by similarity descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in candidates[:top_k]]


# ----------------------------------------------------
# 3. Cache Service (Mocking Redis Cache)
# ----------------------------------------------------
class RedisMockService:
    def __init__(self):
        self.cache = {}
        self.ttl = {}

    def get(self, key: str) -> Any:
        # Check if expired
        if key in self.ttl and time.time() > self.ttl[key]:
            del self.cache[key]
            del self.ttl[key]
            return None
        return self.cache.get(key)

    def set(self, key: str, value: Any, expire_seconds: int = 300):
        self.cache[key] = value
        self.ttl[key] = time.time() + expire_seconds


# ----------------------------------------------------
# 4. Image CDN Service (Mocking Cloudinary)
# ----------------------------------------------------
class CloudinaryMockService:
    """Saves uploaded files locally, compresses them, and provides a web-accessible URL."""
    def upload_image(self, file_bytes: bytes, filename: str) -> str:
        # Ensure name is unique to avoid collision
        timestamp = int(time.time())
        clean_name = f"{timestamp}_{filename.replace(' ', '_')}"
        save_path = os.path.join(UPLOAD_DIR, clean_name)
        
        # Write file
        with open(save_path, "wb") as f:
            f.write(file_bytes)
            
        # Optimize image using Pillow (simulate Cloudinary CDN optimization)
        try:
            from PIL import Image
            img = Image.open(save_path)
            # Resize if very large
            if img.width > 800 or img.height > 800:
                img.thumbnail((800, 800))
            # Save compressed
            img.save(save_path, quality=80, optimize=True)
        except Exception as e:
            print("Pillow optimization bypassed:", e)
            
        # Return the public URL that frontend can load (relative to server root)
        return f"/uploads/{clean_name}"


# ----------------------------------------------------
# 5. Gemini AI Service (Language Generation)
# ----------------------------------------------------
class GeminiAIService:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.has_client = False
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.has_client = True
                print("Gemini API configured successfully!")
            except Exception as e:
                print("Gemini client initialization failed, falling back to local style agent:", e)

    def generate_style_explanation(self, items: List[Dict], occasion: str, score: float) -> str:
        """Generates style reasoning using Gemini API or a high-fidelity local catalog model."""
        item_names = ", ".join([f"{item['color']} {item['category']} ({item['name']})" for item in items])
        
        if self.has_client:
            prompt = f"""
            You are a personal fashion stylist for Myntra For Bharat.
            The user wants to wear this outfit: {item_names}
            Occasion: {occasion}
            Compatibility Score: {score}/100.
            
            Write a short, engaging style explanation (3-4 sentences max) explaining WHY this combination works.
            Highlight the color harmony, layering, and occasion suitability in a warm, encouraging tone.
            Use names that real Indian users appreciate (e.g. kurtis, palazzos, jhumkas, dupatta).
            Avoid generic jargon, speak with fashion authority but in simple, value-conscious language.
            """
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print("Gemini API call failed, using local model:", e)
        
        # HIGH-FIDELITY LOCAL RULE-BASED FALLBACK SYSTEM
        # Builds custom fashion sentences depending on what items are selected
        kurta = next((i for i in items if i["category"] == "kurta"), None)
        bottom = next((i for i in items if i["category"] == "bottom"), None)
        dupatta = next((i for i in items if i["category"] == "dupatta"), None)
        footwear = next((i for i in items if i["category"] == "footwear"), None)
        accessory = next((i for i in items if i["category"] == "accessory"), None)

        sentences = []
        
        if kurta and bottom:
            k_col = kurta["color"]
            b_col = bottom["color"]
            if k_col == "Ivory" and b_col == "Mustard":
                sentences.append("The Chikankari Ivory kurta acts as a elegant, neutral base, allowing the warm Mustard palazzo pants to stand out beautifully.")
            elif k_col == "Indigo" and b_col == "White":
                sentences.append("The Indigo A-Line kurti pairs beautifully with the White palazzo, invoking a classic block-printed Indigo aesthetic that is perfect for professional spaces.")
            elif k_col == "Mustard" and b_col == "White":
                sentences.append("The Mustard Yellow kurta combined with White palazzo creates a bright, cheerful contrast suitable for daytime festivities.")
            else:
                sentences.append(f"Pairing the {k_col} {kurta['category']} with the {b_col} {bottom['silhouette'] or 'bottom'} creates a balanced and stylish silhouette.")

        if dupatta:
            d_col = dupatta["color"]
            if kurta:
                k_col = kurta["color"]
                if d_col == "Red" and k_col == "Ivory":
                    sentences.append("The Red Banarasi Silk dupatta adds immediate festive gravity, draping beautifully and giving the Ivory kurta a royal, celebration-ready look.")
                elif d_col == "Mustard" and k_col == "Ivory":
                    sentences.append("Draping the Mustard dupatta matching the palazzos ties the whole ensemble together seamlessly, creating a clean, coordinated look.")
                else:
                    sentences.append(f"The {d_col} dupatta injects texture and a graceful layer, elevating the outfit's ethnic elegance.")
                    
        if accessory:
            acc_col = accessory["color"]
            if acc_col == "Gold":
                sentences.append("The gold earrings frame the face beautifully, picking up the warm tones and adding a touch of traditional sparkle.")
            elif acc_col == "Silver":
                sentences.append("Oxidized silver earrings give the look a bohemian, artisanal vibe that is perfect for regular wear or college.")
            else:
                sentences.append(f"The {accessory['name']} accessorizes the look beautifully without cluttering the neckline.")

        if footwear:
            sentences.append(f"Finishing the look with {footwear['color']} {footwear['category']} coordinates perfectly, keeping it comfortable and culturally rooted.")

        if occasion == "festive":
            sentences.append("Overall, this combination has a vibrant traditional charm that is highly suited for Diwali or puja celebrations.")
        elif occasion == "wedding":
            sentences.append("This is an elegant choice for pre-wedding celebrations like Haldi or Mehendi, balancing festive weight and ease of movement.")
        elif occasion == "office":
            sentences.append("A smart, sophisticated fusion look that keeps you comfortable and professional all day.")
        else:
            sentences.append("A clean, comfortable daily outfit that looks put-together with minimal effort.")

        return " ".join(sentences)

    def generate_buy_reasoning(self, recommended_item: Dict, owned_item: Dict, event: str) -> str:
        """Explains why a catalog buy recommendation is smart based on an owned item."""
        if self.api_key and self.has_client:
            prompt = f"""
            You are a personal shopper for Myntra For Bharat.
            Write a one-sentence personal shopping recommendation explaining why a user should buy the '{recommended_item['name']}' ({recommended_item['color']} {recommended_item['category']})
            to pair with the '{owned_item['name']}' ({owned_item['color']} {owned_item['category']}) they already own, which was purchased in {owned_item.get('purchase_date', 'March')}.
            Occasion: {event}
            Be persuasive, friendly, value-first, and explain how it expands their wardrobe options. E.g. "This mustard dupatta pairs with the ivory kurta you bought in March and adds festive contrast for Diwali."
            """
            try:
                response = self.model.generate_content(prompt)
                return response.text.strip()
            except Exception:
                pass
                
        # Fallback local logic
        rec_name = recommended_item["name"]
        own_name = owned_item["name"]
        rec_cat = recommended_item["category"]
        own_cat = owned_item["category"]
        rec_col = recommended_item["color"]
        own_col = owned_item["color"]
        date = owned_item.get("purchase_date", "recent months")
        
        if rec_cat == "dupatta" and own_cat == "kurta":
            return f"This {rec_col} dupatta pairs perfectly with the {own_col} kurta you bought in {date}, adding gorgeous traditional contrast for {event} celebrations."
        elif rec_cat == "bottom" and own_cat == "kurta":
            return f"These {rec_col} bottom pants will expand your styling possibilities, matching the {own_col} kurta from {date} to form a comfortable and chic {event} outfit."
        elif rec_cat == "accessory" and own_cat == "kurta":
            return f"These {rec_col} earrings pick up the design details of your {own_col} kurta bought in {date}, completing your ethnic look for {event}."
        elif rec_cat == "footwear" and own_cat == "bottom":
            return f"These {rec_col} footwear flats complement the {own_col} pants you purchased in {date}, making a cohesive look for {event}."
        
        return f"This {rec_col} {rec_cat} is a versatile wardrobe addition that coordinates beautifully with the {own_col} {own_cat} you bought in {date} for a complete {event} look."
