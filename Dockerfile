FROM python:3.11

WORKDIR /app

COPY requarment .

RUN pip install --no-cache-dir -r ./requarment

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
