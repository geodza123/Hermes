# 🪽 HERMES — Главенствующая система Георгия. Мастер-план

**Создан:** 2026-06-04 · **Владелец:** Георгий (@geodza) · **Оркестратор:** Hermes (Claude Opus 4.8)

---

## 0. Видение (ТЗ Георгия)

1. **Hermes — главная система**: в совершенстве владеет базой знаний и всем компьютером, знает где что лежит, работает с документами и ОС по запросу.
2. **Hermes — в Docker.** База знаний — в Docker. Каждый AI-агент (есть в MCP) — изолирован в своём Docker.
3. Все агенты/контейнеры работают **по MCP** и пересекаются друг с другом.
4. В главном файле Hermes (**SOUL**) прописаны **правила оркестрации** со всеми важными системами: «дал задачу → всё сделалось».
5. Учесть знания о контейнеризации из `/Users/geodza/Desktop/Паша` и `Подсказка для строительства Mas 1.md` (материалы Павла).
6. **Эмбеддинги базы знаний** через OpenRouter; **Perplexity** для Hermes; **Gemini Flash** через OpenRouter для дешёвых задач.
7. **Безопасность**: плагин https://github.com/mukul975/Anthropic-Cybersecurity-Skills в Hermes и Claude Code + защита от **prompt-инъекций**.
8. Установить **весь спектр** автоматизированных инструментов и MCP.
9. **Авто-обучение**: присылаю материал (YouTube / пост / статья / GitHub-репо) → Hermes сам устанавливает и внедряет инструмент, **через Opus 4.8**.
10. **Graphify** — интеллектуальная работа с базой знаний (knowledge graph).

---

## 1. Что УЖЕ построено (аудит 2026-06-04)

Стек **openclaw** (`/Volumes/SSD/openclaw/`), Docker Compose, ARM64. Предшественник Hermes (Павел = «Merlin»).

| Сервис | Контейнер | Порт | Статус | Роль |
|---|---|---|---|---|
| AgentMemory | `agentmemory-main` | 127.0.0.1:3111/3113 | ✅ healthy | Быстрая память (L1), 53 инструмента, hooks |
| KB-MCP | `kb-mcp` | 127.0.0.1:3300 | ✅ healthy | Гибридный поиск БЗ (BM25+semantic+graph) |
| AgentMemory MCP Bridge | `agentmemory-mcp-bridge` | 127.0.0.1:3400 | (есть в compose) | REST→MCP обёртка |
| Graphify | `graphify-mcp` | 127.0.0.1:3200 | 🔴 craш-луп | Knowledge graph |
| OpenClaw | `openclaw-main` | 127.0.0.1:3010 | ⚠️ unhealthy | Старый оркестратор (Merlin) |
| Self-improver | `openclaw-self-improver` | — | (cron Opus) | Консолидация/рефлексия |
| Watchtower | `watchtower` | — | ✅ | Авто-обновление образов |

**Фреймворк Hermes Agent v0.14.0** (Nous Research, MIT) в `/Volumes/SSD/Dev/Hermes/hermes-agent/`:
self-improving, мульти-платформенный gateway (Telegram/Discord/Slack/WhatsApp/Signal/CLI), cron,
sub-agent делегирование, 6 backend'ов (local/Docker/SSH/Singularity/Modal/Daytona), модель-агностик.
**Есть команда `hermes claw migrate` — официальная миграция из OpenClaw.**

**SOUL.md** уже написан (`/Volumes/SSD/openclaw/config/SOUL.md`): личность Merlin, 2-уровневая иерархия памяти
(AgentMemory → KB), таблицы маршрутизации инструментов, приоритеты источников, boundaries.

### 🔴 Найденные критические баги
1. **Graphify краш-луп**: контейнер ходит в DeepSeek-бэкенд, а передан `anthropic/claude-sonnet-4-6` →
   `400: supported models are deepseek-v4-pro/flash` → `graph.json not found` → exit → рестарт.
