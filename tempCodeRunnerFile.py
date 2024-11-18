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