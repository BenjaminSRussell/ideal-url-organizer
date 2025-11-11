"""
Production logging system with date-based organization and error tracking
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
    """Centralized logging system with date-based organization"""

    def __init__(self, base_log_dir: str = None, verbose: bool = False):
        if base_log_dir is None:
            project_root = Path(__file__).parent.parent.parent
            base_log_dir = project_root / "logs"

        self.base_log_dir = Path(base_log_dir)
        self.base_log_dir.mkdir(parents=True, exist_ok=True)

        self.today = datetime.now().strftime('%Y-%m-%d')
        self.log_dir = self.base_log_dir / self.today
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.verbose = verbose
        self.loggers = {}
        self._init_loggers()

    def _init_loggers(self):
        """Initialize loggers for different components"""
        components = ['crawler', 'parser', 'organizer', 'analyzer', 'extractor', 'visualizer', 'general', 'failures']

        for component in components:
            logger = logging.getLogger(f'url_organizer.{component}')
            logger.setLevel(logging.DEBUG)

            log_file = self.log_dir / f'{component}.log'
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

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
        """Log failure with full context"""
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

        logger.error(json.dumps(failure_entry, indent=2))
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
    """Decorator to automatically log errors"""
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
    """Execute function with error logging and fallback"""
    op = operation or func.__name__
    logger = get_logger()

    try:
        result = func(*args, **kwargs)
        logger.log_success(component, op)
        return result
    except Exception as e:
        context = {'function': func.__name__, 'args': str(args)[:200], 'kwargs': str(kwargs)[:200]}
        logger.log_failure(component, op, e, context)
        return default


class FailureAnalyzer:
    """Analyze failure logs to identify patterns"""

    def __init__(self, log_dir: Path = None):
        if log_dir is None:
            project_root = Path(__file__).parent.parent.parent
            log_dir = project_root / "logs"
        self.log_dir = Path(log_dir)

    def analyze_failures(self, days: int = 7) -> dict:
        """Analyze failures from past N days"""
        failures = []

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

        analysis = {
            'total_failures': len(failures),
            'by_component': {},
            'by_error_type': {},
            'by_operation': {},
            'most_common': []
        }

        for failure in failures:
            comp = failure.get('component', 'unknown')
            analysis['by_component'][comp] = analysis['by_component'].get(comp, 0) + 1

            error_type = failure.get('error_type', 'unknown')
            analysis['by_error_type'][error_type] = analysis['by_error_type'].get(error_type, 0) + 1

            op = failure.get('operation', 'unknown')
            analysis['by_operation'][op] = analysis['by_operation'].get(op, 0) + 1

        if analysis['by_error_type']:
            analysis['most_common'] = sorted(analysis['by_error_type'].items(), key=lambda x: x[1], reverse=True)[:5]

        return analysis

    def generate_report(self, output_file: str = None) -> str:
        """Generate failure analysis report"""
        analysis = self.analyze_failures()

        report = [
            "Failure Analysis Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Failures: {analysis['total_failures']}",
            "\nFailures by Component:"
        ]

        for comp, count in sorted(analysis['by_component'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {comp}: {count}")

        report.append("\nFailures by Error Type:")
        for error_type, count in sorted(analysis['by_error_type'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {error_type}: {count}")

        report.append("\nMost Common Failures:")
        for error_type, count in analysis['most_common']:
            report.append(f"  {error_type}: {count} occurrences")

        report_text = '\n'.join(report)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)

        return report_text


if __name__ == '__main__':
    logger = get_logger(verbose=True)
    logger.log_success('crawler', 'fetch_page', {'url': 'http://example.com', 'status': 200})
    logger.log_warning('parser', 'Invalid HTML structure', {'url': 'http://example.com'})

    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.log_failure('extractor', 'extract_data', e, {'url': 'http://example.com'})

    @log_errors('organizer', 'organize_urls')
    def test_function():
        return "success"

    test_function()

    analyzer = FailureAnalyzer()
    report = analyzer.generate_report()
    print(f"\n{report}")
