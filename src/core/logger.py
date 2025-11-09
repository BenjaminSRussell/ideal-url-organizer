"""
Production Logging System

Minimal interference with code, comprehensive error tracking.
Date-based organization, separate logs for different components.
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from functools import wraps
import traceback
import json


class ProductionLogger:
    """
    Centralized logging system for production use

    Features:
    - Date-based log organization
    - Component-specific logging
    - Minimal CLI interference
    - Comprehensive error tracking
    - Failure analysis
    """

    def __init__(self, base_log_dir: str = None, verbose: bool = False):
        """
        Initialize production logger

        Args:
            base_log_dir: Base directory for logs
            verbose: If True, also log to console
        """
        if base_log_dir is None:
            project_root = Path(__file__).parent.parent.parent
            base_log_dir = project_root / "logs"

        self.base_log_dir = Path(base_log_dir)
        self.base_log_dir.mkdir(parents=True, exist_ok=True)

        # Create date-based subdirectory
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.log_dir = self.base_log_dir / self.today
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.verbose = verbose
        self.loggers = {}

        # Initialize component loggers
        self._init_loggers()

    def _init_loggers(self):
        """Initialize loggers for different components"""
        components = [
            'crawler', 'parser', 'organizer', 'analyzer',
            'extractor', 'visualizer', 'general', 'failures'
        ]

        for component in components:
            logger = logging.getLogger(f'url_organizer.{component}')
            logger.setLevel(logging.DEBUG)

            # File handler
            log_file = self.log_dir / f'{component}.log'
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)

            # Format
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # Console handler (only if verbose)
            if self.verbose:
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setLevel(logging.INFO)
                console_handler.setFormatter(formatter)
                logger.addHandler(console_handler)

            self.loggers[component] = logger

    def get_logger(self, component: str) -> logging.Logger:
        """Get logger for specific component"""
        return self.loggers.get(component, self.loggers['general'])

    def log_failure(self, component: str, operation: str, error: Exception, context: dict = None):
        """
        Log failure with full context

        Args:
            component: Component name
            operation: Operation that failed
            error: Exception that occurred
            context: Additional context
        """
        logger = self.loggers['failures']

        failure_entry = {
            'timestamp': datetime.now().isoformat(),
            'component': component,
            'operation': operation,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or {}
        }

        # Log to failures.log
        logger.error(json.dumps(failure_entry, indent=2))

        # Also log to component-specific log
        comp_logger = self.get_logger(component)
        comp_logger.error(f"FAILURE in {operation}: {error}")

    def log_success(self, component: str, operation: str, details: dict = None):
        """Log successful operation"""
        logger = self.get_logger(component)

        message = f"SUCCESS: {operation}"
        if details:
            message += f" | {json.dumps(details)}"

        logger.info(message)

    def log_warning(self, component: str, message: str, details: dict = None):
        """Log warning"""
        logger = self.get_logger(component)

        log_message = f"WARNING: {message}"
        if details:
            log_message += f" | {json.dumps(details)}"

        logger.warning(log_message)


# Global logger instance
_logger = None


def get_logger(verbose: bool = False) -> ProductionLogger:
    """Get global logger instance"""
    global _logger
    if _logger is None:
        _logger = ProductionLogger(verbose=verbose)
    return _logger


def log_errors(component: str, operation: str = None):
    """
    Decorator to automatically log errors

    Usage:
        @log_errors('crawler', 'fetch_page')
        def fetch_page(url):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op = operation or func.__name__
            logger = get_logger()

            try:
                result = func(*args, **kwargs)
                logger.log_success(component, op)
                return result
            except Exception as e:
                context = {
                    'function': func.__name__,
                    'args': str(args)[:200],
                    'kwargs': str(kwargs)[:200]
                }
                logger.log_failure(component, op, e, context)
                raise

        return wrapper
    return decorator


