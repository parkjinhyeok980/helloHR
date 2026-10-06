import { ref } from 'vue'
import { request, writeRequest } from '../api/trainings'

export const user = ref(null)
export const authReady = ref(false)
export const authError = ref('')

export async function restoreSession() {
  authError.value = ''
  try {
    user.value = (await request('/api/accounts/session/', { cache: 'no-store' })).user
  } catch {
    authError.value = '서버에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요.'
  } finally {
    authReady.value = true
  }
}

export async function authenticate(kind, payload) {
  user.value = (await writeRequest(`/api/accounts/${kind}/`, 'POST', payload)).user
  authError.value = ''
}

export async function logout() {
  await writeRequest('/api/accounts/logout/', 'POST')
  user.value = null
}

window.addEventListener('session-expired', () => { user.value = null })
