<template>
  <div class="teaching-lecture-container">
    <div class="header-container">
      <button class="back-button" @click="handleBack">←</button>
      <h1 class="title">{{ showEditor ? '讲义编辑器' : '教学讲义' }}</h1>
      <div class="header-right">
        <template v-if="!showEditor">
          <button class="ai-btn" @click="openPrompt()">
            <span class="ai-icon">✨</span>
            AI生成
          </button>
          <button class="save-btn" @click="handleSave" :disabled="isSaving">保存</button>
        </template>
        <button v-else class="back-to-lecture" @click="handleGenerateLectureFromEditor">
          生成讲义
        </button>
      </div>
    </div>

    <!-- 状态消息 -->
    <div v-if="isLoading" class="status-message loading">
      <div class="spinner"></div>
      <span>{{ loadingMessage }}</span>
    </div>

    <div v-if="isGenerating" class="status-message generating">
      <div class="spinner"></div>
      <span>{{ generatingStatus }}</span>
    </div>

    <div v-if="isSaving" class="status-message saving">
      <div class="spinner"></div>
      <span>正在保存...</span>
    </div>

    <div v-if="showSuccessMessage" class="status-message success">
      <span class="success-icon">✓</span>
      <span>{{ successMessage }}</span>
    </div>

    <div v-if="error" class="status-message error">
      <span class="error-icon">❌</span>
      <span>{{ error }}</span>
    </div>

    <!-- 讲义编辑器视图上方的状态区保留加载/保存等必要提示，调试条已注释 -->
    
    <!-- 自动保存状态提示（调试用，已注释） -->
    <!--
    <div v-if="autoSaveEnabled" class="auto-save-indicator">
      <span class="auto-save-icon">🔄</span>
      <span>自动保存已启用 (每5分钟)</span>
    </div>
    -->

    <!-- 内容状态提示（调试用，已注释） -->
    <!--
    <div v-if="contentStatus" class="content-status-indicator" :class="contentStatus.type">
      <span class="status-icon">{{ contentStatus.icon }}</span>
      <span>{{ contentStatus.message }}</span>
    </div>
    -->

    <!-- 讲义编辑器视图 -->
    <div v-if="showEditor" class="lecture-editor-container">
      <LectureEditor 
        :course-id="courseId"
        @back="handleEditorBack"
      />
    </div>
    
    <!-- 原教学讲义视图 -->
    <div v-else class="content-container">
      <!-- 左侧目录 -->
      <div class="catalog-panel" :class="{ 'collapsed': !catalogExpanded }">
        <div class="catalog-header">
          <h3>目录</h3>
          <button class="catalog-toggle-btn" @click="handleCatalogToggle(!catalogExpanded)">
            {{ catalogExpanded ? '收起' : '展开' }}
          </button>
        </div>
        
        <!-- 章节目录 -->
        <div v-if="chapters.length > 0" class="chapters-catalog">
          <div 
            v-for="chapter in chapters" 
            :key="chapter.id"
            class="chapter-catalog-item"
            :class="{ 'active': activeHeading === chapter.title }"
            @click="scrollToChapter(chapter.title)"
          >
            <div class="chapter-catalog-title">{{ chapter.title }}</div>
            <div class="chapter-catalog-status" :class="`status-${chapter.status}`">
              {{ getChapterStatusText(chapter.status) }}
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-else class="catalog-empty">
          <div class="catalog-empty-icon">📚</div>
          <div class="catalog-empty-text">暂无章节</div>
          <button class="create-chapter-btn" @click="showEditor = true">
            创建章节
          </button>
        </div>
      </div>
      
      <!-- 右侧编辑器 -->
      <div class="editor-panel" :class="{ 'expanded': !catalogExpanded }">
        <Markdown 
          ref="markdownRef"
          v-model="markdownContent"
          :height="editorHeight"
          preview-style="tab"
          :editable="true"
          placeholder="开始编写教学讲义..."
          @update:content="updateContent"
        />
        <button v-if="showOptimizeButton" class="ai-optimize-btn" :style="optimizeButtonPosition" @click="openAIOptimize">
          ✨ AI优化
        </button>
      </div>
    </div>
    
    <AiPromptDialog
      :is-visible="showPrompt"
      :reference-content="selectedText"
      :ai-content="aiGeneratedContent"
      :is-generating="isGenerating"
      @close="handleCloseDialog"
      @replace="handleReplace"
      @insert="handleInsert"
      @generate="handleGenerateLecture"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, defineProps, defineEmits, watch } from 'vue';
