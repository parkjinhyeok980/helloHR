import { computed, ref, watch } from 'vue'

const storageKey = 'hellohr-demo-v1'
const dateAfter = (days) => {
  const date = new Date()
  date.setDate(date.getDate() + days)
  return date.toISOString().slice(0, 10)
}

const sampleTrainings = [
  {
    id: 1, title: '2026 하반기 산업안전보건교육', category: '법정 필수',
    date: dateAfter(2), time: '10:00', location: '본관 3층 대회의실', code: '1234',
    participants: [
      { id: 101, name: '김민수', department: '인사팀', attended: true },
      { id: 102, name: '이지은', department: '마케팅팀', attended: true },
      { id: 103, name: '박현우', department: '개발팀', attended: false },
      { id: 104, name: '최수빈', department: '경영지원팀', attended: false },
      { id: 105, name: '정하늘', department: '디자인팀', attended: true },
    ],
  },
  {
    id: 2, title: '직장 내 괴롭힘 예방교육', category: '법정 필수',
    date: dateAfter(7), time: '14:00', location: '온라인 교육', code: '5678',
    participants: [
      { id: 201, name: '김민수', department: '인사팀', attended: false },
      { id: 202, name: '이지은', department: '마케팅팀', attended: false },
    ],
  },
  {
    id: 3, title: '정보보안 기본 교육', category: '사내 교육',
    date: dateAfter(-5), time: '15:00', location: '별관 교육장', code: '9012',
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

export const trainings = ref(loadTrainings())
export const section = ref('dashboard')
export const mode = ref('admin')
export const selectedId = ref(trainings.value[0]?.id ?? null)
export const showCreateForm = ref(false)
export const search = ref('')
export const notice = ref('')
export const today = new Date().toISOString().slice(0, 10)
export const newTraining = ref({ title: '', category: '법정 필수', date: today, time: '10:00', location: '' })
export const newParticipant = ref({ name: '', department: '' })
export const attendee = ref({ trainingId: trainings.value[0]?.id ?? null, name: '', code: '' })
export const attendeeStep = ref('list')
export const attendeeError = ref('')

watch(trainings, (value) => localStorage.setItem(storageKey, JSON.stringify(value)), { deep: true })

export const selectedTraining = computed(() => trainings.value.find((item) => item.id === selectedId.value) ?? trainings.value[0])
export const attendeeTraining = computed(() => trainings.value.find((item) => item.id === attendee.value.trainingId))
export const totalParticipants = computed(() => trainings.value.reduce((sum, item) => sum + item.participants.length, 0))
export const totalAttended = computed(() => trainings.value.reduce((sum, item) => sum + item.participants.filter((person) => person.attended).length, 0))
export const attendanceRate = computed(() => totalParticipants.value ? Math.round(totalAttended.value / totalParticipants.value * 100) : 0)
export const filteredTrainings = computed(() => trainings.value.filter((item) => item.title.toLowerCase().includes(search.value.toLowerCase())))
export const selectedPresent = computed(() => selectedTraining.value?.participants.filter((person) => person.attended).length ?? 0)
export const selectedRate = computed(() => selectedTraining.value?.participants.length ? Math.round(selectedPresent.value / selectedTraining.value.participants.length * 100) : 0)
export const chartValues = computed(() => trainings.value.slice(0, 5).map((item) => ({
  label: item.title.length > 8 ? `${item.title.slice(0, 8)}…` : item.title,
  value: item.participants.length ? Math.round(item.participants.filter((person) => person.attended).length / item.participants.length * 100) : 0,
})))

export function formatDate(value) {
  if (!value) return '일정 미정'
  return new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' }).format(new Date(`${value}T12:00:00`))
}

export function openSection(next) {
  section.value = next
  showCreateForm.value = false
  notice.value = ''
}

export function selectTraining(id, next = 'trainings') {
  selectedId.value = id
  openSection(next)
}

export function createTraining() {
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

export function addParticipant() {
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

export function toggleAttendance(person) {
  person.attended = !person.attended
  notice.value = `${person.name}님의 출석을 ${person.attended ? '확인' : '취소'}했습니다.`
}

export function startCheckIn(trainingId) {
  attendee.value = { trainingId, name: '', code: '' }
  attendeeError.value = ''
  attendeeStep.value = 'checkin'
}

export function checkIn() {
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
