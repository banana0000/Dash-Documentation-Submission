# data.py
"""Demo listing data for Roamly — a house-only stay/property platform."""

LISTINGS = {
    "canyon-overlook-cabin": {
        "id": "canyon-overlook-cabin",
        "title": "Canyon Overlook Cabin",
        "location": "Glen Canyon Region, Utah",
        "coords": [36.8791, -111.5109],
        "price": 189,
        "price_unit": "night",
        "rating": 4.92,
        "reviews": 214,
        "beds": 2,
        "baths": 1,
        "guests": 4,
        "summary": "A secluded cabin perched above a sweeping river canyon, surrounded by "
                   "dramatic redrock formations and cliffs — with a wraparound deck built "
                   "for watching the sunset.",
        "amenities": ["Wifi", "Kitchen", "Free parking", "Fire pit", "Hot tub"],
        "cover_image": "https://images.unsplash.com/photo-1561065091-4908548ee638?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1561065091-4908548ee638?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1615874959474-d609969a20ed?auto=format&fit=crop&w=800&q=80",
        ],
        "host": {"name": "Priya Nandakumar", "since": 2019, "listings": 3},
        "views_last_30d": [12, 18, 15, 22, 19, 27, 24, 31, 28, 35, 30, 41],
    },
    "heritage-house-victoria": {
        "id": "heritage-house-victoria",
        "title": "Sale Heritage House",
        "location": "Victoria, Texas",
        "coords": [28.8053, -96.9997],
        "price": 245,
        "price_unit": "night",
        "rating": 4.85,
        "reviews": 132,
        "beds": 4,
        "baths": 2,
        "guests": 8,
        "summary": "A beautifully preserved two-story colonial-revival home with wraparound "
                   "porches, original woodwork, and a shaded garden — full of historic "
                   "character throughout.",
        "amenities": ["Wifi", "Full kitchen", "Free parking", "Washer/dryer", "Garden"],
        "cover_image": "https://images.unsplash.com/photo-1594348352429-159508d48c57?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1594348352429-159508d48c57?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1616046229478-9901c5536a45?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1616486029423-aaa4789e8c9a?auto=format&fit=crop&w=800&q=80",
        ],
        "host": {"name": "Devon Walsh", "since": 2021, "listings": 1},
        "views_last_30d": [8, 11, 9, 14, 12, 16, 13, 19, 17, 22, 20, 26],
    },
    "atacama-mountain-retreat": {
        "id": "atacama-mountain-retreat",
        "title": "Cerro Toco Mountain Retreat",
        "location": "High Desert, Atacama Foothills, Chile",
        "coords": [-22.9587, -67.7797],
        "price": 268,
        "price_unit": "night",
        "rating": 4.97,
        "reviews": 88,
        "beds": 3,
        "baths": 2,
        "guests": 6,
        "summary": "An off-grid retreat with panoramic mountain views. Explore the grounds — "
                   "from the observation deck to the fire pit — before you book your stay.",
        "amenities": ["Solar power", "Telescope", "Fire pit", "Off-grid kitchen"],
        "cover_image": "https://images.unsplash.com/photo-1775449074495-fb6a4a84b5df?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1775449074495-fb6a4a84b5df?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1583847268964-b28dc8f51f92?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1633836331520-e35c668f1f9d?auto=format&fit=crop&w=800&q=80",
        ],
        "host": {"name": "Marco Ibáñez", "since": 2018, "listings": 2},
        "views_last_30d": [20, 24, 22, 29, 26, 33, 30, 38, 35, 44, 40, 52],
    },
}


def get_listing(listing_id):
    return LISTINGS.get(listing_id)


def list_listings():
    return list(LISTINGS.values())
