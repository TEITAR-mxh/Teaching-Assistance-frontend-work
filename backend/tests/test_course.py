import pytest
from fastapi.testclient import TestClient

class TestCourse:
    """课程功能测试类"""
    
    @pytest.fixture
    def sample_course_data(self):
        """示例课程数据"""
        return {
            "title": "测试课程",
            "description": "这是一个测试课程",
            "teacher_id": 1,
            "category": "计算机科学",
            "level": "初级"
        }
    
    def test_create_course_success(self, client: TestClient, sample_course_data, auth_headers):
        """测试创建课程成功"""
        response = client.post("/courses/", json=sample_course_data, headers=auth_headers)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == sample_course_data["title"]
        assert data["description"] == sample_course_data["description"]
    
    def test_create_course_unauthorized(self, client: TestClient, sample_course_data):
        """测试未授权创建课程失败"""
        response = client.post("/courses/", json=sample_course_data)
        assert response.status_code == 401
    
    def test_get_courses_list(self, client: TestClient, auth_headers):
        """测试获取课程列表"""
        response = client.get("/courses/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_course_by_id(self, client: TestClient, sample_course_data, auth_headers):
        """测试根据ID获取课程"""
        # 先创建课程
        create_response = client.post("/courses/", json=sample_course_data, headers=auth_headers)
        course_id = create_response.json()["id"]
        
        # 获取课程
        response = client.get(f"/courses/{course_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == course_id
        assert data["title"] == sample_course_data["title"]
    
    def test_get_course_not_found(self, client: TestClient, auth_headers):
        """测试获取不存在的课程"""
        response = client.get("/courses/999", headers=auth_headers)
        assert response.status_code == 404
    
    def test_update_course_success(self, client: TestClient, sample_course_data, auth_headers):
        """测试更新课程成功"""
        # 先创建课程
        create_response = client.post("/courses/", json=sample_course_data, headers=auth_headers)
        course_id = create_response.json()["id"]
        
        # 更新课程
        update_data = {
            "title": "更新后的课程标题",
            "description": "更新后的课程描述"
        }
        response = client.put(f"/courses/{course_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
    
    def test_delete_course_success(self, client: TestClient, sample_course_data, auth_headers):
        """测试删除课程成功"""
        # 先创建课程
        create_response = client.post("/courses/", json=sample_course_data, headers=auth_headers)
        course_id = create_response.json()["id"]
        
        # 删除课程
        response = client.delete(f"/courses/{course_id}", headers=auth_headers)
        assert response.status_code == 204
        
        # 验证课程已被删除
        get_response = client.get(f"/courses/{course_id}", headers=auth_headers)
        assert get_response.status_code == 404 
