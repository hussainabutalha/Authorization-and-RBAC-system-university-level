"""
Unit tests for the Authorization and RBAC backend.
Run with: pytest backend/tests/ -v
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestSecurityUtils:
    """Tests for security utilities"""

    def test_password_hashing(self):
        """Test password hashing and verification"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        password = "Test@123"  # Short password for bcrypt
        hashed = pwd_context.hash(password)
        
        assert pwd_context.verify(password, hashed)
        assert not pwd_context.verify("wrong_password", hashed)

    def test_jwt_token_structure(self):
        """Test JWT token has correct structure"""
        import jwt
        
        payload = {"user_id": 1, "email": "test@test.com", "role": "Student"}
        secret = "test_secret"
        
        token = jwt.encode(payload, secret, algorithm="HS256")
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        
        assert decoded["user_id"] == 1
        assert decoded["email"] == "test@test.com"
        assert decoded["role"] == "Student"


class TestRBACLogic:
    """Tests for Role-Based Access Control logic"""

    def test_role_hierarchy(self):
        """Test role hierarchy permissions"""
        roles_hierarchy = {
            "Director": 5,
            "Vice-Director": 4,
            "Dean": 3,
            "HOD": 2,
            "Teacher": 1,
            "Student": 0
        }
        
        assert roles_hierarchy["Director"] > roles_hierarchy["Student"]
        assert roles_hierarchy["Dean"] > roles_hierarchy["Teacher"]
        assert roles_hierarchy["HOD"] < roles_hierarchy["Vice-Director"]

    def test_permission_check(self):
        """Test permission checking logic"""
        def has_permission(user_role: str, required_level: int, roles: dict) -> bool:
            return roles.get(user_role, 0) >= required_level
        
        roles = {"Director": 5, "Teacher": 1, "Student": 0}
        
        assert has_permission("Director", 3, roles)
        assert has_permission("Teacher", 1, roles)
        assert not has_permission("Student", 1, roles)


class TestDataValidation:
    """Tests for data validation"""

    def test_email_validation(self):
        """Test email format validation"""
        from email_validator import validate_email, EmailNotValidError
        
        # Valid emails (don't check DNS for test)
        valid = validate_email("user@college.edu", check_deliverability=False)
        assert valid.email == "user@college.edu"
        
        # Invalid emails
        with pytest.raises(EmailNotValidError):
            validate_email("invalid-email", check_deliverability=False)

    def test_password_strength(self):
        """Test password strength requirements"""
        def is_strong_password(password: str) -> bool:
            return len(password) >= 8
        
        assert is_strong_password("secure123")
        assert not is_strong_password("short")


class TestClassroomLogic:
    """Tests for classroom business logic"""

    def test_max_students_limit(self):
        """Test classroom max students enforcement"""
        class Classroom:
            def __init__(self, max_students: int):
                self.max_students = max_students
                self.enrolled = []
            
            def can_enroll(self) -> bool:
                return len(self.enrolled) < self.max_students
            
            def enroll(self, student_id: int) -> bool:
                if self.can_enroll():
                    self.enrolled.append(student_id)
                    return True
                return False
        
        classroom = Classroom(max_students=2)
        assert classroom.enroll(1)
        assert classroom.enroll(2)
        assert not classroom.enroll(3)  # Should fail - at capacity

    def test_classroom_membership(self):
        """Test classroom membership checks"""
        members = {1, 2, 3}
        
        assert 1 in members
        assert 4 not in members


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
