const baseUrl = '/api/trainings/'

function csrfCookie() {
  return document.cookie.split('; ').find((part) => part.startsWith('csrftoken='))?.split('=')[1] ?? ''
}

async function request(url, options = {}) {
  const response = await fetch(url, { credentials: 'same-origin', ...options })
  if (response.status === 204) return null
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const message = Object.values(data.errors ?? {})[0] ?? data.detail ?? '요청을 처리하지 못했습니다.'
    throw new Error(message)
  }
  return data
}

async function writeRequest(url, method, payload) {
  await request('/api/csrf/')
  return request(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfCookie(),
    },
    ...(payload ? { body: JSON.stringify(payload) } : {}),
  })
}

export async function fetchTrainings() {
  const data = await request(baseUrl)
  return data.results
}

export const createTrainingRequest = (payload) => writeRequest(baseUrl, 'POST', payload)
export const updateTrainingRequest = (id, payload) => writeRequest(`${baseUrl}${id}/`, 'PUT', payload)
export const deleteTrainingRequest = (id) => writeRequest(`${baseUrl}${id}/`, 'DELETE')
export const fetchTrainingReport = (id) => request(`${baseUrl}${id}/report/`, { cache: 'no-store' })
export const checkInRequest = (id, payload) => writeRequest(`${baseUrl}${id}/check-in/`, 'POST', payload)
export const setAttendanceRequest = (id, attended) => writeRequest(`/api/participants/${id}/attendance/`, 'POST', { attended })

export const createParticipantRequest = (trainingId, payload) =>
  writeRequest(`${baseUrl}${trainingId}/participants/`, 'POST', payload)

export const updateParticipantRequest = (trainingId, participantId, payload) =>
  writeRequest(`${baseUrl}${trainingId}/participants/${participantId}/`, 'PUT', payload)

export const deleteParticipantRequest = (trainingId, participantId) =>
  writeRequest(`${baseUrl}${trainingId}/participants/${participantId}/`, 'DELETE')

export async function uploadParticipantsRequest(trainingId, file) {
  await request('/api/csrf/')
  const body = new FormData()
  body.append('file', file)
  return request(`${baseUrl}${trainingId}/participants/upload/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': csrfCookie() },
    body,
  })
}