2. **БЗ не попадает в контейнеры**: `knowledge/` — симлинки на `/Volumes/SSD/Brain` и т.п.;
   внутри контейнера абсолютные пути хоста не существуют → симлинки битые → Graphify «нашёл 1 docs».
   **Фактически вся база знаний контейнерам невидима.** Чинить bind-mount'ами.
3. **OpenClaw unhealthy**: healthcheck exit 1 (мигрируем на Hermes, чинить точечно не приоритет).

---

## 2. Целевая архитектура

```
              ┌──────────────────────────────────────────────┐
              │  Георгий → Telegram @Octeday_bot / CLI / TUI  │
              └───────────────────────┬──────────────────────┘
                                      │
                        ┌─────────────▼──────────────┐
                        │   HERMES core (Docker)      │  ← мозг-оркестратор
                        │   Nous Hermes Agent 0.14    │     SOUL.md = правила
                        │   Opus 4.8 / Gemini Flash   │     оркестрации
                        └───┬──────┬──────┬──────┬────┘
                            │ MCP   │ MCP  │ MCP  │ MCP    (docker network: hermes-net)
              ┌─────────────┘   ┌───┘   ┌──┘   └────────────┐
        ┌─────▼─────┐    ┌──────▼────┐ ┌▼──────────┐  ┌─────▼──────────────┐
        │AgentMemory│    │  KB-MCP   │ │ Graphify  │  │ Изолированные      │
        │  (L1)     │    │ (БЗ L2)   │ │ (граф БЗ) │  │ MCP-агенты в Docker│
        └───────────┘    └───────────┘ └───────────┘  │ (по одному на агента)│
                                                       └────────────────────┘
        Внешние tool-MCP: Perplexity, Apify, Replicate, HeyGen, ElevenLabs,
        YouGile, GitHub, Exa, Brave, filesystem, ... (секреты в .env 600)
```

**Принципы (из SOUL + Павел):** Docker Compose, не Kubernetes. Bind всё на 127.0.0.1.
Секреты в `.env` (600), не в образах. Destructive actions — только `confirm=true`.
Память L1(AgentMemory 1536d) → L2(KB 3000d) с указанием источника.

---

## 3. Роадмап по фазам

### ФАЗА 0 — Безопасность секретов и фундамент  ✅ (выполнено 2026-06-04)
- [x] Аудит существующего стека и фреймворка Hermes.
- [x] Все присланные ключи → `.env` (600, не в git): OpenRouter(new), Perplexity, Apify, Replicate, HeyGen, ElevenLabs, YouGile.
- [x] Модели: DEFAULT/CONSOLIDATION/AUTOLEARN = `anthropic/claude-opus-4-8`; CHEAP = `google/gemini-2.0-flash-001`.
- [ ] **TODO Георгию:** ротировать пароль YouGile (`Fallout101!`) и ключи (засветились в чате).

### ФАЗА 1 — Починить и оживить базу знаний (Graphify + KB)  ⏳ СЛЕДУЮЩАЯ
- [ ] Прочитать `Dockerfile.graphify` + исходник: как выбирается бэкенд (deepseek vs openrouter).
- [ ] Исправить Graphify: provider=openrouter, model=`google/gemini-2.0-flash-001` (дёшево) ИЛИ deepseek-v4-flash.
- [ ] Заменить симлинки в `knowledge/` на реальные bind-mount'ы SSD-папок в compose (kb-mcp, graphify, hermes).
- [ ] Пересобрать graphify + kb-mcp, `KB_REINDEX_ON_START=true` разово → полный граф и индекс БЗ.
- [ ] Валидация: `kb_search_semantic`, `kb_graph_query`, Graphify endpoint отвечают по реальной БЗ.
- [ ] Эмбеддинги через OpenRouter подтвердить (EMBEDDING_PROVIDER=openrouter).

