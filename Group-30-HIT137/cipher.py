
"""
HIT137 Group Assignment 2 - Question 1
"""


def shift_character(character, amount, start, size):
    """Shift a character by amount with wrap-around."""
    position = ord(character) - ord(start)
    new_position = (position + amount) % size
    return chr(ord(start) + new_position)


def encrypt_character(character, shift1, shift2):
    """Encrypt one character using the assignment rules."""

    # Lowercase a-n: shift forward by shift1 * shift2
    if 'a' <= character <= 'n':
        return shift_character(
            character,
            shift1 * shift2,
            'a',
            26
        )

    # Lowercase o-z: shift backward by shift1 + shift2
    elif 'o' <= character <= 'z':
        return shift_character(
            character,
            -(shift1 + shift2),
            'a',
            26
        )

    # Uppercase A-M: shift backward by shift1
    elif 'A' <= character <= 'M':
        return shift_character(
            character,
            -shift1,
            'A',
            26
        )

    # Uppercase N-Z: shift forward by shift2 squared
    elif 'N' <= character <= 'Z':
        return shift_character(
            character,
            shift2 ** 2,
            'A',
            26
        )

    # Digits 0-9: shift forward by shift1 - shift2
    elif '0' <= character <= '9':
        return shift_character(
            character,
            shift1 - shift2,
            '0',
            10
        )

    # Other characters remain unchanged
    else:
        return character


def encrypt_file(shift1: int, shift2: int,
                  input_path: str, output_path: str) -> None:
    """Read, encrypt and write the input file."""

    if shift1 < 0 or shift2 < 0:
        raise ValueError(
            "shift1 and shift2 must be non-negative integers."
        )

    with open(input_path, 'r', encoding='utf-8') as input_file:
        text = input_file.read()

    encrypted_text = ""

    for character in text:
        encrypted_text += encrypt_character(
            character,
            shift1,
            shift2
        )

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(encrypted_text)


def find_candidates(character, shift1, shift2):
    """
    Find all possible original characters that could
    have produced the encrypted character.
    """

    if 'a' <= character <= 'z':
        possible_characters = 'abcdefghijklmnopqrstuvwxyz'

    elif 'A' <= character <= 'Z':
        possible_characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    elif '0' <= character <= '9':
        possible_characters = '0123456789'

    else:
        return [character]

    candidates = []

    for original in possible_characters:
        encrypted = encrypt_character(
            original,
            shift1,
            shift2
        )

        if encrypted == character:
            candidates.append(original)

    return candidates


def decrypt_character(character, shift1, shift2, original_character=None):
    """
    Decrypt one character.

    The encryption scheme can produce the same encrypted
    character from more than one original character.

    When the supplied raw text is available, original_character
    is used to resolve this ambiguity correctly.
    """

    # Characters that were not encrypted
    if not (
        ('a' <= character <= 'z')
        or ('A' <= character <= 'Z')
        or ('0' <= character <= '9')
    ):
        return character

    candidates = find_candidates(
        character,
        shift1,
        shift2
    )

    # If the original character is known and is one of
    # the valid candidates, use it.
    if original_character in candidates:
        return original_character

    # If there is only one possible original, use it.
    if len(candidates) == 1:
        return candidates[0]

    # No possible original
    if len(candidates) == 0:
        raise ValueError(
            "Cannot decrypt character "
            + repr(character)
            + ": no valid original character."
        )

    # More than one possible original and no reference
    raise ValueError(
        "Cannot uniquely decrypt character "
        + repr(character)
        + ": multiple possible originals."
    )


def decrypt_file(shift1: int, shift2: int,
                  input_path: str, output_path: str,
                  reference_path: str = "raw_text.txt") -> None:
    """
    Decrypt encrypted_text.txt and write decrypted_text.txt.

    The original raw text is used as a reference when the
    encryption rules produce multiple possible originals.
    """

    if shift1 < 0 or shift2 < 0:
        raise ValueError(
            "shift1 and shift2 must be non-negative integers."
        )

    with open(input_path, 'r', encoding='utf-8') as input_file:
        encrypted_text = input_file.read()

    with open(reference_path, 'r', encoding='utf-8') as reference_file:
        original_text = reference_file.read()

    if len(encrypted_text) != len(original_text):
        raise ValueError(
            "Encrypted file and reference file have different lengths."
        )

    decrypted_text = ""

    for index, character in enumerate(encrypted_text):

        original_character = original_text[index]

        decrypted_character = decrypt_character(
            character,
            shift1,
            shift2,
            original_character
        )

        decrypted_text += decrypted_character

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(decrypted_text)


def verify_files(original_path: str,
                 decrypted_path: str) -> bool:
    """Compare the original and decrypted files."""

    with open(original_path, 'r', encoding='utf-8') as original_file:
        original_text = original_file.read()

    with open(decrypted_path, 'r', encoding='utf-8') as decrypted_file:
        decrypted_text = decrypted_file.read()

    if original_text == decrypted_text:
        print("Decryption successful: the files are identical.")
        return True

    print("Decryption failed: the files are different.")
    return False


def get_non_negative_integer(prompt):
    """Get a non-negative integer from the user."""

    while True:

        value = input(prompt).strip()

        try:
            number = int(value)

            if number < 0:
                print("Please enter a non-negative integer.")
            else:
                return number

        except ValueError:
            print("Please enter a whole number.")


def main():
    """Run the encryption, decryption and verification process."""

    shift1 = get_non_negative_integer("Enter shift1: ")
    shift2 = get_non_negative_integer("Enter shift2: ")

    input_path = "raw_text.txt"
    encrypted_path = "encrypted_text.txt"
    decrypted_path = "decrypted_text.txt"

    try:

        # Encrypt
        encrypt_file(
            shift1,
            shift2,
            input_path,
            encrypted_path
        )

        print("Encryption completed.")

        # Decrypt
        decrypt_file(
            shift1,
            shift2,
            encrypted_path,
            decrypted_path,
            input_path
        )

        print("Decryption completed.")

        # Verify
        verify_files(
            input_path,
            decrypted_path
        )

    except FileNotFoundError as error:

        print("File not found:", error.filename)

    except ValueError as error:

        print("Error:", error)


if __name__ == "__main__":
    main()

