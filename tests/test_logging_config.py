"""Tests for ptoon.logging_config module.

Tests environment variable handling, logger configuration,
and programmatic logging control.
"""

import logging
import os
from unittest import mock

import pytest

from ptoon.logging_config import (
    DEBUG_LOG_LEVEL,
    DEFAULT_LOG_LEVEL,
    PYTOON_DEBUG_ENV_VAR,
    configure_logging,
    get_logger,
    is_debug_enabled,
)


class TestIsDebugEnabled:
    """Test environment variable detection for debug mode."""

    def test_returns_true_for_value_1(self, monkeypatch):
        """Test PYTOON_DEBUG=1 enables debug mode."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "1")
        # Clear cache
        is_debug_enabled.cache_clear()
        assert is_debug_enabled() is True

    def test_returns_true_for_lowercase_true(self, monkeypatch):
        """Test PYTOON_DEBUG=true enables debug mode."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "true")
        is_debug_enabled.cache_clear()
        assert is_debug_enabled() is True

    def test_returns_true_for_capitalized_true(self, monkeypatch):
        """Test PYTOON_DEBUG=True enables debug mode."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "True")
        is_debug_enabled.cache_clear()
        assert is_debug_enabled() is True

    def test_returns_true_for_uppercase_true(self, monkeypatch):
        """Test PYTOON_DEBUG=TRUE enables debug mode."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "TRUE")
        is_debug_enabled.cache_clear()
        assert is_debug_enabled() is True

    def test_returns_true_for_lowercase_yes(self, monkeypatch):
        """Test PYTOON_DEBUG=yes enables debug mode."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "yes")
        is_debug_enabled.cache_clear()
        assert is_debug_enabled() is True

    def test_returns_true_for_capitalized_yes(self, monkeypatch):
        """Test PYTOON_DEBUG=Yes enables debug mode."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "Yes")
        is_debug_enabled.cache_clear()
        assert is_debug_enabled() is True

    def test_returns_true_for_uppercase_yes(self, monkeypatch):
        """Test PYTOON_DEBUG=YES enables debug mode."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "YES")
        is_debug_enabled.cache_clear()
        assert is_debug_enabled() is True

    def test_returns_false_for_value_0(self, monkeypatch):
        """Test PYTOON_DEBUG=0 disables debug mode."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "0")
        is_debug_enabled.cache_clear()
        assert is_debug_enabled() is False

    def test_returns_false_for_false_string(self, monkeypatch):
        """Test PYTOON_DEBUG=false disables debug mode."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "false")
        is_debug_enabled.cache_clear()
        assert is_debug_enabled() is False

    def test_returns_false_for_empty_string(self, monkeypatch):
        """Test PYTOON_DEBUG='' (empty) disables debug mode."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "")
        is_debug_enabled.cache_clear()
        assert is_debug_enabled() is False

    def test_returns_false_when_not_set(self, monkeypatch):
        """Test debug mode disabled when PYTOON_DEBUG not set."""
        monkeypatch.delenv(PYTOON_DEBUG_ENV_VAR, raising=False)
        is_debug_enabled.cache_clear()
        assert is_debug_enabled() is False

    def test_returns_false_for_invalid_value(self, monkeypatch):
        """Test invalid PYTOON_DEBUG value disables debug mode."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "invalid")
        is_debug_enabled.cache_clear()
        assert is_debug_enabled() is False

    def test_caches_result(self, monkeypatch):
        """Test that is_debug_enabled() caches its result."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "1")
        is_debug_enabled.cache_clear()

        # First call
        result1 = is_debug_enabled()

        # Change env var (cache should ignore this)
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "0")
        result2 = is_debug_enabled()

        # Should still return cached result
        assert result1 is True
        assert result2 is True


