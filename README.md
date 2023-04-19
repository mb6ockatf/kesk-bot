# KEKS
ERP system for school canteen

Telegram bot written on Python aiogram library

## Usage howto
1. Clone this repository
2. Go to project's folder
3. Set-up your postgres server and fill-in all the needed information in
[`config.ini`](config.ini)
4. Add your bot token and your own telegram user id to `bot`
config section in [`config.ini`](config.ini).
    It's required for free access to all bot commands.

    You also need to pass bot token as a run parameter in `test.sh`.
    [`config.ini`](config.ini) `bot.token` value will be deprecated soon,
    so isn't required really
5. Create virtual environment. For instance,
    ```bash
    python3 -m venv venv
    . venv/bin/activate
    ```
6. Install all the dependencies with
    ```bash
    python3 -m pip install -r requirements.txt
    ```
7. Launch the bot with `./test.sh`

## User guide
<details>
<summary>User's role</summary>

Begin communication with `/start` command. 
You'll be asked for username, so simply send `/username <your username>`.
It will be seen by cashier when you revieve order.

You can place new order with `/order <dishname> <qunatity>`.
Checkout `/menu` for available dishes before actually placing the order,
otherwise the error will be shown
</details>
<details>
<summary>Cashier's role</summary>

You have to do `/start` procedure and simply follow a user's guide first.
Then, you need your administrator to assign you a role.

After doing this, information about new orders will be sent to you.
Run `/confirm <account's name>` to close the order.
Account's name can be found right at the order message
Closing the order will decrease number of available dishes in `/menu`.

</details>
<details>
<summary>Cook's guide</summary>

You have to do `/start` procedure and simply follow a user's guide first.
Then, you need your administrator to assign you a role.

You can add new dishes with `/addish <name> <price> <quantity>`
(they'll show up in `/menu`, and there consumers can find them).
</details>

Change language with `/lang <language abbreviation>` command.
Currently, only English and Russian are supported.

For instance, `/lang ru` or `/lang en`

`@mb6ockatf, 19.04.2023`
