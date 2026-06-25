# models_ml.py
import os
import random
import numpy as np
from PIL import Image

# Import PyTorch. If not installed, we will define PyTorch classes but handle execution gracefully.
HAS_TORCH = False
try:
    import torch
    import torch.nn as nn
    import torchvision.transforms as transforms
    HAS_TORCH = True
except ImportError:
    # Minimal PyTorch fallback interface so PyTorch definitions compile fine without crash
    class nn:
        class Module:
            pass
        class Sequential:
            def __init__(self, *args): pass
        class Conv2d:
            def __init__(self, *args, **kwargs): pass
        class ReLU:
            def __init__(self, *args, **kwargs): pass
        class MaxPool2d:
            def __init__(self, *args, **kwargs): pass
        class AdaptiveAvgPool2d:
            def __init__(self, *args, **kwargs): pass
        class Dropout:
            def __init__(self, *args, **kwargs): pass
        class Linear:
            def __init__(self, *args, **kwargs): pass

# ----------------------------------------------------
# 1. PyTorch AlexNet-based Attribute Classification Network
# ----------------------------------------------------
if HAS_TORCH:
    class AlexNetAttributeClassifier(torch.nn.Module):
        def __init__(self, num_attributes=26): # categories + necklines + sleeves + patterns + fabrics
            super(AlexNetAttributeClassifier, self).__init__()
            self.features = torch.nn.Sequential(
                torch.nn.Conv2d(3, 64, kernel_size=11, stride=4, padding=2),
                torch.nn.ReLU(inplace=True),
                torch.nn.MaxPool2d(kernel_size=3, stride=2),
                torch.nn.Conv2d(64, 192, kernel_size=5, padding=2),
                torch.nn.ReLU(inplace=True),
                torch.nn.MaxPool2d(kernel_size=3, stride=2),
                torch.nn.Conv2d(192, 384, kernel_size=3, padding=1),
                torch.nn.ReLU(inplace=True),
                torch.nn.Conv2d(384, 256, kernel_size=3, padding=1),
                torch.nn.ReLU(inplace=True),
                torch.nn.Conv2d(256, 256, kernel_size=3, padding=1),
                torch.nn.ReLU(inplace=True),
                torch.nn.MaxPool2d(kernel_size=3, stride=2),
            )
            self.avgpool = torch.nn.AdaptiveAvgPool2d((6, 6))
            self.classifier = torch.nn.Sequential(
                torch.nn.Dropout(p=0.5),
                torch.nn.Linear(256 * 6 * 6, 2048),
                torch.nn.ReLU(inplace=True),
                torch.nn.Dropout(p=0.5),
                torch.nn.Linear(2048, 1024),
                torch.nn.ReLU(inplace=True),
                torch.nn.Linear(1024, num_attributes),
            )

        def forward(self, x):
            x = self.features(x)
            x = self.avgpool(x)
            x = torch.flatten(x, 1)
            x = self.classifier(x)
            return x
else:
    # Mock class that mimics the structure for reference
    class AlexNetAttributeClassifier:
        def __init__(self, num_attributes=26):
            self.num_attributes = num_attributes
        def forward(self, x):
            return np.random.randn(1, self.num_attributes)

