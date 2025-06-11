#!/usr/bin/env python3
"""
Scholarship scraper scheduler and runner.

This script handles running the scrapers on a schedule,
managing output, and handling errors.
"""

import os
import sys
import subprocess
import logging
import schedule
import time
from datetime import datetime
from pathlib import Path
import json
import argparse


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ScholarshipScheduler:
    """Manages running scholarship scrapers on schedule."""
    
    def __init__(self, scraper_dir=None):
        self.scraper_dir = scraper_dir or Path(__file__).parent
        self.output_dir = self.scraper_dir / 'output'
        self.output_dir.mkdir(exist_ok=True)
        
        # List of all spiders
        self.spiders = [
            'collegescholarships',
            'uncf',
            'hsf',
            'apia',
            'native_american'
        ]
        
    def run_spider(self, spider_name: str) -> bool:
        """
        Run a single spider.
        
        Args:
            spider_name: Name of the spider to run
            
        Returns:
            True if successful, False otherwise
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = self.output_dir / f'{spider_name}_{timestamp}.json'
        log_file = self.output_dir / f'{spider_name}_{timestamp}.log'
        
        cmd = [
            'scrapy', 'crawl', spider_name,
            '-o', str(output_file),
            '-L', 'INFO',
            '--logfile', str(log_file)
        ]
        
        logger.info(f"Starting spider: {spider_name}")
        
        try:
            # Change to scraper directory
            original_cwd = os.getcwd()
            os.chdir(self.scraper_dir)
            
            # Run spider
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Spider {spider_name} completed successfully")
                
                # Log statistics
                if output_file.exists():
                    with open(output_file, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            logger.info(f"Spider {spider_name} scraped {len(data)} items")
                
                return True
            else:
                logger.error(f"Spider {spider_name} failed with return code {result.returncode}")
                logger.error(f"Error output: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Spider {spider_name} timed out after 1 hour")
            return False
        except Exception as e:
            logger.error(f"Error running spider {spider_name}: {e}")
            return False
        finally:
            os.chdir(original_cwd)
    
    def run_all_spiders(self):
        """Run all spiders sequentially."""
        logger.info("Starting full scraping cycle")
        
        results = {}
        for spider in self.spiders:
            success = self.run_spider(spider)
            results[spider] = success
            
            # Wait between spiders to be respectful
            if spider != self.spiders[-1]:  # Don't wait after last spider
                logger.info("Waiting 2 minutes before next spider...")
                time.sleep(120)
        
        # Log summary
        successful = sum(results.values())
        total = len(results)
        logger.info(f"Scraping cycle completed: {successful}/{total} spiders successful")
        
        if successful < total:
            failed_spiders = [spider for spider, success in results.items() if not success]
            logger.warning(f"Failed spiders: {', '.join(failed_spiders)}")
    
    def cleanup_old_files(self, days_to_keep=7):
        """Clean up old output files."""
        logger.info(f"Cleaning up files older than {days_to_keep} days")
        
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        
        for file_path in self.output_dir.glob('*'):
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                file_path.unlink()
                logger.info(f"Deleted old file: {file_path.name}")
    
    def setup_schedule(self):
        """Setup the scraping schedule."""
        # Run all spiders daily at 2 AM
        schedule.every().day.at("02:00").do(self.run_all_spiders)
        
        # Clean up old files weekly
        schedule.every().sunday.at("01:00").do(self.cleanup_old_files)
        
        logger.info("Schedule configured:")
        logger.info("- Daily scraping at 2:00 AM")
        logger.info("- Weekly cleanup on Sunday at 1:00 AM")
    
    def run_scheduler(self):
        """Run the scheduler loop."""
        self.setup_schedule()
        
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Scholarship Scraper Scheduler')
    parser.add_argument('command', choices=['run', 'schedule', 'spider'], 
                       help='Command to execute')
    parser.add_argument('--spider', help='Specific spider to run (for spider command)')
    parser.add_argument('--scraper-dir', help='Path to scraper directory')
    
    args = parser.parse_args()
    
    scheduler = ScholarshipScheduler(args.scraper_dir)
    
    if args.command == 'run':
        # Run all spiders once
        scheduler.run_all_spiders()
    elif args.command == 'schedule':
        # Run scheduler daemon
        scheduler.run_scheduler()
    elif args.command == 'spider':
        # Run specific spider
        if not args.spider:
            logger.error("--spider argument required for 'spider' command")
            sys.exit(1)
        scheduler.run_spider(args.spider)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
