import os
# from dotenv import load_dotenv
import google.generativeai as genai
import mysql.connector
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
import asyncio
import logging

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Initialize the Application instance with a timeout
application = Application.builder().token("7749804636:AAFoK7F06gBWQI10ew9c0fFTpXXyCUFnLyY").build()
application.bot.request.timeout = 120

# Load environment variables
# load_dotenv()

# Google Gemini API Key
genai.configure(api_key="AIzaSyA9nkK6zua8ztPFOLulFyopiKsFzayVY3Y")

# MySQL Connection
def connect_to_db():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Iswar@919",  # Replace with your MySQL password
            database="quiz_bot",
            port=3306
        )
        print(db)
        return db
    except mysql.connector.Error as e:
        logging.error(f"MySQL Connection Error: {e}")
        return None

db = connect_to_db()
cursor = db.cursor() if db else None

# Functions to Interact with Google Gemini API
# Functions to Interact with Google Gemini API
def generate_questions(topic, difficulty):
    prompt = f"""
    Generate a quiz with 5 multiple-choice questions on the topic "{topic}" with difficulty "{difficulty}".
    Each question should have 4 options: A, B, C, D. Specify the correct answer for each question.
    Format:
    Question: <question>
    A) <option>
    B) <option>
    C) <option>
    D) <option>
    Correct Answer: <correct option>
    """
    response = None  # Initialize response
    try:
        # Use the correct method (e.g., `chat` or another appropriate method)
        response = genai.chat(messages=[{"role": "user", "content": prompt}])
        return response['candidates'][0]['content'] if response else "No questions generated."
    except Exception as e:
        logging.error(f"Error generating questions: {e}. Full Response: {response}")
        return "Sorry, there was an error generating questions. Please try again later."



def parse_questions(response):
    questions = []
    if not response or "No questions generated" in response:
        return questions  # Return empty list if no questions generated

    blocks = response.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 6:
            continue
        try:
            question_text = lines[0].split("Question: ")[1].strip()
            options = {
                line[0]: line.split(") ")[1].strip() for line in lines[1:5] if ") " in line
            }
            correct_option = lines[5].split("Correct Answer: ")[1].strip()
            questions.append({
                "question": question_text,
                "options": options,
                "correct": correct_option
            })
        except IndexError:
            continue
    return questions


# Telegram Bot Handlers
async def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    username = update.message.from_user.username
    await update.message.reply_text(
        f"Welcome {username} to the Quiz Bot!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 Play Quiz", callback_data="play_quiz")],
            [InlineKeyboardButton("👤 View Profile", callback_data="view_profile")],
            [InlineKeyboardButton("🏆 Leaderboard", callback_data="view_leaderboard")]
        ])
    )

async def play_quiz(update: Update, context: CallbackContext):
    query = update.callback_query

    # Acknowledge the callback query
    await query.answer()

    try:
        # Attempt to edit the message text with inline keyboard options
        await query.edit_message_text(
            text="Choose a topic:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🌳 Nature", callback_data="topic_Nature")],
                [InlineKeyboardButton("⚙️ Science", callback_data="topic_Science")],
                [InlineKeyboardButton("🕰️ History", callback_data="topic_History")]
            ])
        )
    except Exception as e:
        # Log the error and send a new message if editing fails
        logging.error(f"Error editing message: {e}")
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="Choose a topic:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🌳 Nature", callback_data="topic_Nature")],
                [InlineKeyboardButton("⚙️ Science", callback_data="topic_Science")],
                [InlineKeyboardButton("🕰️ History", callback_data="topic_History")]
            ])
        )


async def topic_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    topic = query.data.split("_")[1]
    await query.edit_message_text(
        f"Topic selected: {topic}. Choose difficulty:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Easy", callback_data=f"difficulty_Easy_{topic}")],
            [InlineKeyboardButton("Medium", callback_data=f"difficulty_Medium_{topic}")],
            [InlineKeyboardButton("Hard", callback_data=f"difficulty_Hard_{topic}")]
        ])
    )

async def difficulty_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    difficulty, topic = query.data.split("_")[1], query.data.split("_")[2]
    await query.answer("Generating questions... Please wait.")
    response = generate_questions(topic, difficulty)
    
    # Parse questions and initialize context
    questions = parse_questions(response)
    if not questions:  # Check if questions list is empty
        await query.answer("No questions generated. Please try a different topic or difficulty.")
        return
    
    context.user_data["questions"] = questions
    context.user_data["current_index"] = 0  # Initialize current_index
    await send_question(query, context)


async def send_question(query, context):
    # Retrieve the questions list and current index from user data
    questions = context.user_data.get("questions", [])
    current_index = context.user_data.get("current_index", 0)

    # Check if questions are empty
    if not questions:
        await query.answer("No questions available.")
        return

    # Ensure the current index is within bounds
    if current_index >= len(questions):
        await query.answer("No more questions available. Quiz is complete.")
        context.user_data["current_index"] = 0  # Reset index for future quizzes
        await query.edit_message_text("You have completed the quiz! 🎉")
        return

    # Retrieve the current question using the current_index
    question_data = questions[current_index]
    question_text = question_data.get("question", "No question text available.")
    options = question_data.get("options", {})

    # Construct options for InlineKeyboard
    keyboard = [
        [InlineKeyboardButton(f"{key}) {value}", callback_data=f"answer_{key}_{current_index}")]
        for key, value in options.items()
    ]

    # Send the question with options as inline buttons
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"Question {current_index + 1}: {question_text}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # Update the current index for the next question
    context.user_data["current_index"] += 1





async def exit_quiz(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.edit_message_text("Quiz exited. Returning to the main menu.")
    await start(update, context)

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(play_quiz, pattern="play_quiz"))
application.add_handler(CallbackQueryHandler(topic_selection, pattern=r"topic_"))
application.add_handler(CallbackQueryHandler(difficulty_selection, pattern=r"difficulty_"))
application.add_handler(CallbackQueryHandler(exit_quiz, pattern="exit_quiz"))

# Start the bot
if __name__ == "__main__":
    asyncio.run(application.run_polling())