import Markdown from './markdown.vue';
import Catalog from './Catalog.vue';
import AiPromptDialog from './AiPromptDialog.vue'; // Changed from Prompt to AiPromptDialog
import { getCourseMaterial, saveCourseMaterial, generateCourseMaterial } from '../api/functions';
import LectureEditor from './LectureEditor.vue';
import { getChaptersByCourse } from '../api/lecture';

// 定义API响应类型（已注释，未使用）
// interface ApiResponse<T = any> {
//   data?: T;
//   code?: number;
//   message?: string;
//   [key: string]: any;
// }

// 定义讲义单元的接口
interface LectureUnit {
  unit_number: string;
  unit_title: string;
  lecture_content: string;
  ideological_target?: string;
  time_allocation?: string;
}

// 定义API响应的接口
interface MaterialResponse {
  content?: string;
  units?: LectureUnit[];
  message?: string;
  status?: string;
  [key: string]: any; // Allow additional properties
}

interface MarkdownInstance {
  setMarkdown: (content: string) => void;
  getMarkdown: () => string;
  insertText: (content: string) => void;
  [key: string]: any;
}

interface Props {
  courseId?: number | string;
  courseName?: string;
  showEditor?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  courseId: 0,
  courseName: '',
  showEditor: false
});

const emit = defineEmits(['back', 'save', 'save-draft']);

// Markdown组件引用
const markdownRef = ref<MarkdownInstance | null>(null);

// 状态变量
const isLoading = ref(false);
const loadingMessage = ref('正在加载讲义内容...');
const isGenerating = ref(false);
const generatingStatus = ref('正在生成讲义...');
const isSaving = ref(false);
const showSuccessMessage = ref(false);
const successMessage = ref('');
const error = ref('');

// 自动保存相关
const autoSaveEnabled = ref(true);
const lastAutoSave = ref<Date | null>(null);

// 内容状态
const contentStatus = ref<{
  type: 'success' | 'error' | 'info';
  icon: string;
  message: string;
} | null>(null);

// 控制Prompt组件显示
const showPrompt = ref(false);
const selectedText = ref('');
const showOptimizeButton = ref(false);
const optimizeButtonPosition = ref({ top: '0px', left: '0px' });
const aiGeneratedContent = ref('');

// 目录展开状态
const catalogExpanded = ref(true);

// 是否显示状态（讲义查看模式默认不显示）
const showStatusInMerged = ref(false);
const showStatusBadge = ref(false);

// 处理目录折叠/展开
const handleCatalogToggle = (expanded: boolean) => {
  catalogExpanded.value = expanded;
};

// 处理Prompt提交事件
const handleGenerateLecture = async (requirements: string) => { // Renamed from handlePromptConfirm
  const courseId = typeof props.courseId === 'string' ? parseInt(props.courseId, 10) : props.courseId;
  if (isNaN(courseId) || courseId <= 0) {
    error.value = '课程ID无效，无法生成讲义';
    console.error('无效的课程ID:', props.courseId);
    return;
  }
  
  if (!requirements.trim()) { // Changed from content to requirements
    error.value = '请输入有效的描述内容';
    return;
  }
  
  // showPrompt.value = false; // Dialog closes itself after generate
  isGenerating.value = true;
  generatingStatus.value = '正在生成讲义内容...';
  aiGeneratedContent.value = '正在生成中，请稍候...';
  error.value = '';
  
  try {
    const courseTitle = '课程讲义';
    const response = await generateCourseMaterial(courseId, courseTitle, requirements) as MaterialResponse;
    
    if (response?.content) {
      aiGeneratedContent.value = response.content; // Update aiGeneratedContent
    } else if (response && response.units) {
      let combinedContent = '';
      response.units.forEach((unit: LectureUnit, index: number) => {
        if (index > 0) {
          combinedContent += '\n\n---\n\n';
        }
        combinedContent += unit.lecture_content;
      });
      aiGeneratedContent.value = combinedContent;
    } else {
      throw new Error('API返回的数据格式不正确或内容为空');
    }
    
    generatingStatus.value = '生成完成';
    // No direct update to markdownContent.value here. It's done via handleReplace/handleInsert from AiPromptDialog
  } catch (err) {
    console.error('生成讲义失败', err);
    error.value = '生成讲义失败，请稍后重试';
    aiGeneratedContent.value = '生成失败，请重试。'; // Display error in dialog
  } finally {
    isGenerating.value = false;
  }
};

