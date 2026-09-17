<script setup>
import { selectedTraining, newParticipant, addParticipant, formatDate } from '../composables/useDemoStore'

</script>

<template>
<div class="detail-grid"><div class="panel detail-card"><span>교육 일정</span><strong>{{ formatDate(selectedTraining.date) }}</strong><small>{{ selectedTraining.time }} · {{ selectedTraining.location }}</small></div><div class="panel detail-card"><span>등록 대상자</span><strong>{{ selectedTraining.participants.length }}명</strong><small>이 교육에 연결된 대상자</small></div><div class="panel detail-card"><span>출석 코드</span><strong>{{ selectedTraining.code }}</strong><small>참여자 화면에서 입력</small></div></div><section class="panel"><div class="panel-header"><div><h3>대상자 명단</h3><p>이름과 부서를 입력해 교육 대상자를 추가하세요.</p></div></div><form class="inline-form" @submit.prevent="addParticipant"><input v-model="newParticipant.name" required placeholder="이름" aria-label="대상자 이름"><input v-model="newParticipant.department" placeholder="부서" aria-label="대상자 부서"><button class="primary-button" type="submit">＋ 대상자 추가</button></form><div class="table-wrap"><table><thead><tr><th>이름</th><th>부서</th><th>출석</th></tr></thead><tbody><tr v-for="person in selectedTraining.participants" :key="person.id"><td class="name-cell">{{ person.name }}</td><td>{{ person.department }}</td><td><span class="badge" :class="person.attended ? 'success' : 'neutral'">{{ person.attended ? '참석' : '미참석' }}</span></td></tr></tbody></table><div v-if="!selectedTraining.participants.length" class="empty-state">등록된 대상자가 없습니다.</div></div></section>
</template>
