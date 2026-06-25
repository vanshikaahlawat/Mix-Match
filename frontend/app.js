// app.js

const API_BASE = "/api";

// Active selection state
let selectedItems = {
    kurta: null,
    bottom: null,
    dupatta: null,
    footwear: null,
    accessory: null
};

let currentOccasion = "daily";
let wardrobeData = [];
let catalogData = [];

// DOM Elements
const wardrobeGrid = document.getElementById("wardrobe-items-grid");
const btnSaveOutfit = document.getElementById("btn-save-outfit");
const explanationText = document.getElementById("explanation-text");
const styleBullets = document.getElementById("style-bullets");
const gaugeFill = document.getElementById("gauge-fill");
const gaugeValue = document.getElementById("gauge-value");
const gaugeVibe = document.getElementById("gauge-vibe");
const emptyCanvasMsg = document.getElementById("empty-canvas-msg");

const occasionSelect = document.getElementById("occasion-select");
const completeRecsList = document.getElementById("complete-recs-list");
const smartBuysList = document.getElementById("smart-buys-list");
const savedOutfitsList = document.getElementById("saved-outfits-list");

const uploadDropzone = document.getElementById("upload-dropzone");
const photoUploadInput = document.getElementById("photo-upload-input");
const cvResultsCard = document.getElementById("cv-results-card");
const cvPreviewImg = document.getElementById("cv-preview-img");
const cvAttributeTags = document.getElementById("cv-attribute-tags");
const cvWardrobeMatches = document.getElementById("cv-wardrobe-matches");
const cvBuyMatches = document.getElementById("cv-buy-matches");

const toastMsg = document.getElementById("toast-msg");

// ----------------------------------------------------
// 1. Initialization
// ----------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
    fetchWardrobe();
    fetchCatalog();
    fetchSavedOutfits();
    setupEventListeners();
});

function setupEventListeners() {
    // Wardrobe category tabs
    document.querySelectorAll(".cat-tab").forEach(tab => {
        tab.addEventListener("click", (e) => {
            document.querySelectorAll(".cat-tab").forEach(t => t.classList.remove("active"));
            e.target.classList.add("active");
            filterWardrobe(e.target.dataset.category);
        });
    });

    // Occasion Select
    occasionSelect.addEventListener("change", (e) => {
        currentOccasion = e.target.value;
        updateOutfitAnalysis();
        fetchCompleteLookRecs();
        fetchSmartBuySuggestions();
    });

    // Save Outfit Button
    btnSaveOutfit.addEventListener("click", saveOutfit);

    // Tools tab switches
    document.querySelectorAll(".tool-tab").forEach(tab => {
        tab.addEventListener("click", (e) => {
            document.querySelectorAll(".tool-tab").forEach(t => t.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
            
            e.target.classList.add("active");
            document.getElementById(`tab-${e.target.dataset.tab}`).classList.add("active");
        });
    });

    // File Upload handling
    uploadDropzone.addEventListener("click", () => photoUploadInput.click());
    photoUploadInput.addEventListener("change", handlePhotoUpload);

    // Drag over support
    uploadDropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        uploadDropzone.style.borderColor = "var(--secondary-color)";
    });
    uploadDropzone.addEventListener("dragleave", () => {
        uploadDropzone.style.borderColor = "rgba(255, 255, 255, 0.15)";
    });
    uploadDropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        uploadDropzone.style.borderColor = "rgba(255, 255, 255, 0.15)";
        if (e.dataTransfer.files.length) {
            photoUploadInput.files = e.dataTransfer.files;
            handlePhotoUpload();
        }
    });
}

// ----------------------------------------------------
// 2. Data Fetching
// ----------------------------------------------------
async function fetchWardrobe() {
    try {
        const res = await fetch(`${API_BASE}/wardrobe`);
        wardrobeData = await res.json();
        renderWardrobeGrid(wardrobeData);
    } catch (err) {
        console.error("Error fetching wardrobe:", err);
        wardrobeGrid.innerHTML = `<div class="loading-spinner">Error loading Almari items.</div>`;
    }
}

async function fetchCatalog() {
    try {
        const res = await fetch(`${API_BASE}/catalog`);
        catalogData = await res.json();
        // Trigger smart buys initial fetch
        fetchSmartBuySuggestions();
    } catch (err) {
        console.error("Error fetching catalog:", err);
    }
}

