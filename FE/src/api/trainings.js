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
