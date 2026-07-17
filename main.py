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
    คุณคือคอนเทนต์ครีเอเตอร์ระดับโลก

    1. **ภารกิจของคุณ**: เขียนบทความเจาะลึกสกินแคร์แบรนด์ชั้นนำจากอังกฤษอย่าง "No7 (นัมเบอร์เซเว่น)" โดยเขียนให้เป็นบทความเชิงให้ความรู้ และ เชิงแนะนำให้รู้จักกับตัวสินค้า และ สารสกัด 

    2. **ข้อกำหนดเนื้อหา (เจาะลึกและมีรายละเอียด)**:
   - เขียนด้วยโทนเสียงปกติ แบบบทความให้ความรู้เชิงวิชาการ แต่ไม่ต้องใช้ภาษาที่เป็นทางการมาก
   - เจาะลึกสารสกัดเด่นที่เป็นลิขสิทธิ์เฉพาะของ No7 เช่น Matrixyl 3000+, Peptides Complex หรือเทคโนโลยีเฉพาะในกลุ่มริ้วรอย (เช่น คอลเลกชัน Pure Retinol หรือ Future Renew) 
   - อธิบายกลไกการทำงานของสารสกัดเหล่านั้นอย่างละเอียดในขั้นตอนเดียว ให้เข้าใจทันทีว่ามันเข้าไปกระตุ้น คอลลาเจน (Collagen) หรืออีลาสติน (Elastin) อย่างไร
   - เชื่อมโยงและอ้างอิงผลการทดสอบตามงานวิจัยจริงของแบรนด์ "No7 (นัมเบอร์เซเว่น)"
   - และเปรียบเทียบผลิตภัณฑ์ (Product) ที่เหมือนกันในตลาดพร้อมบอกจุดเด่นที่ต่างจาก ผลิตภัณฑ์ ในท้องตลาดอย่างไร

    3. **ข้อกำหนดการแนบรูปภาพ**:
   - แทรกแท็ก <img> รูปที่สวยงามและตรงกับหัวข้อจาก Unsplash เท่านั้น (เช่น รูปนางแบบสายฝอผิวโกลว์ฉ่ำ, สกินแคร์แล็บนวัตกรรมล้ำๆ หรือขวดเซรั่มหรูหรา)
   - ใช้ CSS: style="width: 100%; max-width: 650px; height: auto; border-radius: 16px; margin: 30px auto; display: block; box-shadow: 0 10px 30px rgba(0,0,0,0.15);"

    4. **รูปแบบผลลัพธ์**:
   - จัดรูปแบบเป็น HTML เท่านั้น (ห้ามใส่โค้ด ```html ครอบ)
   - ใช้แท็ก <h2>, <h3>, <p>, <strong>, <ul>, <li> 
   - หัวข้อเรื่องต้องอยู่บรรทัดแรกสุดในรูปแบบ: [TITLE] หัวข้อบทความ [/TITLE]
   - ปิดท้ายบทความด้วยการใส่โค้ด HTML อ้างอิงแหล่งข้อมูลที่น่าเชื่อถือทางผิวหนังด้านล่างนี้ (ห้ามแก้ไขดัดแปลงโค้ดนี้):

    <div style="border-top: 1px solid rgb(220, 221, 225); margin-top: 50px; padding-top: 20px;">
        <h3 style="font-family: Prompt, sans-serif; font-size: 1.1rem; margin-bottom: 10px;">เอกสารอ้างอิงและแหล่งข้อมูลที่น่าเชื่อถือ (References)</h3>
        <div style="background-color: rgba(0, 0, 0, 0.01); border-radius: 6px; border: 1px solid rgb(226, 232, 240); padding: 15px 20px;">
            <p style="font-size: 9.5pt; margin-bottom: 8px;"><span style="color: #444444; font-family: Prompt, sans-serif;">• British Journal of Dermatology. (2024). "Clinical evaluation of a novel peptide complex (Pepticology) in reversing visible signs of skin damage."</span></p>
            <p style="font-size: 9.5pt; margin-bottom: 8px;"><span style="color: #444444; font-family: Prompt, sans-serif;"><span>• Watson, R. E. B., et al. (2025). "A randomized double-blind placebo-controlled trial to evaluate the efficacy of anti-ageing cosmetics containing proprietary Matrixyl 3000+ technology." International Journal of Cosmetic Science. </span><a href="[https://doi.org/10.1111/ics.12945](https://doi.org/10.1111/ics.12945)" rel="nofollow" target="_blank"><span>[https://doi.org/10.1111/ics.12945](https://doi.org/10.1111/ics.12945)</span></a></span></p>
            <p style="font-size: 9.5pt; margin-bottom: 8px;"><span style="color: #444444; font-family: Prompt, sans-serif;">• Journal of Investigative Dermatology. (2026). "Matrix metalloproteinase regulation and dermal matrix repair via topical bio-peptides."</span></p>
            <p style="font-size: 9.5pt; margin-bottom: 8px;"><span style="color: #444444; font-family: Prompt, sans-serif;">• University of Manchester School of Biological Sciences. (2025). "Independent scientific validation of next-generation skin repair formulations."</span></p>
            <p style="font-size: 9.5pt; margin-bottom: 8px;"><span style="color: #444444; font-family: Prompt, sans-serif;">• Cosmetic Ingredient Review (CIR) Expert Panel. (2026). "Safety assessment of palmitoyl oligopeptides and retinol delivery systems in commercial skincare."</span></p>
        </div>
    </div>
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
