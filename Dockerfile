FROM python:3.12-slim

WORKDIR /app

# Kopiraj fajlove
COPY ./requirements.txt /app/requirements.txt

# Instaliraj dependencies
RUN pip install -r requirements.txt

# Kopiraj ostatak koda
COPY . /app

# Expose port
EXPOSE 8000

# Start backend with admin seeding
CMD ["sh", "-c", "python seed_admin.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