// ----------------------------------------------------
// 3. UI Rendering & Interactions
// ----------------------------------------------------
function renderWardrobeGrid(items) {
    if (!items.length) {
        wardrobeGrid.innerHTML = `<div class="empty-state">No wardrobe items.</div>`;
        return;
    }

    wardrobeGrid.innerHTML = "";
    items.forEach(item => {
        const card = document.createElement("div");
        card.className = `item-card ${isItemSelected(item) ? 'active' : ''}`;
        card.dataset.id = item.id;
        
        card.innerHTML = `
            <div class="item-img-container">
                <img src="${item.image_url || 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=200&q=80'}" alt="${item.name}">
                <span class="card-badge">Almari</span>
                <span class="selected-indicator"></span>
            </div>
            <div class="card-meta">
                <h4 class="card-title">${item.name}</h4>
                <div class="card-subtext">
                    <span>${item.color}</span>
                    <span>₹${item.purchase_price || item.price || ''}</span>
                </div>
            </div>
        `;
        
        card.addEventListener("click", () => toggleWardrobeItem(item));
        wardrobeGrid.appendChild(card);
    });
}

function filterWardrobe(category) {
    if (category === "all") {
        renderWardrobeGrid(wardrobeData);
    } else {
        const filtered = wardrobeData.filter(i => i.category === category);
        renderWardrobeGrid(filtered);
    }
}

function isItemSelected(item) {
    return selectedItems[item.category] && selectedItems[item.category].id === item.id;
}

function toggleWardrobeItem(item) {
    const category = item.category;
    
    if (selectedItems[category] && selectedItems[category].id === item.id) {
        // De-select
        selectedItems[category] = null;
    } else {
        // Select & replace if category exists
        selectedItems[category] = item;
    }
    
    // Refresh wardrobe list active states
    const activeTab = document.querySelector(".cat-tab.active").dataset.category;
    filterWardrobe(activeTab);

    // Update visuals & recommendations
    updateMannequinVisuals();
    updateOutfitAnalysis();
    fetchCompleteLookRecs();
}

