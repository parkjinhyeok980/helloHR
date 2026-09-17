<script setup>
import { selectedTraining, selectedPresent, selectedRate, toggleAttendance } from '../composables/useDemoStore'

</script>

<template>
<div class="detail-grid two"><div class="panel detail-card"><span>출석 완료</span><strong>{{ selectedPresent }}명</strong><small>전체 {{ selectedTraining.participants.length }}명 중</small></div><div class="panel detail-card"><span>출석률</span><strong>{{ selectedRate }}%</strong><div class="progress"><span :style="{ width: `${selectedRate}%` }"></span></div></div></div><section class="panel"><div class="panel-header"><div><h3>출석 확인</h3><p>참석 여부를 직접 변경하거나 참여자 화면에서 출석할 수 있습니다.</p></div><span class="small-tag">출석 코드 {{ selectedTraining.code }}</span></div><div class="table-wrap"><table><thead><tr><th>이름</th><th>부서</th><th>상태</th><th>관리</th></tr></thead><tbody><tr v-for="person in selectedTraining.participants" :key="person.id"><td class="name-cell">{{ person.name }}</td><td>{{ person.department }}</td><td><span class="badge" :class="person.attended ? 'success' : 'neutral'">{{ person.attended ? '참석' : '미참석' }}</span></td><td><button class="table-action" @click="toggleAttendance(person)">{{ person.attended ? '출석 취소' : '출석 확인' }}</button></td></tr></tbody></table><div v-if="!selectedTraining.participants.length" class="empty-state">등록된 대상자가 없습니다.</div></div></section>
</template>
