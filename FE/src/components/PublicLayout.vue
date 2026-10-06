<template>
  <div class="public-layout">
    <header class="public-header">
      <a href="#/" class="brand public-brand" aria-label="hello HRD 시작페이지">
        <span class="brand-mark" aria-hidden="true">✦</span>
        <span>hello HRD<small>EDUCATION OPERATIONS</small></span>
      </a>
      <a class="public-header-link" href="#/login">로그인 <span aria-hidden="true">↗</span></a>
    </header>
    <slot />
    <footer class="public-footer"><span>hello HRD</span><span>함께 배우고, 더 나은 내일로.</span></footer>
  </div>
</template>

<style scoped>
.public-layout{min-height:100dvh;display:flex;flex-direction:column;background:var(--surface);color:var(--ink)}
.public-header{height:96px;flex:none;display:flex;justify-content:space-between;align-items:center;width:min(1200px,100%);margin:0 auto;padding:0 40px}
.public-brand{text-decoration:none}.public-brand small{color:var(--muted)}
.public-header-link{color:var(--muted);text-decoration:none;font-size:14px;font-weight:500;display:flex;gap:12px;align-items:center}.public-header-link:hover{color:var(--brand)}
.public-footer{display:flex;justify-content:space-between;gap:16px;width:min(1120px,calc(100% - 80px));margin:0 auto;border-top:1px solid var(--border);padding:24px 0;color:var(--muted);font-size:12px}.public-footer>span:first-child{font-weight:600;color:var(--ink)}
@media(max-width:640px){.public-header{height:80px;padding:0 24px}.public-brand{font-size:20px}.public-header-link{font-size:13px}.public-footer{width:calc(100% - 48px);font-size:11px}}
</style>
