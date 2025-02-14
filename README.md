# Discord Bot - Leveling System
---

# EN

## 📌 Description
This bot is designed to interact with members of a Discord server. It adds an experience (EXP) system that awards points for sending messages in chat and joining voice channels. Users can check their experience points using the `/rank` command. The bot also includes commands for configuration and role management.

## ⚙️ Commands

### 🎛 HelpCommand
- `sl.help` - Displays help information about the bot's commands.

### 📈 Leveling
- `sl.set_channel` - Set up a channel for level-up messages.
- `sl.set_exp_range` - Configure the experience gain range. (Admins only.)

### 🎭 RoleManagement
- `sl.edit_rank` - Modify a user's level and experience, update linked roles.
- `sl.set_roles` - Assign roles that are granted upon reaching a certain level.
- `sl.show_roles` - Display a table of roles and levels.

### 🏆 Leaderboard
- `sl.leaderboard` - Shows the leaderboard based on EXP.

## 📦 Installation and Setup

### 🔧 Required Libraries
This bot uses the following libraries:
- `disnake`
- `dotenv`
- `os`
- `json`
- `random`
- `time`

### 📜 Installing Dependencies
Install the required packages using pip:
```bash
pip install -r requirements.txt
```

### 🔑 Setting Up Environment Variables
Create a .env file in the root directory of the project and add your Discord token:
```env
DISCORD_TOKEN=your_token_here
```
### 🚀 Running the Bot
Run the bot using the following command:
```bash
python main.py
```

### 🤝 Contribution
If you have ideas for improving the bot, feel free to create a pull request or issue in the repository!

### 📜 License
This project is licensed under the MIT License.

---

# RU

## 📌 Описание
Данный бот предназначен для работы с участниками Discord-сервера. Он добавляет систему опыта (EXP), которая начисляется за отправку сообщений в чат и заход в голосовые каналы. Полученные очки опыта можно посмотреть с помощью команды `/rank`. Также предусмотрены команды для настройки бота и управления ролями.

## ⚙️ Команды

### 🎛 HelpCommand
- `sl.help` - Выводит справочную информацию о командах бота.

### 📈 Leveling
- `sl.set_channel` - Настроить канал для отправки сообщений о достижении уровня.
- `sl.set_exp_range` - Настроить диапазон получения опыта. (Только для администраторов.)

### 🎭 RoleManagement
- `sl.edit_rank` - Изменить уровень и опыт пользователя, обновить привязанные роли.
- `sl.set_roles` - Привязать роли, выдаваемые при достижении уровня.
- `sl.show_roles` - Показать список ролей и уровней в виде таблицы.

### 🏆 Лидерборд
- `sl.leaderboard` - Показывает таблицу лидеров по EXP.

## 📦 Установка и настройка

### 🔧 Требуемые библиотеки
Бот использует следующие библиотеки:
- `disnake`
- `dotenv`
- `os`
- `json`
- `random`
- `time`

### 📜 Установка зависимостей
Установите необходимые пакеты с помощью pip:
```bash
pip install -r requirements.txt
```

### 🔑 Настройка переменных окружения
Создайте файл .env в корневой папке проекта и добавьте ваш Discord-токен:
```env
DISCORD_TOKEN=your_token_here
```
### 🚀 Запуск бота
Запустите бота с помощью следующей команды:
```bash
python main.py
```

### 🤝 Контрибьюция
Если у вас есть идеи для улучшения бота, создайте pull request или issue в репозитории!

### 📜 Лицензия
Этот проект распространяется под лицензией MIT.
