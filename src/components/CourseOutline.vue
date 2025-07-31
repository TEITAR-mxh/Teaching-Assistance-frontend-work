<template>
  <div class="course-description-container">
    <div class="header-container">
      <button class="back-button" @click="$emit('back')">←</button>
      <h1 class="title">课程大纲</h1>
      <div class="header-right">
        <button class="ai-btn" @click="openPrompt()">
          <span class="ai-icon">✨</span>
          AI生成
        </button>
        <button class="save-btn" @click="saveSyllabus" :disabled="isSaving">保存</button>
      </div>
    </div>

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

    <div class="section editor-wrapper">
      <Markdown 
        ref="markdownRef"
        v-model="courseOutline"
        :initial-value="courseOutline" 
        :height="editorHeight" 
        preview-style="tab"
        :editable="true"
        placeholder="开始编写课程大纲..."
      />
      <button v-if="showOptimizeButton" class="ai-optimize-btn" :style="optimizeButtonPosition" @click="openAIOptimize">
        ✨ AI优化
      </button>
    </div>

    <AiPromptDialog
      :is-visible="showPrompt"
      :reference-content="selectedText"
      :ai-content="aiGeneratedContent"
      :is-generating="isGenerating"
      @close="handleCloseDialog"
      @replace="handleReplace"
      @insert="handleInsert"
      @generate="handleGenerateSyllabus"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, defineEmits, onMounted, onUnmounted, defineProps } from 'vue';
import Markdown from './markdown.vue';
import AiPromptDialog from './AiPromptDialog.vue';
import { getCourseSyllabus, saveCourseSyllabus, generateCourseSyllabus } from '../api/functions';

// 定义Markdown组件实例的类型
interface MarkdownInstance {
  setMarkdown: (content: string) => void;
  getMarkdown: () => string;
  [key: string]: any;
}

const props = defineProps({
  courseId: {
    type: Number,
    required: false,
    default: undefined
  }
});

defineEmits(['back']);

// Markdown组件引用
const markdownRef = ref<MarkdownInstance | null>(null);

// 控制Prompt组件显示
const showPrompt = ref(false);
const selectedText = ref('');
const showOptimizeButton = ref(false);
const optimizeButtonPosition = ref({ top: '0px', left: '0px' });
const aiGeneratedContent = ref('');

// 课程大纲内容
const courseOutline = ref('');
const error = ref('');

// 状态变量
const isLoading = ref(false);
const loadingMessage = ref('正在加载课程大纲...');
const isGenerating = ref(false);
const generatingStatus = ref('正在生成中...');
const isSaving = ref(false);
const showSuccessMessage = ref(false);
const successMessage = ref('');

// 编辑器高度响应式处理
const editorHeight = ref('calc(100vh - 200px)');

// 获取课程大纲
const fetchCourseSyllabus = async () => {
  if (!props.courseId || isNaN(props.courseId)) {
    error.value = '课程ID无效，无法获取大纲';
    return;
  }
  isLoading.value = true;
  loadingMessage.value = '正在加载课程大纲...';
  error.value = '';
  try {
    const data = await getCourseSyllabus(props.courseId);
    courseOutline.value = data.content || '';
    if (markdownRef.value && markdownRef.value.setMarkdown) {
      markdownRef.value.setMarkdown(courseOutline.value);
    }
  } catch (err) {
    console.error('获取课程教学大纲失败', err);
    error.value = '获取课程大纲失败，请稍后重试';
  } finally {
    isLoading.value = false;
  }
};

// 保存课程大纲
const saveSyllabus = async () => {
  if (!props.courseId || isNaN(props.courseId)) {
    alert('课程ID无效，无法保存大纲');
    console.error('无效的课程ID:', props.courseId);
    return;
  }
  isSaving.value = true;
  try {
    if (markdownRef.value && markdownRef.value.getMarkdown) {
      courseOutline.value = markdownRef.value.getMarkdown();
    }
    console.log('准备保存大纲内容:', courseOutline.value);
    await saveCourseSyllabus(props.courseId, {
      content: courseOutline.value
    });
    console.log('保存大纲内容成功:', courseOutline.value);
    showSuccessMessage.value = true;
    successMessage.value = '保存成功！';
    setTimeout(() => {
      showSuccessMessage.value = false;
    }, 3000);
  } catch (err) {
    console.error('保存课程大纲失败', err);
    alert('保存失败，请稍后重试');
  } finally {
    isSaving.value = false;
  }
};

