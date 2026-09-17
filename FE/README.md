# hello,HRD 프런트엔드

Vue 3와 Vite로 만든 교육 운영 MVP 화면입니다. `docsimg`의 관리자 화면과 모바일 참여자 흐름을 참고했습니다.

## 실행

프로젝트 루트에서 Django 서버를 먼저 실행합니다.

```powershell
.\venv\Scripts\Activate.ps1
cd BE
python manage.py migrate
python manage.py runserver
```

별도 터미널에서 프런트엔드를 실행합니다.

```bash
cd FE
npm ci
npm run dev
```

## 데모 흐름

1. 교육 관리에서 교육을 만듭니다.
2. 대상자 관리에서 이름과 부서를 등록합니다.
3. 출석 관리에서 참석 여부를 확인하거나, 상단의 **참여자 화면 보기**에서 이름과 교육별 4자리 출석 코드를 입력합니다.
4. 결과 보고서에서 참석/미참석 현황을 확인하고 인쇄 창에서 PDF로 저장합니다.

교육 목록과 교육의 등록·수정·삭제는 Django API와 SQLite에 저장됩니다. 대상자와 출석 데이터는 아직 브라우저 `localStorage`에만 저장되므로 다른 브라우저와 공유되지 않습니다. QR 출석과 전자서명도 아직 연결되지 않았습니다.
