<script setup>
import { mode, trainings, attendeeStep, attendee, attendeeTraining, attendeeError, checkingIn, loading, apiError, loadTrainings, formatDate, startCheckIn, checkIn } from '../composables/useDemoStore'

import SignaturePad from './SignaturePad.vue'
</script>

<template>
  <div class="participant-page">
    <header class="participant-header">
      <div class="brand"><span class="brand-mark">✦</span><span>hello HRD</span></div>
      <button class="mode-link" @click="mode = 'admin'">관리자 화면으로 →</button>
    </header>
    <div class="phone-shell">
      <div class="phone-content">
        <div v-if="apiError" class="notice error-notice" role="alert">{{ apiError }}<button @click="loadTrainings">다시 시도</button></div>
        <p v-if="loading" role="status">교육 정보를 불러오는 중입니다…</p>
        <template v-else-if="attendeeStep === 'list'">
          <div class="mobile-greeting"><span class="eyebrow">MY EDUCATION</span><h1>내 교육</h1><p>참여할 교육을 선택해 주세요.</p></div>
          <h2>교육 목록 <small>{{ trainings.length }}</small></h2>
          <div v-for="item in trainings" :key="item.id" class="mobile-training-card">
            <span class="type-chip">{{ item.category }}</span><h3>{{ item.title }}</h3>
            <p>{{ formatDate(item.date) }} {{ item.time }}</p><p>{{ item.location }}</p>
            <button class="primary-button" @click="startCheckIn(item.id)">출석·서명하기 →</button>
          </div>
          <div v-if="!trainings.length" class="empty-state">등록된 교육이 없습니다.</div>
        </template>
        <template v-else-if="attendeeStep === 'checkin'">
          <button class="back-button" :disabled="checkingIn" @click="attendeeStep = 'list'">← 교육 목록</button>
          <template v-if="attendeeTraining">
            <span class="eyebrow">CHECK IN</span><h1>출석 및 전자서명</h1><p class="mobile-intro">본인 정보를 입력하고 이름을 서명해 주세요.</p>
            <div class="mobile-training-card selected"><span class="type-chip">{{ attendeeTraining.category }}</span><h3>{{ attendeeTraining.title }}</h3><p>{{ formatDate(attendeeTraining.date) }} {{ attendeeTraining.time }}</p><p>{{ attendeeTraining.location }}</p></div>
            <form class="mobile-form" @submit.prevent="checkIn">
              <fieldset :disabled="checkingIn">
                <label>이름<input v-model="attendee.name" required autocomplete="name" placeholder="등록된 이름"></label>
                <label>사번<input v-model="attendee.employee_number" required placeholder="등록된 사번"></label>
                <label>4자리 출석 번호<input v-model="attendee.code" required maxlength="4" pattern="[0-9]{4}" inputmode="numeric" placeholder="교육 담당자에게 확인해 주세요"></label>
                <SignaturePad v-model="attendee.signature" :disabled="checkingIn" />
                <p v-if="attendeeError" class="error-message" role="alert">{{ attendeeError }}</p>
                <button class="primary-button" type="submit" :disabled="checkingIn">{{ checkingIn ? '출석·서명 저장 중…' : '서명하고 출석 확인' }}</button>
              </fieldset>
            </form>
          </template>
          <p v-else class="empty-state">교육을 찾을 수 없습니다. 담당자에게 참여 링크를 다시 확인해 주세요.</p>
        </template>
        <div v-else class="completion">
          <div class="completion-check">✓</div><h1>출석이 완료되었습니다!</h1>
          <p>{{ attendee.name }}님의 출석과 서명이 저장되었습니다.<br>오늘도 좋은 배움이 되길 바랍니다.</p>
          <div class="mobile-training-card selected"><span class="type-chip">서명 완료</span><h3>{{ attendeeTraining?.title }}</h3><p>{{ formatDate(attendeeTraining?.date) }} {{ attendeeTraining?.time }}</p></div>
          <button class="outline-button" @click="attendeeStep = 'list'">교육 목록으로</button>
        </div>
      </div>
    </div>
  </div>
</template>
