"""Export a Kohl's keyword search to CSV with regular price, sale price and discount.

    python search_to_csv.py "throw blanket" --sort 7 --max-pages 2 --out blankets.csv
    python search_to_csv.py jeans --filter "Price:%2410%20to%20%2425" --out jeans.csv

--filter takes the dimension IDs a search returns in payload.dimensions[].dimensionValues[].ID,
comma-separated, exactly as returned (they are already URL-encoded). --sort: 1 Featured,
2 New Arrivals, 4 Price Low-High, 5 Price High-Low, 6 Highest Rated, 7 Percent Off.
"""

import argparse
import csv

from client import current_price, get

COLUMNS = [
    "webID", "productTitle", "regular_price", "sale_price", "discount_pct", "price_label",
    "sale_ends", "avg_rating", "rating_count", "badges", "ship", "pickup", "colors", "url",
]


def row_of(product):
    regular, sale, label, ends = current_price(product)
    rating = product.get("rating") or {}
    discount = round((regular - sale) / regular * 100) if regular and sale and sale < regular else 0
    return {
        "webID": product["webID"],
        "productTitle": product["productTitle"],
        "regular_price": regular,
        "sale_price": sale,
        "discount_pct": discount,
        "price_label": label,
        "sale_ends": ends,
        "avg_rating": rating.get("avgRating"),
        "rating_count": rating.get("count"),
        "badges": ";".join(product.get("valueAddedIcons") or []),
        "ship": product.get("isAvailableforShip"),
        "pickup": product.get("isAvailableforPickUp"),
        "colors": ";".join(product.get("availableColr") or []),
        "url": "https://www.kohls.com" + product.get("seoURL", ""),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("keyword")
    parser.add_argument("--sort", type=int, default=1)
    parser.add_argument("--filter", help="dimension IDs from payload.dimensions, comma-separated")
    parser.add_argument("--page-limit", type=int, default=120)
    parser.add_argument("--max-pages", type=int, default=5)
    parser.add_argument("--out", default="kohls-search.csv")
    args = parser.parse_args()

    written = 0
    with open(args.out, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        for page in range(1, args.max_pages + 1):
            data = get(
                "/product-search",
                keyword=args.keyword,
                page=page,
                pageLimit=args.page_limit,
                sortID=args.sort,
                dimensionValues=args.filter,
            )
            products = data["payload"]["products"] or []
            for product in products:
                writer.writerow(row_of(product))
                written += 1
            print(f"page {page}: {written} of {data['count']} products")
            if not products or written >= data["count"]:
                break
    print(f"Wrote {written} rows to {args.out}")


if __name__ == "__main__":
    main()
