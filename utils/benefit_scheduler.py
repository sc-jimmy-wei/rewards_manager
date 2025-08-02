"""
Comprehensive Benefit Scheduler - Handles periodic reset of credit benefits based on their frequency.

This scheduler implements the following reset logic:
- Monthly: Reset on 1st day of every month
- Quarterly: Reset on Jan 1st, April 1st, July 1st, Oct 1st
- Bi-yearly: Reset on Jan 1st and July 1st
- Annual: Reset on Jan 1st (calendar) or card anniversary date (card_anniversary)
- Every 4 years: Reset every 4 years from last reset

This service should be run daily to check and reset benefits as needed.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from models import db, BenefitTracker, BenefitTemplate, CreditCard
from app import create_app


class BenefitScheduler:
    """Handles periodic reset of credit benefits with comprehensive frequency support."""
    
    @staticmethod
    def reset_expired_benefits():
        """Check and reset all benefits that have expired based on their frequency."""
        app = create_app()
        
        with app.app_context():
            # Get all benefit trackers
            trackers = BenefitTracker.query.join(BenefitTemplate).filter(
                BenefitTemplate.benefit_type == 'Credit',
                BenefitTemplate.frequency.isnot(None)
            ).all()
            
            reset_count = 0
            today = date.today()
            
            print(f"Checking {len(trackers)} benefit trackers for resets on {today}...")
            
            for tracker in trackers:
                try:
                    if tracker.should_reset():
                        old_amount = tracker.used_amount
                        tracker.reset_if_needed()
                        reset_count += 1
                        
                        frequency = tracker.benefit_template.frequency
                        reset_type = tracker.benefit_template.reset_type or 'calendar'
                        
                        print(f"✓ Reset {frequency} benefit: {tracker.benefit_template.benefit_name}")
                        print(f"  Card: {tracker.credit_card.bank} {tracker.credit_card.name}")
                        print(f"  Reset type: {reset_type}")
                        print(f"  Used amount reset from ${old_amount:.2f} to $0.00")
                        print(f"  Available: ${tracker.benefit_template.amount:.2f}")
                        print()
                except Exception as e:
                    print(f"✗ Error resetting benefit {tracker.id}: {e}")
            
            # Commit all changes
            try:
                db.session.commit()
                print(f"Benefit reset job completed successfully.")
                print(f"Summary: {reset_count} benefits were reset out of {len(trackers)} checked.")
            except Exception as e:
                print(f"Error committing changes: {e}")
                db.session.rollback()
                
            return reset_count
    
    @staticmethod 
    def check_benefits_status():
        """Check status of all benefits without resetting them."""
        app = create_app()
        
        with app.app_context():
            trackers = BenefitTracker.query.join(BenefitTemplate).filter(
                BenefitTemplate.benefit_type == 'Credit'
            ).all()
            
            today = date.today()
            print(f"Benefit Status Report - {today}")
            print("=" * 70)
            
            for tracker in trackers:
                template = tracker.benefit_template
                card = tracker.credit_card
                
                print(f"Card: {card.bank} {card.name} (ID: {card.id})")
                print(f"Benefit: {template.benefit_name}")
                print(f"Frequency: {template.frequency}")
                print(f"Reset Type: {template.reset_type or 'calendar'}")
                if card.opening_date:
                    print(f"Card Opening Date: {card.opening_date}")
                print(f"Used: ${tracker.used_amount:.2f}")
                if template.amount:
                    print(f"Remaining: ${tracker.get_remaining_amount():.2f}")
                    print(f"Total Available: ${template.amount:.2f}")
                print(f"Last Reset: {tracker.last_reset_date}")
                print(f"Should Reset Today: {tracker.should_reset()}")
                
                # Show next reset date
                next_reset = BenefitScheduler._calculate_next_reset_date(tracker)
                if next_reset:
                    print(f"Next Reset Date: {next_reset}")
                
                print("-" * 50)
    
    @staticmethod
    def _calculate_next_reset_date(tracker):
        """Calculate the next reset date for a benefit tracker."""
        if not tracker.benefit_template.frequency:
            return None
            
        frequency = tracker.benefit_template.frequency
        last_reset = tracker.last_reset_date
        today = date.today()
        
        if frequency == 'monthly':
            # Next first day of month
            if today.day == 1:
                return today + relativedelta(months=1, day=1)
            else:
                return today.replace(day=1) + relativedelta(months=1)
        
        elif frequency == 'quarterly':
            # Next quarter start (Jan, Apr, Jul, Oct)
            quarter_starts = [1, 4, 7, 10]
            current_quarter = max([m for m in quarter_starts if m <= today.month])
            next_quarter_idx = (quarter_starts.index(current_quarter) + 1) % 4
            next_quarter_month = quarter_starts[next_quarter_idx]
            
            if next_quarter_month > today.month:
                return date(today.year, next_quarter_month, 1)
            else:
                return date(today.year + 1, next_quarter_month, 1)
        
        elif frequency == 'bi-yearly':
            # Next Jan 1 or Jul 1
            if today < date(today.year, 7, 1):
                return date(today.year, 7, 1)
            else:
                return date(today.year + 1, 1, 1)
        
        elif frequency == 'annual':
            reset_type = tracker.benefit_template.reset_type or 'calendar'
            
            if reset_type == 'calendar':
                # Next January 1st
                return date(today.year + 1, 1, 1)
            
            elif reset_type == 'card_anniversary':
                if not tracker.credit_card.opening_date:
                    return date(today.year + 1, 1, 1)
                
                opening_date = tracker.credit_card.opening_date
                try:
                    anniversary_this_year = opening_date.replace(year=today.year)
                except ValueError:
                    anniversary_this_year = opening_date.replace(year=today.year, day=28)
                
                if today < anniversary_this_year:
                    return anniversary_this_year
                else:
                    try:
                        return opening_date.replace(year=today.year + 1)
                    except ValueError:
                        return opening_date.replace(year=today.year + 1, day=28)
        
        elif frequency == 'every_4_years':
            return last_reset + relativedelta(years=4)
        
        return None
    
    @staticmethod
    def reset_specific_frequency(frequency):
        """Reset benefits of a specific frequency."""
        app = create_app()
        
        with app.app_context():
            trackers = BenefitTracker.query.join(BenefitTemplate).filter(
                BenefitTemplate.frequency == frequency,
                BenefitTemplate.benefit_type == 'Credit'
            ).all()
            
            reset_count = 0
            today = date.today()
            
            print(f"Checking {frequency} benefits for reset on {today}...")
            
            for tracker in trackers:
                if tracker.should_reset():
                    tracker.reset_if_needed()
                    reset_count += 1
                    print(f"Reset {frequency} benefit: {tracker.benefit_template.benefit_name}")
            
            db.session.commit()
            print(f"{frequency.title()} benefits reset: {reset_count}")
            return reset_count
    
    @staticmethod
    def force_reset_all():
        """Force reset all credit benefits (for testing/admin purposes)."""
        app = create_app()
        
        with app.app_context():
            trackers = BenefitTracker.query.join(BenefitTemplate).filter(
                BenefitTemplate.benefit_type == 'Credit'
            ).all()
            
            reset_count = 0
            
            for tracker in trackers:
                tracker.used_amount = 0.0
                tracker.last_reset_date = date.today()
                tracker.updated_at = datetime.utcnow()
                reset_count += 1
            
            db.session.commit()
            print(f"Force reset completed. {reset_count} benefits were reset.")
            return reset_count
    
    @staticmethod
    def simulate_date_reset(target_date):
        """Simulate running the scheduler on a specific date (for testing)."""
        app = create_app()
        
        # This is a simulation - we won't actually change the system date
        # Instead, we'll check what would happen if we ran the scheduler on target_date
        
        with app.app_context():
            trackers = BenefitTracker.query.join(BenefitTemplate).filter(
                BenefitTemplate.benefit_type == 'Credit',
                BenefitTemplate.frequency.isnot(None)
            ).all()
            
            print(f"Simulation: Running scheduler on {target_date}")
            print("=" * 50)
            
            would_reset = []
            
            for tracker in trackers:
                # Temporarily modify the date checking logic for simulation
                original_should_reset = tracker.should_reset
                
                def simulated_should_reset():
                    # This is a simplified simulation - in practice you'd need to 
                    # modify the should_reset method to accept a date parameter
                    frequency = tracker.benefit_template.frequency
                    last_reset = tracker.last_reset_date
                    
                    if frequency == 'monthly':
                        return target_date.day == 1 and (target_date.year != last_reset.year or target_date.month != last_reset.month)
                    elif frequency == 'quarterly':
                        return target_date.day == 1 and target_date.month in [1, 4, 7, 10]
                    elif frequency == 'bi-yearly':
                        return target_date.day == 1 and target_date.month in [1, 7]
                    elif frequency == 'annual':
                        reset_type = tracker.benefit_template.reset_type or 'calendar'
                        if reset_type == 'calendar':
                            return target_date.day == 1 and target_date.month == 1
                        # Add more simulation logic as needed
                    
                    return False
                
                if simulated_should_reset():
                    would_reset.append(tracker)
                    print(f"Would reset: {tracker.benefit_template.benefit_name}")
                    print(f"  Card: {tracker.credit_card.bank} {tracker.credit_card.name}")
                    print(f"  Frequency: {tracker.benefit_template.frequency}")
                    print()
            
            print(f"Simulation complete. {len(would_reset)} benefits would be reset on {target_date}")
            return would_reset


def run_daily_benefit_reset():
    """Entry point for daily benefit reset job."""
    scheduler = BenefitScheduler()
    return scheduler.reset_expired_benefits()


def run_monthly_benefit_reset():
    """Entry point for monthly benefit reset job (can be run on first of month)."""
    scheduler = BenefitScheduler()
    return scheduler.reset_specific_frequency('monthly')


def run_quarterly_benefit_reset():
    """Entry point for quarterly benefit reset job."""
    scheduler = BenefitScheduler()
    return scheduler.reset_specific_frequency('quarterly')


def run_bi_yearly_benefit_reset():
    """Entry point for bi-yearly benefit reset job."""
    scheduler = BenefitScheduler()
    return scheduler.reset_specific_frequency('bi-yearly')


def run_annual_benefit_reset():
    """Entry point for annual benefit reset job."""
    scheduler = BenefitScheduler()
    return scheduler.reset_specific_frequency('annual')


if __name__ == "__main__":
    import sys
    from datetime import datetime
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "reset":
            run_daily_benefit_reset()
        elif command == "monthly":
            run_monthly_benefit_reset()
        elif command == "quarterly":
            run_quarterly_benefit_reset()
        elif command == "bi-yearly":
            run_bi_yearly_benefit_reset()
        elif command == "annual":
            run_annual_benefit_reset()
        elif command == "status":
            scheduler = BenefitScheduler()
            scheduler.check_benefits_status()
        elif command == "force-reset":
            scheduler = BenefitScheduler()
            scheduler.force_reset_all()
        elif command == "simulate":
            if len(sys.argv) > 2:
                try:
                    target_date = datetime.strptime(sys.argv[2], "%Y-%m-%d").date()
                    scheduler = BenefitScheduler()
                    scheduler.simulate_date_reset(target_date)
                except ValueError:
                    print("Invalid date format. Use YYYY-MM-DD")
            else:
                print("Simulate command requires a date argument: python benefit_scheduler.py simulate 2024-01-01")
        else:
            print("Usage: python benefit_scheduler.py [command]")
            print("Commands:")
            print("  reset         - Run daily reset check (checks all frequencies)")
            print("  monthly       - Reset only monthly benefits")
            print("  quarterly     - Reset only quarterly benefits")
            print("  bi-yearly     - Reset only bi-yearly benefits")
            print("  annual        - Reset only annual benefits")
            print("  status        - Check status of all benefits")
            print("  force-reset   - Force reset all benefits (admin only)")
            print("  simulate DATE - Simulate reset on specific date (YYYY-MM-DD)")
    else:
        print("Running daily benefit reset...")
        run_daily_benefit_reset()