# Инструкция пользователя бота

https://t.me/plan_trip_bot

## Регистрация

Регистрация — обязательная часть взаимодействия с ботом. С помощью регистрации бот 

## Поездка и приглашения

Поездка — путешествие, в которое вы собираетесь один или с друзьями. Бот хранит список ваших поездок и помогает вам в них ориентироваться.
Чтобы создать поездку, напишите `/new_trip` в любом чате с ботом. У Вас спросят несколько вопросов, после чего перенаправят на страницу настройки маршрута.

В маршрут есть возможность приглашать друзей. У них будут такие же возможности, как у владельца поездки, в том числе возможность приглашать других пользователей или даже удалить маршрут. 

Так как обсуждение поездок часто происходит в группах, бот приспособлен для работы и в них. Считается, что все участники группы имеют отношение к поездке, поэтому у них есть возможность получить приглашение по упрощённой схеме, без участия владельца поездки. Для этого нужно набрать команду `/invite_me` в соответствующей группе.

Если пользователь, которого вы приглашаете, ещё не зарегиcтрирован, он получит приглашение автоматически как только зарегистрируется.

## Заметки

У Вас есть возможность вести заметки по путешествию. Заметки можео использовать для сохранения информации о билетах, тратах, бронированиях и др. Для создания заметки воспользуйтесь командой `/note` в чате, в котором есть активная поездка. Текст заметки можно написать вручную или взять из уже существующего сообщения (в таком случае нужно послать команду в ответ на это сообщение). Также нужно будет указать заголовок заметки и её видимость.

Заметки могут быть публичными и приватными. Публичные заметки доступны всем участникам путешествия, а приватные — только вам.

Посмотреть свои заметки (а также публичные заметки других) можно с помощью инлайн-команд — просто упомяните бота и начните писать заголовок. Сохраняется всё сообщение, включая картинки и вложения. Также вы можете увидеть весь список заметок в веб-интерфейсе бота, для доступа наберите `/notes`.

Обратите внимание, что для работы интерактивных меню необходимо разрешить боту читать сообщения (или отвечать на сообщения бота вручную).