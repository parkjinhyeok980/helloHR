<script setup>
import { ref } from 'vue'

const props = defineProps({ modelValue: { type: Array, default: () => [] }, disabled: Boolean })
const emit = defineEmits(['update:modelValue'])
const surface = ref(null)
let activePointer = null
const points = (stroke) => stroke.map(([x, y]) => `${x * 600},${y * 240}`).join(' ')

function point(event) {
  const rect = surface.value.getBoundingClientRect()
  return [Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)),
    Math.max(0, Math.min(1, (event.clientY - rect.top) / rect.height))]
}
function begin(event) {
  if (props.disabled || activePointer !== null || event.button !== 0 || props.modelValue.length >= 100) return
  activePointer = event.pointerId
  surface.value.setPointerCapture(event.pointerId)
  emit('update:modelValue', [...props.modelValue, [point(event)]])
}
function move(event) {
  if (props.disabled || activePointer !== event.pointerId) return
  if (props.modelValue.reduce((sum, stroke) => sum + stroke.length, 0) >= 10000) return
  const strokes = props.modelValue.map((stroke) => [...stroke])
  strokes.at(-1).push(point(event))
  emit('update:modelValue', strokes)
}
function end(event) {
  if (activePointer === event.pointerId) activePointer = null
}
</script>

<template>
  <div class="signature-field">
    <div class="signature-heading"><span id="signature-label">전자서명 <span aria-hidden="true">*</span></span>
      <button type="button" class="text-button" :disabled="disabled" @click="emit('update:modelValue', [])">다시 쓰기</button>
    </div>
    <div class="signature-surface">
      <svg ref="surface" viewBox="0 0 600 240" preserveAspectRatio="none"
        role="img" aria-labelledby="signature-label" aria-describedby="signature-help"
        @pointerdown.prevent="begin" @pointermove.prevent="move" @pointerup="end"
        @pointercancel="end" @lostpointercapture="end">
        <polyline v-for="(stroke, index) in modelValue" :key="index" :points="points(stroke)"
          fill="none" stroke="#101114" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" vector-effect="non-scaling-stroke" />
      </svg>
      <span v-if="!modelValue.length" class="signature-placeholder">여기에 이름을 적어 주세요</span>
    </div>
    <p id="signature-help">손가락, 펜 또는 마우스로 서명해 주세요. 출석 확인 시 서명이 함께 저장됩니다.</p>
  </div>
</template>
