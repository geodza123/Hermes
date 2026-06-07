# 🪽 Hermes (@Geragermes_bot) — справочник «из коробки»

_Только стоковое. Добавленные MCP (knowledge-base, agentmemory, ruflo, miro, yougile) исключены._
_Hermes 0.15.1 · 2026-06-06 · Итого: 24 тулсета + ~91 скилл + 2 MCP по запросу._

---

## A. Тулсеты (низкоуровневые возможности) — 24

| Тулсет | Назначение | Статус |
|---|---|:--:|
| web | Поиск и скрейпинг в интернете | ✅ |
| browser | Автоматизация браузера | ✅ |
| terminal | Терминал, запуск процессов | ✅ |
| file | Файлы: чтение / запись / правка / поиск | ✅ |
| code_execution | Исполнение кода | ✅ |
| vision | Анализ изображений | ✅ |
| image_gen | Генерация изображений | ✅ |
| tts | Синтез речи (озвучка) | ✅ |
| skills | Управление скиллами | ✅ |
| todo | Планирование задач | ✅ |
| memory | Память | ✅ |
| session_search | Поиск по прошлым диалогам | ✅ |
| clarify | Уточняющие вопросы | ✅ |
| delegation | Делегирование подагентам | ✅ |
| cronjob | Задачи по расписанию | ✅ |
| messaging | Сообщения между платформами | ✅ |
| computer_use | Управление компьютером (macOS) | ✅ |
| video | Анализ видео | ✗ |
| video_gen | Генерация видео | ✗ |
| x_search | Поиск в X (Twitter) | ✗ |
| moa | Mixture of Agents | ✗ |
| context_engine | Движок контекста | ✗ |
| homeassistant | Умный дом (Home Assistant) | ✗ |
| spotify | Spotify | ✗ |
| yuanbao | Yuanbao AI | ✗ |

---

## B. Встроенные скиллы — описание каждого

### 🍎 Apple (5)
| Скилл | Что делает |
|---|---|
| `apple-notes` | Apple Notes через memo CLI: создавать, искать, править |
| `apple-reminders` | Apple Reminders через remindctl: добавлять, список, отмечать |
| `findmy` | Отслеживание устройств/AirTag через FindMy на macOS |
| `imessage` | Отправка/приём iMessage и SMS через imsg CLI |
| `macos-computer-use` | Управление рабочим столом macOS в фоне (скриншоты, мышь, клавиатура, скролл) |

### 🤖 AI-агенты (5)
| Скилл | Что делает |
|---|---|
| `claude-code` | Делегировать кодинг в Claude Code CLI (фичи, PR) |
| `codex` | Делегировать кодинг в OpenAI Codex CLI |
| `hermes-agent` | Настройка / расширение / доработка самого Hermes |
| `kanban-codex-lane` | Запуск Codex CLI изолированной линией под Kanban-воркера |
| `opencode` | Делегировать кодинг в OpenCode CLI (фичи, ревью PR) |

### 🎨 Креатив (20)
| Скилл | Что делает |
|---|---|
| `architecture-diagram` | Тёмные SVG-схемы архитектуры/инфры в HTML |
| `ascii-art` | ASCII-арт (pyfiglet, cowsay, картинка→ascii) |
| `ascii-video` | Видео/аудио → цветной ASCII (MP4/GIF) |
| `baoyu-article-illustrator` | Иллюстрации к статьям (тип × стиль × палитра) |
| `baoyu-comic` | Образовательные «знание-комиксы» |
| `baoyu-infographic` | Инфографика (21 макет × 21 стиль) |
| `claude-design` | Разовые HTML-артефакты (лендинг, дек, прототип) |
| `comfyui` | Генерация картинок / видео / аудио через ComfyUI |
| `creative-ideation` | Генерация идей через креативные ограничения |
| `design-md` | Создание/валидация DESIGN.md токен-спеков (Google) |
| `excalidraw` | Рисованные Excalidraw-диаграммы (JSON) |
| `humanizer` | «Очеловечить» текст: убрать AI-штампы |
| `manim-video` | Manim-анимации (математика в стиле 3Blue1Brown) |
| `p5js` | p5.js скетчи: генеративный арт, шейдеры, 3D |
| `pixel-art` | Пиксель-арт с палитрами эпох (NES, Game Boy, PICO-8) |
| `popular-web-designs` | 54 реальные дизайн-системы (Stripe, Linear, Vercel) в HTML/CSS |
| `pretext` | Браузерные демо через pretext (DOM-free текст-лейаут) |
| `sketch` | Черновые HTML-макеты: 2-3 варианта для сравнения |
| `songwriting-and-ai-music` | Написание песен + промпты для Suno |
| `touchdesigner-mcp` | Управление TouchDesigner через MCP |

