"""
core/utils/auth.py
Utilidades de autenticación corporativa mediante JWT y almacenamiento en cookies.
Utiliza bibliotecas estándar de Python para evitar dependencias de compilación externas.
"""
import base64
import hashlib
import hmac
import json
import os
import time
from typing import Optional, Tuple
import streamlit as st

# Clave secreta para firmar JWTs
try:
    SECRET_KEY = st.secrets.get("auth_secret", "EMCA_STOCHASTIC_SYSTEM_DEFAULT_JWT_SECRET_2026")
except Exception:
    SECRET_KEY = "EMCA_STOCHASTIC_SYSTEM_DEFAULT_JWT_SECRET_2026"

# ---------------------------------------------------------------------------
# Seguridad y Hashes de Contraseña
# ---------------------------------------------------------------------------

def generate_salt() -> str:
    """Genera un salt aleatorio en formato hexadecimal."""
    return os.urandom(16).hex()

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Genera el hash SHA-256 de una contraseña usando sal (salt).
    Retorna una tupla (hash_hex, salt_hex).
    """
    if salt is None:
        salt = generate_salt()
    
    # Derivación PBKDF2 simplificada usando SHA256 estándar
    password_bytes = password.encode("utf-8")
    salt_bytes = salt.encode("utf-8")
    
    # 50,000 iteraciones para dificultar ataques de fuerza bruta
    pw_hash = hashlib.pbkdf2_hmac("sha256", password_bytes, salt_bytes, 50000)
    return pw_hash.hex(), salt

def verify_password(password: str, expected_hash: str, salt: str) -> bool:
    """Valida si una contraseña ingresada coincide con el hash guardado."""
    pw_hash, _ = hash_password(password, salt)
    return hmac.compare_digest(pw_hash, expected_hash)

# ---------------------------------------------------------------------------
# Creación y Validación de JWT (JSON Web Tokens)
# ---------------------------------------------------------------------------

def create_jwt(payload: dict, expires_in: int = 86400) -> str:
    """
    Crea un token JWT firmado con HMAC-SHA256.
    Por defecto expira en 24 horas (86400 segundos).
    """
    # 1. Header estándar
    header = {"alg": "HS256", "typ": "JWT"}
    header_json = json.dumps(header, separators=(",", ":")).encode("utf-8")
    header_b64 = base64.urlsafe_b64encode(header_json).decode("utf-8").rstrip("=")
    
    # 2. Payload con expiración
    payload_copy = payload.copy()
    payload_copy["exp"] = int(time.time()) + expires_in
    payload_json = json.dumps(payload_copy, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode("utf-8").rstrip("=")
    
    # 3. Firma HMAC-SHA256
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def verify_jwt(token: str) -> Optional[dict]:
    """
    Valida un JWT y retorna su payload original si es válido.
    Retorna None si la firma es incorrecta o el token ya expiró.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
            
        header_b64, payload_b64, signature_b64 = parts
        
        # Validar la firma HMAC-SHA256
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode("utf-8").rstrip("=")
        
        if not hmac.compare_digest(signature_b64, expected_sig_b64):
            return None
            
        # Decodificar el Payload con padding manual
        def b64_decode(data: str) -> dict:
            rem = len(data) % 4
            if rem > 0:
                data += "=" * (4 - rem)
            decoded_bytes = base64.urlsafe_b64decode(data.encode("utf-8"))
            return json.loads(decoded_bytes.decode("utf-8"))
            
        payload = b64_decode(payload_b64)
        
        # Comprobar expiración
        if payload.get("exp", 0) < time.time():
            return None
            
        return payload
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Gestión de Cookies de Navegador en Streamlit
# ---------------------------------------------------------------------------

def inject_cookie_setter_js(token: str, max_age: int = 86400):
    """Inyecta JavaScript en el cliente para guardar el JWT en la cookie de sesión."""
    # Intentamos escribir en el window.parent.document ya que Streamlit renderiza en iframes.
    # Usamos SameSite=Strict y Secure (si es HTTPS) para seguir estándares de seguridad.
    js_code = f"""
    <script>
        const cookieName = "emca_session";
        const cookieValue = "{token}";
        const maxAge = {max_age};
        const sameSite = "SameSite=Strict";
        const secure = window.location.protocol === "https:" ? "Secure" : "";
        
        const cookieStr = `${{cookieName}}=${{cookieValue}}; path=/; max-age=${{maxAge}}; ${{sameSite}}; ${{secure}}`;
        
        try {{
            window.parent.document.cookie = cookieStr;
        }} catch(e) {{
            document.cookie = cookieStr;
        }}
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)

def inject_cookie_remover_js():
    """Inyecta JavaScript en el cliente para eliminar la cookie de sesión y cerrar sesión."""
    js_code = """
    <script>
        const cookieStr = "emca_session=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC; SameSite=Strict";
        try {
            window.parent.document.cookie = cookieStr;
        } catch(e) {
            document.cookie = cookieStr;
        }
    </script>
    """
    st.components.v1.html(js_code, height=0, width=0)
