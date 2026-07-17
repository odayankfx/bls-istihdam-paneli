# ABD İstihdam Verileri Dashboard'u

BLS (U.S. Bureau of Labor Statistics) Public Data API'sinden istihdam verilerini
otomatik çeken, yerel bir SQLite veritabanında saklayan ve Streamlit üzerinden
sektörel / demografik kırılımlarla görselleştiren bir sistem.

## Mimari

```
bls_employment_dashboard/
├── src/
│   ├── series_catalog.py   # Hangi BLS serilerinin çekileceği (kolayca genişletilebilir)
│   ├── bls_client.py       # BLS API v2 istemcisi (chunking, rate-limit yönetimi)
│   ├── database.py         # SQLite şeması + okuma/yazma fonksiyonları
│   └── update_data.py      # Veriyi çekip veritabanına yazan script
├── dashboard.py            # Streamlit arayüzü
├── data/employment.db      # SQLite veritabanı (ilk çalıştırmada oluşur)
├── requirements.txt
├── .env.example
└── .gitignore
```

## ☁️ Kurulum yapmadan online panel (Streamlit Community Cloud) — ÖNERİLEN

Hiçbir şey kurmadan, tarayıcıdan yönetilen bir panel kurmak için:

**1) Kodu GitHub'a atın**
```bash
cd bls_employment_dashboard
git init
git add .
git commit -m "İlk sürüm"
git branch -M main
git remote add origin https://github.com/<kullanici-adiniz>/<repo-adi>.git
git push -u origin main
```
> `data/employment.db` da bu commit'e dahil olur; ilk deploy için önce yerel
> bilgisayarınızda bir kez `python -m src.update_data` çalıştırıp veritabanını
> dolu şekilde push etmeniz önerilir (aşağıdaki "Yerel kurulum" adımına bakın).
> Hiç veri olmadan da deploy edebilirsiniz, ilk GitHub Actions çalışmasında
> dolacaktır.

**2) BLS API anahtarını GitHub Actions'a secret olarak ekleyin**
Repo sayfasında: `Settings → Secrets and variables → Actions → New repository secret`
- Name: `BLS_API_KEY`
- Value: BLS'ten aldığınız ücretsiz anahtar (https://data.bls.gov/registrationEngine/)

Bu adım, `.github/workflows/update_data.yml` dosyasındaki otomatik haftalık
güncellemenin çalışabilmesi için gerekli. İsterseniz repo sayfasında
`Actions` sekmesinden bu workflow'u "Run workflow" ile hemen de tetikleyebilirsiniz.

**3) Streamlit Community Cloud'da deploy edin**
- https://share.streamlit.io adresine GitHub hesabınızla giriş yapın
- "New app" → reponuzu seçin → main branch → main file: `dashboard.py`
- "Advanced settings → Secrets" kısmına şunu yapıştırın:
  ```toml
  BLS_API_KEY = "kendi_anahtariniz"
  ```
- Deploy'a basın. Birkaç dakika içinde `https://<app-adi>.streamlit.app`
  adresinden panelinize her yerden erişebilirsiniz.

**Nasıl güncel kalır?**
- `.github/workflows/update_data.yml` her Pazartesi otomatik çalışır, BLS'ten
  veri çeker ve `data/employment.db`'yi repoya commit eder.
- Streamlit Community Cloud, repoya yeni commit geldiğinde uygulamayı
  otomatik olarak yeniden deploy eder (GitHub webhook ile) — yani panel
  kendiliğinden güncel veriyle açılır, sizin hiçbir şey yapmanıza gerek yok.
- Dashboard içindeki "🔄 Veriyi şimdi güncelle" butonu ise sadece o anki
  oturum için anlık bir yenileme yapar (bulut ortamının dosya sistemi geçici
  olduğundan kalıcı değildir); asıl kalıcı güncelleme yukarıdaki GitHub
  Actions akışıdır.

---

## 💻 Yerel kurulum (kendi bilgisayarınızda çalıştırmak isterseniz)

```bash
git clone <bu-repo>
cd bls_employment_dashboard
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` dosyasını açıp `BLS_API_KEY` alanına kendi ücretsiz BLS API anahtarınızı
girin: https://data.bls.gov/registrationEngine/
(Anahtarsız da çalışır ama günlük istek limiti çok düşüktür: 25 istek/gün,
25 seri/istek — kayıtlı anahtarla 500 istek/gün, 50 seri/istek.)

## Kullanım

**1) Veriyi çek / güncelle:**
```bash
python -m src.update_data              # son 10 yılı çeker
python -m src.update_data --years 20   # son 20 yılı çeker
```

**2) Dashboard'u aç:**
```bash
streamlit run dashboard.py
```

Dashboard içinden de "🔄 Veriyi şimdi güncelle" butonuyla yeniden çekim
yapılabilir.

**3) Otomatik güncelleme (opsiyonel):**
BLS'in Employment Situation raporu her ayın ilk cuma günü yayınlanır. Haftalık
bir cron / Task Scheduler görevi kurmak güncel kalmak için yeterlidir:

```bash
# crontab -e  (macOS/Linux) — her Pazartesi 09:00
0 9 * * 1 cd /path/to/bls_employment_dashboard && venv/bin/python -m src.update_data
```

## Farklı bilgisayarlar arasında taşınabilirlik

Seçtiğiniz yaklaşım: **veri de kodla birlikte taşınsın.**

- `data/employment.db` dosyası `.gitignore`'da **hariç tutulmamıştır** —
  yani `git add data/employment.db && git commit -m "veri güncellendi"` ile
  veritabanını repoya commit edip başka bir bilgisayarda `git pull` ile
  senkronize edebilirsiniz. Aylık güncellemeler için dosya boyutu küçük
  kalacağından (birkaç yüz KB - birkaç MB) bu git için sorun teşkil etmez.
- Alternatif olarak veritabanını Dropbox/OneDrive/Google Drive gibi
  senkronize bir klasöre koyup `.env` içinde `DB_PATH` değişkeniyle o klasörü
  gösterebilirsiniz — bu durumda git'e hiç veri commit etmenize gerek kalmaz,
  sadece kod repoda kalır.
- Her iki durumda da `.env` dosyanız (API anahtarınız) **git'e eklenmez**,
  her bilgisayarda ayrıca `.env.example`'dan kopyalanıp doldurulmalıdır.

## Yeni seri / kırılım eklemek

`src/series_catalog.py` içine yeni bir BLS seri ID'si ve meta bilgisi
eklemeniz yeterlidir; hem `update_data.py` hem `dashboard.py` otomatik olarak
yeni seriyi tanır. Güncel BLS seri kodları için:
https://data.bls.gov/cgi-bin/surveymost

Örneğin eyalet bazlı işsizlik oranları (LAUS serileri) veya yaş grubu bazlı
detaylı kırılımlar eklemek isterseniz aynı mantıkla katalog dosyasını
genişletebilirsiniz.

## Notlar

- Tüm veri BLS'in resmi Public Data API v2'sinden (`api.bls.gov`) gelir.
- Mevsimsel düzeltmeli (seasonally adjusted) seriler kullanılmıştır; bu
  sayede ay içi mevsimsel dalgalanmalar (örn. yaz istihdamı) grafik
  yorumunu bozmaz.
- `period != 'M13'` filtresi yıllık ortalama satırlarını (M13) dışlar,
  sadece aylık veriler gösterilir.
