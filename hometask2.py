from collections import UserDict
from datetime import datetime, timedelta

class UserValueError(ValueError):
    pass

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
            raise UserValueError("The name must be a non-empty string.")
        super().__init__(value.strip())


# Class for phone numbers with validation
class Phone(Field):
    def __init__(self, value:str):
        # vakidate phone number: must be a string of 10 digits
        if not (isinstance(value, str) and value.isdigit() and len(value) == 10):
            raise UserValueError("The phone number must be a string of exactly 10 digits.")
        super().__init__(value)

# Class for birthdays with validation and save as a date object
class Birthday(Field):
    def __init__(self, value:str):
        if not isinstance(value, str):
            raise UserValueError("Birthday must be a string in the format DD.MM.YYYY")
        try:
             date_input = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise UserValueError("Invalid date format. Use DD.MM.YYYY")
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
            raise UserValueError("Invalid old phone number format. It must be a string of exactly 10 digits.")
        
        try:
            valid_new_phone = Phone(new_phone_number) 
        except ValueError as e:
            raise UserValueError("Invalid new phone number format. It must be a string of exactly 10 digits.") 

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

# decorator to handle input errors 
def input_error(func):
    """
     Decorator to handle input errors for functions that process user input.
     This decorator catches specific exceptions such as ValueError, KeyError, and IndexError,
     and returns user-friendly error messages instead of raising exceptions.
     
     Args:
         func (callable): The function to be decorated.
     Returns:
         callable: The decorated function that handles input errors.
    """
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except UserValueError as e:
            return str(e) if str(e) else "Invalid value format. Please check your value."
        except ValueError as e:
            return "Give me name and phone or birthday please."
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid number of arguments. Please check your input."
        except Exception as e:
            return f"An unexpected error occurred: {e}"
    return inner


@input_error
def parse_input(user_input: str)-> tuple[str, ...]:
    """
    Parses user input into a command and its arguments.
    This function splits the input string into a command and its arguments,
    ensuring that the command is in lowercase and stripped of leading/trailing whitespace.
    If the input is empty, it returns an empty tuple.

    Args:   
        user_input (str): The input string from the user.
    Returns:   
        tuple[str, ...]: A tuple containing the command and its arguments.
    """

    if not user_input.strip(): 
        return ("",)  # Return a tuple with an empty string if input is empty
    
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args:tuple[str, ...], book: AddressBook) -> str:
    """ 
    Adds a new contact or updates an existing contact's phone number.
    If the contact already exists, it prompts the user to update the phone number.

    Args:
        args (tuple[str, str]): A tuple containing the contact name and phone number.
        book (AddressBook): An instance of AddressBook where contacts are stored.
    Returns:
        str: A message indicating whether the contact was added or updated.
    """
    # raise ValueError if the number of arguments is not equal to 2
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args: tuple[str, ...], book: AddressBook) -> str:  
    """
    Changes the phone number for an existing contact.

    Args:
        args (tuple[str, str, str]): A tuple containing the contact name, old phone number, and new phone number.
        book (AddressBook): An instance of AddressBook where contacts are stored.
    Returns:
        str: A message indicating whether the contact was updated, the old phone number was not found, or the new phone number already exists.   
    """
    # raise ValueError if the number of arguments is not equal to 3
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record:
        if record.edit_phone(old_phone, new_phone):
            message= "Contact updated."
        else:
            if record.find_phone(new_phone):
                message = f"Phone number {new_phone} already exists for contact {name}."
            else:
                message =  f"Phone number {old_phone} not found for contact {name}."
    else:
        message =  f"Contact {name} not found."
    return message  
    
@input_error
def show_phone(args: tuple[str, ...], book: AddressBook) -> str:
    """
    Shows the phone number for a given contact name.

    Args:  
        args (tuple[str]): A tuple containing the contact name.
        book (AddressBook): An instance of AddressBook where contacts are stored.
    Returns:
        str: A message indicating the phone number for the contact or that the contact was not found.
    """
    # raise index error if args is empty
    try:
        name, *_ = args
    except Exception:
        raise IndexError
    
    record = book.find(name)
    if record:
        return f"Phone number for {name} is {', '.join(phone.value for phone in record.phones)}."
    else:
        return f"Contact {name} not found."

@input_error
def show_all(book: AddressBook) -> str:
    """
    Returns a string representation of all contacts in the address book.

    Args:
        book (AddressBook): An instance of AddressBook where contacts are stored.
    Returns:
        str: A string containing all contacts and their phone numbers, or a message indicating that no contacts are available.
    """      
    if not book.data: 
        return "No contacts available."
    result = ""
    for name, record in book.data.items():
        phones = ', '.join(phone.value for phone in record.phones)
        result += f"\n{name}: {phones}"
    return result

@input_error
def add_birthday(args, book) -> str:
    """
    Adds a birthday for a contact.

    Args:
        args (tuple[str, str]): A tuple containing the contact name and birthday in the format DD.MM.YYYY.
        book (AddressBook): An instance of AddressBook where contacts are stored.
    Returns:
        str: A message indicating whether the birthday was added or if the contact was not found.
    """
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday for {name} added."
    else:
        return f"Contact {name} not found."

@input_error
def show_birthday(args, book) ->str:
    """
    Shows the birthday for a given contact name.
    
    Args:
        args (tuple[str]): A tuple containing the contact name.
        book (AddressBook): An instance of AddressBook where contacts are stored.
    Returns:
        str: A message indicating the birthday for the contact or that the contact was not found.
    """
    try:
        name, *_ = args
    except Exception:
        raise IndexError
    
    record = book.find(name)
    if record:
        return f"Birthday for {name} is {record.birthday.value.strftime('%d.%m.%Y')}."
    else:
        return f"Contact {name} not found."

@input_error
def birthdays(book)->str:
    """ 
    Returns a text of upcoming birthdays within the next 7 days.

    Args:
        book (AddressBook): An instance of AddressBook where contacts are stored.
    Returns:
        str: A string containing upcoming birthdays or a message indicating that there are no upcoming birthdays.
    """
    result=""
    for user in book.get_upcoming_birthdays():
        result += f"\nUpcoming birthday for {user['name']} on {user['congratulation_date']}."
    if not result:
        return "No upcoming birthdays in the next 7 days."
    else:
        return result
    

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))   
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))  
        elif command == "add-birthday":
            print(add_birthday(args, book))  
        elif command == "show-birthday":
           print(show_birthday(args, book))  
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")
    

if __name__ == "__main__":
    main()