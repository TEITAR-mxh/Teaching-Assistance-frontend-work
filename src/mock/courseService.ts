interface Course {
  id: number;
  teacherId: number;
  name: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  isDeleted: number;
  createdAt: string;
  updatedAt: string;
  rejectReason?: string;
}

let courses: Course[] = [
  {
    id: 5,
    teacherId: 1,
    name: '数据结构与算法',
    status: 'APPROVED',
    isDeleted: 0,
    createdAt: '2025-07-01T09:00:00.000Z',
    updatedAt: '2025-07-05T14:30:00.000Z'
  },
  {
    id: 4,
    teacherId: 1,
    name: '数据库系统原理',
    status: 'APPROVED',
    isDeleted: 0,
    createdAt: '2025-06-25T10:15:00.000Z',
    updatedAt: '2025-06-28T11:45:00.000Z'
  },
  {
    id: 3,
    teacherId: 1,
    name: '计算机网络',
    status: 'APPROVED',
    isDeleted: 0,
    createdAt: '2025-06-15T13:20:00.000Z',
    updatedAt: '2025-06-18T16:10:00.000Z'
  },
  {
    id: 2,
    teacherId: 1,
    name: '软件工程',
    status: 'PENDING',
    isDeleted: 0,
    createdAt: '2025-07-20T08:45:00.000Z',
    updatedAt: '2025-07-20T08:45:00.000Z'
  },
  {
    id: 1,
    teacherId: 1,
    name: '人工智能基础',
    status: 'REJECTED',
    isDeleted: 0,
    createdAt: '2025-07-10T14:00:00.000Z',
    updatedAt: '2025-07-12T10:20:00.000Z',
    rejectReason: '课程大纲需要补充更多实践内容'
  }
];

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const courseService = {
  // 获取教师课程列表
  async getTeacherCourses() {
    await delay(300); // Simulate network delay
    return [...courses];
  },

  // 创建新课程
  async createCourse(name: string): Promise<Course> {
    const now = new Date().toISOString();
    const newCourse: Course = {
      id: Math.max(0, ...courses.map(c => c.id)) + 1,
      teacherId: 1, // Default teacher ID
      name,
      status: 'PENDING', // 新课程默认为待审核状态
      isDeleted: 0,
      createdAt: now,
      updatedAt: now
    };
    courses.unshift(newCourse);
    return newCourse;
  },

  // 更新课程名称
  async updateCourseName(courseId: number, newName: string) {
    await delay(300);
    const course = courses.find(c => c.id === courseId);
    if (!course) throw new Error('Course not found');
    
    course.name = newName;
    return { ...course };
  },

  // 删除课程
  async deleteCourse(courseId: number) {
    await delay(300);
    const index = courses.findIndex(c => c.id === courseId);
    if (index === -1) throw new Error('Course not found');
    
    courses.splice(index, 1);
    return { success: true };
  },

  // 批量删除课程
  async deleteCourses(courseIds: number[]) {
    await delay(300);
    const initialLength = courses.length;
    courses = courses.filter(course => !courseIds.includes(course.id));
    return { success: courses.length < initialLength };
  }
};

export default courseService;
