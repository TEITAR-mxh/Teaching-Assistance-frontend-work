<template>
  <div class="lecture-editor">
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

    <div class="lecture-container">
      <!-- Sidebar - Chapter List -->
      <div class="lecture-sidebar">
        <div class="sidebar-header">
          <h3>课程章节</h3>
          <button class="add-chapter-btn" @click="showAddChapterDialog">
            <el-icon><Plus /></el-icon> 添加章节
          </button>
        </div>
        
        <div class="chapter-list">
          <draggable 
            v-model="chapters" 
            item-key="id" 
            @end="onChapterOrderChange"
            handle=".drag-handle"
          >
            <template #item="{ element: chapter, index }">
              <div 
                class="chapter-item" 
                :class="{
                  'active': currentChapter?.id === chapter.id,
                  'status-empty': chapter.status === 'empty',
                  'status-draft': chapter.status === 'draft',
                  'status-published': chapter.status === 'published'
                }"
                @click="selectChapter(chapter)"
              >
                <div class="chapter-item-content">
                  <el-icon class="drag-handle"><Rank /></el-icon>
                  <span class="chapter-title">{{ chapter.title }}</span>
                  <div class="chapter-actions">
                    <el-tooltip content="删除" placement="top">
                      <el-button 
                        type="danger" 
                        size="small" 
                        :icon="Delete" 
                        circle 
                        @click.stop="confirmDeleteChapter(chapter)"
                      />
                    </el-tooltip>
                  </div>
                </div>
                <div class="chapter-progress" :class="'status-' + chapter.status">
                  {{ getStatusText(chapter.status) }}
                </div>
              </div>
            </template>
          </draggable>
        </div>
      </div>

      <!-- Main Content -->
      <div class="lecture-content">
        <div v-if="currentChapter" class="chapter-editor">
          <div class="editor-header">
            <div class="header-left">
              <el-input
                v-model="currentChapter.title"
                placeholder="章节标题"
                @change="updateChapterTitle"
                class="chapter-title-input"
              />
            </div>
            <div class="header-right">
              <button class="save-btn" @click="saveContent" :disabled="isSaving">
                <el-icon><Document /></el-icon>
                保存
              </button>
              <button class="ai-btn" @click="generateChapterContent" style="position: static; transform: none;">
                <span class="ai-icon">✨</span>
                AI生成
              </button>
              <button 
                class="publish-btn" 
                @click="publishChapter"
                :disabled="publishing"
              >
                <el-icon><Upload /></el-icon> 发布章节
              </button>
            </div>
          </div>
          
          <!-- 未保存更改提示 -->
          <div v-if="hasUnsavedChanges" class="unsaved-changes-warning">
            <el-icon><Warning /></el-icon>
            <span>有未保存的更改，请点击保存按钮保存内容</span>
          </div>

          <div class="editor-container">
            <div v-if="editorMode === 'edit'" class="markdown-editor">
              <MarkdownEditor
                v-model="currentChapter.content"
                @update:modelValue="handleContentChange"
              />
            </div>
            <div v-else class="markdown-preview">
              <div v-html="renderedContent"></div>
            </div>
          </div>
        </div>
        
        <div v-else class="no-chapter-selected">
          <el-empty description="请选择或创建一个章节" />
        </div>
      </div>
    </div>

    <!-- Add Chapter Dialog -->
    <el-dialog
      v-model="showDialog"
      title="添加新章节"
      width="30%"
      :close-on-click-modal="false"
    >
      <el-form :model="newChapter" label-width="80px">
        <el-form-item label="章节标题">
          <el-input v-model="newChapter.title" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDialog = false">取消</el-button>
          <el-button type="primary" @click="addChapter">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Plus, Rank, Delete, Upload, Document, Warning } from '@element-plus/icons-vue';
import draggable from 'vuedraggable';
import MarkdownEditor from './markdown.vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { 
  createChapter, 
  getChaptersByCourse, 
  updateChapter, 
  deleteChapter as deleteChapterAPI 
} from '../api/lecture';

