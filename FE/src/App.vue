<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { user, authReady, restoreSession, logout } from './composables/useAuth'
import { resetStore, linkedTrainingId } from './composables/useDemoStore'
import LoginView from './components/LoginView.vue'
import LandingView from './components/LandingView.vue'
import { mode, section, notice, attendeeStep, apiError, loading, saving, uploading, loadTrainings } from './composables/useDemoStore'
import SidebarNav from './components/SidebarNav.vue'
import DashboardView from './components/DashboardView.vue'
import TrainingsView from './components/TrainingsView.vue'
import TrainingWorkspace from './components/TrainingWorkspace.vue'
import ParticipantView from './components/ParticipantView.vue'

const loggingOut = ref(false)
const publicPage = ref(window.location.hash === '#/signup' ? 'signup' : window.location.hash === '#/login' ? 'login' : 'home')
function updatePublicPage() {
  publicPage.value = window.location.hash === '#/signup' ? 'signup' : window.location.hash === '#/login' ? 'login' : 'home'
  window.scrollTo(0, 0)
}
window.addEventListener('hashchange', updatePublicPage)
onBeforeUnmount(() => window.removeEventListener('hashchange', updatePublicPage))
watch(user, async (next, previous) => {
  if (!next && previous) window.location.hash = '/login'
  resetStore()
  if (next || linkedTrainingId) await loadTrainings()
})
onMounted(async () => {
  await restoreSession()
  if (!user.value && linkedTrainingId) await loadTrainings()
})
async function handleLogout() {
  loggingOut.value = true
  try { await logout() }
  catch (error) { apiError.value = error.message }
  finally { loggingOut.value = false }
}

const sectionNames = {
  dashboard: '대시보드',
  trainings: '교육 관리',
  participants: '대상자 관리',
  reports: '결과 보고서',
}

function showParticipantView() {
  mode.value = 'participant'
  attendeeStep.value = 'list'
}
</script>

<template>
  <div v-if="!authReady" class="auth-loading" role="status">로그인 정보를 확인하는 중…</div>
  <template v-else-if="!user && !(linkedTrainingId && mode === 'participant')">
    <LandingView v-if="publicPage === 'home' && !linkedTrainingId" />
    <LoginView v-else :initial-mode="publicPage === 'signup' ? 'signup' : 'login'" />
  </template>
  <div v-else class="app-shell" :class="{ 'participant-mode': mode === 'participant' }">
    <template v-if="mode === 'admin'">
      <SidebarNav />
      <main class="main-area">
        <header class="topbar">
          <div class="breadcrumb">{{ sectionNames[section] }}</div>
          <div class="top-actions">
            <button class="mode-link" @click="showParticipantView">참여자 화면 보기 ↗</button>
            <div class="avatar">{{ user?.name?.slice(0, 1) }}</div>
            <span class="user-label">{{ user?.name }}</span>
            <button class="mode-link" :disabled="loggingOut || saving || uploading" @click="handleLogout">로그아웃</button>
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

<style scoped>
.auth-loading { min-height:100vh; display:grid; place-items:center; color:#7132f5; }
</style>
