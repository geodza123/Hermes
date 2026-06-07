https://www.youtube.com/watch?v=4Yc9xfuEo2w


MESHVPN: Свободная сеть для смелых идей. Мгновенное соединение офисов, команд и ИИ-инфраструктуры без задержек и сложностей. Безопасно. Прямо. Надёжно. Стройте, запускайте, масштабируйте — где бы вы ни были. Ваша сеть, ваши правила, ваш результат.

GitHub-репозиторий:
AgentMemory GitHub
Список релизов:
AgentMemory Releases - https://github.com/rohitg00/agentmemory?utm_source=chatgpt.com"

https://github.com/rohitg00/agentmemory/releases?utm_source=chatgpt.com
Интересно, что:
stars уже улетели примерно к 18k+
repo активно пушится
но после 0.9.21 пока не видно публичного tagged release
Это обычно означает одно из:
готовят 0.10.x / 1.0
идут быстрые коммиты без stable tag
часть изменений уже в main/dev ветке, но не зарелизена официально
По косвенным признакам они сейчас активно пилят:
OpenCode parity
distributed/federated memory
smarter consolidation
better replay/context synthesis
MCP expansion
И да — судя по velocity проекта, 0.10 может выйти очень скоро.

Почему проект резко выстрелил
Он попал ровно в боль 2026:
Claude Code
Codex CLI
Cursor
OpenCode
Gemini CLI
все страдают от:
session amnesia
exploding token costs
lack of continuity
AgentMemory — один из первых, кто сделал:
“memory as infrastructure layer”а не “feature”.
Что еще мало обсуждают
Есть признаки, что рынок движется к:
Agent Runtime
+ Memory Runtime
+ Routing RuntimeИ AgentMemory пытается стать:
“SQLite for agent cognition”
Это уже отдельный infra-layer, а не plugin.

https://github.com/Hanukashats/AiSpase/releases/tag/agentmemory-standalone-v0.9.21

ссылка на мой Git с готовым образом (для нормальной работы нужен ваш api ключ от openrouter (или любой другой api к эмбединг модели)  для генерации ембедингов) практически не тратит токены количество векторов в RAG базе рекомендую не больше 1536 быстро и достаточно (в контейнере прописанно по умолчанию но можно менять)

вот и первый урок: развернуть докер контейнер с AGENTMEMORY  для своих агентов и подключить к ней агентов адаптировать скил  назначить примери памятью агентов

# образ без сборки
docker load -i agentmemory-standalone-0.9.21-image.tar
docker run -d --name agentmemory -p 3111:3111 \
  -e EMBEDDING_PROVIDER=openrouter \
  -e OPENROUTER_API_KEY="..." \
  agentmemory/standalone:0.9.21
docker exec agentmemory cat /data/.hmac

git clone https://github.com/Hanukashats/AI_DEMOS.git
cd AI_DEMOS