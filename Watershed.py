# import cv2
# import numpy as np
# from matplotlib import pyplot as plt

# # --- الخطوة 0: تحميل الصورة ---
# # قراءة الصورة التي تحتوي على كائنات متلامسة
# img = cv2.imread('water_coins.png')
# # تحويلها إلى تدرج رمادي للتحليل
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# # --- الخطوة 1: المعالجة الأولية للحصول على صورة ثنائية ---
# # تطبيق Otsu's Threshold لعزل القطع النقدية عن الخلفية
# ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
# thresh الآن صورة سوداء وبيضاء، حيث القطع النقدية بيضاء

#t
# # --- الخطوة 2: تحديد الخلفية المؤكدة (sure background) ---
# # إزالة أي ضوضاء صغيرة باستخدام Opening
# kernel = np.ones((3,3), np.uint8)
# opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
# # توسيع (dilate) مساحة الكائنات لنجد المنطقة التي هي بالتأكيد خلفية
# sure_bg = cv2.dilate(opening, kernel, iterations=3)


# # --- الخطوة 3: تحديد الكائن المؤكد (sure foreground) ---
# # تحويل المسافة يعطينا قيم أعلى في مراكز الكائنات
# dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
# # بأخذ 70% من أقصى قيمة مسافة، نحصل على نوى الكائنات
# ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
# sure_fg = np.uint8(sure_fg) # تحويلها إلى نوع بيانات مناسب


# # --- الخطوة 4: تحديد المنطقة المجهولة (unknown region) ---
# # هي المنطقة بين الخلفية المؤكدة والكائن المؤكد
# unknown = cv2.subtract(sure_bg, sure_fg)


# # --- الخطوة 5: إنشاء العلامات (Markers) وتطبيق Watershed ---
# # إعطاء أرقام فريدة لكل نواة كائن (1, 2, 3...)
# ret, markers = cv2.connectedComponents(sure_fg)
# # إضافة 1 لجميع العلامات حتى تكون الخلفية المؤكدة 1 بدلاً من 0
# markers = markers + 1
# # الآن، نجعل المنطقة المجهولة 0 (هذه هي المنطقة التي يجب على الخوارزمية تحديدها)
# markers[unknown == 255] = 0

# # تطبيق خوارزمية Watershed
# # ستتعامل الخوارزمية مع المنطقة 0 وترسم حدود (قيمتها -1)
# cv2.watershed(img, markers)

# # تلوين الحدود باللون الأحمر على الصورة الأصلية
# img[markers == -1] = [255, 0, 0]


# # --- عرض النتائج ---
# plt.figure(figsize=(12, 8))

# plt.subplot(1, 2, 1)
# plt.imshow(cv2.cvtColor(cv2.imread('water_coins.png'), cv2.COLOR_BGR2RGB))
# plt.title('الصورة الأصلية')
# plt.axis('off')

# plt.subplot(1, 2, 2)
# plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
# plt.title('الصورة بعد التجزئة')
# plt.axis('off')

# plt.show()

import tkinter as tk
from tkinter import filedialog, ttk
import cv2
import numpy as np
from matplotlib import pyplot as plt

# --- تم وضع كل منطق المعالجة داخل هذه الدالة ---
# def process_and_display_image(image_path):
#     """
#     تقوم هذه الدالة بتحميل الصورة من المسار المحدد،
#     وتطبق خوارزمية Watershed عليها، ثم تعرض النتائج.
#     """
#     # --- الخطوة 0: تحميل الصورة ---
#     # قراءة الصورة الأصلية للحفاظ عليها للعرض لاحقًا
#     original_image = cv2.imread(image_path)
#     # إنشاء نسخة من الصورة لتطبيق التعديلات عليها
#     img = original_image.copy()
    
#     # التأكد من أن الصورة تم تحميلها بنجاح
#     if img is None:
#         print(f"خطأ: لم يتم العثور على الصورة في المسار: {image_path}")
#         return

#     # تحويلها إلى تدرج رمادي للتحليل
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     # --- الخطوة 1: المعالجة الأولية للحصول على صورة ثنائية ---
#     ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

#     # --- الخطوة 2: تحديد الخلفية المؤكدة (sure background) ---
#     kernel = np.ones((3,3), np.uint8)
#     opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
#     sure_bg = cv2.dilate(opening, kernel, iterations=3)

#     # --- الخطوة 3: تحديد الكائن المؤكد (sure foreground) ---
#     dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
#     ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
#     sure_fg = np.uint8(sure_fg)

#     # --- الخطوة 4: تحديد المنطقة المجهولة (unknown region) ---
#     unknown = cv2.subtract(sure_bg, sure_fg)

