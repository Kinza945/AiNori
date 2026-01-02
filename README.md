# AiNori Telegram Bot

Телеграм-бот с авторизацией через Shikimori, хранением токенов в Postgres и очередями в Redis. В разработке используется polling, в продакшене — HTTPS вебхуки.

## Настройка окружения
1. Сгенерируйте бота в [@BotFather](https://t.me/BotFather) и получите `BOT_TOKEN`.
2. Создайте OAuth-приложение в Shikimori и сохраните `SHIKIMORI_CLIENT_ID`, `SHIKIMORI_CLIENT_SECRET`, `SHIKIMORI_REDIRECT_URI`.
3. Сгенерируйте ключ для шифрования токенов:
   ```bash
   python - <<'PY'
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   PY
   ```
4. Скопируйте `.env.example` в `.env` и заполните значения.

## Локальный запуск
```bash
docker compose up --build
```
- Бот стартует в режиме polling.
- Вспомогательный сервер на `http://localhost:8080` обрабатывает `/oauth/callback`.

## Продакшн и вебхуки
1. Настройте домен с HTTPS и укажите `WEBHOOK_URL` (например, `https://bot.example.com`).
2. Откройте порт `HTTP_PORT` для входящих запросов и пробросьте его в инфраструктуре.
3. Пропишите `WEBHOOK_SECRET` для валидации запросов Telegram.
4. Перезапустите сервис: бот автоматически выставит вебхук и продолжит работу.

## Команды бота
- `/start` — отправляет ссылку на авторизацию в Shikimori.
- `/status` — показывает информацию о сохраненных токенах.
- `/refresh` — принудительно обновляет токен через Shikimori.

## Хранение и шифрование токенов
Токены сохраняются в таблице `user_tokens` Postgres с полями `access_token`, `refresh_token`, `expires_at`, `scope`. Перед записью значения шифруются при помощи `cryptography.Fernet` с ключом `FERNET_SECRET`.
