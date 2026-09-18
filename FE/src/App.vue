<script setup>
import { mode, section, notice, attendeeStep, apiError, loading, loadTrainings } from './composables/useDemoStore'
import SidebarNav from './components/SidebarNav.vue'
import DashboardView from './components/DashboardView.vue'
import TrainingsView from './components/TrainingsView.vue'
import TrainingWorkspace from './components/TrainingWorkspace.vue'
import ParticipantView from './components/ParticipantView.vue'

const sectionNames = {
  dashboard: '대시보드',
  trainings: '교육 관리',
  participants: '대상자 관리',
  attendance: '출석 관리',
  reports: '결과 보고서',
}

function showParticipantView() {
  mode.value = 'participant'
  attendeeStep.value = 'list'
}
</script>

<template>
  <div class="app-shell" :class="{ 'participant-mode': mode === 'participant' }">
    <template v-if="mode === 'admin'">
      <SidebarNav />
      <main class="main-area">
        <header class="topbar">
          <div class="breadcrumb">{{ sectionNames[section] }}</div>
          <div class="top-actions">
            <button class="mode-link" @click="showParticipantView">참여자 화면 보기 ↗</button>
            <div class="avatar">관</div>
            <span class="user-label">교육 담당자</span>
          </div>
        </header>
        <div class="page-content">
          <div v-if="apiError" class="notice error-notice" role="alert">
            {{ apiError }} <button @click="loadTrainings">다시 시도</button>
          </div>
          <div v-if="loading" class="notice" role="status">교육 목록을 불러오는 중입니다...</div>
          <div v-if="notice" class="notice" role="status">
            {{ notice }}<button aria-label="닫기" @click="notice = ''">×</button>
          </div>
          <DashboardView v-if="section === 'dashboard'" />
          <TrainingsView v-else-if="section === 'trainings'" />
          <TrainingWorkspace v-else :section="section" />
        </div>
      </main>
    </template>
    <ParticipantView v-else />
  </div>
</template>
