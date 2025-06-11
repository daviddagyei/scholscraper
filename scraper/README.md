# Scholarship Scraper

A comprehensive web scraping system for collecting scholarship data from multiple sources using Scrapy.

## Features

- **Multi-source scraping**: CollegeScholarships.org, UNCF, HSF, APIA Scholars, Native American funds
- **Data validation and cleaning**: Comprehensive pipelines for data quality
- **Multiple export formats**: JSON, CSV, Firebase, Google Sheets
- **Respectful scraping**: Rate limiting, user agent rotation, robots.txt compliance
- **Automated scheduling**: Daily scraping with cleanup
- **Deduplication**: Prevents duplicate scholarship entries
- **Error handling**: Robust error recovery and logging

## Project Structure

```
scraper/
├── items.py                 # Scrapy item definitions
├── settings.py             # Scrapy configuration
├── scrapy.cfg              # Scrapy project config
├── scheduler.py            # Automated scheduling system
├── setup.sh               # Environment setup script
├── requirements-scraper.txt # Python dependencies
├── pipelines/
│   └── pipelines.py       # Data processing pipelines
├── middlewares/
│   └── middlewares.py     # Custom middlewares
├── spiders/
│   ├── base.py           # Base spider class
│   ├── collegescholarships.py
│   ├── uncf.py
│   ├── hsf.py
│   ├── apia.py
│   └── native_american.py
└── output/               # Scraped data output
```

## Setup

1. **Run the setup script**:
   ```bash
   cd scraper
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your configurations
   ```

3. **Set up credentials** (optional):
   - Firebase service account key
   - Google Sheets service account key

## Usage

### Running Individual Spiders

```bash
# Activate virtual environment
source venv/bin/activate

# List available spiders
scrapy list

# Run a specific spider
scrapy crawl collegescholarships

# Run with custom output
scrapy crawl uncf -o output/uncf_scholarships.json
```

### Running All Spiders

```bash
# Run all spiders once
python scheduler.py run

# Run specific spider
python scheduler.py spider --spider collegescholarships
```

### Automated Scheduling

```bash
# Start scheduler daemon (runs daily at 2 AM)
python scheduler.py schedule

# Or set up cron job
# Edit setup_cron.sh with correct paths
# Add to crontab: 0 2 * * * /path/to/setup_cron.sh
```

## Spiders

### 1. CollegeScholarships Spider (`collegescholarships`)
- **Source**: CollegeScholarships.org
- **Focus**: General scholarships database
- **Features**: Category detection, pagination support

### 2. UNCF Spider (`uncf`)
- **Source**: UNCF.org
- **Focus**: African American students
- **Features**: Program-specific parsing, AJAX handling

### 3. HSF Spider (`hsf`)
- **Source**: HSF.net
- **Focus**: Hispanic/Latino students
- **Features**: Card view and detail page parsing

### 4. APIA Scholars Spider (`apia`)
- **Source**: APIAScholars.org
- **Focus**: Asian Pacific Islander American students
- **Features**: Multi-level category extraction

### 5. Native American Spider (`native_american`)
- **Source**: Multiple sites (AISES, NAJA, College Fund, AIANTA)
- **Focus**: Native American/Indigenous students
- **Features**: Multi-domain support, tribal-specific requirements

## Data Pipeline

1. **Validation Pipeline**: Checks required fields and data formats
2. **Deduplication Pipeline**: Removes duplicate entries
3. **Data Cleaning Pipeline**: Normalizes and enriches data
4. **Firebase Pipeline**: Exports to Firestore (optional)
5. **Google Sheets Pipeline**: Exports to Google Sheets (optional)

## Output Format

```json
{
  "title": "Scholarship Name",
  "description": "Detailed description...",
  "amount": "$5,000",
  "deadline": "2024-03-15",
  "eligibility": "Requirements | separated | by | pipes",
  "requirements": "Application | requirements | here",
  "application_url": "https://...",
  "provider": "Organization Name",
  "category": "STEM",
  "tags": ["keyword1", "keyword2"],
  "source": "spider_name",
  "source_url": "https://...",
  "scraped_date": "2024-01-01T00:00:00",
  "is_active": true,
  "item_id": "unique_hash"
}
```

## Configuration

### Environment Variables

- `FIREBASE_PROJECT_ID`: Firebase project ID
- `FIREBASE_CREDENTIALS_PATH`: Path to Firebase service account key
- `GOOGLE_SHEETS_CREDENTIALS_PATH`: Path to Google Sheets credentials
- `GOOGLE_SHEETS_SPREADSHEET_ID`: Google Sheets document ID
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

### Spider Settings

- `DOWNLOAD_DELAY`: Delay between requests (seconds)
- `CONCURRENT_REQUESTS_PER_DOMAIN`: Max concurrent requests per domain
- `RANDOMIZE_DOWNLOAD_DELAY`: Random delay factor
- `ROBOTSTXT_OBEY`: Respect robots.txt (recommended: True)

## Monitoring

### Logs
- `scraper.log`: Main scraping logs
- `scheduler.log`: Scheduler activity logs
- `output/spider_name_timestamp.log`: Individual spider logs

### Statistics
- Items scraped per spider
- Success/failure rates
- Response codes and errors
- Processing time per spider

## Troubleshooting

### Common Issues

1. **Spider not found**:
   ```bash
   # Make sure you're in the scraper directory
   cd scraper
   scrapy list
   ```

2. **Import errors**:
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   pip install -r requirements-scraper.txt
   ```

3. **Permission denied**:
   ```bash
   chmod +x setup.sh scheduler.py
   ```

4. **Firebase/Sheets errors**:
   - Check credentials file paths in .env
   - Verify service account permissions
   - Test credentials separately

### Debug Mode

```bash
# Run with debug logging
scrapy crawl collegescholarships -L DEBUG

# Test specific URL
scrapy shell "https://www.collegescholarships.org/scholarships/"
```

## Development

### Adding New Spiders

1. Create new spider file in `spiders/` directory
2. Extend `BaseSearchSpider` class
3. Implement required methods
4. Add spider name to scheduler
5. Test thoroughly

### Custom Pipelines

1. Add pipeline class to `pipelines/pipelines.py`
2. Register in `settings.py` `ITEM_PIPELINES`
3. Set appropriate priority (lower numbers run first)

## Legal Considerations

- Always respect `robots.txt`
- Use reasonable delays between requests
- Monitor website terms of service
- Consider reaching out to data providers for API access
- Ensure data usage complies with applicable laws

## Contributing

1. Fork the repository
2. Create feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit pull request

## License

This project is for educational and non-commercial use. Always respect website terms of service and robots.txt files.
