from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask_sqlalchemy import SQLAlchemy
from models.credit_card import db


class BenefitTemplate(db.Model):
    """Template for credit card benefits that can be applied to user cards."""
    
    __tablename__ = 'benefit_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    bank = db.Column(db.String(50), nullable=False)
    card_name = db.Column(db.String(100), nullable=False)
    benefit_name = db.Column(db.String(200), nullable=False)
    benefit_type = db.Column(db.String(20), nullable=False)  # 'Credit' or 'Reward'
    category = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Float, nullable=True)
    rate = db.Column(db.Float, nullable=True)
    unit = db.Column(db.String(20), nullable=True)  # 'points', 'miles', 'cashback'
    frequency = db.Column(db.String(20), nullable=True)  # 'monthly', 'quarterly', 'bi-yearly', 'annual', 'every_4_years'
    reset_type = db.Column(db.String(20), nullable=True)  # 'calendar' or 'card_anniversary' (for annual benefits)
    note = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(500), nullable=True)  # URL to card image
    
    def __init__(self, bank, card_name, benefit_name, benefit_type, **kwargs):
        self.bank = bank
        self.card_name = card_name
        self.benefit_name = benefit_name
        self.benefit_type = benefit_type
        self.category = kwargs.get('category')
        self.amount = kwargs.get('amount')
        self.rate = kwargs.get('rate')
        self.unit = kwargs.get('unit')
        self.frequency = kwargs.get('frequency')
        self.reset_type = kwargs.get('reset_type')
        self.note = kwargs.get('note')
        self.image_url = kwargs.get('image_url')
    
    def to_dict(self):
        return {
            'id': self.id,
            'bank': self.bank,
            'card_name': self.card_name,
            'benefit_name': self.benefit_name,
            'benefit_type': self.benefit_type,
            'category': self.category,
            'amount': self.amount,
            'rate': self.rate,
            'unit': self.unit,
            'frequency': self.frequency,
            'reset_type': self.reset_type,
            'note': self.note,
            'image_url': self.image_url
        }


