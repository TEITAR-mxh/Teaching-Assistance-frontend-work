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
        <button v-else class="back-to-lecture" @click="showEditor = false">
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

    <!-- 讲义编辑器视图 -->
    <div v-if="showEditor" class="lecture-editor-container">
      <LectureEditor 
        :course-id="courseId"
        @back="showEditor = false"
      />
    </div>
    
    <!-- 原教学讲义视图 -->
    <div v-else class="content-container">
      <!-- 左侧目录 -->
      <div class="catalog-panel" :class="{ 'collapsed': !catalogExpanded }">
        <Catalog 
          :content="markdownContent" 
          :activeHeading="activeHeading" 
          @navigate="scrollToHeading"
          @toggle="handleCatalogToggle"
        />
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

// 控制Prompt组件显示
const showPrompt = ref(false);
const selectedText = ref('');
const showOptimizeButton = ref(false);
const optimizeButtonPosition = ref({ top: '0px', left: '0px' });
const aiGeneratedContent = ref('');

// 目录展开状态
const catalogExpanded = ref(true);

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

// 示例讲义内容
const markdownContent = ref('');

// 是否显示编辑器
const showEditor = ref(props.showEditor);

// 监听props.showEditor变化
watch(() => props.showEditor, (newVal: boolean) => {
  if (newVal !== undefined) {
    showEditor.value = newVal;
  }
});

// 处理返回按钮
const handleBack = () => {
  if (showEditor.value) {
    showEditor.value = false;
  } else {
    emit('back');
  }
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
  if (!props.courseId) return;
  
  isLoading.value = true;
  loadingMessage.value = '正在加载讲义内容...';
  
  try {
    // 确保courseId是数字类型
    const courseId = typeof props.courseId === 'string' ? parseInt(props.courseId, 10) : props.courseId;
    const response = await getCourseMaterial(courseId);
    console.log('获取讲义接口返回:', response);
    let content = '';
    if (response?.data && typeof response.data === 'object') {
      content = response.data.content || '';
    } else if (response?.content) {
      content = response.content;
    }
    if (!content) {
      content = '';
      // content = '课程讲义\n\n这是课程讲义的默认内容。...';
    }
    markdownContent.value = content;
    console.log('fetch后markdownContent:', markdownContent.value);
    if (markdownEditor.value && markdownEditor.value.setMarkdown) {
      markdownEditor.value.setMarkdown(markdownContent.value);
      if (markdownEditor.value.getMarkdown) {
        console.log('fetch后编辑器内容:', markdownEditor.value.getMarkdown());
      }
    }
  } catch (err) {
    console.error('获取课程讲义失败', err);
    error.value = '获取课程讲义失败，请稍后重试';
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

// 保存讲义
const handleSave = async () => {
  if (!markdownContent.value.trim() || !props.courseId) return;
  
  isSaving.value = true;
  
  try {
    // 确保courseId是数字类型
    const courseId = typeof props.courseId === 'string' ? parseInt(props.courseId, 10) : props.courseId;
    if (isNaN(courseId) || courseId <= 0) {
      throw new Error('无效的课程ID');
    }
    
    // 调用保存API
    await saveCourseMaterial(courseId, markdownContent.value);
    console.log('保存讲义内容成功:', markdownContent.value);
    showSuccessMessage.value = true;
    successMessage.value = '保存成功！';
    setTimeout(() => {
      showSuccessMessage.value = false;
    }, 3000);
  } catch (err) {
    console.error('保存讲义失败', err);
    error.value = '保存讲义失败，请稍后重试';
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

onMounted(() => {
  updateEditorHeight();
  window.addEventListener('resize', updateEditorHeight);
  console.log('TeachingLecture组件挂载，courseId:', props.courseId);
  fetchCourseMaterial(); // 加载讲义内容
  document.addEventListener('selectionchange', handleSelectionChange); // Add selection change listener
});

onUnmounted(() => {
  window.removeEventListener('resize', updateEditorHeight);
  document.removeEventListener('selectionchange', handleSelectionChange); // Remove selection change listener
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
</style>