interface Chapter {
  id: number;
  title: string;
  content?: string;
  status: 'empty' | 'draft' | 'published';
}

// Props 和 Emits
const props = defineProps<{
  courseId?: number;
  courseName?: string;
}>();

const emit = defineEmits(['back']);

// 状态变量
const isLoading = ref(false);
const loadingMessage = ref('');
const isGenerating = ref(false);
const generatingStatus = ref('');
const isSaving = ref(false);
const showSuccessMessage = ref(false);
const successMessage = ref('');
const error = ref('');
const publishing = ref(false);
const showDialog = ref(false);
const editorMode = ref('edit');
const chapters = ref<Chapter[]>([]);
const currentChapter = ref<Chapter | null>(null);
const hasUnsavedChanges = ref(false);
const originalContent = ref('');

// 新章节的默认值
const newChapter = ref({
  title: '',
});

// 计算属性
const renderedContent = computed(() => {
  if (!currentChapter.value?.content) return '';
  const html = marked.parse(currentChapter.value.content);
  return DOMPurify.sanitize(html as string);
});

const saveContent = async () => {
  if (!currentChapter.value) {
    ElMessage.warning('请先选择一个章节');
    return;
  }
  
  isSaving.value = true;
  error.value = ''; // 清除之前的错误
  
  try {
    console.log('开始保存章节内容:', {
      chapterId: currentChapter.value.id,
      title: currentChapter.value.title,
      contentLength: currentChapter.value.content?.length || 0
    });
    
    const updateData = {
      content: currentChapter.value.content || '',
      status: currentChapter.value.status === 'empty' ? 'draft' : currentChapter.value.status
    };
    
    await updateChapter(currentChapter.value.id, updateData);
    
    // 更新原始内容和状态
    originalContent.value = currentChapter.value.content || '';
    hasUnsavedChanges.value = false;
    
    // 如果章节状态为空，则更改为草稿状态
    if (currentChapter.value.status === 'empty') {
      currentChapter.value.status = 'draft';
    }
    
    // 显示成功消息
    showSuccessMessage.value = true;
    successMessage.value = '章节保存成功！';
    setTimeout(() => {
      showSuccessMessage.value = false;
    }, 3000);
    
    // 保存到本地存储作为备份
    const courseId = props.courseId;
    if (courseId) {
      localStorage.setItem(`chapter_${currentChapter.value.id}_content`, currentChapter.value.content || '');
      localStorage.setItem(`chapter_${currentChapter.value.id}_last_saved`, new Date().toISOString());
    }
    
    console.log('章节保存成功');
    
  } catch (err) {
    console.error('保存章节失败:', err);
    error.value = err instanceof Error ? err.message : '保存失败，请稍后重试';
    
    // 显示错误消息
    setTimeout(() => {
      error.value = '';
    }, 5000);
  } finally {
    isSaving.value = false;
  }
};

const generateContent = async () => {
  // 如果有未保存的更改，提示用户
  if (hasUnsavedChanges.value) {
    try {
      await ElMessageBox.confirm(
        '当前有未保存的更改，是否保存？',
        '提示',
        {
          confirmButtonText: '保存',
          cancelButtonText: '不保存',
          type: 'warning',
          distinguishCancelAndClose: true,
          showClose: true,
          closeOnClickModal: false
        }
      );
      // 用户选择保存
      await saveContent();
    } catch (action) {
      if (action !== 'cancel') {
        // 如果不是选择"不保存"，则取消跳转
        return;
      }
      // 用户选择"不保存"，继续跳转
    }
  }
  
  // 通知父组件显示TeachingLecture组件
  emit('back', true);
};

