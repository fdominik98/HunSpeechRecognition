from enum import Enum, unique


@unique
class ProcessState(Enum):
    def __new__(cls, value, label):
        # Create a new instance of the class.
        obj = object.__new__(cls)
        # Set the value attribute to the unique value.
        obj._value_ = value
        # Store the label that will be used for the string representation.
        obj.label = label
        return obj

    @staticmethod
    def from_label(label: str):
        return next((choice for choice in ProcessState if str(choice) == label), ProcessState.STOPPED)

    # Define your enum members with a unique integer and a common label.
    SPLITTING = (0, 'Szegmentálás')
    TRIMMING = (1, 'Trimmelés')
    TRANSCRIPTING = (2, 'Transzkriptálás')
    SPLITTING_TRIMMING = (3, 'Szegmentálás + Trimmelés')
    SPLITTING_TRANSCRIPTING = (4, 'Szegmentálás + Transzkriptálás')
    TRIMMING_TRANSCRIPTING = (5, 'Trimmelés + Transzkriptálás')
    SPLITTING_TRIMMING_TRANSCRIPTING = (
        6, 'Szegmentálás + Trimmelés + Transzkriptálás')
    STOPPED = (7, 'Szünetel')

    def __str__(self):
        # Return the label for the string representation.
        return self.label


non_trimming_options = [str(ProcessState.SPLITTING), str(
    ProcessState.TRANSCRIPTING), str(ProcessState.SPLITTING_TRANSCRIPTING)]
