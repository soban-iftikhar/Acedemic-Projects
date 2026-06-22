"""
Zameen.com Islamabad - Fallback Dataset Generator
==================================================
Generates a realistic 400-row property dataset for Islamabad
based on real Zameen.com listing patterns and price ranges.

Use this if web scraping is blocked or slow.
Run:  python generate_dataset.py
"""

import pandas as pd
import numpy as np
import random

random.seed(42)
np.random.seed(42)

LOCATIONS = [
    "DHA Phase 1", "DHA Phase 2", "DHA Phase 4", "DHA Phase 5",
    "Bahria Town Phase 1", "Bahria Town Phase 2", "Bahria Town Phase 4",
    "Bahria Town Phase 7", "Bahria Town Phase 8", "Bahria Enclave",
    "F-6", "F-7", "F-8", "F-10", "F-11",
    "G-6", "G-7", "G-8", "G-9", "G-10", "G-11", "G-13", "G-14", "G-15",
    "E-7", "E-11",
    "I-8", "I-10", "I-14", "I-16",
    "PWD Housing Society", "PECHS", "Gulberg Greens", "Gulberg Residencia",
    "Capital Smart City", "Park View City", "Blue World City",
    "CBR Town", "Airport Housing Society", "Margalla Hills",
    "Sector B-17", "Sector C-14", "Naval Anchorage",
    "Top City-1", "Mumtaz City", "Faisal Town",
]

PROPERTY_TYPES = [
    "House", "House", "House", "House",
    "Upper Portion", "Lower Portion",
    "Flat", "Flat",
    "Farm House",
    "Penthouse",
]

LOCATION_TIERS = {
    "premium": [
        "DHA Phase 1", "DHA Phase 2", "DHA Phase 4", "DHA Phase 5",
        "F-6", "F-7", "F-8", "E-7",
    ],
    "high": [
        "F-10", "F-11", "E-11", "G-6", "G-7",
        "Bahria Town Phase 1", "Bahria Town Phase 2", "Bahria Enclave",
        "Gulberg Greens", "Gulberg Residencia",
    ],
    "mid": [
        "G-8", "G-9", "G-10", "G-11", "G-13", "G-14", "G-15",
        "I-8", "I-10", "Bahria Town Phase 4", "Bahria Town Phase 7",
        "Bahria Town Phase 8", "PECHS", "PWD Housing Society",
    ],
    "affordable": [
        "I-14", "I-16", "CBR Town", "Airport Housing Society",
        "Sector B-17", "Sector C-14", "Capital Smart City",
        "Park View City", "Blue World City", "Top City-1",
        "Mumtaz City", "Faisal Town", "Naval Anchorage",
        "Margalla Hills",
    ],
}

TIER_BASE_PRICE = {
    "premium":    5_500_000,   # per marla
    "high":       3_800_000,
    "mid":        2_200_000,
    "affordable": 1_200_000,
}

def get_tier(location: str) -> str:
    for tier, locs in LOCATION_TIERS.items():
        if location in locs:
            return tier
    return "affordable"


def generate_listing() -> dict:
    location = random.choice(LOCATIONS)
    tier = get_tier(location)
    prop_type = random.choice(PROPERTY_TYPES)

    if prop_type in ["Flat", "Penthouse"]:
        area = round(random.uniform(3, 15), 1)
        area_unit = "Marla"
    elif prop_type == "Farm House":
        area = round(random.uniform(4, 20), 0)
        area_unit = "Kanal"
    else:
        area = random.choice([
            3, 5, 5, 7, 8, 10, 10, 10, 12, 14, 15, 20, 20
        ])
        area_unit = random.choices(
            ["Marla", "Kanal"], weights=[75, 25]
        )[0]

    area_marla = area * (20 if area_unit == "Kanal" else 1)

    if area_marla <= 5:
        beds = random.choice([2, 3])
        baths = random.choice([1, 2])
    elif area_marla <= 10:
        beds = random.choice([3, 4, 4, 5])
        baths = random.choice([2, 3, 3])
    else:
        beds = random.choice([4, 5, 5, 6, 7])
        baths = random.choice([3, 4, 4, 5])

    kitchens = 1 if beds <= 4 else random.choice([1, 2])
    drawing_rooms = 1 if beds <= 3 else random.choice([1, 2])
    parking = 0 if prop_type == "Flat" else random.choices([1, 2, 3], weights=[40, 45, 15])[0]
    servant_quarters = 0 if area_marla < 10 else random.choice([0, 1])
    store_rooms = 0 if area_marla < 7 else random.choice([0, 1])
    built_year = random.randint(2000, 2023) if random.random() > 0.3 else None

    base_per_marla = TIER_BASE_PRICE[tier]
    if area_marla > 40:
        area_factor = 0.80
    elif area_marla > 20:
        area_factor = 0.90
    else:
        area_factor = 1.0

    age_factor = 1.0
    if built_year:
        age = 2024 - built_year
        age_factor = max(0.70, 1.0 - age * 0.008)

    extras = 1.0 + (servant_quarters * 0.03) + (parking * 0.02) + (store_rooms * 0.01)

    price = (base_per_marla * area_marla * area_factor * age_factor * extras
             * random.uniform(0.88, 1.12))

    price = round(price / 100_000) * 100_000

    return {
        "price_pkr":          price,
        "area":               area,
        "area_unit":          area_unit,
        "city":               "Islamabad",
        "bedrooms":           beds,
        "bathrooms":          baths,
        "location":           location,
        "property_type":      prop_type,
        "built_year":         built_year,
        "parking_spaces":     parking,
        "servant_quarters":   servant_quarters,
        "store_rooms":        store_rooms,
        "kitchens":           kitchens,
        "drawing_rooms":      drawing_rooms,
        "purpose":            "For Sale",
    }


def generate_dataset(n: int = 400) -> pd.DataFrame:
    rows = [generate_listing() for _ in range(n)]
    df = pd.DataFrame(rows)

    for col in ["built_year", "parking_spaces", "servant_quarters", "store_rooms"]:
        mask = np.random.random(len(df)) < 0.05
        df.loc[mask, col] = np.nan

    dup_idx = np.random.choice(df.index, size=int(n * 0.02), replace=False)
    df = pd.concat([df, df.loc[dup_idx]], ignore_index=True)

    return df


if __name__ == "__main__":
    df = generate_dataset(400)
    df.to_csv("zameen_islamabad.csv", index=False)
    print(f"Generated {len(df)} rows -> zameen_islamabad.csv")
    print(df.head())
    print(f"\nPrice range: PKR {df['price_pkr'].min():,.0f} – {df['price_pkr'].max():,.0f}")
    print(df.dtypes)
