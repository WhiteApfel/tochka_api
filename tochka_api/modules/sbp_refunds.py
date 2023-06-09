import re
from _decimal import Decimal
from datetime import datetime, timedelta, date

from models.responses import SbpPaymentsResponse, SbpRefundResponse
from modules import TochkaApiBase
from settings import CHARS_FOR_PURPOSE


class TochkaApiSbpRefunds(TochkaApiBase):
    async def sbp_get_payments(
        self,
        customer_code: str,
        qrc_id: str | None = None,
        from_date: datetime | date | int | str | None = None,
        to_date: datetime | date | int | str | None = None,
        page: int = 1,
        per_page: int = 1000,
        user_code: str | None = None,
    ) -> SbpPaymentsResponse:
        """
        Метод для получения списка платежей в Системе быстрых платежей

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-vozvratami#get_payments_sbp__apiVersion__get_sbp_payments_get

        :param user_code:
        :param customer_code: Код клиента в Точке
        :type customer_code: ``str``
        :param qrc_id: идентификатор QR кода в СБП
        :type qrc_id: ``str``
        :param from_date: начало периода для получения статусов
        :type from_date: ``datetime`` | ``date`` | ``int`` | ``str``, optional
        :param to_date: конец периодов для получения статусов
        :type to_date: ``datetime`` | ``date`` | ``int`` | ``str``, optional
        :param page: страница выдачи
        :type page: ``int``, default=``1``
        :param per_page: количество элементов на страницу
        :type per_page: ``int``, default=``1000``
        :return: Схема SBPPaymentList
        :rtype: SbpPaymentsResponse
        """
        params = {
            "customerCode": customer_code,
            "page": page,
            "perPage": per_page,
        }

        if from_date is not None:
            if isinstance(from_date, int):
                from_date: date = (datetime.now() - timedelta(days=1)).date()
            if isinstance(from_date, datetime):
                from_date: date = from_date.date()
            if isinstance(from_date, date):
                from_date: str = from_date.strftime("%Y-%m-%d")

            if not re.match(r"^\d{4}-\d{2}-\d{2}$", from_date):
                raise ValueError("from_date must be in 'YYYY-MM-DD' format (%Y-%m-%d)")

            params["fromDate"] = from_date

        if to_date is not None:
            if isinstance(to_date, int):
                to_date: date = (datetime.now() - timedelta(days=1)).date()
            if isinstance(to_date, datetime):
                to_date: date = to_date.date()
            if isinstance(to_date, date):
                to_date: date = to_date.strftime("%Y-%m-%d")

            if not re.match(r"^\d{4}-\d{2}-\d{2}$", to_date):
                raise ValueError("from_date must be in 'YYYY-MM-DD' format (%Y-%m-%d)")

            params["toDate"] = to_date

        if qrc_id is not None:
            params["qrcId"] = qrc_id

        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/get-sbp-payments?customerCode={customer_code}&fromDate={from_date}&toDate={to_date}",
            params=params,
        )

    async def sbp_start_refund(
        self,
        account: str,
        amount: Decimal | str | int,
        qrc_id: str,
        trx_id: str,
        purpose: str = None,
        currency: str = "RUB",
        bank_code: str = "044525104",
        is_non_resident: bool = False,
        user_code: str | None = None,
    ) -> SbpRefundResponse:
        """
        Метод запрашивает возврат платежа через Систему быстрых платежей

        Для совместимости с другими методами, аргумент amount при получении значения ``int``
        будет воспринимать эту сумму в копейках.

        От разработчика:
        Для возврата нерезиденту вы можете не прописывать назначение
        из комментария от Точки,
        а просто указать is_non_resident=True, метод самостоятельно добавит
        нужный префикс к назначению или создаст его.

        Следует уточнить актуальные требования на странице метода API, и в случае изменений,
        вернуть параметр на False и руками сгенерировать необходимое purpose.

        От Точки:
        Если нужно вернуть деньги нерезиденту, назначение платежа должно
        начинаться с «{VO99020} Возврат ошибочно полученной суммы transactionId»,
        где transactionId — это идентификатор оригинальной операции.

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-vozvratami#start_refund_sbp__apiVersion__refund_post

        :param user_code:
        :param account: идентификатор счёта юрлица (обычно в формате "{номер счёта}/{бик счёта}")
        :type account: ``str``
        :param amount: Сумма возврата в рублях (``Decimal`` | ``str``) или в копейках (``int``)
        :type amount: ``Decimal`` | ``str`` | ``int``
        :param qrc_id: идентификатор QR кода в СБП
        :type qrc_id: ``str``
        :param trx_id: идентификатор транзакции по QR коду в СБП
        :type trx_id: ``str``
        :param purpose: назначение вовзрата
        :type purpose: ``str``, optional
        :param currency: трёхсимвольный код валюты
        :type currency: ``str``, default=``"RUB"``
        :param bank_code: БИК банка счёта
        :type bank_code: ``str``, default = ``044525104``
        :param is_non_resident: параметр для автоматического добавления префикса к назначению
        :return: Схема SBPRefundRequestResponse
        :rtype: SbpRefundResponse
        """
        if isinstance(amount, str):
            amount: Decimal = Decimal(amount)
        if isinstance(amount, int):
            amount: Decimal = Decimal(amount) / Decimal(100)

        data = {
            "Data": {
                "bankCode": bank_code,
                "accountCode": account,
                "amount": str(amount.quantize(Decimal("0.00"))),
                "currency": currency,
                "qrcId": qrc_id,
                "refTransactionId": trx_id,
            }
        }

        if is_non_resident:
            purpose = (
                f"{{VO99020}} Возврат ошибочно полученной суммы {trx_id}. " + purpose
                if purpose is not None
                else ""
            )

        if purpose is not None:
            data["Data"]["purpose"] = "".join(
                c for c in purpose if c in CHARS_FOR_PURPOSE
            ).strip()[:140]

        return await self.request(
            method="POST",
            url="/sbp/v1.0/refund",
            json=data,
        )

    async def sbp_get_refund_data(
        self, request_id: str, user_code: str | None = None
    ) -> SbpRefundResponse:
        """
        Метод для получения информация о платеже-возврате по Системе быстрых платежей

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-vozvratami#get_refund_data_sbp__apiVersion__refund__request_id__get

        :param user_code:
        :param request_id: идентификатор запроса на возврат
        :type request_id: ``str``
        :return: Странная схема
        :rtype: SbpRefundResponse
        """
        return await self.request(method="GET", url=f"/sbp/v1.0/refund/{request_id}")
