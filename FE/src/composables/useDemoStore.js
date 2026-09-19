import { computed, ref, watch } from 'vue'
import { countAttended, percentage } from '../utils/attendance'
import {
  fetchTrainings,
  checkInRequest,
  setAttendanceRequest,
  createTrainingRequest,
  updateTrainingRequest,
  deleteTrainingRequest,
  createParticipantRequest,
  updateParticipantRequest,
  deleteParticipantRequest,
  uploadParticipantsRequest,
} from '../api/trainings'

const linkedTrainingId = Number(new URLSearchParams(window.location.search).get('training')) || null

export const trainings = ref([])
export const loading = ref(false)
export const saving = ref(false)
export const uploading = ref(false)
export const apiError = ref('')
export const section = ref('dashboard')
export const mode = ref(linkedTrainingId ? 'participant' : 'admin')
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
const emptyParticipant = () => ({ employee_number: '', name: '', department: '' })
export const newParticipant = ref(emptyParticipant())
export const editingParticipantId = ref(null)
export const attendee = ref({ trainingId: linkedTrainingId, name: '', employee_number: '', code: '', signature: [] })
export const attendeeStep = ref(linkedTrainingId ? 'checkin' : 'list')
export const checkingIn = ref(false)
export const attendeeError = ref('')

watch(selectedId, () => cancelParticipantEdit())

export const selectedTraining = computed(() => trainings.value.find((item) => item.id === selectedId.value) ?? trainings.value[0])
export const attendeeTraining = computed(() => trainings.value.find((item) => item.id === attendee.value.trainingId))
export const totalParticipants = computed(() => trainings.value.reduce((sum, item) => sum + item.participants.length, 0))
export const totalAttended = computed(() => trainings.value.reduce((sum, item) => sum + countAttended(item.participants), 0))
export const attendanceRate = computed(() => percentage(totalAttended.value, totalParticipants.value))
export const filteredTrainings = computed(() => {
  const query = search.value.toLowerCase()
  return trainings.value.filter((item) => item.title.toLowerCase().includes(query))
})
export const selectedPresent = computed(() => countAttended(selectedTraining.value?.participants))
export const selectedRate = computed(() => percentage(selectedPresent.value, selectedTraining.value?.participants.length))
export const chartValues = computed(() => trainings.value.slice(0, 5).map((item) => ({
  label: item.title.length > 8 ? `${item.title.slice(0, 8)}…` : item.title,
  value: percentage(countAttended(item.participants), item.participants.length),
})))

const dateFormatter = new Intl.DateTimeFormat('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })

export function formatDate(value) {
  if (!value) return '일정 미정'
  return dateFormatter.format(new Date(`${value}T12:00:00`))
}

export async function loadTrainings() {
  loading.value = true
  apiError.value = ''
  try {
    trainings.value = await fetchTrainings()
    if (!trainings.value.some((item) => item.id === selectedId.value)) {
      selectedId.value = trainings.value[0]?.id ?? null
    }
    if (!attendee.value.trainingId) {
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

async function withSaving(action) {
  saving.value = true
  apiError.value = ''
  try {
    await action()
  } catch (error) {
    apiError.value = error.message
  } finally {
    saving.value = false
  }
}

export async function saveTraining() {
  if (!newTraining.value.title.trim() || !newTraining.value.date || !newTraining.value.time) return
  await withSaving(async () => {
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
  })
}

export async function removeTraining(training) {
  const hasParticipants = training.participants.length || training.participant_count
  const warning = hasParticipants
    ? '교육을 삭제하면 연결된 대상자와 출석 기록도 삭제됩니다. 계속할까요?'
    : '이 교육을 삭제할까요?'
  if (!window.confirm(warning)) return
  await withSaving(async () => {
    await deleteTrainingRequest(training.id)
    trainings.value = trainings.value.filter((item) => item.id !== training.id)
    if (selectedId.value === training.id) selectedId.value = trainings.value[0]?.id ?? null
    if (attendee.value.trainingId === training.id) attendee.value.trainingId = trainings.value[0]?.id ?? null
    if (editingId.value === training.id) cancelTrainingForm()
    notice.value = '교육을 삭제했습니다.'
  })
}

export function startEditParticipant(person) {
  editingParticipantId.value = person.id
  newParticipant.value = {
    employee_number: person.employee_number,
    name: person.name,
    department: person.department,
  }
  notice.value = ''
}

export function cancelParticipantEdit() {
  editingParticipantId.value = null
  newParticipant.value = emptyParticipant()
}

export async function saveParticipant() {
  if (!selectedTraining.value) return
  await withSaving(async () => {
    if (editingParticipantId.value) {
      await updateParticipantRequest(
        selectedTraining.value.id, editingParticipantId.value, newParticipant.value
      )
      notice.value = '대상자 정보를 수정했습니다.'
    } else {
      const person = await createParticipantRequest(selectedTraining.value.id, newParticipant.value)
      notice.value = selectedTraining.value.participants.some((item) => item.id === person.id)
        ? '이미 이 교육에 등록된 사번입니다.'
        : '대상자를 등록했습니다.'
    }
    cancelParticipantEdit()
    await loadTrainings()
  })
}

export async function removeParticipant(person) {
  if (!selectedTraining.value) return
  if (!window.confirm(`${person.name}님을 이 교육의 대상자 명단에서 삭제할까요? 연결된 출석 기록도 삭제됩니다.`)) return
  await withSaving(async () => {
    await deleteParticipantRequest(selectedTraining.value.id, person.id)
    if (editingParticipantId.value === person.id) cancelParticipantEdit()
    await loadTrainings()
    notice.value = '이 교육의 대상자 명단에서 삭제했습니다.'
  })
}

export async function uploadParticipants(file) {
  if (!selectedTraining.value || !file) return false
  uploading.value = true
  apiError.value = ''
  try {
    const result = await uploadParticipantsRequest(selectedTraining.value.id, file)
    selectedTraining.value.participants = result.participants
    selectedTraining.value.participant_count = result.participants.length
    notice.value = `${result.added}명 등록, ${result.skipped}명 중복 건너뜀`
    return true
  } catch (error) {
    apiError.value = error.message
    return false
  } finally {
    uploading.value = false
  }
}

export async function toggleAttendance(person) {
  if (saving.value) return
  await withSaving(async () => {
    Object.assign(person, await setAttendanceRequest(person.id, !person.attended))
  })
}

export function startCheckIn(trainingId) {
  attendee.value = { trainingId, name: '', employee_number: '', code: '', signature: [] }
  attendeeError.value = ''
  attendeeStep.value = 'checkin'
}

export async function checkIn() {
  if (checkingIn.value || !attendeeTraining.value) return
  checkingIn.value = true
  attendeeError.value = ''
  try {
    const person = await checkInRequest(attendeeTraining.value.id, attendee.value)
    const index = attendeeTraining.value.participants.findIndex((item) => item.id === person.id)
    if (index !== -1) attendeeTraining.value.participants[index] = person
    attendeeStep.value = 'done'
  } catch (error) {
    attendeeError.value = error.message
  } finally {
    checkingIn.value = false
  }
}

loadTrainings()
