import os
import json
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# Slack 앱 초기화
app = App(token=os.environ.get("SLACK_BOT_TOKEN2"))

# FAQ 데이터 로드 (4개 파일 통합)
def load_faq_data():
    """출석, 실시간 강의, 온라인 강의, 과정 외 FAQ 데이터를 모두 로드하여 통합"""
    all_faq_data = []
    
    # 파일 목록과 해당 설명
    faq_files = [
        ('data/attendance-faq.json', '출석 관련'),
        ('data/live-lecture-faq.json', '실시간 강의 관련'),
        ('data/online-lecture-faq.json', '온라인 강의 관련'),
        ('data/cource-etc-faq.json', '과정 외 관련')
    ]
    
    for file_path, description in faq_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                all_faq_data.extend(file_data)
                print(f"FAQ 데이터 로드 성공: {file_path} ({len(file_data)}개 항목)")
        except FileNotFoundError:
            print(f"FAQ 파일을 찾을 수 없습니다: {file_path}")
        except json.JSONDecodeError:
            print(f"FAQ 파일 JSON 파싱 오류: {file_path}")
        except Exception as e:
            print(f"FAQ 파일 로드 중 오류: {file_path}, 오류: {str(e)}")
    
    print(f"전체 FAQ 데이터 로드 완료: 총 {len(all_faq_data)}개 항목")
    return all_faq_data

def format_answer(answer_data):
    """답변을 슬랙 메시지 형식으로 포맷팅"""
    if isinstance(answer_data, dict):
        formatted_answer = f"*{answer_data['title']}*\n\n"
        for item in answer_data['items']:
            if item == "":  # 빈 줄 처리
                formatted_answer += "\n"
            else:
                formatted_answer += f"{item}\n"
        return formatted_answer
    else:
        return answer_data

# 봇 멘션 이벤트 처리
@app.event("app_mention")
def handle_mention(event, say):
    # 과정 선택 블록 생성
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "안녕하세요! 🤖 커널아카데미 부트캠프 FAQ 봇입니다.\n현재 진행중인 과정명을 선택해주세요."
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🧠 AI 과정",
                        "emoji": True
                    },
                    "value": "AI 과정",
                    "action_id": "select_ai_course"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 BDA 과정",
                        "emoji": True
                    },
                    "value": "BDA 과정",
                    "action_id": "select_bda_course"
                }
            ]
        }
    ]
    
    say(blocks=blocks, text="과정을 선택해주세요.")

# 과정 선택 버튼 처리
@app.action("select_ai_course")
@app.action("select_bda_course")
def handle_course_selection(ack, body, say):
    ack()
    
    # 선택된 과정 정보
    selected_course = body["actions"][0]["value"]
    user_id = body["user"]["id"]
    
    print(f"사용자 {user_id}가 {selected_course}를 선택했습니다.")
    
    # FAQ 데이터 로드
    faq_data = load_faq_data()
    
    # 선택된 과정에 해당하는 모든 질문들 추출
    course_questions = [faq for faq in faq_data if faq["course"] == selected_course]
    
    # 질문 선택 블록 생성
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{selected_course}*에 대한 모든 FAQ입니다.\n\n*궁금한 질문을 선택해주세요:*\n총 {len(course_questions)}개의 질문이 있습니다."
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # 질문 버튼들 생성
    button_elements = []
    
    for i, faq in enumerate(course_questions):
        # 카테고리 아이콘 설정
        category_icon = ""
        if "출석" in faq["category"]:
            category_icon = "📋"
        elif "실시간" in faq["category"]:
            category_icon = "🏫"
        elif "온라인" in faq["category"]:
            category_icon = "💻"
        elif "수업 외" in faq["category"]:
            category_icon = "📚"
        else:
            category_icon = "❓"
        
        # 질문 텍스트 (카테고리 포함)
        question_text = f"{category_icon} {faq['question']}"
        if len(question_text) > 75:
            question_text = question_text[:72] + "..."
        
        button_elements.append({
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": question_text,
                "emoji": True
            },
            "value": f"{selected_course}|{i}",  # 과정명과 인덱스를 저장
            "action_id": f"question_{i}"
        })
    
    # 버튼을 actions 블록에 추가 (최대 5개씩)
    for i in range(0, len(button_elements), 5):
        chunk = button_elements[i:i+5]
        blocks.append({
            "type": "actions",
            "elements": chunk
        })
    
    # 뒤로가기 버튼 추가
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "◀️ 과정 선택으로 돌아가기",
                    "emoji": True
                },
                "value": "back_to_start",
                "action_id": "back_to_start"
            }
        ]
    })
    
    say(blocks=blocks, text="질문을 선택해주세요.")

