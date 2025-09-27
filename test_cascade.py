import cv2
import os

# المسار النسبي للملف كما هو في مشروعك
face_cascade_path = os.path.join('haarcascades', 'haarcascade_frontalface_default.xml')

# طباعة المسار الكامل الذي يبحث فيه البرنامج
absolute_path = os.path.abspath(face_cascade_path)
print(f"[*] Checking for file at this absolute path:\n    {absolute_path}\n")

# --- الفحص الأول: هل الملف موجود؟ ---
if os.path.exists(absolute_path):
    print("[SUCCESS] File was found at the path.")
    
    # --- الفحص الثاني: هل يمكن لـ OpenCV تحميله؟ ---
    try:
        face_cascade = cv2.CascadeClassifier(absolute_path)
        if face_cascade.empty():
            print("\n[ERROR] File found, but it's empty or corrupt. Please re-download it.")
        else:
            print("\n[SUCCESS] OpenCV loaded the file successfully! The problem might be in your main app.")
            
    except Exception as e:
        print(f"\n[ERROR] An exception occurred while loading the file: {e}")
        print("This indicates the file is likely corrupt.")

else:
    print("[ERROR] File NOT found at the path.")
    print("Please check your folder structure and file names for any typos.")