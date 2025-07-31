<template>
  <div class="prompt-overlay" v-if="isVisible" @click.self="handleCancel">
    <div class="prompt-container">
      <div class="prompt-header">
        <h2>AI 智能生成</h2>
        <button class="close-button" @click="handleCancel">×</button>
      </div>

      <div class="prompt-body">
        <!-- 引用内容 -->
        <div class="form-group">
          <label>引用内容</label>
          <div class="reference-content">{{ referenceContent || '无' }}</div>
        </div>

        <!-- 用户要求 -->
        <div class="form-group">
          <label for="user-requirements">用户要求</label>
          <textarea
            id="user-requirements"
            v-model="userRequirements"
            placeholder="课程应满足如下要求：\n..."
            rows="4"
          ></textarea>
        </div>

        <button class="generate-button" @click="handleGenerate" :disabled="isGenerating">
          <span v-if="isGenerating" class="spinner"></span>
          {{ isGenerating ? '生成中...' : '生成' }}
        </button>

        <!-- AI生成内容 -->
        <div class="form-group">
          <label>AI生成内容</label>
          <div class="ai-content">{{ aiContent }}</div>
        </div>
      </div>

      <div class="prompt-footer">
        <button class="btn-cancel" @click="handleCancel">取消</button>
        <button class="btn-insert" @click="handleInsert">插入</button>
        <button class="btn-replace" @click="handleReplace">替换</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, watch } from 'vue';

const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  referenceContent: {
    type: String,
    default: ''
  },
  aiContent: {
    type: String,
    default: '未生成'
  },
  isGenerating: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close', 'replace', 'insert', 'generate']);

const userRequirements = ref('');

watch(() => props.isVisible, (newValue) => {
  if (newValue) {
    // Reset state when dialog opens
    userRequirements.value = '';
  }
});

const handleGenerate = () => {
  emit('generate', userRequirements.value);
};

const handleCancel = () => {
  emit('close');
};

const handleReplace = () => {
  if (props.aiContent && props.aiContent !== '未生成') {
    emit('replace', props.aiContent);
    emit('close');
  }
};

const handleInsert = () => {
  if (props.aiContent && props.aiContent !== '未生成') {
    emit('insert', props.aiContent);
    emit('close');
  }
};
</script>

<style scoped>
/* Styles adapted from Prompt.vue for consistency */
.prompt-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.prompt-container {
  width: 90%;
  max-width: 700px; /* Wider for more content */
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.18);
  overflow: hidden;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

.prompt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.prompt-header h2 {
  font-size: 1.5rem;
  margin: 0;
  font-weight: 600;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.prompt-body {
  flex-grow: 1;
  overflow-y: auto; /* Allow scrolling for content */
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #444;
}

.reference-content, .ai-content {
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 0.9rem;
  color: #555;
  min-height: 40px;
  white-space: pre-wrap; /* Preserve whitespace */
  word-wrap: break-word;
}

textarea {
  width: 100%;
  padding: 0.75rem;
  font-size: 1rem;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.8);
  resize: vertical;
  outline: none;
  transition: border-color 0.2s ease;
  min-height: 80px;
}

.generate-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 0.75rem;
  margin: 1rem 0;
  background: #6366f1;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: background-color 0.2s ease;
}

.generate-button:disabled {
  background-color: #a5b4fc;
  cursor: not-allowed;
}

.generate-button:hover {
  background: #4f46e5;
}

.prompt-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-cancel, .btn-insert, .btn-replace {
  padding: 0.5rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn-cancel {
  background: transparent;
  border-color: rgba(0, 0, 0, 0.2);
  color: #555;
}

.btn-cancel:hover {
  background: rgba(0, 0, 0, 0.05);
}

.btn-insert {
  background: #10b981;
  color: white;
}

.btn-insert:hover {
  background: #059669;
}

.btn-replace {
  background: #ef4444;
  color: white;
}

.btn-replace:hover {
  background: #dc2626;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
