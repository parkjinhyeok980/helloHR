<script setup>
import { ref } from 'vue'
import { authenticate, authError } from '../composables/useAuth'

const signup = ref(false)
const email = ref('')
const name = ref('')
const password = ref('')
const confirmation = ref('')
const remember = ref(false)
const visible = ref(false)
const busy = ref(false)
const enteringGuest = ref(false)
const error = ref('')
try {
  email.value = localStorage.getItem('hellohr_saved_email') || ''
  remember.value = Boolean(email.value)
} catch { /* Storage may be disabled in this browser. */ }

function switchForm() {
  signup.value = !signup.value
  error.value = ''
  password.value = ''
  confirmation.value = ''
}

async function startGuest() {
  if (busy.value) return
  busy.value = true
  enteringGuest.value = true
  error.value = ''
  try {
    await authenticate('guest', {})
    if (new URLSearchParams(window.location.search).has('training')) window.location.replace('/')
  } catch (err) {
    error.value = err.message
  } finally {
    busy.value = false
    enteringGuest.value = false
  }
}

async function submit() {
  error.value = ''
  if (signup.value && password.value !== confirmation.value) {
    error.value = '비밀번호가 일치하지 않습니다.'
    return
  }
  busy.value = true
  try {
    await authenticate(signup.value ? 'signup' : 'login', {
      email: email.value.trim(), password: password.value, name: name.value.trim(),
    })
    try {
      if (remember.value) localStorage.setItem('hellohr_saved_email', email.value.trim())
      else localStorage.removeItem('hellohr_saved_email')
    } catch { /* Login still works without local storage. */ }
    password.value = ''
    if (new URLSearchParams(window.location.search).has('training')) window.location.replace('/')
  } catch (err) {
    error.value = err.message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <div class="auth-decoration auth-decoration-one" aria-hidden="true"></div>
    <div class="auth-decoration auth-decoration-two" aria-hidden="true"></div>
    <section class="auth-card" aria-labelledby="auth-heading">
      <header class="auth-heading">
        <span class="auth-brand-icon" aria-hidden="true">✦</span>
        <p class="auth-brand">hello, HRD</p>
        <h1 id="auth-heading">{{ signup ? '새로운 배움의 시작' : '다시 만나 반가워요!' }}</h1>
        <p>{{ signup ? '나만의 교육 관리 공간을 만들어 보세요.' : '로그인하고 우리 팀의 교육을 관리하세요.' }}</p>
      </header>
      <form class="auth-form" @submit.prevent="submit">
        <fieldset :disabled="busy">
          <label v-if="signup" for="auth-name">이름
            <input id="auth-name" v-model="name" autocomplete="name" maxlength="100" required placeholder="이름을 입력해 주세요">
          </label>
          <label for="auth-email">이메일
            <input id="auth-email" v-model="email" type="email" autocomplete="username" maxlength="254" required placeholder="example@company.com">
          </label>
          <label for="auth-password">비밀번호</label>
          <div class="auth-password">
            <input id="auth-password" v-model="password" :type="visible ? 'text' : 'password'" :autocomplete="signup ? 'new-password' : 'current-password'" :minlength="signup ? 8 : undefined" maxlength="128" required placeholder="비밀번호를 입력해 주세요">
            <button type="button" :aria-pressed="visible" @click="visible = !visible">{{ visible ? '숨기기' : '보기' }}</button>
          </div>
          <template v-if="signup">
            <p class="auth-hint">8자 이상, 개인정보나 흔한 단어·숫자만으로 구성하지 마세요.</p>
            <label for="auth-confirm">비밀번호 확인
              <input id="auth-confirm" v-model="confirmation" type="password" autocomplete="new-password" maxlength="128" required placeholder="비밀번호를 한 번 더 입력해 주세요">
            </label>
          </template>
          <label class="auth-remember"><input v-model="remember" type="checkbox"> 이메일 저장</label>
          <p v-if="error || authError" class="auth-error" role="alert">{{ error || authError }}</p>
          <button class="auth-submit" type="submit" :disabled="busy">{{ busy ? '처리 중…' : signup ? '회원가입' : '로그인' }} <span aria-hidden="true">→</span></button>
        </fieldset>
      </form>
      <button class="auth-guest" type="button" :disabled="busy" @click="startGuest">
        {{ enteringGuest ? '게스트로 접속 중…' : '게스트 계정으로 시작하기' }}
      </button>
      <p class="auth-guest-hint">회원가입 없이 시작해 보세요. 게스트의 교육 데이터는 함께 공유됩니다.</p>
      <div class="auth-footer">
        <span>{{ signup ? '이미 계정이 있으신가요?' : '아직 계정이 없으신가요?' }}</span>
        <button type="button" :disabled="busy" @click="switchForm">{{ signup ? '로그인' : '회원가입' }}</button>
      </div>
      <p class="auth-caption">교육 준비부터 출석, 결과 보고까지 한 곳에서.</p>
    </section>
    <p class="auth-copyright">hello, HRD · 함께 성장하는 우리 팀</p>
  </main>
</template>

<style scoped>
.auth-guest{width:100%;min-height:48px;margin-top:12px;padding:10px 14px;border:1px solid #d9c9fc;border-radius:12px;background:#f8f5ff;color:#7132f5;font-size:14px;font-weight:700}.auth-guest:hover:not(:disabled){background:#eee6ff}.auth-guest-hint{margin:9px 0 0;text-align:center;font-size:11px;line-height:1.6;color:#827b8c}
.auth-page{min-height:100dvh;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:48px 20px;background:linear-gradient(120deg,#5941d8 0%,#8050ed 48%,#40b9c1 100%);position:relative;overflow:hidden}
.auth-decoration{position:absolute;border:1px solid #ffffff20;border-radius:50%;pointer-events:none;width:580px;height:580px}.auth-decoration-one{top:-300px;right:-180px}.auth-decoration-two{bottom:-360px;left:-180px;width:720px;height:720px}
.auth-card{position:relative;width:460px;max-width:100%;padding:40px 42px 30px;border:1px solid #ffffff99;border-radius:24px;background:#fff;box-shadow:0 24px 70px #29205c30}
.auth-heading{text-align:center}.auth-brand-icon{display:grid;place-items:center;width:44px;height:44px;margin:0 auto 14px;border-radius:14px;background:#f0eafd;color:#7132f5;font-size:28px}.auth-brand{font-size:34px;font-weight:800;letter-spacing:-1.7px;line-height:1.2;background:linear-gradient(90deg,#7132f5,#2caaa9);background-clip:text;color:transparent;margin:0 0 22px}.auth-heading h1{font-size:22px;letter-spacing:-.6px;margin:0 0 8px}.auth-heading>p:last-child{color:#737184;font-size:13px;margin:0 0 30px}
.auth-form fieldset{padding:0;margin:0;border:0;min-width:0}.auth-form label{display:block;font-size:13px;font-weight:600;color:#343044;margin-bottom:8px}.auth-form input:not([type=checkbox]){display:block;width:100%;height:48px;margin:8px 0 18px;padding:0 14px;border:1px solid #dcd9e5;border-radius:12px;background:#fff;font-size:13px;color:#242130;outline:none}.auth-form input:focus{border-color:#7132f5;box-shadow:0 0 0 3px #7132f516}.auth-form input::placeholder{color:#a09baa}.auth-password{position:relative}.auth-password input{padding-right:65px!important}.auth-password button{position:absolute;right:10px;top:12px;background:none;border:0;color:#716a80;font-size:12px;padding:3px 6px}.auth-form .auth-remember{display:flex;align-items:center;gap:7px;font-size:12px;font-weight:400;color:#777082;margin:4px 0 22px}.auth-remember input{accent-color:#7132f5;width:15px;height:15px;margin:0}.auth-hint{font-size:11px;color:#777082;margin-top:-8px}.auth-error{color:#b32f4a;font-size:12px;line-height:1.7;background:#fff1f3;padding:10px 12px;border-radius:8px}.auth-submit{width:100%;height:48px;display:flex;align-items:center;justify-content:center;gap:12px;background:#7132f5;color:#fff;border:0;border-radius:12px;font-size:14px;font-weight:700}.auth-submit:hover{background:#6025dc}.auth-footer{display:flex;align-items:center;justify-content:center;gap:9px;margin:23px 0;font-size:12px;color:#827b8c}.auth-footer button{border:0;background:none;color:#7132f5;font-size:13px;font-weight:700;padding:4px}.auth-caption{border-top:1px solid #efedf3;padding-top:20px;margin:0;text-align:center;color:#938c9e;font-size:11px}.auth-copyright{position:relative;margin:24px 0 0;color:#ffffffe0;font-size:11px;letter-spacing:.3px}
@media(max-width:480px){.auth-page{padding:24px 16px}.auth-card{padding:30px 24px 24px}.auth-brand{font-size:30px}.auth-heading h1{font-size:20px}}
</style>
