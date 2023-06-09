from models.responses import (
    SbpMerchantsResponse,
    SbpRegisterMerchantResponse,
    TochkaBooleanResponse,
)
from modules import TochkaApiBase


class TochkaApiSbpMerchant(TochkaApiBase):
    async def sbp_get_merchants(
        self, legal_id: str, tochka_user_code: str | None = None
    ) -> SbpMerchantsResponse:
        """
        Метод для получения списка ТСП юрлица

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-TSP#get_merchants_list_sbp__apiVersion__merchant_legal_entity__legalId__get

        :param tochka_user_code:
        :param legal_id: Идентификатор юрлица в СБП
        :type legal_id: ``str``
        :return: Схема MerchantListResponse
        :rtype: SbpMerchantsResponse
        """

        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/merchant/legal-entity/{legal_id}",
        )

    async def sbp_get_merchant(
        self, merchant_id: str, user_code: str | None = None
    ) -> SbpMerchantsResponse:
        """
        Метод для получения информации о ТСП.

        Важно: Ответ будет в такой же модели, что и sbp_get_merchants,
        то есть содержать лист из одного конкретного ТСП. Не как в документации Точки.

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-TSP#get_merchant_sbp__apiVersion__merchant__merchantId__get

        :param user_code:
        :param merchant_id: Идентификатор ТСП в СБП
        :type merchant_id: ``str``
        :return: Схема Merchant
        :rtype: SbpMerchantsResponse
        """

        return await self.request(
            method="GET",
            url=f"/sbp/v1.0/merchant/{merchant_id}",
        )

    async def sbp_register_merchant(
        self,
        legal_id: str,
        name: str,
        mcc: str,
        address: str,
        city: str,
        region_code: str,
        zip_code: str,
        phone_number: str | None = None,
        country_code: str = "RU",
        capabilities: str = "011",
        user_code: str | None = None,
    ) -> SbpRegisterMerchantResponse:
        """
        Регистрация мерчанта в СБП

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-TSP#register_merchant_sbp__apiVersion__merchant_legal_entity__legalId__post

        :param user_code:
        :param legal_id: Идентификатор юрлица в СБП
        :type legal_id: ``str``
        :param name: Название ТСП (по вывеске/бренду при наличии, либо краткое название юрлица)
        :type name: ``str``
        :param mcc: MCC код ТСП
        :type mcc: ``str``
        :param country_code: Код страны регистрации юрлица
        :type country_code: ``str``, default=``RU``
        :param region_code: Код региона регистрации юрлица, первые две цифры ОКТМО
        :type region_code: ``str``
        :param zip_code: Почтовый индекс юридического адреса юрлица
        :type zip_code: ``str``
        :param city: Город юридического адреса юрлица
        :type city: ``str``
        :param address: Улица, дом, корпус, офис юридического адреса юрлица
        :type address: ``str``
        :param phone_number: Номер телефона ТСП до 13 знаков в любом формате
        :type phone_number: ``str``, optional
        :param capabilities: Возможности выпуска QR у ТСП: 001 - только статичный, 010 - только динамичный, 011 - оба
        :type capabilities: ``str``, default=``011``
        :return: Схема MerchantId
        :rtype: SbpRegisterMerchantResponse
        """

        data = {
            "Data": {
                "address": address,
                "city": city,
                "countryCode": country_code,
                "countrySubDivisionCode": region_code,
                "zipCode": zip_code,
                "brandName": name,
                "capabilities": capabilities,
                "mcc": mcc,
            }
        }

        if phone_number is not None:
            data["Data"]["contactPhoneNumber"] = phone_number

        return await self.request(
            method="POST", url=f"/sbp/v1.0/merchant/legal-entity/{legal_id}", json=data
        )

    async def sbp_set_merchant_status(
        self,
        merchant_id: str,
        is_active: bool | str = True,
        user_code: str | None = None,
    ) -> TochkaBooleanResponse:
        """
        Метод устанавливает статус ТСП

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-TSP#set_merchant_status_sbp__apiVersion__merchant__merchantId__put

        :param user_code:
        :param merchant_id: Идентификатор ТСП в СБП
        :type merchant_id: ``str``
        :param is_active: Устанавливаемый статус, True - Active, False - Suspended
        :type is_active: ``bool``, default=``True``
        :return: Схема BooleanResponse
        :rtype: TochkaBooleanResponse
        """

        data = {
            "Data": {
                "status": ("Active" if is_active else "Suspended")
                if type(is_active) is bool
                else is_active,
            }
        }

        return await self.request(
            method="PUT", url=f"/sbp/v1.0/merchant/{merchant_id}", json=data
        )
