import hunspell

def check_spelling(text, language='hu_HU'):
    # Initialize Hunspell with the Hungarian dictionary
    hunspell_dict_path = '/usr/share/hunspell'  # Path to Hunspell dictionaries
    hun = hunspell.HunSpell(f'{hunspell_dict_path}/{language}.dic', f'{hunspell_dict_path}/{language}.aff')

    # Check each word in the text
    for word in text.split():
        if not hun.spell(word):
            print(f'Misspelled or unknown word: {word}')

# Example usage
text = "your example text in Hungarian"
check_spelling(text)