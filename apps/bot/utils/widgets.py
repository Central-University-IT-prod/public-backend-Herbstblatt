from aiogram.types import KeyboardButton, KeyboardButtonRequestUser
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text.base import Text
from aiogram_dialog.widgets.kbd.base import Keyboard
from aiogram_dialog.widgets.common import WhenCondition, Whenable
from fluent.runtime import FluentLocalization


class FluentMessage(Text):
    def __init__(self, name: str, when: WhenCondition = None):
        super().__init__(when)
        self.name = name

    async def _render_text(self, data, manager: DialogManager) -> str:
        strings: FluentLocalization = manager.middleware_data["strings"]
        return strings.format_value(self.name, data["dialog_data"])


class SelectUserButton(Keyboard):
    def __init__(self, text: Text, when: WhenCondition = None):
        Whenable.__init__(self, when=when)
        self.text = text

    async def _render_keyboard(
        self,
        data,
        manager: DialogManager,
    ):
        return [
            [
                KeyboardButton(
                    text=await self.text.render_text(data, manager),
                    request_user=KeyboardButtonRequestUser(
                        request_id=True, user_is_bot=False
                    ),
                ),
            ],
        ]
