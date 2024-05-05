from enum import Enum, unique

@unique
class ModelTypeRecommended(Enum):
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
        return next((choice for choice in ModelTypeRecommended if str(choice) == label), ModelTypeRecommended.SMALL)
    
    @staticmethod
    def from_value(value: str):
        return next((choice for choice in ModelTypeRecommended if choice.value == value), ModelTypeRecommended.SMALL)

    # Define your enum members with a unique integer and a common label.
    LARGE = ('large', 'Magas teljesítmény (ajánlott)')
    MEDIUM = ('medium', 'Közepes teljesítmény (ajánlott)')
    SMALL = ('small', 'Alacsony teljesítmény (ajánlott)')

    def __str__(self):
        # Return the label for the string representation.
        return self.label

@unique
class ModelType(Enum):
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
        return next((choice for choice in ModelType if str(choice) == label), ModelTypeRecommended.from_label(label))
    
    @staticmethod
    def from_value(value: str):
        return next((choice for choice in ModelType if choice.value == value), ModelTypeRecommended.from_value(value))

    # Define your enum members with a unique integer and a common label.
    LARGE = ('large', 'Magas teljesítmény')
    MEDIUM = ('medium', 'Közepes teljesítmény')
    SMALL = ('small', 'Alacsony teljesítmény')

    def __str__(self):
        # Return the label for the string representation.
        return self.label
    
    