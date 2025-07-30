import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestAuth:
    """认证功能测试类"""
    
    def test_register_success(self, client: TestClient, sample_user_data):
        """测试用户注册成功"""
        response = client.post("/auth/register", json=sample_user_data)
        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert data["message"] == "用户注册成功"
    
    def test_register_duplicate_email(self, client: TestClient, sample_user_data):
        """测试重复邮箱注册失败"""
        # 先注册一个用户
        client.post("/auth/register", json=sample_user_data)
        
        # 尝试用相同邮箱再次注册
        duplicate_data = sample_user_data.copy()
        duplicate_data["username"] = "anotheruser"
        response = client.post("/auth/register", json=duplicate_data)
        assert response.status_code == 400
        assert "邮箱已存在" in response.json()["detail"]
    
    def test_login_success(self, client: TestClient, sample_user_data):
        """测试登录成功"""
        # 先注册用户
        client.post("/auth/register", json=sample_user_data)
        
        # 登录
        login_data = {
            "username": sample_user_data["username"],
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "userId" in data
        assert "username" in data
        assert "role" in data
    
    def test_login_wrong_credentials(self, client: TestClient, sample_user_data):
        """测试错误凭据登录失败"""
        # 先注册用户
        client.post("/auth/register", json=sample_user_data)
        
        # 使用错误密码登录
        wrong_login_data = {
            "username": sample_user_data["username"],
            "email": sample_user_data["email"],
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=wrong_login_data)
        assert response.status_code == 401
        assert "用户名、邮箱或密码错误" in response.json()["detail"]
    
    def test_login_wrong_username(self, client: TestClient, sample_user_data):
        """测试错误用户名登录失败"""
        # 先注册用户
        client.post("/auth/register", json=sample_user_data)
        
        # 使用错误用户名登录
        wrong_login_data = {
            "username": "wrongusername",
            "email": sample_user_data["email"],
            "password": sample_user_data["password"]
        }
        response = client.post("/auth/login", json=wrong_login_data)
        assert response.status_code == 401
        assert "用户名、邮箱或密码错误" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client: TestClient):
        """测试不存在的用户登录失败"""
        login_data = {
            "username": "nonexistent",
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        assert "用户名、邮箱或密码错误" in response.json()["detail"] 
