# 🎉 Tochka API

**Simple Tochka Bank API wrapper**

## 📥 Installation

### 📦 From pip:

```shell
python -m pip install -u tochka_api
```

### 🏗 From git:

```shell
git clone https://github.com/WhiteApfel/tochka_api.git
cd tochka_api
python setup.py install
```

### 🚧 Dev progress

* [x] Auth
* [x] Balances
* [x] Accounts
* [ ] Webhooks
* [ ] Statements
* [ ] Cards
* [ ] Clients
* [ ] Payments
* [ ] Consents
* [ ] Special accounts
* [ ] SBP
  * [ ] QR
  * [ ] Merchants
  * [x] Legal
  * [ ] Refunds
  * [ ] Account

### 🧑‍🏫 How to use

```python
import asyncio

from tochka_api import TochkaAPI
from tochka_api.models import PermissionsEnum

client_id = "<<client_id>>"
client_secret = "<<client_secret>>"
redirect_uri = "https://tochka-api.pfel.cc/"

tochka = TochkaAPI(client_id, client_secret, redirect_uri=redirect_uri)


async def main():
    if tochka.tokens.access_token is None:
        await tochka.get_consents_token()
        consents_request = await tochka.create_consents(PermissionsEnum.all())
        print(tochka.generate_auth_url(consent_id=consents_request.consent_id))
        await tochka.get_access_token(code=input("Code >>> "))
    
    balances = await tochka.get_balances()
    print(balances[0].amount)


asyncio.run(main())
```
