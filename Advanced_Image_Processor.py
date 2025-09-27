
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, font
import cv2
import numpy as np
from PIL import Image, ImageTk
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

# ==========================================================
# ToolTip Class (No Changes)
# ==========================================================
class ToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget; self.text = text; self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip); self.widget.bind("<Leave>", self.hide_tooltip)
    def show_tooltip(self, event):
        if self.tooltip_window or not self.text: return
        x, y, _, _ = self.widget.bbox("insert"); x = x + self.widget.winfo_rootx() + 25; y = y + self.widget.winfo_rooty() + 25
        self.tooltip_window = tw = tk.Toplevel(self.widget); tw.wm_overrideredirect(True); tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#2E2E2E", foreground="#FFFFFF", relief=tk.SOLID, borderwidth=1, font=("Segoe UI", "10", "normal"), padx=8, pady=4)
        label.pack(ipadx=1)
    def hide_tooltip(self, event):
        if self.tooltip_window: self.tooltip_window.destroy()
        self.tooltip_window = None

# ==========================================================
# WatershedHelper Class (No Changes)
# ==========================================================
class WatershedHelper:
    def __init__(self, image):
        self.image = image; self.markers = np.zeros(image.shape[:2], dtype=np.int32); self.current_marker = 1; self.drawing = False
    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN: self.drawing = True
        elif event == cv2.EVENT_LBUTTONUP: self.drawing = False
        if self.drawing:
            color = (0, 255, 0) if self.current_marker == 1 else (0, 0, 255)
            cv2.circle(self.markers, (x, y), 5, (self.current_marker), -1)
            cv2.circle(self.image, (x, y), 5, color, -1)
    def set_marker_type(self, marker_type):
        if marker_type == 'foreground': self.current_marker = 1
        elif marker_type == 'background': self.current_marker = 2

