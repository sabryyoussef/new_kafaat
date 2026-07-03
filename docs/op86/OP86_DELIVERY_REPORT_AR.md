# تقرير تسليم — طلب كفاءت OP#86 (بيانات المتدرب)

**التاريخ:** 2026-07-01  
**الفرع:** `feature/op86-kafaat-trainee-request`  
**قاعدة الاختبار:** `sabry-test`  
**الحالة:** **مُنجَز — جاهز لاختبار القبول على بيئة العميل (Staging)**

---

## 1. ملخص تنفيذي

تم تنفيذ طلب كفاءت **OP#86** وفق الخطة المعتمدة، ويشمل:

- إصلاح ربط حقول المتدرب (العنوان، الهاتف، رقم الهوية، التخصص) عبر جميع مسارات الإدخال.
- تبسيط واجهات شاشة المتدرب وطلب التسجيل.
- إضافة فلاتر بحث للشهادات على قائمة المتدربين.
- إضافة معالج تعيين جماعي للمتدربين على الدفعات (Batch).

العمل الأساسي في وحدة **`edafaa_student_profile`** مع جسور في البورتال، القبول، استيراد الدفعات، وCRM.

---

## 2. نطاق التسليم

| الشاشة | النموذج | الغرض |
|--------|---------|--------|
| بيانات المتدرب | `op.student` | الملف الرئيسي للمتدرب |
| شاشة الطلب | `student.registration` | تسجيل الطلب والموافقة |
| مسارات ثانوية | `op.admission`، `batch.intake`، `res.partner` | دخول البيانات من القبول والاستيراد وCRM |

---

## 3. ما تم تسليمه حسب المراحل

| المرحلة | الأولوية | الحالة | المخرجات |
|---------|----------|--------|----------|
| 0 — الاكتشاف | بوابة | ✅ | [`PHASE_0_DISCOVERY.md`](PHASE_0_DISCOVERY.md) |
| 1 — ربط الحقول | P1 | ✅ | عنوان، هاتف، هوية، تخصص |
| 2 — تنظيف الواجهة | P1 | ✅ | عرض الهوية، إخفاء حقول غير ضرورية |
| 3 — فلاتر الشهادات | متوسط | ✅ | فلاتر وتجميع على `op.student` |
| 4 — تعيين الدفعات | متوسط | ✅ | معالج `batch.trainee.assignment.wizard` |
| 5 — التحقق | — | ✅ | 7 اختبارات وحدة + Playwright + لقطات شاشة |

---

## 4. إصلاح الحقول (مصدر البيانات المعتمد)

| الحقل (العميل) | التخزين المعياري | ما تم إصلاحه |
|----------------|------------------|--------------|
| **الجنسية** | `op.student.nationality` | إصلاح مسار القبول الذي كان يخلط الجنسية مع دولة العنوان |
| **العنوان** | `street`، `city`، `country_id` على الشريك | نسخ العنوان من التسجيل، القبول، استيراد CSV، والتكامل |
| **التخصص** | `specialization_id` → `op.program` | حقل جديد على المتدرب والطلب مع الربط في جميع المسارات |
| **رقم الهاتف** | `phone` (مفوّض من الشريك) | مزامنة عند الإنشاء/التعديل؛ نسخ `mobile` من القبول إلى `phone` |
| **رقم الهوية** | `op.student.id_number` | مصدر واحد؛ مزامنة مع الشريك؛ إيقاف استخدام `vat`/`ref` كبديل |

**قرار التخصص:** تم تنفيذ **التخصص** كحقل `specialization_id` مرتبط ببرنامج تدريبي (`op.program`).

---

## 5. الوحدات المعدّلة

| الوحدة | الإصدار | التغييرات الرئيسية |
|--------|---------|---------------------|
| `edafaa_student_profile` | 19.0.2.0.0 | حقول التخصص والشهادات، مزامنة الشريك، وراثة القبول، واجهات، اختبارات |
| `edafaa_student_profile_portal` | — | ربط التخصص والعنوان والهوية على التسجيل؛ إخفاء تبويب المستندات |
| `edafaa_training_crm` | 19.0.1.1.0 | الهوية من `id_number` فقط؛ إخفاء حقل الهوية على جهة الاتصال |
| `admission_integration` | — | فصل الجنسية عن عنوان الدولة؛ تمرير الهوية والعنوان والتخصص |
| `edafaa_batch_intake` | 19.0.2.0.0 | إثراء CSV، معالج التعيين الجماعي، صلاحيات |
| `batch_intake` | — | منسوخ إلى Git ومثبت على `sabry-test` |

---

## 6. تحسينات الواجهة

### شاشة المتدرب (`op.student`)
- عرض **رقم بطاقة الهوية** من `op.student.id_number`.
- إظهار **التخصص** (`specialization_id`).
- إخفاء/تقليل الحقول المربكة (مثل `category_id`).
- إزالة أعمدة `certificate_number` من تبويب الدورات (مع الإبقاء على منطق إصدار الشهادات في الخلفية).

### شاشة الطلب (`student.registration`)
- مجموعة **Student Profile Required Data**: الهوية، العنوان، التخصص.
- إخفاء تبويب **Documents** غير المستخدم.

### جهة الاتصال (CRM)
- إخفاء حقل الهوية على نموذج الشريك (المصدر المعياري: سجل المتدرب).

---

