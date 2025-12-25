# 🎬 AI Subtitle Translator (v4.0)

---

### 🎓 Proje Hakkında

Bu proje, **İskenderun Teknik Üniversitesi Bilgisayar Mühendisliği Bölümü Mühendislikte Bilgisayar Uygulamaları I Dersi** kapsamında proje ödevi olarak geliştirilmiştir.

Python ve Google Gemini API kullanılarak geliştirilmiş, modern arayüze sahip profesyonel altyazı (.srt) çeviri aracı.

## 🌟 Özellikler

- **Yapay Zeka Destekli:** Google Gemini 2.5 Flash modeli ile bağlamı anlayan çeviriler.
- **Akıllı Argo Çevirisi:** "Damn it" gibi kelimeleri "Lanet olsun" şeklinde duruma uygun çevirir.
- **Format Koruma:** Zaman kodlarını ve satır yapılarını asla bozmaz.
- **Modern Arayüz:** CustomTkinter ile geliştirilmiş Dark/Light modlu şık tasarım.
- **Çoklu Dil Desteği:** İngilizce, Almanca, Fransızca, İspanyolca vb. dillerden Türkçe'ye (veya tam tersi) çeviri.
- **Kota Dostu:** API limitlerine takılmamak için akıllı bekleme ve batch işleme sistemi.

## 🚀 Kurulum

1. Projeyi indirin:

   ```bash
   git clone [https://github.com/alierentugrul/SRT-TRANSLATE.git](https://github.com/alierentugrul/SRT-TRANSLATE.git)
   cd AI-Subtitle-Translator
   ```

2. Gerekli kütüphaneleri kurun:

pip install -r requirements.txt

3. Uygulamayı çalıştırın:

python modern_cevirici.py

🔑 Kullanım

1. Google AI Studio adresinden ücretsiz bir API Key alın.

2. Uygulamayı açın ve Ayarlar sekmesine API anahtarınızı girip kaydedin.

3. Bir .srt dosyası seçin, hedef dili belirleyin ve başlatın!

🛠️ Kullanılan Teknolojiler

- Python 3.10+

- CustomTkinter (GUI)

- Google Generative AI (Gemini)

- Threading (Eşzamanlı İşleme)

Geliştirici: [Ali Eren Tuğrul]
