import pytest
from fastapi.testclient import TestClient

class TestAdmin:
    """管理员功能测试类"""
    
    @pytest.fixture
    def admin_headers(self, auth_headers):
        """管理员认证头信息"""
        # 这里应该使用管理员token，实际使用时需要先登录管理员账户
        return {"Authorization": "Bearer admin_token"}
    
    @pytest.fixture
    def sample_user_data(self):
        """示例用户数据"""
        return {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "role": "student"
        }
    
    def test_get_all_users(self, client: TestClient, admin_headers):
        """测试管理员获取所有用户列表"""
        response = client.get("/admin/users", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_all_users_unauthorized(self, client: TestClient):
        """测试非管理员获取用户列表失败"""
        response = client.get("/admin/users")
        assert response.status_code == 401
    
    def test_create_user_by_admin(self, client: TestClient, admin_headers, sample_user_data):
        """测试管理员创建用户"""
        response = client.post("/admin/users", json=sample_user_data, headers=admin_headers)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert data["role"] == sample_user_data["role"]
    
    def test_update_user_by_admin(self, client: TestClient, admin_headers, sample_user_data):
        """测试管理员更新用户信息"""
        # 先创建用户
        create_response = client.post("/admin/users", json=sample_user_data, headers=admin_headers)
        user_id = create_response.json()["id"]
        
        # 更新用户信息
        update_data = {
            "username": "updateduser",
            "role": "teacher"
        }
        response = client.put(f"/admin/users/{user_id}", json=update_data, headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == update_data["username"]
        assert data["role"] == update_data["role"]
    
    def test_delete_user_by_admin(self, client: TestClient, admin_headers, sample_user_data):
        """测试管理员删除用户"""
        # 先创建用户
        create_response = client.post("/admin/users", json=sample_user_data, headers=admin_headers)
        user_id = create_response.json()["id"]
        
        # 删除用户
        response = client.delete(f"/admin/users/{user_id}", headers=admin_headers)
        assert response.status_code == 204
        
        # 验证用户已被删除
        get_response = client.get(f"/admin/users/{user_id}", headers=admin_headers)
        assert get_response.status_code == 404
    
    def test_get_user_statistics(self, client: TestClient, admin_headers):
        """测试获取用户统计信息"""
        response = client.get("/admin/statistics", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "total_courses" in data
        assert isinstance(data["total_users"], int)
        assert isinstance(data["total_courses"], int)
    
    def test_admin_access_control(self, client: TestClient, auth_headers):
        """测试管理员权限控制"""
        # 使用普通用户token访问管理员接口
        response = client.get("/admin/users", headers=auth_headers)
        assert response.status_code == 403  # 应该返回权限不足错误 
