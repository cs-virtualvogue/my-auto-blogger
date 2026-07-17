import os
import time
from google import genai
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

def generate_article_with_retry():
    """ใช้ Gemini เจนบทความ พร้อมระบบกันตาย (Retry และสลับโมเดลสำรองอัตโนมัติ)"""
    api_key = os.environ.get('GEMINI_API_KEY')
    client = genai.Client(api_key=api_key)
    
    prompt = """
    คุณคือบล็อกเกอร์มืออาชีพระดับอินเตอร์ สไตล์หรูหรา มั่นใจ และมีรสนิยมลึกซึ้ง (Detail-oriented)
    เขียนบทความเกี่ยวกับ 'Sunset Boulevard After Dark: การครีเอตลุค Luxury Street ด้วยแจ็กเก็ตหนังแกะ และการแมตช์น้ำหอมกลิ่น Woody-Leather'
    
    ข้อกำหนดของบทความ (ต้องปฏิบัติตามอย่างเคร่งครัด):
    1. เขียนเป็นภาษาไทยที่ดูมั่นใจ มีระดับ แฝงความเซ็กซี่น่าค้นหาแบบแฟชั่นนิสต้าตัวจริง
    2. โฟกัสเฉพาะ "ลุคกลางคืนโทนสีเข้ม" เท่านั้น (ห้ามเขียนถึงลุคกลางวัน หรือโทนสีสว่างเด็ดขาด)
    3. เจาะลึกดีเทลของเสื้อผ้า: อธิบายความละมุนของเนื้อผ้าหนังแกะนุ่ม (Lambskin Jacket) การทิ้งตัวของยีนส์ฟอกเทา Charcoal และการคุมโทนสีดาร์กๆ 
    4. เจาะลึกดีเทลน้ำหอมเพียง "กลุ่มเดียว" คือ Woody-Leather (ไม้หอมและหนัง): อธิบายความรู้สึกเมื่อกลิ่น Sandalwood, Cardamom และไอควันจางๆ ทำปฏิกิริยากับอุณหภูมิร่างกายและผิวเสื้อผ้าหนังแกะอย่างไรให้ออกมาลักชัวรีที่สุด
    
    5. **ข้อกำหนดการแนบรูปภาพประกอบ (สำคัญมาก)**:
       - บังคับให้แทรกแท็ก <img> เพื่อแสดงรูปภาพประกอบที่สวยงามและตรงกับเนื้อหาอย่างน้อย 2 รูป (รูปแรกเป็นรูปแฟชั่น Luxury Streetwear และรูปที่สองเป็นรูปขวดน้ำหอมระดับพรีเมียม)
       - ต้องใช้ URL รูปภาพจริงที่มีคุณภาพสูงและเป็นสากลจาก Unsplash (ขึ้นต้นด้วย https://images.unsplash.com/photo-...) เท่านั้น ห้ามใช้ลิงก์เสียหรือลิงก์สมมุติ
       - ตกแต่งสไตล์ของรูปภาพด้วย inline CSS เสมอเพื่อให้ลุคของบล็อกดูแพง เช่น: 
         style="width: 100%; max-width: 650px; height: auto; border-radius: 16px; margin: 30px auto; display: block; box-shadow: 0 10px 30px rgba(0,0,0,0.15);"
         (เพื่อให้รูปภาพมีขอบมนสวยงาม และมีเงาฟุ้งๆ นุ่มนวลตาสไตล์มินิมัลลิสต์)
         
    6. จัดรูปแบบเป็น HTML เท่านั้น (ห้ามใส่โค้ด ```html ครอบ ให้เริ่มด้วยแท็ก HTML เลย)
    7. ใช้แท็ก <h2>, <h3> สำหรับหัวข้อ, <p> สำหรับเนื้อหา, <strong> เน้นคำสำคัญ และ <ul>/<li> สำหรับการไล่เลียงดีเทล
    8. มีหัวข้อเรื่องที่น่าดึงดูด (Title) อยู่ในบรรทัดแรกสุดของผลลัพธ์ โดยเขียนในรูปแบบ: [TITLE] หัวข้อบทความ [/TITLE]
    """
    
    # 📌 วางแผนสำรอง: ลองใช้ตัวหลักก่อน ถ้าล่มค่อยสลับไปตัวสำรอง
    models_to_try = ['gemini-3.5-flash', 'gemini-3-flash-preview']
    
    for model_name in models_to_try:
        for attempt in range(3):  # ลองซ้ำโมเดลละ 3 ครั้ง ถ้าเจอ Error 503
            try:
                print(f"🔄 กำลังเรียกใช้งานโมเดล: {model_name} (พยายามครั้งที่ {attempt + 1})...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                
                raw_text = response.text
                
                # แยกส่วน Title และ Body ออกจากกัน
                try:
                    title = raw_text.split("[TITLE]")[1].split("[/TITLE]")[0].strip()
                    body_content = raw_text.split("[/TITLE]")[1].strip()
                except Exception:
                    title = "Sunset Boulevard After Dark: ครีเอตลุค Luxury Street & Scent"
                    body_content = raw_text
                    
                return title, body_content
                
            except Exception as e:
                error_msg = str(e)
                print(f"⚠️ เกิดปัญหากับโมเดล {model_name}: {error_msg}")
                
                # ถ้าเจออาการ 503 หรือทรัพยากรหนาแน่น ให้รอแป๊บนึงแล้วลองใหม่
                if "503" in error_msg or "UNAVAILABLE" in error_msg or "high demand" in error_msg:
                    print("⏳ เซิร์ฟเวอร์ Google น่าจะหนาแน่นชั่วคราว... รอ 5 วินาทีแล้วลองใหม่อีกครั้งนะคะนัตตี้")
                    time.sleep(5)
                else:
                    # ถ้าเจอ error ชนิดอื่นนอกเหนือจากเซิร์ฟเวอร์ล่ม ให้เปลี่ยนโมเดลทันที
                    break
                    
    # ถ้าพยายามทุกวิถีทางแล้วล่มจริงๆ ถึงจะโยน Error ออกไป
    raise Exception("❌ พยายามเชื่อมต่อทั้งโมเดลหลักและโมเดลสำรองแล้ว แต่เซิร์ฟเวอร์ Google ยังไม่พร้อมให้บริการในขณะนี้ค่ะ")

def main():
    try:
        print("🤖 เริ่มต้นทำงานระบบ AI Auto-Blogger (Official SDK + Auto Images + Smart Retry)...")
        title, content = generate_article_with_retry()
        
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
        print(f"❌ ระบบขัดข้องขั้นสุด: {str(e)}")

if __name__ == "__main__":
    main()
