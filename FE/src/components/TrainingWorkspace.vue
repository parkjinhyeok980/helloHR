<script setup>
import { computed } from 'vue'
import { trainings, selectedId, selectedTraining, formatDate } from '../composables/useDemoStore'
import ParticipantsView from './ParticipantsView.vue'
import ReportsView from './ReportsView.vue'
import TrainingAccess from './TrainingAccess.vue'

const props = defineProps({ section: { type: String, required: true } })
const current = computed(() => ({
  participants: { eyebrow: 'PEOPLE', title: '대상자 관리', description: '대상자 등록부터 출석 확인과 전자서명 현황까지 한곳에서 관리하세요.' },
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
  <template v-else>
    <TrainingAccess v-if="section !== 'reports'" :training="selectedTraining" />
    <ParticipantsView v-if="section === 'participants'" />
    <ReportsView v-else />
  </template>
</template>
