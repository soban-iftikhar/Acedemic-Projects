# House Price Prediction System - Islamabad

This project is an end-to-end machine learning pipeline for predicting residential property prices in Islamabad. It uses Zameen.com listings as the main data source, prepares a structured dataset, trains multiple regression models, and exposes the final predictor through both a Streamlit app and a CLI tool.

## Purpose

The goal is to estimate market price from common property features such as area, location, bedrooms, bathrooms, property type, and extra amenities. The project was built for an ML lab terminal project and demonstrates the full workflow from data collection to deployment.

## What the project does

The workflow is split into four parts:

1. Scrape Islamabad property listings from Zameen.com into a CSV dataset.
2. Fall back to a realistic synthetic dataset if scraping is blocked or too slow.
3. Clean the data, engineer features, and train several regression models.
4. Serve predictions through a Streamlit interface and a terminal-based CLI.

## Project Structure

```text
├── zameen_scraper.py     Web scraper that collects Zameen.com listings
├── generate_dataset.py   Fallback dataset generator for Islamabad listings
├── zameen_islamabad.csv  Dataset used by the training pipeline and apps
├── ml_pipeline.py        Preprocessing, training, evaluation, and model export
├── app.py                Streamlit prediction app
├── predict.py            CLI prediction app
├── requirements.txt      Python dependencies
└── Final_Report.docx     Project report
```

## Requirements

Use Python 3.10 or newer if possible. The project relies on common data-science packages and optionally uses XGBoost and CatBoost if they are installed.

Install dependencies with:

```bash
pip install -r requirements.txt
```

## How to Run

### 1. Get the dataset

Use either the live scraper or the fallback generator.

Live scraping:

```bash
python zameen_scraper.py
```

Fallback dataset generation:

```bash
python generate_dataset.py
```

Both options create or refresh `zameen_islamabad.csv`.

### 2. Train the models

```bash
python ml_pipeline.py
```

This step:

* cleans and preprocesses the dataset,
* encodes categorical columns,
* compares multiple regressors,
* saves the best trained model and metadata.

It writes these outputs:

* `best_model.pkl`
* `all_models.pkl`
* `model_meta.json`
* `model_results.csv`

### 3. Run the Streamlit app

```bash
streamlit run app.py
```

Open the local URL shown by Streamlit, usually `http://localhost:8501`.

### 4. Run the CLI version

```bash
python predict.py
```

This is the terminal version of the same prediction workflow.

## Model Summary

The training pipeline compares six regressors and uses the best performer as the final model. In the current results, Gradient Boosting performs best on the held-out test set.

## What the app shows

The Streamlit app provides:

* a prediction form for entering property details,
* a model comparison tab,
* a dataset explorer with summary charts and sample data.

## Notes

* If scraping fails because the site blocks requests, use `generate_dataset.py` and continue the pipeline from there.
* If the app says model files are missing, run `ml_pipeline.py` first.
* The project is built around Islamabad data only, so the encoders and predictions are scoped to that market.
