# Wolfin Senior plugin

[English](README.md) · **العربية**

> الاسم التقني: `wolfin-senior`، لأن أسماء الـ plugins ما تقبل مسافات. والسكلز تظهر باسم `wolfin-senior:<skill>`.

مجموعة سكلز لـ Claude Code تخلّيه يشتغل مثل مهندس برمجيات كبير، مو بس "واحد يكتب كود".
تجمع أفضل ما في [superpowers](https://github.com/obra/superpowers)، و**قائمة الأداء (31 معيار)**،
و**القواعد الـ19 لهندسة البرمجيات**، و**مبادئ الكود العشرة**، و**دورة حياة تطوير البرمجيات (SDLC)**،
كلها مربوطة ببعض.

> **الشرح الكامل مع المخططات:** [docs/how-it-works.md](docs/how-it-works.md) · **Full guide in English:** [docs/how-it-works.en.md](docs/how-it-works.en.md)

## السكلز

| مرحلة SDLC | السكل | شنو يسوي |
|---|---|---|
| — | `using-wolfin-senior` | الموجّه: يختار السكل المناسب قبل أي عمل، ويحوّل القواعد الـ19 إلى سلوك |
| 01 المتطلبات · 02 التصميم | `requirements-and-design` | يفهم الطلب قبل البناء: أسئلة ذكية، 2-3 حلول مع المقايضات، وثيقة تصميم و ADR، وما يبدأ يكتب كود قبل الموافقة |
| 03 التطوير | `writing-plans` | يحوّل التصميم إلى خطة مهام صغيرة: ملفات، توقيعات، اختبارات، أوامر، ومخرجات متوقعة |
| 03 التطوير | `executing-plans` | ينفّذ الخطة (بنفسه، أو بوكيل جديد لكل مهمة مع مراجعة، أو بالتوازي) مع سجل يصمد بعد ضغط السياق |
| 03 التطوير | `docs-first` | قبل ما يبرمج أي شي: يقارن الإصدارات المنصّبة بالمشروع مع آخر إصدار، ويقرأ الدوكيومنتيشن الرسمي الحالي وسجل التغييرات للـ APIs اللي راح يستخدمها، بدل ما يعتمد على ذاكرته |
| 03 التطوير | `test-driven-development` | يكتب الاختبار أولاً ← يشوفه يفشل ← أقل كود ← إعادة ترتيب |
| 03 التطوير · 06 الصيانة | `engineering-principles` | المبادئ العشرة: المعايير، التوثيق، المتانة، SOLID، سهولة الاختبار، التجريد المعتدل، الأنماط، تقليل الاعتماديات العامة، إعادة الهيكلة المستمرة، الأمان |
| 04 الاختبار | `systematic-debugging` | ما يصلّح شي قبل ما يلگه السبب الجذري. بعد 3 محاولات فاشلة يوگف ويناقش التصميم |
| 04 الاختبار | `verification-before-completion` | ما يگول "خلص" أو "اشتغل" بدون ما يشغّل الأمر ويقرأ النتيجة |
| 04 الاختبار | `code-review-workflow` | مراجعة ذاتية، ووكيل مراجعة مستقل، وكتابة مراجعة مفيدة، واستقبال الملاحظات بدون مجاملة |
| 05 النشر · 06 الصيانة | `finishing-and-shipping` | رسائل commit مفيدة، و merge أو PR، وقائمة جاهزية النشر (migrations، rollback، مراقبة)، وقائمة المتابعات |
| كل المراحل | `project-memory` | ذاكرة دائمة وسجل خطوات: وين وصلنا (NOW)، وشنو انسوّى خطوة بخطوة (journal)، والقرارات والتفضيلات والدروس، حتى ما ينسى بين الجلسات ولا بعد ضغط المحادثة |
| 06 الصيانة | `performance-optimization` | فحص الأداء: يفحص الكود أولاً، ويقيس على جهاز بطيء وشبكة ضعيفة، ويطلع تقرير بحالة كل معيار من الـ31 وأولويته وتأثيره، ويطبّق المناسب بس، وحدة وحدة، مع قياس قبل وبعد |

### فحص الأداء: المعايير الـ31
Skeleton Loading · WebP/AVIF · Lazy Loading · Code Splitting · SSR/SSG · Third-Party Scripts · Font Optimization ·
Unused Dependencies · Debounce · Optimistic UI · Virtualization · Unnecessary Re-renders · AI Streaming · CDN ·
Brotli/Gzip · Browser Caching · Duplicate API Calls · Parallel Requests · Pagination · API Timeouts · N+1 Queries ·
Database Indexes · Required Columns Only · Connection Pooling · Redis Caching · Background Job Queue ·
Server/DB Proximity · Load Balancing · OpenTelemetry · Real User Monitoring · Performance Testing

لكل معيار في [`checklist.md`](skills/performance-optimization/references/checklist.md): شلون يتكشف بالكود، ومتى ينطبق ومتى لا،
وشكله الصحيح، وشلون يتقاس، ومخاطره. وسكربت [`inventory.py`](skills/performance-optimization/scripts/inventory.py) يجمع أدلة من المشروع بثانية
(نوع الإطارات، أحجام الصور والخطوط، مكتبات ممكن ما مستخدمة، وإشارات لكل معيار).
الأمور اللي تضيف بنية تحتية أو كلفة (Redis، CDN، Load Balancer، تغيير قاعدة البيانات) ما تتطبق إلا بموافقتك.

## الدوكيومنتيشن أولاً، على آخر تحديث

معلومات النموذج عن المكتبات إلها تاريخ انتهاء، والفريم ووركات تتغيّر باستمرار. لهذا قبل أي كود:

1. **يعرف الإصدارات الحقيقية** من الـ manifests والـ lockfiles، ويقارنها بآخر إصدار مستقر. سكربت [`versions.py`](skills/docs-first/scripts/versions.py) يسأل npm و PyPI و Go و crates.io و RubyGems و Packagist و pub.dev، ويسأل endoflife.date عن اللغات (Node و Python و Go و Ruby و PHP)، ويطلّع جدول يأشّر على كل شي متأخر إصدار رئيسي أو منتهي الدعم، مع رابط الدوكيومنتيشن لكل مكتبة.
2. **يقرأ الدوكيومنتيشن الرسمي** لنفس الإصدار المنصّب، وسجل التغييرات لحد آخر إصدار، بس للمواضيع اللي راح يستخدمها.
3. **بمشروع موجود** يبرمج على الإصدار المنصّب، وإذا المشروع متأخر يگلك ويقترح ترقية كمهمة مستقلة. **بمشروع جديد** يستخدم آخر إصدار مستقر.
4. **يحفظ اللي فحصه بالذاكرة** حتى ما يعيده كل مرة، ويعيد الفحص إذا تغيّر الإصدار أو مرّ أكثر من 30 يوم.

## الوضع الصارم: يلتزم بيها حرفياً

أي agent ينصّب هذا الـ plugin يتعامل ويا السكلز كتعليمات إلزامية، مو اقتراحات:
- يحمّل كل سكل ينطبق قبل ما يرد، ويعلن عنه، ويطبّق خطواته كلها بالترتيب، بدون تخطي أو دمج أو "تكييف".
- ماكو أحد يلغي خطوة إلا إنت، وبصراحة. وإذا خطوة ما تنسوّى، يگول هذا بوضوح.
- لما يرسل وكيل فرعي يكتب كود، يحط بأمره نفس القواعد (الدوكيومنتيشن، TDD، التحقق).

**والـ hooks تفرض أهم القواعد تلقائياً:**

| الـ hook | يشتغل | يفرض |
|---|---|---|
| `session-start` | ببداية الجلسة وبعد الضغط | يحقن الموجّه كتعليمات إلزامية، ويحقن الذاكرة |
| `prompt-reminder` | مع كل رسالة | تذكير قصير بالقواعد (حوالي 100 token) |
| `code-gate.py` | قبل كل تعديل كود | يرفض التعديل لحد ما ينحمّل `docs-first` و `test-driven-development` (بعد 3 رفضات يسمح، حتى ما يعلّق الجلسة) |
| `stop-gate.py` | بنهاية كل دور | إذا تغيّر كود بعد آخر اختبار، لازم يشغّل الاختبارات. وإذا تغيّر أي شي، لازم يسجّل بالذاكرة |

**الإيقاف** (كل واحد لوحده): `WOLFIN_CODE_GATE=off` و `WOLFIN_VERIFY_GATE=off` و `WOLFIN_MEMORY_GATE=off` و `WOLFIN_REMINDER=off`.

## الذاكرة: ما ينسى، ويسجّل خطواته

ذاكرة كل مشروع تنحفظ في `.wolfin-senior/memory/` بجذر المشروع. وإذا اشتغلت بـ git worktrees، كلها تشترك بنفس الذاكرة:

```
.wolfin-senior/memory/
├── NOW.md               وين وصلنا: المهمة الحالية، شنو خلص، الخطوة الجاية، شنو ننتظر
├── MEMORY.md            فهرس: سطر واحد لكل معلومة محفوظة
├── journal/2026-11-04.md سجل الخطوات: شنو انطلب، شنو انسوّى، شلون انفحص (الأمر ونتيجته)، القرارات
└── <topic>.md           معلومة دائمة: قرار، تفضيل، قاعدة بالمشروع، درس من خطأ
```

والتفضيلات العامة اللي تنطبق على كل المشاريع (مثلاً لغة الجواب) تنحفظ في `~/.claude/wolfin-senior/memory/`.

**شلون يضمن إنه ما ينسى:**
- **ببداية كل جلسة**، وبعد ضغط المحادثة (compact)، وبعد الاستئناف: hook يحقن NOW.md والفهرس وآخر السجل داخل السياق تلقائياً.
- **بنهاية كل دور:** إذا عدّل ملفات أو سوّى commit وما سجّل بالـ journal أو حدّث NOW.md، فـ `stop-gate.py` يوقفه مرة وحدة ويطلب منه يسجّل قبل ما يخلص.
- **ما يحفظ أسرار أبداً** (كلمات سر، توكنات، مفاتيح). يحفظ بس مكانها.
- الذاكرة محلية: الـ hooks تضيفها لـ `.git/info/exclude` تلقائياً، فما تنرفع للـ repo إلا إذا طلبت.

## التثبيت

**جرّبه بجلسة وحدة بدون تنصيب:**
```bash
claude --plugin-url https://wolfin.app/downloads/wolfin-senior.zip
```

الوضع الصارم يشتغل بس إذا نصّبته كـ plugin (من GitHub أو من wolfin.app)، لأن الـ hooks تشتغل بس بهالشكل.

**الطريقة 1: كـ plugin من GitHub (الأسهل)**

```bash
claude plugin marketplace add wolfinApp/wolfin-senior
```
```bash
claude plugin install wolfin-senior@wolfin-senior-marketplace
```

وللتحديث بعدين: `claude plugin marketplace update wolfin-senior-marketplace`

**أو من wolfin.app بدون GitHub:**

```bash
curl -LO https://wolfin.app/downloads/wolfin-senior.zip && unzip -o wolfin-senior.zip -d ~
```
```bash
claude plugin marketplace add ~/wolfin-senior
```
```bash
claude plugin install wolfin-senior@wolfin-senior-marketplace
```

**الطريقة 2: كسكلز شخصية (بدون hooks، يعني ماكو فرض تلقائي: لا ذاكرة تنحمّل، ولا فحص قبل الكود، ولا فحص بنهاية الدور)**

```bash
mkdir -p ~/.claude/skills && ln -s ~/wolfin-senior/skills/* ~/.claude/skills/
```

بعدها افتح جلسة جديدة. السكلز تشتغل تلقائياً حسب الطلب، أو تگدر تطلبها بالاسم، مثلاً:
"استخدم performance-optimization وافحص المشروع".

## ليش السكلز بالإنگليزي؟

محتوى السكلز بالإنگليزي لأن النموذج يلتزم بالتعليمات الإنگليزية بدقة أعلى، والمصادر الأصلية كلها إنگليزية.
بس الأوصاف بيها كلمات عربية حتى تشتغل لما تكتب بالعربي، والموجّه يگول لـ Claude يجاوبك بلغتك.

## الهيكل

```
.claude-plugin/        plugin.json + marketplace.json
hooks/session-start    يحقن الموجّه الإلزامي والذاكرة ببداية كل جلسة وبعد الضغط
hooks/prompt-reminder  تذكير قصير بالقواعد مع كل رسالة
hooks/code-gate.py     يرفض تعديل الكود لحد ما ينحمّل docs-first و TDD
hooks/stop-gate.py     نهاية الدور: اختبر بعد آخر تعديل كود، وسجّل بالذاكرة
skills/docs-first/scripts/versions.py  الإصدارات المنصّبة مقابل آخر إصدار، مع روابط الدوكيومنتيشن
skills/<name>/SKILL.md السكل نفسه
skills/<name>/references/  مراجع تنقرى عند الحاجة فقط (توفّر السياق)
skills/performance-optimization/scripts/inventory.py
```

## المصادر والترخيص

MIT. أجزاء من سكلز سير العمل مقتبسة ومعدّلة من [obra/superpowers](https://github.com/obra/superpowers)
(MIT، © 2025 Jesse Vincent). التفاصيل في [LICENSE](LICENSE).
القواعد الـ19 ومبادئ الكود العشرة (ByteByteGo) ومراحل SDLC مأخوذة من الصور اللي تم تزويدها كإطار، وانكتبت من جديد كتعليمات عملية.
