<template>
  <div class="lecture-editor">
    <div class="lecture-container">
      <!-- Sidebar - Chapter List -->
      <div class="lecture-sidebar">
        <div class="sidebar-header">
          <h3>课程章节</h3>
          <el-button type="primary" size="small" @click="showAddChapterDialog">
            <i class="el-icon-plus"></i> 添加章节
          </el-button>
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
                  <i class="el-icon-rank drag-handle"></i>
                  <span class="chapter-title">{{ chapter.title }}</span>
                  <div class="chapter-actions">
                    <el-tooltip content="删除" placement="top">
                      <el-button 
                        type="danger" 
                        size="mini" 
                        icon="el-icon-delete" 
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
              <el-button type="primary" @click="generateContent" class="generate-btn">
                <i class="el-icon-magic-stick"></i> AI 生成内容
              </el-button>
              <el-input
                v-model="currentChapter.title"
                placeholder="章节标题"
                @change="updateChapterTitle"
                class="chapter-title-input"
              />
            </div>
            <div class="header-right">
              <el-button-group>
                <el-button 
                  :type="editorMode === 'edit' ? 'primary' : ''" 
                  @click="editorMode = 'edit'"
                >
                  <i class="el-icon-edit"></i> 编辑
                </el-button>
                <el-button 
                  :type="editorMode === 'preview' ? 'primary' : ''" 
                  @click="editorMode = 'preview'"
                >
                  <i class="el-icon-view"></i> 预览
                </el-button>
              </el-button-group>
              <el-button 
                type="success" 
                @click="publishChapter"
                :loading="publishing"
              >
                <i class="el-icon-upload"></i> 发布章节
              </el-button>
            </div>
          </div>

          <div class="editor-container">
            <div v-if="editorMode === 'edit'" class="markdown-editor">
              <el-input
                v-model="currentChapter.content"
                type="textarea"
                :rows="25"
                :autosize="{ minRows: 10, maxRows: 50 }"
                placeholder="输入 Markdown 格式的内容..."
                @input="onContentChange"
                resize="none"
              />
            </div>
            <div v-else class="markdown-preview" v-html="compiledMarkdown"></div>
          </div>
        </div>
        <div v-else class="no-chapter-selected">
          <el-empty description="请从左侧选择或创建章节">
            <el-button type="primary" @click="showAddChapterDialog">添加新章节</el-button>
          </el-empty>
        </div>
      </div>
    </div>

    <!-- Add Chapter Dialog -->
    <el-dialog 
      title="添加新章节" 
      v-model="addChapterDialog.visible" 
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="addChapterForm" :rules="addChapterRules" ref="addChapterForm">
        <el-form-item label="章节标题" prop="title">
          <el-input v-model="addChapterForm.title" placeholder="请输入章节标题"></el-input>
        </el-form-item>
        <el-form-item label="章节位置" prop="position">
          <el-select v-model="addChapterForm.position" placeholder="请选择添加位置" style="width: 100%">
            <el-option 
              v-for="(chapter, index) in chapters" 
              :key="chapter.id" 
              :label="`在 ${chapter.title} 之后`"
              :value="index + 1"
            />
            <el-option :label="`添加到最后`" :value="chapters.length" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addChapterDialog.visible = false">取 消</el-button>
          <el-button type="primary" @click="confirmAddChapter" :loading="addChapterDialog.loading">确 定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { ElMessage, ElMessageBox } from 'element-plus';
import draggable from 'vuedraggable';