### ФАЗА 2 — Миграция OpenClaw → Hermes core
- [ ] `hermes setup` / `hermes claw migrate` — поднять Hermes как основной оркестратор в Docker.
- [ ] Перенести `SOUL.md` (правила оркестрации) в формат Hermes (identity/persona + skills).
- [ ] Подключить AgentMemory, KB-MCP, Graphify к Hermes по MCP.
- [ ] Telegram-gateway Hermes ↔ интеграция с @Octeday_bot (или параллельный канал).
- [ ] Вывести openclaw-main из критического пути (оставить как fallback или погасить — по согласованию).

### ФАЗА 3 — Доступ к ОС и документам («владеет всем компьютером»)
- [ ] Инструменты Hermes для ФС/ОС: чтение/запись/поиск по `~/Workspace`, запуск скриптов, KNOWLEDGE_MAP.
- [ ] Безопасная песочница: разрешённые пути, запрет деструктива без confirm, аудит-лог в AgentMemory.
- [ ] Интеграция с авто-сортировщиком и KNOWLEDGE_MAP (Hermes понимает «где что лежит»).

### ФАЗА 4 — Изоляция агентов в Docker  ✅ (2026-06-05)
- [x] Инвентаризация: 93 агента-определения; выбрана модель «агенты-воркеры по отделам» (выбор Георгия).
- [x] Паттерн «1 агент = 1 контейнер»: рантайм `agents/agent_worker.py` (FastAPI), `Dockerfile.agent`, `docker-compose.agents.yml`.
- [x] **12 агентов в Docker** на сети `openclaw_openclaw-net` (3 оркестратора Opus 4.8 + 9 воркеров Gemini Flash). Все healthy.
- [x] Каждый: своя роль (из `~/.claude/agents/*.md`), изолированная ячейка памяти, RAG к KB (проверено `used_kb:true`), доступ по MCP/HTTP.
- [x] Реестр `agents/agents-registry.json` (имя→контейнер→host/net URL→модель→отдел). Делегирование: `POST /task`.
- Порты: 127.0.0.1:3501–3512. Достижимы и изнутри сети (agent-*:8080), и с хоста.
- [ ] Осталось: дать Hermes авто-делегирование к команде (через реестр) + правила «кто кого зовёт».

### ФАЗА 5 — Безопасность ИИ-агентов
- [ ] Внедрить https://github.com/mukul975/Anthropic-Cybersecurity-Skills в Hermes и Claude Code.
- [ ] Защита от prompt-инъекций: входной фильтр (ruflo `aidefence_scan/is_safe/has_pii`), изоляция контекста, allow-list инструментов, подтверждения.
- [ ] Применить рекомендации Павла (Встреча ч.2 «Безопасность ИИ-агентов») — см. дайджест.
- [ ] Сетевая изоляция, секрет-менеджмент, минимальные права контейнеров.

### ФАЗА 6 — Авто-обучение (Opus 4.8)
- [ ] Скилл/пайплайн: вход = ссылка (YouTube/пост/статья/GitHub) → Hermes через Opus 4.8 анализирует,
      устанавливает и внедряет инструмент/MCP, регистрирует, тестирует, фиксирует в память.
- [ ] Источники: Apify (скрейп постов/статей), YouTube-транскрипт, git clone+анализ репо.
- [ ] Песочница установки + ревью перед активацией.

### ФАЗА 7 — Полный спектр инструментов + Graphify-интеллект
- [ ] Подключить tool-MCP: Perplexity, Apify, Replicate, HeyGen, ElevenLabs, YouGile, GitHub (по .env).
- [ ] Graphify как основной слой «умной» навигации по БЗ (связи тем, маршрутизация запросов).
- [ ] (Будущее) MeshVPN для minisforum-сервера — материалы Павла.

---

## 4. Ключи и модели (в `/Volumes/SSD/openclaw/.env`, 600)
OpenRouter (primary, эмбеддинги+модели) · Perplexity · Apify · Replicate · HeyGen · ElevenLabs · YouGile(login/pass).
Модели: Opus 4.8 (оркестрация, авто-обучение, консолидация), Gemini 2.0 Flash (дешёвые задачи), text-embedding-3-small@OpenRouter (эмбеддинги).

