"""
Benefit Controller - Handles business logic for benefit tracking and management.
"""

from datetime import date, datetime
from flask_login import current_user
from models import db, BenefitTemplate, BenefitTracker, CreditCard


class BenefitController:
    """Handles business logic for benefit operations."""
    
    @staticmethod
    def get_benefit_trackers_for_card(card_id, user_id=None):
        """Get all benefit trackers for a specific credit card."""
        # Verify user has access to this card
        card = CreditCard.query.get(card_id)
        if not card:
            return []
        
        # Check access permissions
        if current_user.is_authenticated:
            if card.user_id != current_user.id and not current_user.is_admin():
                return []
        elif user_id and card.user_id != user_id:
            return []
        else:
            return []
        
        # Get trackers and reset any that need it
        trackers = BenefitTracker.query.filter_by(credit_card_id=card_id).all()
        
        for tracker in trackers:
            tracker.reset_if_needed()
        
        db.session.commit()
        return trackers
    
    @staticmethod
    def use_credit_benefit(tracker_id, amount_used, user_id=None):
        """Record usage of a credit benefit."""
        tracker = BenefitTracker.query.get(tracker_id)
        if not tracker:
            raise ValueError("Benefit tracker not found")
        
        # Verify user has access to this tracker's card
        card = tracker.credit_card
        if current_user.is_authenticated:
            if card.user_id != current_user.id and not current_user.is_admin():
                raise ValueError("Access denied")
        elif user_id and card.user_id != user_id:
            raise ValueError("Access denied")
        else:
            raise ValueError("Authentication required")
        
        # Verify this is a credit benefit
        if tracker.benefit_template.benefit_type != 'Credit':
            raise ValueError("Can only track usage for credit benefits")
        
        # Check if amount is valid
        if amount_used <= 0:
            raise ValueError("Amount must be positive")
        
        # Check if this would exceed the benefit limit
        remaining = tracker.get_remaining_amount()
        if remaining is not None and amount_used > remaining:
            raise ValueError(f"Amount exceeds remaining benefit limit (${remaining} remaining)")
        
        # Record the usage
        tracker.use_benefit(amount_used)
        db.session.commit()
        
        return tracker
    
    @staticmethod
    def reset_benefit_tracker(tracker_id, user_id=None):
        """Manually reset a benefit tracker."""
        tracker = BenefitTracker.query.get(tracker_id)
        if not tracker:
            raise ValueError("Benefit tracker not found")
        
        # Verify user has access
        card = tracker.credit_card
        if current_user.is_authenticated:
            if card.user_id != current_user.id and not current_user.is_admin():
                raise ValueError("Access denied")
        elif user_id and card.user_id != user_id:
            raise ValueError("Access denied")
        else:
            raise ValueError("Authentication required")
        
        # Reset the tracker
        tracker.used_amount = 0.0
        tracker.last_reset_date = date.today()
        tracker.updated_at = datetime.utcnow()
        
        db.session.commit()
        return tracker
    
    @staticmethod
    def get_benefit_summary_for_card(card_id, user_id=None):
        """Get a summary of benefit usage for a card."""
        trackers = BenefitController.get_benefit_trackers_for_card(card_id, user_id)
        
        summary = {
            'total_benefits': len(trackers),
            'credit_benefits': 0,
            'total_used': 0.0,
            'total_remaining': 0.0,
            'benefits_due_for_reset': 0,
            'benefits': []
        }
        
        for tracker in trackers:
            if tracker.benefit_template.benefit_type == 'Credit':
                summary['credit_benefits'] += 1
                summary['total_used'] += tracker.used_amount
                
                remaining = tracker.get_remaining_amount()
                if remaining is not None:
                    summary['total_remaining'] += remaining
                
                if tracker.should_reset():
                    summary['benefits_due_for_reset'] += 1
                
                summary['benefits'].append({
                    'tracker': tracker,
                    'template': tracker.benefit_template,
                    'used_amount': tracker.used_amount,
                    'remaining_amount': remaining,
                    'should_reset': tracker.should_reset(),
                    'last_reset': tracker.last_reset_date
                })
        
        return summary
    
    @staticmethod
    def create_trackers_for_card(card_id, user_id=None):
        """Create benefit trackers for a card based on available benefit templates."""
        card = CreditCard.query.get(card_id)
        if not card:
            raise ValueError("Card not found")
        
        # Verify user has access
        if current_user.is_authenticated:
            if card.user_id != current_user.id and not current_user.is_admin():
                raise ValueError("Access denied")
        elif user_id and card.user_id != user_id:
            raise ValueError("Access denied")
        else:
            raise ValueError("Authentication required")
        
        # Find benefit templates for this card
        templates = BenefitTemplate.query.filter_by(
            bank=card.bank,
            card_name=card.name
        ).all()
        
        created_count = 0
        for template in templates:
            # Only create trackers for credit benefits with amounts
            if template.benefit_type == 'Credit' and template.amount:
                # Check if tracker already exists
                existing = BenefitTracker.query.filter_by(
                    credit_card_id=card_id,
                    benefit_template_id=template.id
                ).first()
                
                if not existing:
                    tracker = BenefitTracker(
                        credit_card_id=card_id,
                        benefit_template_id=template.id,
                        used_amount=0.0
                    )
                    db.session.add(tracker)
                    created_count += 1
        
        db.session.commit()
        return created_count