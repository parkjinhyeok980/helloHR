<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { selectedTraining, formatDate } from '../composables/useDemoStore'
import { fetchTrainingReport } from '../api/trainings'

const report = ref(null)
const loading = ref(false)
const error = ref('')
let version = 0
const present = computed(() => report.value?.participants.filter((person) => person.attended).length ?? 0)
const rate = computed(() => report.value?.participants.length ? Math.round(present.value / report.value.participants.length * 100) : 0)
const points = (stroke) => stroke.map(([x, y]) => `${x * 600},${y * 240}`).join(' ')
const signedTime = (value) => new Intl.DateTimeFormat('ko-KR', {
  timeZone: 'Asia/Seoul', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit',
}).format(new Date(value))

async function refreshReport() {
  const id = selectedTraining.value?.id
  const current = ++version
  report.value = null
  error.value = ''
  if (!id) { loading.value = false; return false }
  loading.value = true
  try {
    const data = await fetchTrainingReport(id)
    if (current !== version) return false
    report.value = data
    return true
  } catch (cause) {
    if (current === version) error.value = `보고서를 불러오지 못했습니다. ${cause.message}`
    return false
  } finally {
    if (current === version) loading.value = false
  }
}
async function printReport() {
  if (loading.value) return
  if (await refreshReport()) {
    await nextTick()
    window.print()
  }
}
watch(() => selectedTraining.value?.id, refreshReport, { immediate: true })
onBeforeUnmount(() => { version++ })
</script>

<template>
  <div class="report-layout">
    <section v-if="report" class="panel report-sheet">
      <div class="report-topline"><span>hello HRD</span><span>EDUCATION REPORT</span></div>
      <h2>교육 결과 보고서</h2><p class="report-subtitle">{{ report.title }}</p>
      <div class="report-meta">
        <div><span>교육 일시</span><b>{{ formatDate(report.date) }} {{ report.time }}</b></div>
        <div><span>교육 장소</span><b>{{ report.location }}</b></div>
        <div><span>교육 유형</span><b>{{ report.category }}</b></div>
      </div>
      <div class="report-stats">
        <div><span>교육 대상</span><strong>{{ report.participants.length }}<small>명</small></strong></div>
        <div><span>참석</span><strong>{{ present }}<small>명</small></strong></div>
        <div><span>미참석</span><strong>{{ report.participants.length - present }}<small>명</small></strong></div>
        <div><span>출석률</span><strong>{{ rate }}<small>%</small></strong></div>
      </div>
      <h3>참석 결과 및 전자서명</h3>
      <div class="table-wrap"><table class="signed-report-table">
        <thead><tr><th>이름 / 사번</th><th>부서</th><th>결과</th><th>전자서명</th></tr></thead>
        <tbody><tr v-for="person in report.participants" :key="person.id">
          <td>{{ person.name }}<small class="report-person-number">{{ person.employee_number }}</small></td>
          <td>{{ person.department }}</td><td>{{ person.attended ? '참석' : '미참석' }}</td>
          <td class="report-signature-cell">
            <template v-if="person.signature.length">
              <svg class="report-signature" viewBox="0 0 600 240" role="img" :aria-label="`${person.name}님의 전자서명`">
                <polyline v-for="(stroke, index) in person.signature" :key="index" :points="points(stroke)"
                  fill="none" stroke="#101114" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
              <small v-if="person.signed_at" class="report-signed-time">{{ signedTime(person.signed_at) }}</small>
            </template>
            <span v-else class="report-unsigned">{{ person.attended ? '미서명' : '—' }}</span>
          </td>
        </tr></tbody>
      </table><div v-if="!report.participants.length" class="empty-state">등록된 대상자가 없습니다.</div></div>
    </section>
    <div v-else class="panel empty-state" :role="error ? 'alert' : 'status'">{{ error || '출석 기록과 전자서명을 불러오는 중입니다…' }}</div>
    <aside class="panel report-actions">
      <span class="stat-icon blue">▧</span><h3>보고서 출력</h3>
      <p>참여자가 작성한 전자서명과 서명 일시가 함께 출력됩니다. 인쇄 창에서 PDF로 저장할 수 있습니다.</p>
      <button class="outline-button" :disabled="loading" @click="refreshReport">보고서 새로고침</button>
      <button class="primary-button" :disabled="loading || !report" @click="printReport">{{ loading ? '보고서 불러오는 중…' : '보고서 인쇄 / PDF 저장' }}</button>
      <small>출력 전 최신 출석·서명 기록을 다시 불러옵니다.</small>
    </aside>
  </div>
</template>