#     # --- الخطوة 5: إنشاء العلامات (Markers) وتطبيق Watershed ---
#     ret, markers = cv2.connectedComponents(sure_fg)
#     markers = markers + 1
#     markers[unknown == 255] = 0
#     cv2.watershed(img, markers)

#     # تلوين الحدود باللون الأحمر على الصورة الأصلية
#     img[markers == -1] = [255, 0, 0]

#     # --- عرض النتائج ---
#     plt.figure(figsize=(12, 8))

#     plt.subplot(1, 2, 1)
#     # استخدام النسخة الأصلية النظيفة للعرض
#     plt.imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
#     plt.title('الصورة الأصلية')
#     plt.axis('off')

#     plt.subplot(1, 2, 2)
#     # استخدام النسخة المعدلة للعرض
#     plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
#     plt.title('الصورة بعد التجزئة')
#     plt.axis('off')

#     plt.show()

# # --- دالة خاصة بزر الرفع ---
# def upload_action():
#     """
#     تفتح نافذة لاختيار ملف ثم تستدعي دالة المعالجة.
#     """
#     # فتح نافذة اختيار الملفات وتحديد الأنواع المسموح بها
#     file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
#     # إذا اختار المستخدم ملفًا بالفعل
#     if file_path:
#         process_and_display_image(file_path)

# # --- إعداد الواجهة الرسومية الرئيسية ---
# root = tk.Tk()
# root.title("أداة تجزئة الصور (Watershed)")
# root.geometry("400x150")

# # إعداد تصميم بسيط للواجهة
# style = ttk.Style()
# style.configure("TButton", font=("Helvetica", 12, "bold"), padding=10)

# # إنشاء إطار رئيسي لتوسيط الزر
# main_frame = ttk.Frame(root, padding=20)
# main_frame.pack(expand=True, fill=tk.BOTH)

# # إنشاء زر الرفع وربطه بدالة upload_action
# upload_button = ttk.Button(main_frame, text="🚀 ارفع صورة لمعالجتها", command=upload_action)
# upload_button.pack(expand=True)

# # تشغيل الواجهة الرسومية
# root.mainloop()


import cv2
import numpy as np
from matplotlib import pyplot as plt

# --- الخطوة 0: تحميل الصورة ---
# قراءة الصورة التي تحتوي على كائنات متلامسة
# تأكد من وجود صورة باسم 'coins.png' في نفس المجلد
original_image = cv2.imread('water_coins.png')
img = original_image.copy() # نأخذ نسخة للعمل عليها

# التأكد من تحميل الصورة بنجاح
if img is None:
    print("خطأ: لم يتم العثور على ملف الصورة 'coins.png'. تأكد من وجوده في نفس المجلد.")
else:
    # تحويلها إلى تدرج رمادي للتحليل
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # --- الخطوة 1: المعالجة الأولية للحصول على صورة ثنائية ---
    # تطبيق Otsu's Threshold لعزل القطع النقدية عن الخلفية
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # --- الخطوة 2: تحديد الخلفية المؤكدة (sure background) ---
    # إزالة أي ضوضاء صغيرة باستخدام Opening
    kernel = np.ones((3,3), np.uint8)
    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    # توسيع (dilate) مساحة الكائنات لنجد المنطقة التي هي بالتأكيد خلفية
    sure_bg = cv2.dilate(opening, kernel, iterations=3)

    # --- الخطوة 3: تحديد الكائن المؤكد (sure foreground) ---
    # تحويل المسافة يعطينا قيم أعلى في مراكز الكائنات
    dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    # بأخذ 70% من أقصى قيمة مسافة، نحصل على نوى الكائنات
    ret, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
    sure_fg = np.uint8(sure_fg) # تحويلها إلى نوع بيانات مناسب

    # --- الخطوة 4: تحديد المنطقة المجهولة (unknown region) ---
    # هي المنطقة بين الخلفية المؤكدة والكائن المؤكد
    unknown = cv2.subtract(sure_bg, sure_fg)

    # --- الخطوة 5: إنشاء العلامات (Markers) وتطبيق Watershed ---
    # إعطاء أرقام فريدة لكل نواة كائن (1, 2, 3...)
    ret, markers = cv2.connectedComponents(sure_fg)
    # إضافة 1 لجميع العلامات حتى تكون الخلفية المؤكدة 1 بدلاً من 0
    markers = markers + 1
    # الآن، نجعل المنطقة المجهولة 0
    markers[unknown == 255] = 0

    # تطبيق خوارزمية Watershed
    cv2.watershed(img, markers)

    # تلوين الحدود باللون الأحمر على الصورة
    img[markers == -1] = [255, 0, 0]

    # --- عرض النتائج ---
    plt.figure(figsize=(12, 8))

    plt.subplot(1, 2, 1)
    plt.imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    plt.title('الصورة الأصلية')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title('الصورة بعد التجزئة')
    plt.axis('off')

    plt.show()