<script setup>
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { trainings, totalParticipants, totalAttended, attendanceRate, chartValues, formatDate, openSection, selectTraining, showCreateForm } from '../composables/useDemoStore'




const calendarElement = ref(null)
const selectedDate = ref(null)
let selectedButton = null
const selectedDay = computed(() => days.value.find((day) => day?.key === selectedDate.value))
const selectedRow = computed(() => Math.floor(days.value.findIndex((day) => day?.key === selectedDate.value) / 7) + 1)
const selectedColumn = computed(() => days.value.findIndex((day) => day?.key === selectedDate.value) % 7)
function toggleDay(day, event) {
  selectedButton = event.currentTarget
  selectedDate.value = selectedDate.value === day.key ? null : day.key
}
function closeSchedule(restoreFocus = false) {
  selectedDate.value = null
  if (restoreFocus) selectedButton?.focus()
}
function onOutsideClick(event) {
  if (!calendarElement.value?.contains(event.target)) closeSchedule()
}
function onEscape(event) {
  if (event.key === 'Escape' && selectedDate.value) closeSchedule(true)
}
onMounted(() => {
  document.addEventListener('pointerdown', onOutsideClick)
  document.addEventListener('keydown', onEscape)
})
onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', onOutsideClick)
  document.removeEventListener('keydown', onEscape)
})

