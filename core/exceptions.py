"""
🚨 CRASH EARLY, CRASH LOUD (Engineering Standards v6.5)
Centralized exception registry for data and format integrity.
"""

class CricketProjectError(Exception):
    """Base exception for all cricket project errors."""
    pass

class DataIntegrityError(CricketProjectError):
    """Raised when the database schema or content is corrupted/drifting."""
    pass

class FormatMismatchError(CricketProjectError):
    """Raised when the data format doesn't match the expected engine configuration."""
    pass

class DataNotFoundError(CricketProjectError):
    """Raised when a required data file or DB table is missing."""
    pass


class ConfigurationError(CricketProjectError):
    """Raised when required runtime configuration is missing or invalid."""
    pass
