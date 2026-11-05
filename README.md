# Kohl's API and Scraper

The Kohl's API returns Kohls.com product data as JSON: keyword search with regular and sale
prices, sale windows, ratings, colors and shipping or pickup availability, plus the full
category tree, customer reviews with rating statistics, shopper questions and answers, and
store locations. Kohl's does not publish a public developer API for its catalog, so this REST
API is the way to use Kohl's product data in your own code without running a Kohl's scraper.

Built and maintained by [Happy Endpoint](https://happyendpoint.com/library/kohls-data?utm_source=github&utm_medium=readme&utm_campaign=kohls-api).

- Subscribe and test every endpoint on RapidAPI: https://rapidapi.com/happyendpoint/api/kohls-com
- Product page: https://happyendpoint.com/library/kohls-data?utm_source=github&utm_medium=readme&utm_campaign=kohls-api

---

## At a glance

| | |
|---|---|
| Base URL | `https://kohls-com.p.rapidapi.com` |
| Auth | `x-rapidapi-key` and `x-rapidapi-host` headers |
| Endpoints | 6, all `GET` |
| Coverage | Kohls.com, United States, prices in USD |
| Page size | Up to 120 products per search page (the default) |
| Format | JSON. Search and categories are wrapped in `payload`, reviews and Q&A in `response`, the store locator has no wrapper |

---

## What data you get

**Search**
- Products for a keyword, with six sort orders (Featured, New Arrivals, Price Low-High, Price High-Low, Highest Rated, Percent Off)
- Filters (dimensions) returned with every search, with product counts: brand, price band, size, color, fit, rating, pickup or shipping
- Per product: `webID`, title, image and swatches, regular price, sale price and the dates the sale price is shown for, price label, average rating and rating count, badges such as best seller, available colors, ship and pickup flags, SKU IDs, product page URL

**Reviews and Q&A**
- Written reviews with rating, title, text, date, verified purchaser badge and sub-ratings
- Rating statistics for every rating on the product: distribution by star, average, recommended counts, sub-rating averages (fit, quality, comfort, durability, value, style), reviewer context such as length of ownership
- Shopper questions with their answers, including answers posted by Kohl's

**Catalog and stores**
- The full category tree as shown in the Kohls.com menu, with category IDs and URLs
- Stores within a radius of a point: store number, name, address, coordinates, store badges

---

## Quick start

### 1. Get an API key

Subscribe on [RapidAPI](https://rapidapi.com/happyendpoint/api/kohls-com). Copy `.env.example` to `.env` and paste your key.

### 2. Make a request

```bash
curl "https://kohls-com.p.rapidapi.com/product-search?keyword=jeans&pageLimit=10" \
  -H "x-rapidapi-host: kohls-com.p.rapidapi.com" \
  -H "x-rapidapi-key: YOUR_RAPIDAPI_KEY"

curl "https://kohls-com.p.rapidapi.com/product-reviews?productID=5008379&limit=3" \
  -H "x-rapidapi-host: kohls-com.p.rapidapi.com" \
  -H "x-rapidapi-key: YOUR_RAPIDAPI_KEY"
```

### Python

```bash
pip install -r requirements.txt
cd examples/python
python quickstart.py jeans
```

```python
from client import current_price, get

results = get("/product-search", keyword="jeans", pageLimit=10)
for product in results["payload"]["products"]:
    regular, sale, label, ends = current_price(product)
    print(product["webID"], sale, regular, product["productTitle"])
```

### JavaScript

```bash
RAPIDAPI_KEY=your_key node examples/javascript/quickstart.mjs jeans
```

---

## Example response

One product from `GET /product-search?keyword=jeans`, trimmed. Captured from the live API on
20 October 2026; the full responses are in [`samples/`](samples/).

```json
{
  "payload": {
    "searchTerm": "jeans",
    "products": [
      {
        "webID": "5008379",
        "productTitle": "Men's Sonoma Goods For Life® Straight-Fit Flexwear Jean",
        "prices": [
          {
            "regularPrice": { "minPrice": 34.99, "maxPrice": null },
            "salePrice": { "minPrice": 29.99, "maxPrice": null },
            "displayBegDateTime": "2026/10/20 06:48:42 -0700",
            "displayEndDateTime": "2026/10/22 01:42:27 -0700",
            "isCurrentPrice": true,
            "priceLabel": "sale"
          }
        ],
        "rating": { "avgRating": 4.4, "count": 2140 },
        "valueAddedIcons": ["best_seller"],
        "availableColr": ["Medium Wash", "Black", "Rinse Wash"],
        "isAvailableforShip": true,
        "isAvailableforPickUp": false,
        "seoURL": "/product/prd-5008379/mens-sonoma-goods-for-life-straight-fit-flexwear-jean.jsp"
      }
    ]
  },
  "count": 72,
  "limit": 5,
  "offset": 1
}
```

---

## Endpoints

Base URL: `https://kohls-com.p.rapidapi.com`

| Endpoint | Returns |
|---|---|
| `GET /product-search` | Products for a `keyword`, with `page`, `pageLimit`, `sortID` and `dimensionValues` filters |
| `GET /categories` | The Kohls.com category tree |
| `GET /product-reviews` | Written reviews for a `productID`, plus rating statistics, with `limit` and `page` |
| `GET /product-qnas` | Questions for a `productID`, with their answers, `limit` and `page` |
| `GET /store-locator` | Stores within `radius` miles of `latitude` and `longitude` |
| `GET /health` | Service health |

---

## Things to know about the data

Observed against the live API on 20 October 2026. These are the mistakes that produce wrong
numbers rather than errors.

- **The rating count on a product is not the number of reviews you can download.** For the
  Sonoma Flexwear jean, `ReviewStatistics` counted 2,141 ratings averaging 4.43, but 1,283 of
  those were ratings without text. `/product-reviews` returns the written ones only:
  `TotalResults` was 858, and `FilteredReviewStatistics` (the stats for those 858) averaged
  4.22. Report the overall average from `ReviewStatistics`, and do not use `TotalResults` as
  the rating count. `quickstart.py` prints both.
- **The search card lags the review statistics slightly.** The same blanket showed
  `rating.count` 4,661 in search and 4,688 ratings in `/product-reviews` a moment later. Take
  rating counts from the reviews endpoint when they matter.
- **New products have null ratings.** `rating.avgRating` and `rating.count` are both `null`
  for unrated products; most of the Bedsure products in one "throw blanket" search had none.
- **`prices` is a list of price windows, and sale prices expire.** Each entry has
  `regularPrice` and `salePrice` as `{minPrice, maxPrice}` (`maxPrice` is null unless the
  product is a price range) and the dates the price is shown for. Use the entry with
  `isCurrentPrice: true`; in our test the jeans sale price ran for two days. Store
  `displayEndDateTime` with the price if you track prices.
- **Most products are on sale.** Every product in our sample searches was labelled `sale`,
  some at 60% below the regular price. Track the sale price over time rather than the
  discount percentage.
- **`count` depends on the sort order.** "jeans" returned `count: 72` sorted by Featured and
  54 sorted by Price Low-High. Read `count` from the same request you page through.
- **Sorting by price loosens the keyword match.** "jeans" sorted Price Low-High started with
  leggings, shorts and T-shirts. Keep the default sort, or filter by a price band with
  `dimensionValues`, when you need relevant results.
- **`offset` in the search response is the page number,** not a row offset (`offset: 1` on
  page 1). Reviews and Q&A use a real zero-based `Offset`.
- **Filter IDs are URL-encoded strings.** Pass them to `dimensionValues` exactly as a search
  returns them in `payload.dimensions[].dimensionValues[].ID`, for example
  `Price:%2410%20to%20%2425` for $10 to $25.
- **Sub-rating IDs carry suffixes and are not all "higher is better".** They come as
  `Fit_22`, `Comfort_1` and so on, in `SecondaryRatingsAveragesOrder`. Fit is a slider
  (`DisplayType: SLIDER`), so its 3.17 out of 5 for the jean is a position on a scale, not a
  poor score. Do not average it with quality or comfort.
- **Q&A answers live beside the questions.** Each question lists `AnswerIds`; the answers are
  in `Includes.Answers`, keyed by ID. Some answers are posted by Kohl's itself.
- **Store details are JSON inside an HTML string.** Each `/store-locator` marker has an
  `info` field holding a `<div>` that wraps the store's JSON (store number `fid`, address,
  city, region, post code). `client.parse_store()` extracts it.
- **`productID` is the `webID` from search.**

---

## Examples in this repo

| File | What it does |
|---|---|
| [`examples/python/quickstart.py`](examples/python/quickstart.py) | Keyword search with sale and regular prices, then rating statistics and the latest reviews of the first product |
| [`examples/python/search_to_csv.py`](examples/python/search_to_csv.py) | Exports a search to CSV with regular price, sale price, discount, sale end date, rating and badges |
| [`examples/python/product_insights.py`](examples/python/product_insights.py) | Star distribution, sub-ratings, recommendation counts and questions with their answers for one product |
| [`examples/python/stores_near.py`](examples/python/stores_near.py) | Kohl's stores near a point, parsed out of the store locator's HTML |
| [`examples/javascript/quickstart.mjs`](examples/javascript/quickstart.mjs) | Keyword search in Node 18+, no dependencies |
| [`samples/`](samples/) | Trimmed live responses for five endpoints |

---

## API or your own Kohl's scraper

A homemade Kohl's scraper has to keep up with the site's markup, bot protection and the
separate services behind search, reviews and stores, and it breaks when any of them change.
This API returns the same data as JSON with a stable contract, so the work you keep is the
analysis. If you need a full catalog export as a file instead of API calls,
[contact us](https://happyendpoint.com/contact?utm_source=github&utm_medium=readme&utm_campaign=kohls-api).

---

## Use it from Claude, Cursor or any MCP client

RapidAPI exposes every endpoint as an MCP tool, so an AI assistant can query Kohl's products
without code:

```json
{
  "mcpServers": {
    "kohls": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp.rapidapi.com",
        "--header",
        "x-api-host: kohls-com.p.rapidapi.com",
        "--header",
        "x-api-key: YOUR_RAPIDAPI_KEY"
      ]
    }
  }
}
```

| Client | Config path |
|---|---|
| Claude Desktop (macOS) | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Claude Desktop (Windows) | `%APPDATA%\Claude\claude_desktop_config.json` |
| Cursor | `~/.cursor/mcp.json` |
| Claude Code | `.mcp.json` in your project root |

---

## FAQ

### Does Kohl's have an API?

Kohl's does not publish a public developer API for its product catalog. This API, built and
maintained by Happy Endpoint and independent of Kohl's, provides that access as REST and JSON.

### Is there a free Kohl's API?

Yes. The [RapidAPI listing](https://rapidapi.com/happyendpoint/api/kohls-com) has a free plan, and every endpoint can be tried on it.

### Where is the Kohl's API documentation?

Every endpoint and parameter is documented on the RapidAPI listing, the endpoint table above
summarises them, and [`samples/`](samples/) has real responses to build parsers against.

### How do I scrape Kohl's product data with Python?

Install `requests`, set `RAPIDAPI_KEY`, and call `/product-search`.
[`search_to_csv.py`](examples/python/search_to_csv.py) pages through a search and writes
prices, discounts and ratings to CSV.

### Can I get Kohl's reviews and ratings?

Yes. `/product-reviews` returns written reviews and the product's full rating statistics,
including the star distribution and sub-ratings such as fit and comfort. See
[`product_insights.py`](examples/python/product_insights.py).

### Can I track Kohl's sale prices?

Yes. Every search result carries the regular price, the current sale price and the dates that
sale price is shown for. Run a search on a schedule and store the sale price with
`displayEndDateTime`.

### Can I find Kohl's store locations?

Yes. `/store-locator` returns stores within a radius of a point, with store number and
address.

### Do you cover other retailers?

Yes, including Sephora, IKEA, H&M and Tesco. See the
[API library](https://happyendpoint.com/library?utm_source=github&utm_medium=readme&utm_campaign=kohls-api).

---

## Related repos

- [awesome-ecommerce-data-apis](https://github.com/happyendpointhq/awesome-ecommerce-data-apis) - product, pricing and retail data APIs, including free and official ones
- [sephora-api](https://github.com/happyendpointhq/sephora-api) - Sephora products, prices, reviews and store availability
- [ikea-api](https://github.com/happyendpointhq/ikea-api) - IKEA product, category and store data
- [rent-com-api](https://github.com/happyendpointhq/rent-com-api) - the same repo layout for US rental listings

---

## Disclaimer

Happy Endpoint is an independent provider. This project is **not affiliated
with, endorsed by, sponsored by, or connected to** any of the websites,
platforms, retailers, or marketplaces referenced here or reachable through the
underlying APIs.

All product names, brands, trademarks, and registered trademarks are the
property of their respective owners. Any reference to them is descriptive only,
to identify the subject matter of the data, and does not imply any association
or endorsement.

Users are responsible for ensuring their use of any data complies with
applicable laws and the terms of service of the relevant source.

---

## About Happy Endpoint

[Happy Endpoint](https://happyendpoint.com) builds and maintains real-time data
APIs for property portals, retailers, and marketplaces. All APIs are available on
RapidAPI with a free tier.

- Catalogue: [happyendpoint.com/library](https://happyendpoint.com/library)
- Datasets: [happyendpoint.com/datasets](https://happyendpoint.com/datasets)
- Documentation: [docs.happyendpoint.com](https://docs.happyendpoint.com)
- Contact: hello@happyendpoint.com

## Licence

MIT. See [LICENSE](LICENSE).
