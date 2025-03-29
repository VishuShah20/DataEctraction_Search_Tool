If in case the docker is not setup when you review it. Below are the instructions to run the system locally: <br>

How to run: <br>

1. Prereqs:<br>
	•	Python 3.10+ <br>
	•	PostgreSQL 14+<br>
	•	Node.js + npm (for frontend)<br>
	•	Git<br>

2. git clone https://github.com/VishuShah20/DataEctraction_Search_Tool.git<br>

cd DataEctraction_Search_Tool<br>

3. cd backend<br>
python -m venv dataenv<br>
activate dataenv<br>
pip install -r requirements.txt<br>

4. create a .env inside the root folder<br>

5. Make sure Postgresql is running locally and create a db named data_extraction<br>
CREATE DATABASE data_extraction;<br>

6. run backend:<br>
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000<br>

7. Setup and run frontend:<br>
cd ../frontend<br>
npm install<br>
npm run dev<br>
Then visit http://localhost:5173<br>




Docker how to run:

git clone https://github.com/VishuShah20/DataEctraction_Search_Tool.git <br>
cd DataEctraction_Search_Tool <br>
cp .env.example .env (or add .env yourself) <br>
docker-compose up --build <br>
docker-compose up -d <br>
