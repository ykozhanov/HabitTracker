from fastapi import HTTPException


def get_token(x_token: str) -> str:
    if not x_token.startswith("Bearer"):
        raise HTTPException(detail="Неверный тип токена.", status_code=400)

    token = x_token.split(" ")[1]

    if not token:
        raise HTTPException(detail="Токен отсутствует.", status_code=400)

    return token
