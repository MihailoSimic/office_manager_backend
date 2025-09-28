# Koristimo Python 3.11
FROM python:3.11-slim

# Setujemo radni direktorijum
WORKDIR /app

# Kopiramo requirements.txt i instaliramo zavisnosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiramo sav backend kod
COPY . .

# Expose port FastAPI aplikacije
EXPOSE 8000

# Startujemo FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
