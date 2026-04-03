import requests
import hmac
import hashlib
import time
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode

logger = logging.getLogger('trading_bot')

class BinanceAPIError(Exception):
    """Exception raised for errors returned directly by the Binance API."""
    def __init__(self, status_code, response_body):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(f"Binance API Error [{status_code}]: {response_body}")

class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = "https://testnet.binancefuture.com"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json;charset=utf-8",
            "X-MBX-APIKEY": self.api_key,
        })
        logger.info(f"Initialized BinanceFuturesClient with base_url={self.base_url}")

    def _get_timestamp(self) -> int:
        return int(time.time() * 1000)

    def _sign(self, params: Dict[str, Any]) -> str:
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def request(self, method: str, endpoint: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if parameters is None:
            parameters = {}


        parameters['timestamp'] = self._get_timestamp()
        
 
        parameters['signature'] = self._sign(parameters)

        url = f"{self.base_url}{endpoint}"
        
        logger.debug(f"Sending {method} request to {url} with params: {parameters}")

        try:
            response = self.session.request(method, url, params=parameters)
            logger.debug(f"Received response [{response.status_code}]: {response.text}")
            
          
            if response.status_code >= 400:
                logger.error(f"Binance API Error {response.status_code}: {response.text}")
                raise BinanceAPIError(response.status_code, response.json())
                
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.exception(f"Network/Connection error during {method} to {endpoint}: {e}")
            raise
