"""
Tests for the scholarship scraper scheduler module.

This module contains tests for the ScholarshipScheduler class and its methods.
"""

import pytest
import os
import json
import time
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime

from scraper.scheduler import ScholarshipScheduler


# ----------------------- ScholarshipScheduler initialization tests -----------------------

def test_scholarship_scheduler_init():
    """Test ScholarshipScheduler initialization with default arguments."""
    scheduler = ScholarshipScheduler()
    
    assert scheduler.scraper_dir == Path(__file__).parent.parent.parent
    assert scheduler.output_dir == scheduler.scraper_dir / 'output'
    assert len(scheduler.spiders) == 5  # Should have 5 spiders
    assert 'collegescholarships' in scheduler.spiders
    assert 'uncf' in scheduler.spiders
    assert 'hsf' in scheduler.spiders
    assert 'apia' in scheduler.spiders
    assert 'native_american' in scheduler.spiders


def test_scholarship_scheduler_init_with_custom_dir():
    """Test ScholarshipScheduler initialization with custom directory."""
    custom_dir = Path('/tmp/test_custom_dir')
    
    # Create the directory for the test
    custom_dir.mkdir(exist_ok=True)
    
    try:
        scheduler = ScholarshipScheduler(custom_dir)
        
        assert scheduler.scraper_dir == custom_dir
        assert scheduler.output_dir == custom_dir / 'output'
        assert scheduler.output_dir.exists()
    finally:
        # Clean up after the test
        if (custom_dir / 'output').exists():
            (custom_dir / 'output').rmdir()
        if custom_dir.exists():
            custom_dir.rmdir()


@patch('pathlib.Path.mkdir')
def test_scheduler_creates_output_dir(mock_mkdir):
    """Test that output directory is created if it doesn't exist."""
    ScholarshipScheduler()
    
    mock_mkdir.assert_called_once_with(exist_ok=True)


# ----------------------- ScholarshipScheduler.run_spider tests -----------------------

@patch('subprocess.run')
@patch('os.chdir')
@patch('os.getcwd', return_value='/original/cwd')
def test_run_spider_success(mock_getcwd, mock_chdir, mock_run):
    """Test run_spider method with successful execution."""
    scheduler = ScholarshipScheduler()
    
    # Mock successful subprocess run
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_run.return_value = mock_result
    
    # Mock output file existence and content
    with patch('pathlib.Path.exists', return_value=True):
        with patch('builtins.open', mock_open(read_data='[{"title": "Test Scholarship"}]')):
            with patch('json.load', return_value=[{"title": "Test Scholarship"}]):
                result = scheduler.run_spider('collegescholarships')
    
    assert result is True  # Should return True for success
    
    # Check that commands were called correctly
    mock_getcwd.assert_called_once()
    mock_chdir.assert_any_call(scheduler.scraper_dir)
    mock_chdir.assert_any_call('/original/cwd')  # Should restore original directory
    
    # Verify subprocess command
    mock_run.assert_called_once()
    cmd_args = mock_run.call_args[0][0]
    assert cmd_args[0] == 'scrapy'
    assert cmd_args[1] == 'crawl'
    assert cmd_args[2] == 'collegescholarships'
    assert '-o' in cmd_args
    assert any('collegescholarships_' in arg for arg in cmd_args)
    assert '--logfile' in cmd_args


@patch('subprocess.run')
@patch('os.chdir')
def test_run_spider_failure(mock_chdir, mock_run):
    """Test run_spider method with failed execution."""
    scheduler = ScholarshipScheduler()
    
    # Mock failed subprocess run
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_result.stderr = 'Error message'
    mock_run.return_value = mock_result
    
    result = scheduler.run_spider('collegescholarships')
    
    assert result is False  # Should return False for failure
    mock_run.assert_called_once()


@patch('subprocess.run')
@patch('os.chdir')
def test_run_spider_timeout(mock_chdir, mock_run):
    """Test run_spider method with timeout."""
    scheduler = ScholarshipScheduler()
    
    # Mock timeout exception
    mock_run.side_effect = subprocess.TimeoutExpired(cmd='scrapy crawl', timeout=3600)
    
    result = scheduler.run_spider('collegescholarships')
    
    assert result is False  # Should return False for timeout


