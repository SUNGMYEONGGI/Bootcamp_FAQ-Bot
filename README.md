# 🤖 커널아카데미 부트캠프 FAQ 봇

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Slack](https://img.shields.io/badge/Slack-Bot-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)

*커널아카데미 부트캠프 수강생들을 위한 스마트 FAQ 챗봇*

</div>

---

## 🎯 개요

**커널아카데미 부트캠프 FAQ 봇**은 AI 과정과 BDA 과정 수강생들이 자주 묻는 질문들에 대해 즉시 답변을 제공하는 Slack 기반 챗봇입니다. 

---

## 📊 프로젝트 정보

| 항목 | 내용 |
|------|------|
| **프로젝트명** | 커널아카데미 부트캠프 FAQ 봇 |
| **개발 기간** | 2025년 1월 |
| **개발 언어** | Python 3.8+ |
| **주요 프레임워크** | Slack Bolt SDK |
| **배포 환경** | Socket Mode (개발), HTTP Mode (운영) |
| **데이터 소스** | JSON 기반 FAQ 데이터베이스 |

### 🌐 배포 주소
- **개발 환경**: Socket Mode를 통한 로컬 개발
- **운영 환경**: Slack 워크스페이스 내 봇 설치
- **테스트 채널**: `#faq-bot-test`

---

## 🚀 시작 가이드

### 📋 사전 요구사항
- Python 3.8 이상
- Slack 워크스페이스 관리자 권한
- Git

### 1️⃣ 프로젝트 클론
```bash
git clone https://github.com/SUNGMYEONGGI/Bootcamp_FAQ-Bot.git
cd Bootcamp_FAQ-Bot
```

### 2️⃣ 가상환경 설정 (권장)
```bash
python -m venv qabot-venv
source qabot-venv/bin/activate  # Linux/Mac
# qabot-venv\Scripts\activate  # Windows
```

### 3️⃣ 패키지 설치
```bash
pip install -r requirements.txt
```

### 4️⃣ Slack 앱 설정

#### Bot Token Scopes (필수)
Slack API에서 다음 권한들을 설정하세요:
- `app_mentions:read` - 봇 멘션 읽기
- `channels:read` - 채널 정보 읽기
- `chat:write` - 메시지 쓰기
- `commands` - 슬래시 명령어 사용
- `im:history` - DM 히스토리 읽기
- `im:read` - DM 읽기
- `im:write` - DM 쓰기
- `users:read` - 사용자 정보 읽기

#### Socket Mode 설정
- Socket Mode를 활성화하고 App-Level Token을 생성하세요.

### 5️⃣ 환경 변수 설정
`.env` 파일을 생성하고 다음을 입력하세요:
```env
# Case 1 봇용 (간단한 2단계 버전)
SLACK_BOT_TOKEN1=xoxb-your-bot-token-here
SLACK_APP_TOKEN1=xapp-your-app-token-here

# Case 2 봇용 (3단계 상세 버전)
SLACK_BOT_TOKEN2=xoxb-your-bot-token-here
SLACK_APP_TOKEN2=xapp-your-app-token-here
```

### 6️⃣ 봇 실행
```bash
# Case 1: 간단한 버전 (과정 선택 → 전체 질문 노출)
python main_case1.py

# Case 2: 상세한 버전 (과정 선택 → 카테고리 선택 → 질문 선택)
python main_case2.py
```

---

## 🛠 기술 스택

### Backend
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Slack](https://img.shields.io/badge/Slack_Bolt-4A154B?style=for-the-badge&logo=slack&logoColor=white)

### Data Storage
![JSON](https://img.shields.io/badge/JSON-000000?style=for-the-badge&logo=json&logoColor=white)

### Development Tools
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![VS Code](https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)

### Dependencies
```json
{
  "slack-bolt": "^1.18.0",
  "python-dotenv": "^1.0.0",
  "logging": "Python Built-in"
}
```

---

## ✨ 주요 기능

### 🎯 Core Features

#### 1. 이중 모드 지원
- **Case 1**: 과정 선택 → 모든 질문 직접 노출 (2단계)
- **Case 2**: 과정 선택 → 카테고리 선택 → 질문 선택 (3단계)

#### 2. 다중 과정 지원
- 🧠 **AI 과정**: 인공지능 및 머신러닝 부트캠프
- 📊 **BDA 과정**: 빅데이터 분석 부트캠프

#### 3. 포괄적 FAQ 카테고리
- 📋 **출석 관련**: QR 체크, 지각/조퇴/결석 처리
- 🏫 **실시간 강의**: Zoom 설정, 강의 자료 접근
- 💻 **온라인 강의**: mOTP 인증, 수강 진도 관리
- 📚 **과정 외**: 프로젝트, 특강, 행정 문의

#### 4. 사용자 친화적 인터페이스
- 🎨 카테고리별 이모지 아이콘
- 🔄 네비게이션 버튼 (뒤로가기, 처음으로)
- 📱 Slack Block Kit 기반 인터랙티브 UI

#### 5. 스마트 답변 시스템
- 📄 구조화된 답변 포맷
- 📌 단계별 안내 정보
- ✅ 체크리스트 형태 답변

### 🔧 Technical Features
- 🔒 **보안**: 환경 변수 기반 토큰 관리
- 📊 **로깅**: 사용자 행동 추적 및 디버깅
- 🔄 **에러 핸들링**: 파일 로드 실패 시 graceful handling
- 🎛 **확장성**: 모듈화된 FAQ 데이터 구조

---

## 🏗 아키텍처

### 데이터 플로우
1. **사용자 입력**: Slack에서 봇 멘션
2. **이벤트 처리**: Slack Bolt가 이벤트 수신
3. **데이터 로드**: JSON 파일에서 FAQ 데이터 로드
4. **필터링**: 선택된 과정에 맞는 데이터 추출
5. **UI 생성**: Block Kit을 사용한 인터랙티브 버튼 생성
6. **응답 반환**: 구조화된 답변을 Slack으로 전송

### 클래스 다이어그램
```
📦 FAQ Bot System
 ┣ 📂 Event Handlers
 ┃ ┣ 🎯 handle_mention()
 ┃ ┣ 🎯 handle_course_selection()
 ┃ ┣ 🎯 handle_category_selection() [Case 2 only]
 ┃ ┗ 🎯 handle_question_selection()
 ┣ 📂 Data Management
 ┃ ┣ 📄 load_faq_data()
 ┃ ┗ 📄 format_answer()
 ┗ 📂 UI Components
   ┣ 🎨 create_course_blocks()
   ┣ 🎨 create_category_blocks() [Case 2 only]
   ┣ 🎨 create_question_blocks()
   ┗ 🎨 create_answer_blocks()
```

---

## 📁 파일 구조

```
Bootcamp_FAQ-Bot/
├── 📁 data/                          # FAQ 데이터베이스
│   ├── 📄 attendance-faq.json        # 출석 관련 FAQ (814 라인)
│   ├── 📄 live-lecture-faq.json      # 실시간 강의 FAQ (481 라인)
│   ├── 📄 online-lecture-faq.json    # 온라인 강의 FAQ (146 라인)
│   └── 📄 cource-etc-faq.json        # 과정 외 FAQ (269 라인)
├── 📁 logs/                          # 로그 파일 저장소
├── 🤖 main_case1.py                  # 간단 버전 봇 (2단계)
├── 🤖 main_case2.py                  # 상세 버전 봇 (3단계)
├── 📊 log.py                         # 로깅 유틸리티
├── 📋 requirements.txt               # Python 패키지 의존성
├── 🔒 .env                          # 환경 변수 (git ignore)
├── 🔒 .gitignore                    # Git 제외 파일 설정
└── 📖 README.md                     # 프로젝트 문서 (이 파일)
```

### FAQ 데이터 구조
```json
{
  "question": "질문 내용",
  "category": "카테고리명",
  "answer": {
    "title": "답변 제목",
    "items": ["답변 항목 1", "답변 항목 2", "..."]
  },
  "course": "AI 과정" | "BDA 과정"
}
```

---

## 📖 사용 방법

### Case 1: 간단한 버전 (main_case1.py)
```
1. 봇 멘션 (@FAQ봇)
   ↓
2. 과정 선택 (AI/BDA)
   ↓
3. 질문 선택 (전체 질문 목록에서)
   ↓
4. 답변 확인
```

### Case 2: 상세한 버전 (main_case2.py)
```
1. 봇 멘션 (@FAQ봇)
   ↓
2. 과정 선택 (AI/BDA)
   ↓
3. 카테고리 선택 (출석/실시간강의/온라인강의/과정외)
   ↓
4. 질문 선택
   ↓
5. 답변 확인
```

### 실제 사용 예시

#### 🎯 시나리오 1: 출석 관련 질문
```
사용자: @FAQ봇
봇: 과정을 선택해주세요 [AI 과정] [BDA 과정]
사용자: [AI 과정] 클릭
봇: 카테고리를 선택해주세요 [📋 출석 관련] [🏫 실시간 강의] ...
사용자: [📋 출석 관련] 클릭
봇: 질문을 선택해주세요 [출석 체크는 어떻게...] [지각 기준이...] ...
사용자: [출석 체크는 어떻게...] 클릭
봇: [상세 답변 제공]
```

### 네비게이션 기능
- 🔄 **다른 질문 보기**: 같은 카테고리의 다른 질문들 확인
- 🏠 **처음으로 돌아가기**: 과정 선택 화면으로 복귀
- ◀️ **뒤로가기**: 이전 단계로 이동

---

## 📚 참고 문헌

### 공식 문서
- [Slack Bolt for Python](https://slack.dev/bolt-python/concepts) - Slack 봇 개발 프레임워크
- [Slack Block Kit](https://api.slack.com/block-kit) - 인터랙티브 UI 구성 요소
- [Slack Socket Mode](https://api.slack.com/apis/connections/socket) - 실시간 이벤트 처리

### 개발 참고 자료
- [Python 공식 문서](https://docs.python.org/3/) - Python 3.8+ 문법 및 표준 라이브러리
- [JSON 데이터 처리](https://docs.python.org/3/library/json.html) - FAQ 데이터베이스 구조 설계
- [dotenv 환경 변수 관리](https://pypi.org/project/python-dotenv/) - 보안 토큰 관리

### 디자인 참고
- [GitHub README 작성 가이드](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [Markdown 문법 가이드](https://www.markdownguide.org/) - 문서 포맷팅
- [Shields.io](https://shields.io/) - 배지 생성 도구

### 커널아카데미 관련
- [커널아카데미 공식 사이트](https://www.kernelacademy.co.kr/) - 부트캠프 과정 정보
- 내부 FAQ 데이터 - 수강생 대상 실제 질문/답변 수집

---

<div align="center">

**🤖 Made with ❤️ for Kernel Academy Bootcamp Students**

*이 프로젝트가 도움이 되셨다면 ⭐ Star를 눌러주세요!*

[⬆️ 맨 위로 이동](#-커널아카데미-부트캠프-faq-봇)

</div> 
