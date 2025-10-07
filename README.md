# Glaze Analysis Project

A toolkit for extracting, organizing, and learning from ceramic glaze experiments at scale. This repo combines OCR, segmentation, object detection, structured parsing, and recipe math to convert raw studio images + captions into analyzable datasets and reproducible glaze “recipes.”


> **Status:** WIP. Core pipeline runs locally.

---

## What it does

* **Find tiles** in a photo (detection + optional segmentation).
* **Read text** from strips, each tile, and the margins (OCR).
* **Link notes ↔ tiles** and **parse recipe changes** (e.g., “+2% TiO₂ per step”).
* **Normalize materials** with aliases (EPK ⇢ Kaolin EPK, etc.).
* **Compute unity molecular formula** (incl. standard colorants/opacifiers).
* **Export a dataset** (SQLite/JSON/CSV) for search, charts, and model training.
* **Flag low‑confidence** images for quick human review.

---

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -U pip wheel
pip install -r requirements.txt

# put images under data/raw/
python -m src.pipeline \
  --input data/raw \
  --out data/exports \
  --sqlite data/exports/glazes.db \
  --conf configs/pipeline.yaml
```

**Models:** place YOLO weights in `models/yolo/`, MobileSAM checkpoint in `models/sam/` (optional).

---

## How it works (short)

```
Images → detect/segment tiles → OCR regions → parse notes & deltas
     → normalize materials → unity formula → exports (DB/JSON/CSV)
```

---

## Repo layout (short)

```
src/
  ingest/        # selenium_scraper.py (JS sites), file_watcher.py
  vision/        # detect_tiles_yolo.py, segment_tiles_sam.py, crop_utils.py
  ocr/           # easyocr_runner.py, parse_text_blocks.py
  parsing/       # caption_linker.py, recipe_delta_parser.py, material_aliases.py
  chemistry/     # unity_formula.py, materials_db.py
  datastore/     # sqlite_store.py, export.py
  pipeline.py    # orchestrates the steps
models/          # yolo/ and sam/ checkpoints
data/            # raw/, crops/, ocr/, exports/
configs/         # pipeline.yaml, scraping.yaml
```

---

## Outputs

* `data/crops/` – per‑tile images
* `data/ocr/` – OCR JSON (bbox + confidence)
* `data/exports/records.jsonl` – one record per tile
* `data/exports/glazes.db` – SQLite with materials, recipes, tiles, OCR blocks

Example query:

```sql
SELECT tile_id, step_index, unity_SiO2, unity_Al2O3
FROM tiles
WHERE unity_TiO2 > 0.05
ORDER BY step_index;
```

---

## Notes on OCR & parsing

* Scans **strips**, **tiles**, and **margins**.
* Uses regex + small dictionaries; can call an LLM to clean text and infer deltas.
* Assigns notes to tiles with proximity + string similarity; low confidence ⇒ review.

---

## Training tips

* Label Studio for boxes/masks; export COCO/YOLO.
* YOLO preview files like `train_batch0.jpg` are normal (mosaic debug images).
* Fine‑tune with your studio lighting/clays for best results.

