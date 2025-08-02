# Credit Card Benefits Manager

A comprehensive web application for managing personal credit cards and tracking benefit usage with automatic reset functionality. Built with Flask following MVC architecture, featuring a modern dark UI, benefit tracking, and intelligent scheduling.

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.3+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Test Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen.svg)

## ✨ Key Features

### 💳 Card Management
- **Modern UI**: Dark theme with Geist font and responsive design
- **Card CRUD**: Create, edit, delete, and view credit cards with image uploads
- **Quick Add**: Pre-populated modal with 21+ major credit cards from 5 banks
- **Multi-Select**: Add multiple cards at once with visual feedback

### 🎁 Benefits Tracking System
- **Comprehensive Database**: 93 pre-loaded benefit templates
- **Automatic Reset**: Smart scheduling based on frequency patterns
- **Usage Tracking**: Interactive progress bars and checkboxes
- **Multi-User Support**: User authentication and data isolation

### 📅 Intelligent Reset Logic
- **Monthly**: 1st day of every month
- **Quarterly**: Jan 1st, April 1st, July 1st, Oct 1st
- **Bi-yearly**: Jan 1st and July 1st
- **Annual**: Calendar year (Jan 1st) or card anniversary date
- **4-Year Cycle**: For Global Entry/TSA PreCheck credits

### 🏦 Supported Credit Cards
- **Chase** (9 cards): Sapphire Reserved/Preferred, Freedom series, Business Ink series, Hotel co-brands
- **American Express** (6 cards): Platinum, Gold, Green, Business variants
- **Citi** (4 cards): Double Cash, Strata series, AAdvantage Platinum
- **Capital One** (1 card): Venture X
- **Bank of America** (1 card): Customized Cash Rewards

## 🚀 Quick Start

### 1. Installation
```bash
git clone <repository-url>
cd credit
uv sync  # or pip install -e .
```

### 2. Database Setup
```bash
# Seed users and benefit templates
uv run python seed_data.py

# Optional: Seed specific components
uv run python seed_data.py users      # Default users only
uv run python seed_data.py benefits   # Benefit templates only
```

### 3. Run Application
```bash
uv run python app.py
```
Access at: **http://localhost:5000**

**Default Accounts:**
- Admin: `admin` / `admin123`
- User: `testuser` / `test123`

## 🏗️ Architecture

**MVC Pattern** with clean separation:
- **Models** (`models/`): Data layer with SQLAlchemy ORM
- **Views** (`templates/`): Presentation layer with Jinja2 templates
- **Controllers** (`controllers/`): Business logic layer
- **Routes** (`routes/`): URL routing and request handling

### Core Components
```
├── app.py                           # Flask application factory
├── config.py                        # Environment configurations
├── seed_data.py                     # Comprehensive database seeding
├── credit_card_data.py              # Combined benefits and image data
│
├── models/                          # Database models
│   ├── credit_card.py              # Credit card model with opening_date
│   ├── benefit.py                  # Benefit templates and trackers
│   ├── user.py                     # User authentication
│   └── airline_program.py          # Airline miles tracking
│
├── controllers/                     # Business logic
│   ├── credit_card_controller.py   # Card CRUD and quick_add
│   ├── benefit_controller.py       # Benefit usage tracking
│   ├── auth_controller.py          # User authentication
│   └── file_controller.py          # Image upload handling
│
├── routes/                          # URL endpoints
│   ├── credit_card_routes.py       # Card management routes
│   └── auth_routes.py              # Authentication routes
│
├── utils/                           # Utilities
│   ├── benefit_scheduler.py        # Automatic reset scheduler
│   └── card_image_helper.py        # Image URL management
│
├── migrations/                      # Database operations
│   └── database.py                 # Schema migrations
│
└── templates/                       # UI templates
    ├── index.html                  # Main page with Quick Add modal
    ├── card_detail.html            # Card details and benefit tracking
    └── auth/                       # Authentication templates
```

## 📊 Database Schema

### Core Models

**CreditCard**
- Card details (name, bank, type, opening_date, credit_limit)
- JSON benefits and usage tracking
- Image upload support
- User association

**BenefitTemplate**
- Pre-defined benefits for each card
- Frequency and reset_type configuration
- Credit vs Reward classification
- Image URLs for card display

**BenefitTracker**
- Individual usage tracking per user/card
- Automatic reset logic
- Last reset date tracking

**User**
- Authentication and authorization
- Multi-user data isolation
- Admin and regular user roles

## ⚙️ Benefit Reset Scheduler

