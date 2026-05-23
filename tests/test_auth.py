"""
tests/test_auth.py
Unit tests for the custom JWT and password hashing authentication module.
"""
import time
import pytest
from core.utils.auth import hash_password, verify_password, create_jwt, verify_jwt

def test_password_hashing():
    password = "SuperSecurePassword123"
    
    # Generar hash y salt
    pw_hash, salt = hash_password(password)
    
    assert pw_hash is not None
    assert salt is not None
    assert pw_hash != password
    
    # Verificar correcto
    assert verify_password(password, pw_hash, salt) is True
    
    # Verificar incorrecto
    assert verify_password("WrongPassword", pw_hash, salt) is False

def test_jwt_creation_and_verification():
    payload = {"username": "admin", "role": "admin", "nombre": "Administrador"}
    
    # Crear token
    token = create_jwt(payload, expires_in=10)
    
    assert token is not None
    assert len(token.split(".")) == 3
    
    # Verificar token
    verified_payload = verify_jwt(token)
    assert verified_payload is not None
    assert verified_payload["username"] == "admin"
    assert verified_payload["role"] == "admin"
    assert verified_payload["nombre"] == "Administrador"
    assert "exp" in verified_payload

def test_jwt_invalid_signature():
    payload = {"username": "admin"}
    token = create_jwt(payload, expires_in=10)
    
    # Modificar el token para invalidar la firma
    parts = token.split(".")
    modified_token = f"{parts[0]}.{parts[1]}.invalid_signature"
    
    assert verify_jwt(modified_token) is None

def test_jwt_expired():
    payload = {"username": "admin"}
    
    # Crear token con expiración en el pasado (-10 segundos)
    token = create_jwt(payload, expires_in=-10)
    
    # Validar que falla por estar expirado
    assert verify_jwt(token) is None
