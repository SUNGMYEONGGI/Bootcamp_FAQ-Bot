import os
import json
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
from log import log_info, log_event, log_user_interaction, log_error

# .env 파일에서 환경 변수 로드
load_dotenv()

# Slack 앱 초기화
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# FAQ 데이터 로드 (3개 파일 통합)
def load_faq_data():
    """출석, 실시간 강의, 온라인 강의 FAQ 데이터를 모두 로드하여 통합"""
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
                log_info(f"FAQ 데이터 로드 성공: {file_path} ({len(file_data)}개 항목)")
        except FileNotFoundError:
            log_error(f"FAQ 파일을 찾을 수 없습니다: {file_path}")
        except json.JSONDecodeError:
            log_error(f"FAQ 파일 JSON 파싱 오류: {file_path}")
        except Exception as e:
            log_error(f"FAQ 파일 로드 중 오류: {file_path}, 오류: {str(e)}")
    
    log_info(f"전체 FAQ 데이터 로드 완료: 총 {len(all_faq_data)}개 항목")
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

# 모든 이벤트 로깅 (디버깅용)
@app.event("message")
def handle_message_events(message, say):
    log_event("message", message)

# 봇 멘션 이벤트 처리
@app.event("app_mention")
def handle_mention(event, say):
    log_event("app_mention", event)
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
    
    # 사용자 상호작용 로깅
    log_user_interaction("course_selection", user_id, selected_course, body)
    
    # FAQ 데이터 로드
    faq_data = load_faq_data()
    
    # 선택된 과정에 해당하는 카테고리들 추출
    course_questions = [faq for faq in faq_data if faq["course"] == selected_course]
    categories = list(set([faq["category"] for faq in course_questions]))
    
    # 카테고리 선택 블록 생성
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{selected_course}*에 대한 FAQ입니다.\n\n*카테고리를 선택해주세요:*"
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # 카테고리 버튼들 생성
    category_elements = []
    
    for category in categories:
        # 카테고리별 이모지 설정
        if "실시간" in category:
            emoji = "🏫"
        elif "온라인" in category:
            emoji = "💻"
        else:
            emoji = "📋"
        
        category_elements.append({
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} {category}",
                "emoji": True
            },
            "value": f"{selected_course}|{category}",
            "action_id": f"category_{category.replace(' ', '_').replace('(', '_').replace(')', '_')}"
        })
    
    # 카테고리 버튼을 actions 블록에 추가
    blocks.append({
        "type": "actions",
        "elements": category_elements
    })
    
    say(blocks=blocks, text="카테고리를 선택해주세요.")

# 카테고리 선택 버튼 처리
@app.action(re.compile(r"category_.*"))
def handle_category_selection(ack, body, say):
    ack()
    
    # 선택된 카테고리 정보 파싱
    button_value = body["actions"][0]["value"]
    course, category = button_value.split("|", 1)
    user_id = body["user"]["id"]
    
    # 사용자 상호작용 로깅
    log_user_interaction("category_selection", user_id, button_value, body)
    
    # FAQ 데이터 로드
    faq_data = load_faq_data()
    
    # 선택된 과정과 카테고리에 해당하는 질문들 필터링
    filtered_questions = [faq for faq in faq_data if faq["course"] == course and faq["category"] == category]
    
    # 질문 선택 블록 생성
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{course}* > *{category}*\n\n*궁금한 질문을 선택해주세요:*"
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # 질문 버튼들 생성
    button_elements = []
    
    for i, faq in enumerate(filtered_questions):
        button_elements.append({
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": faq["question"][:75] + ("..." if len(faq["question"]) > 75 else ""),
                "emoji": True
            },
            "value": f"{course}|{category}|{i}",  # 과정명, 카테고리, 인덱스를 저장
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
                    "text": "◀️ 카테고리 선택으로 돌아가기",
                    "emoji": True
                },
                "value": course,
                "action_id": f"back_to_categories_{course.replace(' ', '_')}"
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
    course, category, question_index = button_value.split("|")
    question_index = int(question_index)
    user_id = body["user"]["id"]
    
    # 사용자 상호작용 로깅
    log_user_interaction("question_selection", user_id, button_value, body)
    
    # FAQ 데이터 로드
    faq_data = load_faq_data()
    
    # 해당 과정과 카테고리의 질문들 필터링
    filtered_questions = [faq for faq in faq_data if faq["course"] == course and faq["category"] == category]
    
    if question_index < len(filtered_questions):
        selected_faq = filtered_questions[question_index]
        
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
                            "text": "🔄 같은 카테고리 다른 질문 보기",
                            "emoji": True
                        },
                        "value": f"{course}|{category}",
                        "action_id": f"back_to_questions_{course.replace(' ', '_')}"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "◀️ 카테고리 선택으로 돌아가기",
                            "emoji": True
                        },
                        "value": course,
                        "action_id": f"back_to_categories_{course.replace(' ', '_')}"
                    }
                ]
            }
        ]
        
        say(blocks=blocks, text="FAQ 답변입니다.")

