<script setup>
import { ref } from 'vue'
import { authenticate } from '../composables/useAuth'
import PublicLayout from './PublicLayout.vue'

const busy = ref(false)
const error = ref('')
async function startGuest() {
  if (busy.value) return
  busy.value = true
  error.value = ''
  try { await authenticate('guest', {}) }
  catch (err) { error.value = err.message }
  finally { busy.value = false }
}
</script>

<template>
  <PublicLayout>
    <main class="landing-main">
      <section class="landing-intro" aria-labelledby="landing-heading">
        <span class="eyebrow">A BETTER WAY TO LEARN, TOGETHER</span>
        <h1 id="landing-heading">교육 운영의 모든 과정,<br><span>한 곳에서 간편하게.</span></h1>
        <p class="landing-description">교육 준비부터 출석 확인, 결과 보고까지.<br>반복되는 업무는 줄이고, 우리 팀의 배움에 집중하세요.</p>
        <div class="landing-workflow" aria-label="교육 운영 과정">
          <div><span class="workflow-number">01</span><strong>교육 준비</strong><p>일정과 대상자 등록</p></div>
          <span class="workflow-arrow" aria-hidden="true">→</span>
          <div><span class="workflow-number">02</span><strong>출석 확인</strong><p>QR 출석과 전자서명</p></div>
          <span class="workflow-arrow" aria-hidden="true">→</span>
          <div><span class="workflow-number">03</span><strong>결과 보고</strong><p>교육 현황을 한눈에</p></div>
        </div>
        <p class="landing-note"><span aria-hidden="true">✓</span> 내 계정에서 관리하는 우리 팀의 교육 현황</p>
      </section>
      <section class="landing-actions panel" aria-labelledby="start-heading">
        <span class="start-icon" aria-hidden="true">✦</span>
        <h2 id="start-heading">더 가벼운 교육 운영,<br>지금 시작해 보세요.</h2>
        <p>hello HRD가 처음이신가요?<br>우리 팀만의 교육 관리 공간을 만들어 보세요.</p>
        <a class="primary-button start-button" href="#/signup">회원가입 <span aria-hidden="true">→</span></a>
        <a class="outline-button start-button" href="#/login">로그인</a>
        <div class="start-divider"><span>먼저 둘러보고 싶다면</span></div>
        <button class="start-guest" :disabled="busy" @click="startGuest">{{ busy ? '게스트로 접속 중…' : '게스트 계정으로 시작하기' }} <span aria-hidden="true">↗</span></button>
        <p class="guest-note">가입 없이 체험할 수 있어요.<br>게스트의 교육 데이터는 함께 공유됩니다.</p>
        <p v-if="error" class="error-notice notice" role="alert">{{ error }}</p>
      </section>
    </main>
  </PublicLayout>
</template>

<style scoped>
.landing-main{flex:1;display:grid;grid-template-columns:minmax(0,1fr) 360px;align-items:center;gap:72px;width:min(1200px,100%);margin:0 auto;padding:64px 40px 88px}
.landing-intro .eyebrow{font-size:11px;letter-spacing:2px}.landing-intro h1{font-size:48px;font-weight:700;line-height:1.25;letter-spacing:-1.5px;margin:24px 0}.landing-intro h1>span{color:var(--brand)}
.landing-description{color:var(--muted);font-size:16px;line-height:1.85;margin:0}.landing-workflow{display:flex;align-items:center;gap:20px;padding:28px 0;margin-top:36px;border-top:1px solid var(--border);border-bottom:1px solid var(--border)}.landing-workflow>div{flex:1}.workflow-number{display:block;color:var(--brand);font-size:12px;font-weight:600;margin-bottom:12px}.landing-workflow strong{font-size:16px;font-weight:600}.landing-workflow p{margin:6px 0 0;font-size:12px;color:var(--muted);white-space:nowrap}.workflow-arrow{color:var(--border);font-size:20px}.landing-note{display:flex;gap:8px;font-size:12px;color:var(--muted);margin:20px 0 0}.landing-note span{color:var(--success)}
.landing-actions{padding:32px;background:var(--surface);border-radius:var(--card-radius)}.start-icon{display:grid;place-items:center;width:48px;height:48px;border-radius:12px;background:var(--brand-subtle);color:var(--brand);font-size:28px;margin-bottom:24px}.landing-actions h2{font-size:24px;font-weight:700;line-height:1.4;letter-spacing:-.5px;margin:0 0 14px}.landing-actions>p{font-size:13px;line-height:1.7;color:var(--muted);margin-bottom:28px}.start-button{display:flex;align-items:center;justify-content:center;gap:14px;width:100%;min-height:48px;text-decoration:none;font-size:16px;margin-top:12px}.start-divider{display:flex;align-items:center;gap:12px;margin:28px 0 18px;color:var(--muted);font-size:11px}.start-divider::before,.start-divider::after{content:'';height:1px;flex:1;background:var(--border)}.start-guest{display:flex;align-items:center;justify-content:center;gap:10px;width:100%;min-height:44px;background:var(--brand-subtle);color:var(--brand-deep);border:0;font-size:13px;font-weight:600;border-radius:var(--button-radius)}.start-guest:hover{background:var(--border)}.landing-actions .guest-note{font-size:11px;text-align:center;margin:12px 0 0}.landing-actions .error-notice{margin:16px 0 0;color:var(--error)}
@media(max-width:1024px){.landing-main{gap:40px;grid-template-columns:minmax(0,1fr) 320px}.landing-intro h1{font-size:36px}.landing-workflow{gap:12px}.landing-actions{padding:24px}}
@media(max-width:768px){.landing-main{grid-template-columns:1fr;padding:32px 24px 48px;gap:40px;max-width:600px}.landing-intro h1{font-size:36px}.landing-actions{width:100%;padding:28px}.landing-workflow{margin-top:28px}.landing-description{font-size:14px}}
@media(max-width:375px){.landing-intro h1{font-size:30px}.landing-intro .eyebrow{font-size:9px}.landing-workflow{gap:8px}.landing-workflow p{font-size:10px}.landing-workflow strong{font-size:14px}}
</style>