// 讲义内容相关
const markdownContent = ref('');
const chapters = ref<any[]>([]);
const mergedContent = ref('');

// 是否显示编辑器
const showEditor = ref(props.showEditor);

// 监听props.showEditor变化
watch(() => props.showEditor, (newVal: boolean) => {
  if (newVal !== undefined) {
    showEditor.value = newVal;
  }
});

// 当从编辑器返回时，加载合并的讲义内容
const handleEditorBack = async () => {
  showEditor.value = false;
  await loadMergedLectureContent();
};

// 加载合并的讲义内容
const loadMergedLectureContent = async () => {
  if (!props.courseId) {
    console.warn('loadMergedLectureContent: 无效的课程ID');
    return;
  }
  
  console.log('开始加载合并的讲义内容，courseId:', props.courseId);
  isLoading.value = true;
  loadingMessage.value = '正在加载合并的讲义内容...';
  
  try {
    // 1. 首先尝试从API获取章节数据
    console.log('正在调用getChaptersByCourse API...');
    const courseChapters = await getChaptersByCourse(props.courseId);
    console.log('API返回的章节数据:', courseChapters);
    
    if (courseChapters && Array.isArray(courseChapters) && courseChapters.length > 0) {
      chapters.value = courseChapters;
      console.log('成功加载章节数据，章节数量:', chapters.value.length);
      console.log('章节详情:', chapters.value);
      
      // 2. 合并所有章节内容
      const merged = mergeChaptersContent(courseChapters);
      console.log('合并后的内容长度:', merged.length);
      console.log('合并后的内容预览:', merged.substring(0, 200) + '...');
      
      mergedContent.value = merged;
      markdownContent.value = merged;
      
      // 3. 更新内容状态
      if (merged && merged.trim()) {
        contentStatus.value = {
          type: 'success',
          icon: '📚',
          message: `已加载 ${chapters.value.length} 个章节，总内容 ${merged.length} 字符`
        };
        console.log('内容状态已更新为成功');
      } else {
        contentStatus.value = {
          type: 'info',
          icon: '📄',
          message: '讲义内容为空，请先在编辑器中创建章节'
        };
        console.log('内容状态已更新为信息');
      }
      
      // 4. 保存到本地存储
      localStorage.setItem(`merged_lecture_${props.courseId}`, merged);
      localStorage.setItem(`chapters_data_${props.courseId}`, JSON.stringify(courseChapters));
      console.log('数据已保存到本地存储');
      
    } else {
      console.warn('API返回的章节数据无效或为空:', courseChapters);
      
      // 如果API失败，尝试从本地存储加载
      const localMerged = localStorage.getItem(`merged_lecture_${props.courseId}`);
      const localChapters = localStorage.getItem(`chapters_data_${props.courseId}`);
      
      if (localMerged && localChapters) {
        try {
          chapters.value = JSON.parse(localChapters);
          mergedContent.value = localMerged;
          markdownContent.value = localMerged;
          
          contentStatus.value = {
            type: 'info',
            icon: '💾',
            message: `从本地加载了 ${chapters.value.length} 个章节`
          };
          console.log('从本地存储成功加载数据');
        } catch (e) {
          console.warn('解析本地数据失败:', e);
          createDefaultContent();
        }
      } else {
        console.log('本地存储也没有数据，创建默认内容');
        createDefaultContent();
      }
    }
    
  } catch (err) {
    console.error('加载合并讲义内容失败:', err);
    
    // 尝试从本地存储加载
    const localMerged = localStorage.getItem(`merged_lecture_${props.courseId}`);
    if (localMerged) {
      markdownContent.value = localMerged;
      contentStatus.value = {
        type: 'warning',
        icon: '⚠️',
        message: 'API加载失败，使用本地缓存内容'
      };
      console.log('API失败，使用本地缓存内容');
    } else {
      console.log('本地缓存也没有内容，创建默认内容');
      createDefaultContent();
    }
  } finally {
    isLoading.value = false;
    console.log('loadMergedLectureContent 完成，最终状态:', {
      chaptersCount: chapters.value.length,
      contentLength: markdownContent.value.length,
      contentStatus: contentStatus.value
    });
  }
};

