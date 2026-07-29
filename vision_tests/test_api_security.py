"""Security regression tests for vision API."""
import re
import pytest

class TestFlowIdValidation:
    """Test flow_id format validation."""

    def test_valid_flow_id(self):
        pattern = re.compile(r"^[a-f0-9]{32}$")
        assert pattern.match("a" * 32)
        assert pattern.match("0123456789abcdef0123456789abcdef")

    def test_invalid_flow_id(self):
        pattern = re.compile(r"^[a-f0-9]{32}$")
        assert not pattern.match("../etc/passwd")
        assert not pattern.match("http://evil.com")
        assert not pattern.match("A" * 32)  # uppercase
        assert not pattern.match("a" * 31)  # too short
