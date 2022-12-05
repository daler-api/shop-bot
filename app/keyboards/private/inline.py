from typing import Union, List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from app.config import Config
from app.infrastructure.database.models import Item
from app.utils.markup_constructor import InlineMarkupConstructor
from app.utils.tools import splitting_lists


class ExampleMarkup(InlineMarkupConstructor):
    class CD(CallbackData, prefix="test"):
        number: str

    def get(self) -> InlineKeyboardMarkup:
        schema = [3, 2]
        actions = [
            {"text": "1", "callback_data": self.CD(number="1")},
            {"text": "2", "callback_data": self.CD(number="2").pack()},
            {"text": "3", "callback_data": "3"},
            {"text": "4", "callback_data": self.CD(number="4").pack()},
            {"text": "6", "callback_data": "6"},
        ]
        return self.markup(actions, schema)


class Menu(InlineMarkupConstructor):
    class CD(CallbackData, prefix="menu"):
        show: str

    def get(self, i18n: TranslatorRunner):
        actions = [
            {"text": i18n.brand.kb(), "cd": self.CD(show="brands")},
            {"text": i18n.search.kb(), "cd": self.CD(show="search")},
            {"text": Config.CHANNEL_TITLE, "url": Config.CHANNEL_LINK},
            {"text": i18n.favorite.kb(), "cd": self.CD(show="favorites")},
            {"text": i18n.contact.kb_menu(), "cb": Contact.cb},
            {"text": i18n.feedback.kb_menu(), "url": "t.me/feedbackstuffrilldance"},
            {"text": i18n.info.kb.menu(), "cb": Information.CD(show="info")}
        ]
        schema = [1, 2, 1, 2, 1]
        return self.markup(actions, schema)


class BackToMenu(InlineMarkupConstructor):

    def get(self, i18n: TranslatorRunner):
        actions = [
            {"text": i18n.kb.back_menu(), "cb": Menu.CD(show="menu")}
        ]
        schema = [1]
        return self.markup(actions, schema)


class Contact(InlineMarkupConstructor):
    cb = "contact"

    def get(self, i18n: TranslatorRunner, admin_link: str):
        actions = [
            {"text": i18n.contact.kb(), "url": admin_link},
            {"text": i18n.kb.menu(), "cb": Menu.CD(show="menu")}
        ]
        schema = [1, 1]
        return self.markup(actions, schema)


class Feedback(InlineMarkupConstructor):
    cb = "feedback"

    def get(self, i18n: TranslatorRunner, channel_link: str):
        actions = [
            {"text": i18n.feedback.kb(), "url": channel_link},
            {"text": i18n.kb.menu(), "cb": Menu.CD(show="menu")}
        ]
        schema = [1, 1]
        return self.markup(actions, schema)


class Information(InlineMarkupConstructor):
    class CD(CallbackData, prefix="information"):
        show: str

    def get(self, i18n: TranslatorRunner):
        actions = [
            {"text": i18n.info.kb.delivery(), "cb": self.CD(show="delivery")},
            {"text": i18n.info.kb.pay(), "cb": self.CD(show="pay")},
            {"text": i18n.info.kb.feedback(), "cb": self.CD(show="feedback")},
            {"text": i18n.kb.menu(), "cb": Menu.CD(show="menu")}
        ]
        schema = [2, 2]
        return self.markup(actions, schema)


class BackInformation(InlineMarkupConstructor):
    def get(self, i18n: TranslatorRunner):
        actions = [
            {"text": i18n.kb.back(), "cb": Information.CD(show="info")}
        ]
        schema = [1]
        return self.markup(actions, schema)


class RetrySearch(InlineMarkupConstructor):
    def get(self):
        actions = [
            {"text": "Повторить поиск", "cb": Menu.CD(show="search")},
            {"text": "↩ Главное меню", "cb": Menu.CD(show="menu")}
        ]
        schema = [1, 1]
        return self.markup(actions, schema)


class BuyItem(InlineMarkupConstructor):
    class CD(CallbackData, prefix="buy_item"):
        item_id: str
        size: str


class Favorite(InlineMarkupConstructor):
    class CD(CallbackData, prefix="favorite_item"):
        item_id: str


class SearchItem(InlineMarkupConstructor):
    def get(self, i18n: TranslatorRunner, sizes: list[tuple], item_id: Union[str, int], favorite: bool):
        actions = [
            {"text": i18n.item.kb.size(size=size), "cb": BuyItem.CD(item_id=item_id, size=size)}
            for size, _ in sizes
        ]
        schema = list(map(len, splitting_lists(actions, 2)))

        actions += [
            {
                "text": i18n.item.kb.add_favorite() if not favorite else i18n.item.kb.del_favorite(),
                "cb": Favorite.CD(item_id=item_id)
            }
        ]
        schema += [1]
        return self.markup(actions, schema)
