

Telegram Comprehension Quiz Bot

Project Overview:
This is a Telegram bot that provides a comprehension quiz on various topics. Users can select a topic, read a passage, and answer multiple-choice questions. After 10 questions, the bot will display the user's score and allow them to select a new topic to start another quiz round.

Features:
1. Main Menu: Users can choose from 4-5 topics (e.g., Nature, Science, History, Literature, Technology).
2. Comprehension Display: A 100-150 word passage on the selected topic is shown.
3. Quiz Flow: 10 multiple-choice questions with 4 options each.
   - Correct answer: "Great job! That's correct!"
   - Incorrect answer: "Good try! The correct answer is [Correct Answer]."
4. Navigation: 
   - Users can go to the next question or select another topic from the main menu.
5. Scoring: After 10 questions, the bot displays the user’s score (out of 10) and prompts them to select a new topic.

Database Requirements:
- UserID: Unique ID for each user.
- Topic Selected: Track the chosen topic.
- Current Question Index: Track which question the user is on.
- User’s Score: Track the user's score.

 Operations:
- Insert: Add a new user when they start a quiz.
- Update: Update the question index and score after each question.
- Reset: Reset the quiz data after completing a quiz.

Technical Requirements:
- Language: Python (or another preferred language that supports Telegram's API).
- Database: PostgreSQL or MySQL to store user data.
- State Management: Store user data (current question, score, etc.) in the database.
- Error Handling: Handle unexpected inputs and database connectivity issues.

Setup Instructions:
1. Install Dependencies:
   - Install Python packages: `python-telegram-bot`, `mysql-connector-python`, etc.
   - Set up your database (PostgreSQL or MySQL).
   
2. Database Setup:
   - Create a database with tables for users, topics, questions, and answers.
   - Schema provided in the file `database_schema.sql`.

3. Bot Configuration:
   - Replace the `API_KEY` with your Telegram bot's API key in the code.
   
4. Run the Bot:
   - Run the script: `python bot_script.py`.
   - The bot will start, and you can interact with it on Telegram.

Database Schema:
- Users:
  - `UserID (INT)`
  - `TopicSelected (VARCHAR)`
  - `CurrentQuestionIndex (INT)`
  - `Score (INT)`
  
- Questions:
  - `QuestionID (INT)`
  - `Topic (VARCHAR)`
  - `QuestionText (TEXT)`
  - `OptionA (TEXT)`
  - `OptionB (TEXT)`
  - `OptionC (TEXT)`
  - `OptionD (TEXT)`
  - `CorrectAnswer (VARCHAR)`
