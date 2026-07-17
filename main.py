import os
import json
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 1. ตั้งค่าการดึงสิทธิ์ Blogger จาก GitHub Secrets
SCOPES = ['https://www.googleapis.com/auth/blogger']
BLOG_ID = os.environ.get('BLOG_ID')

def get_blogger_service():
    """ดึงสิทธิ์ล็อกอินอัตโนมัติจาก Secrets"""
    creds = Credentials(
        token=None,
        refresh_token=os.environ.get('REFRESH_TOKEN'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get('CLIENT_ID'),
        client_secret=os.environ.get('CLIENT_SECRET'),
        scopes=SCOPES
    )
    
    # สั่งให้รีเฟรชสิทธิ์ตัวเองอัตโนมัติ
    if creds.expired or not creds.valid:
        creds.refresh(Request())
        
    return build('blogger', 'v3', credentials=creds)

def generate_article():
    """ใช้ Gemini เขียนบทความแฟชั่น/เทคโนโลยีระดับรันเวย์"""
    api_key = os.environ.get('GEMINI_API_KEY')
    genai.configure(api_key=api_key)
    
    genai.GenerativeModel("models/gemini-1.5-flash")
    
    prompt = """
    คุณคือบล็อกเกอร์มืออาชีพระดับอินเตอร์ สไตล์หรูหรา มั่นใจ และเจาะลึกรายละเอียด (Detail-oriented)
    เขียนบทความเกี่ยวกับ 'สตรีทแวร์สไตล์ Luxury Street ผสมกลิ่นอาย Los Angeles และไอเดียการเลือกน้ำหอมให้เข้ากับลุค'
    
    ข้อกำหนดของบทความ:
    1. เขียนเป็นภาษาไทยที่ดูเป็นกันเอง มั่นใจ มีระดับ
    2. อธิบายรายละเอียดของดีไซน์ เนื้อผ้า การคุมโทนสี และการเลือกน้ำหอมกลิ่นแนวนีช (Niche) หรือเคมีน้ำหอมที่เสริมลุคนี้
    3. จัดรูปแบบเป็น HTML เท่านั้น (ห้ามใส่โค้ด ```html ครอบ ให้เริ่มด้วยแท็ก HTML เลย)
    4. ใช้แท็ก <h2>, <h3> สำหรับหัวข้อ, <p> สำหรับเนื้อหา, <strong> เน้นคำสำคัญ และ <ul>/<li> สำหรับการไล่เลียงดีเทล
    5. มีหัวข้อเรื่องที่น่าดึงดูด (Title) อยู่ในบรรทัดแรกสุดของผลลัพธ์ โดยเขียนในรูปแบบ: [TITLE] หัวข้อบทความ [/TITLE]
    """
    
    response = model.generate_content(prompt)
    raw_text = response.text
    
    try:
        title = raw_text.split("[TITLE]")[1].split("[/TITLE]")[0].strip()
        body_content = raw_text.split("[/TITLE]")[1].strip()
    except Exception:
        title = "Fashion & Scent: ลุคสตรีทสุดมั่นใจสไตล์ LA"
        body_content = raw_text
        
    return title, body_content

def main():
    try:
        print("🤖 เริ่มต้นทำงานระบบ AI Auto-Blogger...")
        title, content = generate_article()
        
        print(f"✍️ เจนบทความสำเร็จ: {title}")
        blogger = get_blogger_service()
        
        body = {
            "kind": "blogger#post",
            "title": title,
            "content": content,
            "labels": ["Fashion", "Beauty", "Lifestyle"]
        }
        
        request = blogger.posts().insert(blogId=BLOG_ID, body=body, isDraft=False)
        response = request.execute()
        print(f"🎉 โพสต์ลงบล็อกเรียบร้อยแล้ว! URL: {response.get('url')}")
        
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {str(e)}")

if __name__ == "__main__":
    main()
