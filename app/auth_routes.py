"""
Blueprint de gestión de usuarios y sesiones via Keycloak.

Endpoints:
    POST   /api/auth/login            - Obtener access + refresh token
    POST   /api/auth/logout           - Invalidar sesión (revoke refresh token)
    POST   /api/auth/refresh          - Renovar access token con refresh token
    POST   /api/auth/change-password  - Cambiar contraseña del usuario autenticado
    GET    /api/auth/me               - Información del usuario actual
"""

import logging

import requests
from flask import Blueprint, current_app, jsonify, request

from app.auth import get_current_user, require_auth

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


def _keycloak_token_url() -> str:
    """URL del endpoint de tokens de Keycloak."""
    return (
        f"{current_app.config['KEYCLOAK_URL']}"
        f"/realms/{current_app.config['KEYCLOAK_REALM']}"
        f"/protocol/openid-connect/token"
    )


def _keycloak_logout_url() -> str:
    """URL del endpoint de logout de Keycloak."""
    return (
        f"{current_app.config['KEYCLOAK_URL']}"
        f"/realms/{current_app.config['KEYCLOAK_REALM']}"
        f"/protocol/openid-connect/logout"
    )


def _keycloak_admin_users_url(user_id: str) -> str:
    """URL de la Admin API para gestionar un usuario específico."""
    return (
        f"{current_app.config['KEYCLOAK_URL']}"
        f"/admin/realms/{current_app.config['KEYCLOAK_REALM']}"
        f"/users/{user_id}"
    )


def _get_admin_token() -> str | None:
    """
    Obtiene un token de administrador usando client_credentials (Service Account).
    Requiere que el cliente tenga 'Service Accounts Enabled' en Keycloak
    y que su service account tenga el rol 'manage-users'.
    """
    resp = requests.post(
        _keycloak_token_url(),
        data={
            "grant_type": "client_credentials",
            "client_id": current_app.config["KEYCLOAK_CLIENT_ID"],
            "client_secret": current_app.config.get("KEYCLOAK_CLIENT_SECRET", ""),
        },
        timeout=10,
    )
    if resp.ok:
        return resp.json().get("access_token")
    logger.error("No se pudo obtener token de administrador: %s", resp.text)
    return None


