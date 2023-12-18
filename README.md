# **Crawler**
#### Сенников Дмитрий, Плюснина Елена ФТ-203
---
### 1) **cache.py**
Класс для создания кэша посещённых и непосещённых ссылок

    load - загрузка

    save - сохранение

### 2) **parse.py**

    download_url - получение текста странички по url-ссылке

    HTML_parser - парсер, собирающий все внутренние ссылки странички

### 3) crawler.py
Класс для создания краулера 

    work - для всех непосещённых ссылок многопоточно выполняет _task и периодически обновляет кэши

    _task - выгружает текст, парсит в html и сохраняет его с помощью _save_html

    _update_links - должен обновлять непосещённые ссылки

    _save_html - сохраняет html

    _robot_parser - обработка robots.txt


### Запуск 

    python main.py [-u https://wikipedia.org] [-rc 1] [-th 1000] [-fo https://ru.wikipedia ...] [-fe https://ru.wikipedia.org/wiki ...] [-r] [-c]

Помощь в консоли

    python main.py -h