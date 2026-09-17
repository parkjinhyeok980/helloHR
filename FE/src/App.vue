<script setup>
import { computed, ref, watch } from 'vue'

const storageKey = 'hellohr-demo-v1'
const dateAfter = (days) => {
  const date = new Date()
  date.setDate(date.getDate() + days)
  return date.toISOString().slice(0, 10)
}

const sampleTrainings = [
  {
    id: 1,
    title: '2026 하반기 산업안전보건교육',
    category: '법정 필수',
    date: dateAfter(2),
    time: '10:00',
    location: '본관 3층 대회의실',
    code: '1234',
    participants: [
      { id: 101, name: '김민수', department: '인사팀', attended: true },
      { id: 102, name: '이지은', department: '마케팅팀', attended: true },
      { id: 103, name: '박현우', department: '개발팀', attended: false },
      { id: 104, name: '최수빈', department: '경영지원팀', attended: false },
      { id: 105, name: '정하늘', department: '디자인팀', attended: true },
    ],
  },
  {
    id: 2,
    title: '직장 내 괴롭힘 예방교육',
    category: '법정 필수',
    date: dateAfter(7),
    time: '14:00',
    location: '온라인 교육',
    code: '5678',
    participants: [
      { id: 201, name: '김민수', department: '인사팀', attended: false },
      { id: 202, name: '이지은', department: '마케팅팀', attended: false },
    ],
  },
  {
    id: 3,
    title: '정보보안 기본 교육',
    category: '사내 교육',
    date: dateAfter(-5),
    time: '15:00',
    location: '별관 교육장',
    code: '9012',
    participants: [
      { id: 301, name: '김민수', department: '인사팀', attended: true },
      { id: 302, name: '박현우', department: '개발팀', attended: true },
      { id: 303, name: '정하늘', department: '디자인팀', attended: true },
    ],
  },
]

function loadTrainings() {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey))
    return Array.isArray(saved) ? saved : sampleTrainings
  } catch {
    return sampleTrainings
  }
}

const trainings = ref(loadTrainings())
const section = ref('dashboard')
const mode = ref('admin')
const selectedId = ref(trainings.value[0]?.id ?? null)
const showCreateForm = ref(false)
const search = ref('')
const notice = ref('')
const today = new Date().toISOString().slice(0, 10)
const newTraining = ref({ title: '', category: '법정 필수', date: today, time: '10:00', location: '' })
const newParticipant = ref({ name: '', department: '' })
const attendee = ref({ trainingId: trainings.value[0]?.id ?? null, name: '', code: '' })
const attendeeStep = ref('list')
const attendeeError = ref('')

watch(trainings, (value) => localStorage.setItem(storageKey, JSON.stringify(value)), { deep: true })

const selectedTraining = computed(() => trainings.value.find((item) => item.id === selectedId.value) ?? trainings.value[0])
const attendeeTraining = computed(() => trainings.value.find((item) => item.id === attendee.value.trainingId))
const totalParticipants = computed(() => trainings.value.reduce((sum, item) => sum + item.participants.length, 0))
const totalAttended = computed(() => trainings.value.reduce((sum, item) => sum + item.participants.filter((person) => person.attended).length, 0))
const attendanceRate = computed(() => totalParticipants.value ? Math.round(totalAttended.value / totalParticipants.value * 100) : 0)
const filteredTrainings = computed(() => trainings.value.filter((item) => item.title.toLowerCase().includes(search.value.toLowerCase())))
const selectedPresent = computed(() => selectedTraining.value?.participants.filter((person) => person.attended).length ?? 0)
const selectedRate = computed(() => selectedTraining.value?.participants.length ? Math.round(selectedPresent.value / selectedTraining.value.participants.length * 100) : 0)
const chartValues = computed(() => trainings.value.slice(0, 5).map((item) => ({
  label: item.title.length > 8 ? `${item.title.slice(0, 8)}…` : item.title,
  value: item.participants.length ? Math.round(item.participants.filter((person) => person.attended).length / item.participants.length * 100) : 0,
})))

function formatDate(value) {
  if (!value) return '일정 미정'
  return new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' }).format(new Date(`${value}T12:00:00`))
}

function openSection(next) {
  section.value = next
  showCreateForm.value = false
  notice.value = ''
}

function selectTraining(id, next = 'trainings') {
  selectedId.value = id
  openSection(next)
}