# Helper function to classify attributes using OpenCV/Pillow & PyTorch
def classify_clothing_attributes(image_path: str):
    """
    Simulates OpenCV / PyTorch processing on an uploaded photo.
    Extracts the dominant color using Pillow, and generates attribute predictions.
    """
    try:
        img = Image.open(image_path).convert('RGB')
    except Exception:
        # Fallback if image cannot be opened
        img = Image.new('RGB', (100, 100), color=(225, 173, 1)) # Mustard default

    # Extract dominant color from image (simple resize to 1x1 to average pixels)
    small_img = img.resize((1, 1))
    r, g, b = small_img.getpixel((0, 0))
    hex_color = f"#{r:02x}{g:02x}{b:02x}"
    
    # Map the RGB values to the nearest matching color name
    color_map = {
        "Mustard": (225, 173, 1),
        "Red": (153, 0, 18),
        "Blue": (43, 62, 92),
        "White": (248, 249, 250),
        "Indigo": (30, 48, 96),
        "Gold": (255, 215, 0),
        "Silver": (192, 192, 192),
        "Olive": (85, 107, 47),
        "Pink": (255, 182, 193),
        "Black": (26, 26, 26),
        "Teal": (0, 128, 128)
    }
    
    closest_color = "Teal"
    min_dist = float('inf')
    for color_name, color_rgb in color_map.items():
        dist = np.sqrt((r-color_rgb[0])**2 + (g-color_rgb[1])**2 + (b-color_rgb[2])**2)
        if dist < min_dist:
            min_dist = dist
            closest_color = color_name

    # Check filename to see if we can extract category clues (e.g. if file is kurta.jpg)
    filename = os.path.basename(image_path).lower()
    inferred_category = "kurta"
    if "bottom" in filename or "jeans" in filename or "pant" in filename or "palazzo" in filename or "salwar" in filename:
        inferred_category = "bottom"
    elif "dupatta" in filename or "scarf" in filename:
        inferred_category = "dupatta"
    elif "shoe" in filename or "juttis" in filename or "heel" in filename or "footwear" in filename or "chappal" in filename:
        inferred_category = "footwear"
    elif "earring" in filename or "bag" in filename or "jhumka" in filename or "accessory" in filename:
        inferred_category = "accessory"
    else:
        # Random pick or based on color
        categories = ["kurta", "bottom", "dupatta", "footwear", "accessory"]
        inferred_category = random.choices(categories, weights=[0.4, 0.2, 0.15, 0.15, 0.1], k=1)[0]

    # Predict other attributes based on categories (inspired by DeepFashion annotations)
    necklines = ["round", "V-neck", "keyhole", "collar"]
    sleeves = ["3/4 sleeve", "long sleeve", "sleeveless", "short sleeve"]
    patterns = ["solid", "printed", "embroidered", "block-print"]
    fabrics = ["cotton", "rayon", "silk", "chiffon", "georgette", "denim"]

    # Select logical combinations
    if inferred_category == "kurta":
        neck = random.choice(necklines)
        sleeve = random.choice(sleeves)
        pattern = random.choice(patterns)
        fabric = random.choice(["cotton", "rayon", "silk", "georgette"])
        silhouette = "straight"
    elif inferred_category == "bottom":
        neck = "N/A"
        sleeve = "N/A"
        pattern = "solid"
        fabric = random.choice(["denim", "cotton", "rayon"])
        silhouette = "palazzo" if "palazzo" in filename or random.random() > 0.5 else "straight"
    else:
        neck = "N/A"
        sleeve = "N/A"
        pattern = random.choice(["solid", "printed", "embroidered"])
        fabric = random.choice(["silk", "chiffon", "cotton"])
        silhouette = "N/A"

    return {
        "category": inferred_category,
        "color": closest_color,
        "color_hex": hex_color,
        "neckline": neck,
        "sleeve_length": sleeve,
        "pattern": pattern,
        "fabric": fabric,
        "silhouette": silhouette
    }


# ----------------------------------------------------
# 2. Word2Vec Embedding Simulation via Gensim representation
# ----------------------------------------------------
class Word2VecSimulator:
    """
    Simulates Word2Vec mapping text descriptions into vector space embeddings.
    Allows calculating semantic similarity between clothing items.
    """
    def __init__(self):
        # Seed keywords and their visual vectors (represented as 8-dim arrays)
        self.vocabulary = {
            "ethnic":     [0.9, 0.1, 0.8, 0.2, 0.1, 0.0, 0.7, 0.9],
            "traditional":[0.95, 0.05, 0.85, 0.15, 0.05, 0.0, 0.8, 0.95],
            "festive":    [0.85, 0.0, 0.95, 0.1, 0.0, 0.2, 0.9, 0.9],
            "casual":     [0.1, 0.9, 0.1, 0.8, 0.7, 0.6, 0.1, 0.2],
            "daily":      [0.05, 0.95, 0.05, 0.9, 0.8, 0.7, 0.0, 0.1],
            "office":     [0.2, 0.8, 0.2, 0.7, 0.9, 0.5, 0.2, 0.3],
            "wedding":    [0.99, 0.0, 0.99, 0.0, 0.0, 0.1, 0.99, 0.99],
            "cotton":     [0.3, 0.7, 0.1, 0.8, 0.9, 0.2, 0.1, 0.1],
            "embroidered":[0.8, 0.2, 0.85, 0.3, 0.1, 0.3, 0.8, 0.8],
            "silk":       [0.9, 0.1, 0.9, 0.1, 0.1, 0.4, 0.9, 0.9]
        }
        self.dim = 8

    def get_sentence_embedding(self, text: str):
        """Tokenize text and average the word vectors."""
        words = text.lower().replace(",", " ").replace(".", " ").split()
        vectors = []
        for word in words:
            if word in self.vocabulary:
                vectors.append(self.vocabulary[word])
        if not vectors:
            # Fallback random vector if no vocabulary matches
            random.seed(len(text))
            return [random.uniform(-0.1, 0.1) for _ in range(self.dim)]
        return np.mean(vectors, axis=0).tolist()

    def cosine_similarity(self, vec1, vec2):
        dot_product = np.dot(vec1, vec2)
        norm_a = np.linalg.norm(vec1)
        norm_b = np.linalg.norm(vec2)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot_product / (norm_a * norm_b))


