"""
    This module is largely inspired by django-rest-framework settings.
    This module provides the `settings` object, that is used to access
    app settings, checking for user settings first, then falling
    back to the defaults.
"""
import os
from typing import Any, Dict

from django.conf import settings
from django.test.signals import setting_changed
from django.utils.module_loading import import_string

SETTINGS_DOC = "https://gitlab.com/zerocodes/django-vaults"

VAULTS_DEFAULTS: Dict[str, Any] = {
    # Examples
    # ------------------------------------------------------------------------
    # "SETTING_NAME": getattr(settings, "SETTING_NAME", "default_value"),
    # "SETTING_MODULE_FROM_STRING": getattr(
    #     settings, "SETTING_MODULE_FROM_STRING", "your.module.name"
    # ),
    # "SETTING_MODULE_FROM_LIST_STRING": getattr(
    #     settings, "SETTING_MODULE_FROM_LIST_STRING", [
    #                   "your.module.name1",
    #                   "your.module.name2"
    #     ]
    # ),
    # "SETTING_MODULE_FROM_DICT_STRING": {
    #     "some_key1": "some.module.name1",
    #     "some_key2": "some.module.name2",
    # },
    #
    # VAULT_CONFIGS
    "ACCOUNT_NAMES": {
        "ASSET": "Asset",  # Asset
        "CASH": "Cash",
        "PETTY_CASH": "Petty Cash",
        "BANK": "Petty Cash",
        "INVENTORY": "Inventory",
        "ACCOUNT_RECEIVABLE": "Account Receivable",
        # --------------------------------------------
        "LIABILITY": "Liability",
        "PARTNER_BALANCE": "Partner Balance",
        "ACCOUNT_PAYABLE": "Account Payable",
        # --------------------------------------------
        "EQUITY": "Equity",  # penyertaan modal
        # --------------------------------------------
        "EXPENSE": "Expense",  # Pengeluaran
        "ACTIVITIES_EXPENSE": "Activities Expense",
        "TRANSFER_FEE": "Transfer Fee",  # Pengeluaran
        # --------------------------------------------
        "REVENUE": "Revenue",  # Pendapatan
        "PARTNER_REVENUE": "Partner Revenue",
        "ACTIVITIES_REVENUE": "Activities Revenue",
    },
}

# List of settings that may be in string import notation.
IMPORT_STRINGS = []

# List of settings that have been removed
REMOVED_SETTINGS = []


def perform_import(val, setting_name):
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    elif isinstance(val, dict):
        return {
            key: import_from_string(item, setting_name) for key, item in val.items()
        }
    return val


def import_from_string(val, setting_name):
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import '%s' for VAULTS setting '%s'. %s: %s." % (
            val,
            setting_name,
            e.__class__.__name__,
            e,
        )
        raise ImportError(msg)


class AppSettings:
    """
    This module is largely inspired by django-rest-framework settings.
    This module provides the `vaults_settings` object, that is used to access
    app settings, checking for user settings first, then falling
    back to the defaults.
    """

    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        if user_settings:
            self._user_settings = self.__check_user_settings(user_settings)
        self.defaults = defaults or VAULTS_DEFAULTS
        self.import_strings = import_strings or IMPORT_STRINGS
        self._cached_attrs = set()

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "VAULTS", {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError("Invalid VAULTS settings: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if attr in self.import_strings:
            val = perform_import(val, attr)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def __check_user_settings(self, user_settings):
        for setting in REMOVED_SETTINGS:
            if setting in user_settings:
                raise RuntimeError(
                    "The '%s' setting has been removed. Please refer to '%s' "
                    "for available settings." % (setting, SETTINGS_DOC)
                )
        return user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


vaults_configs = AppSettings(None, VAULTS_DEFAULTS, IMPORT_STRINGS)


def reload_vaults_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == "VAULTS":
        vaults_configs.reload()


setting_changed.connect(reload_vaults_settings)
