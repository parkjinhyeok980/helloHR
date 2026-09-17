<script setup>
import { computed } from 'vue'
import { trainings, selectedId, selectedTraining, formatDate } from '../composables/useDemoStore'
import ParticipantsView from './ParticipantsView.vue'
import AttendanceView from './AttendanceView.vue'
import ReportsView from './ReportsView.vue'

const props = defineProps({ section: { type: String, required: true } })
const current = computed(() => ({
  participants: { eyebrow: 'PEOPLE', title: '대상자 관리', description: '교육 대상자를 등록하고 명단을 확인하세요.' },
  attendance: { eyebrow: 'ATTENDANCE', title: '출석 관리', description: '참석 여부를 확인하고 기록하세요.' },
  reports: { eyebrow: 'REPORTS', title: '결과 보고서', description: '교육 결과를 확인하고 보고서를 출력하세요.' },
})[props.section])
</script>

<template>
  <div class="page-heading">
    <div>
      <span class="eyebrow">{{ current.eyebrow }}</span>
      <h1>{{ current.title }}</h1>
      <p>{{ current.description }}</p>
    </div>
  </div>
  <div v-if="trainings.length" class="selection-bar">
    <label for="training-select">교육 선택</label>
    <select id="training-select" v-model.number="selectedId">
      <option v-for="item in trainings" :key="item.id" :value="item.id">{{ item.title }}</option>
    </select>
    <span>{{ formatDate(selectedTraining?.date) }}</span>
  </div>
  <div v-if="!selectedTraining" class="panel empty-state">먼저 교육을 만들어 주세요.</div>
  <ParticipantsView v-else-if="section === 'participants'" />
  <AttendanceView v-else-if="section === 'attendance'" />
  <ReportsView v-else />
</template>
