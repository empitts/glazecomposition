# glazecomposition
ML/AI project to create potential glaze recipes based on image analysis and glaze recipe pretraining


A toolkit for extracting, organizing, and learning from ceramic glaze experiments at scale. This repo combines OCR, segmentation, object detection, structured parsing, and recipe math to convert raw studio images + captions into analyzable datasets and reproducible glaze “recipes.”

> **Status:** work‑in‑progress; core components run locally. Focus areas: multi‑tile image parsing, caption/handwritten note correlation, dataset/build tooling, and a unity molecular formula calculator.


## Goals

1. **Automate** extraction of glaze variables from photos: tiles, rows/series, captions, handwritten notes, and incremental recipe changes.
2. **Normalize** recipes into a consistent, queryable schema (materials, formulas, unity values).
3. **Learn** the relationship between composition and outcomes (color/texture, defects, etc.).
4. **Scale** from a handful of photos to thousands with robust retries, confidence scoring, and review queues.

---

## Key Features

* **Multi‑tile image understanding**: segment tiles in a single photo; preserve order (gradients/series) and map to captions.
* **OCR from multiple regions**: top/bottom strips, within each tile bounding box, and surrounding image margins for notes/IDs.
* **Caption ↔ tile correlation**: link handwritten notes and web captions to the correct tiles using proximity + string similarity + heuristics.
* **Recipe differencing**: detect incremental changes (e.g., “+2% TiO₂ across the row”) and propagate per‑tile “final” formulas.
* **Low‑confidence flagging**: send ambiguous images to human review.
* **Web scraping helpers**: headless collection from JS‑heavy sources (e.g., keen‑slider galleries) via Selenium.
* **Dataset builder**: standardized JSON/CSV exports + image crops for ML.
* **Unity molecular formula calculator**: computes oxide totals, unity, and includes standard colorants/opacifiers.

---

## Architecture

```
[ Images + Captions ]
        │
        ▼
   Ingestion Layer
   - local folders
   - website scraping (Selenium)
   - metadata (JSON sidecars)
        │
        ▼
  Preprocessing
  - resize/orient
  - denoise/contrast (as needed)
        │
        ▼
  Vision Models
  - Object Detection (tile frames)
  - Segmentation (MobileSAM for precise shapes)
        │
        ▼
  OCR Layer
  - EasyOCR
  - region proposals (tile boxes, strips, margins)
        │
        ▼
  Parsing & Correlation
  - caption/handwriting parsing
  - series/order inference
  - recipe delta extraction
        │
        ▼
  Normalization & Math
  - material dictionary + aliases
  - unity molecular formula calculator
        │
        ▼
  Storage & Exports
  - SQLite (local dev)
  - JSON/CSV + cropped tiles
        │
        ▼
  Review & Training
  - confidence thresholds
  - review queue
  - dataset for model fine‑tuning
```

---

## Data Flow

1. **Ingest** images and (optional) text sidecars/captions.
2. **Detect/segment** tiles; generate per‑tile crops.
3. **OCR** text from (a) global strips/borders, (b) within each tile, and (c) margin notes.
4. **Parse** recipe instructions, series ordering (A→F, 0→10), and deltas (e.g., +2% rutile per step).
5. **Correlate** OCR text with captions; resolve IDs (tile labels, handwritten markers).
6. **Normalize** materials using an alias dictionary.
7. **Compute** unity molecular formula and add derived features.
8. **Export** to SQLite/CSV/JSON; flag items for manual review if low confidence.

---

## Directory Layout

```
project-root/
├─ src/
│  ├─ ingest/
│  │  ├─ selenium_scraper.py        # JS-enabled scraping (keen-slider, etc.)
│  │  └─ file_watcher.py            # optional folder ingestion
│  ├─ vision/
│  │  ├─ detect_tiles_yolo.py       # detection of tile bounding boxes
│  │  ├─ segment_tiles_sam.py       # MobileSAM/Segment-Anything segmentation
│  │  └─ crop_utils.py              # crop extraction & tiling
│  ├─ ocr/
│  │  ├─ easyocr_runner.py          # OCR across regions
│  │  └─ parse_text_blocks.py       # regex + heuristics + LLM prompts
│  ├─ parsing/
│  │  ├─ caption_linker.py          # correlate captions ↔ tiles
│  │  ├─ recipe_delta_parser.py     # extract incremental changes
│  │  └─ material_aliases.py        # alias map (e.g., "EPK" → "Kaolin EPK")
│  ├─ chemistry/
│  │  ├─ unity_formula.py           # oxide math, unity normalization
│  │  └─ materials_db.py            # base materials + oxides, colorants/opacifiers
│  ├─ datastore/
│  │  ├─ sqlite_store.py            # local persistence
│  │  └─ export.py                  # CSV/JSON writers
│  └─ pipeline.py                   # orchestrates end-to-end run
├─ models/
│  ├─ yolo/                         # weights, config
│  └─ sam/                          # MobileSAM checkpoints
├─ data/
│  ├─ raw/                          # original images
│  ├─ interim/                      # detected boxes/segments
│  ├─ crops/                        # per‑tile crops
│  ├─ ocr/                          # text blocks & confidences
│  └─ exports/                      # CSV/JSON outputs, sqlite.db
├─ notebooks/                       # exploratory work
├─ configs/
│  ├─ pipeline.yaml                 # thresholds, model paths, regexes
│  └─ scraping.yaml                 # source sites, selectors, auth
├─ tests/                           # unit/integration tests
└─ README.md                        # this file
```

