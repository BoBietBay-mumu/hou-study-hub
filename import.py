import json
import urllib.request

SUPABASE_URL = "https://pbyrzmmetkvvqydzkxo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBieXJ6bW1ldGt2dnF5b2R6a3hvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEyNzk1NzMsImV4cCI6MjEwNjg1NTU3M30.DGqyr-ESNBo1tYK5hCyG-nP2Tbq_ehAQKcyEgvEAlXM"

# Tên file JSON bạn vừa gửi
filename = "Kho_Dap_An_Backup_Full.json" 

try:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"Đã đọc file thành công, đang xử lý dữ liệu...")
except Exception as e:
    print(f"Lỗi đọc file: {e}")
    exit()

records = []

# Duyệt qua các môn học (Ví dụ: Đọc 1, Pháp luật đại cương, Triết học Mác,...)
for subject_name, content in data.items():
    # Lấy các câu đúng (correct)
    correct_dict = content.get("correct", {})
    for q_text, q_data in correct_dict.items():
        ans = q_data.get("correct", "")
        opts = q_data.get("options", [])
        if q_text and ans:
            records.append({
                "subject": subject_name,
                "question": q_text,
                "correct_answer": ans,
                "options": opts,
                "status": "correct"
            })
            
    # Lấy các câu sai (nếu có) để đưa vào kho sai
    wrong_dict = content.get("wrong", {})
    for q_text, q_data in wrong_dict.items():
        ans = q_data.get("correct", "")
        opts = q_data.get("options", [])
        if q_text and ans:
            records.append({
                "subject": subject_name,
                "question": q_text,
                "correct_answer": ans,
                "options": opts,
                "status": "wrong"
            })

print(f"Tổng số câu hỏi chuẩn bị đẩy lên mây: {len(records)} câu.")

# Gửi lên Supabase theo từng lô 50 câu để đảm bảo không bị nghẽn mạng
batch_size = 50
for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]
    req_data = json.dumps(batch).encode("utf-8")
    
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/question_banks",
        data=req_data,
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Đã đẩy thành công lô từ câu {i} đến {i+len(batch)}")
    except Exception as e:
        print(f"Lỗi ở lô {i}: {e}")

print("✨ Hoàn tất! Toàn bộ câu hỏi đã nằm trọn trên mây Supabase.")
