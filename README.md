A Demo Multiimport App
===

## Задача 
Необходимо очень часто импортировать данные из большого количества различных внешних xml/json источников в существующую реляционную модель данных.Стоит учесть, что структура и формат данных источника и конечной модели могут существенно различаться, иметь взаимозависимости(например документ содержащий множество зависимых M2M данных вида событие-дата-место), а данные импортироваться лишь частично.Задача: спроектировать и реализовать сервис, который позволит гибко, быстро и просто собирать данные из внешних источников и складывать в существующие таблицы.
* в рамках тестового задания достаточно реализовать RSS feed в качестве источника данных 
* при проектировании следует учесть возможность подключения других произвольных источников данных в будущем 
* функционал должен быть покрыт тестами

По реализации желательно сделать библиотеку которая будет содержать общий функционал маппера и микросервис работающий с ней.

## Реализация

Состав демо-приложения:

1. генератор RSS-feed (web, aiohttp)
2. библиотека-маппер RSS <-> database: Python package `demo-mapper==1.0`, исходный код в каталоге `lib-demo`
3. воркер-агрегатор RSS (Django + aiohttp)

Используются 2 фреймворка: aiohttp и Django. 

Aiohttp используется для веб-воркера - генератора RSS-feed и для производства
http-запросов из джанго-воркера агрегатора. 

Модели описаны в виде Django-моделей, как в целях демонстрации, 
так и потому, что в качестве базы данных выбрана SQLite, работа с которой в любом
случае производится синхронно. Также Django-админ панель используется для конфигурации источников RSS.



## Запуск

Основные задачи описаны в Makefile:

* `make runserver` - запуск Django-сервера с админ-панелью по адресу http://localhost:8000/admin .
  Эта задача подготовит виртуальное окружение, включая установку пакета маппера,
  выполнит миграции и загрузит исходные данные - 3 источника RSS, 
  с URL ссылающимися на воркер-генератор RSS-feed. Также создаст юзера c логином `admin` для админ-панели Django - необходим ввод пароля
  в консоли.

* `make rss_generator` - запуск воркера-генератора RSS-feed. Он будет доступен по URL 
    http://localhost:18000/feed/11211/ , где вместо 11211 можно подставить любое целое число.

* `make rss_aggregator` -  запуск воркера-агрегатора RSS (выполнит 1 проход по источникам).
    Альтернативно, можно выполнить `./manage.py aggregator_worker -i -t 30` для бесконечного опроса источников с интервалом 30 сек, 
    до нажатия Ctrl-C.
    
    Примечание: для данного воркера необходим либо установленный пакет `demo-mapper==1.0`, который устанавливается при
    запуске с помощью `make`, либо установка python path, например: 
    ```
    PYTHONPATH=.:./lib-demo ./manage.py aggregator_worker
    ```  
    В этом случае будет использован не пакет, а исходный код маппера. 

* `make test` - запуск тестов пакета маппера 
    

## Прочее

Так как объём и так вышел достаточно большой, для экономии времени не были написаны тесты
на функционал, не входящий в пакет маппера. Coverage 100% для файла `mapper/base.py`.
    
    


