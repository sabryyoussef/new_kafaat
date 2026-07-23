# ردّ تفصيلي على ملاحظات اختبار كفاءات — مع إثبات وشاشات

**OpenProject:** [#385](https://projects.drpaws.ai/work_packages/385)  
**Parent:** [#87](https://projects.drpaws.ai/work_packages/87)  
**Related:** #351–#358  
**DB proofs:** `sabry-test` (primary) · `TR_K19` (notes)  
**Date:** 2026-07-22

---

## ملخص للعميل

أغلب البنود **منفَّذة في النظام**. عدة ملاحظات «غير موجودة» ناتجة عن **مكان الواجهة** أو **شروط تشغيل** (مثل جلسة حضور للـ QR)، وليست غياب الكود.

| # | ملاحظة المختبر | الحكم | إثبات الشاشة |
|---|----------------|--------|--------------|
| 1 | بحث برقم الهوية — Done | **منفَّذ** ✅ | `01_search_by_id.png` |
| 2 | حالة الطالب view-only | **قابلة للتعديل** (لبس مع Training Status) | `02_application_status.png` |
| 3 | رقم القسيمة غير موجود | **موجود** على فورم الطالب | `03_voucher_number.png` |
| 4 | اشرح Batch أوفلاين | **دليل عربي + Batch Intake** | `04_batch_intakes.png` + الدليل |
| 5 | Excel مبيعات لا يعمل | **منفَّذ تحت Students** (ليس Contact Pools) | `05_excel_assign_wizard.png` |
| 6 | الدورات لا تظهر | **بيانات/صلاحيات** (ليس باقٍ برمجي كامل) | `06_courses_list.png` |
| 7 | ترجمة عربية كاملة | **جزئي** — S4 / #357 معلّق | نص + ملاحظة |
| 8 | Batch QR غير موجود | **منفَّذ ومثبّت**؛ يحتاج Generate QR + `op.session` | `08_batch_qr.png` |

---

## 1) البحث برقم الهوية

**الرد:** تم التنفيذ ويعمل.

- الحقل: `op.student.id_number` (رقم الهوية)
- البحث من قائمة الطلاب + `name_search`
- OP: #351 · Odoo: #42

**كيف تجرب:** Students → شريط البحث → أدخل رقم الهوية → Enter.

**إثبات:** `evidence/screenshots/01_search_by_id.png`  
(Playwright: meeting_s1 · `s1_351_search_by_id_number.png`)

---

## 2) حالة الطالب (مقبول / مرفوض / تحت المراجعة / ملغي)

**الرد:** الحقل موجود و**قابل للتعديل**. المختبر غالباً نظر إلى حقل آخر.

| الحقل الصحيح | الحقل المُربك |
|--------------|---------------|
| **حالة الطالب** (`application_status`) — قابل للكتابة | **Training Status** (`training_status`) — محسوب و readonly |

قيم `application_status`: مقبول · مرفوض · تحت المراجعة · ملغي

**كيف تعدّل:** افتح ملف الطالب → **حالة الطالب** → غيّر → احفظ.  
لا تستخدم حقل Training Status لهذا الغرض.

**إثبات:** `evidence/screenshots/02_application_status.png`  
OP: #352 · Odoo: #43

---

## 3) رقم قسيمة الاختبار

**الرد:** الحقل موجود على فورم الطالب (مثبّت على sabry-test و TR_K19).

- الاسم في الواجهة: **رقم قسيمة الاختبار** (`voucher_number`)
- يظهر بعد رقم الهوية؛ قابل للبحث في القائمة

**إن لم يظهر:** حدّث الصفحة / امسح الكاش / تأكد من موديول `edafaa_student_profile`.

**إثبات:** `evidence/screenshots/03_voucher_number.png`  
OP: #353 · Odoo: #44

---

## 4) آلية الـ Batch أوفلاين

**الرد:** ليست مزامنة أوفلاين منفصلة؛ المقصود التشغيلي هو **Batch Intake** (استيراد دفعة من ملف).

**القائمة:** Students → General → **Batch Intakes**  
**الدليل:** `guides/USER_GUIDE_BATCH_AR.md`

باختصار: Intake → رفع **CSV UTF-8** → Validate → Course + Schedule Batch → Process → Assign to Batch.

ملاحظة: التحليل الحالي يرفض xlsx برسالة واضحة؛ استخدم CSV.

**إثبات:** `evidence/screenshots/04_batch_intakes.png`  
OP: #354 · Odoo: #45

---

## 5) توزيع المتدربين على المبيعات بـ Excel

**الرد:** منفَّذ تحت **الطلاب**، وليس Contact Pools.

| المسار الصحيح | المسار الخطأ |
|---------------|--------------|
| **Students → Excel assign to sales** | Contact Pools (توزيع يدوي/round-robin بدون Excel) |

- المعالج: `trainee.sales.assign.wizard`
- الأعمدة: `id_number` + `staff_login` و/أو `staff_email`
- النتيجة: `op.student.assigned_user_id` (موظف المبيعات المسؤول)

أسباب شائعة لفشل التجربة: فتح Contact Pools، رفع CSV بدل XLSX، نقص `openpyxl`، أو صلاحيات Sales Manager.

**إثبات:** `evidence/screenshots/05_excel_assign_wizard.png`  
OP: #355 · Odoo: #46

---

## 6) الدورات لا تظهر بعد الإنشاء

**الرد:** غالباً **تشغيل/بيانات/صلاحيات**، وليس غياب إنشاء السجل.

1. قائمة **Courses** المستقلة غالباً لمسؤولي SIS فقط.
2. غير الأدمن يرون الدورات عبر **Program → Linked Courses**.
3. دورة بلا `program_id` = يتيمة ولا تظهر تحت أي برنامج.

**إجراء مقترح:** ربط الدورة ببرنامج، أو منح صلاحية قائمة الدورات.

**إثبات سياق:** `evidence/screenshots/06_courses_list.png` (قائمة الأدمن ليست محدودة بدورتين)  
OP: #356 · Odoo: #47

---

## 7) الترجمة العربية للواجهة

**الرد:** **جزئي** — لا نغلق كـ Done.

- OpenEduCat: ترجمة جزئية (`ar_001`)
- بعض تسميات كفاءات عربية ثابتة في XML
- الترجمة الكاملة لموديولات Edafaa/SIS: ضمن **S4 / OP#357** (معلّق)
- حضور QR: يوجد `edafaa_batch_attendance/i18n/ar_001.po`

**إثبات:** لا لقطة «ترجمة كاملة»؛ البند مفتوح عمداً. راجع #357.

---

## 8) حضور الـ Batch + QR للمتدربين المسجّلين

**الرد:** منفَّذ ومثبّت (`edafaa_batch_attendance` 19.0.1.2.0 على sabry-test و TR_K19).

**أين:** افتح **Batch** → مجموعة **Attendance QR Check-in** → **Generate QR**.

**شروط التشغيل (Option A):**
1. وجود حصة نشطة `op.session` تغطي وقت المسح
2. توليد QR على الدفعة
3. الطالب مسجّل في الدفعة + حساب بوابة مربوط

بدون جلسة يظهر: لا توجد حصة نشطة (يبدو كعطل وهو سلوك متعمّد).

على **TR_K19** وقت الفحص: **0** دفعات لها QR مولَّد — لذلك المختبر لم يرَ الميزة حتى يُولَّد QR بعد جدولة جلسة.

**إثبات:** `evidence/screenshots/08_batch_qr.png` (+ check-in shots في الحزمة)  
OP: #358 · Odoo: #49 / #56

---

## English summary (for delivery comment)

Implementor delivered items **1–5 and 8** in code. Tester often looked in the wrong UI place, confused readonly `training_status` with editable `application_status`, missed `voucher_number` / Batch QR section, and expected Contact Pool Excel or auto session for QR. **Item 6** needs ops (`program_id` / ACL). **Item 7** remains open (S4/#357). **Item 8** needs TR_K19: schedule `op.session` → Generate QR → portal scan.

Playwright suites: `tests/playwright/meeting_s{1,2,3,5}` → screenshots mirrored into this pack.

---

## محتويات الحزمة

- هذا الملف
- `guides/USER_GUIDE_BATCH_AR.md`
- `evidence/screenshots/*` (مُسمّاة حسب البند)
- `WHATSAPP_UAT_NOTES_REPLY_AR.txt` (ملخص واتساب)
- `analysis/KAFAAT_UAT_NOTES_VERIFICATION_REPORT.md` (تقرير التحقيق الكامل)