// 合并章节内容
const mergeChaptersContent = (chapters: any[]): string => {
  console.log('开始合并章节内容，输入章节数量:', chapters.length);
  
  if (!chapters || chapters.length === 0) {
    console.warn('没有章节数据，返回空字符串');
    return '';
  }
  
  // 按order_index排序
  const sortedChapters = [...chapters].sort((a, b) => (a.order_index || 0) - (b.order_index || 0));
  console.log('排序后的章节:', sortedChapters.map(c => ({ id: c.id, title: c.title, order_index: c.order_index })));
  
  let merged = '';
  
  sortedChapters.forEach((chapter, index) => {
    console.log(`处理第 ${index + 1} 个章节:`, { id: chapter.id, title: chapter.title, contentLength: chapter.content?.length || 0 });
    
    if (index > 0) {
      merged += '\n\n---\n\n'; // 章节分隔符
    }
    
    // 添加章节标题
    merged += `# ${chapter.title}\n\n`;
    
    // 添加章节内容
    if (chapter.content && chapter.content.trim()) {
      merged += chapter.content;
      console.log(`章节 "${chapter.title}" 内容已添加，长度: ${chapter.content.length}`);
    } else {
      const placeholder = `*${chapter.title} 的内容尚未编写，请点击\"讲义编辑器\"进行编辑。*`;
      merged += placeholder;
      console.log(`章节 "${chapter.title}" 使用占位符内容`);
    }
    
    // 可选：添加章节状态信息（默认关闭）
    if (showStatusInMerged.value) {
      const statusText = getChapterStatusText(chapter.status);
      merged += `\n\n*状态: ${statusText}*`;
      console.log(`章节 "${chapter.title}" 状态: ${statusText}`);
    }
  });
  
  console.log('章节合并完成，最终内容长度:', merged.length);
  console.log('最终内容预览:', merged.substring(0, 300) + '...');
  
  return merged;
};

// 获取章节状态文本
const getChapterStatusText = (status: string): string => {
  const statusMap = {
    'empty': '未开始',
    'draft': '草稿',
    'published': '已发布'
  };
  return statusMap[status as keyof typeof statusMap] || '未知';
};

// 创建默认内容（去除状态行）
const createDefaultContent = () => {
  chapters.value = [{
    id: 1,
    title: '课程介绍',
    content: '',
    status: 'empty',
    order_index: 0
  }];
  
  const defaultContent = `# 课程介绍\n\n*课程介绍的内容尚未编写，请点击\"讲义编辑器\"进行编辑。*\n\n---\n## 课程大纲\n\n*课程大纲的内容尚未编写，请点击\"讲义编辑器\"进行编辑。*\n\n---\n## 教学讲义\n\n*教学讲义的内容尚未编写，请点击\"讲义编辑器\"进行编辑。*`;
  
  mergedContent.value = defaultContent;
  markdownContent.value = defaultContent;
  
  contentStatus.value = {
    type: 'info',
    icon: '📝',
    message: '已创建默认讲义结构，请点击"讲义编辑器"进行编辑'
  };
};

// 处理返回按钮
const handleBack = () => {
  // 统一行为：返回上一层（课程功能选择/上一页）
  emit('back');
};

// 当前活跃的标题锚点
const activeHeading = ref('');

// 编辑器引用
const markdownEditor = ref<any>(null);

// 编辑器高度响应式处理
const editorHeight = ref('calc(100vh - 200px)');

// 更新编辑器高度
const updateEditorHeight = () => {
  const calculatedHeight = Math.min(window.innerHeight - 200, 1800);
  editorHeight.value = `${calculatedHeight}px`;
};

// 监听内容变化
const updateContent = (content: string) => {
  markdownContent.value = content;
};

