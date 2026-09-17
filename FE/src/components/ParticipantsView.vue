<script setup>
import { ref } from 'vue'
import {
  selectedTraining, newParticipant, editingParticipantId, saveParticipant,
  startEditParticipant, cancelParticipantEdit, removeParticipant,
  uploadParticipants, saving, uploading, formatDate,
} from '../composables/useDemoStore'

const selectedFile = ref(null)
const fileInput = ref(null)

function chooseFile(event) {
  selectedFile.value = event.target.files?.[0] ?? null
}

async function submitFile() {
  if (!selectedFile.value) return
  const succeeded = await uploadParticipants(selectedFile.value)
  if (succeeded) {
    selectedFile.value = null
    if (fileInput.value) fileInput.value.value = ''
  }
}
</script>

<template>
  <div class="detail-grid">
    <div class="panel detail-card">
      <span>교육 일정</span>
      <strong>{{ formatDate(selectedTraining.date) }}</strong>
      <small>{{ selectedTraining.time }} · {{ selectedTraining.location }}</small>
    </div>
    <div class="panel detail-card">
      <span>등록 대상자</span>
      <strong>{{ selectedTraining.participants.length }}명</strong>
      <small>이 교육에 연결된 대상자</small>
    </div>
    <div class="panel detail-card">
      <span>출석 코드</span>
      <strong>{{ selectedTraining.code }}</strong>
      <small>참여자 화면에서 입력</small>
    </div>
  </div>

  <section class="panel participant-panel">
    <div class="panel-header">
      <div>
        <h3>{{ editingParticipantId ? '대상자 정보 수정' : '대상자 한 명씩 등록' }}</h3>
        <p>사번을 기준으로 중복 등록을 방지합니다. 사원 정보 수정은 다른 교육 명단에도 반영됩니다.</p>
      </div>
    </div>
    <form class="inline-form" @submit.prevent="saveParticipant">
      <input v-model="newParticipant.employee_number" required maxlength="50" placeholder="사번" aria-label="사번">
      <input v-model="newParticipant.name" required maxlength="100" placeholder="이름" aria-label="이름">
      <input v-model="newParticipant.department" required maxlength="100" placeholder="부서" aria-label="부서">
      <button v-if="editingParticipantId" class="outline-button" type="button" :disabled="saving" @click="cancelParticipantEdit">취소</button>
      <button class="primary-button" type="submit" :disabled="saving">{{ saving ? '저장 중...' : editingParticipantId ? '수정 저장' : '＋ 대상자 추가' }}</button>
    </form>
  </section>

  <section class="panel participant-panel">
    <div class="panel-header">
      <div>
        <h3>엑셀 명부 업로드</h3>
        <p>첫 행에 <b>사번 · 이름 · 부서</b> 열이 있는 .xlsx 파일을 업로드하세요. 기존 사번은 건너뜁니다.</p>
      </div>
      <a class="text-button template-link" href="/api/participants/template/" download>양식 다운로드 ↓</a>
    </div>
    <form class="upload-form" @submit.prevent="submitFile">
      <input ref="fileInput" type="file" accept=".xlsx" aria-label="대상자 엑셀 파일" @change="chooseFile">
      <button class="primary-button" type="submit" :disabled="uploading || !selectedFile">{{ uploading ? '업로드 중...' : '엑셀 업로드' }}</button>
    </form>
    <p class="upload-help">최대 5MB · 한 번에 1,000명 · 잘못된 행이 있으면 전체 업로드를 취소합니다.</p>
  </section>

  <section class="panel">
    <div class="panel-header">
      <div><h3>대상자 명단 <span class="count-pill">{{ selectedTraining.participants.length }}</span></h3></div>
    </div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>사번</th><th>이름</th><th>부서</th><th>출석</th><th>관리</th></tr></thead>
        <tbody>
          <tr v-for="person in selectedTraining.participants" :key="person.id">
            <td>{{ person.employee_number }}</td>
            <td class="name-cell">{{ person.name }}</td>
            <td>{{ person.department }}</td>
            <td><span class="badge" :class="person.attended ? 'success' : 'neutral'">{{ person.attended ? '참석' : '미참석' }}</span></td>
            <td class="participant-actions">
              <button class="table-action" type="button" :disabled="saving" :aria-label="`${person.name} 수정`" @click="startEditParticipant(person)">수정</button>
              <button class="table-action danger" type="button" :disabled="saving" :aria-label="`${person.name} 삭제`" @click="removeParticipant(person)">삭제</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!selectedTraining.participants.length" class="empty-state">등록된 대상자가 없습니다.</div>
    </div>
  </section>
</template>
