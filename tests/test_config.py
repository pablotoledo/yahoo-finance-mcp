"""
Tests for configuration system.
"""
import pytest
import os
from src.config import ServerConfig, TransportType, HTTPConfig


class TestServerConfig:
    """Tests for ServerConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ServerConfig()
        
        assert config.transport == TransportType.STDIO
        assert config.log_level == "INFO"
        assert config.http.host == "0.0.0.0"
        assert config.http.port == 3000
        assert config.http.stateless is False

    def test_transport_types(self):
        """Test transport type enum."""
        assert TransportType.STDIO.value == "stdio"
        assert TransportType.HTTP.value == "http"

    def test_custom_http_config(self):
        """Test custom HTTP configuration."""
        http = HTTPConfig(
            host="127.0.0.1",
            port=8080,
            stateless=True,
            cors_origins=["http://localhost:3000"]
        )
        
        assert http.host == "127.0.0.1"
        assert http.port == 8080
        assert http.stateless is True
        assert "http://localhost:3000" in http.cors_origins


class TestEnvironmentVariables:
    """Tests for environment variable configuration."""

    def test_transport_from_env(self, monkeypatch):
        """Test setting transport via environment variable."""
        monkeypatch.setenv("YF_MCP_TRANSPORT", "http")
        
        config = ServerConfig()
        assert config.transport == TransportType.HTTP

    def test_log_level_from_env(self, monkeypatch):
        """Test setting log level via environment variable."""
        monkeypatch.setenv("YF_MCP_LOG_LEVEL", "DEBUG")
        
        config = ServerConfig()
        assert config.log_level == "DEBUG"

    def test_nested_http_config_from_env(self, monkeypatch):
        """Test nested HTTP configuration via environment variables."""
        monkeypatch.setenv("YF_MCP_HTTP__HOST", "0.0.0.0")
        monkeypatch.setenv("YF_MCP_HTTP__PORT", "8000")
        monkeypatch.setenv("YF_MCP_HTTP__STATELESS", "true")
        
        config = ServerConfig()
        assert config.http.host == "0.0.0.0"
        assert config.http.port == 8000
        assert config.http.stateless is True

    def test_case_insensitive_env_vars(self, monkeypatch):
        """Test case-insensitive environment variables."""
        monkeypatch.setenv("yf_mcp_transport", "http")
        
        config = ServerConfig()
        assert config.transport == TransportType.HTTP


class TestHTTPConfig:
    """Tests for HTTPConfig."""

    def test_default_cors_origins(self):
        """Test default CORS origins."""
        http = HTTPConfig()
        
        assert "*" in http.cors_origins

    def test_custom_cors_origins(self):
        """Test custom CORS origins."""
        http = HTTPConfig(
            cors_origins=[
                "http://localhost:3000",
                "https://example.com"
            ]
        )
        
        assert len(http.cors_origins) == 2
        assert "http://localhost:3000" in http.cors_origins

    def test_auth_disabled_by_default(self):
        """Test OAuth is disabled by default."""
        http = HTTPConfig()
        
        assert http.enable_auth is False
        assert http.issuer_url is None

    def test_auth_configuration(self):
        """Test OAuth configuration."""
        http = HTTPConfig(
            enable_auth=True,
            issuer_url="https://auth.example.com",
            required_scopes=["read", "write"]
        )
        
        assert http.enable_auth is True
        assert http.issuer_url == "https://auth.example.com"
        assert "read" in http.required_scopes


class TestConfigValidation:
    """Tests for configuration validation."""

    def test_invalid_port_too_low(self):
        """Test port validation (too low)."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            HTTPConfig(port=100)

    def test_invalid_port_too_high(self):
        """Test port validation (too high)."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            HTTPConfig(port=70000)

    def test_valid_port_range(self):
        """Test valid port range."""
        for port in [1024, 3000, 8080, 65535]:
            http = HTTPConfig(port=port)
            assert http.port == port

    def test_invalid_log_level(self):
        """Test invalid log level."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            ServerConfig(log_level="INVALID")

    def test_valid_log_levels(self):
        """Test valid log levels."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
            config = ServerConfig(log_level=level)
            assert config.log_level == level


class TestConfigSerialization:
    """Tests for configuration serialization."""

    def test_config_to_dict(self):
        """Test converting config to dict."""
        config = ServerConfig(
            transport=TransportType.HTTP,
            log_level="DEBUG"
        )
        
        data = config.model_dump()
        
        assert data["transport"] == "http"
        assert data["log_level"] == "DEBUG"
        assert "http" in data

    def test_config_to_json(self):
        """Test converting config to JSON."""
        config = ServerConfig()
        
        json_str = config.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "transport" in json_str


class TestRateLimitingConfig:
    """Tests for rate limiting configuration (future feature)."""

    def test_rate_limiting_disabled_by_default(self):
        """Test rate limiting is disabled by default."""
        config = ServerConfig()
        
        assert config.enable_rate_limit is False

    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration."""
        config = ServerConfig(
            enable_rate_limit=True,
            requests_per_minute=120
        )
        
        assert config.enable_rate_limit is True
        assert config.requests_per_minute == 120
