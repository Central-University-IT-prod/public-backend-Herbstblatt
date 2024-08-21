from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import types, filters, Router, F, enums
from aiogram.utils import formatting
from fluent.runtime import FluentLocalization
from tortoise.expressions import Q
from tortoise.exceptions import DoesNotExist

from db.models import Note, NoteVisibility, User, ChatTripInfo


router = Router()


class NoteSG(StatesGroup):
    add_text = State()
    add_title = State()
    set_privacy = State()


@router.message(filters.Command("notes"))
async def notes(message: types.Message, strings: FluentLocalization, web_app_url: str):
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

    msg = formatting.TextLink(
        formatting.Bold("Открыть список заметок"),
        url="https://t.me/plan_trip_bot/managetrip?startapp=notes_"
        + str(current_trip.id),
    )
    await message.answer(**msg.as_kwargs())

@router.message(filters.Command("note"))
async def note(message: types.Message, state: FSMContext, strings: FluentLocalization):
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

    await state.set_data({"current_trip": current_trip})
    if message.reply_to_message is not None:
        data = await state.get_data()
        data.update(
            {
                "text": message.reply_to_message.text,
                "chat_id": message.reply_to_message.chat.id,
                "msg_id": message.reply_to_message.message_id,
            }
        )
        await state.set_data(data)
        await state.set_state(NoteSG.add_title)
        await message.reply(strings.format_value("select-note-heading"))
    else:
        await state.set_state(NoteSG.add_text)
        await message.reply(strings.format_value("select-note-text"))


@router.message(filters.StateFilter(NoteSG.add_text))
async def insert_text(
    message: types.Message, state: FSMContext, strings: FluentLocalization
):
    data = await state.get_data()
    data.update(
        {"text": message.text, "chat_id": message.chat.id, "msg_id": message.message_id}
    )
    await state.set_data(data)
    await state.set_state(NoteSG.add_title)
    await message.reply(strings.format_value("select-note-heading"))


@router.message(filters.StateFilter(NoteSG.add_title))
async def insert_title(
    message: types.Message, state: FSMContext, strings: FluentLocalization
):
    data = await state.get_data()
    data.update({"title": message.text})
    await state.set_data(data)
    await state.set_state(NoteSG.set_privacy)

    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=strings.format_value("note-public"), callback_data="set_public"
                ),
                types.InlineKeyboardButton(
                    text=strings.format_value("note-private"),
                    callback_data="set_private",
                ),
            ]
        ]
    )

    await message.reply(
        strings.format_value("select-note-privacy"), reply_markup=keyboard
    )


@router.callback_query(filters.StateFilter(NoteSG.set_privacy))
async def set_privacy(
    callback: types.CallbackQuery, state: FSMContext, strings: FluentLocalization
):
    data = await state.get_data()
    if callback.data == "set_public":
        visibility = NoteVisibility.public
    else:
        visibility = NoteVisibility.private

    await Note.create(
        chat_id=data["chat_id"],
        message_id=data["msg_id"],
        title=data["title"],
        visibility=visibility,
        text=data["text"],
        owner_id=callback.from_user.id,
        trip=data["current_trip"],
    )
    await callback.answer()
    await callback.message.answer(strings.format_value("note-created"))
    await state.set_state(None)


@router.inline_query()
async def search_notes(query: types.InlineQuery, strings: FluentLocalization):
    notes = Note.filter(
        Q(visibility=NoteVisibility.public) | Q(owner__id=query.from_user.id),
        title__icontains=query.query,
    ).prefetch_related("owner", "trip")
    results = []
    async for note in notes:
        if not note.trip.participants.filter(id=query.from_user.id).exists():
            continue
        text = formatting.as_list(
            formatting.Bold(note.title),
            formatting.Italic(
                formatting.TextLink(
                    note.owner.name, url=f"tg://user?id={note.owner.id}"
                )
            ),
            note.text,
        )
        text_element = types.InputTextMessageContent(
            message_text=text.as_markdown(), parse_mode="MarkdownV2"
        )
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=strings.format_value("delete-note"),
                        callback_data=f"delete_note_{note.id}",
                    ),
                    types.InlineKeyboardButton(
                        text=strings.format_value("note-orig"),
                        callback_data=f"orig_note_{note.id}_{query.from_user.id}",
                    ),
                ]
            ]
        )
        results.append(
            types.InlineQueryResultArticle(
                input_message_content=text_element,
                id=str(note.id),
                title=note.title,
                description=note.text,
                reply_markup=keyboard,
            )
        )
        if len(results) == 50:
            break
    await query.answer(results=results, is_personal=True, cache_time=0)


@router.callback_query(F.data.startswith("orig_note_"))
async def get_orig_note(callback: types.CallbackQuery, strings: FluentLocalization):
    note_id = callback.data.split("_")[2]
    user_id = int(callback.data.split("_")[3])
    note = await Note.get(id=note_id)
    await callback.bot.copy_message(
        from_chat_id=note.chat_id, message_id=note.message_id, chat_id=user_id
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delete_note_"))
async def delete_note(callback: types.CallbackQuery, strings: FluentLocalization):
    note_id = callback.data[12:]
    await Note.filter(id=note_id).delete()
    await callback.answer(strings.format_value("note-deleted"), alert=True)