// 获取课程讲义
const fetchCourseMaterial = async () => {
  if (!props.courseId) {
    console.warn('fetchCourseMaterial: 无效的课程ID');
    return;
  }
  
  isLoading.value = true;
  loadingMessage.value = '正在加载讲义内容...';
  error.value = ''; // 清除之前的错误
  
  try {
    // 确保courseId是数字类型
    const courseId = typeof props.courseId === 'string' ? parseInt(props.courseId, 10) : props.courseId;
    
    if (isNaN(courseId) || courseId <= 0) {
      throw new Error('无效的课程ID');
    }
    
    console.log('开始获取讲义内容，courseId:', courseId);
    
    // 首先尝试从localStorage获取缓存内容
    const cachedContent = localStorage.getItem(`lecture_content_${courseId}`);
    const lastSaved = localStorage.getItem(`lecture_last_saved_${courseId}`);
    
    if (cachedContent && lastSaved) {
      const lastSavedTime = new Date(lastSaved);
      const now = new Date();
      const timeDiff = now.getTime() - lastSavedTime.getTime();
      const hoursDiff = timeDiff / (1000 * 60 * 60);
      
      // 如果缓存时间不超过1小时，使用缓存内容
      if (hoursDiff < 1) {
        console.log('使用缓存的讲义内容');
        markdownContent.value = cachedContent;
        isLoading.value = false;
        return;
      }
    }
    
    // 调用API获取最新内容
    const response = await getCourseMaterial(courseId);
    console.log('获取讲义接口返回:', response);
    
    let content = '';
    if (response?.data && typeof response.data === 'object') {
      content = response.data.content || '';
    } else if (response?.content) {
      content = response.content;
    } else if (typeof response === 'string') {
      content = response;
    }
    
    // 如果API返回空内容，使用缓存内容（如果有的话）
    if (!content && cachedContent) {
      console.log('API返回空内容，使用缓存内容');
      content = cachedContent;
    }
    
    // 设置内容
    markdownContent.value = content;
    console.log('fetch后markdownContent:', markdownContent.value);
    
    // 更新内容状态
    if (content && content.trim()) {
      contentStatus.value = {
        type: 'success',
        icon: '📝',
        message: `已加载讲义内容 (${content.length} 字符)`
      };
    } else {
      contentStatus.value = {
        type: 'info',
        icon: '📄',
        message: '讲义内容为空，可以开始编写'
      };
    }
    
    // 更新编辑器内容
    if (markdownRef.value && markdownRef.value.setMarkdown) {
      markdownRef.value.setMarkdown(markdownContent.value);
      if (markdownRef.value.getMarkdown) {
        console.log('fetch后编辑器内容:', markdownRef.value.getMarkdown());
      }
    }
    
    // 缓存内容到localStorage
    if (content) {
      localStorage.setItem(`lecture_content_${courseId}`, content);
      localStorage.setItem(`lecture_last_saved_${courseId}`, new Date().toISOString());
    }
    
  } catch (err) {
    console.error('获取课程讲义失败', err);
    error.value = err instanceof Error ? err.message : '获取课程讲义失败，请稍后重试';
    
    // 尝试使用缓存内容
    const courseId = typeof props.courseId === 'string' ? parseInt(props.courseId, 10) : props.courseId;
    const cachedContent = localStorage.getItem(`lecture_content_${courseId}`);
    
    if (cachedContent) {
      console.log('API失败，使用缓存内容');
      markdownContent.value = cachedContent;
    }
    
    // 显示错误消息
    setTimeout(() => {
      error.value = '';
    }, 5000);
  } finally {
    isLoading.value = false;
  }
};

// 滚动到指定标题位置
const scrollToHeading = (anchor: string) => {
  activeHeading.value = anchor;
  
  if (markdownEditor.value) {
    const editor = markdownEditor.value.editor();
    if (!editor) return;
    
    // 使用正则表达式搜索对应的标题文本
    const content = markdownContent.value;
    const lines = content.split('\n');
    const anchorText = anchor.replace(/-/g, ' ');
    const targetTextRegex = new RegExp(`^(#+)\\s+${anchorText}`, 'i');
    
    // 查找对应的行号
    let lineNumber = -1;
    for (let i = 0; i < lines.length; i++) {
      if (targetTextRegex.test(lines[i]) || lines[i].toLowerCase().includes(anchorText)) {
        lineNumber = i;
        break;
      }
    }
    
    if (lineNumber >= 0) {
      // 检查编辑器当前模式
      const isWysiwygMode = editor.isWysiwygMode();
      
      if (isWysiwygMode) {
        // 在所见即所得模式下，尝试查找标题元素并滚动
        try {
          const wysiwygEl = editor.getEditorElements().wysiwyg;
          if (wysiwygEl) {
            const headers = wysiwygEl.querySelectorAll('h1, h2, h3, h4, h5, h6');
            for (let i = 0; i < headers.length; i++) {
              if (headers[i].textContent?.toLowerCase().includes(anchorText)) {
                headers[i].scrollIntoView({ behavior: 'smooth' });
                break;
              }
            }
          }
        } catch (e) {
          console.log('无法在所见即所得模式下滚动到标题', e);
        }
      } else {
        // 在Markdown模式下，使用行号滚动
        try {
          // 滚动到对应行
          editor.setScrollTop(lineNumber * 21); // 假设每行约21px高
          
          // 尝试将光标定位到该行以突出显示
          setTimeout(() => {
            try {
              editor.setSelection({
                line: lineNumber,
                ch: 0
              }, {
                line: lineNumber,
                ch: lines[lineNumber].length
              });
            } catch (e) {
              console.log('无法设置选择区域', e);
            }
          }, 100);
        } catch (e) {
          console.log('无法滚动到标题', e);
        }
      }
    }
  }
};