@patch('subprocess.run')
@patch('os.chdir')
def test_run_spider_exception(mock_chdir, mock_run):
    """Test run_spider method with general exception."""
    scheduler = ScholarshipScheduler()
    
    # Mock general exception
    mock_run.side_effect = Exception('Something went wrong')
    
    result = scheduler.run_spider('collegescholarships')
    
    assert result is False  # Should return False for any exception


# ----------------------- ScholarshipScheduler.run_all_spiders tests -----------------------

@patch('time.sleep')  # Don't actually sleep during tests
def test_run_all_spiders_all_successful(mock_sleep):
    """Test run_all_spiders when all spiders succeed."""
    scheduler = ScholarshipScheduler()
    
    # Mock run_spider to always return True
    with patch.object(scheduler, 'run_spider', return_value=True) as mock_run_spider:
        scheduler.run_all_spiders()
        
        # Should call run_spider for each spider
        assert mock_run_spider.call_count == 5
        
        # Should sleep between spiders (except after the last one)
        assert mock_sleep.call_count == 4


@patch('time.sleep')  # Don't actually sleep during tests
def test_run_all_spiders_mixed_results(mock_sleep):
    """Test run_all_spiders with mixed success and failure."""
    scheduler = ScholarshipScheduler()
    
    # Mock run_spider to alternate between True and False
    side_effects = [True, False, True, False, True]
    
    with patch.object(scheduler, 'run_spider', side_effect=side_effects) as mock_run_spider:
        scheduler.run_all_spiders()
        
        # Should still call run_spider for each spider
        assert mock_run_spider.call_count == 5


@patch('time.sleep')  # Don't actually sleep during tests
def test_run_all_spiders_all_fail(mock_sleep):
    """Test run_all_spiders when all spiders fail."""
    scheduler = ScholarshipScheduler()
    
    # Mock run_spider to always return False
    with patch.object(scheduler, 'run_spider', return_value=False) as mock_run_spider:
        scheduler.run_all_spiders()
        
        # Should call run_spider for each spider
        assert mock_run_spider.call_count == 5


# ----------------------- ScholarshipScheduler.cleanup_old_files tests -----------------------

def test_cleanup_old_files_removes_old_files():
    """Test cleanup_old_files removes files older than the threshold."""
    scheduler = ScholarshipScheduler()
    
    # Create mock file paths with different timestamps
    mock_files = [
        MagicMock(name='old_file1.json'),
        MagicMock(name='old_file2.log'),
        MagicMock(name='new_file1.json'),
        MagicMock(name='new_file2.log'),
    ]
    
    # Set up old and new file stats
    current_time = time.time()
    ten_days_ago = current_time - (10 * 24 * 60 * 60)
    
    mock_files[0].is_file.return_value = True
    mock_files[0].stat.return_value.st_mtime = ten_days_ago
    
    mock_files[1].is_file.return_value = True
    mock_files[1].stat.return_value.st_mtime = ten_days_ago
    
    mock_files[2].is_file.return_value = True
    mock_files[2].stat.return_value.st_mtime = current_time
    
    mock_files[3].is_file.return_value = True
    mock_files[3].stat.return_value.st_mtime = current_time
    
    # Set up the glob to return our mock files
    with patch('pathlib.Path.glob', return_value=mock_files):
        scheduler.cleanup_old_files(days_to_keep=7)
    
    # The two old files should be deleted
    mock_files[0].unlink.assert_called_once()
    mock_files[1].unlink.assert_called_once()
    
    # The two new files should not be deleted
    mock_files[2].unlink.assert_not_called()
    mock_files[3].unlink.assert_not_called()


def test_cleanup_old_files_ignores_directories():
    """Test cleanup_old_files ignores directories."""
    scheduler = ScholarshipScheduler()
    
    # Create a mock directory path
    mock_dir = MagicMock(name='some_dir')
    mock_dir.is_file.return_value = False
    
    # Set up the glob to return our mock directory
    with patch('pathlib.Path.glob', return_value=[mock_dir]):
        scheduler.cleanup_old_files()
    
    # The directory should not be deleted
    mock_dir.unlink.assert_not_called()


# ----------------------- ScholarshipScheduler.setup_schedule tests -----------------------

