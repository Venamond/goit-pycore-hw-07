from collections import UserDict
from datetime import datetime, timedelta

# Basic class for fields in the address book
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

# Class for names with validation
class Name(Field):
    def __init__(self, value: str):
        #validate name: must be a non-empty string
        if not isinstance(value, str) or not value.strip():
            raise ValueError("The name must be a non-empty string.")
        super().__init__(value.strip())


# Class for phone numbers with validation
class Phone(Field):
    def __init__(self, value:str):
        # vakidate phone number: must be a string of 10 digits
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise ValueError("The phone number must be a string of exactly 10 digits.")
        super().__init__(value)

# Class for birthdays with validation and save as a date object
class Birthday(Field):
    def __init__(self, value:str):
        if not isinstance(value, str):
            raise ValueError("Birthday must be a string in the format DD.MM.YYYY")
        try:
             date_input = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(date_input)

# Class for a contact record, which includes a name and a list of phone numbers
class Record:
    def __init__(self, name:str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)

    def find_phone(self, phone_number: str) -> Phone | None:
        """Find a phone in the record by its number."""
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def add_phone(self, phone_number: str) -> None:
        """Add a new phone to the record."""
        phone_value = self.find_phone(phone_number)
        if not phone_value:
        #if not any(ph.value == phone_value for ph in self.phones):
            self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number: str) -> bool:
        """Removes a phone from the record by its number."""
        phone_remove = self.find_phone(phone_number)
        if phone_remove:
            self.phones.remove(phone_remove)
            return True
        else:
            return False


    def edit_phone(self, old_phone_number: str, new_phone_number: str) -> bool:
        """Edit an existing phone number in the record. """
        try:
            Phone(old_phone_number) 
        except ValueError as e:
            raise ValueError("Invalid old phone number format. It must be a string of exactly 10 digits.")
        
        try:
            valid_new_phone = Phone(new_phone_number) 
        except ValueError as e:
            raise ValueError("Invalid new phone number format. It must be a string of exactly 10 digits.") 

        phone_to_edit = self.find_phone(old_phone_number)
        if phone_to_edit and not self.find_phone(new_phone_number):
            phone_to_edit.value = valid_new_phone.value
            return True
        else:
            return False

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

# Class for the address book, which holds multiple records
class AddressBook(UserDict):
    def add_record(self, record: Record):
        """Adds a Record to the address book. If a record with the same name exists, it overwrites it."""
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        """Find a Record by name. Returns None if not found."""
        return self.data.get(name)

    def delete(self, name: str)-> bool:
        """Delete a Record by name."""
        if name in self.data:
            del self.data[name]
            return True
        else:
            return False
    from datetime import datetime, timedelta

    # Function to get upcoming birthdays within the next 7 days
    def get_upcoming_birthdays(self) -> list[dict[str,str]]:
        """
        Function return a list of users whose birthdays occur within the next 7 days,
        adjusting for leap-year dates and weekend celebrations.

        Args:
            users (list[dict[str, str]]): A list of user dictionaries, each with "name" and "birthday" (DD.MM.YYYY).
        Returns:
            list[dict[str, str]]: A list of dictionaries, each with "name" and "congratulation_date" (DD.MM.YYYY)
                                for birthdays falling within the next 7 days.
                                Weekend birthdays are shifted to the following Monday.
                                Feb 29 birthdays in non-leap years are shifted to March 1.
        """
        today = datetime.today().date()
        result: list[dict[str, str]] = []  

        for user in self.data.values():
            user_birthday = user.birthday.value # birthday sttored as a date object
            try:
                birthday_this_year = user_birthday.replace(year=today.year)
            except ValueError:
                # If it was February 29 and the year is not a leap year, we celebrate March 1
                birthday_this_year = datetime(today.year, 3, 1).date()

            if birthday_this_year < today:
                try:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)
                except ValueError:   
                    # If it will February 29 and the year is not a leap year, we celebrate March 1
                    birthday_this_year = datetime(today.year+1, 3, 1).date()

            days_count= (birthday_this_year - today).days

            if 0 <= days_count <= 7:
                iso_weekday = birthday_this_year.isoweekday()
                if iso_weekday >= 6: # Saturday or Sunday
                        congratulation_date=birthday_this_year+ timedelta(days= 8 - iso_weekday)
                else:
                        congratulation_date=birthday_this_year

                result.append({"name": user.name.value,"congratulation_date": congratulation_date.strftime("%d.%m.%Y")})
        return result
    
    def __str__(self):
        if not self.data:
            return "Address book is empty."
        return "\n".join(str(record) for record in self.data.values())


if __name__ == "__main__":
 # Створення нової адресної книги
    book = AddressBook()

    # Створення запису для John
    john_record = Record("John")
    john_record.add_phone("1234567890")
    john_record.add_phone("5555555555")
    john_record.add_birthday("12.07.1990")  # Додавання дня народження John

    # Додавання запису John до адресної книги
    book.add_record(john_record)

    # Створення та додавання нового запису для Jane
    jane_record = Record("Jane")
    jane_record.add_phone("9876543210")
    jane_record.add_birthday("29.02.1992")  # Додавання дня народження Jane
    book.add_record(jane_record)

    #Отримання майбутніх днів народження
    print(book.get_upcoming_birthdays())  

    # Виведення всіх записів у книзі
    for name, record in book.data.items():
        print(record)

    # Знаходження та редагування телефону для John
    john = book.find("John")
    john.edit_phone("1234567890", "1112223333")

    print(john)  # Виведення: Contact name: John, phones: 1112223333; 5555555555

    # Пошук конкретного телефону у записі John
    found_phone = john.find_phone("5555555555")
    print(f"{john.name}: {found_phone}")  # Виведення: 5555555555

    # Видалення запису Jane
    book.delete("Jane")
    print(book)  # Виведення: Contact name: John, phones: 1112223333; 5555555555