// 滚动到指定章节
const scrollToChapter = (chapterTitle: string) => {
  activeHeading.value = chapterTitle;
  const chapter = chapters.value.find(c => c.title === chapterTitle);
  if (chapter) {
    const anchor = chapter.title.toLowerCase().replace(/\s+/g, '-');
    scrollToHeading(anchor);
  }
};

// 保存讲义
const handleSave = async () => {
  // 允许保存空内容，但需要有效的课程ID
  if (!props.courseId) {
    error.value = '无效的课程ID，无法保存';
    return;
  }
  
  isSaving.value = true;
  error.value = ''; // 清除之前的错误
  
  try {
    // 确保courseId是数字类型
    const courseId = typeof props.courseId === 'string' ? parseInt(props.courseId, 10) : props.courseId;
    if (isNaN(courseId) || courseId <= 0) {
      throw new Error('无效的课程ID');
    }
    
    // 获取当前内容（可能为空）
    const contentToSave = markdownContent.value || '';
    console.log('准备保存讲义内容:', { courseId, contentLength: contentToSave.length, content: contentToSave });
    
    // 调用保存API
    await saveCourseMaterial(courseId, contentToSave);
    console.log('保存讲义内容成功:', contentToSave);
    
    // 显示成功消息
    showSuccessMessage.value = true;
    successMessage.value = '保存成功！';
    setTimeout(() => {
      showSuccessMessage.value = false;
    }, 3000);
    
    // 更新内容状态
    contentStatus.value = {
      type: 'success',
      icon: '💾',
      message: `讲义已保存 (${contentToSave.length} 字符) - ${new Date().toLocaleTimeString()}`
    };
    
    // 保存成功后，更新本地状态
    localStorage.setItem(`lecture_content_${courseId}`, contentToSave);
    localStorage.setItem(`lecture_last_saved_${courseId}`, new Date().toISOString());
    
  } catch (err) {
    console.error('保存讲义失败', err);
    error.value = err instanceof Error ? err.message : '保存讲义失败，请稍后重试';
    
    // 显示错误消息
    setTimeout(() => {
      error.value = '';
    }, 5000);
  } finally {
    isSaving.value = false;
  }
};

const handleReplace = (content: string) => {
  if (markdownRef.value && markdownRef.value.setMarkdown) {
      markdownRef.value.setMarkdown(content);
  }
};

const handleInsert = (content: string) => {
  if (markdownRef.value && markdownRef.value.insertText) {
      markdownRef.value.insertText(content);
  } else {
    markdownContent.value += `\n${content}`;
  }
};

const handleCloseDialog = () => {
  showPrompt.value = false;
  aiGeneratedContent.value = ''; // Reset on close
};

const openPrompt = (text: string = '') => {
  if (isGenerating.value || isLoading.value || isSaving.value) {
    return;
  }
  selectedText.value = text;
  aiGeneratedContent.value = '未生成'; // Reset content when opening
  showPrompt.value = true;
};

const handleSelectionChange = () => {
  const selection = window.getSelection();
  if (selection && selection.rangeCount > 0 && !selection.isCollapsed) {
    const range = selection.getRangeAt(0);
    const editorEl = (markdownRef.value?.$el as HTMLElement)?.querySelector('.editor-wrapper') || (markdownRef.value?.$el as HTMLElement);
    if (!editorEl) return;

    const editorRect = editorEl.getBoundingClientRect();
    const rect = range.getBoundingClientRect();

    if (rect.top >= editorRect.top && rect.bottom <= editorRect.bottom) {
      selectedText.value = selection.toString().trim();
      if (selectedText.value.length > 0) {
        showOptimizeButton.value = true;
        optimizeButtonPosition.value = {
          top: `${rect.bottom - editorRect.top + 10}px`, // Position 10px below selection
          left: `${rect.left - editorRect.left + rect.width / 2}px`,
        };
      }
    } else {
      showOptimizeButton.value = false;
    }
  } else {
    showOptimizeButton.value = false;
  }
};

