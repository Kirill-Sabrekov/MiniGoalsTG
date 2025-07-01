# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

# Frontend для MiniGoalsTG

## Запуск фронтенда

1. Перейдите в папку frontend:
   ```bash
   cd frontend
   ```
2. Установите зависимости (если ещё не установлены):
   ```bash
   npm install
   ```
3. Запустите dev-сервер:
   ```bash
   npm run dev
   ```
   По умолчанию приложение будет доступно на http://localhost:5173

## Запуск всего проекта

1. **Запустите backend** (FastAPI):
   ```bash
   cd ../backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
2. **Запустите frontend** (см. выше).
3. **(Опционально) Запустите Telegram-бота**:
   ```bash
   cd ../telegram
   python bot.py
   ```

## Как это работает
- Пользователь заходит по ссылке из Telegram-бота, где в URL есть параметр `user_id`.
- Фронтенд использует этот `user_id` для работы с вашими целями через REST API backend.
- Можно создавать, редактировать, удалять и просматривать свои цели.

---

Если backend и frontend работают на разных портах/хостах, убедитесь, что CORS разрешён в backend (уже настроено в main.py).
