import telebot
from telebot import types

TOKEN = "7884961487:AAFLm_ame2yHEHc-rIvipLtKer3kPAe8LsU" 
bot = telebot.TeleBot(TOKEN)

# Store user data
user_data = {}

subjects = ["Applied Maths 1", "English", "Entrepreneursh", "Anthropology ", "History","C++","Civic","Emerging Technologies " ]

score_to_gpa = {
    "90-100": 4,
    "85-90": 4,
    "80-85": 3.75,
    "75-80": 3.5,
    "70-75": 3,
    "65-70": 2.75,
    "60-65": 2.5,
    "50-60": 2,
    "45-50": 1.75,
    "40-45": 1,
    "<40": 0
}

# ---- HELPER: delete previous message ----
def delete_previous_message(chat_id):
    if chat_id in user_data and "msg_id" in user_data[chat_id]:
        try:
            bot.delete_message(chat_id, user_data[chat_id]["msg_id"])
        except:
            pass

# ---- START ----
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    # Delete any previous message
    delete_previous_message(chat_id)

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Eeyyee", callback_data="yes"),
        types.InlineKeyboardButton("Lakki", callback_data="no")
    )

    msg = bot.send_message(
        chat_id,
        "BAGA NAGAAN GARA ABbot DHUFTE\n\nGPA kee herreguu ni barbaaddaa?",
        reply_markup=markup
    )

    # Initialize user data
    user_data[chat_id] = {
        "msg_id": msg.message_id,
        "scores": {},
        "index": 0,
        "context": "start"
    }

# ---- CALLBACK HANDLER ----
@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    chat_id = call.message.chat.id
    msg_id = call.message.message_id

    # Always delete previous message for clean UI
    delete_previous_message(chat_id)

    if chat_id not in user_data:
        user_data[chat_id] = {"msg_id": msg_id, "scores": {}, "index": 0, "context": "start"}

    # ---- Lakki ----
    if call.data == "no":
        user_data[chat_id]["context"] = "lakki"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ Go Back", callback_data="back"))
        msg = bot.send_message(
            chat_id,
            "Kadhattuu wayii Eenyu abbaa keetu Kottu siin jedhe sila immoo, waxii, bukoo, distii, jabanaa wayii.",
            reply_markup=markup
        )
        user_data[chat_id]["msg_id"] = msg.message_id
        return

    # ---- Eeyyee ----
    if call.data == "yes":
        user_data[chat_id]["scores"] = {}
        user_data[chat_id]["index"] = 0
        user_data[chat_id]["context"] = "subjects"
        ask_subject(chat_id)
        return

    # ---- Go Back ----
    if call.data == "back":
        context = user_data[chat_id].get("context", "start")

        # From GPA, Lakki, or <50 warning -> go to start
        if context in ["gpa", "lakki", "less50"]:
            start(call.message)
            return

        # From subjects -> previous subject
        elif context == "subjects":
            user_data[chat_id]["index"] = max(0, user_data[chat_id]["index"] - 1)
            ask_subject(chat_id)
            return

        else:
            start(call.message)
            return

    # ---- Score selection ----
    if call.data.startswith("score_"):
        score = call.data.replace("score_", "")
        index = user_data[chat_id].get("index", 0)

        # <40 case
        if score == "<40":
            user_data[chat_id]["context"] = "less40"
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⬅️ Go Back", callback_data="back"))
            msg = bot.send_message(
                chat_id,
                "Galagali kadhattuu wayii budddeen mootummaa nyaattee kana fiduu keef iyyuu mana adabaa galuu qabda.",
                reply_markup=markup
            )
            user_data[chat_id]["msg_id"] = msg.message_id
            return

        # Save GPA
        subject = subjects[index]
        user_data[chat_id]["scores"][subject] = score_to_gpa[score]

        user_data[chat_id]["index"] = index + 1
        ask_subject(chat_id)

# ---- ASK SUBJECT ----
def ask_subject(chat_id):
    index = user_data[chat_id]["index"]

    # Delete previous message
    delete_previous_message(chat_id)

    # Finish all subjects
    if index >= len(subjects):
        total = sum(user_data[chat_id]["scores"].values())
        gpa = round(total / len(subjects), 2)

        user_data[chat_id]["context"] = "gpa"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("⬅️ Go Back", callback_data="back"))

        msg = bot.send_message(
            chat_id,
            f"🎓 Your GPA is: {gpa}",
            reply_markup=markup
        )
        user_data[chat_id]["msg_id"] = msg.message_id
        return

    subject = subjects[index]
    user_data[chat_id]["context"] = "subjects"

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = ["90-100","85-90","80-85","75-80","70-75","65-70","60-65","50-60","45-50","40-45","<40"]
    for b in buttons:
        markup.add(types.InlineKeyboardButton(b, callback_data=f"score_{b}"))
    markup.add(types.InlineKeyboardButton("⬅️ Go Back", callback_data="back"))

    msg = bot.send_message(
        chat_id,
        f"Qabxii {subject} galchi:",
        reply_markup=markup
    )
    user_data[chat_id]["msg_id"] = msg.message_id

bot.polling()