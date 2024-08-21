from aiogram import Router, filters, types
from aiogram.fsm.context import FSMContext
from fluent.runtime import FluentLocalization

from db.models import User
from .registration import start_registration

router = Router()


@router.message(filters.Command("start"))
async def start(message: types.Message, strings: FluentLocalization, state: FSMContext):
    author = message.from_user
    if author is None:
        return

    user = await User.get_or_none(id=author.id)
    if user is None:
        await start_registration(message=message, strings=strings, state=state)
    else:
        await message.reply(strings.format_value("welcome-registered"))


@router.message(filters.Command("help"))
async def help(message: types.Message, strings: FluentLocalization):
    await message.reply(strings.format_value("help"))