def test_setup_schedule():
    """Test setup_schedule configures jobs correctly."""
    scheduler = ScholarshipScheduler()
    
    with patch('schedule.every') as mock_schedule:
        # Mock the chained methods
        mock_day = MagicMock()
        mock_sunday = MagicMock()
        mock_schedule.return_value.day = mock_day
        mock_schedule.return_value.sunday = mock_sunday
        
        scheduler.setup_schedule()
        
        # Check that schedules are set up correctly
        mock_day.at.assert_called_once_with("02:00")
        mock_day.at.return_value.do.assert_called_once_with(scheduler.run_all_spiders)
        
        mock_sunday.at.assert_called_once_with("01:00")
        mock_sunday.at.return_value.do.assert_called_once_with(scheduler.cleanup_old_files)


# ----------------------- ScholarshipScheduler.run_scheduler tests -----------------------

@patch('schedule.run_pending')
@patch('time.sleep')
def test_run_scheduler_loop(mock_sleep, mock_run_pending):
    """Test run_scheduler main loop."""
    scheduler = ScholarshipScheduler()
    
    # Make sleep raise KeyboardInterrupt after one iteration
    mock_sleep.side_effect = [None, KeyboardInterrupt()]
    
    with patch.object(scheduler, 'setup_schedule') as mock_setup:
        scheduler.run_scheduler()
        
        # setup_schedule should be called once
        mock_setup.assert_called_once()
        
        # run_pending should be called at least once
        mock_run_pending.assert_called()
        
        # Should check every minute
        mock_sleep.assert_any_call(60)


# ----------------------- Main function tests -----------------------

def test_main_run_command():
    """Test main function with 'run' command."""
    mock_args = MagicMock()
    mock_args.command = 'run'
    mock_args.scraper_dir = None
    
    with patch('argparse.ArgumentParser') as mock_parser:
        mock_parser.return_value.parse_args.return_value = mock_args
        
        with patch('scraper.scheduler.ScholarshipScheduler') as mock_scheduler_class:
            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler
            
            from scraper.scheduler import main
            main()
            
            mock_scheduler.run_all_spiders.assert_called_once()
            mock_scheduler.run_scheduler.assert_not_called()
            mock_scheduler.run_spider.assert_not_called()


def test_main_schedule_command():
    """Test main function with 'schedule' command."""
    mock_args = MagicMock()
    mock_args.command = 'schedule'
    mock_args.scraper_dir = None
    
    with patch('argparse.ArgumentParser') as mock_parser:
        mock_parser.return_value.parse_args.return_value = mock_args
        
        with patch('scraper.scheduler.ScholarshipScheduler') as mock_scheduler_class:
            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler
            
            from scraper.scheduler import main
            main()
            
            mock_scheduler.run_scheduler.assert_called_once()
            mock_scheduler.run_all_spiders.assert_not_called()
            mock_scheduler.run_spider.assert_not_called()


def test_main_spider_command():
    """Test main function with 'spider' command."""
    mock_args = MagicMock()
    mock_args.command = 'spider'
    mock_args.spider = 'collegescholarships'
    mock_args.scraper_dir = None
    
    with patch('argparse.ArgumentParser') as mock_parser:
        mock_parser.return_value.parse_args.return_value = mock_args
        
        with patch('scraper.scheduler.ScholarshipScheduler') as mock_scheduler_class:
            mock_scheduler = MagicMock()
            mock_scheduler_class.return_value = mock_scheduler
            
            from scraper.scheduler import main
            main()
            
            mock_scheduler.run_spider.assert_called_once_with('collegescholarships')
            mock_scheduler.run_all_spiders.assert_not_called()
            mock_scheduler.run_scheduler.assert_not_called()


def test_main_spider_command_missing_spider():
    """Test main function with 'spider' command but missing spider name."""
    mock_args = MagicMock()
    mock_args.command = 'spider'
    mock_args.spider = None
    mock_args.scraper_dir = None
    
    with patch('argparse.ArgumentParser') as mock_parser:
        mock_parser.return_value.parse_args.return_value = mock_args
        
        with patch('scraper.scheduler.ScholarshipScheduler') as mock_scheduler_class:
            with patch('sys.exit') as mock_exit:
                with patch('logging.getLogger') as mock_get_logger:
                    from scraper.scheduler import main
                    main()
                    
                    mock_scheduler_class.return_value.run_spider.assert_called_with(None)
                    mock_get_logger.return_value.error.assert_called_with(
                        "--spider argument required for 'spider' command"
                    )
