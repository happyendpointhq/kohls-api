// Kohl's API quickstart. Node 18+ (built-in fetch), no dependencies.
//   RAPIDAPI_KEY=... node quickstart.mjs jeans

const HOST = 'kohls-com.p.rapidapi.com';

async function get(path, params = {}) {
  const url = new URL(`https://${HOST}${path}`);
  for (const [key, value] of Object.entries(params)) {
    if (value != null) url.searchParams.set(key, value);
  }
  const res = await fetch(url, {
    headers: { 'x-rapidapi-host': HOST, 'x-rapidapi-key': process.env.RAPIDAPI_KEY },
  });
  if (!res.ok) throw new Error(`Kohl's API ${res.status}: ${await res.text()}`);
  return res.json();
}

const keyword = process.argv[2] ?? 'jeans';
const results = await get('/product-search', { keyword, pageLimit: 10, sortID: 4 });
console.log(`${results.count} products for "${keyword}", cheapest first`);
for (const product of results.payload.products ?? []) {
  // prices is a list of price windows; use the one marked current.
  const price = product.prices.find((p) => p.isCurrentPrice) ?? product.prices[0];
  const sale = price?.salePrice?.minPrice ?? price?.regularPrice?.minPrice;
  console.log(`${product.webID.padStart(8)}  $${sale}  ${product.productTitle}`);
}
