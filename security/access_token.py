import json
from datetime import datetime, timedelta, timezone

import jwt

from settings import settings

def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # 预留sub字段，暂不使用，后期可以通过device_uuid来获取接入连接的客户端设备数字证书已验证合法性
    # to_encode.update({"sub": json.dumps({"identity": "", "device_uuid": ""})})
    # to_encode.update({"iat": datetime.now(timezone.utc)})
    to_encode.update({"exp": expire})
    print("to_encode:", settings.SECRET_KEY)
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt