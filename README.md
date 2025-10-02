# Office Manager Backend


## Running Locally

1. Install Python 3.10+
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. (Optional, but recommended) Seed the database with an admin user:
   ```bash
   python seed_admin.py
   ```
   This will create an admin account if it does not already exist.
   
   **Admin credentials:**
   - Username: `Admin`
   - Password: `Admin123!`

5. Start the application:
   ```bash
   uvicorn main:app --reload
   ```
   The backend will run at [http://localhost:8000](http://localhost:8000).

⚠️ MongoDB must be running locally (default at `mongodb://localhost:27017/office_manager`).
If you use a different connection, change the `MONGO_URI` in the `db.py` file.

---


## Running with Docker

1. In the root folder of the project, there is a `docker-compose.yml` file that starts **MongoDB**, **backend**, and **frontend**.
2. Run:
   ```bash
   docker compose up --build
   ```
3. The backend will be available at [http://localhost:8000](http://localhost:8000).
   MongoDB runs in a container and the backend is connected directly via `MONGO_URI=mongodb://mongo:27017/office_manager`.

**Admin user is automatically created in the backend container on startup.**

**Admin credentials:**
- Username: `admin`
- Password: `Admin123!`
