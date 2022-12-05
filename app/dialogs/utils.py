from typing import Any, Dict, Optional

from aiogram.types import ContentType
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.api.protocols import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.media.base import Media
from aiogram_dialog.widgets.text import Text
from aiogram_dialog.widgets.text.format import _FormatDataStub
from fluentogram import TranslatorRunner


class FormatTranslate(Text):
    def __init__(self, text_translate: str, form: dict = None, when: WhenCondition = None):
        super().__init__(when)
        self.text_translate = text_translate
        self.form = form or {}

    async def _render_text(self, data: Dict, manager: DialogManager) -> str:
        i18n: TranslatorRunner = manager.middleware_data["i18n"]
        for key, value in self.form.items():
            data[key] = value.format_map(_FormatDataStub(data=data))
        return i18n.get(self.text_translate, **data)


class DynamicMedia(Media):
    def __init__(
            self,
            *,
            key_in_data: str,
            type: ContentType = ContentType.PHOTO,
            media_params: Dict = None,
            when: WhenCondition = None,
    ):
        super().__init__(when=when)
        self.key_in_data = key_in_data
        self.type = type
        self.media_params = media_params or {}

    async def _render_media(
            self, data: Any, manager: DialogManager,
    ) -> Optional[MediaAttachment]:
        file_id = data[self.key_in_data]

        return MediaAttachment(
            type=self.type,
            file_id=MediaId(file_id),
            **self.media_params,
        )
