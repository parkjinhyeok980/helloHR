import { ref } from 'vue'
import { request, writeRequest } from '../api/trainings'

export const user = ref(null)
export const authReady = ref(false)
export const authError = ref('')
const expiredMessage = '로그인 시간이 만료되었습니다. 다시 로그인해 주세요.'
let expiryTimer
let expiresAt = 0
let version = 0
const channel = typeof BroadcastChannel === 'function' ? new BroadcastChannel('hellohr-auth') : null

function clearAuth(message = '') {
  version++
  clearTimeout(expiryTimer)
  expiresAt = 0
  user.value = null
  authError.value = message
}

function acceptSession(data) {
  clearTimeout(expiryTimer)
  if (!data.user) {
    clearAuth(user.value ? expiredMessage : authError.value)
    return
  }
  const remaining = (data.expires_at - data.server_time) * 1000
  if (!Number.isFinite(remaining) || remaining <= 0) {
    clearAuth(expiredMessage)
    return
  }
  expiresAt = Date.now() + remaining
  expiryTimer = setTimeout(() => clearAuth(expiredMessage), remaining)
  if (user.value?.id !== data.user.id) user.value = data.user
  authError.value = ''
}

export async function restoreSession() {
  const currentVersion = ++version
  try {
    const data = await request('/api/accounts/session/', { cache: 'no-store' })
    if (currentVersion === version) acceptSession(data)
  } catch (error) {
    if (currentVersion === version && error.status !== 401) {
      authError.value = '서버에 연결하지 못했습니다. 잠시 후 다시 시도해 주세요.'
    }
  } finally {
    authReady.value = true
  }
}

export async function authenticate(kind, payload) {
  const currentVersion = ++version
  const data = await writeRequest(`/api/accounts/${kind}/`, 'POST', payload)
  if (currentVersion !== version) return
  acceptSession(data)
  channel?.postMessage('changed')
}

export async function logout() {
  await writeRequest('/api/accounts/logout/', 'POST')
  clearAuth()
  channel?.postMessage('changed')
}

window.addEventListener('session-expired', () => clearAuth(expiredMessage))
function resume() {
  if (document.visibilityState === 'hidden') return
  if (expiresAt && Date.now() >= expiresAt) clearAuth(expiredMessage)
  if (authReady.value) restoreSession()
}
window.addEventListener('focus', resume)
document.addEventListener('visibilitychange', resume)
if (channel) channel.onmessage = () => {
  clearAuth()
  restoreSession()
}
