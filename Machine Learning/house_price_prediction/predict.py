"""
House Price Prediction — CLI System (Task 5)
============================================
Run: python predict.py
"""

import pickle
import json
import numpy as np
import os

G  = "\033[92m"   # green
B  = "\033[94m"   # blue
Y  = "\033[93m"   # yellow
R  = "\033[91m"   # red
W  = "\033[97m"   # white bold
RS = "\033[0m"    # reset
BOLD = "\033[1m"

def cls():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print(f"""
{B}{BOLD}╔══════════════════════════════════════════════════════╗
║     ISLAMABAD HOUSE PRICE PREDICTOR                  ║
║        Trained on Zameen.com Listings                ║
╚══════════════════════════════════════════════════════╝{RS}
""")

def format_pkr(amount: float) -> str:
    if amount >= 1e7:
        return f"PKR {amount/1e7:.2f} Crore"
    elif amount >= 1e5:
        return f"PKR {amount/1e5:.1f} Lakh"
    return f"PKR {amount:,.0f}"

def ask(prompt: str, typ=str, choices=None, min_val=None, max_val=None):
    while True:
        try:
            raw = input(f"  {Y}▶{RS} {prompt}: ").strip()
            val = typ(raw)
            if choices and val not in choices:
                print(f"  {R}  Please choose from: {', '.join(str(c) for c in choices)}{RS}")
                continue
            if min_val is not None and val < min_val:
                print(f"  {R}  Minimum value is {min_val}{RS}")
                continue
            if max_val is not None and val > max_val:
                print(f"  {R}  Maximum value is {max_val}{RS}")
                continue
            return val
        except (ValueError, KeyboardInterrupt, EOFError):
            print(f"  {R}  Invalid input. Please try again.{RS}")

def pick_from_list(label: str, options: list) -> str:
    print(f"\n  {W}{label}:{RS}")
    cols = 3
    for i, opt in enumerate(options, 1):
        print(f"    {Y}{i:2}.{RS} {opt:<25}", end="" if i % cols else "\n")
    if len(options) % cols:
        print()
    while True:
        try:
            idx = int(input(f"\n  {Y}▶{RS} Enter number (1–{len(options)}): ").strip())
            if 1 <= idx <= len(options):
                return options[idx - 1]
            print(f"  {R}  Enter a number between 1 and {len(options)}{RS}")
        except (ValueError, KeyboardInterrupt, EOFError):
            print(f"  {R}  Please enter a valid number{RS}")

def to_marla(val: float, unit: str) -> float:
    if unit == "2":   return val * 20          # Kanal
    if unit == "3":   return val / 272.251     # Sq Ft
    return val                                  # Marla

def make_features(area_marla, beds, baths, loc_enc, type_enc,
                  parking, servant, store, kitchens, drawing, built_year, feature_cols):
    age = 2024 - built_year
    baths_ratio = beds / (baths + 1)
    row = {
        "area_marla":        area_marla,
        "bedrooms":          beds,
        "bathrooms":         baths,
        "parking_spaces":    parking,
        "servant_quarters":  servant,
        "store_rooms":       store,
        "kitchens":          kitchens,
        "drawing_rooms":     drawing,
        "property_age":      age,
        "beds_baths_ratio":  baths_ratio,
        "location_enc":      loc_enc,
        "property_type_enc": type_enc,
        "city_enc":          0,
        "purpose_enc":       0,
    }
    import pandas as pd
    return pd.DataFrame([{c: row.get(c, 0) for c in feature_cols}])


def run():
    cls()
    banner()

    try:
        with open("best_model.pkl", "rb") as f:
            model = pickle.load(f)
        with open("model_meta.json") as f:
            meta = json.load(f)
    except FileNotFoundError:
        print(f"{R}  ✗ Model files not found. Run 'python ml_pipeline.py' first.{RS}")
        return

    locations    = meta["location_classes"]
    prop_types   = meta["property_type_classes"]
    feature_cols = meta["feature_cols"]

    print(f"{G}  Model loaded: {meta['best_model_name']}{RS}\n")

    while True:
        print(f"{B}{'─'*56}{RS}")
        print(f"  {W}Enter property details to get an estimated price{RS}")
        print(f"{B}{'─'*56}{RS}\n")

        location = pick_from_list("Select Location", sorted(locations))
        loc_enc  = sorted(locations).index(location)

        prop_type = pick_from_list("Select Property Type", sorted(prop_types))
        type_enc  = sorted(prop_types).index(prop_type)

        print(f"\n  {W}Area Unit:{RS}")
        print(f"    {Y}1.{RS} Marla   {Y}2.{RS} Kanal   {Y}3.{RS} Square Feet")
        unit = ask("Choose unit (1/2/3)", str, choices=["1","2","3"])
        unit_label = {"1":"Marla","2":"Kanal","3":"Square Feet"}[unit]
        area_val   = ask(f"Area in {unit_label}", float, min_val=0.5, max_val=500)
        area_marla = to_marla(area_val, unit)

        print(f"\n  {W}Room Details:{RS}")
        beds     = ask("Bedrooms  (1–10)", int, min_val=1, max_val=10)
        baths    = ask("Bathrooms (1–8)",  int, min_val=1, max_val=8)
        kitchens = ask("Kitchens  (1–4)",  int, min_val=1, max_val=4)
        drawing  = ask("Drawing Rooms (0–3)", int, min_val=0, max_val=3)

        print(f"\n  {W}Additional Features:{RS}")
        parking = ask("Parking Spaces (0–5)", int, min_val=0, max_val=5)
        servant = ask("Servant Quarters? (0=No / 1=Yes)", int, choices=[0, 1])
        store   = ask("Store Room?       (0=No / 1=Yes)", int, choices=[0, 1])
        built_yr = ask("Built Year (1990–2024)", int, min_val=1990, max_val=2024)

        X        = make_features(area_marla, beds, baths, loc_enc, type_enc,
                                 parking, servant, store, kitchens, drawing,
                                 built_yr, feature_cols)
        log_pred = model.predict(X)[0]
        price    = np.expm1(log_pred)
        low      = price * 0.88
        high     = price * 1.12

        print(f"""
    {G}{BOLD}╔══════════════════════════════════════════════════════╗
    ║              ESTIMATED PRICE                         ║
╠══════════════════════════════════════════════════════╣
║  Property : {prop_type:<40}║
║  Location : {location:<40}║
║  Area     : {f"{area_val} {unit_label}":<40}║
║  Bedrooms : {str(beds):<40}║
╠══════════════════════════════════════════════════════╣
║  Price    : {format_pkr(price):<40}║
║  Low Est. : {format_pkr(low):<40}║
║  High Est.: {format_pkr(high):<40}║
║  Per Marla: {format_pkr(price/max(area_marla,1)):<40}║
╚══════════════════════════════════════════════════════╝{RS}
""")

        again = input(f"  {Y}▶{RS} Predict another property? (y/n): ").strip().lower()
        if again != "y":
            print(f"\n{B}  Goodbye!{RS}\n")
            break
        cls()
        banner()


if __name__ == "__main__":
    run()
