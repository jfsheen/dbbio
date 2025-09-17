FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 创建必要的目录
RUN mkdir -p /app/app/static /app/app/templates

# 暴露端口
EXPOSE 5000

# CMD ["python"， "app.py"]

# 生产环境使用 gunicorn，指向正确的应用实例
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
