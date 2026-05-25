"""
Middleware de autenticación con Keycloak via Bearer Token (JWT).

Uso en rutas:
    from app.auth import require_auth, get_current_user

    @bp.route("/protected")
    @require_auth
    def protected_route():
        user = get_current_user()   # Dict con claims del token
        return jsonify(user)

    # Restringir por rol de Keycloak:
    @bp.route("/admin-only")
    @require_auth(roles=["editorial-admin"])
    def admin_route():
        ...
"""

import logging
from functools import wraps
from typing import Optional

import jwt
import requests
from flask import current_app, g, jsonify, request
from jwt import PyJWKClient, InvalidTokenError

logger = logging.getLogger(__name__)

# Cache del cliente JWKS para no descargar las claves en cada request
_jwks_client: Optional[PyJWKClient] = None


def _get_jwks_client() -> PyJWKClient:
    """Devuelve (o crea) el cliente JWKS cacheado."""
    global _jwks_client
    if _jwks_client is None:
        jwks_uri = current_app.config["KEYCLOAK_URL"] + \
                   "/realms/" + current_app.config["KEYCLOAK_REALM"] + \
                   "/protocol/openid-connect/certs"
        _jwks_client = PyJWKClient(jwks_uri, cache_keys=True)
    return _jwks_client


def _extract_token() -> Optional[str]:
    """Extrae el Bearer token del header Authorization."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[len("Bearer "):]
    return None


def _decode_token(token: str) -> dict:
    """
    Valida y decodifica el JWT de Keycloak.
    Lanza jwt.InvalidTokenError si el token no es válido.
    """
    client = _get_jwks_client()
    signing_key = client.get_signing_key_from_jwt(token)

    payload = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        options={"verify_exp": True, "verify_aud": False},
    )
    return payload


def require_auth(f=None, *, roles: list[str] | None = None):
    """
    Decorador que protege un endpoint con autenticación Bearer Token de Keycloak.

    Uso básico (solo autenticación):
        @require_auth
        def mi_ruta(): ...

    Uso con roles (autorización):
        @require_auth(roles=["editorial-admin"])
        def mi_ruta(): ...
    """
    # Permite usarlo tanto con como sin paréntesis: @require_auth o @require_auth(roles=[...])
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            token = _extract_token()

            if not token:
                return jsonify({"error": "Token de autenticación requerido."}), 401

            try:
                payload = _decode_token(token)
            except InvalidTokenError as e:
                logger.warning("Token inválido: %s", e)
                return jsonify({"error": "Token inválido o expirado."}), 401
            except requests.RequestException as e:
                logger.error("Error al contactar Keycloak: %s", e)
                return jsonify({"error": "Error interno de autenticación."}), 503

            # Guardar claims en el contexto de la request para usarlos en la ruta
            g.current_user = payload

            # Validar roles si se especificaron
            if roles:
                # Keycloak incluye los roles del cliente en resource_access.<client_id>.roles
                client_id = current_app.config["KEYCLOAK_CLIENT_ID"]
                user_roles: list[str] = (
                    payload.get("resource_access", {})
                    .get(client_id, {})
                    .get("roles", [])
                )
                # También incluir roles de realm si los hay
                realm_roles: list[str] = (
                    payload.get("realm_access", {}).get("roles", [])
                )
                all_roles = set(user_roles + realm_roles)

                if not any(role in all_roles for role in roles):
                    return jsonify({"error": "No tienes permisos para esta acción."}), 403

            return func(*args, **kwargs)
        return wrapper

    # @require_auth sin paréntesis: f es la función directamente
    if f is not None:
        return decorator(f)

    # @require_auth(...) con paréntesis: devuelve el decorador
    return decorator


def get_current_user() -> dict:
    """
    Devuelve los claims del token JWT del usuario autenticado.
    Solo disponible dentro de rutas protegidas con @require_auth.
    """
    return getattr(g, "current_user", {})
