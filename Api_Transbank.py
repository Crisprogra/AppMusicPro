import requests
from flask import request

def header_request_transbank():
    headers = {
        "Authorization": "Token",  # Reemplaza "Token" con el tipo de autorización que corresponda
        "Tbk-Api-Key-Id": "597055555532",  # Reemplaza con tu API Key ID de Transbank
        "Tbk-Api-Key-Secret": "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",  # Reemplaza con tu API Key Secret de Transbank
        "Content-Type": "application/json"
    }
    return headers

