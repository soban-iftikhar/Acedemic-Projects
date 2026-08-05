import re
import json
import scrapy
from dataclasses import dataclass, field
from leads_scraper.spiders.base_spider import BaseSpider


@dataclass
class SearchTarget:
    city_name: str
    city_id: int
    canonical_category: str
    platform_category: str
    purpose_name: str
    purpose_id: int


class ZameenFieldExtractor:
    """Pulls all item fields out of a property detail response."""

    SELECTORS = {
        "title": "[aria-label='Title']::text",
        "location": "[aria-label='Property header']::text",
        "locality": "span[aria-label='Location']::text",
        "price": "span[aria-label='Price']::text",
        "size": "[aria-label='Area'] *::text",
        "bedrooms": "[aria-label='Beds']::text",
        "bathrooms": "[aria-label='Baths']::text",
        "added_date": "span[aria-label='Creation date']::text",
        "seller_name": "[aria-label='Agent name']::text",
        "agency_name": "[aria-label='Agency info'] div::text",
    }

    FALLBACKS = {
        "location": "[aria-label='Breadcrumb'] span:last-child::text",
        "added_date": "[aria-label='Listing creation date']::text",
        "seller_name": "[aria-label='Seller name']::text",
        "agency_name": "[aria-label='Agency name']::text",
    }

    @classmethod
    def text(cls, response, field_name, default=""):
        val = response.css(cls.SELECTORS[field_name]).get()
        if not val and field_name in cls.FALLBACKS:
            val = response.css(cls.FALLBACKS[field_name]).get()
        return (val or default).strip()

    @classmethod
    def description(cls, response):
        parts = response.css("[aria-label='Property description'] *::text").getall()
        return " ".join(p.strip() for p in parts if p.strip())

    @classmethod
    def amenities(cls, response):
        raw = response.css(
            "[aria-label='Amenities'] span::text, [aria-label='Features'] span::text"
        ).getall()
        return [a.strip() for a in raw if a.strip()]

    @classmethod
    def agency_profile_url(cls, response):
        href = response.css(
            "[aria-label='Agency profile']::attr(href), a[title*='Agency']::attr(href)"
        ).get("")
        if href and not href.startswith("http"):
            return f"https://www.zameen.com{href}"
        return href

    @classmethod
    def looks_blocked(cls, response):
        return response.status in (403, 429) or (
            not response.css("span[aria-label='Price']::text").get()
            and not response.css("[aria-label='Title']::text").get()
        )


class ZameenSpider(BaseSpider):
    name = "zameen"
    platform_name = "zameen"
    allowed_domains = ["zameen.com"]
    BASE_URL = "https://www.zameen.com"

    CITY_IDS = {"Islamabad": 3, "Lahore": 2, "Karachi": 1, "Rawalpindi": 41, "Peshawar": 6}
    CATEGORY_MAP = {
        "house": "Homes", "flat": "Flats",
        "residential_plot": "Plots", "commercial_plot": "Plots",
        "shop": "Commercial", "office": "Commercial", "warehouse": "Commercial",
        "factory": "Commercial", "building": "Commercial", "commercial_other": "Commercial",
    }
    PURPOSE_IDS = {"sale": 1, "rent": 2}

    DEFAULT_CITIES = ("Islamabad", "Lahore", "Karachi")
    DEFAULT_CATEGORIES = ("house", "residential_plot")
    DEFAULT_PURPOSES = ("sale",)

    HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    LISTING_ID_RE = re.compile(r"-(\d+-\d+)-\d+\.html$")
    EXTERNAL_ID_RE = re.compile(r"-(\d{7,})-\d+-\d+\.html$")
    PAGE_NUM_RE = re.compile(r"-(\d+)(\.html)$")

    # ---------- target resolution ----------

    def _pick(self, requested, options_map, defaults, label):
        if requested:
            val = options_map.get(requested) if isinstance(options_map, dict) else requested
            if requested not in options_map:
                self.logger.error(f"[zameen] Unsupported {label}: {requested}")
                return {}
            return {requested: options_map[requested]}
        if self.full_scrape:
            return dict(options_map) if isinstance(options_map, dict) else {k: options_map[k] for k in options_map}
        return {k: options_map[k] for k in defaults}

    def _resolve_categories(self):
        if self.category:
            plat = self.platform_category(self.category)
            if not plat:
                self.logger.warning(f"[zameen] Category '{self.category}' not supported on Zameen")
                return {}
            return {self.category: plat}
        if self.full_scrape:
            seen, out = set(), {}
            for canon, plat in self.CATEGORY_MAP.items():
                if plat not in seen:
                    seen.add(plat)
                    out[canon] = plat
            return out
        return {c: self.CATEGORY_MAP[c] for c in self.DEFAULT_CATEGORIES}

    def _build_targets(self):
        cities = self._pick(self.city, self.CITY_IDS, self.DEFAULT_CITIES, "city")
        categories = self._resolve_categories()
        purposes = self._pick(self.purpose, self.PURPOSE_IDS, self.DEFAULT_PURPOSES, "purpose")

        targets = []
        for city_name, city_id in cities.items():
            for canon_cat, plat_cat in categories.items():
                for purpose_name, purpose_id in purposes.items():
                    targets.append(SearchTarget(city_name, city_id, canon_cat, plat_cat, purpose_name, purpose_id))
        return targets

    # ---------- requests ----------

    def start_requests(self):
        for target in self._build_targets():
            yield self._search_request(target, page=1)

    def _search_request(self, target: SearchTarget, page: int, url: str = None):
        url = url or (
            f"{self.BASE_URL}/{target.platform_category}/"
            f"{target.city_name}-{target.city_id}-{page}.html?purpose={target.purpose_id}"
        )
        return scrapy.Request(
            url=url,
            callback=self.parse,
            cb_kwargs={"page": page, "target": target},
            headers=self.HEADERS,
            errback=self.handle_error,
        )

    def parse(self, response, page, target: SearchTarget):
        self.logger.info(
            f"[zameen] [{target.city_name}/{target.canonical_category}/{target.purpose_name}] "
            f"page {page} — {response.url}"
        )

        listings = response.css("li[aria-label='Listing']")
        if not listings:
            self.logger.warning(f"[zameen] 0 listings: {response.url}")
            return

        for listing in listings:
            if not self.should_dispatch():
                return
            link = (
                listing.css("a[aria-label='Listing link']::attr(href)").get()
                or listing.css("a::attr(href)").get()
            )
            if not link:
                continue
            detail_url = link if link.startswith("http") else f"{self.BASE_URL}{link}"

            self.dispatched += 1
            yield scrapy.Request(
                url=detail_url,
                callback=self.parse_property,
                cb_kwargs={"target": target},
                meta={
                    "playwright": True,
                    "playwright_page_goto_kwargs": {"wait_until": "domcontentloaded", "timeout": 30000},
                },
                headers={**self.HEADERS, "Referer": response.url},
                errback=self.handle_error,
            )

        if self.should_dispatch() and page < self.max_pages:
            next_url = self._next_page_url(response, page)
            if next_url:
                yield self._search_request(target, page + 1, url=next_url)

    def _next_page_url(self, response, current_page):
        next_link = response.css("a[title='Next']::attr(href)").get()
        if next_link:
            return next_link if next_link.startswith("http") else f"{self.BASE_URL}{next_link}"

        base_url = response.url.split("?")[0]
        match = self.PAGE_NUM_RE.search(base_url)
        if not match:
            return None
        next_url = base_url.replace(f"-{match.group(1)}{match.group(2)}", f"-{current_page + 1}{match.group(2)}")
        if "?" in response.url:
            next_url += "?" + response.url.split("?", 1)[1]
        return next_url

    # ---------- property detail ----------

    def parse_property(self, response, target: SearchTarget):
        if self.max_records is not None and self.records_collected >= self.max_records:
            return
        if ZameenFieldExtractor.looks_blocked(response):
            self.logger.warning(f"[zameen] Blocked/empty [{response.status}]: {response.url}")
            return

        item = self._build_item_from_response(response, target)

        external_id = self._match(self.EXTERNAL_ID_RE, response.url)
        if not external_id:
            item["phone"] = ""
            item["mobile"] = ""
            yield item
            return

        yield scrapy.Request(
            url=f"{self.BASE_URL}/api/showNumbers?listingExternalID={external_id}&isProject=false",
            callback=self.parse_phone,
            cb_kwargs={"item": item},
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Referer": response.url,
                "X-Requested-With": "XMLHttpRequest",
            },
            errback=self.handle_error,
        )

    def _build_item_from_response(self, response, target: SearchTarget):
        ex = ZameenFieldExtractor
        item = self.build_item(is_project=False)
        item["listing_id"] = self._match(self.LISTING_ID_RE, response.url) or response.url.split("/")[-1]
        item["url"] = response.url
        item["city"] = target.city_name
        item["purpose"] = target.purpose_name
        item["category"] = target.canonical_category

        for field_name in ("title", "location", "locality", "price", "size",
                            "bedrooms", "bathrooms", "added_date", "seller_name", "agency_name"):
            item[field_name] = ex.text(response, field_name, default="0" if field_name in ("bedrooms", "bathrooms") else "")

        item["description"] = ex.description(response)
        item["amenities"] = ex.amenities(response)
        item["agency_profile_url"] = ex.agency_profile_url(response)
        return item

    def parse_phone(self, response, item):
        item["phone"], item["mobile"] = "", ""
        try:
            data = json.loads(response.text)
            if data.get("success"):
                contact = data.get("contact_details", {})
                phones = contact.get("phone", [])
                item["phone"] = phones[0] if phones else ""
                item["mobile"] = contact.get("mobile", "")
                api_agency = contact.get("agency_name", "")
                if api_agency and not item.get("agency_name"):
                    item["agency_name"] = api_agency
        except Exception as e:
            self.logger.warning(f"[zameen] Phone API error: {e} — status {response.status} — body: '{response.text[:150]}'")

        yield item

    @staticmethod
    def _match(pattern, url):
        m = pattern.search(url)
        return m.group(1) if m else ""