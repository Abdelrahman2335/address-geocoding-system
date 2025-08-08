"""
Utility functions for the geocoding application
Helper functions that don't belong to specific services
"""
import time
from datetime import datetime
from typing import List, Any
import sys


class Logger:
    """Simple logger utility for application messaging"""
    
    @staticmethod
    def info(message: str) -> None:
        """Log info message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[INFO] {timestamp} - {message}")
    
    @staticmethod
    def error(message: str) -> None:
        """Log error message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[ERROR] {timestamp} - {message}")
    
    @staticmethod
    def warning(message: str) -> None:
        """Log warning message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[WARNING] {timestamp} - {message}")


class Timer:
    """Timer utility for measuring execution time"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self) -> None:
        """Start the timer"""
        self.start_time = time.time()
    
    def stop(self) -> float:
        """Stop the timer and return elapsed time in seconds"""
        if self.start_time is None:
            return 0.0
        self.end_time = time.time()
        return self.end_time - self.start_time
    
    def elapsed(self) -> float:
        """Get elapsed time without stopping the timer"""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time


class Formatter:
    """Formatting utilities for data presentation"""
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
        else:
            days = seconds / 86400
            return f"{days:.1f} days"
    
    @staticmethod
    def format_number(number: int) -> str:
        """Format number with thousand separators"""
        return f"{number:,}"
    
    @staticmethod
    def format_percentage(value: float, total: float) -> str:
        """Format percentage"""
        if total == 0:
            return "0.0%"
        percentage = (value / total) * 100
        return f"{percentage:.1f}%"
    
    @staticmethod
    def format_file_size(bytes_size: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"


class Validator:
    """Validation utilities for data integrity"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Basic email validation"""
        return "@" in email and "." in email
    
    @staticmethod
    def is_valid_address(address: str) -> bool:
        """Basic address validation"""
        if not address or not isinstance(address, str):
            return False
        return len(address.strip()) > 3
    
    @staticmethod
    def is_valid_coordinates(lat: float, lng: float) -> bool:
        """Validate latitude and longitude"""
        return -90 <= lat <= 90 and -180 <= lng <= 180


class Console:
    """Console utilities for better output formatting"""
    
    @staticmethod
    def clear_screen() -> None:
        """Clear console screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def print_header(title: str, width: int = 80) -> None:
        """Print formatted header"""
        print("=" * width)
        print(f"{title:^{width}}")
        print("=" * width)
    
    @staticmethod
    def print_section(title: str, width: int = 60) -> None:
        """Print formatted section header"""
        print(f"\n{'-' * width}")
        print(f"{title}")
        print(f"{'-' * width}")
    
    @staticmethod
    def print_progress_bar(current: int, total: int, width: int = 50) -> None:
        """Print a simple progress bar"""
        if total == 0:
            return
        
        progress = current / total
        filled = int(width * progress)
        bar = '█' * filled + '░' * (width - filled)
        percentage = progress * 100
        
        print(f"\rProgress: |{bar}| {percentage:.1f}% ({current}/{total})", end='', flush=True)
        
        if current == total:
            print()  # New line when complete