### 📊 Data Science (1)
| Скилл | Что делает |
|---|---|
| `jupyter-live-kernel` | Итеративный Python через живое ядро Jupyter |

### 🚀 DevOps (4)
| Скилл | Что делает |
|---|---|
| `docker-container-diagnostics` | Диагностика Docker-контейнеров (логи, состояние) |
| `kanban-orchestrator` | Плейбук декомпозиции для оркестратора через Kanban |
| `kanban-worker` | Подводные камни/примеры для Kanban-воркеров |
| `webhook-subscriptions` | Вебхук-подписки: запуск агента по событиям |

### ✉️ Почта (1)
| Скилл | Что делает |
|---|---|
| `himalaya` | Почта IMAP/SMTP из терминала (Himalaya CLI) |

### 🎮 Игры (2)
| Скилл | Что делает |
|---|---|
| `minecraft-modpack-server` | Хостинг модовых Minecraft-серверов (CurseForge, Modrinth) |
| `pokemon-player` | Игра в Pokemon (эмулятор + чтение RAM) |

### 🐙 GitHub (6)
| Скилл | Что делает |
|---|---|
| `codebase-inspection` | Инспекция кодовой базы (LOC, языки) через pygount |
| `github-auth` | Настройка GitHub-авторизации (токены, SSH, gh CLI) |
| `github-code-review` | Ревью PR: диффы, инлайн-комментарии |
| `github-issues` | Создание/триаж/метки/назначение issues |
| `github-pr-workflow` | Жизненный цикл PR: ветка → коммит → CI → merge |
| `github-repo-management` | Клон/создание/форк репо, remotes, релизы |

### ♾️ MCP (1)
| Скилл | Что делает |
|---|---|
| `native-mcp` | MCP-клиент: подключение серверов, регистрация инструментов (stdio/HTTP) |

### 🎬 Медиа (5)
| Скилл | Что делает |
|---|---|
| `gif-search` | Поиск/скачивание GIF из Tenor |
| `heartmula` | Генерация песен (Suno-подобно) из текста + тегов |
| `songsee` | Аудио-спектрограммы и фичи (mel, chroma, MFCC) |
| `spotify` | Spotify: воспроизведение, поиск, очередь, плейлисты |
| `youtube-content` | Транскрипты YouTube → саммари / треды / блоги |

### 🧠 MLOps (9)
| Скилл | Что делает |
|---|---|
| `audiocraft-audio-generation` | Генерация музыки/звука (Meta AudioCraft) |
| `dspy` | Программирование промптов/пайплайнов (Stanford DSPy) |
| `evaluating-llms-harness` | Оценка LLM (lm-eval-harness) |
| `huggingface-hub` | HuggingFace CLI: поиск/скачивание/загрузка моделей и датасетов |
| `llama-cpp` | Локальный инференс LLM (llama.cpp) |
| `obliteratus` | Модификация весов LLM (abliteration) |
| `segment-anything-model` | Сегментация изображений (Meta SAM) |
| `serving-llms-vllm` | Раздача LLM через vLLM |
| `weights-and-biases` | Трекинг ML-экспериментов (W&B) |

### 📝 Заметки (1)
| Скилл | Что делает |
|---|---|
| `obsidian` | Чтение/поиск/создание/правка заметок в Obsidian |

