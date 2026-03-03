"""
Configuration management for trading system
Centralized configuration with environment variable support
"""
import os
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ExchangeConfig:
    """Exchange-specific configuration"""
    name: str
    api_key_env: str
    api_secret_env: str
    enabled: bool = True
    rate_limit: int = 10  # requests per second
    markets: List[str] = field(default_factory=lambda: ['BTC/USDT', 'ETH/USDT'])
    
@dataclass
class FirebaseConfig:
    """Firebase configuration"""
    project_id: str
    collection_prefix: str = "trading_system"
    # Service account path will be loaded from environment
    service_account_info: Optional[Dict] = None
    
@dataclass
class ResearchConfig:
    """Research engine configuration"""
    data_collection_interval: int = 60  # seconds
    max_candles: int = 1000
    indicators: List[str] = field(default_factory=lambda: [
        'RSI', 'MACD', 'BBANDS', 'ATR', 'VWAP'
    ])
    sentiment_sources: List[str] = field(default_factory=lambda: [
        'cryptopanic', 'twitter'
    ])
    
@dataclass
class RiskConfig:
    """Risk management configuration"""
    max_position_size: float = 0.1  # 10% of portfolio
    max_daily_loss: float = 0.02  # 2%
    stop_loss_pct: float = 0.02  # 2%
    take_profit_pct: float = 0.04  # 4%
    max_open_positions: int = 5
    
class TradingSystemConfig:
    """Main configuration class"""
    
    def __init__(self):
        self.environment = os.getenv('TRADING_ENV', 'development')
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        
        # Firebase configuration
        firebase_project = os.getenv('FIREBASE_PROJECT_ID')
        if not firebase_project:
            logger.warning("FIREBASE_PROJECT_ID not set, Firebase features disabled")
        self.firebase = FirebaseConfig(project_id=firebase_project or "trading-system-dev")
        
        # Exchange configurations
        self.exchanges = [
            ExchangeConfig(
                name='binance',
                api_key_env='BINANCE_API_KEY',
                api_secret_env='BINANCE_API_SECRET'
            ),
            ExchangeConfig(
                name='coinbase',
                api_key_env='COINBASE_API_KEY',
                api_secret_env='COINBASE_API_SECRET'
            )
        ]
        
        # Research configuration
        self.research = ResearchConfig()
        
        # Risk configuration
        self.risk = RiskConfig()
        
        # System paths
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / 'data'
        self.logs_dir = self.base_dir / 'logs'
        
        # Ensure directories exist
        self._ensure_directories()
        
        logger.info(f"Configuration loaded for environment: {self.environment}")
    
    def _ensure_directories(self):
        """Create necessary directories"""
        for directory in [self.data_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    def validate(self) -> bool:
        """Validate configuration"""
        issues = []
        
        # Check Firebase configuration
        if not self.firebase.project_id:
            issues.append("Firebase project ID not configured")
        
        # Check exchange API keys for enabled exchanges
        for exchange in self.exchanges:
            if exchange.enabled:
                if not os.getenv(exchange.api_key_env):
                    issues.append(f"API key not set for {exchange.name}: {exchange.api_key_env}")
                if not os.getenv(exchange.api_secret_env):
                    issues.append(f"API secret not set for {exchange.name}: {exchange.api_secret_env}")
        
        if issues:
            logger.error(f"Configuration validation failed: {issues}")