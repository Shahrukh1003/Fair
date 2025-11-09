"""
JWT Authentication Module for BiasCheck v3.0

Provides secure JWT-based authentication with access and refresh tokens.
Supports role-based access control (monitor, auditor, admin).
"""

import os
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET', secrets.token_urlsafe(32))
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE = int(os.getenv('JWT_ACCESS_EXPIRE', 900))  # 15 minutes
REFRESH_TOKEN_EXPIRE = int(os.getenv('JWT_REFRESH_EXPIRE', 2592000))  # 30 days

# Simple in-memory user database (for production, use PostgreSQL)
USERS_DB = {
    'admin': {
        'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
        'role': 'admin',
        'name': 'Administrator'
    },
    'auditor': {
        'password_hash': hashlib.sha256('auditor123'.encode()).hexdigest(),
        'role': 'auditor',
        'name': 'Compliance Auditor'
    },
    'monitor': {
        'password_hash': hashlib.sha256('monitor123'.encode()).hexdigest(),
        'role': 'monitor',
        'name': 'Fairness Monitor'
    }
}

# Refresh token storage (in production, use Redis or database)
REFRESH_TOKENS = set()


def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == password_hash


def create_access_token(username: str, role: str) -> str:
    """Create JWT access token with 15-minute expiration"""
    payload = {
        'username': username,
        'role': role,
        'type': 'access',
        'exp': datetime.now(timezone.utc) + timedelta(seconds=ACCESS_TOKEN_EXPIRE),
        'iat': datetime.now(timezone.utc)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(username: str, role: str) -> str:
    """Create JWT refresh token with 30-day expiration"""
    token_id = secrets.token_urlsafe(32)
    payload = {
        'username': username,
        'role': role,
        'type': 'refresh',
        'jti': token_id,
        'exp': datetime.now(timezone.utc) + timedelta(seconds=REFRESH_TOKEN_EXPIRE),
        'iat': datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    REFRESH_TOKENS.add(token_id)
    return token


def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {'valid': True, 'payload': payload}
    except jwt.ExpiredSignatureError:
        return {'valid': False, 'error': 'Token has expired'}
    except jwt.InvalidTokenError as e:
        return {'valid': False, 'error': f'Invalid token: {str(e)}'}


def authenticate_user(username: str, password: str) -> dict:
    """Authenticate user and return tokens"""
    user = USERS_DB.get(username)
    
    if not user:
        return {'success': False, 'message': 'Invalid username or password'}
    
    if not verify_password(password, user['password_hash']):
        return {'success': False, 'message': 'Invalid username or password'}
    
    access_token = create_access_token(username, user['role'])
    refresh_token = create_refresh_token(username, user['role'])
    
    logger.info(f"User '{username}' logged in successfully (role: {user['role']})")
    
    return {
        'success': True,
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRE,
        'user': {
            'username': username,
            'role': user['role'],
            'name': user['name']
        }
    }


def refresh_access_token(refresh_token: str) -> dict:
    """Generate new access token from refresh token"""
    result = decode_token(refresh_token)
    
    if not result['valid']:
        return {'success': False, 'message': result['error']}
    
    payload = result['payload']
    
    if payload.get('type') != 'refresh':
        return {'success': False, 'message': 'Invalid token type'}
    
    if payload.get('jti') not in REFRESH_TOKENS:
        return {'success': False, 'message': 'Refresh token has been revoked'}
    
    access_token = create_access_token(payload['username'], payload['role'])
    
    logger.info(f"Access token refreshed for user '{payload['username']}'")
    
    return {
        'success': True,
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRE
    }


def revoke_refresh_token(refresh_token: str) -> bool:
    """Revoke a refresh token"""
    result = decode_token(refresh_token)
    if result['valid'] and result['payload'].get('jti'):
        REFRESH_TOKENS.discard(result['payload']['jti'])
        return True
    return False


def require_jwt(required_roles=None):
    """
    Decorator to protect endpoints with JWT authentication
    
    Usage:
        @require_jwt()  # Any authenticated user
        @require_jwt(['admin'])  # Admin only
        @require_jwt(['auditor', 'admin'])  # Auditor or Admin
    """
    if required_roles is None:
        required_roles = []
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({
                    'status': 'error',
                    'message': 'Authorization header missing'
                }), 401
            
            try:
                scheme, token = auth_header.split()
                if scheme.lower() != 'bearer':
                    return jsonify({
                        'status': 'error',
                        'message': 'Invalid authentication scheme'
                    }), 401
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid authorization header format'
                }), 401
            
            result = decode_token(token)
            
            if not result['valid']:
                return jsonify({
                    'status': 'error',
                    'message': result['error']
                }), 401
            
            payload = result['payload']
            
            if payload.get('type') != 'access':
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid token type'
                }), 401
            
            # Check role authorization
            if required_roles and payload.get('role') not in required_roles:
                return jsonify({
                    'status': 'error',
                    'message': f"Insufficient permissions. Required roles: {', '.join(required_roles)}"
                }), 403
            
            # Add user info to request context
            request.current_user = {
                'username': payload.get('username'),
                'role': payload.get('role')
            }
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def get_current_user():
    """Get current authenticated user from request context"""
    return getattr(request, 'current_user', None)
