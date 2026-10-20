"""Search Kohl's, then read the ratings and latest reviews of the first product.

    python quickstart.py "jeans"
"""

import sys

from client import current_price, get, review_stats

keyword = sys.argv[1] if len(sys.argv) > 1 else "jeans"

# 1. Keyword search. Products come under payload.products; `count` is the total.
results = get("/product-search", keyword=keyword, pageLimit=10, sortID=1)
products = results["payload"]["products"] or []
print(f"{results['count']} products for {keyword!r}, showing {len(products)}\n")
for product in products:
    regular, sale, label, _ = current_price(product)
    rating = product.get("rating") or {}
    # New products have no ratings yet: avgRating and count are null.
    stars = f"{rating['avgRating']} stars x {rating['count']}" if rating.get("count") else "no ratings"
    print(
        f"{product['webID']:>8}  ${sale or regular:>7,.2f} (reg ${regular:,.2f}, {label})  "
        f"{stars:<18} {product['productTitle']}"
    )

if not products:
    raise SystemExit("No products found")

# 2. Reviews for the first product. productID is the webID from search.
first = products[0]
reviews = get("/product-reviews", productID=first["webID"], limit=3)["response"]
every = review_stats(reviews)
written = review_stats(reviews, filtered=True)
print(f"\n{first['productTitle']}")
print(
    f"  {every.get('TotalReviewCount')} ratings, average {every.get('AverageOverallRating', 0):.2f} "
    f"({every.get('RatingsOnlyReviewCount')} without text)"
)
print(
    f"  {reviews['TotalResults']} written reviews returned by the API, "
    f"average {written.get('AverageOverallRating', 0):.2f}"
)
for review in reviews["Results"]:
    print(f"  {review['Rating']}/5  {review['SubmissionTime'][:10]}  {review.get('Title') or ''}")
