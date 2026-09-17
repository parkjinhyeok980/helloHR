<script setup>
import { section, openSection } from '../composables/useDemoStore'

</script>

<template>
    <aside class="sidebar">
      <div class="brand"><span class="brand-mark">✦</span><span>hello<span class="brand-comma">,</span>HRD<small>EDUCATION OPERATIONS</small></span></div>
      <div class="workspace-label">WORKSPACE</div>
      <nav class="side-nav" aria-label="주 메뉴">
        <button :class="{ active: section === 'dashboard' }" @click="openSection('dashboard')"><span>▦</span> 대시보드</button>
        <button :class="{ active: section === 'trainings' }" @click="openSection('trainings')"><span>▤</span> 교육 관리</button>
        <button :class="{ active: section === 'participants' }" @click="openSection('participants')"><span>♧</span> 대상자 관리</button>
        <button :class="{ active: section === 'attendance' }" @click="openSection('attendance')"><span>✓</span> 출석 관리</button>
        <button :class="{ active: section === 'reports' }" @click="openSection('reports')"><span>▧</span> 결과 보고서</button>
      </nav>
      <div class="sidebar-bottom"><span class="status-dot"></span> 교육·대상자 서버 저장 <small>출석 데모는 브라우저에 저장됩니다</small></div>
    </aside>
</template>