class BenefitTracker(db.Model):
    """Tracks usage of credit benefits for user's credit cards."""
    
    __tablename__ = 'benefit_trackers'
    
    id = db.Column(db.Integer, primary_key=True)
    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_card.id'), nullable=False)
    benefit_template_id = db.Column(db.Integer, db.ForeignKey('benefit_templates.id'), nullable=False)
    used_amount = db.Column(db.Float, default=0.0)
    last_reset_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    credit_card = db.relationship('CreditCard', backref='benefit_trackers')
    benefit_template = db.relationship('BenefitTemplate', backref='trackers')
    
    def __init__(self, credit_card_id, benefit_template_id, used_amount=0.0):
        self.credit_card_id = credit_card_id
        self.benefit_template_id = benefit_template_id
        self.used_amount = used_amount
        self.last_reset_date = date.today()
    
    def should_reset(self):
        """Check if benefit tracker should be reset based on frequency and reset type."""
        if not self.last_reset_date or not self.benefit_template.frequency:
            return False
        
        today = date.today()
        frequency = self.benefit_template.frequency
        
        if frequency == 'monthly':
            # Reset on first day of every month
            return today.day == 1 and (today.year != self.last_reset_date.year or today.month != self.last_reset_date.month)
        
        elif frequency == 'quarterly':
            # Reset on Jan 1st, April 1st, July 1st, Oct 1st
            if today.day != 1:
                return False
            if today.month not in [1, 4, 7, 10]:
                return False
            # Check if we haven't reset in this quarter yet
            quarter_start_months = [1, 4, 7, 10]
            current_quarter_start = max([m for m in quarter_start_months if m <= today.month])
            last_quarter_start = max([m for m in quarter_start_months if m <= self.last_reset_date.month])
            return (today.year > self.last_reset_date.year or 
                   (today.year == self.last_reset_date.year and current_quarter_start > last_quarter_start))
        
        elif frequency == 'bi-yearly':
            # Reset on Jan 1st and July 1st
            if today.day != 1:
                return False
            if today.month not in [1, 7]:
                return False
            # Check if we haven't reset in this half-year yet
            if today.month == 1:  # January 1st
                return (today.year > self.last_reset_date.year or 
                       (today.year == self.last_reset_date.year and self.last_reset_date.month >= 7))
            else:  # July 1st
                return (today.year == self.last_reset_date.year and self.last_reset_date.month < 7)
        
        elif frequency == 'annual':
            reset_type = self.benefit_template.reset_type or 'calendar'
            
            if reset_type == 'calendar':
                # Reset on January 1st
                return today.day == 1 and today.month == 1 and today.year > self.last_reset_date.year
            
            elif reset_type == 'card_anniversary':
                # Reset on card opening anniversary
                if not self.credit_card.opening_date:
                    # Fallback to calendar year if no opening date
                    return today.day == 1 and today.month == 1 and today.year > self.last_reset_date.year
                
                opening_date = self.credit_card.opening_date
                # Calculate this year's anniversary
                try:
                    anniversary_this_year = opening_date.replace(year=today.year)
                except ValueError:
                    # Handle leap year edge case (Feb 29)
                    anniversary_this_year = opening_date.replace(year=today.year, day=28)
                
                # If today's anniversary has passed and we haven't reset this year
                if today >= anniversary_this_year:
                    last_anniversary = anniversary_this_year
                    if self.last_reset_date.year < today.year:
                        return True
                    # Check if last reset was before this year's anniversary
                    return self.last_reset_date < last_anniversary
                else:
                    # This year's anniversary hasn't come yet, check last year's
                    try:
                        anniversary_last_year = opening_date.replace(year=today.year - 1)
                    except ValueError:
                        anniversary_last_year = opening_date.replace(year=today.year - 1, day=28)
                    return self.last_reset_date < anniversary_last_year
        
        elif frequency == 'every_4_years':
            # Reset every 4 years from last reset
            next_reset = self.last_reset_date + relativedelta(years=4)
            return today >= next_reset
        
        return False
    
    def reset_if_needed(self):
        """Reset usage if the time period has elapsed."""
        if self.should_reset():
            self.used_amount = 0.0
            self.last_reset_date = date.today()
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_remaining_amount(self):
        """Get remaining credit amount."""
        if not self.benefit_template.amount:
            return None
        return max(0, self.benefit_template.amount - self.used_amount)
    
    def use_benefit(self, amount):
        """Record usage of a credit benefit."""
        if self.benefit_template.benefit_type != 'Credit':
            raise ValueError("Can only use credit benefits")
        
        self.reset_if_needed()
        self.used_amount += amount
        self.updated_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            'id': self.id,
            'credit_card_id': self.credit_card_id,
            'benefit_template': self.benefit_template.to_dict() if self.benefit_template else None,
            'used_amount': self.used_amount,
            'remaining_amount': self.get_remaining_amount(),
            'last_reset_date': self.last_reset_date.isoformat() if self.last_reset_date else None,
            'should_reset': self.should_reset(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class CardBenefitTemplate(db.Model):
    """Association table for linking credit cards to their benefit templates."""
    
    __tablename__ = 'card_benefit_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    bank = db.Column(db.String(50), nullable=False)
    card_name = db.Column(db.String(100), nullable=False)
    
    def __init__(self, bank, card_name):
        self.bank = bank
        self.card_name = card_name
    
    def get_benefit_templates(self):
        """Get all benefit templates for this card."""
        return BenefitTemplate.query.filter_by(
            bank=self.bank,
            card_name=self.card_name
        ).all()
    
    def to_dict(self):
        return {
            'id': self.id,
            'bank': self.bank,
            'card_name': self.card_name,
            'benefits': [bt.to_dict() for bt in self.get_benefit_templates()]
        }