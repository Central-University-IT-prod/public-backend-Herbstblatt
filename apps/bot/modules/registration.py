from aiogram import types, Router, filters, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import aiohttp
from fluent.runtime import FluentLocalization

from db.models import User, Invite


class RegistrationSG(StatesGroup):
    start = State()
    reselect_location = State()
    select_location = State()
    location_selected = State()
    suggest_bio = State()
    done = State()


async def query_city_by_coords(lat: float, long: float):
    path = "https://nominatim.openstreetmap.org/reverse"
    async with aiohttp.ClientSession() as sess:
        async with sess.get(
            path, params=dict(lat=lat, lon=long, zoom=10, format="json")
        ) as resp:
            result = await resp.json()
    return (
        result["osm_type"] + str(result["osm_id"]),
        result["display_name"],
        result["name"],
    )


async def query_city_by_name(name: str):
    path = "https://nominatim.openstreetmap.org/search"
    async with aiohttp.ClientSession() as sess:
        async with sess.get(path, params=dict(q=name, format="json")) as resp:
            results = await resp.json()
    try:
        result = results[0]
    except IndexError as exc:
        raise ValueError("Not found") from exc

    return (
        result["osm_type"] + str(result["osm_id"]),
        result["display_name"],
        result["name"],
        float(result["lat"]),
        float(result["lon"]),
    )


router = Router()


async def start_registration(
    message: types.Message, strings: FluentLocalization, state: FSMContext
):
    await state.set_state(RegistrationSG.start)
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=strings.format_value("begin"), callback_data="select-location"
                ),
            ]
        ]
    )
    await message.answer(
        strings.format_value("welcome-unregistered"), reply_markup=keyboard
    )


@router.callback_query(
    filters.StateFilter(RegistrationSG.location_selected, RegistrationSG.start),
    F.data == "select-location",
)
async def ask_location(
    callback: types.CallbackQuery | None = None,
    strings: FluentLocalization = ...,
    state: FSMContext = ...,
    message: types.Message | None = None,
):
    await state.set_state(RegistrationSG.select_location)

    if callback is not None:
        assert callback is not None and isinstance(callback.message, types.Message)
        await callback.answer()
        message = callback.message

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(
                    text=strings.format_value("select-location-button"),
                    request_location=True,
                )
            ]
        ],
        one_time_keyboard=True,
        resize_keyboard=True,
    )
    await message.answer(strings.format_value("select-location"), reply_markup=keyboard)


@router.message(filters.StateFilter(RegistrationSG.select_location))
async def handle_location(
    message: types.Message, strings: FluentLocalization, state: FSMContext
):
    # remove keyboard
    msg = await message.answer("...", reply_markup=types.ReplyKeyboardRemove())
    await msg.delete()

    if message.location is not None:
        code, name, short_name = await query_city_by_coords(
            message.location.latitude, message.location.longitude
        )
        await state.set_data(
            {
                "location-code": code,
                "location-name": name,
                "location-short-name": short_name,
                "location-lat": message.location.latitude,
                "location-long": message.location.longitude,
            }
        )
    else:
        try:
            code, name, short_name, lat, long = await query_city_by_name(
                message.text or "Караганда"
            )
        except ValueError:
            await message.answer(
                "К сожалению, я не нашёл такой город. Попробуйте снова."
            )
            return
        await state.set_data(
            {
                "location-code": code,
                "location-name": name,
                "location-short-name": short_name,
                "location-lat": lat,
                "location-long": long,
            }
        )

    await state.set_state(RegistrationSG.location_selected)
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=strings.format_value("location-reselect"),
                    callback_data="select-location",
                ),
                types.InlineKeyboardButton(
                    text=strings.format_value("location-approve"),
                    callback_data="approve-location",
                ),
            ]
        ]
    )

    await message.answer(
        strings.format_value("location-selected", {"location-name": name}),
        reply_markup=keyboard,
    )


@router.callback_query(
    filters.StateFilter(RegistrationSG.location_selected), F.data == "approve-location"
)
async def location_approved(
    callback: types.CallbackQuery, strings: FluentLocalization, state: FSMContext
):
    await state.set_state(RegistrationSG.suggest_bio)
    await callback.answer()
    await callback.message.answer(strings.format_value("select-bio"))


@router.message(filters.StateFilter(RegistrationSG.suggest_bio))
async def handle_bio(
    message: types.Message, strings: FluentLocalization, state: FSMContext
):
    skipped = False
    for entity in message.entities or []:
        if (
            entity.type == "bot_command"
            and entity.extract_from(message.text) == "/skip"
        ):
            skipped = True
    if skipped:
        bio = ""
    else:
        bio = message.text

    assert message.from_user is not None
    name = message.from_user.username or message.from_user.full_name

    data = await state.get_data()
    user = await User.create(
        id=message.from_user.id,
        bio=bio,
        name=name,
        location=data["location-code"],
        location_lat=data["location-lat"],
        location_long=data["location-long"],
        location_name=data["location-short-name"],
    )

    invites = await Invite.filter(user_id=user.id).prefetch_related("trip")
    await user.trips.add(*(inv.trip for inv in invites))

    text = strings.format_value("registered")
    if len(invites) > 0:
        text += "\n" + strings.format_value(
            "registered-invite",
            args={"trips": ", ".join(inv.trip.name for inv in invites)},
        )
    await message.answer(text)
    await state.set_state(None)
