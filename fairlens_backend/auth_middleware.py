"""
Authentication Middleware for FairLens

Purpose: Implement role-based access control (RBAC) for compliance endpoints.

This module provides simple token-based authentication to demonstrate
how fairness monitoring systems should restrict access to sensitive
compliance data based on user roles.

How it fits: This is the SECURITY layer protecting the FairLens API.
User → [Auth Check] → API → Data → Metric → Alert → Log
"""

from functools import wraps
from flask import request, jsonify
from typing import Dict, Optional, Callable


# Static token store (for demonstration only)
# In production, use JWT, OAuth2, or integrate with identity provider
TOKENS = {
    "MONITOR123": {
        "role": "monitor",
        "description": "Can view fairness metrics and run checks"
    },
    "AUDITOR123": {
        "role": "auditor",
        "description": "Can view audit logs and decrypt alerts"
    },
    "ADMIN123": {
        "role": "admin",
        "description": "Full access including key management"
    }
}


# Role hierarchy (higher roles inherit lower role permissions)
ROLE_HIERARCHY = {
    "monitor": 1,
    "auditor": 2,
    "admin": 3
}


def verify_token(token: str) -> Optional[Dict]:
    """
    Verify if a token is valid and return associated role information.
    
    Parameters:
    -----------
    token : str
        The authentication token to verify
    
    Returns:
    --------
    Dict or None : Token info if valid, None if invalid
        Contains: {"role": str, "description": str}
    """
    return TOKENS.get(token)


def has_permission(user_role: str, required_role: str) -> bool:
    """
    Check if a user role has permission for a required role.
    
    Uses role hierarchy - higher roles inherit lower role permissions.
    For example, "admin" can access "auditor" and "monitor" endpoints.
    
    Parameters:
    -----------
    user_role : str
        The role of the authenticated user
    required_role : str
        The minimum role required for the endpoint
    
    Returns:
    --------
    bool : True if user has permission, False otherwise
    """
    user_level = ROLE_HIERARCHY.get(user_role, 0)
    required_level = ROLE_HIERARCHY.get(required_role, 999)
    return user_level >= required_level


def require_role(required_role: str) -> Callable:
    """
    Decorator to protect Flask routes with role-based access control.
    
    Usage:
    ------
    @app.route('/api/audit_history')
    @require_role('auditor')
    def audit_history():
        return jsonify({"data": "sensitive audit logs"})
    
    Parameters:
    -----------
    required_role : str
        Minimum role required to access the endpoint
        Options: "monitor", "auditor", "admin"
    
    Returns:
    --------
    Callable : Decorated function with auth check
    
    Authentication Flow:
    --------------------
    1. Extract token from Authorization header
    2. Verify token is valid
    3. Check if user role has required permissions
    4. Allow access or return 401/403 error
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extract token from Authorization header
            auth_header = request.headers.get('Authorization', '')
            
            # Support both "Bearer TOKEN" and just "TOKEN" formats
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]
            else:
                token = auth_header
            
            # Verify token
            token_info = verify_token(token)
            
            if not token_info:
                return jsonify({
                    "error": "Unauthorized",
                    "message": "Invalid or missing authentication token",
                    "hint": "Include 'Authorization: Bearer <token>' header"
                }), 401
            
            # Check role permissions
            user_role = token_info['role']
            if not has_permission(user_role, required_role):
                return jsonify({
                    "error": "Forbidden",
                    "message": f"Role '{user_role}' does not have permission to access this endpoint",
                    "required_role": required_role,
                    "your_role": user_role
                }), 403
            
            # Add user info to request context for logging
            request.user_role = user_role
            
            # Allow access
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def get_token_for_role(role: str) -> Optional[str]:
    """
    Get a valid token for a specific role (for testing/demo purposes).
    
    Parameters:
    -----------
    role : str
        The role to get a token for
    
    Returns:
    --------
    str or None : A valid token for that role, or None if role doesn't exist
    """
    for token, info in TOKENS.items():
        if info['role'] == role:
            return token
    return None


def list_available_roles() -> Dict:
    """
    List all available roles and their descriptions.
    
    Returns:
    --------
    Dict : Mapping of role names to descriptions
    """
    roles = {}
    for token_info in TOKENS.values():
        role = token_info['role']
        if role not in roles:
            roles[role] = token_info['description']
    return roles


"""
WHY ROLE-BASED ACCESS CONTROL MATTERS:

1. SEPARATION OF DUTIES:
   - Monitors can check fairness but not access sensitive audit logs
   - Auditors can review compliance data but not modify system
   - Admins have full control for system management

2. COMPLIANCE REQUIREMENTS:
   - GDPR requires access controls for personal data
   - SOC 2 mandates role-based permissions
   - Banking regulations require audit trail access restrictions

3. SECURITY BEST PRACTICES:
   - Principle of least privilege
   - Prevents unauthorized data access
   - Creates accountability trail

REAL-WORLD ROLES IN BANKING:

Monitor Role:
- Data scientists running fairness checks
- ML engineers testing models
- Automated monitoring systems

Auditor Role:
- Compliance officers reviewing alerts
- Internal audit teams
- Regulatory inspectors

Admin Role:
- Security team managing encryption keys
- System administrators
- Senior compliance managers

HOW TO EXTEND FOR PRODUCTION:

1. Replace static tokens with JWT (JSON Web Tokens):
   - Include expiration times
   - Add refresh token mechanism
   - Sign with secret key

2. Integrate with identity provider:
   - OAuth2 / OpenID Connect
   - LDAP / Active Directory
   - SAML for enterprise SSO

3. Add more granular permissions:
   - Read vs. write access
   - Model-specific permissions
   - Time-based access (business hours only)

4. Implement audit logging:
   - Log every authentication attempt
   - Track which user accessed what data
   - Alert on suspicious access patterns

5. Add rate limiting:
   - Prevent brute force attacks
   - Limit API calls per user
   - Implement backoff strategies

DEMO TOKENS FOR TESTING:
- Monitor: MONITOR123
- Auditor: AUDITOR123
- Admin: ADMIN123

Example curl commands:
curl -H "Authorization: Bearer MONITOR123" http://localhost:8000/api/monitor_fairness
curl -H "Authorization: Bearer AUDITOR123" http://localhost:8000/api/audit_history
"""
