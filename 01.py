import pickle
import os
import datetime
from collections import UserDict, defaultdict

class CustomError(Exception):
    pass

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value
    
    @property
    def value(self):
        return self.__value
    @value.setter
    def value(self, value):
        max_length = 10
        if len(value) == max_length and all([d.isdigit() for d in value]):
            self.__value = value 
        else:
            raise CustomError("Phone should be = 10 symbols")

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        self.__value = None
        self.value = value
    
    @property
    def value(self):
        return self.__value
    @value.setter
    def value(self, value):
        try:
            datetime.datetime.strptime(value, '%d.%m.%Y')
        except ValueError:
            raise CustomError("Incorrect data format, should be DD.MM.YYYY")
        today = datetime.datetime.today().date()
        birthday = datetime.datetime.strptime(value, '%d.%m.%Y').date()
        delta_date = (today - birthday).days
        delt_years = delta_date / 365
        if delt_years < 120 and today > birthday:
            self.__value = value
        else:
            raise CustomError("Birthday shoulde be less than 120 years and not in future")
    
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.birthday = None
        self.phones = []
    
    def add_phone(self, phone):
        new_phone = Phone(value=phone)
        self.phones.append(new_phone)
    
    def edit_phone(self, old_phone, new_phone):
        for ph in self.phones:
            if ph.value == old_phone:
                ph.value = new_phone

    def remove_phone(self, phone):
        self.phones = [ph for ph in self.phones if ph.value != phone]

    def find_phone(self, phone):
        for ph in self.phones:
            if ph.value == phone:
                return ph
        return None
    
    def add_birthday(self, value):
        self.birthday = Birthday(value)
    
    def __repr__(self):
        tail = f"Birthday: {self.birthday}" if self.birthday else "" 
        return f"Contact name: {self.name.value}, Phones: {'; '.join(p.value for p in self.phones)} " + tail
    

class AddressBook(UserDict):
    
    def add_record(self, record: Record):
        self.data[record.name.value] = record
    
    def find(self, name):
        record = self.data.get(name)
        return record
    
    def delete(self, name):
        self.data.pop(name)

    def get_birthdays_per_week(self):
        contacts = defaultdict(list)
        today = datetime.datetime.today().date()
        for name, record in self.data.items():
            birthday = record.birthday
            if not birthday:
                continue
            birthday = datetime.datetime.strptime(birthday.value, '%d.%m.%Y').date()
            birthday_this_year = birthday.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            delta_days = (birthday_this_year - today).days
            if delta_days <= 7:
                birthday_weekday = (today + datetime.timedelta(days=delta_days)).strftime("%A")
                if birthday_weekday in ['Sunday','Saturday']:
                    birthday_weekday = 'Next Monday'
                contacts[birthday_weekday].append(name)
        info = ''
        tail = ''
        for k, value in contacts.items():
            if k == 'Next Monday':
                tail += f"{k}: {', '.join(value)}"
                continue
            info += f"{k}: {', '.join(value)}\n"
        info += tail 
        return info
    
    def save(self):
        file_name = "AddressBook.bin"
        with open(file_name, "wb") as fh:
            pickle.dump(self, fh)

    @classmethod    
    def load(cls):
        file_name = "AddressBook.bin"
        if os.path.exists(file_name):
            with open(file_name, "rb") as fh:
                self = pickle.load(fh)
            return self
        else:
            return AddressBook()

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone (10 symbols) please."
        except IndexError:
            return "You should write 2 values"
        except KeyError:
            return "Contact not found, please add contact."
        except CustomError as error:
            return str(error)
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    if not record:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        book.save()
        return "Contact added."
    else:
        record.add_phone(phone)
        book.save()
        return "New phone added" 

@input_error
def change_contact(args, book: AddressBook):
    name = args[0]
    old_phone = args[1]
    new_phone = args[2]
    record = book.find(name)
    if not record:
        return "Contact not found"
    record.edit_phone(old_phone, new_phone)
    book.save()
    return "Contact changed"

@input_error
def show_contact(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        return "Contact not found"
    return record

def show_all_contact(book: AddressBook):
    info = ""
    for name, record in book.data.items():
        info += f'{record}\n'
    return info

@input_error
def add_birthday(args, book: AddressBook):
    name = args[0]
    birthday = args[1]
    record = book.find(name)
    if not record:
        return f'Contact {name} not found'
    record.add_birthday(birthday)
    book.save()
    return "Birthday was added"

@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        return f'Contact {name} not found'
    birthday = record.birthday
    if not birthday:
        return f"Birthday was not added for contact {name}"
    return birthday

def show_all_birthday(book: AddressBook):
    info = ""
    for name, record in book.data.items():
        if not record.birthday:
            continue
        info += f'{name}: {record.birthday}\n'
    return info

def show_next_birthdays(book: AddressBook):
    if not book.get_birthdays_per_week():
        return "No any birthdays in near 1 week"
    else:
        return book.get_birthdays_per_week()

def main():
    book = AddressBook.load()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            print("Good bye!")
            book.save()
            break

        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))   
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_contact(args, book))
        elif command == "all":
            print(show_all_contact(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(show_all_birthday(book))
        elif command == "next-birthdays":
            print(show_next_birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()


