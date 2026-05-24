"""
House Price Prediction - Streamlit Web App
==========================================
Final System (Task 5) — User enters property features → Predicted price

Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import json
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Islamabad House Price Predictor",
    page_icon="IH",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2e6da4 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .price-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: #f0f4f8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2e6da4;
        margin: 0.5rem 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #1e3a5f 0%, #2e6da4 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-size: 1.1rem;
        width: 100%;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_model():
    with open("best_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("model_meta.json") as f:
        meta = json.load(f)
    results = pd.read_csv("model_results.csv")
    return model, meta, results

@st.cache_data
def load_dataset():
    return pd.read_csv("zameen_islamabad.csv")


try:
    model, meta, results_df = load_model()
    df = load_dataset()
    MODEL_LOADED = True
except FileNotFoundError:
    MODEL_LOADED = False

def make_features(area_marla, beds, baths, location, prop_type,
                  parking, servant, store, kitchens, drawing, built_year,
                  meta):
    loc_classes  = meta["location_classes"]
    type_classes = meta["property_type_classes"]

    loc_enc  = loc_classes.index(location)  if location  in loc_classes  else 0
    type_enc = type_classes.index(prop_type) if prop_type in type_classes else 0

    age = 2024 - built_year
    baths_ratio = beds / (baths + 1)

    row = {
        "area_marla":       area_marla,
        "bedrooms":         beds,
        "bathrooms":        baths,
        "parking_spaces":   parking,
        "servant_quarters": servant,
        "store_rooms":      store,
        "kitchens":         kitchens,
        "drawing_rooms":    drawing,
        "property_age":     age,
        "beds_baths_ratio": baths_ratio,
        "location_enc":     loc_enc,
        "property_type_enc":type_enc,
        "city_enc":         0,    # only Islamabad
        "purpose_enc":      0,    # only For Sale
    }
    cols = meta["feature_cols"]
    return pd.DataFrame([{c: row.get(c, 0) for c in cols}])


def format_pkr(amount: float) -> str:
    if amount >= 1e7:
        return f"PKR {amount/1e7:.2f} Crore"
    elif amount >= 1e5:
        return f"PKR {amount/1e5:.1f} Lakh"
    else:
        return f"PKR {amount:,.0f}"

st.markdown("""
<div class="main-header">
    <h1>Islamabad House Price Predictor</h1>
    <p style="font-size:1.1rem; opacity:0.9;">
        Machine Learning-Powered Valuation System | Trained on Zameen.com Listings
    </p>
