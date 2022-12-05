from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from fluentogram import TranslatorRunner

from app.utils.markup_constructor import InlineMarkupConstructor


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


class CancelKb(InlineMarkupConstructor):
    cb = "adm_cancel"

    def get(self) -> InlineKeyboardMarkup:
        schema = [1]
        actions = [
            {"text": "❌ Отмена", "cb": self.cb},
        ]
        return self.markup(actions, schema)


class SelectBroadcastGroup(InlineMarkupConstructor):
    class CD(CallbackData, prefix="select_bc_group"):
        group: str

    def get(self):
        actions = [
            {"text": "👤 Юзеры", "cb": self.CD(group="user")},
            {"text": "🛍 Покупатели", "cb": self.CD(group="buyer")}
        ]
        schema = [1, 1]
        return self.markup(actions, schema)


class StartBroadcast(InlineMarkupConstructor):
    cb = "start_broadcast"

    def get(self):
        actions = [
            {"text": "✅ Начать рассылку", "cb": self.cb},
            {"text": "❌ Отмена", "cb": CancelKb.cb}
        ]
        schema = [1, 1]
        return self.markup(actions, schema)


class CancelBroadcast(InlineMarkupConstructor):
    cb = "cancel_broadcast"

    def get(self):
        actions = [{"text": "❌ Закончить рассылку", "cb": self.cb}]
        schema = [1]
        return self.markup(actions, schema)


class ShowBrand(InlineMarkupConstructor):
    class CD(CallbackData, prefix="act_brand"):
        id: str
        act: str

    def get(self, brand_id):
        actions = [
            {"text": "✏ Изменить название", "cb": self.CD(id=brand_id)},
            {"text": "❌ Удалить", "cb": self.CD(id=brand_id)}
        ]
        schema = [1, 1]
        return self.markup(actions, schema)


class EditInfo(InlineMarkupConstructor):
    class CD(CallbackData, prefix="edit_info"):
        show: str

    def get(self, i18n: TranslatorRunner):
        actions = [
            {"text": i18n.info.kb.delivery(), "cb": self.CD(show="delivery")},
            {"text": i18n.info.kb.pay(), "cb": self.CD(show="pay")},
            {"text": i18n.info.kb.feedback(), "cb": self.CD(show="feedback")},
            {"text": "❌ Отмена", "cb": CancelKb.cb}
        ]
        schema = [2, 2]
        return self.markup(actions, schema)
