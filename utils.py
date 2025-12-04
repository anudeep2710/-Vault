"""
Utility functions for the Privacy-First Personal Agent.
"""
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import re

from config import LOG_CONFIG, LOGS_DIR


def setup_logging(name: str = "privacy_agent") -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_CONFIG['level'])
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # File handler
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_CONFIG['file'],
        maxBytes=LOG_CONFIG['max_bytes'],
        backupCount=LOG_CONFIG['backup_count']
    )
    file_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(LOG_CONFIG['format'])
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger


def format_currency(amount: float) -> str:
    """Format amount as currency."""
    return f"₹{amount:,.2f}"


def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats."""
    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%b-%Y",
        "%d %B %Y",
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Could not parse date: {date_str}")


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()


def extract_amount(text: str) -> float:
    """Extract amount from text (supports ₹, Rs., INR)."""
    patterns = [
        r'₹\s*([\d,]+\.?\d*)',
        r'Rs\.?\s*([\d,]+\.?\d*)',
        r'INR\s*([\d,]+\.?\d*)',
        r'([\d,]+\.?\d*)\s*(?:₹|Rs|INR)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(',', '')
            try:
                return float(amount_str)
            except ValueError:
                continue
    
    return 0.0


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_date_range_str(start: datetime, end: datetime) -> str:
    """Get human-readable date range string."""
    if start.date() == end.date():
        return start.strftime("%B %d, %Y")
    elif start.year == end.year:
        if start.month == end.month:
            return f"{start.strftime('%B %d')} - {end.strftime('%d, %Y')}"
        else:
            return f"{start.strftime('%B %d')} - {end.strftime('%B %d, %Y')}"
    else:
        return f"{start.strftime('%B %d, %Y')} - {end.strftime('%B %d, %Y')}"


def validate_file_size(file_path: Path, max_size_mb: int = 50) -> bool:
    """Check if file size is within limits."""
    if not file_path.exists():
        return False
    
    size_mb = file_path.stat().st_size / (1024 * 1024)
    return size_mb <= max_size_mb


def safe_filename(filename: str) -> str:
    """Create a safe filename by removing invalid characters."""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    name = name[:200]
    return f"{name}.{ext}" if ext else name


def color_text(text: str, color: str) -> str:
    """Color text for terminal output (Windows compatible)."""
    from colorama import Fore, Style
    
    colors = {
        'red': Fore.RED,
        'green': Fore.GREEN,
        'yellow': Fore.YELLOW,
        'blue': Fore.BLUE,
        'cyan': Fore.CYAN,
        'magenta': Fore.MAGENTA,
    }
    
    color_code = colors.get(color.lower(), '')
    return f"{color_code}{text}{Style.RESET_ALL}"


def create_table(headers: List[str], rows: List[List[Any]]) -> str:
    """Create a formatted table from data."""
    from tabulate import tabulate
    return tabulate(rows, headers=headers, tablefmt="simple")


if __name__ == "__main__":
    # Test utilities
    print("Testing Utilities...")
    
    # Test currency formatting
    print(f"Currency: {format_currency(1234.56)}")
    
    # Test amount extraction
    test_texts = [
        "Debited Rs.500.50 from your account",
        "Credited ₹1,234.00 to account",
        "Amount: INR 99.99",
    ]
    for text in test_texts:
        amount = extract_amount(text)
        print(f"Extracted from '{text}': {format_currency(amount)}")
    
    # Test text cleaning
    dirty_text = "This   has   extra    spaces!!!"
    print(f"Cleaned: '{clean_text(dirty_text)}'")
    
    # Test date range
    start = datetime(2024, 1, 15)
    end = datetime(2024, 1, 20)
    print(f"Date range: {get_date_range_str(start, end)}")
    
    # Test colored text
    print(color_text("Success!", "green"))
    print(color_text("Warning!", "yellow"))
    print(color_text("Error!", "red"))
