# 🎉 Tochka API

**Удобная обёртка над открытым API Банка Точка**

## 📥 Установка

### 📦 Из pip:

```shell
python -m pip install -u tochka_api
```

### 🏗 Из репозитория:

```shell
git clone https://github.com/WhiteApfel/tochka_api.git
cd tochka_api
python setup.py install
```

### 🚧 Прогресс разработки

* [x] Авторизация
* [x] Балансы
* [x] Счета
* [ ] Webhooks
* [ ] Выписки
* [ ] Карты
* [ ] Клиенты
* [ ] Платежи
* [ ] Разрешения
* [ ] Специальные счета
* [x] СБП
  * [x] QR
  * [x] ТСП (Merchant)
  * [x] Компании (Legal)
  * [x] Возвраты

### 🧑‍🏫 Как использовать

**💰 Уточнения по типу данных для суммы**

* ``Decimal`` and ``str`` - amount in rubles
* ``int`` - amount in kopecks

**Различия user_code и customer_code**

* ``user_code`` это код клиента, который имеет доступ к компании
* ``customer_code`` это код компании(ИП), на которую открыты счета

```python
import asyncio

from decimal import Decimal

from tochka_api import TochkaAPI, context_user_code
from tochka_api.models import PermissionsEnum

client_id = "<<client_id>>"
client_secret = "<<client_secret>>"
redirect_uri = "https://tochka-api.pfel.cc/"

tochka = TochkaAPI(client_id, client_secret, redirect_uri=redirect_uri)


async def add_user():
  consents_token, consents_expires_in = await tochka.get_consents_token()
  consents_request = await tochka.create_consents(
      consents_token, PermissionsEnum.all()
  )
  auth_url = tochka.generate_auth_url(consent_id=consents_request.consent_id)
  print("Auth:", auth_url)
  
  code = input("Code >>> ")
  token_id = input("Token_id >>> ")
  tokens = await tochka.get_access_token(
      code=code, token_id=token_id
  )
  
  print(f"User {tokens.user_code=} are authorized.")
  context_user_code.set(tokens.user_code)
  
  asyncio.create_task(get_accounts())
  merchant_id = await register_merchant(user_code=tokens.user_code)
  await register_qr(merchant_id=merchant_id)

async def get_accounts():
  # user_code будет унаследован из context_user_code
  # Это thread-safe и loop-safe
  for _ in range(25):
    await tochka.get_accounts()
    await asyncio.sleep(2)

async def register_merchant(user_code) -> str:
  # Будет использоваться указанный user_code
  # Даже если в context_user_code было задано другое значение
  accounts = await tochka.get_accounts(user_code=user_code)
  
  customer_info = await tochka.sbp_get_customer_info(
      customer_code=accounts[0].customer_code
  )
  legal_entity = await tochka.sbp_get_legal_entity(customer_info.legal_id)

  merchant = await tochka.sbp_register_merchant(
      legal_id=legal_entity.legal_id,
      name="TochkaExample",
      mcc="7277",
      address=" 1-й Вешняковский проезд, д. 1, стр. 8, этаж 1, помещ. 43",
      city="Москва",
      region_code="45",
      zip_code="109456",
      phone_number="+78002000024",
  )
  
  print(f"New merchant {merchant.merchant_id=}")
  print(
    *(await tochka.sbp_get_merchants(legal_id=legal_entity.legal_id)).merchants,
    sep="\n",
  )
  
  return merchant.merchant_id

async def register_qr(merchant_id):
  # user_code будет унаследован из context_user_code
  # Это thread-safe и loop-safe
  accounts = await tochka.get_accounts()

  customer_info = await tochka.sbp_get_customer_info(
      customer_code=accounts[0].customer_code
  )
  legal_entity = await tochka.sbp_get_legal_entity(customer_info.legal_id)
  sbp_accounts = await tochka.sbp_get_accounts(legal_entity.legal_id)
    
  qr = await tochka.sbp_register_qr(
    merchant_id=merchant_id,
    account=sbp_accounts[0].account,
    is_static=True,
    purpose="Перечисление по договору минета",
    media_type="image/svg+xml",
  )
  print("Статичный без суммы:\n",qr.image.content)
  
  qr = await tochka.sbp_register_qr(
    merchant_id=merchant_id,
    account=sbp_accounts[0].account,
    is_static=True,
    amount=Decimal("100.00"),  # или Decimal(100), или 10000
    purpose="Оплата аренды борделя",
    media_type="image/svg+xml",
  )
  print("Статичный с суммой:\n",qr.image.content)
  
  qr = await tochka.sbp_register_qr(
    merchant_id=merchant_id,
    account=sbp_accounts[0].account,
    is_static=False,
    amount=10000,  # или Decimal(100)
    ttl=60,  # 0 - максимально возможное ограничение, иначе в минутах
    purpose="Оплата поставки презервативов",
    media_type="image/svg+xml",
  )
  print("Динамический с суммой:\n",qr.image.content)

async def refund():
  accounts = await tochka.get_accounts()

  customer_info = await tochka.sbp_get_customer_info(
      customer_code=accounts[0].customer_code
  )
  sbp_accounts = await tochka.sbp_get_accounts(customer_info.legal_id)
  
  payments = await tochka.sbp_get_payments(
    customer_info.customer_code, from_date=1,
  )
  print(payments)
  
  last_payment = payments.payments[0]
  refund_response = await tochka.sbp_start_refund(
      account=sbp_accounts[0].account,
      amount=Decimal("1.25"),  # или 125
      qrc_id=last_payment.qrc_id,
      trx_id=last_payment.trx_id,
  )
  print("Refund: ", refund_response)

async def main():
  # Добавить два пользователя. 
  # Это могут быть бухгалтер и владелец одной компании
  # или совершенно разные люди из разных компаний.
  # Приложение может работать с несколькими пользователями
  # либо в однопользовательском режиме, тогда надо указать
  # tochka = TochkaAPI(client_id, client_secret, redirect_uri=redirect_uri, one_customer_mode=True)
  # и тогда после добавления одного пользователя, система его запомнит.
  # Указывать context_user_code не придётся
  print("Введите что-либо, чтобы добавить пользователей")
  print("Для пропуска нажмите Enter")
  if input(">>> "):
    await add_user()
    await add_user()
  else:
    # можно не указывать, если one_customer_mode=True
    context_user_code.set("212332030")
      
    await refund()
    

  balances = await tochka.get_balances()
  print(balances[0].amount)


asyncio.run(main())
```
