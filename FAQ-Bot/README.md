# 커널아카데미 FAQ 봇 🤖

슬랙에서 사용할 수 있는 FAQ 봇입니다.

## 설치 및 설정

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 슬랙 앱 설정

#### Bot Token Scopes (필수)
슬랙 API에서 다음 권한들을 설정해주세요:
- `app_mentions:read`
- `channels:read`
- `chat:write`
- `commands`
- `im:history`
- `im:read`
- `im:write`
- `users:read`

#### Socket Mode 설정
- Socket Mode를 활성화하고 App-Level Token을 생성하세요.

### 3. 환경 변수 설정
`.env` 파일을 생성하고 다음을 입력하세요:
```
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
```

### 4. 봇 실행
```bash
python main.py
```

## 사용 방법

1. 슬랙 채널에서 `@봇이름`을 멘션합니다.
2. 과정(AI/BDA)을 선택합니다.
3. 궁금한 질문을 선택합니다.
4. FAQ 답변을 확인합니다.

## 파일 구조
```
FAQ-Bot/
├── main.py                    # 메인 봇 코드
├── data/
│   └── attendance-faq.json    # FAQ 데이터
├── requirements.txt           # 패키지 의존성
├── env.example               # 환경 변수 예시
└── README.md                 # 이 파일
```

## 테스트 채널
`#faq-bot-test` 채널에서 테스트할 수 있습니다. 