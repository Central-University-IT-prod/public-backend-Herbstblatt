from aiogram import Router, filters, F, types
from aiogram.fsm.state import StatesGroup, State
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, SwitchTo
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.input import MessageInput
from fluent.runtime import FluentLocalization
from tortoise.exceptions import DoesNotExist

from utils.widgets import FluentMessage, SelectUserButton
from db.models import User, Invite, Trip, ChatTripInfo


class UserManagementSG(StatesGroup):
    select_user = State()
    select_new_user = State()


router = Router()


@router.callback_query(F.data.startswith("manage_users_"))
async def manage_users(callback: types.CallbackQuery, dialog_manager: DialogManager):
    trip_id = callback.data[13:]
    strings: FluentLocalization = dialog_manager.middleware_data["strings"]

    has_access = await User.filter(id=callback.from_user.id, trips__id=trip_id).exists()
    if not has_access:
        await callback.message.answer(strings.format_value("trip-no-access"))
        return

    users = await User.filter(trips__id=trip_id)
    await dialog_manager.start(
        UserManagementSG.select_user, data={"users": users, "trip_id": trip_id}
    )


async def on_user_selected(
    callback: types.CallbackQuery, widget, dialog_manager: DialogManager, user_id: str
):
    strings: FluentLocalization = dialog_manager.middleware_data["strings"]
    trip = await Trip.get(id=dialog_manager.start_data["trip_id"])
    user = await User.get(id=user_id)
    await trip.participants.remove(user)
    await callback.answer(strings.format_value("user-removed"), show_alert=True)
    await dialog_manager.done()


async def on_user_add(message: types.Message, widget, dialog_manager: DialogManager):
    assert message.user_shared is not None
    strings: FluentLocalization = dialog_manager.middleware_data["strings"]
    try:
        user = await User.get(id=message.user_shared.user_id)
    except DoesNotExist:
        await Invite.create(
            user_id=message.user_shared.user_id,
            trip_id=dialog_manager.start_data["trip_id"],
        )
        await message.answer(strings.format_value("user-invited"))
    else:
        trip = await Trip.get(id=dialog_manager.start_data["trip_id"])
        await trip.participants.add(user)
        await message.answer(strings.format_value("user-added"))

    await dialog_manager.done()


async def getter(dialog_manager: DialogManager, **kwargs):
    return {"users": dialog_manager.start_data["users"]}


selection_dialog = Dialog(
    Window(
        FluentMessage("manage-users-message"),
        ScrollingGroup(
            Select(
                Format("@{item.name}"),
                id="select_user",
                item_id_getter=lambda item: item.id,
                items="users",
                on_click=on_user_selected,
            ),
            id="trips",
            width=1,
            height=5,
        ),
        SwitchTo(
            text=FluentMessage("select-new-user-button"),
            state=UserManagementSG.select_new_user,
            id="switch_new_user",
        ),
        getter=getter,
        state=UserManagementSG.select_user,
    ),
    Window(
        FluentMessage("select-new-user"),
        SelectUserButton(FluentMessage("select-new-user-button")),
        MessageInput(filter=F.user_shared, func=on_user_add),
        state=UserManagementSG.select_new_user,
        markup_factory=ReplyKeyboardFactory(
            resize_keyboard=True, one_time_keyboard=True
        ),
    ),
)


@router.message(filters.Command("invite_me"))
async def invite_me(message: types.Message, strings: FluentLocalization):
    try:
        user = await User.get(id=message.from_user.id)
    except DoesNotExist:
        await message.answer(strings.format_value("action-unregistered"))
        return
    try:
        current_chat = await ChatTripInfo.get(chat_id=message.chat.id).prefetch_related(
            "trip"
        )
        if current_chat.trip == None:
            raise DoesNotExist
        current_trip = current_chat.trip
    except DoesNotExist:
        await message.answer(strings.format_value("trip-not-set"))
        return

    await current_trip.participants.add(user)
    await message.answer(strings.format_value("invited"))
