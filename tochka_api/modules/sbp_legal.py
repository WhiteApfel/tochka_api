from models.responses import (
    SbpCustomerInfoResponse,
    SbpLegalEntityResponse,
    SbpRegisterLegalEntityResponse,
    TochkaBooleanResponse,
)
from models.responses.sbp_legal import SbpAccountsResponse
from modules import TochkaApiBase


class TochkaApiSbpLegal(TochkaApiBase):
    async def sbp_get_customer_info(
        self,
        customer_code: str,
        bank_code: str = "044525104",
        user_code: str | None = None,
    ) -> SbpCustomerInfoResponse:
        """
        Возвращает информацию о клиенте СБП

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-YuL#get_accounts_list_sbp__apiVersion__account__legalId__get

        :param user_code:
        :param customer_code: Код клиента в Точке
        :type customer_code: ``str``
        :param bank_code: БИК банка счёта
        :type bank_code: ``str``, default = ``044525104``
        :return: Схема CustomerInfoResponseV3
        ":rtype: SbpCustomerInfoResponse
        """
        return await self.request(
            method="GET", url=f"/sbp/v1.0/customer/{customer_code}/{bank_code}"
        )

    async def sbp_get_legal_entity(
        self, legal_id: str, user_code: str | None = None
    ) -> SbpLegalEntityResponse:
        """
        Метод для получения данных юрлица в Системе быстрых платежей

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-YuL#get_legal_entity_sbp__apiVersion__legal_entity__legalId__get

        :param user_code:
        :param legal_id: Идентификатор юрлица в СБП
        :type legal_id: ``str``
        :return: Схема LegalEntity
        :rtype: SbpLegalEntityResponse
        """

        return await self.request(
            method="GET", url=f"/sbp/v1.0/legal-entity/{legal_id}"
        )

    async def sbp_set_legal_entity_status(
        self,
        legal_id: str,
        is_active: str | bool = True,
        user_code: str | None = None,
    ) -> TochkaBooleanResponse:
        """
        Метод устанавливает статус юрлица в Системе быстрых платежей

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-YuL#set_legal_entity_status_sbp__apiVersion__legal_entity__legalId__post

        :param user_code:
        :param legal_id: Идентификатор юрлица в СБП
        :type legal_id: ``str``
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
            method="POST",
            url=f"/sbp/v1.0/legal-entity/{legal_id}",
            json=data,
        )

    async def sbp_register_legal_entity(
        self,
        customer_code: str,
        bank_code: str = "044525104",
        user_code: str | None = None,
    ) -> SbpRegisterLegalEntityResponse:
        """
        Выполняет регистрацию юрлица в СБП.

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-YuL#register_legal_entity_sbp__apiVersion__register_sbp_legal_entity_post

        :param user_code:
        :param customer_code: Код клиента в Точке
        :type customer_code: ``str``
        :param bank_code: БИК банка счёта
        :type bank_code: ``str``, default = ``044525104``
        :return: Схема LegalId
        ":rtype: SbpRegisterLegalEntityResponse
        """
        data = {
            "Data": {
                "customerCode": customer_code,
                "bankCode": bank_code,
            }
        }

        return await self.request(
            method="POST",
            url=f"/sbp/v1.0/register-sbp-legal-entity",
            json=data,
        )

    async def sbp_get_accounts(
        self, legal_id: str, user_code: str | None = None
    ) -> SbpAccountsResponse:
        """
        Метод для получения списка счетов юрлица в Системе быстрых платежей

        https://enter.tochka.com/doc/v2/redoc/tag/Servis-SBP:-Rabota-s-YuL#get_accounts_list_sbp__apiVersion__account__legalId__get

        :param user_code:
        :param legal_id: Идентификатор юрлица в СБП
        :type legal_id: ``str``
        :return: Схема AccountListResponse
        :rtype: SbpAccountsResponse
        """

        return await self.request(method="GET", url=f"sbp/v1.0/account/{legal_id}")
