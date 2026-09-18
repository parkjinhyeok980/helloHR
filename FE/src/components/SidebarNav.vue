<script setup>
import { section, openSection } from '../composables/useDemoStore'

</script>

<template>
    <aside class="sidebar">
      <div class="brand"><span class="brand-mark">✦</span><span>hello HRD<small>EDUCATION OPERATIONS</small></span></div>
      <div class="workspace-label">WORKSPACE</div>
      <nav class="side-nav" aria-label="주 메뉴">
        <button :class="{ active: section === 'dashboard' }" :aria-current="section === 'dashboard' ? 'page' : undefined" @click="openSection('dashboard')"><span>▦</span> 대시보드</button>
        <button :class="{ active: section === 'trainings' }" :aria-current="section === 'trainings' ? 'page' : undefined" @click="openSection('trainings')"><span>▤</span> 교육 관리</button>
        <button :class="{ active: section === 'participants' }" :aria-current="section === 'participants' ? 'page' : undefined" @click="openSection('participants')"><span>♧</span> 대상자 관리</button>
        <button :class="{ active: section === 'attendance' }" :aria-current="section === 'attendance' ? 'page' : undefined" @click="openSection('attendance')"><span>✓</span> 출석 관리</button>
        <button :class="{ active: section === 'reports' }" :aria-current="section === 'reports' ? 'page' : undefined" @click="openSection('reports')"><span>▧</span> 결과 보고서</button>
      </nav>
    </aside>
</template>
