# KEKS
ЕРП система для школьной столовой

Реализовано в виде Телеграм-бота на Python с использованием библиотеки aiogram

## Инструкции по использованию
1. Склонируйте этот репозиторий
2. Перейдите в каталог проекта
3. Настройте ваш сервер Postgres и введите всю необходимую информацию в файле
[`config.ini`](config.ini)
4. Добавьте токен вашего бота и id пользователя telegram в секцию `bot` в файле
[`config.ini`](config.ini)
    Это необходимо для доступа ко всем коммандам для пользователя с указанным
    id.

    Также необходимо передать токен бота как параметр запуска в файле
    [`test.sh'](test.sh)
    В файле [`config.ini`](config.ini) значение `bot.token` скоро будет
    удалено, и на самом деле уже не используется
5. Создайте виртуальное окружение. Например, virtualenv:
    ```bash
    python3 -m venv venv
    . venv/bin/activate
    ```
6. Установите все необходимые пакеты:
    ```bash
    python3 -m pip install -r requirements.txt
    ```
6. Запустите бота с помощью `./test.sh`

## Справка по коммандам
<details>
<summary>Инструкции для обычного пользователя</summary>

Начните с команды `/start`.
Бот спросит ваше имя пользователя, и необходимо будет ввести команду
`/username <ваше имя пользователя>`.
Ваше имя пользователя будет видно кассиру при получении заказа

Вы можете разместить новый заказ коммандой
`/order <название пункта меню> <количество>`.
Меню доступно по команде `/menu`.
Если будет заказано что-то, отсутствующее в меню - будет отображено сообщение
об ошибке
</details>
<details>
<summary>Инструкции для кассира</summary>

Введите команду `/start`, как и обычный пользователь.
Вам доступны все команды обычного пользователя.
Затем ваш администратор должен присвоить вам роль [кассира].

После этого вы начнёте получать уведомления о новых заказах.
Используйте комманду `/confirm <имя пользователя>` чтобы закрыть заказ.
Закрытие заказа уменьшает количество блюд в `/menu`.

</details>
<details>
<summary>Инструкции для повара</summary>

Введите команду `/start`, как и обычный пользователь.
Вам доступны все команды обычного пользователя.
Затем ваш администратор должен присвоить вам роль [повара].

Вы можете добавлять новые блюда в меню с помощью команды
`/addish <название> <цена> <количество>`
(Они появятся в `/menu`)
</details>

Можно поменять язык с помощью `/lang <обозначение языка>`
В настоящее время поддерживаются только русский и английский

Например, `/lang ru` или `/lang en`

`@mb6ockatf, 19.04.2023`
