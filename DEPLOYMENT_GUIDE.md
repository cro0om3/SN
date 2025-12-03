# 🚀 دليل نشر SNOW LIWA على الإنترنت

## ⚠️ ملاحظة مهمة

**FastAPI لا يعمل على Streamlit Cloud!**
Streamlit Cloud مخصص فقط لتطبيقات Streamlit، وتطبيقنا مبني على FastAPI.

---

## ✅ خيارات النشر المتاحة

### 1. **Render.com** (موصى به - مجاني)

#### الخطوات

1. ارفع الكود على GitHub
2. اذهب إلى <https://render.com>
3. سجل دخول بحساب GitHub
4. اضغط "New" → "Web Service"
5. اختر المشروع من GitHub
6. اعدادات النشر:

   ```
   Name: snow-liwa
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

7. أضف Environment Variables:

   ```
   ZIINA_ACCESS_TOKEN=TLDnkcL8YUppUW0BSndn4u0z/pnbcVz0JLsekNx6DidN4y2CYAA8Jw3Ixxwy/xIn
   ZIINA_APP_BASE_URL=https://snow-liwa.onrender.com
   ZIINA_TEST_MODE=false
   ADMIN_PIN=your_admin_pin
   TICKET_PRICE_AED=175
   ```

8. اضغط "Create Web Service"

**مميزات Render:**

- ✅ مجاني تماماً
- ✅ HTTPS تلقائي
- ✅ سهل الاستخدام
- ⚠️ قد ينام بعد 15 دقيقة من عدم الاستخدام

---

### 2. **Railway.app** (سريع جداً)

#### الخطوات

1. ارفع الكود على GitHub
2. اذهب إلى <https://railway.app>
3. سجل دخول بحساب GitHub
4. اضغط "New Project" → "Deploy from GitHub repo"
5. اختر المشروع
6. أضف Environment Variables (نفس القيم أعلاه لكن غير `ZIINA_APP_BASE_URL` للرابط الجديد)
7. Railway سيكتشف FastAPI تلقائياً وينشره

**مميزات Railway:**

- ✅ سريع جداً في النشر
- ✅ HTTPS تلقائي
- ✅ لا ينام
- ⚠️ خطة مجانية محدودة ($5 credit شهرياً)

---

### 3. **Fly.io** (احترافي)

#### الخطوات

1. نصب Fly CLI:

   ```powershell
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. سجل دخول:

   ```powershell
   fly auth login
   ```

3. من مجلد المشروع:

   ```powershell
   cd snow_liwa_web
   fly launch
   ```

4. أضف Environment Variables:

   ```powershell
   fly secrets set ZIINA_ACCESS_TOKEN=TLDnkcL8YUppUW0BSndn4u0z/pnbcVz0JLsekNx6DidN4y2CYAA8Jw3Ixxwy/xIn
   fly secrets set ZIINA_APP_BASE_URL=https://snow-liwa.fly.dev
   fly secrets set ZIINA_TEST_MODE=false
   fly secrets set ADMIN_PIN=your_admin_pin
   ```

5. انشر:

   ```powershell
   fly deploy
   ```

**مميزات Fly.io:**

- ✅ أداء ممتاز
- ✅ خوادم قريبة من الإمارات
- ✅ HTTPS تلقائي
- ⚠️ يحتاج بطاقة ائتمان للتسجيل

---

### 4. **DigitalOcean App Platform**

#### الخطوات

1. ارفع الكود على GitHub
2. اذهب إلى <https://cloud.digitalocean.com/apps>
3. اضغط "Create App"
4. اختر GitHub → المشروع
5. حدد:

   ```
   Type: Web Service
   Run Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

6. أضف Environment Variables
7. انشر

**مميزات DigitalOcean:**

- ✅ موثوق جداً
- ✅ خوادم في الإمارات
- ⚠️ مدفوع ($5/شهر)

---

## 📝 ملفات إضافية للنشر

سأقوم بإنشاء الملفات المطلوبة:

### Procfile (لـ Render)
