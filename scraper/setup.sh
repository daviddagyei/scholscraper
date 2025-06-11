#!/bin/bash

# Scholarship Scraper Setup Script
# Run this script to set up the scraping environment

set -e

echo "🎓 Setting up Scholarship Scraper Environment"
echo "=============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-scraper.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p output
mkdir -p logs
mkdir -p config

# Copy environment file
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment configuration..."
    cp .env.example .env
    echo "Please edit .env file with your configuration before running scrapers"
fi

# Make scripts executable
echo "🔧 Setting up executable permissions..."
chmod +x scheduler.py

# Create cron job template
echo "📅 Creating cron job template..."
cat > setup_cron.sh << 'EOF'
#!/bin/bash
# Add this to your crontab to run scrapers daily at 2 AM
# Run: crontab -e
# Add line: 0 2 * * * /path/to/your/scraper/setup_cron.sh

cd /path/to/your/scholscraper/scraper
source venv/bin/activate
python scheduler.py run >> logs/cron.log 2>&1
EOF

chmod +x setup_cron.sh

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your configuration"
echo "2. Set up Firebase and Google Sheets credentials"
echo "3. Test a spider: python -m scrapy crawl collegescholarships"
echo "4. Run all spiders: python scheduler.py run"
echo "5. Setup cron job: edit setup_cron.sh and add to crontab"
echo ""
echo "For help:"
echo "- Test connection: python -m scrapy check"
echo "- List spiders: python -m scrapy list"
echo "- Run scheduler: python scheduler.py schedule"
echo ""
echo "Remember to activate the virtual environment:"
echo "source venv/bin/activate"
