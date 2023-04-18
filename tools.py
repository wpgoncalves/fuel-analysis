def word_capitalize(word: str) -> str:

    words = word.split()

    if len(words) > 1:
        return ' '.join(list(map(word_capitalize, words)))

    return word.capitalize()