# ==========================================================
# Main App Class
# ==========================================================
class AdvancedImageProcessor:
    def __init__(self, root):
        self.root = root
        self.root.title("المشروع المتكامل لمعالجة الصور والفيديو")
        self.root.geometry("1600x950")
        self.root.configure(bg='#2E2E2E')

        self.setup_styles()

        self.original_image = None; self.processed_image = None; self.video_capture = None
        self.is_camera_on = False; self.is_recording = False; self.video_writer = None
        self.effect_grayscale = tk.BooleanVar(); self.effect_canny = tk.BooleanVar()
        self.effect_face_detect = tk.BooleanVar(); self.effect_flip = tk.BooleanVar()
        self.last_processed_frame = None

        self.load_cascades()
        self.setup_gui()

    def setup_styles(self):
        # ... (No changes here, but adding style for horizontal scrollbar)
        self.BG_COLOR = '#2E2E2E'; self.FG_COLOR = '#F5F5F5'; self.FRAME_COLOR = '#3A3A3A'; self.ACCENT_COLOR = '#4A90E2'; self.RESET_COLOR = '#C06C84'; self.BUTTON_HOVER_COLOR = '#63A4F4'
        self.title_font = font.Font(family="Helvetica", size=16, weight="bold"); self.label_font = font.Font(family="Segoe UI", size=11, weight="bold"); self.button_font = font.Font(family="Segoe UI", size=10, weight="bold"); self.team_font = font.Font(family="Segoe UI", size=10)
        style = ttk.Style(self.root); style.theme_use('clam')
        style.configure('TFrame', background=self.BG_COLOR); style.configure('TLabel', background=self.BG_COLOR, foreground=self.FG_COLOR, font=self.label_font); style.configure('TLabelframe', background=self.FRAME_COLOR, borderwidth=1, relief="solid"); style.configure('TLabelframe.Label', background=self.FRAME_COLOR, foreground=self.ACCENT_COLOR, font=self.label_font)
        style.configure('TNotebook', background=self.BG_COLOR, borderwidth=0); style.configure('TNotebook.Tab', background=self.FRAME_COLOR, foreground=self.FG_COLOR, font=self.button_font, padding=[10, 5]); style.map('TNotebook.Tab', background=[('selected', self.ACCENT_COLOR), ('active', self.BUTTON_HOVER_COLOR)], foreground=[('selected', self.FG_COLOR), ('active', self.FG_COLOR)])
        style.configure('TButton', font=self.button_font, padding=10, borderwidth=0, background=self.ACCENT_COLOR, foreground=self.FG_COLOR); style.map('TButton', background=[('active', self.BUTTON_HOVER_COLOR), ('pressed', self.ACCENT_COLOR)], relief=[('pressed', 'sunken')])
        style.configure('Reset.TButton', background=self.RESET_COLOR); style.map('Reset.TButton', background=[('active', '#D18198')])
        style.configure('TCheckbutton', background=self.FRAME_COLOR, foreground=self.FG_COLOR, font=self.team_font, indicatorcolor=self.ACCENT_COLOR); style.map('TCheckbutton', indicatorcolor=[('selected', self.ACCENT_COLOR), ('active', self.BUTTON_HOVER_COLOR)])
        style.configure('Horizontal.TScale', background=self.FRAME_COLOR, troughcolor='#555555')
        # Style for BOTH vertical and horizontal scrollbars
        style.configure('Vertical.TScrollbar', background=self.FRAME_COLOR, troughcolor=self.BG_COLOR, arrowcolor=self.FG_COLOR)
        style.configure('Horizontal.TScrollbar', background=self.FRAME_COLOR, troughcolor=self.BG_COLOR, arrowcolor=self.FG_COLOR)

    # ===================================================================
    # GUI Setup (*** MODIFIED TO ADD HORIZONTAL SCROLLBAR ***)
    # ===================================================================
    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        controls_container = ttk.Frame(main_frame, width=420)
        controls_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        controls_container.pack_propagate(False)

        canvas = tk.Canvas(controls_container, bg=self.BG_COLOR, highlightthickness=0)

        # --- Scrollbars (Vertical and Horizontal) ---
        v_scrollbar = ttk.Scrollbar(controls_container, orient="vertical", command=canvas.yview, style='Vertical.TScrollbar')
        h_scrollbar = ttk.Scrollbar(controls_container, orient="horizontal", command=canvas.xview, style='Horizontal.TScrollbar')
        
        # Configure canvas to use both scrollbars
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Packing order is important for layout
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        scrollable_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", on_frame_configure)

        # --- All widgets are packed into the scrollable_frame (same as before) ---
        title_label = ttk.Label(scrollable_frame, text="معالج الصور المتقدم", font=self.title_font, foreground=self.ACCENT_COLOR, anchor='center')
        title_label.pack(pady=15, fill=tk.X, padx=10)

        load_btn = ttk.Button(scrollable_frame, text="📸  تحميل صورة", command=self.load_image)
        load_btn.pack(pady=(0, 5), padx=10, fill=tk.X)
        
        reset_btn = ttk.Button(scrollable_frame, text="🔄  إعادة ضبط الصورة", command=self.reset_image, style='Reset.TButton')
        reset_btn.pack(pady=5, padx=10, fill=tk.X)
        
        ttk.Separator(scrollable_frame, orient='horizontal').pack(fill='x', pady=15, padx=10)
        
        notebook = ttk.Notebook(scrollable_frame)
        notebook.pack(pady=10, padx=10, expand=True, fill=tk.BOTH)

        self.create_camera_tab(notebook)
        self.create_basic_filters_tab(notebook)
        self.create_edge_detection_tab(notebook)
        self.create_feature_detection_tab(notebook)
        self.create_segmentation_tab(notebook)
        self.create_morphology_tab(notebook)
        self.create_geometric_tab(notebook)
        
        team_frame = ttk.LabelFrame(scrollable_frame, text="أسماء الفريق")
        team_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10, padx=10)
        team_names = "أيمن قمحان\nحازم العمري\nضياء الحضرمي\nطارق العمري\nعلي القواس"
        team_label = ttk.Label(team_frame, text=team_names, justify=tk.CENTER, font=self.team_font)
        team_label.pack(pady=10)

        # --- Right Image Display Panel (No Changes Here) ---
        self.images_frame = ttk.Frame(main_frame)
        self.images_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.original_label = ttk.Label(self.images_frame, text="الصورة الأصلية", background='#252525', anchor='center')
        self.original_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.processed_label = ttk.Label(self.images_frame, text="الصورة المعالجة / الفيديو", background='#252525', anchor='center')
        self.processed_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))


    # ===================================================================
    # ALL OTHER FUNCTIONS REMAIN UNCHANGED
    # The rest of the code is identical to the previous version.
    # ===================================================================

    def create_camera_tab(self, notebook):
        # This function remains unchanged
        tab = ttk.Frame(notebook); notebook.add(tab, text='📹 الكاميرا')
        control_frame = ttk.LabelFrame(tab, text="التحكم والأدوات"); control_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Button(control_frame, text="▶️ تشغيل", command=self.start_camera).pack(side=tk.LEFT, expand=True, padx=2, pady=5)
        ttk.Button(control_frame, text="⏹️ إيقاف", command=self.stop_camera).pack(side=tk.LEFT, expand=True, padx=2, pady=5)
        self.record_button = ttk.Button(control_frame, text="🔴 تسجيل", command=self.toggle_recording, style='Reset.TButton'); self.record_button.pack(side=tk.LEFT, expand=True, padx=2, pady=5)
        ttk.Button(control_frame, text="📸 التقاط", command=self.take_snapshot).pack(side=tk.LEFT, expand=True, padx=2, pady=5)
        adjustments_frame = ttk.LabelFrame(tab, text="تعديلات الفيديو الحية"); adjustments_frame.pack(fill=tk.X, padx=10, pady=10)
        self.live_sliders = {}
        controls = {"Contrast": [-100, 100], "Exposure": [-100, 100], "Sharpen": [0, 100]}
        for text, limits in controls.items():
            f = ttk.Frame(adjustments_frame); ttk.Label(f, text=text, width=8).pack(side=tk.LEFT); slider = ttk.Scale(f, from_=limits[0], to=limits[1], orient=tk.HORIZONTAL, style='Horizontal.TScale'); slider.set(0); slider.pack(fill=tk.X, expand=True, padx=5); self.live_sliders[text] = slider; f.pack(fill=tk.X, pady=2)
        effects_frame = ttk.LabelFrame(tab, text="المؤثرات المرئية"); effects_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Checkbutton(effects_frame, text="تدرج الرمادي (Grayscale)", variable=self.effect_grayscale, style='TCheckbutton').pack(anchor='w', padx=5)
        ttk.Checkbutton(effects_frame, text="كشف الحواف (Canny)", variable=self.effect_canny, style='TCheckbutton').pack(anchor='w', padx=5)
        ttk.Checkbutton(effects_frame, text="كشف الوجوه والعيون", variable=self.effect_face_detect, style='TCheckbutton').pack(anchor='w', padx=5)
        ttk.Checkbutton(effects_frame, text="قلب أفقي (Flip)", variable=self.effect_flip, style='TCheckbutton').pack(anchor='w', padx=5)
    
    def create_basic_filters_tab(self, notebook):
        tab = ttk.Frame(notebook); notebook.add(tab, text='🎨 فلاتر')
        self.add_button(tab, "Log Transformation", self.apply_log_transform, "تطبيق التحويل اللوغاريتمي لتوضيح التفاصيل في المناطق المظلمة")
        self.add_button(tab, "Interactive Gaussian Blur", self.interactive_blur, "تنعيم الصورة بشكل تفاعلي للحد من الضوضاء")
        self.add_button(tab, "Median Filter", self.apply_median_filter, "إزالة ضوضاء الملح والفلفل (salt-and-pepper noise)")
        self.add_button(tab, "Custom Filter (Averaging)", self.apply_custom_filter, "تطبيق فلتر مخصص للمعدل (blur) على الصورة")
        self.add_button(tab, "Difference Filters", self.apply_difference_filters, "إظهار الفروقات الأفقية والعمودية في الصورة")
        self.add_button(tab, "Interactive Sharpening", self.interactive_sharpen, "زيادة حدة وتفاصيل الصورة بشكل تفاعلي")

    def create_edge_detection_tab(self, notebook):
        tab = ttk.Frame(notebook); notebook.add(tab, text='📉 حواف')
        self.add_button(tab, "Sobel Operator", self.apply_sobel, "كشف الحواف باستخدام مؤثر سوبل في الاتجاهين X و Y")
        self.add_button(tab, "Interactive Canny", self.interactive_canny, "كشف الحواف بدقة عالية مع التحكم في العتبات بشكل تفاعلي")

    def create_feature_detection_tab(self, notebook):
        tab = ttk.Frame(notebook); notebook.add(tab, text='✨ ميزات')
        self.add_button(tab, "Face & Eye Detection", self.detect_faces_eyes, "التعرف على الوجوه والعيون باستخدام Haar Cascades")
        self.add_button(tab, "Circle Detection (Hough)", self.detect_circles, "البحث عن الأشكال الدائرية باستخدام تحويل Hough")
        self.add_button(tab, "Line Detection (Hough)", self.detect_lines, "البحث عن الخطوط المستقيمة في الصورة")
        self.add_button(tab, "Corner Detection", self.detect_corners, "كشف الزوايا والاركان المهمة في الصورة")
        self.add_button(tab, "Ball Detection (Color Mask)", self.detect_and_copy_ball, "عزل الأجسام بناءً على لونها (مثال: كرة خضراء)")
        self.add_button(tab, "Manual Object Masking", self.manually_mask_object, "عزل كائن عن الخلفية يدويًا باستخدام خوارزمية GrabCut")

    def create_segmentation_tab(self, notebook):
        tab = ttk.Frame(notebook); notebook.add(tab, text='🧩 تجزئة')
        self.add_button(tab, "K-Means Segmentation", self.segment_kmeans, "تجزئة الصورة إلى مجموعات لونية باستخدام K-Means")
        self.add_button(tab, "Automatic Watershed", self.segment_watershed_auto, "تجزئة الصورة تلقائيًا لفصل الكائنات المتلامسة")
        self.add_button(tab, "Interactive Watershed", self.segment_watershed_interactive, "تجزئة الصورة بشكل تفاعلي عبر تحديد الكائن والخلفية")

    def create_morphology_tab(self, notebook):
        tab = ttk.Frame(notebook); notebook.add(tab, text='💠 مورفولوجيا')
        self.add_button(tab, "Erosion, Dilation, Gradient", self.apply_morph_basic, "تطبيق عمليات التآكل والتمدد والتدرج على الصورة")
        self.add_button(tab, "Opening & TopHat", self.apply_opening_tophat, "إزالة النقاط الصغيرة (Opening) وإبراز التفاصيل الدقيقة (Top-hat)")

    def create_geometric_tab(self, notebook):
        tab = ttk.Frame(notebook); notebook.add(tab, text='📐 هندسية')
        self.add_button(tab, "Rotation (تدوير)", self.apply_rotation, "تدوير الصورة بزاوية محددة")
        self.add_button(tab, "Translation (إزاحة)", self.apply_translation, "تحريك الصورة أفقيًا أو عموديًا")
        self.add_button(tab, "Zooming/Shrinking", self.apply_zoom, "تكبير أو تصغير الصورة بمعامل محدد")
        self.add_button(tab, "Cropping (اقتصاص)", self.apply_crop, "قص جزء محدد من الصورة بشكل تفاعلي")

    def start_camera(self):
        if self.is_camera_on: return
        self.video_capture = cv2.VideoCapture(0);
        if not self.video_capture.isOpened(): messagebox.showerror("خطأ", "لا يمكن فتح الكاميرا."); return
        self.is_camera_on = True; self.original_image = None; self.processed_image = None
        self.original_label.pack_forget(); self.display_images(); self.update_camera_feed()
    def stop_camera(self):
        if not self.is_camera_on: return
        self.is_camera_on = False
        if self.is_recording: self.toggle_recording()
        if self.video_capture: self.video_capture.release()
        self.processed_label.config(image='', text="الكاميرا متوقفة")
        self.original_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
    def update_camera_feed(self):
        if not self.is_camera_on: return
        ret, frame = self.video_capture.read()
        if ret:
            processed_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB); contrast = self.live_sliders["Contrast"].get(); exposure = self.live_sliders["Exposure"].get(); sharpen_amount = self.live_sliders["Sharpen"].get()
            if contrast != 0: factor = (100.0 + contrast) / 100.0; processed_frame = cv2.addWeighted(processed_frame, factor, np.zeros_like(processed_frame), 0, 0)
            if exposure != 0: processed_frame = cv2.add(processed_frame, np.array([float(exposure)]))
            if sharpen_amount > 0: blurred = cv2.GaussianBlur(processed_frame, (0,0), 3); alpha = 1.0 + (sharpen_amount / 100.0) * 1.5; processed_frame = cv2.addWeighted(processed_frame, alpha, blurred, 1.0 - alpha, 0)
            if self.effect_flip.get(): processed_frame = cv2.flip(processed_frame, 1)
            if self.effect_face_detect.get(): self.detect_faces_on_frame(processed_frame)
            gray_frame_for_effects = None
            if self.effect_grayscale.get() or self.effect_canny.get(): gray_frame_for_effects = cv2.cvtColor(processed_frame, cv2.COLOR_RGB2GRAY)
            if self.effect_canny.get(): processed_frame = cv2.Canny(gray_frame_for_effects, 100, 200)
            elif self.effect_grayscale.get(): processed_frame = gray_frame_for_effects
            self.last_processed_frame = processed_frame.copy(); self.display_image(processed_frame, self.processed_label, max_size=800)
            if self.is_recording and self.video_writer is not None:
                frame_to_write = self.last_processed_frame
                if len(frame_to_write.shape) == 2: frame_to_write = cv2.cvtColor(frame_to_write, cv2.COLOR_GRAY2BGR)
                else: frame_to_write = cv2.cvtColor(frame_to_write, cv2.COLOR_RGB2BGR)
                self.video_writer.write(frame_to_write)
        self.root.after(15, self.update_camera_feed)
    def detect_faces_on_frame(self, frame_to_process):
        if self.face_cascade is None or self.eye_cascade is None: return
        gray = cv2.cvtColor(frame_to_process, cv2.COLOR_RGB2GRAY); faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)
        for (x,y,w,h) in faces:
            cv2.rectangle(frame_to_process, (x,y), (x+w,y+h), (255,0,0), 2); roi_gray = gray[y:y+h, x:x+w]; roi_color = frame_to_process[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            for (ex,ey,ew,eh) in eyes: cv2.rectangle(roi_color, (ex,ey), (ex+ew,ey+eh), (0,255,0), 2)
    def toggle_recording(self):
        if not self.is_camera_on: messagebox.showwarning("تنبيه", "يجب تشغيل الكاميرا أولاً."); return
        if self.is_recording:
            self.is_recording = False; self.record_button.config(text="🔴 تسجيل", style='Reset.TButton')
            if self.video_writer: self.video_writer.release(); self.video_writer = None
            messagebox.showinfo("التسجيل", "تم إيقاف التسجيل وحفظ الملف.")
        else:
            if self.last_processed_frame is not None:
                self.is_recording = True; self.record_button.config(text="⏹️ إيقاف", style='TButton'); h, w = self.last_processed_frame.shape[:2]
                filename = f"recording_{time.strftime('%Y%m%d_%H%M%S')}.avi"; fourcc = cv2.VideoWriter_fourcc(*'XVID'); self.video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (w, h))
            else: messagebox.showerror("خطأ", "لا يوجد إطار فيديو لبدء التسجيل.")
    def take_snapshot(self):
        if not self.is_camera_on or self.last_processed_frame is None: messagebox.showwarning("تنبيه", "يجب تشغيل الكاميرا أولاً."); return
        filename = f"snapshot_{time.strftime('%Y%m%d_%H%M%S')}.png"; snapshot = self.last_processed_frame
        if len(snapshot.shape) == 3: snapshot = cv2.cvtColor(snapshot, cv2.COLOR_RGB2BGR)
        cv2.imwrite(filename, snapshot); messagebox.showinfo("نجاح", f"تم حفظ اللقطة باسم:\n{filename}")
    def _create_interactive_window(self, title):
        if self.original_image is None: messagebox.showerror("خطأ", "يرجى تحميل صورة أولاً"); return None, None, None
        top = tk.Toplevel(self.root); top.title(title); top.configure(bg=self.BG_COLOR)
        image_label = ttk.Label(top, background=self.BG_COLOR); image_label.pack(pady=10, padx=10)
        controls_frame = ttk.Frame(top); controls_frame.pack(pady=5, padx=10, fill=tk.X); return top, image_label, controls_frame
    def interactive_blur(self):
        top, image_label, controls_frame = self._create_interactive_window("Interactive Gaussian Blur")
        if top is None: return
        def update_blur(val):
            ksize = int(float(val)); ksize += 1 if ksize % 2 == 0 else 0
            blurred_img = cv2.GaussianBlur(self.original_image, (ksize, ksize), 0)
            self.display_image(blurred_img, image_label, max_size=500)
        ttk.Label(controls_frame, text="Kernel Size").pack(side=tk.LEFT)
        slider = ttk.Scale(controls_frame, from_=1, to=51, orient=tk.HORIZONTAL, command=update_blur, style='Horizontal.TScale'); slider.set(5); slider.pack(side=tk.LEFT, expand=True, fill=tk.X)
        update_blur(5)
    def interactive_canny(self):
        top, image_label, controls_frame = self._create_interactive_window("Interactive Canny Edge Detection")
        if top is None: return
        gray_img = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
        def update_canny(*args):
            t1, t2 = t1_slider.get(), t2_slider.get()
            if t1 > t2: t1_slider.set(t2); t1 = t2
            edges = cv2.Canny(gray_img, t1, t2); self.display_image(edges, image_label, max_size=500)
        t1_frame = ttk.Frame(controls_frame); ttk.Label(t1_frame, text="Threshold 1").pack(side=tk.LEFT); t1_slider = tk.Scale(t1_frame, from_=0, to=255, orient=tk.HORIZONTAL, command=update_canny); t1_slider.set(100); t1_slider.pack(side=tk.LEFT, expand=True, fill=tk.X); t1_frame.pack(fill=tk.X)
        t2_frame = ttk.Frame(controls_frame); ttk.Label(t2_frame, text="Threshold 2").pack(side=tk.LEFT); t2_slider = tk.Scale(t2_frame, from_=0, to=255, orient=tk.HORIZONTAL, command=update_canny); t2_slider.set(200); t2_slider.pack(side=tk.LEFT, expand=True, fill=tk.X); t2_frame.pack(fill=tk.X)
        update_canny()
    def interactive_sharpen(self):
        top, image_label, controls_frame = self._create_interactive_window("Interactive Sharpening")
        if top is None: return
        def update_sharpen(val):
            amount = float(val) / 10.0; blurred = cv2.GaussianBlur(self.original_image, (0, 0), 3)
            sharpened_img = cv2.addWeighted(self.original_image, 1.0 + amount, blurred, -amount, 0)
            self.display_image(sharpened_img, image_label, max_size=500)
        ttk.Label(controls_frame, text="Amount").pack(side=tk.LEFT)
        slider = ttk.Scale(controls_frame, from_=0, to=50, orient=tk.HORIZONTAL, command=update_sharpen, style='Horizontal.TScale'); slider.set(10); slider.pack(side=tk.LEFT, expand=True, fill=tk.X)
        update_sharpen(10)
    def apply_log_transform(self):
        img_gray = self.get_current_image(gray=True);
        if img_gray is None: return
        img_float = np.float32(img_gray) + 1; log_image = np.log(img_float)
        normalized_image = cv2.normalize(log_image, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
        self.processed_image = normalized_image; self.display_images()
    def apply_median_filter(self):
        img = self.get_current_image();
        if img is None: return
        self.processed_image = cv2.medianBlur(img, 5); self.display_images()
    def apply_custom_filter(self):
        img = self.get_current_image();
        if img is None: return
        kernel = np.ones((5, 5), np.float32) / 25; self.processed_image = cv2.filter2D(img, -1, kernel); self.display_images()
    def apply_difference_filters(self):
        img = self.get_current_image(gray=True);
        if img is None: return
        kernel_h = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]); kernel_v = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
        horizontal = cv2.filter2D(img, -1, kernel_h); vertical = cv2.filter2D(img, -1, kernel_v)
        self.show_results_in_new_window([self.original_image, horizontal, vertical], ["Original", "Horizontal", "Vertical"])
    def apply_sobel(self):
        img = self.get_current_image(gray=True);
        if img is None: return
        sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=5); sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=5)
        sobel_combined = cv2.magnitude(sobelx, sobely)
        self.show_results_in_new_window([cv2.convertScaleAbs(sobelx), cv2.convertScaleAbs(sobely), cv2.convertScaleAbs(sobel_combined)], ["Sobel X", "Sobel Y", "Magnitude"])
    def detect_faces_eyes(self):
        img = self.get_current_image();
        if img is None: return
        if self.face_cascade is None or self.eye_cascade is None: messagebox.showerror("خطأ", "لم يتم تحميل ملفات Haar Cascade."); return
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY); faces = self.face_cascade.detectMultiScale(gray, 1.3, 5); img_with_detections = img.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(img_with_detections, (x, y), (x + w, y + h), (255, 0, 0), 3)
            roi_gray = gray[y:y + h, x:x + w]; roi_color = img_with_detections[y:y + h, x:x + w]; eyes = self.eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes: cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
        self.processed_image = img_with_detections; self.display_images()
    def detect_circles(self):
        img = self.get_current_image();
        if img is None: return
        output = img.copy(); gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY); gray = cv2.medianBlur(gray, 5)
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=10, maxRadius=100)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]: cv2.circle(output, (i[0], i[1]), i[2], (0, 255, 0), 2); cv2.circle(output, (i[0], i[1]), 2, (0, 0, 255), 3)
        self.processed_image = output; self.display_images()
    def detect_lines(self):
        img = self.get_current_image();
        if img is None: return
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY); edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=80, minLineLength=50, maxLineGap=10); img_with_lines = img.copy()
        if lines is not None:
            for line in lines: x1, y1, x2, y2 = line[0]; cv2.line(img_with_lines, (x1, y1), (x2, y2), (0, 255, 0), 2)
        else: messagebox.showinfo("Result", "لم يتم العثور على خطوط.", parent=self.root)
        self.show_results_in_new_window([self.original_image, edges, img_with_lines], ["Original", "Canny Edges", "Detected Lines"])
    def detect_corners(self):
        img = self.get_current_image();
        if img is None: return
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY); gray = np.float32(gray); dst = cv2.cornerHarris(gray, 2, 3, 0.04); dst = cv2.dilate(dst, None)
        img_with_corners = img.copy(); img_with_corners[dst > 0.01 * dst.max()] = [0, 0, 255]; self.processed_image = img_with_corners; self.display_images()
    def detect_and_copy_ball(self):
        img = self.get_current_image();
        if img is None: return
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV); lower_green = np.array([35, 100, 100]); upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green); result = cv2.bitwise_and(img, img, mask=mask)
        self.processed_image = result; self.display_images()
    def segment_kmeans(self):
        img = self.get_current_image();
        if img is None: return
        k = simpledialog.askinteger("K-Means Clusters", "أدخل عدد الألوان (K):", parent=self.root, minvalue=2, maxvalue=32)
        if k is None: return
        pixel_values = img.reshape((-1, 3)); pixel_values = np.float32(pixel_values); criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, (centers) = cv2.kmeans(pixel_values, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers); segmented_image = centers[labels.flatten()]; self.processed_image = segmented_image.reshape(img.shape); self.display_images()
    def segment_watershed_auto(self):
        img = self.get_current_image();
        if img is None: return
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY); ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU); kernel = np.ones((3,3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2); sure_bg = cv2.dilate(opening, kernel, iterations=3)
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5); ret, sure_fg = cv2.threshold(dist_transform, 0.7*dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg); unknown = cv2.subtract(sure_bg, sure_fg); ret, markers = cv2.connectedComponents(sure_fg)
        markers = markers + 1; markers[unknown==255] = 0; markers = cv2.watershed(img, markers)
        img_result = img.copy(); img_result[markers == -1] = [255, 0, 0]; self.processed_image = img_result; self.display_images()
    def segment_watershed_interactive(self):
        img = self.get_current_image();
        if img is None: return
        helper = WatershedHelper(img.copy()); window_name = "Watershed Marking - Press Enter to Apply"; cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, helper.mouse_callback); messagebox.showinfo("Watershed Instructions", "1. ارسم على الصورة.\n2. اضغط 'f' للكائن و 'b' للخلفية.\n3. اضغط 'Enter' للتنفيذ.", parent=self.root)
        while True:
            cv2.imshow(window_name, helper.image); key = cv2.waitKey(1) & 0xFF
            if key == ord('b'): helper.set_marker_type('background')
            elif key == ord('f'): helper.set_marker_type('foreground')
            elif key == 13: break
            elif key == 27: cv2.destroyWindow(window_name); return
        cv2.destroyWindow(window_name); original_img_for_watershed = self.get_current_image(); markers = cv2.watershed(original_img_for_watershed, helper.markers)
        img_result = original_img_for_watershed.copy(); img_result[markers == -1] = [255, 0, 0]; self.processed_image = img_result; self.display_images()
    def manually_mask_object(self):
        img = self.get_current_image();
        if img is None: return
        messagebox.showinfo("Instructions", "ارسم مستطيلًا حول الكائن ثم اضغط Enter", parent=self.root)
        roi = cv2.selectROI("Select Object", cv2.cvtColor(img, cv2.COLOR_RGB2BGR), False); cv2.destroyWindow("Select Object")
        if not any(roi): return
        mask = np.zeros(img.shape[:2], np.uint8); bgdModel = np.zeros((1, 65), np.float64); fgdModel = np.zeros((1, 65), np.float64)
        cv2.grabCut(img, mask, roi, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8'); self.processed_image = img * mask2[:, :, np.newaxis]; self.display_images()
    def apply_morph_basic(self):
        img = self.get_current_image(gray=True);
        if img is None: return
        _, img_bin = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY); kernel = np.ones((5,5), np.uint8)
        erosion = cv2.erode(img_bin, kernel, iterations=1); dilation = cv2.dilate(img_bin, kernel, iterations=1); gradient = cv2.morphologyEx(img_bin, cv2.MORPH_GRADIENT, kernel)
        self.show_results_in_new_window([img_bin, erosion, dilation, gradient], ["Binary", "Erosion", "Dilation", "Gradient"])
    def apply_opening_tophat(self):
        img = self.get_current_image(gray=True);
        if img is None: return
        _, img_bin = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY); kernel = np.ones((9,9), np.uint8)
        opening = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN, kernel); tophat = cv2.morphologyEx(img_bin, cv2.MORPH_TOPHAT, kernel)
        self.show_results_in_new_window([img_bin, opening, tophat], ["Binary", "Opening", "Top-hat"])
    def apply_rotation(self):
        img = self.get_current_image();
        if img is None: return
        angle = simpledialog.askfloat("Input", "أدخل زاوية الدوران:", parent=self.root, minvalue=-360, maxvalue=360)
        if angle is None: return
        (h, w) = img.shape[:2]; center = (w // 2, h // 2); M = cv2.getRotationMatrix2D(center, angle, 1.0)
        self.processed_image = cv2.warpAffine(img, M, (w, h)); self.display_images()
    def apply_translation(self):
        img = self.get_current_image();
        if img is None: return
        tx = simpledialog.askinteger("Input", "أدخل الإزاحة الأفقية (X):", parent=self.root); ty = simpledialog.askinteger("Input", "أدخل الإزاحة العمودية (Y):", parent=self.root)
        if tx is None or ty is None: return
        (h, w) = img.shape[:2]; M = np.float32([[1, 0, tx], [0, 1, ty]]); self.processed_image = cv2.warpAffine(img, M, (w, h)); self.display_images()
    def apply_zoom(self):
        img = self.get_current_image();
        if img is None: return
        factor = simpledialog.askfloat("Input", "أدخل معامل التكبير:", parent=self.root, minvalue=0.1)
        if factor is None: return
        self.processed_image = cv2.resize(img, None, fx=factor, fy=factor, interpolation=cv2.INTER_LINEAR); self.display_images()
    def apply_crop(self):
        img = self.get_current_image();
        if img is None: return
        messagebox.showinfo("Instructions", "ارسم مستطيلًا للقص ثم اضغط Enter", parent=self.root)
        roi = cv2.selectROI("Crop Image", cv2.cvtColor(img, cv2.COLOR_RGB2BGR), False); cv2.destroyWindow("Crop Image")
        if not any(roi): return
        x, y, w, h = roi; self.processed_image = img[y:y+h, x:x+w]; self.display_images()
    def load_cascades(self):
        self.face_cascade, self.eye_cascade = None, None
        face_path = os.path.join('haarcascades', 'haarcascade_frontalface_default.xml'); eye_path = os.path.join('haarcascades', 'haarcascade_eye.xml')
        if os.path.exists(face_path): self.face_cascade = cv2.CascadeClassifier(face_path)
        if os.path.exists(eye_path): self.eye_cascade = cv2.CascadeClassifier(eye_path)
    def load_image(self):
        self.stop_camera()
        path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not path: return
        self.original_image = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB); self.reset_image()
    def reset_image(self):
        if self.original_image is not None: self.processed_image = self.original_image.copy(); self.display_images()
    def display_images(self):
        self.display_image(self.original_image, self.original_label); self.display_image(self.processed_image, self.processed_label)
    def display_image(self, img, label_widget, max_size=600):
        if img is None: label_widget.config(image='', text=""); return
        if len(img.shape) == 2: img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        h, w, _ = img.shape
        if w == 0 or h == 0: return
        scale = min(max_size/w, max_size/h) if w > 0 and h > 0 else 1
        img_resized = cv2.resize(img, (int(w*scale), int(h*scale)))
        img_pil = Image.fromarray(img_resized); img_tk = ImageTk.PhotoImage(image=img_pil)
        label_widget.config(image=img_tk); label_widget.image = img_tk
    def show_results_in_new_window(self, images, titles):
        top = tk.Toplevel(self.root); top.title("نتائج المعالجة"); top.configure(bg=self.BG_COLOR)
        fig = plt.figure(figsize=(12, 8), facecolor=self.BG_COLOR)
        cols = 3; rows = (len(images) + cols - 1) // cols
        for i, (img, title) in enumerate(zip(images, titles)):
            img_display = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB) if len(img.shape) == 2 else img
            ax = fig.add_subplot(rows, cols, i + 1); ax.imshow(img_display)
            ax.set_title(title, color=self.FG_COLOR); ax.axis('off')
        plt.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=top); canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1); canvas.draw()
    def get_current_image(self, gray=False):
        if self.original_image is None: messagebox.showerror("خطأ", "يرجى تحميل صورة أولاً"); return None
        img = self.original_image.copy()
        if gray: return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        return img
    def add_button(self, parent, text, command, tooltip_text=None):
        button = ttk.Button(parent, text=text, command=command)
        button.pack(fill=tk.X, padx=10, pady=4)
        tip_text = tooltip_text if tooltip_text else text
        ToolTip(button, tip_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedImageProcessor(root)
    root.mainloop()