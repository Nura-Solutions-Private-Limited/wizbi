import base64
import json
import os
from datetime import datetime, timedelta
from typing import Optional

import structlog
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from jose import jwt

from core.config import settings

logger = structlog.getLogger(__name__)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


async def check_license():
    try:
        public_key_file = os.path.join(os.getcwd(), "public_key.pem")
        license_key_file = os.path.join(os.getcwd(), "license.json")
        with open(public_key_file, "rb") as public_file:
            public_pem = public_file.read()
            public_key = serialization.load_pem_public_key(public_pem,
                                                           backend=default_backend())

        # Read the license file
        with open(license_key_file, "r") as f:
            license_file = json.load(f)

        # Extract the license data and signature
        license_data = license_file["license_data"]
        signature = base64.b64decode(license_file["signature"])  # Decode the Base64-encoded signature

        # Serialize the license data back into JSON
        license_json = json.dumps(license_data).encode("utf-8")

        # Verify the signature using the public key
        try:
            public_key.verify(
                signature,
                license_json,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            # Check expiration date
            expiration_date = datetime.strptime(license_data["expiration_date"], "%Y-%m-%d").date()
            if expiration_date >= datetime.now().date():
                logger.info(f"License is active. Expiry date: {expiration_date}")
                return True
            else:
                logger.info(f"License has expired. Expiry date: {expiration_date}")
                return False
        except Exception as e:
            logger.info("Invalid license:", e)
            return False
    except Exception as e:
        logger.info(f"License check failed: {e}")
        return False