const openAIOptimize = () => {
  openPrompt(selectedText.value);
};

const handleGenerateLectureFromEditor = async () => {
  console.log('从编辑器切换到讲义查看模式');
  showEditor.value = false; // 切换到讲义查看模式
  await loadMergedLectureContent(); // 加载合并的讲义内容
};

onMounted(() => {
  updateEditorHeight();
  window.addEventListener('resize', updateEditorHeight);
  
  console.log('TeachingLecture组件挂载，courseId:', props.courseId);
  
  // 检查课程ID是否有效
  if (!props.courseId || props.courseId <= 0) {
    console.error('TeachingLecture组件挂载失败：无效的课程ID:', props.courseId);
    error.value = '无效的课程ID，请返回课程管理页面重新选择课程';
    return;
  }
  
  // 如果不是编辑器模式，加载合并的讲义内容
  if (!showEditor.value) {
    console.log('非编辑器模式，加载合并的讲义内容');
    loadMergedLectureContent();
  } else {
    // 如果是编辑器模式，加载讲义内容
    console.log('编辑器模式，加载讲义内容');
    fetchCourseMaterial();
  }
  
  // 添加选择变化监听器
  document.addEventListener('selectionchange', handleSelectionChange);
  
  // 设置定时自动保存（每5分钟）
  const autoSaveInterval = setInterval(() => {
    if (markdownContent.value && markdownContent.value.trim()) {
      console.log('自动保存讲义内容...');
      handleSave();
    }
  }, 5 * 60 * 1000);
  
  // 清理定时器
  const cleanup = () => {
    clearInterval(autoSaveInterval);
    window.removeEventListener('resize', updateEditorHeight);
    document.removeEventListener('selectionchange', handleSelectionChange);
  };
  
  // 在组件卸载时清理
  onUnmounted(cleanup);
});
</script>

