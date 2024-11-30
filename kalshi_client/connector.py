import requests
from datetime import datetime
from typing import Any, Dict, Optional
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature
import time 
import base64
from kalshi_client.http_helpers import HttpError


class Connector:
    """A simple client that allows utils to call authenticated Kalshi API endpoints."""
    def __init__(
        self,
        host: str,
        key_id: str,
        private_key: rsa.RSAPrivateKey,
        rate_limit = 10,
        user_id: Optional[str] = None,
    ):
        """Initializes the client and logs in the specified user.
        Raises an HttpError if the user could not be authenticated.
        """
        self.host = host 
        self.key_id: str = key_id
        self.user_id = user_id
        self.private_key: rsa.RSAPrivateKey = private_key
        self.threshold = 1 / rate_limit
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json",
                                     "KALSHI-ACCESS-KEY": self.key_id,})
        self.last_api_call = datetime.now()

    """Built in rate-limiter. We STRONGLY encourage you to keep 
    some sort of rate limiting, just in case there is a bug in your 
    code. Feel free to adjust the threshold"""
    def rate_limit(self) -> None:

        # Check if the time since the last API call is below the threshold
        elapsed_time = (datetime.now() - self.last_api_call).total_seconds()
        if elapsed_time < self.threshold:
            time.sleep(self.threshold - elapsed_time)

        # Update the last API call timestamp
        self.last_api_call = datetime.now()


    def post(self, path: str, body: dict) -> Any:
        """POSTs to an authenticated Kalshi HTTP endpoint.
        Returns the response body. Raises an HttpError on non-2XX results.
        """
        self.rate_limit()

        response = self.session.post(
            self.host + path, data=body, headers=self.request_headers("POST", path)
        )
        self.raise_if_bad_response(response)
        return response.json()

    def get(self, path: str, params: Dict[str, Any] = {}) -> Any:
        """GETs from an authenticated Kalshi HTTP endpoint.
        Returns the response body. Raises an HttpError on non-2XX results."""
        self.rate_limit()
        
        response = self.session.get(
            self.host + path, headers=self.request_headers("GET", path), params=params
        )
        self.raise_if_bad_response(response)
        return response.json()

    def delete(self, path: str, params: Dict[str, Any] = {}) -> Any:
        """Posts from an authenticated Kalshi HTTP endpoint.
        Returns the response body. Raises an HttpError on non-2XX results."""
        self.rate_limit()
        
        response = self.session.delete(
            self.host + path, headers=self.request_headers("DELETE", path), params=params
        )
        self.raise_if_bad_response(response)
        return response.json()

    def request_headers(self, method: str, path: str) -> Dict[str, Any]:
        # Generate the current timestamp in milliseconds
        timestampt_str = str(int(datetime.now().timestamp() * 1000))

        # Extract the path without query parameters
        clean_path = path.split('?', 1)[0]

        # Construct the message string for signing
        msg_string = f"{timestampt_str}{method}/trade-api/v2{clean_path}"

        # Sign the message string
        signature = self.sign_pss_text(msg_string)

        # Build headers dictionary
        headers = {
            "KALSHI-ACCESS-SIGNATURE": signature,
            "KALSHI-ACCESS-TIMESTAMP": timestampt_str,
        }
        return headers

    
    def sign_pss_text(self, text: str) -> str:
        # Before signing, we need to hash our message.
        # The hash is what we actually sign.
        # Convert the text to bytes
        message = text.encode('utf-8')
        try:
            signature = self.private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.DIGEST_LENGTH
                ),
                hashes.SHA256()
            )
            return base64.b64encode(signature).decode('utf-8')
        except InvalidSignature as e:
            raise ValueError("RSA sign PSS failed") from e

    def raise_if_bad_response(self, response: requests.Response) -> None:
        if response.status_code not in range(200, 299):
            if response.status_code == 404:
                raise HttpError(response.reason, response.status_code, tip='Check ticker used for call if one was provided')
            elif response.status_code == 400:
                raise HttpError(response.reason, response.status_code, tip='One or more of the parameters could be wrong')
            else:
                raise HttpError(response.reason, response.status_code)
            
    def query_generation(self, params:dict) -> str:
        """
        Generate a URL query string from a dictionary of parameters.
        """
        query = '&'.join(f'{str(k)}={str(v)}' for k, v in params.items() if v)
        return f'?{query}' if query else ''