// ----------------------------------------------------
// 4. Mannequin Layer Updates
// ----------------------------------------------------
function updateMannequinVisuals() {
    let activeAny = false;

    // A. Kurta Layer
    const layerKurta = document.getElementById("layer-kurta");
    const shapeKurtaStraight = document.getElementById("shape-kurta-straight");
    const shapeKurtaAnarkali = document.getElementById("shape-kurta-anarkali");
    
    if (selectedItems.kurta) {
        activeAny = true;
        layerKurta.classList.remove("hidden");
        const kurta = selectedItems.kurta;
        const color = kurta.color_hex;
        
        // Pick shape based on silhouette or name
        const isAnarkali = kurta.silhouette === "anarkali" || kurta.name.toLowerCase().includes("anarkali");
        if (isAnarkali) {
            shapeKurtaStraight.classList.add("hidden");
            shapeKurtaAnarkali.classList.remove("hidden");
            shapeKurtaAnarkali.setAttribute("fill", color);
        } else {
            shapeKurtaAnarkali.classList.add("hidden");
            shapeKurtaStraight.classList.remove("hidden");
            shapeKurtaStraight.setAttribute("fill", color);
        }
    } else {
        layerKurta.classList.add("hidden");
        shapeKurtaStraight.classList.add("hidden");
        shapeKurtaAnarkali.classList.add("hidden");
    }

    // B. Bottom Layer
    const layerBottom = document.getElementById("layer-bottom");
    const shapeJeans = document.getElementById("shape-jeans");
    const shapePalazzo = document.getElementById("shape-palazzo");
    
    if (selectedItems.bottom) {
        activeAny = true;
        layerBottom.classList.remove("hidden");
        const bottom = selectedItems.bottom;
        const color = bottom.color_hex;
        
        // Pick shape based on silhouette or name
        const isPalazzo = bottom.silhouette === "palazzo" || bottom.name.toLowerCase().includes("palazzo") || bottom.name.toLowerCase().includes("salwar");
        if (isPalazzo) {
            shapeJeans.classList.add("hidden");
            shapePalazzo.classList.remove("hidden");
            shapePalazzo.setAttribute("fill", color);
        } else {
            shapePalazzo.classList.add("hidden");
            shapeJeans.classList.remove("hidden");
            shapeJeans.setAttribute("fill", color);
        }
    } else {
        layerBottom.classList.add("hidden");
        shapeJeans.classList.add("hidden");
        shapePalazzo.classList.add("hidden");
    }

    // C. Dupatta Layer
    const layerDupatta = document.getElementById("layer-dupatta");
    if (selectedItems.dupatta) {
        activeAny = true;
        layerDupatta.classList.remove("hidden");
        const color = selectedItems.dupatta.color_hex;
        
        // Set path color. For multicolor, use the Bandhani gradient defined in SVG Defs
        const pathElements = layerDupatta.querySelectorAll("path");
        pathElements.forEach(p => {
            if (selectedItems.dupatta.color.toLowerCase() === "multicolor" || color.includes("gradient")) {
                p.setAttribute("fill", "url(#bandhani)");
            } else {
                p.setAttribute("fill", color);
            }
        });
    } else {
        layerDupatta.classList.add("hidden");
    }

    // D. Accessory (Jhumka) Layer
    const layerAccessory = document.getElementById("layer-accessory");
    if (selectedItems.accessory && selectedItems.accessory.category === "accessory") {
        activeAny = true;
        layerAccessory.classList.remove("hidden");
        const color = selectedItems.accessory.color_hex;
        const subPaths = layerAccessory.querySelectorAll("path, line");
        subPaths.forEach(sp => {
            if (sp.tagName === "line") {
                sp.setAttribute("stroke", color);
            } else {
                sp.setAttribute("fill", color);
            }
        });
    } else {
        layerAccessory.classList.add("hidden");
    }

    // E. Footwear Layer
    const layerFootwear = document.getElementById("layer-footwear");
    if (selectedItems.footwear) {
        activeAny = true;
        layerFootwear.classList.remove("hidden");
        const color = selectedItems.footwear.color_hex;
        const subPaths = layerFootwear.querySelectorAll("path");
        subPaths.forEach(sp => {
            sp.setAttribute("fill", color);
        });
    } else {
        layerFootwear.classList.add("hidden");
    }

    // Toggle Empty State Message
    if (activeAny) {
        emptyCanvasMsg.classList.add("hidden");
    } else {
        emptyCanvasMsg.classList.remove("hidden");
    }
}

// ----------------------------------------------------
// 5. Outfit Analysis (Score & AI explanations)
// ----------------------------------------------------
async function updateOutfitAnalysis() {
    const ids = Object.values(selectedItems).filter(item => item !== null).map(item => item.id);
    
    if (ids.length < 2) {
        // Reset gauge
        setGaugeValue(0, "Choose items");
        explanationText.textContent = "Assemble at least a Kurta and Bottom to get a personalized style lesson explaining color harmony and cultural suitability.";
        btnSaveOutfit.disabled = true;
        return;
    }
    
    btnSaveOutfit.disabled = false;
    explanationText.innerHTML = "<em>Analyzing your outfit coordinates...</em>";

    try {
        const res = await fetch(`${API_BASE}/why-it-works`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ item_ids: ids, occasion: currentOccasion })
        });
        
        const data = await res.json();
        
        // Update Gauge
        let vibeLabel = "Good Vibe";
        if (data.score >= 85) vibeLabel = "Stylist Approved! 🔥";
        else if (data.score >= 70) vibeLabel = "Beautiful Blend ✨";
        else vibeLabel = "Daily Comfort 👍";

        setGaugeValue(data.score, vibeLabel);
        explanationText.textContent = data.explanation;
        
    } catch (err) {
        console.error("Error analyzing outfit:", err);
        explanationText.textContent = "Failed to load style analysis, but your combination looks good!";
    }
}

function setGaugeValue(val, label) {
    gaugeValue.textContent = val > 0 ? Math.round(val) : "--";
    gaugeVibe.textContent = label;
    
    // Gauge SVG stroke animation
    // Circle length is 2 * PI * r = 2 * 3.14159 * 45 = 282.7
    const dashOffset = val > 0 ? 283 - (val / 100) * 283 : 283;
    gaugeFill.style.strokeDashoffset = dashOffset;
}