<style scoped>
.teaching-lecture-container {
  max-width: 1500px;
  margin: 0 auto;
  padding: 20px;
  overflow: hidden; /* 隐藏滚动条 */
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header-container { /* Renamed from .header */
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  position: relative;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-button {
  background-color: transparent;
  border: none;
  color: #2196f3;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.back-button:hover {
  background-color: rgba(33, 150, 243, 0.1);
}

.title { /* Changed from .section-title */
  font-size: 24px; /* 统一字号 */
  font-weight: bold; /* 统一字重 */
  color: #333;
  text-align: center;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  user-select: none; /* 禁止选中 */
}

/* Removed .section-title existing styles */

.ai-btn {
  display: flex;
  align-items: center;
  background-color: rgba(76, 175, 80, 0.7);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.ai-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.ai-btn:hover:not(:disabled) {
  background-color: rgba(76, 175, 80, 0.85);
}

.ai-icon {
  margin-right: 8px;
}

.save-btn { /* Changed from .btn .btn-primary */
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background-color: rgba(76, 175, 80, 0.7);
  color: white;
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.save-btn:hover:not(:disabled) {
  background-color: rgba(76, 175, 80, 0.85);
}

.status-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.loading {
  background-color: rgba(33, 150, 243, 0.1);
}

.generating {
  background-color: rgba(255, 193, 7, 0.1);
}

.saving {
  background-color: rgba(76, 175, 80, 0.1);
}

.success {
  background-color: rgba(76, 175, 80, 0.2);
  animation: fadeOut 3s forwards;
}

.error {
  background-color: rgba(244, 67, 54, 0.1);
}

.success-icon {
  color: #4caf50;
  font-weight: bold;
  font-size: 18px;
}

.error-icon {
  color: #f44336;
  font-weight: bold;
  font-size: 18px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #2196f3;
  animation: spin 1s ease-in-out infinite;
}

@keyframes fadeOut {
  0% { opacity: 1; }
  70% { opacity: 1; }
  100% { opacity: 0; }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.content-container {
  display: flex;
  gap: 20px;
  height: calc(100vh - 120px);
  overflow: hidden;
}

.catalog-panel {
  width: 300px;
  flex-shrink: 0;
  overflow-y: auto;
  transition: width 0.3s ease;
}

.catalog-panel.collapsed {
  width: 40px;
}

.editor-panel {
  flex-grow: 1;
  overflow-y: auto;
  transition: width 0.3s ease;
  position: relative; /* Added for AI Optimize button positioning */
}

.editor-panel.expanded {
  width: calc(100% - 60px);
}

/* Removed .btn, .btn-primary, .btn-secondary styles as they are replaced by .save-btn */

.ai-optimize-btn {
  position: absolute;
  transform: translateX(-50%);
  padding: 6px 12px;
  background-color: #6366f1;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 10;
  transition: all 0.2s ease;
}

.ai-optimize-btn:hover {
  background-color: #4f46e5;
  transform: translateX(-50%) translateY(-2px);
}

@media (max-width: 768px) {
  .content-container {
    flex-direction: column;
  }
  
  .catalog-panel {
    width: 100%;
    height: auto;
    max-height: 300px;
  }
}

/* 隐藏全局滚动条 */
/* 编辑器容器样式 */
.lecture-editor-container {
  height: calc(100vh - 120px);
  margin: 10px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 编辑讲义按钮 */
.action-buttons {
  margin: 10px 0 15px 20px;
  display: flex;
  justify-content: flex-start;
}

.edit-lecture-btn {
  background-color: #409eff;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.3s;
}

.edit-lecture-btn:hover {
  background-color: #66b1ff;
  transform: translateY(-1px);
}

.edit-lecture-btn i {
  font-size: 16px;
}

/* 返回按钮样式 */
.back-to-lecture {
  background-color: #67c23a;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.back-to-lecture:hover {
  background-color: #85ce61;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .lecture-editor-container {
    height: calc(100vh - 150px);
    margin: 5px;
  }
  
  .action-buttons {
    margin: 5px 10px 10px 10px;
  }
  
  .edit-lecture-btn,
  .back-to-lecture {
    padding: 6px 12px;
    font-size: 14px;
  }
}

body {
  overflow: hidden;
}

::-webkit-scrollbar {
  display: none;
}

* {
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}

/* New styles for auto-save indicator and content status */
.auto-save-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #e0f2f7;
  border-radius: 6px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  font-size: 14px;
  color: #333;
}

.auto-save-icon {
  font-size: 18px;
}

.content-status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  font-size: 14px;
  color: #333;
}

.content-status-indicator.success {
  background-color: #e8f5e9;
  border: 1px solid #a5d6a7;
}

.content-status-indicator.error {
  background-color: #ffebee;
  border: 1px solid #ef9a9a;
}

.content-status-indicator.info {
  background-color: #e3f2fd;
  border: 1px solid #90caf9;
}

.status-icon {
  font-size: 18px;
}

/* 目录样式 */
.catalog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  background-color: rgba(255, 255, 255, 0.9);
}

.catalog-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.catalog-toggle-btn {
  background: transparent;
  border: 1px solid #ddd;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.catalog-toggle-btn:hover {
  background-color: #f5f5f5;
  border-color: #ccc;
}

.chapters-catalog {
  padding: 10px;
}

.chapter-catalog-item {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.chapter-catalog-item:hover {
  background-color: rgba(227, 242, 253, 0.8);
  border-color: rgba(33, 150, 243, 0.2);
  transform: translateY(-1px);
}

.chapter-catalog-item.active {
  background-color: rgba(227, 242, 253, 0.9);
  border-color: rgba(33, 150, 243, 0.4);
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.1);
}

.chapter-catalog-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.chapter-catalog-status {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
}

.status-empty {
  background-color: rgba(244, 67, 54, 0.1);
  color: #f44336;
}

.status-draft {
  background-color: rgba(251, 140, 0, 0.1);
  color: #fb8c00;
}

.status-published {
  background-color: rgba(76, 175, 80, 0.1);
  color: #4caf50;
}

.catalog-empty {
  padding: 40px 20px;
  text-align: center;
  color: #666;
}

.catalog-empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.catalog-empty-text {
  margin-bottom: 20px;
  font-size: 14px;
}

.create-chapter-btn {
  background-color: #2196f3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.create-chapter-btn:hover {
  background-color: #1976d2;
}
</style>
