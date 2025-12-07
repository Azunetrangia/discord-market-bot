"""
Logging configuration for Discord News Bot
Setup centralized logging with file rotation
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional


def setup_logging(log_dir: str = 'logs', log_level: int = logging.INFO) -> logging.Logger:
    """
    Cấu hình logging cho bot với file rotation
    
    Args:
        log_dir: Directory để lưu log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        logger: Configured logger instance
    """
    # Tạo logs directory nếu chưa tồn tại
    os.makedirs(log_dir, exist_ok=True)
    
    # Tạo logger
    logger = logging.getLogger('discord_news_bot')
    logger.setLevel(log_level)
    
    # Xóa handlers cũ nếu có (để avoid duplicate logs)
    if logger.handlers:
        logger.handlers.clear()
    
    # Format cho log messages
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 1. Console Handler - Simple format cho terminal
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # 2. Main Log File Handler - Detailed format với rotation
    main_log_file = os.path.join(log_dir, 'bot.log')
    file_handler = RotatingFileHandler(
        main_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB per file
        backupCount=5,  # Keep 5 backup files
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # 3. Error Log File Handler - Chỉ log errors
    error_log_file = os.path.join(log_dir, 'errors.log')
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB per file
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    # 4. Debug Log File Handler - Detailed debug logs (optional)
    if log_level == logging.DEBUG:
        debug_log_file = os.path.join(log_dir, 'debug.log')
        debug_handler = RotatingFileHandler(
            debug_log_file,
            maxBytes=20 * 1024 * 1024,  # 20MB per file
            backupCount=2,
            encoding='utf-8'
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(detailed_formatter)
        logger.addHandler(debug_handler)
    
    # Log initial message
    logger.info("="*70)
    logger.info("Logging system initialized successfully")
    logger.info(f"Log directory: {log_dir}")
    logger.info(f"Log level: {logging.getLevelName(log_level)}")
    logger.info("="*70)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name (optional)
    
    Returns:
        logger: Logger instance
    """
    if name:
        return logging.getLogger(f'discord_news_bot.{name}')
    return logging.getLogger('discord_news_bot')


# Convenience functions for common logging patterns
def log_api_call(
    logger: logging.Logger,
    source: str,
    url: str,
    success: bool = True,
    response_time: Optional[float] = None
) -> None:
    """Log API call với structured format"""
    if success:
        msg = f"API Call Success | Source: {source} | URL: {url}"
        if response_time:
            msg += f" | Response Time: {response_time:.2f}s"
        logger.info(msg)
    else:
        logger.error(f"API Call Failed | Source: {source} | URL: {url}")


def log_news_posted(logger: logging.Logger, guild_name: str, source: str, article_title: str) -> None:
    """Log khi post news thành công"""
    logger.info(f"News Posted | Guild: {guild_name} | Source: {source} | Title: {article_title[:50]}...")


def log_translation(
    logger: logging.Logger,
    original_lang: str,
    target_lang: str,
    text_length: int,
    success: bool = True
) -> None:
    """Log translation activity"""
    if success:
        logger.debug(f"Translation Success | {original_lang} -> {target_lang} | Length: {text_length} chars")
    else:
        logger.warning(f"Translation Failed | {original_lang} -> {target_lang} | Length: {text_length} chars")


# Initialize default logger when module is imported
default_logger = setup_logging()
