import { ref } from 'vue'
import { request, writeRequest } from '../api/trainings'

export const user = ref(null)
export const authReady = ref(false)
export const authError = ref('')
const expiredMessage = '로그인 시간이 만료되었습니다. 다시 로그인해 주세요.'
let expiryTimer
let expiresAt = 0
let version = 0
let refreshing = null
let signingOut = false
let lastRefresh = 0
let refreshInterval = 30000
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
  lastRefresh = Date.now()
  refreshInterval = Math.min(30000, remaining / 4)
  expiryTimer = setTimeout(() => clearAuth(expiredMessage), remaining)
  if (user.value?.id !== data.user.id) user.value = data.user
  authError.value = ''
}

export async function restoreSession() {
  if (refreshing) await refreshing
  if (signingOut) return
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
  signingOut = true
  version++
  try {
    // Let an already-started renewal finish before deleting the shared cookie.
    if (refreshing) await refreshing
    await writeRequest('/api/accounts/logout/', 'POST')
    clearAuth()
    channel?.postMessage('changed')
  } finally {
    signingOut = false
  }
}

async function activity(event) {
  if (signingOut || event?.isTrusted === false || document.visibilityState === 'hidden' || !user.value) return
  if (Date.now() >= expiresAt) {
    clearAuth(expiredMessage)
    return
  }
  if (refreshing || Date.now() - lastRefresh < refreshInterval) return
  lastRefresh = Date.now()
  const currentVersion = version
  refreshing = (async () => {
    try {
      const data = await writeRequest('/api/accounts/refresh/', 'POST', {})
      if (currentVersion !== version) return
      acceptSession(data)
      channel?.postMessage('renewed')
    } catch (error) {
      if (error.status === 401 && currentVersion === version) clearAuth(expiredMessage)
      // Temporary network errors do not extend the existing expiry timer.
    } finally {
      refreshing = null
    }
  })()
  await refreshing
}

for (const event of ['pointerdown', 'pointermove', 'keydown', 'scroll']) {
  document.addEventListener(event, activity, { passive: true })
}
window.addEventListener('auth-activity', () => activity())

window.addEventListener('session-expired', () => clearAuth(expiredMessage))
function resume() {
  if (document.visibilityState === 'hidden') return
  if (expiresAt && Date.now() >= expiresAt) clearAuth(expiredMessage)
  if (authReady.value) restoreSession()
}
window.addEventListener('focus', resume)
document.addEventListener('visibilitychange', resume)
if (channel) channel.onmessage = (event) => {
  if (event.data !== 'renewed') clearAuth()
  restoreSession()
}
