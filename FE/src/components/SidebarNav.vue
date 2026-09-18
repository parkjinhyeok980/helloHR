<script setup>
import { section, openSection } from '../composables/useDemoStore'

</script>

<template>
    <aside class="sidebar">
      <button type="button" class="brand brand-home" aria-label="hello HRD 대시보드로 이동" @click="openSection('dashboard')"><span class="brand-mark" aria-hidden="true">✦</span><span>hello HRD<small>EDUCATION OPERATIONS</small></span></button>
      <div class="workspace-label">WORKSPACE</div>
      <nav class="side-nav" aria-label="주 메뉴">
        <button :class="{ active: section === 'dashboard' }" :aria-current="section === 'dashboard' ? 'page' : undefined" @click="openSection('dashboard')"><span>▦</span> 대시보드</button>
        <button :class="{ active: section === 'trainings' }" :aria-current="section === 'trainings' ? 'page' : undefined" @click="openSection('trainings')"><span class="nav-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m2 9 10-5 10 5-10 5L2 9Z"/><path d="M6 11v6c3 3 9 3 12 0v-6M22 9v7"/></svg></span> 교육 관리</button>
        <button :class="{ active: section === 'participants' }" :aria-current="section === 'participants' ? 'page' : undefined" @click="openSection('participants')"><span class="nav-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21v-2a8 8 0 0 1 16 0v2"/></svg></span> 대상자 관리</button>
        <button :class="{ active: section === 'reports' }" :aria-current="section === 'reports' ? 'page' : undefined" @click="openSection('reports')"><span class="nav-icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M14 3H5v18h14V8l-5-5Z"/><path d="M14 3v5h5M8 12h8M8 16h8"/></svg></span> 결과 보고서</button>
      </nav>
    </aside>
</template>

<style scoped>
.nav-icon { display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; }
.nav-icon svg { display: block; width: 1em; height: 1em; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
.brand-home { appearance: none; border: 0; background: transparent; text-align: left; }
.brand-home:focus-visible { outline: 2px solid var(--brand); outline-offset: 4px; border-radius: 8px; }
</style>