// ----------------------------------------------------
// 6. Complete the Look Recommendations
// ----------------------------------------------------
async function fetchCompleteLookRecs() {
    const ids = Object.values(selectedItems).filter(item => item !== null).map(item => item.id);
    
    if (!ids.length) {
        completeRecsList.innerHTML = `<div class="empty-state">Select items in the wardrobe first to see matching suggestions.</div>`;
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/complete-look`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ item_ids: ids, occasion: currentOccasion })
        });
        
        const data = await res.json();
        renderCompleteLookList(data.recommendations);
    } catch (err) {
        console.error("Error fetching look completion:", err);
    }
}

function renderCompleteLookList(recs) {
    if (!recs.length) {
        completeRecsList.innerHTML = `<div class="empty-state">All set! You have selected all categories.</div>`;
        return;
    }

    completeRecsList.innerHTML = "";
    recs.forEach(rec => {
        const card = document.createElement("div");
        card.className = "rec-card";
        
        const isOwned = rec.is_owned;
        
        card.innerHTML = `
            <div class="rec-thumbnail">
                <img src="${rec.item.image_url || 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=80&q=80'}" alt="${rec.item.name}">
            </div>
            <div class="rec-info">
                <div class="rec-title-row">
                    <h5 class="rec-title">${rec.item.name}</h5>
                    ${!isOwned ? `<span class="rec-price">₹${rec.item.price}</span>` : ''}
                </div>
                <p class="rec-note">${rec.style_note}</p>
                <div class="rec-action-row">
                    <span class="rec-score-badge">Match: ${Math.round(rec.compatibility_score)}%</span>
                    ${isOwned 
                        ? `<button class="btn btn-sm btn-add-rec" data-id="${rec.item.id}">Wear Now</button>`
                        : `<button class="btn btn-sm btn-buy-myntra" data-id="${rec.item.id}">Buy (₹${rec.item.price})</button>`
                    }
                </div>
            </div>
        `;
        
        // Attach action handlers
        const actionBtn = card.querySelector("button");
        actionBtn.addEventListener("click", () => {
            if (isOwned) {
                // Wear the item directly
                toggleWardrobeItem(rec.item);
            } else {
                // Mock purchase and add to wardrobe
                mockPurchaseItem(rec.item);
            }
        });

        completeRecsList.appendChild(card);
    });
}

// ----------------------------------------------------
// 7. Purchase History & Smart Buys
// ----------------------------------------------------
async function fetchSmartBuySuggestions() {
    try {
        const res = await fetch(`${API_BASE}/suggest-buy`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ item_ids: [], occasion: currentOccasion })
        });
        
        const data = await res.json();
        renderSmartBuys(data.suggestions);
    } catch (err) {
        console.error("Error loading smart buys:", err);
    }
}

function renderSmartBuys(suggestions) {
    if (!suggestions || !suggestions.length) {
        smartBuysList.innerHTML = `<div class="empty-state">Buy suggestions will show here based on purchase history.</div>`;
        return;
    }

    smartBuysList.innerHTML = "";
    suggestions.forEach(sug => {
        const card = document.createElement("div");
        card.className = "rec-card";
        
        card.innerHTML = `
            <div class="rec-thumbnail">
                <img src="${sug.item.image_url || 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=80&q=80'}" alt="${sug.item.name}">
            </div>
            <div class="rec-info">
                <div class="rec-title-row">
                    <h5 class="rec-title">${sug.item.name}</h5>
                    <span class="rec-price">₹${sug.item.price}</span>
                </div>
                <p class="rec-note"><strong>Why it works:</strong> ${sug.reason}</p>
                <div class="rec-action-row">
                    <span class="rec-score-badge">Match Score: ${Math.round(sug.compatibility_score)}%</span>
                    <button class="btn btn-sm btn-buy-myntra">Buy on Myntra</button>
                </div>
            </div>
        `;
        
        card.querySelector("button").addEventListener("click", () => mockPurchaseItem(sug.item));
        smartBuysList.appendChild(card);
    });
}

// ----------------------------------------------------
// 8. Photo Upload & Computer Vision Match
// ----------------------------------------------------
async function handlePhotoUpload() {
    const file = photoUploadInput.files[0];
    if (!file) return;

    // Show temporary spinner
    uploadDropzone.style.display = "none";
    cvResultsCard.classList.add("hidden");
    
    const loadingDiv = document.createElement("div");
    loadingDiv.className = "loading-spinner";
    loadingDiv.id = "cv-loading-spinner";
    loadingDiv.innerHTML = "📸 Extracting visual attributes using AlexNet CNN...";
    uploadDropzone.parentNode.insertBefore(loadingDiv, uploadDropzone.nextSibling);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("occasion", currentOccasion);

    try {
        const res = await fetch(`${API_BASE}/upload-match`, {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        
        // Remove loading state
        document.getElementById("cv-loading-spinner").remove();
        uploadDropzone.style.display = "block";
        cvResultsCard.classList.remove("hidden");

        // Display results
        cvPreviewImg.src = data.uploaded_image_url;
        
        // Extracted Tags
        const attr = data.extracted_attributes;
        cvAttributeTags.innerHTML = `
            <span class="tag-badge tag-badge-accent">${attr.category.toUpperCase()}</span>
            <span class="tag-badge">Color: ${attr.color}</span>
            ${attr.fabric !== "N/A" ? `<span class="tag-badge">Fabric: ${attr.fabric}</span>` : ''}
            ${attr.pattern !== "N/A" ? `<span class="tag-badge">Pattern: ${attr.pattern}</span>` : ''}
            ${attr.neckline !== "N/A" ? `<span class="tag-badge">Neck: ${attr.neckline}</span>` : ''}
            ${attr.sleeve_length !== "N/A" ? `<span class="tag-badge">Sleeve: ${attr.sleeve_length}</span>` : ''}
        `;

        // Render Wardrobe matches
        renderCVWardrobeMatches(data.wardrobe_matches);
        
        // Render missing buys
        renderCVBuyMatches(data.buy_suggestions);
        
    } catch (err) {
        console.error("Error in upload & match:", err);
        document.getElementById("cv-loading-spinner").remove();
        uploadDropzone.style.display = "block";
        alert("Could not analyze photo. Please try a different image.");
    }
}

function renderCVWardrobeMatches(matches) {
    if (!matches || !matches.length) {
        cvWardrobeMatches.innerHTML = `<div class="empty-state">No matching items in your Almari.</div>`;
        return;
    }
    
    cvWardrobeMatches.innerHTML = "";
    matches.forEach(item => {
        const card = document.createElement("div");
        card.className = "rec-card";
        
        card.innerHTML = `
            <div class="rec-thumbnail">
                <img src="${item.image_url}" alt="${item.name}">
            </div>
            <div class="rec-info">
                <h5 class="rec-title">${item.name}</h5>
                <p class="rec-note">Match from your wardrobe closet. Try styling it now!</p>
                <div class="rec-action-row">
                    <button class="btn btn-sm btn-add-rec">Wear Now</button>
                </div>
            </div>
        `;
        
        card.querySelector("button").addEventListener("click", () => {
            toggleWardrobeItem(item);
            // Switch tab to look builder
            document.querySelector(".tool-tab[data-tab='complete']").click();
        });
        cvWardrobeMatches.appendChild(card);
    });
}

function renderCVBuyMatches(buys) {
    if (!buys || !buys.length) {
        cvBuyMatches.innerHTML = `<div class="empty-state">No recommendations. Catalog already matches your closet.</div>`;
        return;
    }

    cvBuyMatches.innerHTML = "";
    buys.forEach(buy => {
        const card = document.createElement("div");
        card.className = "rec-card";
        
        card.innerHTML = `
            <div class="rec-thumbnail">
                <img src="${buy.item.image_url}" alt="${buy.item.name}">
            </div>
            <div class="rec-info">
                <div class="rec-title-row">
                    <h5 class="rec-title">${buy.item.name}</h5>
                    <span class="rec-price">₹${buy.item.price}</span>
                </div>
                <p class="rec-note">${buy.reason}</p>
                <div class="rec-action-row">
                    <button class="btn btn-sm btn-buy-myntra">Buy on Myntra</button>
                </div>
            </div>
        `;
        
        card.querySelector("button").addEventListener("click", () => mockPurchaseItem(buy.item));
        cvBuyMatches.appendChild(card);
    });
}

// ----------------------------------------------------
// 9. Mock Purchase Logic (Add Catalog item to Wardrobe)
// ----------------------------------------------------
function mockPurchaseItem(item) {
    // Show quick alert
    showToast(`🛒 Purchased ${item.name}! Added to Almari.`);
    
    // Simulate API adding to database
    // In a production backend, this represents payment / order sync
    const newWardrobeItem = {
        ...item,
        id: `wardrobe_${item.id}`,
        purchase_date: "Today",
        purchase_price: item.price
    };

    // Update locally and fetch wardrobe again
    setTimeout(async () => {
        try {
            // Standard simulated add via POST body (since mock DB supports it)
            // Or we just add it to wardrobeData and re-render
            wardrobeData.push(newWardrobeItem);
            
            // Re-render and match
            const activeTab = document.querySelector(".cat-tab.active").dataset.category;
            filterWardrobe(activeTab);
            
            // Highlight / auto select the item
            toggleWardrobeItem(newWardrobeItem);
            
            // Clear look completes / fetch again
            fetchCompleteLookRecs();
            fetchSmartBuySuggestions();
        } catch (e) {
            console.error(e);
        }
    }, 500);
}

// ----------------------------------------------------
// 10. Saved Outfits
// ----------------------------------------------------
async function saveOutfit() {
    const ids = Object.values(selectedItems).filter(item => item !== null).map(item => item.id);
    const score = parseFloat(gaugeValue.textContent);
    const explanation = explanationText.textContent;
    
    if (ids.length < 2) return;
    
    try {
        const res = await fetch(`${API_BASE}/save-outfit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                item_ids: ids,
                occasion: currentOccasion,
                compatibility_score: score,
                style_explanation: explanation
            })
        });
        
        if (res.ok) {
            showToast("✨ Outfit saved to Wardrobe Book!");
            fetchSavedOutfits();
        }
    } catch (err) {
        console.error("Error saving outfit:", err);
    }
}

