import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import time
import json
import urllib.request
import urllib.error
import webbrowser

# --- AYAR DOSYASI ---
CONFIG_FILE = "settings.json"

# --- TEMA RENKLERİ (TOKYO NIGHT ESİNTİSİ) ---
BG_COLOR = "#1a1b26"
CARD_COLOR = "#24283b"
ACCENT_COLOR = "#bb9af7"      # Neon Mor
ACCENT_HOVER = "#9d7cd8"
TEXT_PRIMARY = "#c0caf5"
TEXT_SECONDARY = "#565f89"
SUCCESS_COLOR = "#73daca"    # Neon Yeşil
ERROR_COLOR = "#f7768e"      # Neon Kırmızı

class ModernTranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- PENCERE AYARLARI ---
        self.title("SRT TRANSLATE - PREMIUM")
        self.geometry("850x600")
        self.minsize(700, 550)
        self.resizable(True, True)
        self.configure(fg_color=BG_COLOR)
        
        # Değişkenler
        self.input_path = ctk.StringVar()
        self.api_key_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value="Sistem Hazır")
        self.target_lang_var = ctk.StringVar(value="Türkçe")
        self.is_running = False
        self.is_paused = False
        self.is_stopped = False

        # --- DİL TANIMLAMALARI ---
        self.languages = {
            "Türkçe": ("Turkish", "TR"), "İngilizce": ("English", "EN"), "Almanca": ("German", "DE"),
            "Fransızca": ("French", "FR"), "İspanyolca": ("Spanish", "ES"), "İtalyanca": ("Italian", "IT"),
            "Rusça": ("Russian", "RU"), "Arapça": ("Arabic", "AR"), "Japonca": ("Japanese", "JA"),
            "Korece": ("Korean", "KO"), "Portekizce": ("Portuguese", "PT"), 
            "Azerbaycan Türkçesi": ("Azerbaijani", "AZ"), "Hollandaca": ("Dutch", "NL")
        }

        self.load_config()
        self.create_dashboard()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    self.api_key_var.set(data.get("api_key", ""))
            except Exception:
                pass

    def save_config(self):
        data = { "api_key": self.api_key_var.get() }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(data, f)
            messagebox.showinfo("Başarılı", "API Key başarıyla kaydedildi!")
        except Exception as e:
            messagebox.showerror("Hata", f"Kaydedilemedi: {e}")

    def create_dashboard(self):
        # Ana Konteyner
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. HEADER (Başlık ve Ayarlar Butonu)
        self.header_frame = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 10))
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="SRT TRANSLATE", 
            font=("Century Gothic", 28, "bold"),
            text_color=ACCENT_COLOR
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="AI-Powered Precision",
            font=("Century Gothic", 12),
            text_color=TEXT_SECONDARY
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w")

        # Ayarlar Paneli
        self.settings_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.settings_frame.grid(row=0, column=1, rowspan=2, sticky="e")
        
        self.api_entry = ctk.CTkEntry(
            self.settings_frame, textvariable=self.api_key_var, show="*",
            width=200, height=35, placeholder_text="Gemini API Key...",
            fg_color=CARD_COLOR, border_color=TEXT_SECONDARY, text_color=TEXT_PRIMARY,
            font=("Consolas", 12)
        )
        self.api_entry.pack(side="left", padx=(0, 10))

        self.btn_save_api = ctk.CTkButton(
            self.settings_frame, text="Kaydet", command=self.save_config,
            width=80, height=35, fg_color=CARD_COLOR, hover_color=ACCENT_HOVER,
            border_width=1, border_color=ACCENT_COLOR, text_color=TEXT_PRIMARY,
            font=("Century Gothic", 12, "bold")
        )
        self.btn_save_api.pack(side="left")

        # 2. İÇERİK KARTI (Çeviri Araçları)
        self.main_card = ctk.CTkFrame(self, fg_color=CARD_COLOR, corner_radius=15)
        self.main_card.grid(row=1, column=0, sticky="nsew", padx=30, pady=(10, 25))
        self.main_card.grid_columnconfigure(0, weight=1)
        self.main_card.grid_rowconfigure(2, weight=1)

        # Üst Araçlar (Dosya ve Dil)
        self.tools_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.tools_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(25, 10))
        self.tools_frame.grid_columnconfigure(1, weight=1)

        self.btn_browse = ctk.CTkButton(
            self.tools_frame, text="📂 DOSYA SEÇ", command=self.select_file,
            width=140, height=45, fg_color=ACCENT_COLOR, hover_color=ACCENT_HOVER,
            text_color="#ffffff", font=("Century Gothic", 13, "bold"), corner_radius=8
        )
        self.btn_browse.grid(row=0, column=0, padx=(0, 15))

        self.entry_path = ctk.CTkEntry(
            self.tools_frame, textvariable=self.input_path, state="readonly",
            height=45, fg_color=BG_COLOR, border_color=BG_COLOR,
            text_color=TEXT_PRIMARY, font=("Consolas", 12)
        )
        self.entry_path.grid(row=0, column=1, sticky="ew", padx=(0, 15))

        # Dil Seçimi
        sorted_langs = sorted(list(self.languages.keys()))
        if "Türkçe" in sorted_langs:
            sorted_langs.remove("Türkçe")
            sorted_langs.insert(0, "Türkçe")

        self.option_lang = ctk.CTkOptionMenu(
            self.tools_frame, values=sorted_langs, variable=self.target_lang_var,
            width=160, height=45, fg_color=BG_COLOR, button_color=BG_COLOR,
            button_hover_color=CARD_COLOR, dropdown_fg_color=CARD_COLOR,
            dropdown_text_color=TEXT_PRIMARY, text_color=TEXT_PRIMARY,
            font=("Century Gothic", 13)
        )
        self.option_lang.grid(row=0, column=2)

        # Durum Çubuğu ve Buton
        self.action_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.action_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(10, 15))
        self.action_frame.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            self.action_frame, textvariable=self.status_var,
            font=("Century Gothic", 12), text_color=TEXT_SECONDARY
        )
        self.status_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.progress = ctk.CTkProgressBar(
            self.action_frame, orientation="horizontal", height=8,
            fg_color=BG_COLOR, progress_color=ACCENT_COLOR
        )
        self.progress.set(0)
        self.progress.grid(row=1, column=0, sticky="ew")

        self.buttons_frame = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        self.buttons_frame.grid(row=0, column=1, rowspan=2, sticky="e", padx=(20, 0))

        self.btn_stop = ctk.CTkButton(
            self.buttons_frame, text="⏹", command=self.stop_translation,
            width=45, height=45, fg_color="transparent", hover_color=ERROR_COLOR,
            border_width=2, border_color=ERROR_COLOR, text_color=ERROR_COLOR,
            font=("Century Gothic", 18), corner_radius=8, state="disabled"
        )
        self.btn_stop.pack(side="right", padx=(10, 0))

        self.btn_pause = ctk.CTkButton(
            self.buttons_frame, text="⏸", command=self.toggle_pause,
            width=45, height=45, fg_color="transparent", hover_color="#e0af68",
            border_width=2, border_color="#e0af68", text_color="#e0af68",
            font=("Century Gothic", 18), corner_radius=8, state="disabled"
        )
        self.btn_pause.pack(side="right", padx=(10, 0))

        self.btn_start = ctk.CTkButton(
            self.buttons_frame, text="ÇEVİRİYİ BAŞLAT", command=self.start_thread,
            width=160, height=45, fg_color="transparent", hover_color=CARD_COLOR,
            border_width=2, border_color=ACCENT_COLOR, text_color=ACCENT_COLOR,
            font=("Century Gothic", 14, "bold"), corner_radius=8
        )
        self.btn_start.pack(side="right")

        # Konsol (Log)
        self.console_frame = ctk.CTkFrame(self.main_card, fg_color=BG_COLOR, corner_radius=10)
        self.console_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 20))
        self.console_frame.grid_columnconfigure(0, weight=1)
        self.console_frame.grid_rowconfigure(0, weight=1)

        self.txt_log = ctk.CTkTextbox(
            self.console_frame, font=("Consolas", 12), fg_color="transparent",
            text_color=TEXT_PRIMARY, wrap="word"
        )
        self.txt_log.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.log("Sistem Başlatıldı. Bir dosya seçin ve hedef dili belirleyin.")

    def log(self, message):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Subtitle", "*.srt"), ("All", "*.*")])
        if path:
            self.input_path.set(path)
            self.log(f"Dosya Seçildi: {os.path.basename(path)}")

    def toggle_pause(self):
        if not self.is_running: return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.btn_pause.configure(text="▶", border_color=SUCCESS_COLOR, text_color=SUCCESS_COLOR)
            self.status_var.set("Duraklatıldı.")
            self.log("Çeviri duraklatıldı.")
        else:
            self.btn_pause.configure(text="⏸", border_color="#e0af68", text_color="#e0af68")
            self.status_var.set("İşleniyor...")
            self.log("Çeviri devam ediyor.")

    def stop_translation(self):
        if not self.is_running: return
        self.is_stopped = True
        self.log("Durdurma isteği alındı, mevcut paket bitince sonlandırılacak...")
        self.btn_stop.configure(state="disabled")

    def start_thread(self):
        if not self.input_path.get():
            messagebox.showwarning("Hata", "Lütfen bir dosya seçin.")
            return
        if not self.api_key_var.get():
            messagebox.showwarning("Hata", "API Key eksik! Lütfen yukarıdaki alana girip kaydedin.")
            return
        
        if self.is_running: return

        selected_lang_name = self.target_lang_var.get()
        target_lang_english, lang_code = self.languages[selected_lang_name]

        self.is_running = True
        self.is_paused = False
        self.is_stopped = False
        self.btn_start.configure(
            state="disabled", text="İŞLENİYOR...", 
            fg_color=BG_COLOR, border_color=TEXT_SECONDARY, text_color=TEXT_SECONDARY
        )
        self.btn_pause.configure(state="normal", text="⏸", border_color="#e0af68", text_color="#e0af68")
        self.btn_stop.configure(state="normal")
        
        threading.Thread(target=self.run_ai_translation, args=(target_lang_english, lang_code), daemon=True).start()

    def run_ai_translation(self, target_lang_english, lang_code):
        input_file = self.input_path.get()
        api_key = self.api_key_var.get()
        output_file = input_file.replace(".srt", f"_{lang_code}.srt")

        try:
            model_name = "openrouter/free"
            self.log(f"Bağlantı Kuruldu (OpenRouter). Model: {model_name}")
            self.log(f"Hedef Dil: {target_lang_english} ({lang_code})")

            with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            blocks = [b for b in content.split('\n\n') if b.strip()]
            total_blocks = len(blocks)
            
            BATCH_SIZE = 50 
            batches = [blocks[i:i + BATCH_SIZE] for i in range(0, total_blocks, BATCH_SIZE)]
            total_batches = len(batches)

            translated_blocks = []
            
            for i, batch in enumerate(batches):
                if self.is_stopped:
                    self.log("İşlem durduruldu. Çevirilen kısım kaydediliyor...")
                    break
                    
                while self.is_paused:
                    if self.is_stopped:
                        break
                    time.sleep(0.5)
                
                if self.is_stopped:
                    self.log("İşlem durduruldu. Çevirilen kısım kaydediliyor...")
                    break
                    
                current = i + 1
                percent = current / total_batches
                self.progress.set(percent)
                self.status_var.set(f"İşleniyor: {current}/{total_batches} paket")
                
                batch_text = "\n\n".join(batch)
                
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
                        req_data = {
                            "model": model_name,
                            "messages": [{"role": "user", "content": instruction}]
                        }
                        req = urllib.request.Request(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json"
                            },
                            data=json.dumps(req_data).encode("utf-8")
                        )
                        with urllib.request.urlopen(req) as response:
                            result = json.loads(response.read().decode("utf-8"))
                            resp_text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                        
                        if resp_text:
                            translated_blocks.append(resp_text.strip())
                            success = True
                            time.sleep(10)
                        else: raise Exception("Boş yanıt")
                    except urllib.error.HTTPError as he:
                        err_msg = f"HTTP {he.code}: {he.reason}"
                        if "429" in str(he.code) or "Quota" in err_msg:
                            self.log(f"⚠️ Kota Doldu/Rate Limit! 65 sn bekleniyor...")
                            for k in range(65, 0, -5):
                                self.status_var.set(f"Bekleniyor: {k} sn...")
                                time.sleep(5)
                        else:
                            retry += 1
                            self.log(f"Tekrar ({retry}): {err_msg}")
                            time.sleep(5)
                        
                        if retry > 3 and "429" not in str(he.code):
                            self.log(f"❌ Paket {current} atlandı.")
                            translated_blocks.append(batch_text)
                            success = True
                    except Exception as e:
                        err_msg = str(e)
                        retry += 1
                        self.log(f"Tekrar ({retry}): {e}")
                        time.sleep(5)
                        
                        if retry > 3:
                            self.log(f"❌ Paket {current} atlandı.")
                            translated_blocks.append(batch_text)
                            success = True

            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n\n".join(translated_blocks))

            if self.is_stopped:
                self.status_var.set("Çeviri Durduruldu!")
            else:
                self.status_var.set("Çeviri Tamamlandı!")
            self.log(f"Başarı: {os.path.basename(output_file)} kaydedildi.")
            self.progress.set(1)
            
            self.btn_start.configure(
                text="BAŞARIYLA TAMAMLANDI", 
                border_color=SUCCESS_COLOR, text_color=SUCCESS_COLOR
            )
            time.sleep(3)

            if os.name == 'nt': os.startfile(os.path.dirname(output_file))

        except Exception as e:
            self.log(f"HATA: {e}")
            self.status_var.set("Hata Oluştu!")
            messagebox.showerror("Hata", str(e))
        finally:
            self.is_running = False
            self.is_paused = False
            self.is_stopped = False
            self.btn_start.configure(
                state="normal", text="ÇEVİRİYİ BAŞLAT",
                fg_color="transparent", border_color=ACCENT_COLOR, text_color=ACCENT_COLOR
            )
            self.btn_pause.configure(state="disabled", text="⏸", border_color="#e0af68", text_color="#e0af68")
            self.btn_stop.configure(state="disabled")

if __name__ == "__main__":
    app = ModernTranslatorApp()
    app.mainloop()