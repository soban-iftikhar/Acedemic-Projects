"""
Zameen.com Property Listing Scraper - Islamabad
================================================
Scrapes 300-400 property listings from Zameen.com for Islamabad.
Uses requests + BeautifulSoup with fallback to Selenium for JS-heavy pages.

Usage:
    pip install requests beautifulsoup4 selenium pandas lxml
    python zameen_scraper.py
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import json
import re
import logging
from datetime import datetime
from pathlib import Path

# ── Optional Selenium import (used only if requests fails) ──────────────────
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────
BASE_URL   = "https://www.zameen.com"
CITY_SLUG  = "islamabad"
CITY_ID    = "2"          # Zameen internal city ID for Islamabad
TARGET_LISTINGS = 350
OUTPUT_CSV = "zameen_islamabad.csv"
REQUEST_DELAY = (2, 5)    # random sleep range between requests (seconds)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.zameen.com/",
}

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# ── Helpers ──────────────────────────────────────────────────────────────────

def sleep():
    time.sleep(random.uniform(*REQUEST_DELAY))


def get_page(url: str) -> BeautifulSoup | None:
    """Fetch a URL and return BeautifulSoup, or None on failure."""
    try:
        resp = SESSION.get(url, timeout=20)
        if resp.status_code == 200:
            return BeautifulSoup(resp.text, "lxml")
        log.warning(f"HTTP {resp.status_code} for {url}")
    except Exception as e:
        log.error(f"Request error: {e}")
    return None


def get_page_selenium(url: str) -> BeautifulSoup | None:
    """Fallback: use headless Chrome via Selenium."""
    if not SELENIUM_AVAILABLE:
        return None
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(f"user-agent={HEADERS['User-Agent']}")
    driver = webdriver.Chrome(options=opts)
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li[class*='listing']"))
        )
        soup = BeautifulSoup(driver.page_source, "lxml")
        return soup
    except Exception as e:
        log.error(f"Selenium error: {e}")
        return None
    finally:
        driver.quit()

# ── Price Parser ─────────────────────────────────────────────────────────────

def parse_price(text: str) -> float | None:
    """Convert 'PKR 1.5 Crore' → 15000000.0"""
    if not text:
        return None
    text = text.replace(",", "").strip().upper()
    multiplier = 1
    if "CRORE" in text:
        multiplier = 10_000_000
    elif "LAKH" in text:
        multiplier = 100_000
    elif "ARAB" in text:
        multiplier = 1_000_000_000
    nums = re.findall(r"[\d.]+", text)
    if not nums:
        return None
    try:
        return float(nums[0]) * multiplier
    except ValueError:
        return None


def parse_area(text: str) -> tuple[float | None, str | None]:
    """Convert '10 Marla' → (10.0, 'Marla')"""
    if not text:
        return None, None
    text = text.strip()
    match = re.match(r"([\d,.]+)\s*(.*)", text)
    if match:
        val = match.group(1).replace(",", "")
        unit = match.group(2).strip() or "Marla"
        try:
            return float(val), unit
        except ValueError:
            pass
    return None, None

# ── Listing Page Parser ───────────────────────────────────────────────────────

def parse_listing_detail(url: str) -> dict:
    """Scrape a single property detail page."""
    soup = get_page(url)
    if not soup:
        sleep()
        soup = get_page_selenium(url) if SELENIUM_AVAILABLE else None
    if not soup:
        return {}

    data = {"source_url": url}

    # ── Price ──
    for sel in ["span[class*='price']", "div[class*='price']", "strong[class*='price']"]:
        el = soup.select_one(sel)
        if el:
            data["price_raw"] = el.get_text(strip=True)
            data["price_pkr"] = parse_price(el.get_text(strip=True))
            break

    # ── Title / Property Type ──
    title_el = soup.select_one("h1")
    if title_el:
        data["title"] = title_el.get_text(strip=True)

    # ── Location ──
    for sel in ["div[class*='location']", "span[class*='location']", "li[class*='location']"]:
        el = soup.select_one(sel)
        if el:
            data["location"] = el.get_text(strip=True)
            break

    # ── Key details table (beds, baths, area, type) ──
    for item in soup.select("li[class*='IconItem'], div[class*='iconItem'], ul[class*='features'] li"):
        label = item.select_one("span[class*='label'], span[class*='Label']")
        value = item.select_one("span[class*='value'], span[class*='Value']")
        if not label or not value:
            # Try aria-label pattern
            aria = item.get("aria-label", "")
            text = item.get_text(separator=" ", strip=True)
            if "bed" in aria.lower() or "bed" in text.lower():
                nums = re.findall(r"\d+", text)
                if nums:
                    data.setdefault("bedrooms", int(nums[0]))
            elif "bath" in aria.lower() or "bath" in text.lower():
                nums = re.findall(r"\d+", text)
                if nums:
                    data.setdefault("bathrooms", int(nums[0]))
            continue
        lbl = label.get_text(strip=True).lower()
        val = value.get_text(strip=True)
        if "bed" in lbl:
            data["bedrooms"] = _safe_int(val)
        elif "bath" in lbl:
            data["bathrooms"] = _safe_int(val)
        elif "area" in lbl:
            area_val, area_unit = parse_area(val)
            data["area"] = area_val
            data["area_unit"] = area_unit
        elif "type" in lbl:
            data["property_type"] = val
        elif "floor" in lbl:
            data["floor"] = val
        elif "purpose" in lbl:
            data["purpose"] = val

    # ── Additional features (parking, servant, kitchens, etc.) ──
    for row in soup.select("div[class*='Detail'], table tr, div[class*='feature']"):
        text = row.get_text(separator="|", strip=True).lower()
        val_match = re.search(r"\|(\d+)", row.get_text(separator="|"))
        val = int(val_match.group(1)) if val_match else None
        if "parking" in text:
            data.setdefault("parking_spaces", val)
        elif "servant" in text:
            data.setdefault("servant_quarters", val if val else (1 if "yes" in text else 0))
        elif "store" in text:
            data.setdefault("store_rooms", val)
        elif "kitchen" in text:
            data.setdefault("kitchens", val)
        elif "drawing" in text:
            data.setdefault("drawing_rooms", val)
        elif "built" in text and "year" in text:
            yr = re.search(r"(19|20)\d{2}", text)
            if yr:
                data.setdefault("built_year", int(yr.group()))

    data["city"] = "Islamabad"
    return data


def _safe_int(s: str) -> int | None:
    try:
        return int(re.sub(r"[^\d]", "", s))
    except (ValueError, TypeError):
        return None

# ── Listing Index Parser ──────────────────────────────────────────────────────

def get_listing_urls_from_page(soup: BeautifulSoup) -> list[str]:
    """Extract individual listing URLs from a search results page."""
    urls = []
    # Zameen uses <li> cards with an <a> wrapping each listing
    for a in soup.select("li[class*='_2b0c6'] a, li[class*='listing'] a, article a, div[class*='listingCard'] a"):
        href = a.get("href", "")
        if href and ("/property/" in href or "/homes/" in href or "-" in href):
            full = href if href.startswith("http") else BASE_URL + href
            if full not in urls:
                urls.append(full)
    # Fallback: any link containing /property/
    if not urls:
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/property/" in href or re.search(r"/[a-z-]+-\d+\.html", href):
                full = href if href.startswith("http") else BASE_URL + href
                if full not in urls:
                    urls.append(full)
    return urls


def scrape(target: int = TARGET_LISTINGS) -> pd.DataFrame:
    """Main scraping loop — pages of search results → detail pages."""
    all_data = []
    page = 1
    seen_urls: set[str] = set()

    while len(all_data) < target:
        search_url = (
            f"{BASE_URL}/homes/for_sale/{CITY_SLUG}-{CITY_ID}/"
            f"?page={page}"
        )
        log.info(f"Scraping index page {page}: {search_url}")

        soup = get_page(search_url)
        if not soup:
            log.warning("Falling back to Selenium for index page...")
            soup = get_page_selenium(search_url) if SELENIUM_AVAILABLE else None
        if not soup:
            log.error("Cannot fetch search page. Stopping.")
            break

        urls = get_listing_urls_from_page(soup)
        log.info(f"  Found {len(urls)} listing URLs on page {page}")

        if not urls:
            log.warning("No listing URLs found — site structure may have changed or we're blocked.")
            break

        for url in urls:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            log.info(f"  Scraping listing ({len(all_data)+1}/{target}): {url}")
            detail = parse_listing_detail(url)
            if detail.get("price_pkr"):   # only keep listings with a price
                all_data.append(detail)
                log.info(f"    ✓ Price: {detail.get('price_pkr')}, Beds: {detail.get('bedrooms')}")
            if len(all_data) >= target:
                break
            sleep()

        # Check for next page
        next_btn = soup.select_one("a[class*='next'], a[rel='next'], button[class*='next']")
        if not next_btn:
            log.info("No next page button found. Done.")
            break
        page += 1
        sleep()

    df = pd.DataFrame(all_data)
    df.to_csv(OUTPUT_CSV, index=False)
    log.info(f"\n✅ Saved {len(df)} listings to '{OUTPUT_CSV}'")
    return df


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log.info("=" * 60)
    log.info("  Zameen.com Islamabad Property Scraper")
    log.info("=" * 60)
    df = scrape(TARGET_LISTINGS)
    print(df.head())
    print(f"\nShape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