# ─── Login ────────────────────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Autentica un usuario y retorna los tokens de Keycloak.

    Body JSON:
        username (str, requerido)
        password (str, requerido)

    Response:
        access_token  - JWT para incluir en el header Authorization
        refresh_token - Token para renovar la sesión
        expires_in    - Segundos hasta que expira el access_token
    """
    data = request.get_json()
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Los campos 'username' y 'password' son requeridos."}), 400

    try:
        resp = requests.post(
            _keycloak_token_url(),
            data={
                "grant_type": "password",
                "client_id": current_app.config["KEYCLOAK_CLIENT_ID"],
                "client_secret": current_app.config.get("KEYCLOAK_CLIENT_SECRET", ""),
                "username": data["username"],
                "password": data["password"],
                "scope": "openid profile email",
            },
            timeout=10,
        )
    except requests.RequestException as e:
        logger.error("Error al conectar con Keycloak: %s", e)
        return jsonify({"error": "No se pudo conectar con el servicio de autenticación."}), 503

    if resp.status_code == 401:
        return jsonify({"error": "Credenciales incorrectas."}), 401
    if not resp.ok:
        logger.error("Keycloak login error %s: %s", resp.status_code, resp.text)
        return jsonify({"error": "Error en el servicio de autenticación."}), resp.status_code

    token_data = resp.json()
    return jsonify({
        "access_token": token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token"),
        "token_type": token_data.get("token_type", "Bearer"),
        "expires_in": token_data.get("expires_in"),
    }), 200


# ─── Logout ───────────────────────────────────────────────────────────────────

@auth_bp.route("/logout", methods=["POST"])
@require_auth
def logout():
    """
    Cierra la sesión del usuario revocando el refresh token en Keycloak.

    Body JSON:
        refresh_token (str, requerido)
    """
    data = request.get_json()
    if not data or not data.get("refresh_token"):
        return jsonify({"error": "El campo 'refresh_token' es requerido."}), 400

    try:
        resp = requests.post(
            _keycloak_logout_url(),
            data={
                "client_id": current_app.config["KEYCLOAK_CLIENT_ID"],
                "client_secret": current_app.config.get("KEYCLOAK_CLIENT_SECRET", ""),
                "refresh_token": data["refresh_token"],
            },
            timeout=10,
        )
    except requests.RequestException as e:
        logger.error("Error al conectar con Keycloak para logout: %s", e)
        return jsonify({"error": "No se pudo conectar con el servicio de autenticación."}), 503

    if not resp.ok and resp.status_code != 204:
        logger.error("Keycloak logout error %s: %s", resp.status_code, resp.text)
        return jsonify({"error": "Error al cerrar la sesión."}), 400

    return jsonify({"message": "Sesión cerrada correctamente."}), 200


# ─── Refresh Token ─────────────────────────────────────────────────────────────

@auth_bp.route("/refresh", methods=["POST"])
def refresh():
    """
    Renueva el access_token usando el refresh_token.

    Body JSON:
        refresh_token (str, requerido)
    """
    data = request.get_json()
    if not data or not data.get("refresh_token"):
        return jsonify({"error": "El campo 'refresh_token' es requerido."}), 400

    try:
        resp = requests.post(
            _keycloak_token_url(),
            data={
                "grant_type": "refresh_token",
                "client_id": current_app.config["KEYCLOAK_CLIENT_ID"],
                "client_secret": current_app.config.get("KEYCLOAK_CLIENT_SECRET", ""),
                "refresh_token": data["refresh_token"],
            },
            timeout=10,
        )
    except requests.RequestException as e:
        logger.error("Error al renovar token: %s", e)
        return jsonify({"error": "No se pudo conectar con el servicio de autenticación."}), 503

    if resp.status_code == 400:
        return jsonify({"error": "Refresh token inválido o expirado. Inicia sesión nuevamente."}), 401
    if not resp.ok:
        return jsonify({"error": "Error al renovar la sesión."}), resp.status_code

    token_data = resp.json()
    return jsonify({
        "access_token": token_data.get("access_token"),
        "refresh_token": token_data.get("refresh_token"),
        "token_type": token_data.get("token_type", "Bearer"),
        "expires_in": token_data.get("expires_in"),
    }), 200


# ─── Cambio de Contraseña ─────────────────────────────────────────────────────

@auth_bp.route("/change-password", methods=["POST"])
@require_auth
def change_password():
    """
    Cambia la contraseña del usuario autenticado.

    Usa la Admin API de Keycloak con un Service Account del cliente.
    El cliente debe tener 'Service Accounts Enabled' y el rol 'manage-users'.

    Body JSON:
        new_password    (str, requerido)
        temporary       (bool, opcional) - Si es True, el usuario deberá cambiarla en el próximo login
    """
    data = request.get_json()
    if not data or not data.get("new_password"):
        return jsonify({"error": "El campo 'new_password' es requerido."}), 400

    new_password = data["new_password"]
    if len(new_password) < 8:
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres."}), 400

    # Obtener el ID del usuario desde el token actual (claim 'sub')
    current_user = get_current_user()
    user_id = current_user.get("sub")
    if not user_id:
        return jsonify({"error": "No se pudo identificar al usuario."}), 400

    # Obtener token de administrador via Service Account
    admin_token = _get_admin_token()
    if not admin_token:
        return jsonify({"error": "Error interno: no se pudo obtener permisos de administración."}), 503

    # Llamar a la Admin API de Keycloak para resetear la contraseña
    try:
        resp = requests.put(
            f"{_keycloak_admin_users_url(user_id)}/reset-password",
            json={
                "type": "password",
                "value": new_password,
                "temporary": data.get("temporary", False),
            },
            headers={"Authorization": f"Bearer {admin_token}"},
            timeout=10,
        )
    except requests.RequestException as e:
        logger.error("Error al cambiar contraseña: %s", e)
        return jsonify({"error": "No se pudo conectar con el servicio de autenticación."}), 503

    if not resp.ok and resp.status_code != 204:
        logger.error("Error al cambiar contraseña %s: %s", resp.status_code, resp.text)
        return jsonify({"error": "No se pudo cambiar la contraseña."}), 400

    return jsonify({"message": "Contraseña actualizada correctamente."}), 200


# ─── Perfil del usuario actual ────────────────────────────────────────────────

@auth_bp.route("/me", methods=["GET"])
@require_auth
def me():
    """
    Retorna la información del usuario autenticado extraída del JWT.
    No hace ninguna llamada adicional a Keycloak.
    """
    user = get_current_user()
    return jsonify({
        "id": user.get("sub"),
        "username": user.get("preferred_username"),
        "email": user.get("email"),
        "first_name": user.get("given_name"),
        "last_name": user.get("family_name"),
        "roles": (
            user.get("resource_access", {})
            .get(current_app.config["KEYCLOAK_CLIENT_ID"], {})
            .get("roles", [])
        ),
    }), 200