function createTraining() {
  if (!newTraining.value.title.trim() || !newTraining.value.date) return
  const id = Date.now()
  trainings.value.unshift({ ...newTraining.value, id, title: newTraining.value.title.trim(), location: newTraining.value.location.trim() || '장소 미정', code: String(id).slice(-4), participants: [] })
  selectedId.value = id
  attendee.value.trainingId = id
  newTraining.value = { title: '', category: '법정 필수', date: today, time: '10:00', location: '' }
  showCreateForm.value = false
  section.value = 'participants'
  notice.value = '교육을 만들었습니다. 이제 대상자를 등록해 주세요.'
}

function addParticipant() {
  if (!selectedTraining.value || !newParticipant.value.name.trim()) return
  const name = newParticipant.value.name.trim()
  if (selectedTraining.value.participants.some((person) => person.name === name)) {
    notice.value = '이 교육에 같은 이름의 대상자가 이미 있습니다.'
    return
  }
  selectedTraining.value.participants.push({ id: Date.now(), name, department: newParticipant.value.department.trim() || '미지정', attended: false })
  newParticipant.value = { name: '', department: '' }
  notice.value = '대상자를 등록했습니다.'
}

function toggleAttendance(person) {
  person.attended = !person.attended
  notice.value = `${person.name}님의 출석을 ${person.attended ? '확인' : '취소'}했습니다.`
}

function startCheckIn(trainingId) {
  attendee.value = { trainingId, name: '', code: '' }
  attendeeError.value = ''
  attendeeStep.value = 'checkin'
}

function checkIn() {
  const training = attendeeTraining.value
  const person = training?.participants.find((item) => item.name === attendee.value.name.trim())
  if (!person) {
    attendeeError.value = '등록된 대상자 이름을 확인해 주세요.'
    return
  }
  if (attendee.value.code.trim() !== training.code) {
    attendeeError.value = '출석 코드가 일치하지 않습니다.'
    return
  }
  person.attended = true
  attendeeError.value = ''
  attendeeStep.value = 'done'
}

function printReport() {
  window.print()
}
</script>