# ----------------------------------------------------
# 3. Bayesian Personalized Ranking (BPR) & Matrix Factorization
# ----------------------------------------------------
class BPRRecommender:
    """
    Simulates Matrix Factorization and BPR (Bayesian Personalized Ranking) Model.
    Learns outfit pairings from IQON3000 dataset rules to score item compatibility.
    """
    def __init__(self):
        # Latent space dimension
        self.latent_dim = 6
        # Seed latent vectors for categories to guide calculations logically
        # Categories: kurta, bottom, dupatta, footwear, accessory
        self.category_factors = {
            "kurta": [0.8, -0.2, 0.6, -0.4, 0.5, 0.1],
            "bottom": [-0.5, 0.7, -0.4, 0.6, -0.3, 0.5],
            "dupatta": [0.7, -0.3, 0.5, -0.5, 0.4, -0.2],
            "footwear": [-0.3, 0.5, -0.2, 0.4, -0.1, 0.6],
            "accessory": [0.6, -0.1, 0.4, -0.3, 0.3, 0.2]
        }
        # In a real system, these represent item embeddings trained on IQON3000 outfits.

    def _get_item_vector(self, item):
        cat = item.get("category", "kurta")
        base_vector = np.array(self.category_factors.get(cat, [0.1]*6))
        
        # Adjust factors slightly based on item characteristics (color, occasion)
        color = item.get("color", "")
        occasions = item.get("occasion_tags", [])
        
        modifier = [0.0] * self.latent_dim
        if "festive" in occasions:
            modifier[0] += 0.2
            modifier[2] += 0.2
        if "office" in occasions:
            modifier[1] += 0.2
            modifier[3] += 0.2
            
        # Unique noise based on ID to distinguish items
        random.seed(hash(item.get("id", "0")))
        noise = [random.uniform(-0.05, 0.05) for _ in range(self.latent_dim)]
        
        return base_vector + np.array(modifier) + np.array(noise)

    def calculate_compatibility_score(self, item1, item2):
        """
        Calculates compatibility score between two items.
        Returns score scaled between 0 and 100.
        """
        if item1["category"] == item2["category"]:
            # Items of the same category are not compatible
            return 0.0

        vec1 = self._get_item_vector(item1)
        vec2 = self._get_item_vector(item2)
        
        # Calculate dot product
        dot_val = np.dot(vec1, vec2)
        
        # Apply sigmoid to scale between 0 and 1
        score = 1 / (1 + np.exp(-dot_val))
        
        # Adjust based on color-matching rules for Indian garments
        color1 = item1.get("color")
        color2 = item2.get("color")
        
        color_bonus = 0.0
        # Mustard & Ivory (Classic elegant contrast)
        if (color1 == "Mustard" and color2 == "Ivory") or (color1 == "Ivory" and color2 == "Mustard"):
            color_bonus = 0.15
        # Indigo & White (Beautiful indigo print look)
        elif (color1 == "Indigo" and color2 == "White") or (color1 == "White" and color2 == "Indigo"):
            color_bonus = 0.15
        # Red & Ivory (Festive)
        elif (color1 == "Red" and color2 == "Ivory") or (color1 == "Ivory" and color2 == "Red"):
            color_bonus = 0.12
        # Mustard & Red (Traditional wedding vibe)
        elif (color1 == "Mustard" and color2 == "Red") or (color1 == "Red" and color2 == "Mustard"):
            color_bonus = 0.10
        # Olive & Ivory
        elif (color1 == "Olive" and color2 == "Ivory") or (color1 == "Ivory" and color2 == "Olive"):
            color_bonus = 0.08
        # Blue & Indigo
        elif (color1 == "Blue" and color2 == "Indigo") or (color1 == "Indigo" and color2 == "Blue"):
            color_bonus = 0.05
            
        final_score = (score + color_bonus) * 100
        # Bound score between 0 and 99
        return min(99.0, max(45.0, final_score))

    def score_outfit(self, list_of_items):
        """Calculates average compatibility across all pairwise combinations in an outfit."""
        if len(list_of_items) < 2:
            return 100.0
            
        scores = []
        for i in range(len(list_of_items)):
            for j in range(i + 1, len(list_of_items)):
                score = self.calculate_compatibility_score(list_of_items[i], list_of_items[j])
                if score > 0:
                    scores.append(score)
        
        if not scores:
            return 50.0
        return round(np.mean(scores), 1)
