import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import vm from 'node:vm'

// Run the actual composable with deterministic browser/network/clock boundaries.
function harness() {
  let now = 0
  let nextId = 0
  let response = { user: { id: 1, name: 'Guest' }, server_time: 100, expires_at: 160 }
  const timers = new Map()
  const events = {}
  const documentEvents = {}
  const writes = []
  const context = {
    ref: value => ({ value }),
    request: async () => response,
    writeRequest: async (url) => { writes.push(url); return response },
    Date: { now: () => now },
    setTimeout: (callback, delay) => { timers.set(++nextId, { callback, at: now + delay }); return nextId },
    clearTimeout: id => timers.delete(id),
    window: { addEventListener: (name, callback) => { events[name] = callback } },
    document: { visibilityState: 'visible', addEventListener: (name, callback) => { documentEvents[name] = callback } },
  }
  const source = readFileSync(new URL('../src/composables/useAuth.js', import.meta.url), 'utf8')
    .replace(/^import .*$/gm, '').replace(/export /g, '')
  vm.runInNewContext(source + '\nglobalThis.auth = { user, authError, authenticate, restoreSession, logout };', context)
  return {
    auth: context.auth, events, documentEvents, writes,
    response: value => { response = value },
    advance: (ms, fire = true) => {
      now += ms
      if (fire) for (const [id, timer] of [...timers]) if (timer.at <= now) {
        timers.delete(id); timer.callback()
      }
    },
  }
}

test('expires automatically without making another API request', async () => {
  const h = harness()
  await h.auth.authenticate('guest', {})
  h.advance(59999)
  assert.equal(h.auth.user.value.id, 1)
  h.advance(1)
  assert.equal(h.auth.user.value, null)
  assert.ok(h.auth.authError.value.includes('만료'))
})

test('restoring an existing JWT does not extend its expiry', async () => {
  const h = harness()
  await h.auth.authenticate('guest', {})
  h.advance(30000)
  h.response({ user: { id: 1 }, server_time: 130, expires_at: 160 })
  await h.auth.restoreSession()
  h.advance(30000)
  assert.equal(h.auth.user.value, null)
})

test('returning to a suspended tab expires immediately', async () => {
  const h = harness()
  await h.auth.authenticate('guest', {})
  h.advance(61000, false)
  h.documentEvents.visibilitychange()
  assert.equal(h.auth.user.value, null)
})

test('manual logout cancels old expiry notification', async () => {
  const h = harness()
  await h.auth.authenticate('guest', {})
  await h.auth.logout()
  h.advance(61000)
  assert.equal(h.auth.user.value, null)
  assert.equal(h.auth.authError.value, '')
})

test('user activity renews the token and keeps the page signed in', async () => {
  const h = harness()
  await h.auth.authenticate('guest', {})
  h.advance(20000)
  h.response({ user: { id: 1 }, server_time: 120, expires_at: 180 })
  await h.documentEvents.keydown()
  assert.equal(h.writes.at(-1), '/api/accounts/refresh/')
  h.advance(40000)
  assert.equal(h.auth.user.value.id, 1)
  h.advance(20000)
  assert.equal(h.auth.user.value, null)
})

test('activity bursts are throttled and background tabs do not run a heartbeat', async () => {
  const h = harness()
  await h.auth.authenticate('guest', {})
  h.advance(20000)
  h.response({ user: { id: 1 }, server_time: 120, expires_at: 180 })
  await h.documentEvents.pointermove()
  await h.documentEvents.pointermove()
  await h.documentEvents.keydown()
  assert.equal(h.writes.filter(url => url.endsWith('/refresh/')).length, 1)
  h.advance(60000)
  assert.equal(h.auth.user.value, null)
  assert.equal(h.writes.filter(url => url.endsWith('/refresh/')).length, 1)
})

test('expired activity cannot restore authentication', async () => {
  const h = harness()
  await h.auth.authenticate('guest', {})
  h.advance(61000, false)
  await h.documentEvents.keydown()
  assert.equal(h.auth.user.value, null)
  assert.equal(h.writes.filter(url => url.endsWith('/refresh/')).length, 0)
})