def safe_execute(func, *args, component: str = 'general', operation: str = None, default=None, **kwargs):
    """
    Execute function with automatic error logging and fallback

    Args:
        func: Function to execute
        component: Component name for logging
        operation: Operation name
        default: Default value to return on error

    Returns:
        Function result or default on error
    """
    op = operation or func.__name__
    logger = get_logger()

    try:
        result = func(*args, **kwargs)
        logger.log_success(component, op)
        return result
    except Exception as e:
        context = {
            'function': func.__name__,
            'args': str(args)[:200],
            'kwargs': str(kwargs)[:200]
        }
        logger.log_failure(component, op, e, context)

        # Return default instead of crashing
        return default


class FailureAnalyzer:
    """Analyze failure logs to identify patterns and weaknesses"""

    def __init__(self, log_dir: Path = None):
        """Initialize failure analyzer"""
        if log_dir is None:
            project_root = Path(__file__).parent.parent.parent
            log_dir = project_root / "logs"

        self.log_dir = Path(log_dir)

    def analyze_failures(self, days: int = 7) -> dict:
        """
        Analyze failures from past N days

        Args:
            days: Number of days to analyze

        Returns:
            Analysis report
        """
        failures = []

        # Collect all failure logs
        for date_dir in self.log_dir.iterdir():
            if not date_dir.is_dir():
                continue

            failure_log = date_dir / 'failures.log'
            if failure_log.exists():
                with open(failure_log) as f:
                    for line in f:
                        try:
                            failures.append(json.loads(line))
                        except:
                            continue

        # Analyze patterns
        analysis = {
            'total_failures': len(failures),
            'by_component': {},
            'by_error_type': {},
            'by_operation': {},
            'most_common': [],
            'critical_failures': []
        }

        for failure in failures:
            # By component
            comp = failure.get('component', 'unknown')
            analysis['by_component'][comp] = analysis['by_component'].get(comp, 0) + 1

            # By error type
            error_type = failure.get('error_type', 'unknown')
            analysis['by_error_type'][error_type] = analysis['by_error_type'].get(error_type, 0) + 1

            # By operation
            op = failure.get('operation', 'unknown')
            analysis['by_operation'][op] = analysis['by_operation'].get(op, 0) + 1

        # Find most common
        if analysis['by_error_type']:
            analysis['most_common'] = sorted(
                analysis['by_error_type'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

        return analysis

    def generate_report(self, output_file: str = None) -> str:
        """Generate failure analysis report"""
        analysis = self.analyze_failures()

        report = [
            "FAILURE ANALYSIS REPORT",
            "=" * 80,
            f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\nTotal Failures: {analysis['total_failures']}",
            "\n\nFAILURES BY COMPONENT:",
            "-" * 40
        ]

        for comp, count in sorted(analysis['by_component'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {comp}: {count}")

        report.extend([
            "\n\nFAILURES BY ERROR TYPE:",
            "-" * 40
        ])

        for error_type, count in sorted(analysis['by_error_type'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {error_type}: {count}")

        report.extend([
            "\n\nMOST COMMON FAILURES:",
            "-" * 40
        ])

        for error_type, count in analysis['most_common']:
            report.append(f"  {error_type}: {count} occurrences")

        report_text = '\n'.join(report)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)

        return report_text


if __name__ == '__main__':
    # Demo logging system
    logger = get_logger(verbose=True)

    # Test different log types
    logger.log_success('crawler', 'fetch_page', {'url': 'http://example.com', 'status': 200})
    logger.log_warning('parser', 'Invalid HTML structure', {'url': 'http://example.com'})

    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.log_failure('extractor', 'extract_data', e, {'url': 'http://example.com'})

    # Test decorator
    @log_errors('organizer', 'organize_urls')
    def test_function():
        return "success"

    test_function()

    # Analyze failures
    analyzer = FailureAnalyzer()
    report = analyzer.generate_report()
    print("\n" + report)