class TestGetLogger:
    """Test logger creation and configuration."""

    def test_returns_logger_instance(self):
        """Test get_logger() returns a Logger instance."""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_sets_log_level_based_on_debug_mode_enabled(self, monkeypatch):
        """Test logger level is DEBUG when PYTOON_DEBUG=1."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "1")
        is_debug_enabled.cache_clear()

        logger = get_logger("test_debug_enabled")
        assert logger.level == DEBUG_LOG_LEVEL

    def test_sets_log_level_based_on_debug_mode_disabled(self, monkeypatch):
        """Test logger level is WARNING when PYTOON_DEBUG not set."""
        monkeypatch.delenv(PYTOON_DEBUG_ENV_VAR, raising=False)
        is_debug_enabled.cache_clear()

        logger = get_logger("test_debug_disabled")
        assert logger.level == DEFAULT_LOG_LEVEL

    def test_adds_stream_handler_on_first_call(self):
        """Test StreamHandler is added on first get_logger() call."""
        logger = get_logger("test_new_logger")

        # Should have at least one handler
        assert len(logger.handlers) > 0

        # Should have a StreamHandler
        has_stream_handler = any(
            isinstance(h, logging.StreamHandler) for h in logger.handlers
        )
        assert has_stream_handler

    def test_does_not_duplicate_handlers(self):
        """Test get_logger() doesn't add duplicate handlers."""
        logger1 = get_logger("test_no_duplicate")
        handler_count_1 = len(logger1.handlers)

        # Call again with same name
        logger2 = get_logger("test_no_duplicate")
        handler_count_2 = len(logger2.handlers)

        # Should be same logger instance with same number of handlers
        assert logger1 is logger2
        assert handler_count_1 == handler_count_2

    def test_handler_has_formatter(self):
        """Test handler has proper formatter configured."""
        logger = get_logger("test_formatter")

        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                assert handler.formatter is not None
                # Check format contains expected elements
                format_str = handler.formatter._fmt
                assert "%(name)s" in format_str
                assert "%(levelname)s" in format_str
                assert "%(message)s" in format_str

    def test_handler_level_matches_logger_level(self, monkeypatch):
        """Test handler level matches logger level."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "1")
        is_debug_enabled.cache_clear()

        logger = get_logger("test_handler_level")

        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                assert handler.level == logger.level


class TestConfigureLogging:
    """Test programmatic logging configuration."""

    def test_sets_level_to_debug(self):
        """Test configure_logging(DEBUG) sets debug level."""
        # Create a logger first
        logger = get_logger("ptoon.test_set_debug")

        # Configure to DEBUG
        configure_logging(logging.DEBUG)

        # Verify level changed
        assert logger.level == logging.DEBUG
        for handler in logger.handlers:
            assert handler.level == logging.DEBUG

    def test_sets_level_to_warning(self):
        """Test configure_logging(WARNING) sets warning level."""
        # Create a logger first
        logger = get_logger("ptoon.test_set_warning")

        # Configure to WARNING
        configure_logging(logging.WARNING)

        # Verify level changed
        assert logger.level == logging.WARNING
        for handler in logger.handlers:
            assert handler.level == logging.WARNING

    def test_sets_level_to_info(self):
        """Test configure_logging(INFO) sets info level."""
        # Create a logger first
        logger = get_logger("ptoon.test_set_info")

        # Configure to INFO
        configure_logging(logging.INFO)

        # Verify level changed
        assert logger.level == logging.INFO
        for handler in logger.handlers:
            assert handler.level == logging.INFO

    def test_uses_debug_level_when_none_and_debug_enabled(self, monkeypatch):
        """Test configure_logging(None) uses DEBUG when PYTOON_DEBUG=1."""
        monkeypatch.setenv(PYTOON_DEBUG_ENV_VAR, "1")
        is_debug_enabled.cache_clear()

        logger = get_logger("ptoon.test_none_debug")
        configure_logging(None)

        assert logger.level == DEBUG_LOG_LEVEL

    def test_uses_default_level_when_none_and_debug_disabled(self, monkeypatch):
        """Test configure_logging(None) uses WARNING when PYTOON_DEBUG not set."""
        monkeypatch.delenv(PYTOON_DEBUG_ENV_VAR, raising=False)
        is_debug_enabled.cache_clear()

        logger = get_logger("ptoon.test_none_default")
        configure_logging(None)

        assert logger.level == DEFAULT_LOG_LEVEL

    def test_only_affects_pytoon_loggers(self):
        """Test configure_logging() only modifies ptoon.* loggers."""
        # Create pytoon logger
        pytoon_logger = get_logger("ptoon.submodule")

        # Create non-pytoon logger
        other_logger = logging.getLogger("other_package.module")
        other_logger.setLevel(logging.INFO)
        other_original_level = other_logger.level

        # Configure pytoon logging
        configure_logging(logging.DEBUG)

        # Pytoon logger should change
        assert pytoon_logger.level == logging.DEBUG

        # Other logger should not change
        assert other_logger.level == other_original_level

    def test_updates_all_existing_pytoon_loggers(self):
        """Test configure_logging() updates all ptoon.* loggers."""
        # Create multiple pytoon loggers
        logger1 = get_logger("ptoon.module1")
        logger2 = get_logger("ptoon.module2")
        logger3 = get_logger("ptoon.subpackage.module3")

        # Configure all at once
        configure_logging(logging.ERROR)

        # All should have new level
        assert logger1.level == logging.ERROR
        assert logger2.level == logging.ERROR
        assert logger3.level == logging.ERROR
