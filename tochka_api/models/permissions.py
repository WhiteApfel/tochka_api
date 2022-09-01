from enum import Enum


class PermissionsEnum(str, Enum):
    account_basic: str = "ReadAccountsBasic"
    account_detail: str = "ReadAccountsDetail"
    balances: str = "ReadBalances"
    statements: str = "ReadStatements"
    transactions_basic: str = "ReadTransactionsBasic"
    transactions_debits: str = "ReadTransactionsDebits"
    transactions_credits: str = "ReadTransactionsCredits"
    transactions_detail: str = "ReadTransactionsDetail"
    special_accounts: str = "ReadSpecialAccounts"
    customer_data: str = "ReadCustomerData"
    sbp_data: str = "ReadSBPData"
    edit_sbp_data: str = "EditSBPData"
    card_data: str = "ReadCardData"
    edit_card_data: str = "EditCardData"
    edit_card_state: str = "EditCardState"
    card_limits: str = "ReadCardLimits"
    edit_card_limits: str = "EditCardLimits"
    payment_for_sign: str = "CreatePaymentForSign"
    payment_order: str = "CreatePaymentOrder"

    @classmethod
    def all_read(cls) -> list[str]:
        return [
            cls.account_basic,
            cls.account_detail,
            cls.balances,
            cls.statements,
            cls.transactions_basic,
            cls.transactions_debits,
            cls.transactions_credits,
            cls.transactions_detail,
            cls.special_accounts,
            cls.customer_data,
            cls.sbp_data,
            cls.card_data,
            cls.card_limits,
        ]

    @classmethod
    def all(cls) -> list[str]:
        return [
            cls.account_basic,
            cls.account_detail,
            cls.balances,
            cls.statements,
            cls.transactions_basic,
            cls.transactions_debits,
            cls.transactions_credits,
            cls.transactions_detail,
            cls.special_accounts,
            cls.customer_data,
            cls.sbp_data,
            cls.edit_sbp_data,
            cls.card_data,
            cls.edit_card_data,
            cls.edit_card_state,
            cls.card_limits,
            cls.edit_card_limits,
            cls.payment_for_sign,
            cls.payment_order,
        ]
