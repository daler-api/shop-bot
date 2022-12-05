from aiogram_dialog import DialogRegistry

from . import find_item, category_edit, item_acts, buy_item


def register(registry: DialogRegistry):
    for module in (find_item, category_edit, item_acts, buy_item):
        registry.register(module.dialog)
