import courseService from '../mock/courseService';

/**
 * 获取教师所有课程
 * @returns 课程列表
 */
export const getTeacherCourses = async () => {
  try {
    const courses = await courseService.getTeacherCourses();
    return courses.filter((course: any) => !course.isDeleted);
  } catch (error) {
    console.error('获取课程列表失败:', error);
    throw error;
  }
};

/**
 * 获取课程详情
 * @param courseId 课程ID
 * @returns 课程详情
 */
export const getCourseDetail = async (courseId: number) => {
  try {
    const courses = await courseService.getTeacherCourses();
    const course = courses.find((c: any) => c.id === courseId);
    if (!course) {
      throw new Error('课程不存在');
    }
    return course;
  } catch (error) {
    console.error('获取课程详情失败:', error);
    throw error;
  }
};

/**
 * 创建新课程
 * @param courseName 课程名称
 * @returns 创建的课程信息
 */
export const createCourse = async (courseName: string) => {
  try {
    if (!courseName || courseName.trim() === '') {
      throw new Error('课程名称不能为空');
    }
    
    const newCourse = await courseService.createCourse(courseName);
    return newCourse;
  } catch (error) {
    console.error('创建课程失败:', error);
    throw error;
  }
};

/**
 * 更新课程名称
 * @param courseId 课程ID
 * @param courseName 新的课程名称
 * @returns 更新后的课程信息
 */
export const updateCourseName = async (courseId: number, courseName: string) => {
  try {
    if (!courseName || courseName.trim() === '') {
      throw new Error('课程名称不能为空');
    }
    
    const updatedCourse = await courseService.updateCourseName(courseId, courseName);
    return updatedCourse;
  } catch (error) {
    console.error('更新课程名称失败:', error);
    throw error;
  }
};

/**
 * 删除课程
 * @param courseId 课程ID
 * @returns 删除结果
 */
export const deleteCourse = async (courseId: number) => {
  try {
    const result = await courseService.deleteCourse(courseId);
    return result;
  } catch (error) {
    console.error('删除课程失败:', error);
    throw error;
  }
};