// 更新编辑器高度
const updateEditorHeight = () => {
  const calculatedHeight = Math.min(window.innerHeight - 200, 1800);
  editorHeight.value = `${calculatedHeight}px`;
};

// 处理Prompt提交事件
const handleReplace = (content: string) => {
  // Placeholder for replace logic. This will be implemented fully later.
  if (markdownRef.value && markdownRef.value.setMarkdown) {
      markdownRef.value.setMarkdown(content);
  }
};

const handleInsert = (content: string) => {
  // Placeholder for insert logic.
  if (markdownRef.value && markdownRef.value.insertText) {
      markdownRef.value.insertText(content);
  } else {
    courseOutline.value += `\n${content}`;
  }
};

const handleCloseDialog = () => {
  showPrompt.value = false;
  aiGeneratedContent.value = ''; // Reset on close
};

const handleGenerateSyllabus = async (requirements: string) => {
  if (!props.courseId || isNaN(props.courseId)) {
    alert('课程ID无效，无法生成大纲');
    return;
  }

  isGenerating.value = true;
  generatingStatus.value = '正在生成中...';
  aiGeneratedContent.value = '正在生成中，请稍候...';
  error.value = '';

  try {
    const response = await generateCourseSyllabus(props.courseId, requirements);
    if (response && response.data && typeof response.data.content === 'string') {
      aiGeneratedContent.value = response.data.content;
    } else {
      throw new Error('API返回的数据格式不正确或内容为空');
    }
  } catch (err) {
    console.error('生成课程教学大纲失败', err);
    error.value = '生成课程大纲失败，请检查输入或稍后重试';
    aiGeneratedContent.value = '生成失败，请重试。';
  } finally {
    isGenerating.value = false;
    generatingStatus.value = '生成完成';
  }
};

// 打开Prompt对话框
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
    const rect = range.getBoundingClientRect();
    const editorEl = (markdownRef.value?.$el as HTMLElement)?.querySelector('.editor-wrapper') || (markdownRef.value?.$el as HTMLElement);
    if (!editorEl) return;

    const editorRect = editorEl.getBoundingClientRect();

    // Check if the selection is inside the editor
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
  fetchCourseSyllabus();
  document.addEventListener('selectionchange', handleSelectionChange);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateEditorHeight);
  document.removeEventListener('selectionchange', handleSelectionChange);
});
</script>

<style scoped>
.course-description-container {
  max-width: 1500px;
  margin: 0 auto;
  padding: 20px;
  overflow: hidden; /* 隐藏滚动条 */
  height: 100%;
  display: flex;
  flex-direction: column;
}

.header-container {
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

.title {
  font-size: 24px; /* 统一字号 */
  font-weight: bold; /* 统一字重 */
  color: #333;
  text-align: center;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  user-select: none; /* 禁止选中 */
}

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

.save-btn {
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

.loading {
  text-align: center;
  padding: 20px;
  font-size: 16px;
  color: #666;
}

.error {
  text-align: center;
  padding: 20px;
  font-size: 16px;
  color: #f44336;
}

.error {
  background-color: rgba(244, 67, 54, 0.1);
}

.error-icon {
  color: #f44336;
  font-weight: bold;
  font-size: 18px;
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

.success-icon {
  color: #4caf50;
  font-weight: bold;
  font-size: 18px;
}

@keyframes fadeOut {
  0% { opacity: 1; }
  70% { opacity: 1; }
  100% { opacity: 0; }
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #2196f3;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.editor-wrapper {
  position: relative;
}

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
</style>

<style>
/* 隐藏全局滚动条 */
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
