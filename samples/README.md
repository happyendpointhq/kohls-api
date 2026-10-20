# Sample responses

Responses from the live Kohl's API, captured on 20 October 2026. The API's public
documentation has no example responses, so these are real ones. They are trimmed: arrays
are cut to their first few items, search keeps four of its filter groups, and the store
locator's `maplist` HTML is dropped. Reviewer and author nicknames, author IDs, locations,
IP addresses and submission IDs are removed from the review and Q&A samples. Field names and
the remaining values are unchanged.

| File | Request |
|---|---|
| `product-search.json` | `GET /product-search?keyword=jeans&pageLimit=5` |
| `categories.json` | `GET /categories` |
| `product-reviews.json` | `GET /product-reviews?productID=5008379&limit=3` |
| `product-qnas.json` | `GET /product-qnas?productID=5008379&limit=3` |
| `store-locator.json` | `GET /store-locator?latitude=40.941111&longitude=-73.982308&radius=10` |

They are useful for writing parsers and tests before you subscribe. Prices, sale windows and
review counts change daily, so do not hard-code these values.
