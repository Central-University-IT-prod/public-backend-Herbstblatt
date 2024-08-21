from aiogram import F, Router, filters, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils import formatting

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Select, ScrollingGroup
from aiogram_dialog.widgets.text import Format

from fluent.runtime import FluentLocalization
from tortoise.connection import connections
from tortoise.exceptions import DoesNotExist

from db.models import Trip, User, ChatTripInfo
from utils.widgets import FluentMessage


router = Router()


class TripCreationSG(StatesGroup):
    select_name = State()


class TripSelectionSG(StatesGroup):
    select_trip = State()


@router.message(filters.Command("new_trip"), filters.StateFilter(None))
async def begin_create_trip(
    message: types.Message, strings: FluentLocalization, state: FSMContext
):
    try:
        user = await User.get(id=message.from_user.id)
    except DoesNotExist:
        await message.answer(strings.format_value("action-unregistered"))
        return

    await state.set_state(TripCreationSG.select_name)
    await message.reply(strings.format_value("create-trip"))


@router.message(
    filters.StateFilter(TripCreationSG.select_name),
    (F.content_type == "text") & (F.text.len() < 100),
)
async def continue_create_trip(
    message: types.Message,
    strings: FluentLocalization,
    state: FSMContext,
    web_app_url: str,
):
    await state.set_state(None)
    trip = await Trip.create(name=message.text)

    user = await User.get(id=message.from_user.id)
    await trip.participants.add(user)

    # tortoise doesn't support upserts
    conn = connections.get("default")
    await conn.execute_insert(
        """
        INSERT INTO chattripinfo (chat_id, trip_id)
        VALUES ($1, $2)
        ON CONFLICT (chat_id) DO UPDATE
            SET trip_id = excluded.trip_id
    """,
        [message.chat.id, trip.id],
    )

    text = strings.format_value("create-trip-webapp-continue")
    if message.chat.type != "private":
        text += "\n" + strings.format_value("trip-group-access")

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=strings.format_value("create-trip-webapp-button"),
                    web_app=types.WebAppInfo(url=web_app_url + f"trip/{trip.id}"),
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=strings.format_value("trip-manage-users"),
                    callback_data=f"manage_users_{trip.id}",
                )
            ],
        ]
    )

    await message.answer(text, reply_markup=keyboard)


@router.message(
    filters.StateFilter(TripCreationSG.select_name), F.content_type == "text"
)
async def create_trip_name_invalid(
    message: types.Message, strings: FluentLocalization, state: FSMContext
):
    await message.reply(text=strings.format_value("create-trip-name-invalid"))


@router.message(filters.Command("current_trip"))
async def current_trip(
    message: types.Message, strings: FluentLocalization, web_app_url: str
):
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

    has_access = await current_trip.participants.filter(id=user.id).exists()
    if not has_access:
        await message.answer(strings.format_value("trip-no-access"))
        return

    await current_trip.fetch_related("points")
    route = [user.location_name]
    for point in current_trip.points:
        route.append(point.name)
    route.append(user.location_name)

    msg = formatting.as_list(
        formatting.as_key_value(
            strings.format_value("current-trip"), current_trip.name
        ),
        formatting.as_key_value(strings.format_value("route"), " — ".join(route)),
        formatting.TextLink(
            formatting.Bold("Открыть управление маршрутом"),
            url="https://t.me/plan_trip_bot/managetrip?startapp=route_"
            + str(current_trip.id),
        ),
    )

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=strings.format_value("trip-manage-users"),
                    callback_data=f"manage_users_{current_trip.id}",
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=strings.format_value("trip-map"),
                    callback_data=f"show_map_{current_trip.id}",
                ),
                types.InlineKeyboardButton(
                    text=strings.format_value("trip-delete"),
                    callback_data=f"trip_delete_{current_trip.id}",
                ),
            ],
        ]
    )

    await message.answer(**msg.as_kwargs(), reply_markup=keyboard)


async def on_trip_selected(
    callback: types.CallbackQuery, widget, manager: DialogManager, trip_id: str
):
    assert isinstance(callback.message, types.Message)
    await callback.answer()

    # tortoise doesn't support upserts
    conn = connections.get("default")
    await conn.execute_insert(
        """
        INSERT INTO chattripinfo (chat_id, trip_id)
        VALUES ($1, $2)
        ON CONFLICT (chat_id) DO UPDATE
            SET trip_id = excluded.trip_id
    """,
        [callback.message.chat.id, trip_id],
    )
    await callback.message.answer(
        manager.middleware_data["strings"].format_value("trip-selected")
    )
    await manager.done()


selection_dialog = Dialog(
    Window(
        FluentMessage("select-trip"),
        ScrollingGroup(
            Select(
                Format("{item.name}"),
                id="select_trip",
                item_id_getter=lambda item: item.id,
                items="start_data",
                on_click=on_trip_selected,
            ),
            id="trips",
            width=1,
            height=5,
        ),
        state=TripSelectionSG.select_trip,
    )
)


@router.message(filters.Command("select_trip"))
async def select_trip(
    message: types.Message,
    strings: FluentLocalization,
    web_app_url: str,
    dialog_manager: DialogManager,
):
    try:
        user = await User.get(id=message.from_user.id).prefetch_related("trips")
    except DoesNotExist:
        await message.answer(strings.format_value("action-unregistered"))
        return
    await dialog_manager.start(TripSelectionSG.select_trip, data=user.trips)


@router.callback_query(F.data.startswith("trip_delete_"))
async def delete_trip(callback: types.CallbackQuery, strings: FluentLocalization):
    await callback.answer()
    try:
        user = await User.get(id=callback.from_user.id)
    except DoesNotExist:
        await callback.message.answer(strings.format_value("action-unregistered"))
        return
    try:
        current_chat = await ChatTripInfo.get(
            chat_id=callback.message.chat.id
        ).prefetch_related("trip")
        if current_chat.trip == None:
            raise DoesNotExist
        current_trip = current_chat.trip
    except DoesNotExist:
        await callback.message.answer(strings.format_value("trip-not-set"))
        return

    has_access = await current_trip.participants.filter(id=user.id).exists()
    if not has_access:
        await callback.message.answer(strings.format_value("trip-no-access"))
        return

    await Trip.filter(id=callback.data[12:]).delete()
    await callback.message.answer(strings.format_value("trip-deleted"))