// 加载章节数据
const loadChapters = async () => {
  if (!props.courseId) {
    console.warn('loadChapters: 无效的课程ID');
    return;
  }
  
  try {
    console.log('开始加载课程章节，courseId:', props.courseId);
    const courseChapters = await getChaptersByCourse(props.courseId);
    
    if (courseChapters && Array.isArray(courseChapters)) {
      chapters.value = courseChapters.map(chapter => ({
        id: chapter.id,
        title: chapter.title,
        content: chapter.content || '',
        status: chapter.status || 'empty',
        order_index: chapter.order_index || 0
      }));
      
      console.log('成功加载章节数据:', chapters.value);
      
      // 如果有章节，选择第一个
      if (chapters.value.length > 0) {
        selectChapter(chapters.value[0]);
      }
    } else {
      console.warn('API返回的章节数据格式不正确:', courseChapters);
      chapters.value = [];
    }
  } catch (err) {
    console.error('加载章节数据失败:', err);
    
    // 尝试从本地存储加载备份数据
    try {
      const backupData = localStorage.getItem(`chapters_backup_${props.courseId}`);
      if (backupData) {
        const parsedData = JSON.parse(backupData);
        if (Array.isArray(parsedData)) {
          chapters.value = parsedData;
          console.log('从本地备份加载章节数据:', chapters.value);
          
          if (chapters.value.length > 0) {
            selectChapter(chapters.value[0]);
          }
          return;
        }
      }
    } catch (backupErr) {
      console.warn('加载本地备份失败:', backupErr);
    }
    
    // 如果都失败了，创建默认章节
    chapters.value = [{
      id: 1,
      title: '课程介绍',
      content: '',
      status: 'empty',
      order_index: 0
    }];
    
    selectChapter(chapters.value[0]);
    console.log('创建默认章节作为备选');
    
    // 显示错误信息
    error.value = '加载章节失败，已创建默认章节';
    setTimeout(() => {
      error.value = '';
    }, 5000);
  }
};

// 选择章节
const selectChapter = (chapter: Chapter) => {
  currentChapter.value = chapter;
  originalContent.value = chapter.content || '';
  hasUnsavedChanges.value = false;
  console.log('选择章节:', chapter);
};

// 添加新章节
const addChapter = async () => {
  if (!newChapter.value.title.trim()) {
    ElMessage.warning('请输入章节标题');
    return;
  }
  
  if (!props.courseId) {
    ElMessage.error('课程ID无效');
    return;
  }
  
  try {
    const chapterData = {
      title: newChapter.value.title,
      content: '',
      status: 'empty' as const,
      course_id: props.courseId
    };
    
    const newChapterResponse = await createChapter(chapterData);
    
    if (newChapterResponse) {
      const createdChapter: Chapter = {
        id: newChapterResponse.id,
        title: newChapterResponse.title,
        content: newChapterResponse.content || '',
        status: newChapterResponse.status || 'empty'
      };
      
      chapters.value.push(createdChapter);
      selectChapter(createdChapter);
      showDialog.value = false;
      newChapter.value.title = '';
      
      ElMessage.success('章节创建成功');
    }
  } catch (err) {
    console.error('创建章节失败:', err);
    ElMessage.error('创建章节失败');
  }
};

// 显示添加章节对话框
const showAddChapterDialog = () => {
  showDialog.value = true;
  newChapter.value.title = '';
};

// 更新章节标题
const updateChapterTitle = async (newTitle: string) => {
  if (!currentChapter.value || !newTitle.trim()) return;
  
  try {
    await updateChapter(currentChapter.value.id, { title: newTitle });
    currentChapter.value.title = newTitle;
    ElMessage.success('章节标题更新成功');
  } catch (err) {
    console.error('更新章节标题失败:', err);
    ElMessage.error('更新章节标题失败');
  }
};

// 删除章节
const deleteChapter = async (chapter: Chapter) => {
  try {
    await deleteChapterAPI(chapter.id);
    const index = chapters.value.findIndex(c => c.id === chapter.id);
    if (index > -1) {
      chapters.value.splice(index, 1);
    }
    
    if (currentChapter.value?.id === chapter.id) {
      currentChapter.value = chapters.value.length > 0 ? chapters.value[0] : null;
    }
    
    ElMessage.success('章节删除成功');
  } catch (err) {
    console.error('删除章节失败:', err);
    ElMessage.error('删除章节失败');
  }
};