---

## Setup

### 1) Environment

# Miniconda Instructions

To activate this environment, use

     $ conda activate glazenotebook

 To deactivate an active environment, use

    $ conda deactivate
## install libraries for environemnt
    $ conda install -n myenv scipy

```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip wheel
pip install -r requirements.txt
```

Typical libs (subset): `opencv-python`, `numpy`, `scipy`, `pillow`, `torch`, `easyocr`, `pytesseract`, `matplotlib`, `pandas`, `sqlalchemy`, `scikit-image`, `rapidfuzz`, `selenium`.

> If using MobileSAM/Segment Anything, ensure the correct PyTorch + CUDA (or CPU) stack is installed.

### 2) Model Weights

* **YOLO**: place `best.pt` under `models/yolo/` or update `configs/pipeline.yaml`.
* **MobileSAM**: place checkpoint under `models/sam/`.


### Outputs

* `data/crops/` — per‑tile cropped images
* `data/ocr/` — OCR JSON with bounding boxes + confidences
* `data/exports/records.jsonl` — per‑tile normalized records
* `data/exports/glazes.db` — SQLite database for queries

### Example Query (SQLite)

```sql
SELECT tile_id, base_recipe_id, step_index, outcome_color, unity_SiO2, unity_Al2O3
FROM tiles
WHERE material_alias = 'EPK' AND unity_TiO2 > 0.05
ORDER BY step_index;
```

---

## OCR & Parsing

**Regions scanned:**

1. Global strips/banners (top/bottom captions).
2. Inside each detected/segmented tile box.
3. Surrounding margins for handwritten notes, arrows, IDs.

---

## Computer Vision Models

* **Tile detection:** YOLO model trained on tile frames; supports multi‑tile images.
* **Precise boundaries:** MobileSAM integrates with detected boxes to refine masks/crops.
* **Training notes:**

  * YOLO’s training preview images like `train_batch0.jpg` are mosaics for visualization/debugging.
  * Use Label Studio to annotate bounding boxes/segments; export in YOLO/COCO.
  * Fine‑tune with studio imagery to improve generalization across clays and lighting.

---

## Dataset Building & Ingestion

**Scraping:**

* Selenium driver (e.g., for glazy.org) to handle JavaScript‑rendered elements like `keen-slider` and capture image URLs.
* Robust selectors + retries; fall back to network logs when needed.

**Storage:**

* **Local dev:** SQLite (`data/exports/glazes.db`).
* **Exports:** JSONL/CSV for ML pipelines. Images/crops stored alongside with stable IDs.

**Schema (simplified):**

```
materials(material_id, canonical_name, aliases_json, oxides_json)
recipes(recipe_id, base_json)
tiles(tile_id, image_id, recipe_id, step_index, masks_json, notes_json,
      unity_json, outcome_labels, confidence)
ocr_blocks(block_id, image_id, bbox, text, confidence, region_type)
images(image_id, path, captured_at, meta_json)
```

---

## Molecular Math (Unity Formula)

A Python module computes oxide totals and unity normalization for a recipe, including **standard colorants/opacifiers** (e.g., TiO₂, Fe₂O₃, MnO₂, CuO, CoO, Cr₂O₃, ZrO₂, SnO₂, ZnO).

**Highlights:**

* Redefinable **ingredient list** and **molecular weights** via `materials_db.py`.
* **Alias support** (e.g., "EPK", "Kaolin EPK").
* Batch mode to compute unity for all tiles after recipe deltas are resolved.

Usage (module):

```python
from src.chemistry.unity_formula import compute_unity
unity = compute_unity(materials_dict, recipe_grams)
print(unity["SiO2"], unity["Al2O3"])  # etc.
```

---

## Quality Control & Human‑in‑the‑loop

* **Confidence thresholds** from OCR + model scores produce an overall record confidence.
* **Ambiguity detection** (conflicting deltas, missing base recipe, illegible labels) routes to a **review queue**.
* Keep raw OCR blocks and annotated crops to simplify manual corrections.
