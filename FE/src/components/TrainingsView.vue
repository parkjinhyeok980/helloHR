<script setup>
import {
  trainings, filteredTrainings, search, showCreateForm, editingId,
  newTraining, saving, formatDate, selectTraining, startCreateTraining,
  startEditTraining, cancelTrainingForm, saveTraining, removeTraining,
} from '../composables/useDemoStore'
</script>

<template>
  <div class="page-heading">
    <div>
      <span class="eyebrow">TRAININGS</span>
      <h1>교육 관리</h1>
      <p>교육을 만들고 일정을 관리하세요.</p>
    </div>
    <button class="primary-button" @click="startCreateTraining">＋ 새 교육 만들기</button>
  </div>

  <form v-if="showCreateForm" class="panel form-panel" @submit.prevent="saveTraining">
    <div class="panel-header">
      <div>
        <h3>{{ editingId ? '교육 수정' : '새 교육 만들기' }}</h3>
        <p>교육 정보를 입력해 저장합니다.</p>
      </div>
    </div>
    <div class="form-grid">
      <label>교육명 <span>*</span><input v-model="newTraining.title" required maxlength="200" placeholder="예: 산업안전보건교육"></label>
      <label>교육 유형
        <select v-model="newTraining.category">
          <option>법정 필수</option><option>사내 교육</option><option>기타</option>
        </select>
      </label>
      <label>교육일 <span>*</span><input v-model="newTraining.date" type="date" required></label>
      <label>시작 시간 <span>*</span><input v-model="newTraining.time" type="time" required></label>
      <label class="full-width">장소<input v-model="newTraining.location" maxlength="200" placeholder="예: 본관 3층 대회의실"></label>
      <label class="full-width">설명<textarea v-model="newTraining.description" rows="3" placeholder="교육 내용을 간단히 적어 주세요"></textarea></label>
    </div>
    <div class="form-actions">
      <button type="button" class="outline-button" :disabled="saving" @click="cancelTrainingForm">취소</button>
      <button type="submit" class="primary-button" :disabled="saving">{{ saving ? '저장 중...' : editingId ? '수정 저장' : '교육 등록' }}</button>
    </div>
  </form>

  <section class="panel">
    <div class="panel-header">
      <div>
        <h3>교육 목록 <span class="count-pill">{{ trainings.length }}</span></h3>
        <p>교육을 선택하거나 정보를 수정·삭제할 수 있습니다.</p>
      </div>
      <input v-model="search" class="search-input" placeholder="교육명 검색" aria-label="교육명 검색">
    </div>
    <div class="training-list">
      <div v-for="item in filteredTrainings" :key="item.id" class="training-row">
        <button class="training-open" @click="selectTraining(item.id, 'participants')">
          <span class="training-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m2 9 10-5 10 5-10 5L2 9Z"/><path d="M6 11v6c3 3 9 3 12 0v-6M22 9v7"/></svg></span>
          <span class="training-info">
            <b>{{ item.title }}</b>
            <small>{{ formatDate(item.date) }} {{ item.time }} · {{ item.location || '장소 미정' }}</small>
          </span>
          <span class="type-chip">{{ item.category }}</span>
          <span class="row-count">{{ item.participants.length }}명</span>
        </button>
        <div class="training-actions">
          <button class="table-action" :disabled="saving" :aria-label="`${item.title} 수정`" @click="startEditTraining(item)">수정</button>
          <button class="table-action danger" :disabled="saving" :aria-label="`${item.title} 삭제`" @click="removeTraining(item)">삭제</button>
        </div>
      </div>
      <div v-if="!filteredTrainings.length" class="empty-state">{{ trainings.length ? '검색 결과가 없습니다.' : '아직 등록된 교육이 없습니다.' }}</div>
    </div>
  </section>
</template>

<style scoped>
.training-icon svg { display: block; width: 1em; height: 1em; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
</style>