## 7. فلاتر الشهادات والتعيين الجماعي

### فلاتر البحث (قائمة المتدربين)
- **Has Previous Certificate** — شهادة سابقة من التسجيل.
- **Has Issued Certificate** — شهادة إصدار مكتملة.
- **تجميع حسب:** التخصص، نوع الشهادة.

### معالج تعيين الدفعة
- من قائمة `op.student` (تحديد متعدد) → **Assign to Batch**.
- اختيار المقرر والدفعة → إنشاء/تحديث سطور `op.student.course`.

---

## 8. نتائج الاختبار

### 8.1 اختبارات الوحدة (Odoo)

```bash
cp -a custom_addons/edafaa_* custom_addons/batch_intake custom_addons/admission_integration /opt/localaddons/
odoo -c /etc/odoo/odoo.conf -d sabry-test \
  -u edafaa_student_profile,edafaa_batch_intake \
  --test-enable --stop-after-init \
  --test-tags=/edafaa_student_profile,/edafaa_batch_intake \
  --http-port=8079
```

**النتيجة:** 7 اختبارات — **0 فشل، 0 أخطاء**

| الاختبار | الوحدة |
|----------|--------|
| مزامنة الهوية والهاتف مع الشريك | edafaa_student_profile |
| نسخ الهوية والجوال من القبول | edafaa_student_profile |
| حفظ التخصص على المتدرب | edafaa_student_profile |
| استخراج بيانات CSV | edafaa_batch_intake |
| حظر المعالجة بدون دفعة | edafaa_batch_intake |
| مزامنة الشريك مع batch intake | edafaa_batch_intake |
| وجود قائمة batch intake | edafaa_batch_intake |

### 8.2 اختبارات Playwright (واجهة)

```bash
cd tests/playwright/op86
npm install && npx playwright install chromium
ODOO_PASSWORD=admin npm test
```

**النتيجة:** **3/3 ناجحة** (2026-07-01)

| الاختبار | ما يتحقق منه |
|----------|--------------|
| قائمة المتدربين (Kanban) | تحميل SIS → طلاب |
| نموذج المتدرب | ID Number، Specialization، Phone |
| نموذج التسجيل | حقول OP86 (هوية، عنوان، تخصص) |

---

## 9. أدلة القبول (لقطات الشاشة)

المسار: [`docs/op86/evidence/screenshots/`](evidence/screenshots/)

| الملف | المحتوى |
|-------|---------|
| `01_student_list.png` | قائمة المتدربين (Kanban) |
| `02_student_list_filters.png` | شريط البحث والفلاتر |
| `03_trainee_form.png` | نموذج المتدرب — هوية، تخصص، عنوان، هاتف |
| `04_registration_form.png` | نموذج الطلب — مجموعة بيانات الملف المطلوبة |
| `04b_registration_list.png` | Kanban طلبات التسجيل |
| `05_student_multi_select.png` | تحديد متعدد على قائمة المتدربين |

---

## 10. ترقية النظام (Staging / Production)

```bash
# مزامنة الكود
cp -a custom_addons/edafaa_* custom_addons/batch_intake custom_addons/admission_integration /opt/localaddons/

# ترقية الوحدات
odoo -c /etc/odoo/odoo.conf -d <DATABASE> \
  -u edafaa_training_crm,edafaa_student_profile,edafaa_student_profile_portal,\
edafaa_batch_intake,batch_intake,admission_integration \
  --stop-after-init --http-port=8079
```

**بعد الترقية:** إعادة تحميل خدمة Odoo (أو إرسال إشارة HUP للعمال).

---

## 11. ملاحظات مهمة

1. **لا تثبّت** `batch_intake_processor` مع `batch_intake` على نفس قاعدة البيانات (تعارض نموذج `batch.intake`).
2. **تجنب** الاعتماد الدائري بين `edafaa_student_profile` و`edafaa_training_crm` في الـ manifest؛ إصلاح واجهة هوية الشريك في CRM.
3. **إصلاح عرض قائمة المتدربين:** تم تعديل `student_search_views.xml` لعدم إعلان `specialization_id` كـ `<field>` في البحث (فلاتر وتجميع فقط) — يمنع خطأ OWL `Unknown field specialization_id`.
4. **اختبار القبول على Staging** مطلوب قبل الإنتاج — راجع [`UAT_CHECKLIST.md`](UAT_CHECKLIST.md).

---

## 12. المستندات المرفقة

| المستند | الوصف |
|---------|--------|
| [`PHASE_0_DISCOVERY.md`](PHASE_0_DISCOVERY.md) | مصفوفة مصادر الحقول |
| [`OP86_IMPLEMENTATION_REPORT.md`](OP86_IMPLEMENTATION_REPORT.md) | تقرير التنفيذ (إنجليزي) |
| [`UAT_CHECKLIST.md`](UAT_CHECKLIST.md) | قائمة تحقق القبول |
| [`evidence/README.md`](evidence/README.md) | دليل Playwright واللقطات |

---

## 13. التوقيع

| الدور | الاسم | التاريخ | الحالة |
|------|-------|---------|--------|
| فريق التطوير (Edafaa) | | 2026-07-01 | ✅ مُسلَّم للاختبار |
| مسؤول كفاءت | | | ☐ قبول Staging |
| | | | ☐ قبول Production |

---

*نهاية تقرير التسليم — OP#86*
