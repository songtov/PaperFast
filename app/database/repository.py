import datetime
import json
import logging
from typing import List, Optional, Tuple, Dict

from database.model import Message
from database.session import db_session

logger = logging.getLogger(__name__)


class RepositoryError(Exception):
    pass


class MessageRepository:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MessageRepository, cls).__new__(cls)
        return cls._instance

    def _generate_default_name(self, messages: List[Dict]) -> str:
        """첫 번째 사용자 메시지에서 대화 이름 생성"""
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                # 최대 30자로 제한
                return content[:30] + "..." if len(content) > 30 else content
        return "새 대화"

    def save(self, messages: List[Dict], message_id: Optional[int] = None) -> int:
        """
        메시지를 저장하거나 업데이트합니다.

        Args:
            messages: 저장할 메시지 리스트
            message_id: 기존 대화 ID (None이면 새로 생성, 있으면 업데이트)

        Returns:
            저장된 또는 업데이트된 메시지의 ID
        """
        try:
            with db_session.get_db_session() as session:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                messages_json = json.dumps(messages, ensure_ascii=False)

                if message_id:
                    # 기존 대화 업데이트
                    message = session.query(Message).filter(Message.id == message_id).first()
                    if message:
                        message.messages = messages_json
                        message.date = now
                        # 이름이 없으면 생성 (기존 대화 마이그레이션 지원)
                        if not message.name:
                            message.name = self._generate_default_name(messages)
                        return message_id
                    else:
                        # ID가 있지만 찾을 수 없으면 새로 생성
                        logger.warning(f"ID {message_id}를 찾을 수 없어 새 대화를 생성합니다.")

                # 새 대화 생성
                default_name = self._generate_default_name(messages)
                message = Message(
                    name=default_name,
                    date=now,
                    messages=messages_json,
                )
                session.add(message)
                session.flush()  # ID를 얻기 위해 flush
                return message.id
        except Exception as e:
            logger.error(f"메시지 저장 중 오류 발생: {str(e)}")
            raise RepositoryError(f"메시지 저장 오류: {str(e)}") from e

    def fetch(self) -> List[Tuple[int, str, str]]:
        """
        모든 대화 목록을 조회합니다.

        Returns:
            (id, name, date) 튜플의 리스트
        """
        try:
            with db_session.get_db_session() as session:
                messages = (
                    session.query(Message.id, Message.name, Message.date)
                    .order_by(Message.date.desc())
                    .all()
                )
                return [(d.id, d.name or d.date, d.date) for d in messages]
        except Exception as e:
            logger.error(f"메시지 이력 조회 중 오류 발생: {str(e)}")
            raise RepositoryError(f"메시지 이력 조회 오류: {str(e)}") from e

    def rename(self, message_id: int, new_name: str) -> bool:
        """
        대화 이름을 변경합니다.

        Args:
            message_id: 대화 ID
            new_name: 새로운 이름

        Returns:
            성공 여부
        """
        try:
            with db_session.get_db_session() as session:
                message = session.query(Message).filter(Message.id == message_id).first()
                if message:
                    message.name = new_name
                    return True
                return False
        except Exception as e:
            logger.error(f"대화 이름 변경 중 오류 발생: {str(e)}")
            raise RepositoryError(f"대화 이름 변경 오류: {str(e)}") from e

    def fetch_by_id(self, message_id: int) -> Optional[List[Dict]]:
        try:
            with db_session.get_db_session() as session:
                message = session.query(Message).filter(Message.id == message_id).first()

                if message:
                    messages = json.loads(message.messages)
                    return messages
                return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON 디코딩 오류: {str(e)}")
            raise RepositoryError(f"토론 데이터 변환 오류: {str(e)}") from e
        except Exception as e:
            logger.error(f"메시지 불러오기 중 오류 발생: {str(e)}")
            raise RepositoryError(f"메시지 불러오기 오류: {str(e)}") from e

    def delete_by_id(self, message_id: int) -> bool:
        try:
            with db_session.get_db_session() as session:
                result = session.query(Message).filter(Message.id == message_id).delete()
                return result > 0
        except Exception as e:
            logger.error(f"메시지 삭제 중 오류 발생: {str(e)}")
            raise RepositoryError(f"메시지 삭제 오류: {str(e)}") from e

    def delete_all(self) -> int:
        try:
            with db_session.get_db_session() as session:
                result = session.query(Message).delete()
                return result
        except Exception as e:
            logger.error(f"전체 메시지 삭제 중 오류 발생: {str(e)}")
            raise RepositoryError(f"전체 메시지 삭제 오류: {str(e)}") from e


message_repository = MessageRepository()
