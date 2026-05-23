# 🏠 House Price Prediction System — Islamabad
## ML Lab Terminal Project | Zameen.com Data

---

## 📁 Project Structure

```
├── zameen_scraper.py       # Web scraper (Zameen.com → CSV)
├── generate_dataset.py     # Fallback realistic dataset generator
├── zameen_islamabad.csv    # 408-row Islamabad property dataset
├── ml_pipeline.py          # Full ML pipeline (preprocessing + 6 models)
├── app.py                  # Streamlit prediction web app
├── requirements.txt        # Python dependencies
└── Final_Report.docx       # Project report
```

---

## ⚡ Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get the dataset

**Option A — Scrape live data (may be slow due to anti-bot):**
```bash
python zameen_scraper.py
```

**Option B — Generate realistic dataset instantly:**
```bash
python generate_dataset.py
```
This creates `zameen_islamabad.csv` with 400+ realistic Islamabad property listings.

### 3. Train the models
```bash
python ml_pipeline.py
```
This produces:
- `best_model.pkl` — Best performing model (Gradient Boosting, R²=0.931)
- `all_models.pkl` — All 6 trained models
- `model_meta.json` — Feature encoders and metadata
- `model_results.csv` — Performance comparison table

### 4. Launch the prediction app
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`

---

## 📊 Model Performance

| Model              | MAE (PKR)    | RMSE (PKR)    | R²     |
|--------------------|-------------|---------------|--------|
| Gradient Boosting  | 13,920,576  | 35,010,589    | 0.9310 |
| Random Forest      | 15,771,038  | 38,271,505    | 0.9176 |
| XGBoost            | 15,340,673  | 40,221,907    | 0.9090 |
| Decision Tree      | 19,725,382  | 44,621,408    | 0.8880 |
| CatBoost           | 17,612,123  | 45,787,133    | 0.8820 |
| Linear Regression  | 38,469,865  | 119,274,287   | 0.1996 |

🏆 **Best Model: Gradient Boosting (R²=0.931)**

---

## 🔮 Prediction System

The Streamlit app allows users to enter:
- Area (Marla/Kanal/Square Feet)
- Location (44 Islamabad areas)
- Bedrooms, Bathrooms, Kitchens, Drawing Rooms
- Property Type (House, Flat, Farm House, etc.)
- Parking Spaces, Servant Quarters, Store Rooms
- Built Year

And outputs: **Estimated House Price in PKR** with confidence range.
