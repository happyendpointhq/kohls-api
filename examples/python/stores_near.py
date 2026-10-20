"""List Kohl's stores near a point.

    python stores_near.py 40.941111 -73.982308 --radius 10
"""

import argparse

from client import get, parse_store


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("latitude", type=float)
    parser.add_argument("longitude", type=float)
    parser.add_argument("--radius", type=int, default=25, help="miles")
    args = parser.parse_args()

    data = get("/store-locator", latitude=args.latitude, longitude=args.longitude, radius=args.radius)
    markers = data.get("markers") or []
    print(f"{len(markers)} stores within {args.radius} miles")
    for marker in markers:
        store = parse_store(marker)
        print(
            f"#{store.get('fid'):<5} {store.get('location_name')}, {store.get('address_1')}, "
            f"{store.get('city')}, {store.get('region')} {store.get('post_code')}"
        )
        if store["specialties"]:
            print(f"       {', '.join(store['specialties'])}")


if __name__ == "__main__":
    main()
