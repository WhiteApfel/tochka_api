import re
from decimal import Decimal
from datetime import date, datetime, timedelta
from typing import Literal

from models.responses import (
    SbpQrPaymentDataResponse,
    SbpQrPaymentStatusResponse,
    SbpQrsResponse,
    SbpRegisterQrResponse,
    TochkaBooleanResponse,
)
from modules import TochkaApiBase


class TochkaApiSbpQr(TochkaApiBase):
    async def sbp_get_qrs(
        self, legal_id: str, user_code: str | None = None
    ) -> SbpQrsResponse:
        """
        Метод для получения списка всех QR кодов по всем ТСП

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-QR-kodami#get_qr_codes_list_sbp__apiVersion__qr_code_legal_entity__legalId__get

        :param user_code:
        :param legal_id: Идентификатор юрлица в СБП
        :type legal_id: ``str``
        :return: Схема QRCodeListResponse
        :rtype: SbpQrsResponse
        """

        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/qr-code/legal-entity/{legal_id}",
        )

    async def sbp_get_qr(
        self, qrc_id: str, user_code: str | None = None
    ) -> SbpQrsResponse:
        """
        Метод для получения информации о QR коде

        Важно: Ответ будет в такой же модели, что и sbp_get_qrs,
        то есть содержать лист из одного конкретного QR кода. Не как в документации Точки.

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-QR-kodami#get_qr_code_sbp__apiVersion__qr_code__qrcId__get

        :param user_code:
        :param qrc_id: идентификатор QR кода в СБП
        :type qrc_id: ``str``
        :return: Схема QrCode
        :rtype: SbpQrsResponse
        """

        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/qr-code/{qrc_id}",
        )

    async def sbp_register_qr(
        self,
        merchant_id: str,
        account: str,
        is_static: bool | str = True,
        amount: int | Decimal | None = None,
        currency: int | None = None,
        ttl: int | None = None,
        purpose: str = "",
        width: int = 300,
        height: int = 300,
        media_type: Literal["image/png", "image/svg+xml"] = "image/png",
        source_name: str = "https://github.com/whiteapfel/tochka_api",
        user_code: str | None = None,
    ) -> SbpRegisterQrResponse:
        """
        Метод для регистрации QR кода в СБП

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-QR-kodami#register_qr_code_sbp__apiVersion__qr_code_merchant__merchant_id___account__post

        :param user_code:
        :param merchant_id: Идентификатор ТСП в СБП
        :type merchant_id: ``str``
        :param account: идентификатор счёта юрлица (обычно в формате "{номер счёта}/{бик счёта}")
        :type account: ``str``
        :param is_static: статичный (True) или динамический (False) QR код
        :type is_static: ``bool``, default=``True``
        :param amount: Сумма, если нужна фиксированная. В копейках (``int``) или в рублях (``Decimal``). Для Decimal будет округление до копейки, то есть два знака после запятой. Обязательна для динамического (is_static=False).
        :type amount: ``int`` | ``Decimal``, optional
        :param currency: трёхсимвольный код валюты
        :type currency: ``str``, default=``"RUB"``
        :param ttl: Период активности динамического (is_static=False) кода в минутах. 0 - максимальный, но не бесконечный
        :type ttl: ``int``, default=``0``
        :param purpose: Комментарий к QR коду, до 140 символов
        :type purpose: ``str``, default=``""``
        :param width: ширина изображения QR кода, не меньше 200
        :type width: ``int``, default=``300``
        :param height: высота изображения QR кода, не меньше 300
        :type height: ``int``, default=``300``
        :param media_type: Тип изображения: ``image/png`` или ``image/svg+xml``
        :type media_type: ``str``, default=``"image/png"``
        :param source_name: Название системы, выпустившей QR код
        :type source_name: ``str``, optional
        :return: Схема RegisteredQrCode
        :rtype: SbpRegisterQrResponse
        """

        data = {
            "Data": {
                "paymentPurpose": purpose,
                "qrcType": ("01" if is_static else "02")
                if type(is_static) is bool
                else is_static,
                "imageParams": {
                    "width": width,
                    "height": height,
                    "media_type": media_type,
                },
                "sourceName": source_name,
            }
        }
        if not is_static:
            data["Data"]["ttl"] = ttl or 0
            if amount is None:
                raise ValueError(
                    "Dynamic QR code (is_static=False) requires a non-zero and non-None"
                    " amount value."
                )
        if amount is not None:
            data["Data"]["amount"] = amount
            data["Data"]["currency"] = currency or "RUB"

        return await self.request(
            method="POST",
            url=f"/sbp/v1.0/qr-code/merchant/{merchant_id}/{account}",
            json=data,
        )

    async def sbp_set_qr_status(
        self,
        qrc_id: str,
        is_active: bool | str = True,
        user_code: str | None = None,
    ) -> TochkaBooleanResponse:
        """
        Метод устанавливает статус QR-кода

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-QR-kodami#set_qr_code_status_sbp__apiVersion__qr_code__qrcId__put

        :param user_code:
        :param qrc_id: идентификатор QR кода в СБП
        :type qrc_id: ``str``
        :param is_active: Устанавливаемый статус, True - Active, False - Suspended
        :type is_active: ``bool``, default=``True``
        :return: Схема BooleanResponse
        :rtype: TochkaBooleanResponse
        """

        data = {
            "Data": {
                "status": ("Active" if is_active else "Suspended")
                if type(is_active) is bool
                else is_active
            }
        }
        return await self.request(
            method="PUT",
            url=f"/sbp/v1.0/qr-code/{qrc_id}",
            json=data,
        )

    async def sbp_get_qr_payment_data(
        self, qrc_id: str, user_code: str | None = None
    ) -> SbpQrPaymentDataResponse:
        """
        Метод для получения данных о QR-коде и ТСП по идентификатору QR-кода

        Описание модели ответа расписано в документации к ней: SbpQrPaymentDataResponse

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-QR-kodami#get_qr_code_payment_data_sbp__apiVersion__qr_code__qrcId__payment_sbp_data_get

        :param user_code:
        :param qrc_id: идентификатор QR кода в СБП
        :type qrc_id: ``str``
        :return: Схема QrCodePaymentDataV3
        :rtype: SbpQrPaymentDataResponse
        """
        return await self.request(
            method="GET", url=f"/sbp/v1.0/qr-code/{qrc_id}/payment-sbp-data"
        )

    async def sbp_get_qrs_payment_status(
        self,
        qrc_ids: list[str] | str,
        from_date: datetime | date | int | str | None = None,
        to_date: datetime | date | int | str | None = None,
        user_code: str | None = None,
    ) -> SbpQrPaymentStatusResponse:
        """
        Метод для получения статусов операций по динамическим QR-кодам

        Параметры ``from/to_date`` могут принимать date, datetime
        или строку в формате ``YYYY-MM-DD``,
        а также ``int``, который расценивается как количество дней назад.
        Например, можно указать from_date=7, чтобы получить за прошедшие 7 дней

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-QR-kodami#get_qr_codes_payment_status_sbp__apiVersion__qr_codes__qrc_ids__payment_status_get

        :param user_code:
        :param qrc_ids: идентификатор QR кода в СБП
        :type qrc_ids: ``list[str]`` | ``str``
        :param from_date: начало периода для получения статусов
        :type from_date: ``datetime`` | ``date`` | ``int`` | ``str``, optional
        :param to_date: конец периодов для получения статусов
        :type to_date: ``datetime`` | ``date`` | ``int`` | ``str``, optional
        :return: Схема QRCodePaymentStatusListResponse
        :rtype: SbpQrPaymentStatusResponse
        """
        if isinstance(qrc_ids, str):
            qrc_ids = [qrc_ids]

        params = {}

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

        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/qr-code/{','.join(qrc_ids)}/payment-status",
            params=params,
        )
