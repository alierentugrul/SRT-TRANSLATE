import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import time
import json
import google.generativeai as genai
import webbrowser

# --- AYAR DOSYASI ---
CONFIG_FILE = "settings.json"

class ModernTranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- PENCERE AYARLARI ---
        self.title("SRT TRANSLATE")
        self.geometry("750x550") 
        self.minsize(600, 500)
        self.resizable(True, True)
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=0) # Sidebar sabit
        self.grid_columnconfigure(1, weight=1) # Sağ taraf esnek
        self.grid_rowconfigure(0, weight=1)

        # Değişkenler
        self.input_path = ctk.StringVar()
        self.api_key_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value="Hazır")
        self.target_lang_var = ctk.StringVar(value="Türkçe") # Varsayılan dil
        self.is_running = False

        # --- DİL TANIMLAMALARI ---
        # Format: "Görünen Ad": ("AI İçin İngilizce Adı", "Dosya Kodu")
        self.languages = {
            "Türkçe": ("Turkish", "TR"),
            "İngilizce": ("English", "EN"),
            "Almanca": ("German", "DE"),
            "Fransızca": ("French", "FR"),
            "İspanyolca": ("Spanish", "ES"),
            "İtalyanca": ("Italian", "IT"),
            "Rusça": ("Russian", "RU"),
            "Arapça": ("Arabic", "AR"),
            "Japonca": ("Japanese", "JA"),
            "Korece": ("Korean", "KO"),
            "Portekizce": ("Portuguese", "PT"),
            "Azerbaycan Türkçesi": ("Azerbaijani", "AZ"),
            "Hollandaca": ("Dutch", "NL")
        }

        # Ayarları Yükle
        self.load_config()

        # Arayüzü Kur
        self.create_sidebar()
        self.create_main_area()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.api_key_var.set(data.get("api_key", ""))
                    theme = data.get("theme", "System")
                    ctk.set_appearance_mode(theme)
            except Exception as e:
                print(f"Config yüklenemedi: {e}")
        else:
            ctk.set_appearance_mode("System")

    def save_config(self):
        data = {
            "api_key": self.api_key_var.get(),
            "theme": ctk.get_appearance_mode()
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)
            if self.tabview.get() == "Ayarlar": 
                messagebox.showinfo("Başarılı", "Ayarlar kaydedildi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydedilemedi: {e}")

    def create_sidebar(self):
        """Sol Menü (Slim Design)"""
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Logo
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="SRT\nTRANSLATE", font=ctk.CTkFont(size=16, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=10, pady=(20, 10))

        # Versiyon
        self.lbl_ver = ctk.CTkLabel(self.sidebar_frame, text="Ali Eren Tuğrul", font=ctk.CTkFont(size=10), text_color="gray")
        self.lbl_ver.grid(row=1, column=0, padx=10, pady=(0, 10))

        # Tema
        self.lbl_theme = ctk.CTkLabel(self.sidebar_frame, text="Tema:", anchor="w", font=ctk.CTkFont(size=12))
        self.lbl_theme.grid(row=5, column=0, padx=10, pady=(10, 0))
        
        self.option_theme = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Dark", "Light"],
                                              command=self.change_appearance_mode_event, width=110, height=25)
        self.option_theme.grid(row=6, column=0, padx=10, pady=(5, 20))
        self.option_theme.set(ctk.get_appearance_mode())

    def create_main_area(self):
        """Sağ Ana Alan"""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=(10, 10), pady=(0, 10), sticky="nsew")
        
        self.tab_translate = self.tabview.add("Çeviri")
        self.tab_settings = self.tabview.add("Ayarlar")

        self.setup_translation_tab()
        self.setup_settings_tab()

    def setup_settings_tab(self):
        lbl_info = ctk.CTkLabel(self.tab_settings, text="Gemini API Key", font=ctk.CTkFont(size=14, weight="bold"))
        lbl_info.pack(pady=15)

        entry_api = ctk.CTkEntry(self.tab_settings, textvariable=self.api_key_var, width=350, placeholder_text="AI Studio Key...", show="*")
        entry_api.pack(pady=5)

        btn_save = ctk.CTkButton(self.tab_settings, text="Kaydet", command=self.save_config, fg_color="green", hover_color="darkgreen", width=100)
        btn_save.pack(pady=10)

        lbl_link = ctk.CTkLabel(self.tab_settings, text="Key Al: aistudio.google.com", text_color="#1E90FF", cursor="hand2")
        lbl_link.pack(pady=10)
        lbl_link.bind("<Button-1>", lambda e: webbrowser.open("https://aistudio.google.com/app/apikey"))

    def setup_translation_tab(self):
        # 1. Dosya Seçim
        frame_file = ctk.CTkFrame(self.tab_translate, fg_color="transparent")
        frame_file.pack(fill="x", padx=5, pady=10)

        self.entry_path = ctk.CTkEntry(frame_file, textvariable=self.input_path, placeholder_text="Dosya yolu...", height=35)
        self.entry_path.pack(side="left", padx=(0, 10), fill="x", expand=True)

        btn_browse = ctk.CTkButton(frame_file, text="📂", command=self.select_file, width=40, height=35)
        btn_browse.pack(side="right", padx=0)

        # 2. Hedef Dil Seçimi (YENİ)
        frame_lang = ctk.CTkFrame(self.tab_translate, fg_color="transparent")
        frame_lang.pack(fill="x", padx=5, pady=(0, 10))

        lbl_lang = ctk.CTkLabel(frame_lang, text="Hedef Dil:", font=("Roboto", 12, "bold"))
        lbl_lang.pack(side="left", padx=(0, 10))

        # Dil listesini sıralı al
        sorted_langs = sorted(list(self.languages.keys()))
        # Türkçe'yi en başa koymak istersen:
        if "Türkçe" in sorted_langs:
            sorted_langs.remove("Türkçe")
            sorted_langs.insert(0, "Türkçe")

        self.option_lang = ctk.CTkOptionMenu(frame_lang, values=sorted_langs, variable=self.target_lang_var, width=150)
        self.option_lang.pack(side="left")

        # 3. Log
        self.txt_log = ctk.CTkTextbox(self.tab_translate, font=("Consolas", 11), activate_scrollbars=True)
        self.txt_log.pack(fill="both", expand=True, padx=0, pady=5)
        self.log("Sistem Hazır. Çevrilecek dili seçip başlatın.")

        # 4. Durum ve Progress
        frame_status = ctk.CTkFrame(self.tab_translate, fg_color="transparent")
        frame_status.pack(fill="x", padx=0, pady=5)
        
        self.lbl_status = ctk.CTkLabel(frame_status, textvariable=self.status_var, font=("Roboto", 11), anchor="w")
        self.lbl_status.pack(side="left")

        self.progress = ctk.CTkProgressBar(self.tab_translate, orientation="horizontal", height=10)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=0, pady=(0, 10))

        # 5. Başlat
        self.btn_start = ctk.CTkButton(self.tab_translate, text="ÇEVİRİYİ BAŞLAT", command=self.start_thread, height=40, font=("Roboto", 13, "bold"))
        self.btn_start.pack(fill="x", padx=0, pady=(0, 10))

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        self.save_config()

    def log(self, message):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f"> {message}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Subtitle", "*.srt"), ("All", "*.*")])
        if path:
            self.input_path.set(path)
            self.log(f"Seçildi: {os.path.basename(path)}")

    def start_thread(self):
        if not self.input_path.get():
            messagebox.showwarning("Hata", "Lütfen bir dosya seçin.")
            return
        if not self.api_key_var.get():
            messagebox.showwarning("Hata", "API Key eksik! Ayarlar sekmesinden giriniz.")
            self.tabview.set("Ayarlar")
            return
        
        if self.is_running: return

        # Seçilen dilin bilgilerini al
        selected_lang_name = self.target_lang_var.get()
        target_lang_english, lang_code = self.languages[selected_lang_name]

        self.is_running = True
        self.btn_start.configure(state="disabled", text=f"{selected_lang_name}'ye Çevriliyor...")
        
        # Thread'e dil parametrelerini gönderiyoruz
        threading.Thread(target=self.run_ai_translation, args=(target_lang_english, lang_code), daemon=True).start()

    def run_ai_translation(self, target_lang_english, lang_code):
        input_file = self.input_path.get()
        api_key = self.api_key_var.get()
        
        # Dosya ismini seçilen dile göre ayarla (Örn: movie_DE.srt)
        output_file = input_file.replace(".srt", f"_{lang_code}.srt")

        try:
            genai.configure(api_key=api_key)
            
            # Model Seçimi
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            model_name = 'models/gemini-2.5-flash'
            
            for m in available_models:
                if 'gemini-2.5-flash' in m: model_name = m; break
                elif 'gemini-pro' in m: model_name = m; break
            
            self.log(f"Model: {model_name}")
            self.log(f"Hedef Dil: {target_lang_english} ({lang_code})")
            model = genai.GenerativeModel(model_name)

            with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            blocks = [b for b in content.split('\n\n') if b.strip()]
            total_blocks = len(blocks)
            
            # Batch Size 50 (Kota Dostu)
            BATCH_SIZE = 50 
            batches = [blocks[i:i + BATCH_SIZE] for i in range(0, total_blocks, BATCH_SIZE)]
            total_batches = len(batches)

            translated_blocks = []
            
            for i, batch in enumerate(batches):
                current = i + 1
                percent = current / total_batches
                self.progress.set(percent)
                self.status_var.set(f"Paket {current}/{total_batches}")
                
                batch_text = "\n\n".join(batch)
                
                # --- DİNAMİK PROMPT ---
                # target_lang_english değişkeni burada kullanılıyor
                instruction = (
                    f"Aşağıdaki SRT formatındaki altyazıları {target_lang_english} diline (To {target_lang_english}) çevir.\n"
                    "1. Zaman kodlarını ve sayıları ASLA değiştirme.\n"
                    "2. Argo kelimeleri bağlama uygun çevir.\n"
                    "3. Satır yapısını KORU.\n"
                    "METİN:\n" + batch_text
                )

                success = False
                retry = 0
                while not success:
                    try:
                        resp = model.generate_content(instruction)
                        if resp.text:
                            translated_blocks.append(resp.text.strip())
                            success = True
                            time.sleep(10) # 10 sn bekle
                        else: raise Exception("Boş yanıt")
                    except Exception as e:
                        err_msg = str(e)
                        if "429" in err_msg or "Quota" in err_msg:
                            self.log(f"⚠️ Kota Doldu! 65 sn bekleniyor...")
                            for k in range(65, 0, -5):
                                self.status_var.set(f"Bekleniyor: {k} sn...")
                                time.sleep(5)
                        else:
                            retry += 1
                            self.log(f"Tekrar ({retry}): {e}")
                            time.sleep(5)
                        
                        if retry > 3 and "429" not in err_msg:
                            self.log(f"❌ Paket {current} atlandı.")
                            translated_blocks.append(batch_text)
                            success = True

            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n\n".join(translated_blocks))

            self.status_var.set("Bitti!")
            self.log(f"Dosya: {os.path.basename(output_file)}")
            self.progress.set(1)
            messagebox.showinfo("Başarılı", f"Çeviri ({lang_code}) tamamlandı!")
            
            if os.name == 'nt': os.startfile(os.path.dirname(output_file))

        except Exception as e:
            self.log(f"HATA: {e}")
            messagebox.showerror("Hata", str(e))
        finally:
            self.is_running = False
            self.btn_start.configure(state="normal", text="ÇEVİRİYİ BAŞLAT")

if __name__ == "__main__":
    app = ModernTranslatorApp()
    app.mainloop()