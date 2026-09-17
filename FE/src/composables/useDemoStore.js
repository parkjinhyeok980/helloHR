import { computed, ref, watch } from 'vue'
import {
  fetchTrainings,
  createTrainingRequest,
  updateTrainingRequest,
  deleteTrainingRequest,
} from '../api/trainings'

const participantStorageKey = 'hellohr-demo-participants-v2'

function readLocalParticipants() {
  try {
    return JSON.parse(localStorage.getItem(participantStorageKey)) ?? {}
  } catch {
    return {}
  }
}

const withLocalParticipants = (training) => ({
  ...training,
  participants: readLocalParticipants()[training.id] ?? [],
})

export const trainings = ref([])
export const loading = ref(false)
export const saving = ref(false)
export const apiError = ref('')
export const section = ref('dashboard')
export const mode = ref('admin')
export const selectedId = ref(null)
export const showCreateForm = ref(false)
export const editingId = ref(null)
export const search = ref('')
export const notice = ref('')
export const today = new Date().toISOString().slice(0, 10)

const emptyTraining = () => ({
  title: '', description: '', category: '법정 필수', date: today, time: '10:00', location: '',
})

export const newTraining = ref(emptyTraining())
export const newParticipant = ref({ name: '', department: '' })
export const attendee = ref({ trainingId: null, name: '', code: '' })
export const attendeeStep = ref('list')
export const attendeeError = ref('')

watch(trainings, (value) => {
  const participants = Object.fromEntries(value.map((item) => [item.id, item.participants]))
  localStorage.setItem(participantStorageKey, JSON.stringify(participants))
}, { deep: true })

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

export async function loadTrainings() {
  loading.value = true
  apiError.value = ''
  try {
    trainings.value = (await fetchTrainings()).map(withLocalParticipants)
    if (!trainings.value.some((item) => item.id === selectedId.value)) {
      selectedId.value = trainings.value[0]?.id ?? null
    }
    if (!trainings.value.some((item) => item.id === attendee.value.trainingId)) {
      attendee.value.trainingId = trainings.value[0]?.id ?? null
    }
  } catch (error) {
    apiError.value = `교육 목록을 불러오지 못했습니다. Django 서버를 확인해 주세요. (${error.message})`
  } finally {
    loading.value = false
  }
}

export function openSection(next) {
  section.value = next
  showCreateForm.value = false
  editingId.value = null
  notice.value = ''
}

export function selectTraining(id, next = 'trainings') {
  selectedId.value = id
  openSection(next)
}

export function startCreateTraining() {
  editingId.value = null
  newTraining.value = emptyTraining()
  showCreateForm.value = true
}

export function startEditTraining(training) {
  editingId.value = training.id
  newTraining.value = {
    title: training.title,
    description: training.description ?? '',
    category: training.category,
    date: training.date,
    time: training.time,
    location: training.location,
  }
  showCreateForm.value = true
  notice.value = ''
}

export function cancelTrainingForm() {
  showCreateForm.value = false
  editingId.value = null
  newTraining.value = emptyTraining()
}

export async function saveTraining() {
  if (!newTraining.value.title.trim() || !newTraining.value.date || !newTraining.value.time) return
  saving.value = true
  apiError.value = ''
  try {
    if (editingId.value) {
      const updated = await updateTrainingRequest(editingId.value, newTraining.value)
      const index = trainings.value.findIndex((item) => item.id === updated.id)
      trainings.value[index] = { ...updated, participants: trainings.value[index].participants }
      notice.value = '교육 정보를 수정했습니다.'
    } else {
      const created = await createTrainingRequest(newTraining.value)
      trainings.value.unshift({ ...created, participants: [] })
      selectedId.value = created.id
      attendee.value.trainingId = created.id
      section.value = 'participants'
      notice.value = '교육을 만들었습니다. 이제 대상자를 등록해 주세요.'
    }
    cancelTrainingForm()
  } catch (error) {
    apiError.value = error.message
  } finally {
    saving.value = false
  }
}

export async function removeTraining(training) {
  const hasParticipants = training.participants.length || training.participant_count
  const warning = hasParticipants
    ? '교육을 삭제하면 연결된 대상자와 출석 기록도 삭제됩니다. 계속할까요?'
    : '이 교육을 삭제할까요?'
  if (!window.confirm(warning)) return
  saving.value = true
  apiError.value = ''
  try {
    await deleteTrainingRequest(training.id)
    trainings.value = trainings.value.filter((item) => item.id !== training.id)
    if (selectedId.value === training.id) selectedId.value = trainings.value[0]?.id ?? null
    if (attendee.value.trainingId === training.id) attendee.value.trainingId = trainings.value[0]?.id ?? null
    if (editingId.value === training.id) cancelTrainingForm()
    notice.value = '교육을 삭제했습니다.'
  } catch (error) {
    apiError.value = error.message
  } finally {
    saving.value = false
  }
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

loadTrainings()
