<script setup>
import { computed, ref, watch } from 'vue'
import QRCode from 'qrcode'

const props = defineProps({ training: { type: Object, required: true } })
const qr = ref('')
const message = ref('')
const error = ref('')
const link = computed(() => {
  const url = new URL('/', window.location.origin)
  url.searchParams.set('training', props.training.id)
  return url.href
})
const isLocal = ['localhost', '127.0.0.1', '[::1]'].includes(window.location.hostname)
watch(link, async (url, _, onCleanup) => {
  let cancelled = false
  onCleanup(() => { cancelled = true })
  qr.value = ''
  error.value = ''
  message.value = ''
  try {
    const data = await QRCode.toDataURL(url, { width: 320, margin: 4, errorCorrectionLevel: 'M' })
    if (!cancelled) qr.value = data
  } catch {
    if (!cancelled) error.value = 'QR을 생성하지 못했습니다. 참여 링크를 이용해 주세요.'
  }
}, { immediate: true })
async function copyLink() {
  try {
    await navigator.clipboard.writeText(link.value)
    message.value = '참여 링크를 복사했습니다.'
  } catch {
    message.value = '아래 참여 링크를 직접 선택해 복사해 주세요.'
  }
}
</script>

<template>
  <section class="panel training-access" aria-label="출석 번호 및 QR">
    <div class="access-details">
      <span class="eyebrow">CHECK-IN</span>
      <h3>출석 번호 & QR</h3>
      <p>QR을 스캔하면 이 교육의 출석·서명 화면으로 연결됩니다.</p>
      <strong class="attendance-code" aria-label="출석 번호">{{ training.code }}</strong>
      <div class="access-actions">
        <button class="outline-button" @click="copyLink">참여 링크 복사</button>
        <a v-if="qr" class="outline-button" :href="qr" :download="`training-${training.id}-qr.png`">QR 이미지 저장</a>
        <a class="text-button" :href="link" target="_blank" rel="noopener">참여 화면 열기 ↗</a>
      </div>
      <input class="access-link" :value="link" readonly aria-label="교육 참여 링크" @focus="$event.target.select()">
      <p v-if="message" role="status">{{ message }}</p>
      <p v-if="isLocal" class="access-hint">현재 QR은 이 컴퓨터의 로컬 주소입니다. 휴대폰 공유용 QR은 배포 사이트에서 저장해 주세요.</p>
    </div>
    <div class="access-qr"><img v-if="qr" :src="qr" :alt="`${training.title} 출석 참여 QR`" width="160" height="160"><p v-else role="status">{{ error || 'QR 생성 중…' }}</p><small>카메라로 스캔해 주세요</small></div>
  </section>
</template>
