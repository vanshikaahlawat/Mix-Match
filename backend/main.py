# main.py
import os
import uuid
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import local services and models
from services import (
    SupabaseMockService,
    PineconeMockService,
    RedisMockService,
    CloudinaryMockService,
    GeminiAIService,
    bpr,
    UPLOAD_DIR
)
from models_ml import classify_clothing_attributes

app = FastAPI(title="Myntra For Bharat — Wardrobe Planner API")

# Configure CORS so any local frontend can access it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Services
db = SupabaseMockService()
vector_db = PineconeMockService(db)
cache = RedisMockService()
cloudinary = CloudinaryMockService()
gemini = GeminiAIService()

# ----------------------------------------------------
# Request / Response Schemas
# ----------------------------------------------------
class SelectionRequest(BaseModel):
    item_ids: List[str]
    occasion: str

class SavedOutfitRequest(BaseModel):
    item_ids: List[str]
    occasion: str
    compatibility_score: float
    style_explanation: str

# ----------------------------------------------------
# API Routes
# ----------------------------------------------------
@app.get("/api/wardrobe")
def get_wardrobe():
    """Retrieve the user's current wardrobe items."""
    cache_key = "wardrobe_all"
    cached = cache.get(cache_key)
    if cached:
        return cached
        
    wardrobe = db.get_wardrobe()
    cache.set(cache_key, wardrobe, 60)
    return wardrobe

@app.get("/api/catalog")
def get_catalog():
    """Retrieve items available for purchase."""
    return db.get_catalog()

@app.get("/api/history")
def get_purchase_history():
    """Retrieve user purchase history."""
    return db.get_purchase_history()

@app.post("/api/why-it-works")
def explain_outfit(req: SelectionRequest):
    """Calculates compatibility and returns AI style explanation."""
    # Find matching items in database
    wardrobe_items = db.get_wardrobe()
    catalog_items = db.get_catalog()
    all_items = {item["id"]: item for item in wardrobe_items + catalog_items}
    
    selected_items = [all_items[iid] for iid in req.item_ids if iid in all_items]
    
    if len(selected_items) < 2:
        return {
            "score": 100,
            "explanation": "Add more items to see why this combination works."
        }
        
    # Calculate score
    score = bpr.score_outfit(selected_items)
    
    # Generate style explanation
    explanation = gemini.generate_style_explanation(selected_items, req.occasion, score)
    
    return {
        "score": score,
        "explanation": explanation
    }

@app.post("/api/complete-look")
def complete_look(req: SelectionRequest):
    """Recommends matching items from wardrobe & catalog to complete a partial outfit."""
    wardrobe_items = db.get_wardrobe()
    catalog_items = db.get_catalog()
    all_items = {item["id"]: item for item in wardrobe_items + catalog_items}
    
    selected = [all_items[iid] for iid in req.item_ids if iid in all_items]
    if not selected:
        return {"recommendations": []}

    selected_categories = {item["category"] for item in selected}
    
    # We want to recommend categories that are NOT already selected
    # Occasions map outfit formulas
    from seed_data import OCCASIONS
    formula = OCCASIONS.get(req.occasion, {}).get("formula", ["kurta", "bottom", "dupatta", "footwear", "accessory"])
    missing_categories = [cat for cat in formula if cat not in selected_categories]
    
    recommendations = []
    
    # Look at both wardrobe and catalog
    for item in wardrobe_items + catalog_items:
        # Avoid recommending items already selected
        if item["id"] in req.item_ids:
            continue
            
        if item["category"] in missing_categories:
            # Calculate compatibility score of this item with the current outfit
            compat_scores = []
            for sel_item in selected:
                score = bpr.calculate_compatibility_score(item, sel_item)
                compat_scores.append(score)
            
            avg_score = round(sum(compat_scores) / len(compat_scores) if compat_scores else 50, 1)
            
            # Form style note
            note = f"Pairs with your {selected[0]['color']} {selected[0]['category']}. "
            if item["color"] == "Gold" and "festive" in req.occasion:
                note += "Gold accents elevate the festive tone."
            elif item["color"] == "Silver" and "office" in req.occasion:
                note += "Oxidized silver keeps it elegant and professional."
            else:
                note += f"Adds a beautiful {item['color']} element for a coordinated look."

            is_owned = item["id"].startswith("wardrobe_")
            
            recommendations.append({
                "item": item,
                "compatibility_score": avg_score,
                "style_note": note,
                "is_owned": is_owned
            })
            
    # Sort recommendations by compatibility score descending
    recommendations.sort(key=lambda x: x["compatibility_score"], reverse=True)
    return {"recommendations": recommendations[:5]} # Top 5 recommendations