</div>
""", unsafe_allow_html=True)

if not MODEL_LOADED:
    st.error("Model files not found. Please run python ml_pipeline.py first.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Predict Price", "Model Performance", "Dataset Explorer"])

with tab1:
    st.subheader("Enter Property Details")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Size & Location**")
        area_val  = st.number_input("Area", min_value=1.0, max_value=100.0, value=10.0, step=0.5)
        area_unit = st.selectbox("Area Unit", ["Marla", "Kanal", "Square Feet"])
        location  = st.selectbox("Location", sorted(meta["location_classes"]))

    with col2:
        st.markdown("**Rooms**")
        beds      = st.slider("Bedrooms",  1, 10, 4)
        baths     = st.slider("Bathrooms", 1, 8,  3)
        kitchens  = st.slider("Kitchens",  1, 4,  1)
        drawing   = st.slider("Drawing Rooms", 0, 3, 1)

    with col3:
        st.markdown("**Property Details**")
        prop_type = st.selectbox("Property Type", sorted(meta["property_type_classes"]))
        parking   = st.slider("Parking Spaces", 0, 5, 2)
        servant   = st.selectbox("Servant Quarters", [0, 1], format_func=lambda x: "Yes" if x else "No")
        store     = st.selectbox("Store Room", [0, 1], format_func=lambda x: "Yes" if x else "No")
        built_yr  = st.slider("Built Year", 1990, 2024, 2015)

    def to_marla(val, unit):
        if unit == "Kanal":        return val * 20
        elif unit == "Square Feet": return val / 272.251
        return val

    area_marla = to_marla(area_val, area_unit)

    st.markdown("---")
    predict_btn = st.button("Predict House Price")

    if predict_btn:
        X = make_features(
            area_marla, beds, baths, location, prop_type,
            parking, servant, store, kitchens, drawing, built_yr, meta
        )
        log_pred = model.predict(X)[0]
        price    = np.expm1(log_pred)
        low      = price * 0.88
        high     = price * 1.12

        st.markdown("---")
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            st.markdown(f"""
            <div class="price-card">
                <h2 style="margin:0; font-size:2.2rem;">{format_pkr(price)}</h2>
                <p style="opacity:0.9; margin:0.5rem 0;">Estimated Market Value</p>
                <p style="font-size:0.9rem; opacity:0.8;">
                    Range: {format_pkr(low)} – {format_pkr(high)}
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("Property Summary")
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Location",      location)
        s2.metric("Area",          f"{area_val} {area_unit}")
        s3.metric("Bedrooms",      beds)
        s4.metric("Bathrooms",     baths)
        s1.metric("Property Type", prop_type)
        s2.metric("Built Year",    built_yr)
        s3.metric("Parking",       parking)
        s4.metric("Price/Marla",   format_pkr(price / area_marla))

        fig = go.Figure(go.Indicator(
            mode   = "gauge+number+delta",
            value  = price / 1e7,
            title  = {"text": "Estimated Price (Crore PKR)"},
            delta  = {"reference": df["price_pkr"].median() / 1e7},
            gauge  = {
                "axis": {"range": [0, df["price_pkr"].quantile(0.98) / 1e7]},
                "bar":  {"color": "#11998e"},
                "steps": [
                    {"range": [0, df["price_pkr"].quantile(0.33)/1e7], "color": "#e8f4f8"},
                    {"range": [df["price_pkr"].quantile(0.33)/1e7,
                               df["price_pkr"].quantile(0.66)/1e7], "color": "#c5dff0"},
                    {"range": [df["price_pkr"].quantile(0.66)/1e7,
                               df["price_pkr"].quantile(0.98)/1e7], "color": "#9dc5e0"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 3},
                    "thickness": 0.75,
                    "value": df["price_pkr"].median() / 1e7,
                },
            },
            number = {"suffix": " Cr", "valueformat": ".2f"},
        ))
        fig.update_layout(height=300, margin=dict(t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Model Comparison")
    st.dataframe(results_df.style.highlight_max(subset=["R²"], color="#c6efce")
                                  .highlight_min(subset=["MAE", "RMSE"], color="#c6efce"),
                 use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig_r2 = px.bar(
            results_df, x="Model", y="R²", color="R²",
            color_continuous_scale="Blues",
            title="R² Score by Model (higher = better)",
        )
        fig_r2.update_layout(showlegend=False)
        st.plotly_chart(fig_r2, use_container_width=True)

    with c2:
        fig_mae = px.bar(
            results_df, x="Model", y="MAE", color="MAE",
            color_continuous_scale="Reds_r",
            title="MAE by Model (lower = better)",
        )
        fig_mae.update_layout(showlegend=False)
        st.plotly_chart(fig_mae, use_container_width=True)

    st.info(f"Best Model: {results_df.iloc[0]['Model']} with R²={results_df.iloc[0]['R²']}")

with tab3:
    st.subheader("Dataset Overview")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Listings", len(df))
    c2.metric("Avg Price",       format_pkr(df["price_pkr"].mean()))
    c3.metric("Median Price",    format_pkr(df["price_pkr"].median()))
    c4.metric("Locations",       df["location"].nunique())

    c1, c2 = st.columns(2)
    with c1:
        fig_dist = px.histogram(
            df, x="price_pkr", nbins=40,
            title="Price Distribution",
            labels={"price_pkr": "Price (PKR)"},
            color_discrete_sequence=["#2e6da4"],
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    with c2:
        loc_avg = df.groupby("location")["price_pkr"].median().sort_values(ascending=False).head(15)
        fig_loc = px.bar(
            loc_avg, title="Top 15 Locations by Median Price",
            labels={"value": "Median Price (PKR)", "index": "Location"},
            color=loc_avg.values,
            color_continuous_scale="Blues",
        )
        fig_loc.update_layout(showlegend=False)
        st.plotly_chart(fig_loc, use_container_width=True)

    st.subheader("Raw Data")
    st.dataframe(df.head(50), use_container_width=True)

st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#888;'>"
    "House Price Prediction System | ML Lab Terminal Project | "
    "Data: Zameen.com Islamabad"
    "</p>",
    unsafe_allow_html=True
)
