from collections import UserDict
import cmd
from datetime import date, datetime, timedelta
import pickle
import re


class Field:
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def __str__(self):
        return str(self.__value)


class Name(Field):
    pass


class Address(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        self.__value = value

    def __str__(self):
        return str(self.__value)


class Email(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        pattern = r"^[a-zA-Z0-9._]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if (bool(re.search(pattern, value))) is False:
            raise ValueError("\033[91mInvalid email format.\033[0m")
        self.__value = value

    def __str__(self):
        return str(self.__value)


class Birthday(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value: str):
        try:
            self.__value = datetime.strptime(value, "%Y.%m.%d").date()
        except ValueError:
            raise ValueError(
                "\033[91mInvalid date format. Correct format: YYYY.MM.DD\033[0m"
            )

    def __str__(self):
        return self.__value.strftime("%Y.%m.%d")


class Phone(Field):
    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if len(value) != 10 or not value.isdigit():
            raise ValueError(
                "\033[91mThe phone number should be digits only and have 10 symbols.\033[0m"
            )
        self.__value = value

    def __str__(self):
        return str(self.__value)


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.email = None
        self.address = None

    def add_phone(self, value: str):
        """
        The add_phone function adds a phone number to the list of phones for a contact.


        :param self: Represent the instance of the class
        :param value: str: Specify the type of value that is being passed into the function
        :return: Nothing
        :doc-author: Trelent
        """
        phone = Phone(value)
        self.phones.append(phone)

    def add_email(self, value: str):
        """
        The add_email function adds an email to the user's profile.

        :param self: Refer to the instance of the class
        :param value: str: Specify the type of data that can be passed into the function
        :return: The email class, which is a new instance of the email class
        :doc-author: Trelent
        """
        self.email = Email(value)

    def add_address(self, value: str):
        """
        The add_address function adds an address to the user.

        :param self: Reference the object that is calling the function
        :param value: str: Pass in the address string
        :return: The address object
        :doc-author: Trelent
        """
        self.address = Address(value)

    def add_birthday(self, birthday: str):
        """
        The add_birthday function takes a string as an argument and sets the birthday attribute of the object to a Birthday object.


        :param self: Refer to the object itself
        :param birthday: str: Pass in a string that will be used to create an instance of the birthday class
        :return: Nothing
        :doc-author: Trelent
        """
        self.birthday = Birthday(birthday)

    def remove_phone(self, phone: str):
        """
        The remove_phone function removes a phone number from the list of phones for a given contact.
            Args:
                self (Contact): The Contact object to remove the phone number from.
                phone (str): The string representation of the phone number to be removed.

        :param self: Represent the instance of the class
        :param phone: str: Identify the phone number to be deleted
        :return: A string
        :doc-author: Trelent
        """
        for item in self.phones:
            if item.value == phone:
                self.phones.remove(item)
                return f"The phone number: {phone} has been deleted."
        return f"The phone number {phone} not found."

    def edit_phone(self, old_phone: str, new_phone: str):
        """
        The edit_phone function takes two arguments:
            - old_phone, a string representing the phone number to be replaced.
            - new_phone, a string representing the replacement phone number.

        :param self: Access the attributes and methods of the class
        :param old_phone: str: Find the phone number that needs to be changed
        :param new_phone: str: Pass the new phone number to the function
        :return: The string that contains all the phones of the contact,
        :doc-author: Trelent
        """
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                return f'Phones: {"; ".join(p.value for p in self.phones)}'
        return None

    def find_phone(self, phone: str):
        """
        The find_phone function takes a phone number as an argument and returns the Phone object that matches it.
        If no match is found, None is returned.

        :param self: Access the attributes and methods of a class
        :param phone: str: Specify the type of data that is being passed to the function
        :return: The phone object if the value of that object is equal to the phone passed in
        :doc-author: Trelent
        """
        for item in self.phones:
            if item.value == phone:
                return item
        return None

    def days_to_birthday(self):
        """
        The days_to_birthday function takes a birthday and returns the number of days until that person's next birthday.
        If today is their birthday, it returns &quot;Birthday today&quot;. If their last birthday was yesterday, it returns the number of days until next year's.

        :param self: Refer to the object itself
        :return: The number of days until the user's birthday
        :doc-author: Trelent
        """
        if self.birthday is None:
            return None
        date_today = date.today()
        birthday_date = self.birthday.value.replace(year=date_today.year)
        if date_today == birthday_date:
            return "Birthday today"
        if birthday_date <= date_today - timedelta(days=1):
            birthday_date = birthday_date.replace(year=date_today.year + 1)
        day_to_birthday = (birthday_date - date_today).days
        return day_to_birthday

    def __str__(self):
        return f'{self.name.value},\
            {"; ".join(p.value for p in self.phones)},\
                {self.birthday}, {self.email}, \
                    {self.address}, {self.days_to_birthday()}'


class AddressBook(UserDict):
    def __init__(self):
        super().__init__()
        self.file = "Phone_Book.bin"

    def add_record(self, record: Record):
        """
        The add_record function adds a record to the database.

        :param self: Represent the instance of the object itself
        :param record: Record: Pass the record object to the function
        :return: The record that was added
        :doc-author: Trelent
        """
        self.data[record.name.value] = record

    def find(self, name: str):
        """
        The find function is a function that takes in the name of an object and returns it if it exists.
        If the object does not exist, then None is returned.

        :param self: Represent the instance of the object itself
        :param name: str: Specify the name of the item to be found
        :return: The value of the key if it exists in the dictionary,
        :doc-author: Trelent
        """
        if name in self.data:
            return self.data[name]
        return None

    def search(self, value: str):
        """
        The search function takes a string as an argument and searches the phonebook for any records that contain the search term.
        The function returns a list of all records containing the search term.

        :param self: Represent the instance of the class
        :param value: str: Pass the value that we want to search for
        :return: A string with the result of the search
        :doc-author: Trelent
        """
        if len(value) < 3:
            return "\033[91mYou need at least 3 letters to search by name or 3 digit to search by phone number.\033[0m"
        result = ""
        for name, rec in self.data.items():
            if value.lower() in name.lower():
                result += f"{str(rec)}\n"
            for item in rec.phones:
                if value in item.value:
                    result += f"{str(rec)}"
        if len(result) != 0:
            return result
        else:
            return None

    def delete(self, name: str):
        """
        The delete function takes a name as an argument and deletes the contact from the dictionary.
        If the contact is not found, it returns a message saying so.

        :param self: Represent the instance of the class
        :param name: str: Specify the name of the contact that will be deleted
        :return: A string that says &quot;the contact {name} has been deleted
        :doc-author: Trelent
        """
        if name in self.data:
            self.data.pop(name)
            return f"The contact {name} has been deleted."
        else:
            return f"The contact {name} not found."

    def iterator(self, item_number):
        """
        The iterator function takes in a dictionary and returns an iterator that
        yields the key-value pairs of the dictionary. The function also takes in a
        parameter, item_number, which is used to determine how many items are yielded at
        a time.

        :param self: Access the data attribute of the class
        :param item_number: Determine how many items will be printed
        :return: A generator object
        :doc-author: Trelent
        """
        counter = 0
        result = "Contacts:\n"
        print(result)
        print(self.data)
        for item, record in self.data.items():
            result += f"{item}: {str(record)}\n"
            counter += 1
            print(counter)
            if counter >= item_number:
                yield result
                counter = 0
                result = ""
        print(result)
        yield result

    def write_to_file(self):
        """
        The write_to_file function takes the data from the file and writes it to a new file.
        It is used in conjunction with pickle, which allows us to write our data into a binary format.

        :param self: Represent the instance of the object itself
        :return: Nothing
        :doc-author: Trelent
        """
        with open(self.file, "wb") as file:
            pickle.dump(self.data, file)

    def read_from_file(self):
        """
        The read_from_file function reads the data from a file and returns it.


        :param self: Refer to the object itself
        :return: The data from the file
        :doc-author: Trelent
        """
        with open(self.file, "rb") as file:
            self.data = pickle.load(file)
        return self.data


class Note:
    def __init__(self, content, tags=None):
        if tags is None:
            tags = []
        self.content = content
        self.tags = tags


class Controller(cmd.Cmd):
    def exit(self):
        self.book.dump()
        return True
