# Office Manager Backend

## Pokretanje lokalno

1. Instaliraj Python 3.10+  
2. Kreiraj i aktiviraj virtuelno okruženje:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Instaliraj zavisnosti:
   ```bash
   pip install -r requirements.txt
   ```
4. Pokreni aplikaciju:
   ```bash
   uvicorn main:app --reload
   ```
   Backend će raditi na [http://localhost:8000](http://localhost:8000).

⚠️ Potrebno je da MongoDB radi lokalno (default na `mongodb://localhost:27017/office_manager`).  
Ako koristiš drugu konekciju, promeni `MONGO_URI` u `.env` fajlu ili kao environment varijablu.

---

## Pokretanje sa Docker-om

1. U root folderu projekta nalazi se `docker-compose.yml` koji podiže **MongoDB**, **backend** i **frontend**.  
2. Pokreni:
   ```bash
   docker compose up --build
   ```
3. Backend će biti dostupan na [http://localhost:8000](http://localhost:8000).  
   MongoDB se pokreće u kontejneru i backend je povezan direktno preko `MONGO_URI=mongodb://mongo:27017/office_manager`.