# 다른 질문 보기 버튼 처리 (같은 카테고리 내)
@app.action(re.compile(r"back_to_questions_.*"))
def handle_back_to_questions(ack, body, say):
    ack()
    
    # 과정명과 카테고리 추출
    button_value = body["actions"][0]["value"]
    course, category = button_value.split("|")
    user_id = body["user"]["id"]
    
    # 사용자 상호작용 로깅
    log_user_interaction("back_to_questions", user_id, button_value, body)
    
    # 다시 같은 카테고리의 질문 선택 화면으로
    handle_category_selection_direct(course, category, say)

# 카테고리 선택으로 돌아가기 버튼 처리
@app.action(re.compile(r"back_to_categories_.*"))
def handle_back_to_categories(ack, body, say):
    ack()
    
    # 과정명 추출
    course = body["actions"][0]["value"]
    user_id = body["user"]["id"]
    
    # 사용자 상호작용 로깅
    log_user_interaction("back_to_categories", user_id, course, body)
    
    # 다시 카테고리 선택 화면으로
    handle_course_selection_direct(course, say)

def handle_course_selection_direct(selected_course, say):
    """과정 선택 로직을 직접 호출하는 헬퍼 함수 (카테고리 선택 화면)"""
    # FAQ 데이터 로드
    faq_data = load_faq_data()
    
    # 선택된 과정에 해당하는 카테고리들 추출
    course_questions = [faq for faq in faq_data if faq["course"] == selected_course]
    categories = list(set([faq["category"] for faq in course_questions]))
    
    # 카테고리 선택 블록 생성
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{selected_course}*에 대한 FAQ입니다.\n\n*카테고리를 선택해주세요:*"
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # 카테고리 버튼들 생성
    category_elements = []
    
    for category in categories:
        # 카테고리별 이모지 설정
        if "실시간" in category:
            emoji = "🏫"
        elif "온라인" in category:
            emoji = "💻"
        else:
            emoji = "📋"
        
        category_elements.append({
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} {category}",
                "emoji": True
            },
            "value": f"{selected_course}|{category}",
            "action_id": f"category_{category.replace(' ', '_').replace('(', '_').replace(')', '_')}"
        })
    
    # 카테고리 버튼을 actions 블록에 추가
    blocks.append({
        "type": "actions",
        "elements": category_elements
    })
    
    say(blocks=blocks, text="카테고리를 선택해주세요.")

def handle_category_selection_direct(course, category, say):
    """카테고리 선택 로직을 직접 호출하는 헬퍼 함수 (질문 선택 화면)"""
    # FAQ 데이터 로드
    faq_data = load_faq_data()
    
    # 선택된 과정과 카테고리에 해당하는 질문들 필터링
    filtered_questions = [faq for faq in faq_data if faq["course"] == course and faq["category"] == category]
    
    # 질문 선택 블록 생성
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{course}* > *{category}*\n\n*궁금한 질문을 선택해주세요:*"
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # 질문 버튼들 생성
    button_elements = []
    
    for i, faq in enumerate(filtered_questions):
        button_elements.append({
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": faq["question"][:75] + ("..." if len(faq["question"]) > 75 else ""),
                "emoji": True
            },
            "value": f"{course}|{category}|{i}",
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
                    "text": "◀️ 카테고리 선택으로 돌아가기",
                    "emoji": True
                },
                "value": course,
                "action_id": f"back_to_categories_{course.replace(' ', '_')}"
            }
        ]
    })
    
    say(blocks=blocks, text="질문을 선택해주세요.")

# 앱 시작
if __name__ == "__main__":
    log_info("슬랙 봇을 시작합니다...")
    
    token_status = {
        "SLACK_BOT_TOKEN": bool(os.environ.get('SLACK_BOT_TOKEN')),
        "SLACK_APP_TOKEN": bool(os.environ.get('SLACK_APP_TOKEN'))
    }
    log_info("토큰 설정 상태 확인", token_status)
    
    # Socket Mode 사용 (개발용)
    try:
        handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
        log_info("Socket Mode Handler 생성 완료")
        log_info("웹소켓 연결을 시작합니다...")
        handler.start()
    except Exception as e:
        log_error("봇 시작 중 오류 발생", e)