export default {
  name: 'LectureEditor',
  
  props: {
    courseId: {
      type: [String, Number],
      required: true
    },
    courseName: {
      type: String,
      default: '课程讲义'
    }
  },

  components: {
    draggable
  },
  
  setup(props) {
    const router = useRouter();
    
    // 状态管理
    const chapters = ref(JSON.parse(localStorage.getItem('lectureChapters') || '[]'));
    const currentChapter = ref(null);
    const editorMode = ref('edit');
    const publishing = ref(false);
    const hasUnsavedChanges = ref(false);
    
    // 添加章节对话框
    const addChapterDialog = ref({
      visible: false,
      loading: false
    });
    
    const addChapterForm = ref({
      title: '',
      position: 0
    });
    
    const addChapterRules = {
      title: [
        { required: true, message: '请输入章节标题', trigger: 'blur' },
        { min: 2, message: '章节标题不能少于2个字符', trigger: 'blur' }
      ],
      position: [
        { required: true, message: '请选择添加位置', trigger: 'change' }
      ]
    };
    
    // 如果没有章节数据，初始化一些示例数据
    if (chapters.value.length === 0) {
      chapters.value = [
        { 
          id: Date.now(), 
          title: '第一章：课程介绍', 
          content: '# 第一章：课程介绍\n\n这是第一章的内容...', 
          status: 'empty',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
      ];
    }
    
    // 默认选中第一个章节
    if (chapters.value.length > 0 && !currentChapter.value) {
      currentChapter.value = chapters.value[0];
    }

    // 保存章节到本地存储
    const saveChapters = () => {
      localStorage.setItem('lectureChapters', JSON.stringify(chapters.value));
    };
    
    // 自动保存
    watch(chapters, () => {
      saveChapters();
    }, { deep: true });
    
    // 生成章节内容
    const generateContent = async () => {
      try {
        // 这里添加AI生成内容的逻辑
        ElMessage.info('正在生成内容，请稍候...');
        
        // 模拟API调用延迟
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 生成示例内容
        const generatedContent = `# ${currentChapter.value.title}\n\n` +
          `## 学习目标\n- 理解${currentChapter.value.title.split('：')[1] || '本章节'}的基本概念\n- 掌握相关知识点\n- 能够应用所学知识解决问题\n\n` +
          `## 主要内容\n- 内容1\n- 内容2\n- 内容3\n\n` +
          `## 总结\n- 重点回顾\n- 常见问题\n\n` +
          `## 课后练习\n1. 练习题1\n2. 练习题2`;
        
        currentChapter.value.content = generatedContent;
        currentChapter.value.status = 'draft';
        currentChapter.value.updatedAt = new Date().toISOString();
        hasUnsavedChanges.value = true;
        
        ElMessage.success('内容生成成功');
      } catch (error) {
        console.error('生成内容失败:', error);
        ElMessage.error('生成内容失败，请稍后重试');
      }
    };
    
    // 发布章节
    const publishChapter = async () => {
      if (!currentChapter.value) return;
      
      try {
        publishing.value = true;
        
        // 这里添加发布章节的API调用
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        currentChapter.value.status = 'published';
        currentChapter.value.publishedAt = new Date().toISOString();
        currentChapter.value.updatedAt = new Date().toISOString();
        hasUnsavedChanges.value = false;
        
        ElMessage.success('章节发布成功');
      } catch (error) {
        console.error('发布失败:', error);
        ElMessage.error('发布失败，请稍后重试');
      } finally {
        publishing.value = false;
      }
    };

    // 计算属性：编译Markdown为HTML
    const compiledMarkdown = computed(() => {
      if (!currentChapter.value?.content) return '';
      return DOMPurify.sanitize(marked(currentChapter.value.content));
    });
    
    // 获取状态文本
    const getStatusText = (status) => {
      const statusMap = {
        'empty': '未生成',
        'draft': '草稿',
        'published': '已发布'
      };
      return statusMap[status] || '未知状态';
    };
    
    // 显示添加章节对话框
    const showAddChapterDialog = () => {
      addChapterForm.value = {
        title: `第${chapters.value.length + 1}章：新章节`,
        position: chapters.value.length
      };
      addChapterDialog.value.visible = true;
    };
    
    // 确认添加章节
    const confirmAddChapter = () => {
      const newChapter = {
        id: Date.now(),
        title: addChapterForm.value.title,
        content: '',
        status: 'empty',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      
      // 在指定位置插入新章节
      const position = Math.min(addChapterForm.value.position, chapters.value.length);
      chapters.value.splice(position, 0, newChapter);
      
      // 更新章节编号
      updateChapterNumbers();
      
      // 选中新添加的章节
      currentChapter.value = newChapter;
      editorMode.value = 'edit';
      
      // 关闭对话框
      addChapterDialog.value.visible = false;
      
      ElMessage.success('章节添加成功');
    };
    
    // 更新章节编号
    const updateChapterNumbers = () => {
      chapters.value.forEach((chapter, index) => {
        // 只更新没有自定义标题的章节
        if (chapter.title.startsWith('第') && chapter.title.includes('章：')) {
          const newTitle = `第${index + 1}章：${chapter.title.split('：')[1] || '新章节'}`;
          if (chapter.title !== newTitle) {
            chapter.title = newTitle;
          }
        }
      });
    };
    
    // 确认删除章节
    const confirmDeleteChapter = (chapter) => {
      if (chapters.value.length <= 1) {
        ElMessage.warning('至少需要保留一个章节');
        return;
      }
      
      ElMessageBox.confirm(
        `确定要删除章节"${chapter.title}"吗？此操作不可恢复！`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        const index = chapters.value.findIndex(c => c.id === chapter.id);
        if (index !== -1) {
          chapters.value.splice(index, 1);
          
          // 如果删除的是当前选中的章节，则选中上一个或下一个章节
          if (currentChapter.value && currentChapter.value.id === chapter.id) {
            if (chapters.value.length > 0) {
              currentChapter.value = chapters.value[Math.max(0, index - 1)];
            } else {
              currentChapter.value = null;
            }
          }
          
          // 更新章节编号
          updateChapterNumbers();
          
          ElMessage.success('章节删除成功');
        }
      }).catch(() => {
        // 用户取消删除
      });
    };
    
    // 选择章节
    const selectChapter = async (chapter) => {
      // 检查是否有未保存的更改
      if (hasUnsavedChanges.value && currentChapter.value) {
        try {
          await ElMessageBox.confirm(
            '当前章节有未保存的更改，是否保存？',
            '提示',
            {
              confirmButtonText: '保存',
              cancelButtonText: '不保存',
              type: 'warning'
            }
          );
          
          // 用户选择保存
          await saveCurrentChapter();
        } catch (error) {
          // 用户选择不保存或取消，继续切换章节
        }
      }
      
      // 切换章节
      currentChapter.value = chapter;
      hasUnsavedChanges.value = false;
      editorMode.value = 'edit';
    };
    
    // 保存当前章节
    const saveCurrentChapter = async () => {
      if (!currentChapter.value) return;
      
      try {
        // 这里添加保存到API的逻辑
        currentChapter.value.updatedAt = new Date().toISOString();
        hasUnsavedChanges.value = false;
        
        // 更新章节状态
        if (currentChapter.value.content.trim()) {
          currentChapter.value.status = 'draft';
        } else {
          currentChapter.value.status = 'empty';
        }
        
        ElMessage.success('保存成功');
        return true;
      } catch (error) {
        console.error('保存失败:', error);
        ElMessage.error('保存失败，请稍后重试');
        return false;
      }
    };
    
    // 更新章节标题
    const updateChapterTitle = () => {
      if (!currentChapter.value) return;
      
      currentChapter.value.updatedAt = new Date().toISOString();
      hasUnsavedChanges.value = true;
      
      // 更新章节状态
      if (currentChapter.value.status === 'empty' && currentChapter.value.content.trim()) {
        currentChapter.value.status = 'draft';
      }
    };
    
    // 内容变更处理
    const onContentChange = () => {
      if (!currentChapter.value) return;
      
      currentChapter.value.updatedAt = new Date().toISOString();
      hasUnsavedChanges.value = true;
      
      // 更新章节状态
      if (currentChapter.value.status === 'empty' && currentChapter.value.content.trim()) {
        currentChapter.value.status = 'draft';
      }
    };
    
    // 章节顺序变更
    const onChapterOrderChange = () => {
      updateChapterNumbers();
      hasUnsavedChanges.value = true;
    };
    
    // 组件挂载时检查URL参数
    onMounted(() => {
      // 检查是否有chapterId参数
      const route = router.currentRoute.value;
      if (route.params.chapterId) {
        const chapter = chapters.value.find(c => c.id === parseInt(route.params.chapterId));
        if (chapter) {
          currentChapter.value = chapter;
        }
      }
      
      // 监听浏览器刷新/关闭事件，提示保存
      window.addEventListener('beforeunload', (e) => {
        if (hasUnsavedChanges.value) {
          e.preventDefault();
          e.returnValue = '您有未保存的更改，确定要离开吗？';
          return e.returnValue;
        }
      });
    });

    return {
      // 响应式数据
      chapters,
      currentChapter,
      editorMode,
      publishing,
      addChapterDialog,
      addChapterForm,
      addChapterRules,
      
      // 方法
      getStatusText,
      showAddChapterDialog,
      confirmAddChapter,
      selectChapter,
      updateChapterTitle,
      onContentChange,
      generateContent,
      publishChapter,
      confirmDeleteChapter,
      onChapterOrderChange,
      
      // 计算属性
      compiledMarkdown,
      
      // 组件
      draggable
    };
  }
};
</script>

<style scoped>
.lecture-editor {
  height: calc(100vh - 60px);
  padding: 20px;
  background-color: #f5f7fa;
  box-sizing: border-box;
}

.lecture-container {
  display: flex;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

/* Sidebar */
.lecture-sidebar {
  width: 240px;
  border-right: 1px solid #e6e6e6;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.sidebar-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f0f2f5;
  flex-shrink: 0;
}

.chapter-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.chapter-item {
  margin: 4px 10px;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #ebeef5;
  background-color: #fff;
}

.chapter-item:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.chapter-item.active {
  border-color: #409eff;
  box-shadow: 0 0 0 1px #409eff;
}

.chapter-item-content {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  position: relative;
}

.drag-handle {
  margin-right: 8px;
  color: #c0c4cc;
  cursor: move;
  font-size: 16px;
}

.drag-handle:hover {
  color: #409eff;
}

.chapter-title {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
  color: #303133;
}

.chapter-actions {
  margin-left: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.chapter-item:hover .chapter-actions {
  opacity: 1;
}

.chapter-progress {
  height: 4px;
  font-size: 0;
  transition: all 0.3s;
}

.status-empty {
  background-color: #f56c6c;
}

.status-draft {
  background-color: #e6a23c;
}

.status-published {
  background-color: #67c23a;
}

.lecture-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.editor-header {
  padding: 15px 25px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  flex-shrink: 0;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  max-width: 70%;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chapter-title-input {
  flex: 1;
  max-width: 400px;
}

.chapter-title-input :deep(.el-input__wrapper) {
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  transition: border-color 0.3s;
}

.chapter-title-input :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff;
  border-color: #409eff;
}

.generate-btn {
  white-space: nowrap;
}

.editor-container {
  flex: 1;
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.markdown-editor {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.markdown-editor :deep(.el-textarea__inner) {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  line-height: 1.6;
  font-size: 14px;
  border: none;
  resize: none;
  box-shadow: none;
  padding: 15px;
  min-height: 100% !important;
}

.markdown-preview {
  flex: 1;
  padding: 25px 30px;
  overflow-y: auto;
  background-color: #fff;
  line-height: 1.7;
  color: #24292e;
}

/* Markdown 样式 */
.markdown-preview :deep(h1) {
  margin: 0.67em 0 0.5em;
  padding-bottom: 0.3em;
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-preview :deep(h2) {
  margin: 1.2em 0 0.8em;
  padding-bottom: 0.3em;
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-preview :deep(h3) {
  margin: 1em 0 0.6em;
  font-size: 1.25em;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-preview :deep(p) {
  margin: 0 0 16px 0;
  line-height: 1.7;
}

.markdown-preview :deep(ul),
.markdown-preview :deep(ol) {
  padding-left: 2em;
  margin-bottom: 16px;
}

.markdown-preview :deep(li) {
  margin-bottom: 0.25em;
}

.markdown-preview :deep(blockquote) {
  margin: 0 0 16px 0;
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
  background-color: #f6f8fa;
  border-radius: 4px;
  padding: 10px 15px;
}

.markdown-preview :deep(pre) {
  background-color: #f6f8fa;
  border-radius: 6px;
  padding: 16px;
  overflow: auto;
  margin-bottom: 16px;
  line-height: 1.45;
}

.markdown-preview :deep(code) {
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
}

.markdown-preview :deep(pre code) {
  background-color: transparent;
  padding: 0;
  border-radius: 0;
  font-size: 100%;
}

.markdown-preview :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 16px;
  display: block;
  overflow: auto;
}

.markdown-preview :deep(th),
.markdown-preview :deep(td) {
  padding: 6px 13px;
  border: 1px solid #dfe2e5;
}

.markdown-preview :deep(tr) {
  background-color: #fff;
  border-top: 1px solid #c6cbd1;
}

.markdown-preview :deep(tr:nth-child(2n)) {
  background-color: #f6f8fa;
}

.markdown-preview :deep(img) {
  max-width: 100%;
  box-sizing: content-box;
  background-color: #fff;
}

.markdown-preview :deep(a) {
  color: #0366d6;
  text-decoration: none;
}

.markdown-preview :deep(a:hover) {
  text-decoration: underline;
}

/* 空状态 */
.no-chapter-selected {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #909399;
  flex-direction: column;
  padding: 40px 0;
}

.no-chapter-selected :deep(.el-empty__description) {
  margin: 20px 0 0 0;
}

/* 响应式调整 */
@media (max-width: 992px) {
  .lecture-container {
    flex-direction: column;
    height: auto;
    max-height: 90vh;
  }
  
  .lecture-sidebar {
    width: 100%;
    height: 300px;
    border-right: none;
    border-bottom: 1px solid #e6e6e6;
  }
  
  .header-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .header-right {
    flex-wrap: wrap;
    justify-content: flex-end;
  }
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-thumb {
  background-color: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background-color: #a8a8a8;
}

::-webkit-scrollbar-track {
  background-color: #f1f1f1;
}

/* 动画效果 */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.chapter-item {
  animation: fadeIn 0.3s ease-out forwards;
}

/* 过渡效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
