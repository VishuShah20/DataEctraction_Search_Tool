Please check docker instructions below. <br><br>
Below are the instructions to run the system locally. <br><br>Overview of the project is in the end, and all the possible optimizations and improvements I would do are commented all over the code under '''comment type''':<br><br>
I used FastAPI here in place of Node.js and express as I'm comfotable with FastAPI currently. I have had experience with Node.js as well.  <br><br><br>

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

<br>
<br>
<br>
Docker how to run:

git clone https://github.com/VishuShah20/DataEctraction_Search_Tool.git <br>
cd DataEctraction_Search_Tool <br>
cp .env.example .env (or add .env yourself) <br>
docker-compose up --build <br>
docker-compose up -d <br><br>
Once the docker is up wait for about 10 seconds for the classifier to load<br>
You will require the .env file to run it<br><br>
Frontend opens up on localhost:80<br>



<br>
<br>
<br>
Project overview:<br><br>
This is a full-stack project that lets users upload documents, intelligently processes them using NLP, stores key data, and lets users interact with their documents through search and Q&A.<br><br>

Key API Endpoints<br>
	•	POST /upload – Upload a document<br>
	•	GET /documents – Get documents for a user<br>
	•	GET /key_details – Get extracted key details<br>
	•	POST /search_answer – Ask questions about your docs<br>

What it does: <br><br>
	1.	Upload & Classify<br>
Users can upload a PDF document. We classify it using a zero-shot classifier from Hugging Face, and if needed, fallback to Anthropic Claude for tricky cases.<br><br>
	2.	Extract & Store<br>
We pull text from the PDF, upload both the original doc and the extracted text to AWS S3.<br><br>
	3.	Extract Key Info<br>
Based on the type of document, we extract important details (like PO number, dates, etc.) and save them in a PostgreSQL database.<br><br>
	4.	Query & Chat<br>
Users can:<br>
	•	See all their uploaded documents<br>
	•	Fetch structured details from them<br>
	•	Ask questions in a chatbot-style interface — we pull relevant content using fuzzy search and generate an answer using Claude.<br><br>
