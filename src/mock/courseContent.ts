interface CourseContent {
  id: number;
  courseId: number;
  introduction: string;
  objectives: string;
  syllabus: string;
  teachingMaterials: string;
  createdAt: string;
  updatedAt: string;
}

// Default content templates
const defaultTemplates = {
  introduction: `## 课程简介

本课程旨在帮助学生掌握[学科领域]的基本概念、原理和方法。通过本课程的学习，学生将能够理解[核心概念]，掌握[关键技能]，并能够将其应用于[应用场景]中。

### 课程特色

- 理论与实践相结合
- 案例分析与项目实践
- 互动式教学
- 实时反馈与评估

### 适用对象

- 本专业本科生/研究生
- 对[学科领域]感兴趣的学者
- 相关领域从业人员`,

  objectives: `## 教学目标

### 知识目标
1. 理解[核心概念]的基本概念和原理
2. 掌握[关键理论]的基本框架和应用方法
3. 了解[相关领域]的最新研究进展

### 能力目标
1. 能够运用[技能/方法]解决实际问题
2. 具备[特定能力]的基本技能
3. 能够独立完成[具体任务/项目]

### 素质目标
1. 培养批判性思维和创新能力
2. 提高团队协作与沟通能力
3. 培养终身学习的意识和能力`,

  syllabus: `## 课程大纲

### 第一部分：基础篇
1. 第1章 [主题1]
   - 1.1 [子主题1]
   - 1.2 [子主题2]
   - 1.3 [子主题3]

2. 第2章 [主题2]
   - 2.1 [子主题1]
   - 2.2 [子主题2]

### 第二部分：进阶篇
3. 第3章 [主题3]
   - 3.1 [子主题1]
   - 3.2 [子主题2]

4. 第4章 [主题4]
   - 4.1 [子主题1]
   - 4.2 [子主题2]

### 第三部分：实践篇
5. 第5章 [主题5]
   - 5.1 [子主题1]
   - 5.2 [子主题2]`,

  teachingMaterials: `## 教学讲义

### 第一讲 [讲座标题]

#### 主要内容
- 要点1
- 要点2
- 要点3

#### 学习目标
- 目标1
- 目标2

#### 参考资料
1. 参考书1
2. 参考书2
3. 学术论文1

### 第二讲 [讲座标题]

#### 主要内容
- 要点1
- 要点2

#### 学习目标
- 目标1
- 目标2

#### 参考资料
1. 参考书1
2. 学术论文2`
};

// Mock data for course content
let courseContents: CourseContent[] = [
  {
    id: 1,
    courseId: 5, // 数据结构与算法
    introduction: defaultTemplates.introduction.replace('[学科领域]', '数据结构与算法')
      .replace('[核心概念]', '数据结构与算法设计')
      .replace('[关键技能]', '算法分析与设计')
      .replace('[应用场景]', '软件开发与系统设计'),
    objectives: defaultTemplates.objectives
      .replace(/\[核心概念\]/g, '数据结构与算法')
      .replace(/\[关键理论\]/g, '算法复杂度分析')
      .replace(/\[相关领域\]/g, '计算机科学')
      .replace(/\[技能\/方法\]/g, '常见数据结构和算法')
      .replace(/\[特定能力\]/g, '算法设计与分析')
      .replace(/\[具体任务\/项目\]/g, '算法问题解决方案'),
    syllabus: defaultTemplates.syllabus
      .replace(/\[主题1\]/g, '算法分析基础')
      .replace(/\[子主题1\]/g, '算法复杂度')
      .replace(/\[子主题2\]/g, '渐进表示法')
      .replace(/\[子主题3\]/g, '递归与分治')
      .replace(/\[主题2\]/g, '基本数据结构')
      .replace(/\[主题3\]/g, '高级数据结构')
      .replace(/\[主题4\]/g, '经典算法设计')
      .replace(/\[主题5\]/g, '算法实践'),
    teachingMaterials: defaultTemplates.teachingMaterials
      .replace(/\[讲座标题\]/g, '算法分析基础')
      .replace(/\[要点1\]/g, '算法复杂度概念')
      .replace(/\[要点2\]/g, '时间与空间复杂度')
      .replace(/\[要点3\]/g, '常见复杂度分析')
      .replace(/\[目标1\]/g, '理解算法复杂度的概念')
      .replace(/\[目标2\]/g, '掌握复杂度分析方法')
      .replace(/\[参考书1\]/g, '《算法导论》')
      .replace(/\[参考书2\]/g, '《数据结构与算法分析》')
      .replace(/\[学术论文1\]/g, 'Recent Advances in Algorithm Design')
      .replace(/\[学术论文2\]/g, 'Efficient Data Structures in Practice'),
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
  // 可以为其他课程添加更多默认内容
];

// Simulate API delay
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const courseContentService = {
  // 获取课程内容
  async getCourseContent(courseId: number): Promise<CourseContent | undefined> {
    await delay(200);
    let content = courseContents.find(c => c.courseId === courseId);
    
    // 如果找不到课程内容，创建默认内容
    if (!content) {
      content = {
        id: Math.max(0, ...courseContents.map(c => c.id)) + 1,
        courseId,
        introduction: defaultTemplates.introduction,
        objectives: defaultTemplates.objectives,
        syllabus: defaultTemplates.syllabus,
        teachingMaterials: defaultTemplates.teachingMaterials,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      courseContents.push(content);
    }
    
    return { ...content };
  },

  // 更新课程内容
  async updateCourseContent(courseId: number, updates: Partial<CourseContent>): Promise<CourseContent> {
    await delay(300);
    const index = courseContents.findIndex(c => c.courseId === courseId);
    
    if (index === -1) {
      // 如果不存在，创建新记录
      const newContent: CourseContent = {
        id: Math.max(0, ...courseContents.map(c => c.id)) + 1,
        courseId,
        introduction: '',
        objectives: '',
        syllabus: '',
        teachingMaterials: '',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        ...updates
      };
      courseContents.push(newContent);
      return { ...newContent };
    }
    
    // 更新现有记录
    const updated = {
      ...courseContents[index],
      ...updates,
      updatedAt: new Date().toISOString()
    };
    courseContents[index] = updated;
    return { ...updated };
  },

  // 获取默认模板
  getDefaultTemplates() {
    return { ...defaultTemplates };
  }
};

export default courseContentService;