### ⚙️ Продуктивность (12)
| Скилл | Что делает |
|---|---|
| `airtable` | Airtable через REST API |
| `calendar-meetings` | Встречи и календарь |
| `google-workspace` | Gmail, Calendar, Drive, Docs, Sheets (gws CLI/Python) |
| `linear` | Linear: задачи, проекты, команды (GraphQL) |
| `maps` | Геокодинг, POI, маршруты, таймзоны (OSM/OSRM) |
| `meeting-calendar` | Календарь встреч |
| `meeting-reminders` | Напоминания о встречах |
| `nano-pdf` | Правка текста/опечаток/заголовков в PDF (на естественном языке) |
| `notion` | Notion API + ntn CLI: страницы, базы, markdown |
| `ocr-and-documents` | Извлечение текста из PDF/сканов (pymupdf, marker-pdf) |
| `powerpoint` | Создание/чтение/правка .pptx (слайды, заметки, шаблоны) |
| `teams-meeting-pipeline` | Пайплайн саммари встреч в Teams |

### 🛡️ Red-teaming (1)
| Скилл | Что делает |
|---|---|
| `godmode` | Джейлбрейк LLM (Parseltongue, GODMODE, ULTRAPLINIAN) |

### 🔬 Research (5)
| Скилл | Что делает |
|---|---|
| `arxiv` | Поиск статей на arXiv (ключ, автор, категория, ID) |
| `blogwatcher` | Мониторинг блогов и RSS/Atom-лент |
| `llm-wiki` | LLM-вики Карпатого: строить/запрашивать markdown-базу |
| `polymarket` | Данные Polymarket: рынки, цены, ордербуки, история |
| `research-paper-writing` | Написание ML-статей (NeurIPS/ICML/ICLR) |

### 🏠 Умный дом (1)
| Скилл | Что делает |
|---|---|
| `openhue` | Управление Philips Hue (лампы, сцены, комнаты) |

### 📱 Соцсети (1)
| Скилл | Что делает |
|---|---|
| `xurl` | X/Twitter через xurl CLI: посты, поиск, DM, медиа |

### 💻 Разработка (12)
| Скилл | Что делает |
|---|---|
| `debugging-hermes-tui-commands` | Отладка слэш-команд Hermes TUI |
| `hermes-agent-skill-authoring` | Написание SKILL.md (frontmatter, валидатор, структура) |
| `hermes-s6-container-supervision` | Правка дерева supervision (s6) в Docker-образе Hermes |
| `node-inspect-debugger` | Отладка Node.js (--inspect + DevTools Protocol) |
| `plan` | Режим планирования: записать план в markdown, без исполнения |
| `python-debugpy` | Отладка Python (pdb + debugpy/DAP) |
| `requesting-code-review` | Пред-коммит ревью: security-скан, гейты, автофикс |
| `spike` | Одноразовые эксперименты для проверки идеи |
| `subagent-driven-development` | Исполнение планов через подагентов (2-этапное ревью) |
| `systematic-debugging` | 4-фазная отладка по корню причины |
| `test-driven-development` | TDD: RED-GREEN-REFACTOR, тесты до кода |
| `writing-plans` | Написание планов реализации (мелкие задачи, пути, код) |

### — Прочее (2)
| Скилл | Что делает |
|---|---|
| `dogfood` | Внутренний демо/тест-скилл Hermes |
| `yuanbao` | Интеграция с Yuanbao AI (Tencent) |

---

## C. Подключаются сами по запросу (MCP-каталог Nous) — `hermes mcp install <name>`
| Имя | Что даёт |
|---|---|
| `linear` | Поиск / создание / обновление задач, проектов и комментариев в Linear |
| `n8n` | Управление и инспекция n8n-воркфлоу (stdio-мост) |

> Многие из скиллов выше «подключаются на лету» при первом использовании (требуют авторизации к сервису: notion, github, google-workspace, spotify, obsidian, airtable, linear и т.д.).
