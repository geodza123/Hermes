# Hermes Runtime Config — снимок настроек

Снимок рабочей конфигурации Hermes (~/.hermes/) без секретов.
Содержит: оркестрацию моделей, плагины, подключения MCP.

## Что внутри
- `config.yaml` — модели, оркестрация, MCP-серверы, display (ключи — через ${VAR}, не хранятся тут)
- `SOUL.md` — идентичность агента + карта маршрутизации моделей/инструментов
- `plugins/perplexity/` — research с источниками и учётом трат
- `plugins/replicate/` — генерация картинок (FLUX 1.1 Pro Ultra) и видео (Google Veo 3)

## Подключено (на момент снимка)
- OpenRouter (341 модель), Perplexity, Replicate
- MCP: GitHub (48), Firecrawl (20 + 30 skills), YouGile (57)
- Оркестрация: основной minimax-m3, подагенты deepseek-v4-pro, fallback minimax-m3

## Восстановление / откат
```bash
cp config.yaml ~/.hermes/config.yaml
cp SOUL.md ~/.hermes/SOUL.md
cp -R plugins/* ~/.hermes/plugins/
hermes gateway restart
```
Секреты (API-ключи) живут в ~/.hermes/.env — не в этом снимке. После отката
убедись, что нужные ключи есть в .env (OPENROUTER_API_KEY, PERPLEXITY_API_KEY,
REPLICATE_API_TOKEN, GITHUB_PERSONAL_ACCESS_TOKEN, FIRECRAWL_API_KEY).
