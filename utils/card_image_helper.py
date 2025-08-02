"""
Helper functions for credit card images.
"""

from models import BenefitTemplate
from credit_card_data import get_card_image_url


def get_card_image_from_template(bank, card_name):
    """Get card image URL from benefit template or fallback to placeholder."""
    # Try to get from benefit template first
    template = BenefitTemplate.query.filter_by(
        bank=bank, 
        card_name=card_name
    ).first()
    
    if template and template.image_url:
        return template.image_url
    
    # Fallback to our image data
    return get_card_image_url(bank, card_name)


def get_all_card_images():
    """Get all unique card images from benefit templates."""
    # Get unique bank/card combinations with their image URLs
    cards = BenefitTemplate.query.with_entities(
        BenefitTemplate.bank,
        BenefitTemplate.card_name, 
        BenefitTemplate.image_url
    ).distinct().all()
    
    result = {}
    for bank, card_name, image_url in cards:
        if bank not in result:
            result[bank] = {}
        result[bank][card_name] = image_url or get_card_image_url(bank, card_name)
    
    return result