### Usage
```bash
# Daily reset check (recommended for cron)
uv run python utils/benefit_scheduler.py reset

# Check status and next reset dates
uv run python utils/benefit_scheduler.py status

# Frequency-specific resets
uv run python utils/benefit_scheduler.py monthly
uv run python utils/benefit_scheduler.py quarterly
uv run python utils/benefit_scheduler.py bi-yearly
uv run python utils/benefit_scheduler.py annual

# Admin/testing commands
uv run python utils/benefit_scheduler.py force-reset
uv run python utils/benefit_scheduler.py simulate 2025-01-01
```

### Reset Logic Features
- **Date-Specific**: Only resets on exact target dates
- **Anniversary Support**: Uses card opening dates for annual resets
- **Leap Year Handling**: Graceful Feb 29 edge case management
- **Simulation Mode**: Test scenarios without affecting data
- **Comprehensive Reporting**: Status, next reset dates, usage tracking

## 🧪 Testing

**91% Test Coverage** across all components:

```bash
# Run all tests
uv run pytest

# Coverage report
uv run pytest --cov=. --cov-report=html

# Custom test runner
uv run python run_tests.py --coverage
```

**Test Categories:**
- **Models** (24 tests): 100% coverage
- **Controllers** (60 tests): 99% coverage  
- **Routes** (24 tests): 81% coverage
- **Templates** (19 tests): 100% coverage
- **Database** (17 tests): 96% coverage

## 🚀 Production Deployment

### PostgreSQL Setup
```bash
# Set database URL
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"

# Initialize production database
uv run python setup_postgres.py

# Production run
FLASK_ENV=production uv run python app.py
```

### Environment Variables
```bash
export FLASK_ENV=production
export DATABASE_URL="postgresql://..."
export SECRET_KEY="your-secure-secret-key"
export UPLOAD_FOLDER="/path/to/uploads"
```

### Cloud Deployment Ready
- **Heroku**: PostgreSQL addon support
- **Railway**: Database service integration
- **Render**: PostgreSQL service compatible
- **AWS/GCP/Azure**: Managed database support

## 📖 Usage Guide

### Adding Cards
1. **Quick Add**: Click "Quick Add Card" → Select from pre-loaded templates
2. **Manual Add**: Click "Add New Card" → Fill custom details
3. **Multi-Select**: Choose multiple cards in Quick Add modal

### Benefits Management
1. Navigate to card detail view
2. Use checkboxes to track benefit usage
3. View progress bars and remaining amounts
4. Automatic resets based on card schedule

### User Management
- **Admin users**: View all data across users
- **Regular users**: Only see their own cards and benefits
- **Multi-tenant**: Complete data isolation between users

## 🔧 Configuration

### Development vs Production
- **Development**: SQLite default, PostgreSQL optional
- **Production**: PostgreSQL with connection pooling
- **Testing**: In-memory SQLite for speed

### Security Features
- **Password Hashing**: Secure user authentication
- **File Upload Validation**: Image type and size restrictions
- **CSRF Protection**: Form security
- **SQL Injection Prevention**: SQLAlchemy ORM protection

## 🛠️ Troubleshooting

### Common Issues
```bash
# Reset database
rm instance/credit_cards.db
uv run python seed_data.py

# Test database connection
uv run python -c "from app import create_app; app = create_app(); print('✓ App created successfully')"

# Run specific tests
uv run pytest tests/models/ -v
```

### Database Migration Issues
```bash
# Force migration
uv run python -c "
from app import create_app
from migrations.database import DatabaseManager
app = create_app()
with app.app_context():
    DatabaseManager.migrate_database()
"
```

## 📄 API Reference

### Key Endpoints
- `GET /` - Card listing with filters
- `POST /quick_add_card` - Add pre-configured cards
- `GET /card/<id>` - Card details with benefit tracking
- `POST /benefits_usage/<id>` - Update benefit usage
- `POST /auth/login` - User authentication

## 🎯 Future Enhancements

- **Email Notifications**: Benefit reset alerts
- **Usage Analytics**: Spending category analysis
- **Mobile App**: React Native companion
- **API Integration**: Real-time transaction monitoring
- **Advanced Reporting**: Usage trends and optimization suggestions

## 📜 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Bootstrap](https://getbootstrap.com/) - UI components
- [Geist Font](https://vercel.com/font) - Typography
- [SQLAlchemy](https://sqlalchemy.org/) - Database ORM

---

**Built with ❤️ for credit card optimization enthusiasts**