FROM python:3.13-slim

# .pyc ファイルを作らない / ログをすぐに出力する
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ライブラリを先に入れる（requirements.txt が変わらなければ、この層はキャッシュが再利用される）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# --reload: ソースを保存すると自動で再起動する（開発用）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
