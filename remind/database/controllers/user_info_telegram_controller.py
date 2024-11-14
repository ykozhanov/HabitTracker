from remind.database import get_session, User, UserInfoTelegram


class UserInfoTelegramController:

    def __init__(self, user: User):
        self._user = user

    def add_user_info_telegram(self, chat_id_telegram: int, user_id_telegram: int, bot_token: str) -> UserInfoTelegram:
        with get_session() as session:
            new_user_info_telegram = UserInfoTelegram(
                user_id_telegram=user_id_telegram,
                chat_id_telegram=chat_id_telegram,
                telegram_bot_token=bot_token,
                user_id=self._user.id,
            )
            session.add(new_user_info_telegram)
            session.commit()
            session.refresh(new_user_info_telegram)
            return new_user_info_telegram
