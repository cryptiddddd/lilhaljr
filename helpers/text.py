def clean_string(text: str) -> str:
    """
    Cleans a string of all punctuation, returns it lowercase.
    :param text: Input text.
    :return: Output text.
    """
    new_text = ""
    for i in text.lower():
        # Save letters, numbers, and spaces.
        if i.isalnum() or i.isspace():
            new_text += i

    return new_text