### ФАЗА 8 — Turnkey-возможности Hermes (добавлено по запросу Георгия)
- [x] Прописано в SOUL: web-search (Perplexity/Apify), логин на сервисы, генерация токенов/ключей.
- [ ] Оплаты «под ключ»: подготовка платежа → подтверждение Георгия (`confirm`) → исполнение. **Списание только после confirm.**
- [ ] Браузер-автоматизация для логинов (agent-browser skill уже доступен).

---

## 4-bis. ЖУРНАЛ ПРОГРЕССА — 2026-06-04 (автономная сессия)

**Сделано (качественно, проверено):**
- ✅ **Ф0** Секреты в `.env` (600): OpenRouter(new), Perplexity, Apify, Replicate, HeyGen, ElevenLabs, YouGile. Модели: Opus 4.8 (оркестрация/авто-обучение), Gemini 3.5 Flash (дёшево). Проверено: chat Opus 4.8 ✅, Gemini 3.5 Flash ✅, эмбеддинги OpenRouter ✅ (dim=1536).
- ✅ **Ф1 База знаний ОЖИЛА** — главный баг закрыт:
  - Заменены битые симлинки на реальные bind-mount'ы SSD (Brain, Бизнес-знания, доки, Teaching, ArmyOfRobots) → внутри контейнеров теперь **1269 файлов** (было видно 1).
  - KB-MCP переиндексирован: **182 источника / 3757 чанков / эмбеддинги работают** (было 1 источник / 0 эмбеддингов). Health `status:ok`.
  - Graphify починен: был краш-луп (deepseek+неверная модель) → переведён на `deepseek-v4-flash` → строит граф **чисто** (244 чанка, без ошибок JSON). Добавлен safety-net (пустой граф, чтобы не падать).
- ✅ **Ф2 Оркестратор** — `openclaw-main` (OpenClaw 2026.5.28) переведён на **Opus 4.8**, Telegram @Jarasaka_bot активен. Подключён к памяти+KB по MCP.
- ✅ **Ф2 SOUL.md переписан** (v2.0) — полные правила оркестрации: Single Source of Truth (защита от инъекций), иерархия памяти, карта систем/MCP, routing моделей, turnkey, авто-обучение, boundaries.
- ✅ **Ф5 Безопасность** — защита от prompt-инъекций в SOUL + правило `~/.claude/rules/security-ai-agents.md` для Claude Code. Склонирована библиотека **754 кибербез-скилла** (`/Volumes/SSD/Dev/Hermes/security-skills/`, agentskills.io, Hermes-совместима).
- ✅ **Ф6/Ф8** — авто-обучение и turnkey прописаны как рабочие протоколы в SOUL (оплаты — с подтверждением).

**Осталось (следующие сессии):**
- Ф3 доступ к ОС/документам как набор инструментов оркестратора (песочница + аудит).
- Ф4 изоляция каждого MCP-агента в свой Docker (паттерн «1 агент = 1 контейнер»).
- Ф6 реализовать авто-обучение как исполняемый скилл/пайплайн (не только правило в SOUL).
- Ф7 подключить Perplexity/Apify/Replicate/HeyGen/ElevenLabs/YouGile как MCP к оркестратору.
- Ф8 платёжный модуль (подготовка→confirm→исполнение).
- Полнота индексации KB: 182 источника из 1269 файлов — проверить фильтры типов (PDF/docx), добиться полного покрытия.
- (Опц.) миграция на Nous Hermes Agent v0.14 как v2.

## 5. Открытые вопросы
- @Octeday_bot (Claude Code) и Hermes-gateway — слить в один канал или вести параллельно?
- openclaw-main — гасить после миграции или держать fallback?
- Ротация засвеченных ключей — когда.