// 确认删除章节
const confirmDeleteChapter = async (chapter: Chapter) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除章节"${chapter.title}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    );
    await deleteChapter(chapter);
  } catch (action) {
    if (action !== 'cancel') {
      console.log('删除操作被取消');
    }
  }
};

// 章节顺序变化
const onChapterOrderChange = async () => {
  // 这里可以添加保存章节顺序的逻辑
  console.log('章节顺序已更新:', chapters.value);
};

// 生成章节内容
const generateChapterContent = async () => {
  if (!currentChapter.value) {
    ElMessage.warning('请先选择一个章节');
    return;
  }
  
  // 这里可以添加AI生成内容的逻辑
  ElMessage.info('AI生成功能开发中...');
};

// 监听内容变化
const handleContentChange = (newContent: string) => {
  if (currentChapter.value) {
    currentChapter.value.content = newContent;
    
    // 检查是否有未保存的更改
    const hasChanges = newContent !== originalContent.value;
    hasUnsavedChanges.value = hasChanges;
    
    if (hasChanges) {
      console.log('检测到内容变化，标记为未保存状态');
    }
  }
};

// 监听章节变化，重置未保存状态
watch(currentChapter, (newChapter) => {
  if (newChapter) {
    originalContent.value = newChapter.content || '';
    hasUnsavedChanges.value = false;
  }
});

// 发布章节
const publishChapter = async () => {
  if (!currentChapter.value) {
    ElMessage.warning('请先选择一个章节');
    return;
  }
  
  publishing.value = true;
  
  try {
    await updateChapter(currentChapter.value.id, { status: 'published' });
    currentChapter.value.status = 'published';
    ElMessage.success('章节发布成功');
  } catch (err) {
    console.error('发布章节失败:', err);
    ElMessage.error('发布章节失败');
  } finally {
    publishing.value = false;
  }
};

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap = {
    'empty': '未开始',
    'draft': '草稿',
    'published': '已发布'
  };
  return statusMap[status as keyof typeof statusMap] || '未知';
};

// 生命周期钩子
onMounted(async () => {
  isLoading.value = true;
  loadingMessage.value = '正在加载章节数据...';
  
  try {
    if (props.courseId) {
      await loadChapters();
    }
  } catch (err) {
    console.error('加载章节失败:', err);
    error.value = '加载章节失败';
  } finally {
    isLoading.value = false;
  }
  
  // 设置自动保存（每3分钟）
  const autoSaveInterval = setInterval(() => {
    if (hasUnsavedChanges.value && currentChapter.value) {
      console.log('自动保存章节内容...');
      saveContent();
    }
  }, 3 * 60 * 1000);
  
  // 清理定时器
  onUnmounted(() => {
    clearInterval(autoSaveInterval);
  });
});
</script>

<style scoped>
.lecture-editor {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: transparent;
  padding: 0 20px;
}

.header-container {
  display: flex;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  background-color: transparent;
  position: relative;
}

.back-button {
  background: transparent;
  border: none;
  font-size: 24px;
  color: #2196f3;
  cursor: pointer;
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
  position: absolute;
  left: 20px;
}

.back-button:hover {
  background-color: rgba(33, 150, 243, 0.1);
}

.title {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #333;
  flex: 1;
  text-align: center;
}

.header-right {
  display: flex;
  gap: 12px;
}

.ai-btn {
  background-color: #2196f3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.2s;
}

.ai-btn:hover {
  background-color: #1976d2;
}

.save-btn {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background-color 0.2s;
  margin-right: 8px;
}

.save-btn:hover {
  background-color: #388e3c;
}

.save-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.lecture-container {
  display: flex;
  flex: 1;
  overflow: hidden;
  padding: 0px;
  gap: 10px;
}