const now = new Date()
const month = ref(new Date(now.getFullYear(), now.getMonth(), 1))
const weekdays = ['일', '월', '화', '수', '목', '금', '토']
const dateKey = (date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
const today = dateKey(now)
const monthLabel = computed(() => `${month.value.getFullYear()}년 ${month.value.getMonth() + 1}월`)
const schedules = computed(() => {
  const dates = new Map()
  for (const training of trainings.value) {
    if (!training.date) continue
    if (!dates.has(training.date)) dates.set(training.date, [])
    dates.get(training.date).push(training)
  }
  return dates
})
const days = computed(() => {
  const year = month.value.getFullYear()
  const monthIndex = month.value.getMonth()
  const offset = month.value.getDay()
  const length = new Date(year, monthIndex + 1, 0).getDate()
  return Array.from({ length: Math.ceil((offset + length) / 7) * 7 }, (_, index) => {
    const day = index - offset + 1
    if (day < 1 || day > length) return null
    const key = dateKey(new Date(year, monthIndex, day))
    const items = schedules.value.get(key) ?? []
    return { day, key, items, label: `${year}년 ${monthIndex + 1}월 ${day}일${key === today ? ', 오늘' : ''}, ${items.length ? `교육 ${items.length}건: ${items.map((item) => item.title).join(', ')}` : '교육 없음'}` }
  })
})

function moveMonth(direction) {
  closeSchedule()
  month.value = new Date(month.value.getFullYear(), month.value.getMonth() + direction, 1)
}

function goToToday() {
  closeSchedule()
  const current = new Date()
  month.value = new Date(current.getFullYear(), current.getMonth(), 1)
}

</script>

<template>
          <div class="page-heading"><div><span class="eyebrow">OVERVIEW</span><h1>교육 운영 현황</h1><p>교육부터 출석, 결과까지 한눈에 확인하세요.</p></div><button class="primary-button" @click="openSection('trainings'); showCreateForm = true">＋ 새 교육 만들기</button></div>
          <div class="hero-card"><div><span class="hero-kicker">BETTER PEOPLE, BRIGHTER TOMORROW</span><h2>더 간편한 교육 운영,<br>더 정확한 출석 관리.</h2><p>오늘의 교육 현황을 확인하고 다음 업무를 시작하세요.</p><button @click="openSection('trainings')">교육 목록 보기 <span>→</span></button></div><div class="hero-art" aria-hidden="true"><div class="hero-circle circle-one"></div><div class="hero-circle circle-two"></div><div class="floating-note"><span>✓</span><div><b>출석 확인 완료</b><small>교육 운영을 한 곳에서</small></div></div></div></div>
          <div class="stats-grid">
            <button type="button" class="stat-card stat-link" title="교육 관리로 이동" @click="openSection('trainings')"><span class="stat-icon education-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m2 9 10-5 10 5-10 5L2 9Z"/><path d="M6 11v6c3 3 9 3 12 0v-6M22 9v7"/></svg></span><span class="stat-label">전체 교육</span><strong>{{ trainings.length }}<small>건</small></strong><span class="stat-foot">등록된 교육 과정</span></button>
            <button type="button" class="stat-card stat-link" title="대상자 관리로 이동" @click="openSection('participants')"><span class="stat-icon people-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/></svg></span><span class="stat-label">등록 대상자</span><strong>{{ totalParticipants }}<small>명</small></strong><span class="stat-foot">전체 교육 기준</span></button>
            <button type="button" class="stat-card stat-link" title="대상자 관리에서 출석 확인" @click="openSection('participants')"><span class="stat-icon attendance-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/></svg></span><span class="stat-label">출석 완료</span><strong>{{ totalAttended }}<small>명</small></strong><span class="stat-foot">확인된 출석 기록</span></button>
            <button type="button" class="stat-card stat-link" title="결과 보고서로 이동" @click="openSection('reports')"><span class="stat-icon rate-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M12 3a9 9 0 1 0 9 9h-9V3Z"/><path d="M16 3.9a9 9 0 0 1 4.1 4.1H16V3.9Z"/></svg></span><span class="stat-label">전체 출석률</span><strong>{{ attendanceRate }}<small>%</small></strong><span class="stat-foot">등록 대상자 대비</span></button>
          </div>
          <div class="dashboard-grid dashboard-overview">
            <section class="panel"><div class="panel-header"><div><h3>교육별 출석률</h3><p>교육별 등록 대상자 대비 출석 현황</p></div><span class="small-tag">LIVE</span></div><div v-if="chartValues.length" class="chart"><div v-for="(bar, index) in chartValues" :key="index" class="chart-column"><div class="chart-track"><div class="chart-fill" :style="{ height: `${Math.max(bar.value, 3)}%` }"><span>{{ bar.value }}%</span></div></div><span class="chart-label">{{ bar.label }}</span></div></div><div v-else class="empty-state">등록된 교육이 없습니다.</div></section>
            <section ref="calendarElement" class="panel training-calendar" aria-labelledby="calendar-title">
    <div class="panel-header">
      <h3 id="calendar-title">교육 일정</h3>
      <button type="button" class="text-button" @click="goToToday">오늘</button>
    </div>
    <div class="calendar-navigation">
      <button type="button" aria-label="이전 달" @click="moveMonth(-1)">‹</button>
      <strong aria-live="polite" aria-atomic="true">{{ monthLabel }}</strong>
      <button type="button" aria-label="다음 달" @click="moveMonth(1)">›</button>
    </div>
    <div class="calendar-grid" :aria-label="monthLabel" :style="{ '--weeks': days.length / 7 }">
      <span v-for="weekday in weekdays" :key="weekday" class="calendar-weekday" aria-hidden="true">{{ weekday }}</span>
      <div v-for="(day, index) in days" :key="index" class="calendar-cell">
        <button v-if="day" type="button" :aria-label="day.label" :aria-current="day.key === today ? 'date' : undefined" :aria-expanded="selectedDate === day.key" :aria-controls="selectedDate === day.key ? 'calendar-schedule' : undefined" class="calendar-day" :class="{ 'is-today': day.key === today, 'has-training': day.items.length, 'is-selected': selectedDate === day.key }" @click="toggleDay(day, $event)">
          {{ day.day }}
          <span v-if="day.items.length" class="calendar-dot" aria-hidden="true"></span>
        </button>
      </div>
      <section v-if="selectedDay" id="calendar-schedule" class="calendar-popover" role="region" aria-labelledby="schedule-title" :style="{ '--row': selectedRow, '--arrow': ((selectedColumn + .5) / 7 * 100) + '%' }">
        <div class="schedule-heading">
          <strong id="schedule-title">{{ formatDate(selectedDay.key) }}</strong>
          <button type="button" aria-label="교육 일정 닫기" @click="closeSchedule(true)">×</button>
        </div>
        <div class="schedule-list">
          <article v-for="item in selectedDay.items" :key="item.id" class="schedule-item">
            <b>{{ item.title }}</b>
            <p>{{ item.time?.slice(0, 5) || '시간 미정' }} · {{ item.location || '장소 미정' }}</p>
            <p v-if="item.category" class="schedule-category">{{ item.category }}</p>
            <p v-if="item.description" class="schedule-description">{{ item.description }}</p>
            <button type="button" class="text-button" @click="selectTraining(item.id)">교육 상세 보기 →</button>
          </article>
          <p v-if="!selectedDay.items.length" class="schedule-empty">등록된 교육이 없습니다.</p>
        </div>
      </section>
    </div>
    <div class="calendar-legend"><span class="calendar-dot" aria-hidden="true"></span>교육 있는 날</div>
  </section>
            <section class="panel"><div class="panel-header"><div><h3>최근 교육</h3><p>교육 일정과 진행 상태를 확인하세요</p></div><button class="text-button" @click="openSection('trainings')">전체 보기 →</button></div><div class="recent-list"><button v-for="item in trainings.slice(0, 4)" :key="item.id" class="recent-item" @click="selectTraining(item.id)"><span class="recent-icon">▤</span><span><b>{{ item.title }}</b><small>{{ formatDate(item.date) }} · {{ item.participants.length }}명 대상</small></span><span class="chevron">›</span></button><div v-if="!trainings.length" class="empty-state">아직 교육이 없습니다.</div></div></section>
          </div>
</template>

<style scoped>
.stat-icon svg { display: block; width: 1em; height: 1em; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.education-icon { color: var(--brand); background: var(--brand-subtle); }
.people-icon { color: #4774c4; background: #edf2fc; }
.attendance-icon { color: #149e61; background: #e8f5ee; }
.rate-icon { color: #b58127; background: #fbf3e3; }
.stat-link { appearance: none; width: 100%; text-align: left; color: var(--ink); }
.stat-link:focus-visible { outline: 2px solid var(--brand); outline-offset: 3px; }
.dashboard-overview { grid-template-columns: minmax(0, 1fr) minmax(260px, .9fr) minmax(0, 1.2fr); gap: 20px; }
@media (max-width: 1200px) {
  .dashboard-overview { grid-template-columns: 1fr; }
}
.dashboard-overview > .panel { height: 400px; display: flex; flex-direction: column; }
.dashboard-overview > .panel > .panel-header { min-height: 98px; padding: 20px; flex: none; }
.dashboard-overview .chart { flex: 1; min-height: 0; height: auto; padding: 28px 20px 20px; }
.dashboard-overview .chart-track { flex: 1; min-height: 0; height: auto; }
.dashboard-overview .chart-label { flex: none; }
.dashboard-overview .recent-list { flex: 1; min-height: 0; display: flex; flex-direction: column; padding: 0 20px 20px; overflow-y: auto; }
.dashboard-overview .recent-item { flex: 1; min-height: 62px; padding: 10px 0; }
.dashboard-overview .recent-item > span:nth-child(2) { min-width: 0; overflow-wrap: anywhere; }
.dashboard-overview .recent-item b { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.dashboard-overview .empty-state { flex: 1; display: grid; place-items: center; }
.training-calendar { padding-bottom: 20px; position: relative; }
.dashboard-overview > .training-calendar > .panel-header { min-height: 60px; padding: 20px 20px 12px; }
.training-calendar .panel-header { padding: 24px 20px 12px; }
.training-calendar h3 { margin: 0; }
.calendar-navigation { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin: 0 16px 12px; }
.calendar-navigation strong { font-size: 14px; }
.calendar-navigation button { display: grid; place-items: center; width: 32px; height: 32px; border: 0; border-radius: 8px; background: transparent; color: var(--muted); font-size: 24px; }
.calendar-navigation button:hover { background: var(--brand-subtle); color: var(--brand); }
.calendar-grid { position: relative; flex: 1; display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); grid-template-rows: 24px repeat(var(--weeks), minmax(0, 1fr)); margin: 0 16px; }
.calendar-weekday { text-align: center; color: var(--muted); font-size: 11px; padding: 4px 0 8px; }
.calendar-cell { display: grid; place-items: center; min-height: 34px; }
.calendar-day { position: relative; display: grid; place-items: center; width: 30px; height: 34px; padding: 0; border: 0; background: transparent; color: var(--ink); border-radius: 10px; font-size: 12px; font-variant-numeric: tabular-nums; }
.calendar-day.has-training { font-weight: 700; }
.calendar-day.is-today { color: white; background: var(--brand); }
.calendar-dot { display: inline-block; width: 4px; height: 4px; border-radius: 50%; background: var(--brand); flex: none; }
.calendar-day .calendar-dot { position: absolute; bottom: 3px; left: calc(50% - 2px); }
.calendar-day.is-today .calendar-dot { background: white; }
.calendar-legend { display: flex; align-items: center; justify-content: center; gap: 6px; color: var(--muted); font-size: 11px; margin-top: 14px; }
.training-calendar button:focus-visible, .calendar-day:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; }

.calendar-day:hover, .calendar-day.is-selected { background: var(--brand-subtle); color: var(--brand-deep); }
.calendar-day.is-today { background: var(--brand); color: white; }
.calendar-day.is-selected { outline: 2px solid var(--brand); outline-offset: 1px; }
.calendar-popover { position: absolute; z-index: 10; left: 0; right: 0; bottom: calc((100% - 24px) / var(--weeks) * (var(--weeks) - var(--row) + 1) + 8px); background: white; border: 1px solid var(--border); border-radius: 12px; box-shadow: 0 8px 28px #10111426; padding: 14px; }
.calendar-popover::before { content: ''; position: absolute; bottom: -6px; left: clamp(12px, var(--arrow), calc(100% - 18px)); width: 10px; height: 10px; background: white; border-bottom: 1px solid var(--border); border-right: 1px solid var(--border); transform: rotate(45deg); }
.schedule-heading { display: flex; align-items: center; justify-content: space-between; gap: 8px; font-size: 13px; }
.schedule-heading button { border: 0; border-radius: 6px; background: transparent; color: var(--muted); width: 28px; height: 28px; font-size: 20px; }
.schedule-list { max-height: 240px; overflow-y: auto; overscroll-behavior: contain; }
.schedule-item { border-top: 1px solid var(--border); padding: 12px 0; overflow-wrap: anywhere; }
.schedule-item:last-child { padding-bottom: 0; }
.schedule-item b { font-size: 13px; }
.schedule-item p { color: var(--muted); font-size: 12px; line-height: 1.6; margin: 6px 0; }
.schedule-item .schedule-category { color: var(--brand); }
.schedule-description { white-space: pre-wrap; }
.schedule-item .text-button { padding: 6px 0; }
.schedule-empty { font-size: 12px; color: var(--muted); margin: 12px 0 4px; }
@media (max-width: 1200px) {
  .dashboard-overview > .panel { height: 360px; }
  .training-calendar:has(.calendar-popover) { z-index: 1; }
}
</style>
