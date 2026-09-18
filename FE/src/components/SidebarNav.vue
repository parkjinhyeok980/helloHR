<script setup>
import { section, openSection } from '../composables/useDemoStore'

</script>

<template>
    <aside class="sidebar">
      <button type="button" class="brand brand-home" aria-label="hello HRD 대시보드로 이동" @click="openSection('dashboard')"><span class="brand-mark" aria-hidden="true">✦</span><span>hello HRD<small>EDUCATION OPERATIONS</small></span></button>
      <div class="workspace-label">WORKSPACE</div>
      <nav class="side-nav" aria-label="주 메뉴">
        <button :class="{ active: section === 'dashboard' }" :aria-current="section === 'dashboard' ? 'page' : undefined" @click="openSection('dashboard')"><span>▦</span> 대시보드</button>
        <button :class="{ active: section === 'trainings' }" :aria-current="section === 'trainings' ? 'page' : undefined" @click="openSection('trainings')"><span>▤</span> 교육 관리</button>
        <button :class="{ active: section === 'participants' }" :aria-current="section === 'participants' ? 'page' : undefined" @click="openSection('participants')"><span>♧</span> 대상자 관리</button>
        <button :class="{ active: section === 'reports' }" :aria-current="section === 'reports' ? 'page' : undefined" @click="openSection('reports')"><span>▧</span> 결과 보고서</button>
      </nav>
    </aside>
</template>

<style scoped>
.brand-home { appearance: none; border: 0; background: transparent; text-align: left; }
.brand-home:focus-visible { outline: 2px solid var(--brand); outline-offset: 4px; border-radius: 8px; }
</style>