<template>
  <div class="app-shell" :class="{ 'participant-mode': mode === 'participant' }">
    <aside class="sidebar" v-if="mode === 'admin'">
      <div class="brand"><span class="brand-mark">✦</span><span>hello<span class="brand-comma">,</span>HRD<small>EDUCATION OPERATIONS</small></span></div>
      <div class="workspace-label">WORKSPACE</div>
      <nav class="side-nav" aria-label="주 메뉴">
        <button :class="{ active: section === 'dashboard' }" @click="openSection('dashboard')"><span>▦</span> 대시보드</button>
        <button :class="{ active: section === 'trainings' }" @click="openSection('trainings')"><span>▤</span> 교육 관리</button>
        <button :class="{ active: section === 'participants' }" @click="openSection('participants')"><span>♧</span> 대상자 관리</button>
        <button :class="{ active: section === 'attendance' }" @click="openSection('attendance')"><span>✓</span> 출석 관리</button>
        <button :class="{ active: section === 'reports' }" @click="openSection('reports')"><span>▧</span> 결과 보고서</button>
      </nav>
      <div class="sidebar-bottom"><span class="status-dot"></span> 로컬 데모 데이터 <small>이 브라우저에만 저장됩니다</small></div>
    </aside>

    <main class="main-area" v-if="mode === 'admin'">
      <header class="topbar">
        <div class="breadcrumb">워크스페이스 <span>/</span> {{ { dashboard: '대시보드', trainings: '교육 관리', participants: '대상자 관리', attendance: '출석 관리', reports: '결과 보고서' }[section] }}</div>
        <div class="top-actions"><button class="mode-link" @click="mode = 'participant'; attendeeStep = 'list'">참여자 화면 보기 ↗</button><div class="avatar">관</div><span class="user-label">교육 담당자</span></div>
      </header>

      <div class="page-content">
        <div v-if="notice" class="notice" role="status">{{ notice }}<button aria-label="닫기" @click="notice = ''">×</button></div>

        <template v-if="section === 'dashboard'">
          <div class="page-heading"><div><span class="eyebrow">OVERVIEW</span><h1>교육 운영 현황</h1><p>교육부터 출석, 결과까지 한눈에 확인하세요.</p></div><button class="primary-button" @click="openSection('trainings'); showCreateForm = true">＋ 새 교육 만들기</button></div>
          <div class="hero-card"><div><span class="hero-kicker">BETTER PEOPLE, BRIGHTER TOMORROW</span><h2>더 간편한 교육 운영,<br>더 정확한 출석 관리.</h2><p>오늘의 교육 현황을 확인하고 다음 업무를 시작하세요.</p><button @click="openSection('trainings')">교육 목록 보기 <span>→</span></button></div><div class="hero-art"><div class="hero-circle circle-one"></div><div class="hero-circle circle-two"></div><div class="floating-note"><span>✓</span><div><b>출석 확인 완료</b><small>교육 운영을 한 곳에서</small></div></div></div></div>
          <div class="stats-grid">
            <div class="stat-card"><span class="stat-icon blue">▤</span><span class="stat-label">전체 교육</span><strong>{{ trainings.length }}<small>건</small></strong><span class="stat-foot">등록된 교육 과정</span></div>
            <div class="stat-card"><span class="stat-icon mint">♧</span><span class="stat-label">등록 대상자</span><strong>{{ totalParticipants }}<small>명</small></strong><span class="stat-foot">전체 교육 기준</span></div>
            <div class="stat-card"><span class="stat-icon amber">✓</span><span class="stat-label">출석 완료</span><strong>{{ totalAttended }}<small>명</small></strong><span class="stat-foot">확인된 출석 기록</span></div>
            <div class="stat-card"><span class="stat-icon violet">◔</span><span class="stat-label">전체 출석률</span><strong>{{ attendanceRate }}<small>%</small></strong><span class="stat-foot">등록 대상자 대비</span></div>
          </div>
          <div class="dashboard-grid">
            <section class="panel"><div class="panel-header"><div><h3>교육별 출석률</h3><p>교육별 등록 대상자 대비 출석 현황</p></div><span class="small-tag">LIVE</span></div><div v-if="chartValues.length" class="chart"><div v-for="(bar, index) in chartValues" :key="index" class="chart-column"><div class="chart-track"><div class="chart-fill" :style="{ height: `${Math.max(bar.value, 3)}%` }"><span>{{ bar.value }}%</span></div></div><span class="chart-label">{{ bar.label }}</span></div></div><div v-else class="empty-state">등록된 교육이 없습니다.</div></section>
            <section class="panel"><div class="panel-header"><div><h3>최근 교육</h3><p>교육 일정과 진행 상태를 확인하세요</p></div><button class="text-button" @click="openSection('trainings')">전체 보기 →</button></div><div class="recent-list"><button v-for="item in trainings.slice(0, 4)" :key="item.id" class="recent-item" @click="selectTraining(item.id)"><span class="recent-icon">▤</span><span><b>{{ item.title }}</b><small>{{ formatDate(item.date) }} · {{ item.participants.length }}명 대상</small></span><span class="chevron">›</span></button><div v-if="!trainings.length" class="empty-state">아직 교육이 없습니다.</div></div></section>
          </div>
        </template>

        <template v-else-if="section === 'trainings'">
          <div class="page-heading"><div><span class="eyebrow">TRAININGS</span><h1>교육 관리</h1><p>교육을 만들고 대상자를 연결하세요.</p></div><button class="primary-button" @click="showCreateForm = !showCreateForm">＋ 새 교육 만들기</button></div>
          <form v-if="showCreateForm" class="panel form-panel" @submit.prevent="createTraining"><div class="panel-header"><div><h3>새 교육 만들기</h3><p>필수 항목을 입력해 교육을 등록합니다.</p></div></div><div class="form-grid"><label>교육명 <span>*</span><input v-model="newTraining.title" required placeholder="예: 산업안전보건교육"></label><label>교육 유형<select v-model="newTraining.category"><option>법정 필수</option><option>사내 교육</option><option>기타</option></select></label><label>교육일 <span>*</span><input v-model="newTraining.date" type="date" required></label><label>시작 시간<input v-model="newTraining.time" type="time"></label><label class="full-width">장소<input v-model="newTraining.location" placeholder="예: 본관 3층 대회의실"></label></div><div class="form-actions"><button type="button" class="outline-button" @click="showCreateForm = false">취소</button><button type="submit" class="primary-button">교육 등록</button></div></form>
          <section class="panel"><div class="panel-header"><div><h3>교육 목록 <span class="count-pill">{{ trainings.length }}</span></h3><p>교육을 선택하면 대상자와 출석을 관리할 수 있습니다.</p></div><input v-model="search" class="search-input" placeholder="교육명 검색" aria-label="교육명 검색"></div><div class="training-list"><button v-for="item in filteredTrainings" :key="item.id" class="training-row" @click="selectTraining(item.id, 'participants')"><span class="training-icon">▤</span><span class="training-info"><b>{{ item.title }}</b><small>{{ formatDate(item.date) }} {{ item.time }} · {{ item.location }}</small></span><span class="type-chip">{{ item.category }}</span><span class="row-count">{{ item.participants.length }}명</span><span class="chevron">›</span></button><div v-if="!filteredTrainings.length" class="empty-state">검색 결과가 없습니다.</div></div></section>
        </template>

        <template v-else-if="section === 'participants' || section === 'attendance' || section === 'reports'">
          <div class="page-heading"><div><span class="eyebrow">{{ section === 'participants' ? 'PEOPLE' : section === 'attendance' ? 'ATTENDANCE' : 'REPORTS' }}</span><h1>{{ section === 'participants' ? '대상자 관리' : section === 'attendance' ? '출석 관리' : '결과 보고서' }}</h1><p>{{ section === 'participants' ? '교육 대상자를 등록하고 명단을 확인하세요.' : section === 'attendance' ? '참석 여부를 확인하고 기록하세요.' : '교육 결과를 확인하고 보고서를 출력하세요.' }}</p></div></div>
          <div v-if="trainings.length" class="selection-bar"><label for="training-select">교육 선택</label><select id="training-select" v-model.number="selectedId"><option v-for="item in trainings" :key="item.id" :value="item.id">{{ item.title }}</option></select><span>{{ formatDate(selectedTraining?.date) }}</span></div>
          <div v-if="!selectedTraining" class="panel empty-state">먼저 교육을 만들어 주세요.</div>
          <template v-else-if="section === 'participants'"><div class="detail-grid"><div class="panel detail-card"><span>교육 일정</span><strong>{{ formatDate(selectedTraining.date) }}</strong><small>{{ selectedTraining.time }} · {{ selectedTraining.location }}</small></div><div class="panel detail-card"><span>등록 대상자</span><strong>{{ selectedTraining.participants.length }}명</strong><small>이 교육에 연결된 대상자</small></div><div class="panel detail-card"><span>출석 코드</span><strong>{{ selectedTraining.code }}</strong><small>참여자 화면에서 입력</small></div></div><section class="panel"><div class="panel-header"><div><h3>대상자 명단</h3><p>이름과 부서를 입력해 교육 대상자를 추가하세요.</p></div></div><form class="inline-form" @submit.prevent="addParticipant"><input v-model="newParticipant.name" required placeholder="이름" aria-label="대상자 이름"><input v-model="newParticipant.department" placeholder="부서" aria-label="대상자 부서"><button class="primary-button" type="submit">＋ 대상자 추가</button></form><div class="table-wrap"><table><thead><tr><th>이름</th><th>부서</th><th>출석</th></tr></thead><tbody><tr v-for="person in selectedTraining.participants" :key="person.id"><td class="name-cell">{{ person.name }}</td><td>{{ person.department }}</td><td><span class="badge" :class="person.attended ? 'success' : 'neutral'">{{ person.attended ? '참석' : '미참석' }}</span></td></tr></tbody></table><div v-if="!selectedTraining.participants.length" class="empty-state">등록된 대상자가 없습니다.</div></div></section></template>
          <template v-else-if="section === 'attendance'"><div class="detail-grid two"><div class="panel detail-card"><span>출석 완료</span><strong>{{ selectedPresent }}명</strong><small>전체 {{ selectedTraining.participants.length }}명 중</small></div><div class="panel detail-card"><span>출석률</span><strong>{{ selectedRate }}%</strong><div class="progress"><span :style="{ width: `${selectedRate}%` }"></span></div></div></div><section class="panel"><div class="panel-header"><div><h3>출석 확인</h3><p>참석 여부를 직접 변경하거나 참여자 화면에서 출석할 수 있습니다.</p></div><span class="small-tag">출석 코드 {{ selectedTraining.code }}</span></div><div class="table-wrap"><table><thead><tr><th>이름</th><th>부서</th><th>상태</th><th>관리</th></tr></thead><tbody><tr v-for="person in selectedTraining.participants" :key="person.id"><td class="name-cell">{{ person.name }}</td><td>{{ person.department }}</td><td><span class="badge" :class="person.attended ? 'success' : 'neutral'">{{ person.attended ? '참석' : '미참석' }}</span></td><td><button class="table-action" @click="toggleAttendance(person)">{{ person.attended ? '출석 취소' : '출석 확인' }}</button></td></tr></tbody></table><div v-if="!selectedTraining.participants.length" class="empty-state">등록된 대상자가 없습니다.</div></div></section></template>
          <template v-else><div class="report-layout"><section class="panel report-sheet"><div class="report-topline"><span>hello,HRD</span><span>EDUCATION REPORT</span></div><h2>교육 결과 보고서</h2><p class="report-subtitle">{{ selectedTraining.title }}</p><div class="report-meta"><div><span>교육 일시</span><b>{{ formatDate(selectedTraining.date) }} {{ selectedTraining.time }}</b></div><div><span>교육 장소</span><b>{{ selectedTraining.location }}</b></div><div><span>교육 유형</span><b>{{ selectedTraining.category }}</b></div></div><div class="report-stats"><div><span>교육 대상</span><strong>{{ selectedTraining.participants.length }}<small>명</small></strong></div><div><span>참석</span><strong>{{ selectedPresent }}<small>명</small></strong></div><div><span>미참석</span><strong>{{ selectedTraining.participants.length - selectedPresent }}<small>명</small></strong></div><div><span>출석률</span><strong>{{ selectedRate }}<small>%</small></strong></div></div><h3>참석 결과</h3><div class="table-wrap"><table><thead><tr><th>이름</th><th>부서</th><th>결과</th></tr></thead><tbody><tr v-for="person in selectedTraining.participants" :key="person.id"><td>{{ person.name }}</td><td>{{ person.department }}</td><td>{{ person.attended ? '참석' : '미참석' }}</td></tr></tbody></table></div></section><aside class="panel report-actions"><span class="stat-icon blue">▧</span><h3>보고서 출력</h3><p>현재 출석 기록을 기준으로 결과를 정리합니다. 인쇄 창에서 PDF로 저장할 수 있습니다.</p><button class="primary-button" @click="printReport">보고서 인쇄 / PDF 저장</button><small>데모 데이터는 현재 브라우저에만 저장됩니다.</small></aside></div></template>
        </template>
      </div>
    </main>

    <div v-else class="participant-page"><header class="participant-header"><div class="brand"><span class="brand-mark">✦</span><span>hello<span class="brand-comma">,</span>HRD</span></div><button class="mode-link" @click="mode = 'admin'">관리자 화면으로 →</button></header><div class="phone-shell"><div class="phone-status">9:41 <span>●●● ▰</span></div><div v-if="attendeeStep === 'list'" class="phone-content"><div class="mobile-greeting"><span class="eyebrow">MY EDUCATION</span><h1>내 교육</h1><p>참여할 교육을 선택해 주세요.</p></div><div class="mobile-tabs"><span class="active">전체</span><span>진행 예정</span><span>출석 확인</span></div><h2>교육 목록 <small>{{ trainings.length }}</small></h2><div v-for="item in trainings" :key="item.id" class="mobile-training-card"><span class="type-chip">{{ item.category }}</span><h3>{{ item.title }}</h3><p>◷ {{ formatDate(item.date) }} {{ item.time }}</p><p>⌖ {{ item.location }}</p><button class="primary-button" @click="startCheckIn(item.id)">출석하기 →</button></div><div v-if="!trainings.length" class="empty-state">등록된 교육이 없습니다.</div></div><div v-else-if="attendeeStep === 'checkin'" class="phone-content"><button class="back-button" @click="attendeeStep = 'list'">← 교육 목록</button><span class="eyebrow">CHECK IN</span><h1>출석 확인</h1><p class="mobile-intro">교육 대상자 이름과 출석 코드를 입력해 주세요.</p><div class="mobile-training-card selected"><span class="type-chip">{{ attendeeTraining?.category }}</span><h3>{{ attendeeTraining?.title }}</h3><p>◷ {{ formatDate(attendeeTraining?.date) }} {{ attendeeTraining?.time }}</p><p>⌖ {{ attendeeTraining?.location }}</p></div><form class="mobile-form" @submit.prevent="checkIn"><label>이름<input v-model="attendee.name" required placeholder="등록된 이름을 입력하세요"></label><label>4자리 출석 코드<input v-model="attendee.code" required maxlength="4" inputmode="numeric" placeholder="교육 담당자에게 코드를 확인하세요"></label><p v-if="attendeeError" class="error-message" role="alert">{{ attendeeError }}</p><button class="primary-button" type="submit">출석 확인</button></form></div><div v-else class="phone-content completion"><div class="completion-check">✓</div><h1>출석이 완료되었습니다!</h1><p>{{ attendee.name }}님의 출석이 확인되었어요.<br>오늘도 좋은 배움이 되길 바랍니다.</p><div class="mobile-training-card selected"><span class="type-chip">출석 완료</span><h3>{{ attendeeTraining?.title }}</h3><p>◷ {{ formatDate(attendeeTraining?.date) }} {{ attendeeTraining?.time }}</p><p>⌖ {{ attendeeTraining?.location }}</p></div><button class="outline-button" @click="attendeeStep = 'list'">교육 목록으로</button></div><div class="phone-bottom"><span>⌂<small>홈</small></span><span class="active">▤<small>내 교육</small></span><span>✓<small>출석 내역</small></span></div></div><p class="participant-caption">교육 참여자 화면 · 모바일 크기로 미리보기</p></div>
  </div>
</template>
