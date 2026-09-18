<script setup>
import { selectedTraining, selectedPresent, selectedRate, formatDate } from '../composables/useDemoStore'

function printReport() { window.print() }
</script>

<template>
<div class="report-layout"><section class="panel report-sheet"><div class="report-topline"><span>hello HRD</span><span>EDUCATION REPORT</span></div><h2>교육 결과 보고서</h2><p class="report-subtitle">{{ selectedTraining.title }}</p><div class="report-meta"><div><span>교육 일시</span><b>{{ formatDate(selectedTraining.date) }} {{ selectedTraining.time }}</b></div><div><span>교육 장소</span><b>{{ selectedTraining.location }}</b></div><div><span>교육 유형</span><b>{{ selectedTraining.category }}</b></div></div><div class="report-stats"><div><span>교육 대상</span><strong>{{ selectedTraining.participants.length }}<small>명</small></strong></div><div><span>참석</span><strong>{{ selectedPresent }}<small>명</small></strong></div><div><span>미참석</span><strong>{{ selectedTraining.participants.length - selectedPresent }}<small>명</small></strong></div><div><span>출석률</span><strong>{{ selectedRate }}<small>%</small></strong></div></div><h3>참석 결과</h3><div class="table-wrap"><table><thead><tr><th>이름</th><th>부서</th><th>결과</th></tr></thead><tbody><tr v-for="person in selectedTraining.participants" :key="person.id"><td>{{ person.name }}</td><td>{{ person.department }}</td><td>{{ person.attended ? '참석' : '미참석' }}</td></tr></tbody></table></div></section><aside class="panel report-actions"><span class="stat-icon blue">▧</span><h3>보고서 출력</h3><p>현재 출석 기록을 기준으로 결과를 정리합니다. 인쇄 창에서 PDF로 저장할 수 있습니다.</p><button class="primary-button" @click="printReport">보고서 인쇄 / PDF 저장</button></aside></div>
</template>