@app.post("/api/suggest-buy")
def suggest_buy(req: SelectionRequest):
    """
    Analyzes purchase history and current wardrobe to recommend items from catalog
    that expand styling possibilities, providing clear natural-language reasons.
    """
    history = db.get_purchase_history()
    wardrobe = db.get_wardrobe()
    catalog = db.get_catalog()
    
    if not history:
        return {"suggestions": []}
        
    suggestions = []
    
    # We look at each purchased item and find catalog items that complement it
    for owned in wardrobe:
        for cat_item in catalog:
            # Only recommend items in different categories that aren't already owned
            if cat_item["category"] == owned["category"]:
                continue
                
            # Compute similarity/compatibility
            score = bpr.calculate_compatibility_score(owned, cat_item)
            
            # Recommend items that fit well (score > 75)
            if score > 75:
                reason = gemini.generate_buy_reasoning(cat_item, owned, req.occasion)
                suggestions.append({
                    "item": cat_item,
                    "owned_reference": owned,
                    "compatibility_score": score,
                    "reason": reason
                })
                
    # Sort by compatibility score
    suggestions.sort(key=lambda x: x["compatibility_score"], reverse=True)
    
    # Remove duplicate recommended items to keep recommendations diverse
    seen_ids = set()
    unique_suggestions = []
    for s in suggestions:
        if s["item"]["id"] not in seen_ids:
            seen_ids.add(s["item"]["id"])
            unique_suggestions.append(s)
            
    return {"suggestions": unique_suggestions[:4]}

@app.post("/api/upload-match")
async def upload_match(
    file: UploadFile = File(...),
    occasion: str = Form("festive")
):
    """
    Process uploaded image via Computer Vision, extract attributes,
    search vector database (Pinecone) for wardrobe matches, and suggest catalog additions.
    """
    # 1. Read file bytes
    file_bytes = await file.read()
    
    # 2. Upload to Local Storage (Cloudinary mock)
    uploaded_url = cloudinary.upload_image(file_bytes, file.filename)
    
    # 3. Form full path to analyze
    local_path = os.path.join(UPLOAD_DIR, os.path.basename(uploaded_url))
    
    # 4. Classify attributes using PIL & PyTorch
    attributes = classify_clothing_attributes(local_path)
    
    # Construct description for vector search
    query_text = f"{attributes['color']} {attributes['pattern']} {attributes['fabric']} {attributes['category']}"
    
    # 5. Search Wardrobe matches using Vector similarity (Pinecone mock)
    wardrobe_matches = vector_db.query_nearest(query_text, category=attributes["category"], top_k=2)
    
    # Find matching items in database
    wardrobe_items = db.get_wardrobe()
    catalog_items = db.get_catalog()
    
    # 6. If wardrobe matching is low or has no matching categories, suggest catalog buys
    buy_suggestions = []
    
    # For matching catalog buys
    catalog_matches = vector_db.query_nearest(query_text, category=attributes["category"], top_k=3)
    # Check if catalog matches are already owned
    owned_names = {w["name"].lower() for w in wardrobe_items}
    for item in catalog_matches:
        if item["name"].lower() not in owned_names:
            # Formulate reasoning
            reason = f"This {item['color']} {item['category']} shares similar {attributes['fabric']} styling to the photo you uploaded and fits perfectly for {occasion}."
            buy_suggestions.append({
                "item": item,
                "reason": reason
            })
            
    return {
        "uploaded_image_url": uploaded_url,
        "extracted_attributes": attributes,
        "wardrobe_matches": wardrobe_matches,
        "buy_suggestions": buy_suggestions[:2]
    }

@app.post("/api/save-outfit")
def save_outfit(req: SavedOutfitRequest):
    """Save an outfit combination."""
    outfit_id = db.save_outfit(
        req.item_ids,
        req.occasion,
        req.compatibility_score,
        req.style_explanation
    )
    return {"message": "Outfit saved successfully", "outfit_id": outfit_id}

@app.get("/api/saved-outfits")
def get_saved_outfits():
    """Get saved outfits list."""
    outfits = db.get_saved_outfits()
    # Populate item details
    wardrobe_items = db.get_wardrobe()
    catalog_items = db.get_catalog()
    all_items = {item["id"]: item for item in wardrobe_items + catalog_items}
    
    for o in outfits:
        o["items"] = [all_items[iid] for iid in o["item_ids"] if iid in all_items]
        
    return outfits


# Serve Static files for the frontend
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
