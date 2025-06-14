import os
import uuid
import psycopg2
from sentence_transformers import SentenceTransformer
import requests

PG_URI = os.getenv("PG_URI")
HE_TOKEN = os.getenv("HE_TOKEN")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": f"Bearer {HE_TOKEN}"}

def get_db_connection():
    return psycopg2.connect(PG_URI)

def store_data_with_vectors(texts, source):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        for chunk in texts:
            emb = embedding_model.encode([chunk])[0]
            emb_str = "[" + ",".join(map(str, emb)) + "]"
            cur.execute("""
                INSERT INTO knowledge_base (source, content, embedding)
                VALUES (%s, %s, %s::vector)
            """, (source, chunk, emb_str))
        
        cur.execute("DELETE FROM recent_uploads")
        cur.execute("INSERT INTO recent_uploads (source) VALUES (%s)", (source,))
        conn.commit()
        return f"Stored {len(texts)} rows from {source}"
    except Exception as e:
        return f"Upload error: {str(e)}"
    finally:
        cur.close()
        conn.close()

def ask_mixtral(query):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        q_emb = embedding_model.encode([query])[0]
        emb_str = "[" + ",".join(map(str, q_emb)) + "]"
        
        cur.execute("SELECT source FROM recent_uploads ORDER BY id DESC LIMIT 1")
        latest = cur.fetchone()
        if not latest:
            return "No recent documents found"
        
        cur.execute("""
            SELECT content FROM knowledge_base 
            WHERE source = %s
            ORDER BY embedding <-> %s::vector 
            LIMIT 5
        """, (latest[0], emb_str))
        rows = cur.fetchall()
        
        if not rows:
            return "No relevant content found"
        
        context = "\n\n".join([r[0] for r in rows])
        return query_mixtral_api(query, context)
    except Exception as e:
        return f"Query error: {str(e)}"
    finally:
        cur.close()
        conn.close()

def query_mixtral_api(query, context):
    prompt = f"<s>[INST] Use context to answer:\n\nContext:\n{context}\n\nQuestion: {query} [/INST]"
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 300, "temperature": 0.7}
    }
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        return response.json()[0]["generated_text"]
    except Exception as e:
        return f"API error: {str(e)}"

def register_complaint(name, email, complaint):
    try:
        token = str(uuid.uuid4())[:8]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO complaints (token, name, email, complaint)
            VALUES (%s, %s, %s, %s)
        """, (token, name, email, complaint))
        conn.commit()
        return f"Complaint registered. Token: {token}"
    except Exception as e:
        return f"Complaint error: {str(e)}"
    finally:
        cur.close()
        conn.close()

def check_complaint_status(token):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, complaint, status FROM complaints WHERE token = %s", (token,))
        result = cur.fetchone()
        if result:
            return f"Name: {result[0]}\nComplaint: {result[1]}\nStatus: {result[2]}"
        return "Complaint not found"
    except Exception as e:
        return f"Status error: {str(e)}"
    finally:
        cur.close()
        conn.close()