async function fetchSavedOutfits() {
    try {
        const res = await fetch(`${API_BASE}/saved-outfits`);
        const data = await res.json();
        renderSavedOutfits(data);
    } catch (err) {
        console.error("Error loading saved looks:", err);
    }
}

function renderSavedOutfits(outfits) {
    if (!outfits.length) {
        savedOutfitsList.innerHTML = `<div class="empty-state">No saved outfits yet. Assemble your first look and click "Save Look"!</div>`;
        return;
    }
    
    savedOutfitsList.innerHTML = "";
    outfits.forEach(o => {
        const card = document.createElement("div");
        card.className = "rec-card";
        
        const details = o.items.map(i => `${i.color} ${i.category}`).join(" + ");
        
        card.innerHTML = `
            <div class="rec-info" style="padding-left: 0.5rem">
                <h5 class="rec-title" style="max-width: 100%">${o.occasion.toUpperCase()} Look - Score: ${Math.round(o.compatibility_score)}%</h5>
                <p class="rec-note" style="margin-top:0.2rem"><strong>Combination:</strong> ${details}</p>
                <p class="rec-note" style="margin-top:0.25rem; font-style:italic">"${o.style_explanation.substring(0, 110)}..."</p>
                <div class="rec-action-row" style="margin-top:0.5rem">
                    <button class="btn btn-sm btn-add-rec" style="background:#553066">Drape Look</button>
                </div>
            </div>
        `;
        
        // Wear saved outfit on click
        card.querySelector("button").addEventListener("click", () => {
            // Reset active selections
            selectedItems = { kurta: null, bottom: null, dupatta: null, footwear: null, accessory: null };
            
            // Match saved items to selections
            o.items.forEach(item => {
                selectedItems[item.category] = item;
            });
            
            // Trigger UI update
            const activeTab = document.querySelector(".cat-tab.active").dataset.category;
            filterWardrobe(activeTab);
            
            updateMannequinVisuals();
            updateOutfitAnalysis();
            fetchCompleteLookRecs();
            
            // Switch visual tab to complete
            document.querySelector(".tool-tab[data-tab='complete']").click();
            showToast("✨ Draping saved look onto mannequin...");
        });
        
        savedOutfitsList.appendChild(card);
    });
}

// ----------------------------------------------------
// 11. Toast Utility
// ----------------------------------------------------
function showToast(msg) {
    toastMsg.textContent = msg;
    toastMsg.classList.remove("hidden");
    
    setTimeout(() => {
        toastMsg.classList.add("hidden");
    }, 3000);
}