# 질문 선택 버튼 처리
@app.action(re.compile(r"question_\d+"))
def handle_question_selection(ack, body, say):
    ack()
    
    # 선택된 질문 정보 파싱
    button_value = body["actions"][0]["value"]
    course, question_index = button_value.split("|")
    question_index = int(question_index)
    user_id = body["user"]["id"]
    
    print(f"사용자 {user_id}가 {course}의 {question_index}번 질문을 선택했습니다.")
    
    # FAQ 데이터 로드
    faq_data = load_faq_data()
    
    # 해당 과정의 질문들 필터링
    course_questions = [faq for faq in faq_data if faq["course"] == course]
    
    if question_index < len(course_questions):
        selected_faq = course_questions[question_index]
        
        # 답변 블록 생성
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Q: {selected_faq['question']}*\n📂 카테고리: {selected_faq['category']}\n🎓 과정: {selected_faq['course']}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*A:* {format_answer(selected_faq['answer'])}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🔄 다른 질문 보기",
                            "emoji": True
                        },
                        "value": course,
                        "action_id": f"back_to_questions_{course.replace(' ', '_')}"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "🏠 처음으로 돌아가기",
                            "emoji": True
                        },
                        "value": "back_to_start",
                        "action_id": "back_to_start"
                    }
                ]
            }
        ]
        
        say(blocks=blocks, text="FAQ 답변입니다.")

# 다른 질문 보기 버튼 처리
@app.action(re.compile(r"back_to_questions_.*"))
def handle_back_to_questions(ack, body, say):
    ack()
    
    # 과정명 추출
    course = body["actions"][0]["value"]
    user_id = body["user"]["id"]
    
    print(f"사용자 {user_id}가 {course}의 질문 목록으로 돌아갑니다.")
    
    # 다시 같은 과정의 질문 선택 화면으로
    handle_course_selection_direct(course, say)

# 처음으로 돌아가기 버튼 처리
@app.action("back_to_start")
def handle_back_to_start(ack, body, say):
    ack()
    
    user_id = body["user"]["id"]
    print(f"사용자 {user_id}가 처음 화면으로 돌아갑니다.")
    
    # 처음 과정 선택 화면으로
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "안녕하세요! 🤖 커널아카데미 부트캠프 FAQ 봇입니다.\n현재 진행중인 과정명을 선택해주세요."
            }
        },
        {
            "type": "divider"
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "🧠 AI 과정",
                        "emoji": True
                    },
                    "value": "AI 과정",
                    "action_id": "select_ai_course"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "📊 BDA 과정",
                        "emoji": True
                    },
                    "value": "BDA 과정",
                    "action_id": "select_bda_course"
                }
            ]
        }
    ]
    
    say(blocks=blocks, text="과정을 선택해주세요.")

def handle_course_selection_direct(selected_course, say):
    """과정 선택 로직을 직접 호출하는 헬퍼 함수"""
    # FAQ 데이터 로드
    faq_data = load_faq_data()
    
    # 선택된 과정에 해당하는 모든 질문들 추출
    course_questions = [faq for faq in faq_data if faq["course"] == selected_course]
    
    # 질문 선택 블록 생성
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{selected_course}*에 대한 모든 FAQ입니다.\n\n*궁금한 질문을 선택해주세요:*\n총 {len(course_questions)}개의 질문이 있습니다."
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # 질문 버튼들 생성
    button_elements = []
    
    for i, faq in enumerate(course_questions):
        # 카테고리 아이콘 설정
        category_icon = ""
        if "출석" in faq["category"]:
            category_icon = "📋"
        elif "실시간" in faq["category"]:
            category_icon = "🏫"
        elif "온라인" in faq["category"]:
            category_icon = "💻"
        elif "수업 외" in faq["category"]:
            category_icon = "📚"
        else:
            category_icon = "❓"
        
        # 질문 텍스트 (카테고리 포함)
        question_text = f"{category_icon} {faq['question']}"
        if len(question_text) > 75:
            question_text = question_text[:72] + "..."
        
        button_elements.append({
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": question_text,
                "emoji": True
            },
            "value": f"{selected_course}|{i}",
            "action_id": f"question_{i}"
        })
    
    # 버튼을 actions 블록에 추가 (최대 5개씩)
    for i in range(0, len(button_elements), 5):
        chunk = button_elements[i:i+5]
        blocks.append({
            "type": "actions",
            "elements": chunk
        })
    
    # 뒤로가기 버튼 추가
    blocks.append({
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "◀️ 과정 선택으로 돌아가기",
                    "emoji": True
                },
                "value": "back_to_start",
                "action_id": "back_to_start"
            }
        ]
    })
    
    say(blocks=blocks, text="질문을 선택해주세요.")

# 앱 시작
if __name__ == "__main__":
    print("슬랙 봇을 시작합니다...")
    
    token_status = {
        "SLACK_BOT_TOKEN2": bool(os.environ.get('SLACK_BOT_TOKEN2')),
        "SLACK_APP_TOKEN2": bool(os.environ.get('SLACK_APP_TOKEN2'))
    }
    print("토큰 설정 상태 확인:", token_status)
    
    # Socket Mode 사용 (개발용)
    try:
        handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN2"))
        print("Socket Mode Handler 생성 완료")
        print("웹소켓 연결을 시작합니다...")
        handler.start()
    except Exception as e:
        print("봇 시작 중 오류 발생:", e)
