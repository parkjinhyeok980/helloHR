<script setup>
import { trainings, totalParticipants, totalAttended, attendanceRate, chartValues, formatDate, openSection, selectTraining, showCreateForm } from '../composables/useDemoStore'

</script>

<template>
          <div class="page-heading"><div><span class="eyebrow">OVERVIEW</span><h1>교육 운영 현황</h1><p>교육부터 출석, 결과까지 한눈에 확인하세요.</p></div><button class="primary-button" @click="openSection('trainings'); showCreateForm = true">＋ 새 교육 만들기</button></div>
          <div class="hero-card"><div><span class="hero-kicker">BETTER PEOPLE, BRIGHTER TOMORROW</span><h2>더 간편한 교육 운영,<br>더 정확한 출석 관리.</h2><p>오늘의 교육 현황을 확인하고 다음 업무를 시작하세요.</p><button @click="openSection('trainings')">교육 목록 보기 <span>→</span></button></div><div class="hero-art" aria-hidden="true"><div class="hero-circle circle-one"></div><div class="hero-circle circle-two"></div><div class="floating-note"><span>✓</span><div><b>출석 확인 완료</b><small>교육 운영을 한 곳에서</small></div></div></div></div>
          <div class="stats-grid">
            <div class="stat-card"><span class="stat-icon blue">▤</span><span class="stat-label">전체 교육</span><strong>{{ trainings.length }}<small>건</small></strong><span class="stat-foot">등록된 교육 과정</span></div>
            <div class="stat-card"><span class="stat-icon mint">♧</span><span class="stat-label">등록 대상자</span><strong>{{ totalParticipants }}<small>명</small></strong><span class="stat-foot">전체 교육 기준</span></div>
            <div class="stat-card"><span class="stat-icon amber">✓</span><span class="stat-label">출석 완료</span><strong>{{ totalAttended }}<small>명</small></strong><span class="stat-foot">확인된 출석 기록</span></div>
            <div class="stat-card"><span class="stat-icon violet">◔</span><span class="stat-label">전체 출석률</span><strong>{{ attendanceRate }}<small>%</small></strong><span class="stat-foot">등록 대상자 대비</span></div>
          </div>
          <div class="dashboard-grid">
            <section class="panel"><div class="panel-header"><div><h3>교육별 출석률</h3><p>교육별 등록 대상자 대비 출석 현황</p></div><span class="small-tag">LIVE</span></div><div v-if="chartValues.length" class="chart"><div v-for="(bar, index) in chartValues" :key="index" class="chart-column"><div class="chart-track"><div class="chart-fill" :style="{ height: `${Math.max(bar.value, 3)}%` }"><span>{{ bar.value }}%</span></div></div><span class="chart-label">{{ bar.label }}</span></div></div><div v-else class="empty-state">등록된 교육이 없습니다.</div></section>
            <section class="panel"><div class="panel-header"><div><h3>최근 교육</h3><p>교육 일정과 진행 상태를 확인하세요</p></div><button class="text-button" @click="openSection('trainings')">전체 보기 →</button></div><div class="recent-list"><button v-for="item in trainings.slice(0, 4)" :key="item.id" class="recent-item" @click="selectTraining(item.id)"><span class="recent-icon">▤</span><span><b>{{ item.title }}</b><small>{{ formatDate(item.date) }} · {{ item.participants.length }}명 대상</small></span><span class="chevron">›</span></button><div v-if="!trainings.length" class="empty-state">아직 교육이 없습니다.</div></div></section>
          </div>
</template>