.lecture-sidebar {
  width: 250px;
  border-right: 1px solid rgba(224, 224, 224, 0.5);
  background-color: rgba(255, 255, 255, 0.7);
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid rgba(224, 224, 224, 0.5);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-radius: 12px 12px 0 0;
  background-color: rgba(255, 255, 255, 0.9);
}

.add-chapter-btn {
  padding: 6px 12px;
  border-radius: 6px;
  background-color: #2196f3;
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.add-chapter-btn:hover {
  background-color: #1976d2;
}

.chapter-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.chapter-item {
  margin-bottom: 12px;
  border-radius: 10px;
  background-color: rgba(248, 249, 250, 0.7);
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.chapter-item:hover {
  background-color: rgba(227, 242, 253, 0.7);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(92, 105, 116, 0.1);
}

.chapter-item.active {
  background-color: rgba(227, 242, 253, 0.9);
  border: 1px solid rgba(33, 150, 243, 0.3);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.1);
}

.chapter-item-content {
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.chapter-title {
  flex: 1;
  font-weight: 500;
}

.chapter-actions {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.chapter-item:hover .chapter-actions {
  opacity: 1;
}

.chapter-progress {
  padding: 4px 12px;
  font-size: 12px;
  color: #666;
  border-top: 1px solid #eee;
}

.status-empty {
  color: #f44336;  /* 红色表示未生成 */
  background-color: rgba(244, 67, 54, 0.1);
}

.status-draft {
  color: #fb8c00;  /* 黄色表示未确认/未发布 */
  background-color: rgba(251, 140, 0, 0.1);
}

.status-published {
  color: #4caf50;  /* 绿色表示已发布 */
  background-color: rgba(76, 175, 80, 0.1);
}

.lecture-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background-color: rgba(255, 255, 255, 0.7);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.editor-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.9);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.chapter-title-input {
  width: 100%;
  max-width: 700px;
}

.button-group {
  display: flex;
  gap: 1px;
  background-color: #e0e0e0;
  border-radius: 8px;
  padding: 1px;
}

.mode-btn {
  padding: 8px 16px;
  border: none;
  background-color: #fff;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mode-btn:first-child {
  border-top-left-radius: 8px;
  border-bottom-left-radius: 8px;
}

.mode-btn:last-child {
  border-top-right-radius: 8px;
  border-bottom-right-radius: 8px;
}

.mode-btn.active {
  background-color: #2196f3;
  color: white;
}

.publish-btn {
  padding: 8px 16px;
  border-radius: 8px;
  border: none;
  background-color: #4caf50;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.publish-btn:hover {
  background-color: #388e3c;
}

.publish-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.editor-container {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.markdown-editor {
  height: calc(100vh - 300px);
}

.markdown-preview {
  padding: 20px;
  height: calc(100vh - 300px);
  overflow-y: auto;
}

/* 状态消息样式 */
.status-message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.loading, .generating, .saving {
  background-color: #f8f9fa;
  border-left: 4px solid #2196f3;
}

.success {
  background-color: #e8f5e9;
  border-left: 4px solid #4caf50;
}

.error {
  background-color: #ffebee;
  border-left: 4px solid #f44336;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #2196f3;
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.success-icon {
  color: #4caf50;
  font-weight: bold;
}

.error-icon {
  color: #f44336;
}

/* 响应式设计 */
@media (max-width: 992px) {
  .lecture-container {
    flex-direction: column;
  }
  
  .lecture-sidebar {
    width: 100%;
    height: 300px;
  }
  
  .editor-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .header-right {
    width: 100%;
    justify-content: flex-end;
  }
  
  .chapter-title-input {
    width: 100%;
  }
}

.unsaved-changes-warning {
  background-color: #fff3cd;
  border: 1px solid #ffeeba;
  color: #856404;
  padding: 10px 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.unsaved-changes-warning .el-icon {
  color: #ffeeba;
}
</style>
