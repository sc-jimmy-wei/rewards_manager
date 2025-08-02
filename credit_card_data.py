"""
Combined credit card data including benefits and images for major banks.
This data is used to seed the database with benefit templates and provide card images.
"""

CREDIT_CARD_DATA = {
    "Chase": {
        "Sapphire Reserved": {
            "image_url": "/static/images/chase/chase_sapphire_reserve_card.png",
            "credits": [
                {"name": "Annual Travel Credit", "amount": 300, "frequency": "annual", "category": "travel"},
                {"name": "DoorDash Credit", "amount": 60, "frequency": "annual", "category": "dining"},
                {"name": "Lyft Credit", "amount": 120, "frequency": "annual", "category": "transportation"},
                {"name": "Global Entry/TSA PreCheck Credit", "amount": 100, "frequency": "every_4_years", "category": "travel"}
            ],
            "rewards": [
                {"category": "travel", "rate": 3, "unit": "points"},
                {"category": "dining", "rate": 3, "unit": "points"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        },
        "Sapphire Preferred": {
            "image_url": "/static/images/chase/chase_sapphire_preferred_card.png",
            "credits": [],
            "rewards": [
                {"category": "travel", "rate": 2, "unit": "points"},
                {"category": "dining", "rate": 2, "unit": "points"},
                {"category": "streaming", "rate": 2, "unit": "points"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        },
        "Freedom Flex": {
            "image_url": "/static/images/chase/chase_freedom_flex_card.jpeg",
            "credits": [],
            "rewards": [
                {"category": "quarterly_bonus", "rate": 5, "unit": "points", "note": "Up to $1,500 per quarter"},
                {"category": "drugstores", "rate": 3, "unit": "points"},
                {"category": "dining", "rate": 3, "unit": "points"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        },
        "Freedom": {
            "image_url": "/static/images/chase/chase_freedom_card.jpeg",
            "credits": [],
            "rewards": [
                {"category": "quarterly_bonus", "rate": 5, "unit": "points", "note": "Up to $1,500 per quarter"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        },
        "Business Ink Cash": {
            "image_url": "/static/images/chase/chase_ink_cash_card.png",
            "credits": [],
            "rewards": [
                {"category": "office_supplies", "rate": 5, "unit": "points", "note": "Up to $25,000 per year"},
                {"category": "internet_cable_phone", "rate": 5, "unit": "points", "note": "Up to $25,000 per year"},
                {"category": "gas_stations", "rate": 2, "unit": "points", "note": "Up to $25,000 per year"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        },
        "Business Ink Unlimited": {
            "image_url": "/static/images/chase/chase_ink_unlimited_card.png",
            "credits": [],
            "rewards": [
                {"category": "all_purchases", "rate": 1.5, "unit": "points"}
            ]
        },
        "Business Ink Preferred": {
            "image_url": "/static/images/chase/chase_ink_preferred_card.png",
            "credits": [],
            "rewards": [
                {"category": "travel", "rate": 3, "unit": "points"},
                {"category": "shipping", "rate": 3, "unit": "points"},
                {"category": "internet_cable_phone", "rate": 3, "unit": "points"},
                {"category": "advertising", "rate": 3, "unit": "points", "note": "Up to $150,000 per year"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        },
        "Marriott Bonvoy Boundless": {
            "image_url": "/static/images/chase/chase_marriott_bonvoy_boundless_card.png",
            "credits": [
                {"name": "Annual Free Night Award", "amount": 1, "frequency": "annual", "category": "hotel", "note": "Up to 35,000 points"}
            ],
            "rewards": [
                {"category": "marriott", "rate": 6, "unit": "points"},
                {"category": "other", "rate": 2, "unit": "points"}
            ]
        },
        "IHG Premier One Rewards": {
            "image_url": "/static/images/chase/chase_ihg_premier_card.png",
            "credits": [
                {"name": "Annual Free Night Award", "amount": 1, "frequency": "annual", "category": "hotel", "note": "Up to 40,000 points"}
            ],
            "rewards": [
                {"category": "ihg", "rate": 10, "unit": "points"},
                {"category": "gas_stations", "rate": 2, "unit": "points"},
                {"category": "grocery_stores", "rate": 2, "unit": "points"},
                {"category": "restaurants", "rate": 2, "unit": "points"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        }
    },
    "Citi": {
        "Double Cash": {
            "image_url": "/static/images/citi/citi_double_cash_credit_card.webp",
            "credits": [],
            "rewards": [
                {"category": "all_purchases", "rate": 2, "unit": "cashback", "note": "1% when you buy, 1% when you pay"}
            ]
        },
        "Strata Premier": {
            "image_url": "/static/images/citi/citi_strata_premier_credit_card.webp",
            "credits": [
                {"name": "Annual Hotel Credit", "amount": 100, "frequency": "annual", "category": "hotel"}
            ],
            "rewards": [
                {"category": "travel", "rate": 3, "unit": "points"},
                {"category": "gas_stations", "rate": 3, "unit": "points"},
                {"category": "grocery_stores", "rate": 3, "unit": "points"},
                {"category": "restaurants", "rate": 3, "unit": "points"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        },
        "Strata Elite": {
            "image_url": "/static/images/citi/citi_strata_elite_credit_card.webp",
            "credits": [
                {"name": "Annual Hotel Credit", "amount": 200, "frequency": "annual", "category": "hotel"},
                {"name": "Global Entry Credit", "amount": 100, "frequency": "every_4_years", "category": "travel"}
            ],
            "rewards": [
                {"category": "travel", "rate": 5, "unit": "points"},
                {"category": "restaurants", "rate": 5, "unit": "points"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        },
        "AAdvantage Platinum Select": {
            "image_url": "/static/images/citi/citi_aadvantage_platinum_elite_credit_card.webp",
            "credits": [
                {"name": "American Airlines Purchase Credit", "amount": 125, "frequency": "annual", "category": "airline"}
            ],
            "rewards": [
                {"category": "american_airlines", "rate": 2, "unit": "miles"},
                {"category": "gas_stations", "rate": 2, "unit": "miles"},
                {"category": "restaurants", "rate": 2, "unit": "miles"},
                {"category": "other", "rate": 1, "unit": "miles"}
            ]
        }
    },
    "American Express": {
        "Platinum": {
            "image_url": "/static/images/american_express/amex_platinum_card.avif",
            "credits": [
                {"name": "Airline Fee Credit", "amount": 200, "frequency": "annual", "category": "airline"},
                {"name": "Hotel Credit", "amount": 200, "frequency": "annual", "category": "hotel"},
                {"name": "Uber Credit", "amount": 200, "frequency": "annual", "category": "transportation", "note": "$15 monthly + $20 December"},
                {"name": "Saks Credit", "amount": 100, "frequency": "annual", "category": "shopping", "note": "$50 per 6 months"},
                {"name": "Entertainment Credit", "amount": 240, "frequency": "annual", "category": "entertainment", "note": "$20 monthly"},
                {"name": "Global Entry Credit", "amount": 100, "frequency": "every_4_years", "category": "travel"}
            ],
            "rewards": [
                {"category": "flights", "rate": 5, "unit": "points"},
                {"category": "hotels", "rate": 5, "unit": "points"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        },
        "Gold": {
            "image_url": "/static/images/american_express/amex_gold_card.avif",
            "credits": [
                {"name": "Dining Credit", "amount": 120, "frequency": "annual", "category": "dining", "note": "$10 monthly"},
                {"name": "Uber Eats Credit", "amount": 120, "frequency": "annual", "category": "dining", "note": "$10 monthly"}
            ],
            "rewards": [
                {"category": "dining", "rate": 4, "unit": "points"},
                {"category": "us_supermarkets", "rate": 4, "unit": "points", "note": "Up to $25,000 per year"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        },
        "Green": {
            "image_url": "/static/images/american_express/amex_green_card.avif",
            "credits": [
                {"name": "LoungeBuddy Credit", "amount": 100, "frequency": "annual", "category": "travel"}
            ],
            "rewards": [
                {"category": "travel", "rate": 3, "unit": "points"},
                {"category": "transit", "rate": 3, "unit": "points"},
                {"category": "restaurants", "rate": 3, "unit": "points"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        },
        "Business Platinum": {
            "image_url": "/static/images/american_express/amex_business_platinum.avif",
            "credits": [
                {"name": "Airline Fee Credit", "amount": 200, "frequency": "annual", "category": "airline"},
                {"name": "Dell Credit", "amount": 400, "frequency": "annual", "category": "business", "note": "$200 per 6 months"},
                {"name": "Adobe Credit", "amount": 150, "frequency": "annual", "category": "business"},
                {"name": "Global Entry Credit", "amount": 100, "frequency": "every_4_years", "category": "travel"}
            ],
            "rewards": [
                {"category": "flights", "rate": 5, "unit": "points"},
                {"category": "hotels", "rate": 5, "unit": "points"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        },
        "Business Gold": {
            "image_url": "/static/images/american_express/amex_business_gold.avif",
            "credits": [],
            "rewards": [
                {"category": "top_2_categories", "rate": 4, "unit": "points", "note": "Automatically selected from advertising, shipping, gas, restaurants, computer hardware/software"},
                {"category": "other", "rate": 1, "unit": "points"}
            ]
        },
        "Blue Business Plus": {
            "image_url": "/static/images/american_express/amex_blue_business_plus_card.avif",
            "credits": [],
            "rewards": [
                {"category": "all_purchases", "rate": 2, "unit": "points", "note": "Up to $50,000 per year"},
                {"category": "over_50k", "rate": 1, "unit": "points"}
            ]
        }
    },
    "Capital One": {
        "Venture X": {
            "image_url": "/static/images/capital_one/c1_venture_x_card.avif",
            "credits": [
                {"name": "Annual Travel Credit", "amount": 300, "frequency": "annual", "category": "travel"},
                {"name": "Global Entry Credit", "amount": 100, "frequency": "every_4_years", "category": "travel"},
                {"name": "Annual Free Night Award", "amount": 1, "frequency": "annual", "category": "hotel", "note": "Up to 10,000 miles value"}
            ],
            "rewards": [
                {"category": "travel", "rate": 2, "unit": "miles"},
                {"category": "dining", "rate": 2, "unit": "miles"},
                {"category": "other", "rate": 1, "unit": "miles"}
            ]
        }
    },
    "Bank of America": {
        "Customized Cash Rewards": {
            "image_url": "/static/images/bank_of_america/boa__customize_cash_rewards_card.jpeg",
            "credits": [],
            "rewards": [
                {"category": "choice_category", "rate": 3, "unit": "cashback", "note": "Choose from gas, online shopping, dining, travel, drug stores, or home improvement/furnishings. Up to $2,500 per quarter"},
                {"category": "grocery_stores", "rate": 2, "unit": "cashback", "note": "Up to $2,500 per quarter"},
                {"category": "wholesale_clubs", "rate": 2, "unit": "cashback", "note": "Up to $2,500 per quarter"},
                {"category": "other", "rate": 1, "unit": "cashback"}
            ]
        }
    }
}

# Fallback placeholder images by bank
BANK_PLACEHOLDER_IMAGES = {
    "Chase": "https://via.placeholder.com/300x190/005CBB/FFFFFF?text=Chase",
    "American Express": "https://via.placeholder.com/300x190/006FCF/FFFFFF?text=Amex", 
    "Citi": "https://via.placeholder.com/300x190/D32F2F/FFFFFF?text=Citi",
    "Capital One": "https://via.placeholder.com/300x190/004879/FFFFFF?text=Capital+One",
    "Bank of America": "https://via.placeholder.com/300x190/E53E3E/FFFFFF?text=BofA"
}

def get_card_image_url(bank, card_name):
    """Get the image URL for a specific credit card."""
    if bank in CREDIT_CARD_DATA and card_name in CREDIT_CARD_DATA[bank]:
        card_data = CREDIT_CARD_DATA[bank][card_name]
        if "image_url" in card_data:
            return card_data["image_url"]
    
    # Fallback to bank placeholder
    if bank in BANK_PLACEHOLDER_IMAGES:
        return BANK_PLACEHOLDER_IMAGES[bank]
    else:
        return "https://via.placeholder.com/300x190/6C757D/FFFFFF?text=Credit+Card"

def get_card_benefits(bank, card_name):
    """Get the benefits data for a specific credit card."""
    if bank in CREDIT_CARD_DATA and card_name in CREDIT_CARD_DATA[bank]:
        card_data = CREDIT_CARD_DATA[bank][card_name]
        return {
            "credits": card_data.get("credits", []),
            "rewards": card_data.get("rewards", [])
        }
    return {"credits": [], "rewards": []}

def get_all_cards():
    """Get all available credit cards."""
    all_cards = {}
    for bank, cards in CREDIT_CARD_DATA.items():
        all_cards[bank] = list(cards.keys())
    return all_cards

def get_all_card_images():
    """Get all unique card images from the data."""
    result = {}
    for bank, cards in CREDIT_CARD_DATA.items():
        result[bank] = {}
        for card_name, card_data in cards.items():
            result[bank][card_name] = card_data.get("image_url", get_card_image_url(bank, card_name))
    return result