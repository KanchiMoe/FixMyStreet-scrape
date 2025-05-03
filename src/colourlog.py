import logging

class ColorFormatter(logging.Formatter):
    COLORS = {
        'WARNING': '\033[93m',   # Yellow
        'ERROR':   '\033[91m',   # Red
        'CRITICAL':'\033[91m\033[1m',  # Red + Bold
        'RESET':   '\033[0m'
    }

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        original = super().format(record)
        return f"{log_color}{original}{reset}"

def setup_logger(level=logging.DEBUG):
    handler = logging.StreamHandler()
    formatter = ColorFormatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    if not logger.handlers:
        logger.addHandler(handler)
    logger.setLevel(level)

# Now you use it
setup_logger()

# Test logs
logging.debug('Debug message')       # No color
logging.info('Info message')          # No color
logging.warning('Warning message')    # Yellow
logging.error('Error message')        # Red
logging.critical('Critical message')  # Red + Bold
