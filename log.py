import os
import json
import csv
import logging
from datetime import datetime
from typing import Dict, Any
import sys

class SlackBotLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = log_dir
        self.create_log_directory()
        self.setup_logging()
        self.json_logs = []
        self.csv_headers = set()
        self.csv_data = []
        
    def create_log_directory(self):
        """로그 디렉토리 생성"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
    
    def setup_logging(self):
        """기본 로그 파일 설정"""
        log_filename = f"{self.log_dir}/bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # 로거 설정
        self.logger = logging.getLogger('slack_bot')
        self.logger.setLevel(logging.INFO)
        
        # 파일 핸들러
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 핸들러 추가
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        self.json_filename = f"{self.log_dir}/bot_events_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.csv_filename = f"{self.log_dir}/bot_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    def log_info(self, message: str, extra_data: Dict[Any, Any] = None):
        """INFO 레벨 로깅"""
        timestamp = datetime.now()
        
        # 1. 기본 로그 파일에 기록
        self.logger.info(message)
        
        # 2. JSON 파일용 데이터 준비
        json_entry = {
            "timestamp": timestamp.isoformat(),
            "level": "INFO",
            "message": message,
            "extra_data": extra_data or {}
        }
        self.json_logs.append(json_entry)
        self.save_json_log()
        
        # 3. CSV 파일용 데이터 준비
        if extra_data:
            csv_row = {
                "timestamp": timestamp.isoformat(),
                "level": "INFO",
                "message": message,
                **self._flatten_dict(extra_data)
            }
            self.csv_data.append(csv_row)
            self.update_csv_headers(csv_row.keys())
            self.save_csv_log()

    def log_event(self, event_type: str, event_data: Dict[Any, Any]):
        """슬랙 이벤트 로깅"""
        timestamp = datetime.now()
        
        message = f"[{event_type}] 이벤트 수신"
        
        # 1. 기본 로그 파일에 기록
        self.logger.info(f"{message}: {json.dumps(event_data, ensure_ascii=False, indent=2)}")
        
        # 2. JSON 파일용 데이터
        json_entry = {
            "timestamp": timestamp.isoformat(),
            "event_type": event_type,
            "message": message,
            "event_data": event_data,
            "question_time": timestamp.isoformat() if event_type == "app_mention" else None
        }
        self.json_logs.append(json_entry)
        self.save_json_log()
        
        # 3. CSV 파일용 데이터
        csv_row = {
            "timestamp": timestamp.isoformat(),
            "event_type": event_type,
            "message": message,
            **self._flatten_dict(event_data, prefix="event_")
        }
        if event_type == "app_mention":
            csv_row["question_time"] = timestamp.isoformat()
            
        self.csv_data.append(csv_row)
        self.update_csv_headers(csv_row.keys())
        self.save_csv_log()

    def log_user_interaction(self, action_type: str, user_id: str, selected_value: str, interaction_data: Dict[Any, Any] = None):
        """사용자 상호작용 로깅"""
        timestamp = datetime.now()
        
        message = f"[사용자 상호작용] {action_type} - 사용자: {user_id}, 선택값: {selected_value}"
        
        # 1. 기본 로그 파일에 기록
        self.logger.info(message)
        
        # 2. JSON 파일용 데이터
        json_entry = {
            "timestamp": timestamp.isoformat(),
            "action_type": action_type,
            "user_id": user_id,
            "selected_value": selected_value,
            "message": message,
            "interaction_data": interaction_data or {}
        }
        self.json_logs.append(json_entry)
        self.save_json_log()
        
        # 3. CSV 파일용 데이터
        csv_row = {
            "timestamp": timestamp.isoformat(),
            "action_type": action_type,
            "user_id": user_id,
            "selected_value": selected_value,
            "message": message,
            **self._flatten_dict(interaction_data or {}, prefix="interaction_")
        }
        self.csv_data.append(csv_row)
        self.update_csv_headers(csv_row.keys())
        self.save_csv_log()

    def _flatten_dict(self, d: Dict[Any, Any], prefix: str = "", max_depth: int = 3) -> Dict[str, Any]:
        """중첩된 딕셔너리를 평면화"""
        if max_depth <= 0:
            return {prefix.rstrip('_'): str(d)}
            
        items = []
        for k, v in d.items():
            new_key = f"{prefix}{k}" if prefix else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, f"{new_key}_", max_depth - 1).items())
            elif isinstance(v, (list, tuple)):
                items.append((new_key, json.dumps(v, ensure_ascii=False)))
            else:
                items.append((new_key, str(v)))
        return dict(items)

    def update_csv_headers(self, new_headers):
        """CSV 헤더 업데이트"""
        self.csv_headers.update(new_headers)

    def save_json_log(self):
        """JSON 로그 파일 저장"""
        try:
            with open(self.json_filename, 'w', encoding='utf-8') as f:
                json.dump(self.json_logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"JSON 로그 저장 오류: {e}")

    def save_csv_log(self):
        """CSV 로그 파일 저장"""
        try:
            if not self.csv_data:
                return
                
            headers = sorted(list(self.csv_headers))
            
            with open(self.csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                
                for row in self.csv_data:
                    # 빈 컬럼을 빈 문자열로 채움
                    complete_row = {header: row.get(header, '') for header in headers}
                    writer.writerow(complete_row)
        except Exception as e:
            print(f"CSV 로그 저장 오류: {e}")

    def log_error(self, message: str, error: Exception = None):
        """에러 로깅"""
        timestamp = datetime.now()
        
        error_msg = f"ERROR: {message}"
        if error:
            error_msg += f" - {str(error)}"
            
        # 1. 기본 로그 파일에 기록
        self.logger.error(error_msg)
        
        # 2. JSON 파일용 데이터
        json_entry = {
            "timestamp": timestamp.isoformat(),
            "level": "ERROR",
            "message": message,
            "error": str(error) if error else None
        }
        self.json_logs.append(json_entry)
        self.save_json_log()
        
        # 3. CSV 파일용 데이터
        csv_row = {
            "timestamp": timestamp.isoformat(),
            "level": "ERROR",
            "message": message,
            "error": str(error) if error else ""
        }
        self.csv_data.append(csv_row)
        self.update_csv_headers(csv_row.keys())
        self.save_csv_log()

# 전역 로거 인스턴스
bot_logger = SlackBotLogger()

# 편의 함수들
def log_info(message: str, extra_data: Dict[Any, Any] = None):
    bot_logger.log_info(message, extra_data)

def log_event(event_type: str, event_data: Dict[Any, Any]):
    bot_logger.log_event(event_type, event_data)

def log_user_interaction(action_type: str, user_id: str, selected_value: str, interaction_data: Dict[Any, Any] = None):
    bot_logger.log_user_interaction(action_type, user_id, selected_value, interaction_data)

def log_error(message: str, error: Exception = None):
    bot_logger.log_error(message, error) 