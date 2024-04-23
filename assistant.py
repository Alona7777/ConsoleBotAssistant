from collections import defaultdict
from datetime import date, datetime, timedelta
import pickle
import os
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from rich.table import Table
from record import Record, AddressBook, Note
from abc import ABC, abstractmethod
import questionary
from termcolor import colored
import requests
from googletrans import Translator


def input_error(func):
    """
    The input_error function is a decorator that wraps the function it's applied to.
    It catches any errors raised by the wrapped function and returns a helpful error message instead.

    :param func: Pass the function to be decorated
    :return: A function that catches errors
    :doc-author: Trelent
    """

    def inner(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except KeyError:
            return "No user with this name"
        except ValueError:
            return "Incorrect information entered"
        except IndexError:
            return "Enter user name"

    return inner


class AssistantBot(ABC):
    @abstractmethod
    def handler(self):
        pass


class Assistant(AssistantBot):
    """ main command menu """
    def __init__(self):
        super().__init__()
        self.colors = "cyan"
        self.console = Console()

    def handler(self):
        """
        The handler function is the main function of the program. It displays a menu with options for user to choose from.
        The user can choose between:
            - Contact Menu (ContactAssistant)
            - Note (NotesAssistant)
            - Goodies Menu (GoodiesAssistant)  
        
        :param self: Represent the instance of the class
        :return: A string, which is the name of the next assistant to run
        :doc-author: Trelent
        """
        commands_text = "How can I help you? Please choose:"
        commands_menu = {
            "CONTACT MENU": [ContactAssistant, "yellow"],
            "NOTE": [NotesAssistant, "blue"],
            "GOODIES MENU": [GoodiesAssistant, "bold green"],
            "EXIT": [ExitAssistant, "red"],
        }
        self.table_menu(commands_menu, commands_text)
        result = self.handler_user_input(commands_menu)
        if result in commands_menu:
            commands_menu[result][0]()
            return

    def handler_user_input(self, commands_menu):
        """
        The handler_user_input function is a function that takes in the commands_menu dictionary as an argument.
        The handler_user_input function then uses the questionary library to prompt the user with a list of options from 
        the commands menu dictionary and returns their choice.
        
        :param self: Allow an object to refer to itself inside of a method
        :param commands_menu: Display the menu options to the user
        :return: The user's choice from the commands_menu dictionary
        :doc-author: Trelent
        """
        result = questionary.select(
            "Choose an action:", choices=commands_menu.keys()
        ).ask()
        return result

    def table_menu(self, commands, commands_text):
        """
        The table_menu function is a function that takes in the self, commands, and commands_text parameters.
        The table_menu function creates a Table object with no header and cyan style. The table_menu function then adds
        a column to the Table object with bold magenta style and 50 width. The table_menu function then iterates through 
        the items in the commands dictionary parameter using an if statement to check if values[-2] is True or False. If 
        values[-2] is True, color will be assigned values[-2]. Then, another column will be added to the Table object with 
        option
        
        :param self: Access the instance of the class
        :param commands: Create the table
        :param commands_text: Display the text that is displayed above the table
        :return: A table with the commands and their respective colors
        :doc-author: Trelent
        """
        table = Table(show_header=False, style="cyan", width=150)
        table.add_column("", style="bold magenta", width=50, justify="center")
        for option, values in commands.items():
            if values[-1]:
                color = values[-1]
                table.add_column(
                    option, style=color, width=len(option) + 5, justify="center"
                )

        row_values = [f"{commands_text}"]
        row_values.extend(option for option, values in commands.items() if values[-1])
        table.add_row(*row_values)
        self.console.print(table)


class ContactAssistant(Assistant, AddressBook):
    """ menu for working with the contact book """
    def __init__(self):
        super().__init__()
        self.phone_book = AddressBook()

    def handler(self):
        """
        The handler function is the main function of the program.
        It displays a menu with options to add, edit, delete and search contacts in your phone book.
        
        
        :param self: Represent the instance of the class
        :return: The result of the handler_user_input function
        :doc-author: Trelent
        """
        if os.path.isfile(self.phone_book.file):
            self.phone_book.read_from_file()
        commands_text = "How can I help you? Please choose:"
        add_menu = AddAssistant()
        edit_menu = EditAssistant()
        delete_menu = DeleteAssistant()
        exit_menu = ExitAssistant()
        commands_menu = {
            "ADD": [add_menu.handler, "cyan"],
            "EDIT": [edit_menu.handler, "blue"],
            "DELETE": [delete_menu.handler, "red"],
            "SEARCH": [self.search, "blue"],
            "SHOW ALL": [self.show_all, "blue"],
            "RETURN TO MAIN MENU": [Assistant, ""],
            "EXIT": [exit_menu.handler, ""],
        }
        self.table_menu(commands_menu, commands_text)
        result = self.handler_user_input(commands_menu)
        if result in commands_menu:
            commands_menu[result][0]()
            return

    def table_print(self, record: Record):
        """
        The table_print function is used to print the information of a record in a table format.
        The function takes one argument, which is the record that we want to print.
        It returns a table with all the information about this record.
        
        :param self: Represent the instance of the class
        :param record: Record: Pass the record object to the function
        :return: A table
        :doc-author: Trelent
        """
        table = Table(
            title="Contact Information",
            style="cyan",
            title_style="bold magenta",
            width=100,
        )
        table.add_column("Name", style="red", justify="center")
        table.add_column("Phones", style="bold blue", justify="center")
        table.add_column("Birthday", style="bold green", justify="center")
        table.add_column("Email", style="bold blue", justify="center")
        table.add_column("Address", style="yellow", justify="center")
        table.add_column("Days to birthday", style="yellow", justify="center")
        phone_str = "\n".join(
            "; ".join(p.value for p in record.phones[i : i + 2])
            for i in range(0, len(record.phones), 2)
        )
        table.add_row(
            str(record.name.value),
            str(phone_str),
            str(record.birthday),
            str(record.email),
            str(record.address),
            str(record.days_to_birthday()),
        )
        return table

    @input_error
    def find_record(self):
        """
        The find_record function is used to find a record in the phone book.
            It takes one argument, self, and returns a record if it exists.
        
        :param self: Represent the instance of the class
        :return: A record
        :doc-author: Trelent
        """
        if os.path.isfile(self.phone_book.file):
            self.phone_book.read_from_file()
        print("=" * 150)
        completer = WordCompleter(list(self.phone_book.keys()), ignore_case=True)
        name = prompt("Enter the name of an existing contact=> ", completer=completer)
        record: Record = self.phone_book.find(name)
        if record:
            return record

    @input_error
    def save_record(self, record: Record):
        """
        The save_record function saves a record to the phone book.
            Args:
                self (PhoneBook): The PhoneBook object.
                record (Record): The Record object to be saved in the phone book.
        
        :param self: Represent the instance of the class
        :param record: Record: Pass the record object to the function
        :return: None, because it is not specified
        :doc-author: Trelent
        """
        if os.path.isfile(self.phone_book.file):
            self.phone_book.read_from_file()
        self.phone_book.add_record(record)
        self.phone_book.write_to_file()
        return

    @input_error
    def search(self):
        """
        The search function allows the user to search for a record in the phone book.
        The function takes as input at least 3 letters or numbers and returns all records that match this pattern.
        If no matches are found, an appropriate message is displayed.
        
        :param self: Represent the instance of the class
        :return: A string with all the records that match the search criteria
        :doc-author: Trelent
        """
        table = Table(
            title="Search results", style="cyan", title_style="bold magenta", width=100
        )
        table.add_column("Name", style="red", justify="center")
        table.add_column("Phones", style="bold blue", justify="center")
        table.add_column("Birthday", style="bold green", justify="center")
        table.add_column("Email", style="bold blue", justify="center")
        table.add_column("Address", style="yellow", justify="center")
        table.add_column("Days to birthday", style="yellow", justify="center")
        while True:
            print("=" * 150)
            print(
                "\033[38;2;10;235;190mEnter at least 3 letters or numbers to search or press ENTER to exit.\033[0m"
            )
            res = input("Enter your text=>  ").lower()
            if res:
                result = self.phone_book.search(res)
                if result:
                    result = result.split("\n")
                    for item in result:
                        record = item.split(",")
                        table.add_row(
                            record[0],
                            record[1],
                            record[2],
                            record[3],
                            record[4],
                            record[5],
                        )
                        self.console.print(table)
                print("\033[38;2;10;235;190mNo matches found.\033[0m")
            else:
                break

    def show_all(self):
        """
        The show_all function displays all records in the phone book.
            The function takes two arguments: self and item_number.
            If the user enters a number, then this number is assigned to item_number, 
            otherwise it is None. If there are no contacts in the phone book, 
            then an error message will be displayed on the screen that there are no contacts.
        
        :param self: Represent the instance of the class
        :return: A table with all the contacts
        :doc-author: Trelent
        """
        while True:
            table = Table(
                title="Contact Information",
                style="cyan",
                title_style="bold magenta",
                width=100,
            )
            table.add_column("Name", style="red", justify="center")
            table.add_column("Phones", style="bold blue", justify="center")
            table.add_column("Birthday", style="bold green", justify="center")
            table.add_column("Email", style="bold blue", justify="center")
            table.add_column("Address", style="yellow", justify="center")
            table.add_column("Days to birthday", style="yellow", justify="center")
            print("=" * 150)
            print(
                "\033[38;2;10;235;190mEnter how many records to display or press ENTER to skip.\033[0m"
            )
            item_number = input("Enter number=> ")
            if item_number.isdigit():
                if self.phone_book:
                    item_number = int(item_number)
                    metka = 0
                    iteration_count = 0
                    for name, record in self.phone_book.data.items():
                        phone_str = "\n".join(
                            "; ".join(p.value for p in record.phones[i : i + 2])
                            for i in range(0, len(record.phones), 2)
                        )
                        table.add_row(
                            str(record.name.value),
                            str(phone_str),
                            str(record.birthday),
                            str(record.email),
                            str(record.address),
                            str(record.days_to_birthday()),
                        )
                        iteration_count += 1
                        metka = 1
                        if iteration_count % item_number == 0:
                            self.console.print(table)
                            metka = 0
                            table = Table(
                                title="Contact Information",
                                style="cyan",
                                title_style="bold magenta",
                                width=100,
                            )
                            table.add_column("Name", style="red", justify="center")
                            table.add_column(
                                "Phones", style="bold blue", justify="center"
                            )
                            table.add_column(
                                "Birthday", style="bold green", justify="center"
                            )
                            table.add_column(
                                "Email", style="bold blue", justify="center"
                            )
                            table.add_column(
                                "Address", style="yellow", justify="center"
                            )
                            table.add_column(
                                "Days to birthday", style="yellow", justify="center"
                            )
                    if metka == 1:
                        self.console.print(table)
                    return
                else:
                    print("\033[91mNo contacts.\033[0m")
            elif item_number.isalpha():
                print(f"You entered letters: {item_number}")
            else:
                if self.phone_book:
                    for name, record in self.phone_book.data.items():
                        phone_str = "\n".join(
                            "; ".join(p.value for p in record.phones[i : i + 2])
                            for i in range(0, len(record.phones), 2)
                        )
                        table.add_row(
                            str(record.name.value),
                            str(phone_str),
                            str(record.birthday),
                            str(record.email),
                            str(record.address),
                            str(record.days_to_birthday()),
                        )
                    self.console.print(table)
                    return
                else:
                    print("\033[91mNo contacts.\033[0m")
                    return

    def exit(self):
        """
        The exit function is used to exit the program.
        It writes all changes made to the phone book file and then exits.
        
        :param self: Refer to the instance of the class
        :return: Nothing
        :doc-author: Trelent
        """
        self.phone_book.write_to_file()
        return


class AddAssistant(ContactAssistant):
    """ menu for adding information to the contact book """
    def __init__(self):
        super().__init__()

    def handler(self):
        """
        The handler function is the main function of this class. It displays a menu
        with options to add a contact, phone number, birthday, email address or an
        address. The user can also return to the main menu or exit the program.
        
        :param self: Access the instance of the class
        :return: The function that the user chooses
        :doc-author: Trelent
        """
        exit_menu = ExitAssistant()
        commands_text = "What would you like to add? Please choose:"
        commands_menu = {
            "CONTACT": [self.add_contact, "cyan"],
            "PHONE": [self.add_phone_menu, "blue"],
            "BIRTHDAY": [self.add_birthday_menu, "green"],
            "EMAIL": [self.add_email_menu, "blue"],
            "ADDRESS": [self.add_address_menu, "yellow"],
            "RETURN TO MAIN MENU": [Assistant, ""],
            "EXIT": [exit_menu.handler, ""],
        }
        self.table_menu(commands_menu, commands_text)
        result = self.handler_user_input(commands_menu)
        if result in commands_menu:
            commands_menu[result][0]()
            return

    @input_error
    def add_contact(self):
        """
        The add_contact function is used to add a new contact to the address book.
        It takes in user input for name, phone number, birthday, email and address.
        The function then saves the record and prints out a table with all of the information.
        
        :param self: Access the attributes and methods of the class
        :return: Nothing
        :doc-author: Trelent
        """
        name = input("Enter name=> ")
        record = Record(name)
        self.add_phone(record)
        self.add_birthday(record)
        self.add_email(record)
        self.add_address(record)
        self.save_record(record)
        contact = self.table_print(record)
        print("\033[92mYou have created a new contact:\033[0m")
        self.console.print(contact)
        return

    @input_error
    def add_address(self, record: Record):
        """
        The add_address function allows the user to add an address to a record.
            The function takes in a Record object and prompts the user for an address.
            If the user enters something, it adds that as an Address object to the record's addresses list attribute.
            It then saves this new information into our database file using pickle.
        
        :param self: Refer to the object itself
        :param record: Record: Pass the record object to the function
        :return: The none value
        :doc-author: Trelent
        """
        print("\033[38;2;10;235;190mEnter your address or press ENTER to skip.\033[0m")
        address = input("Enter address=> ")
        if address:
            record.add_address(address)
            self.save_record(record)
            print(f"\033[38;2;10;235;190mThe address {address} has been added.\033[0m")
            return
        else:
            return

    @input_error
    def add_address_menu(self):
        """
        The add_address_menu function is used to add an address to a contact.
        It takes in the self parameter, which is the AddressBook object that contains all of the contacts.
        The function then creates a record variable and sets it equal to whatever record was found by calling find_record().
        If no record was found, then it prints out an error message and returns nothing. If there is already an address for this contact, 
        then another error message will be printed out and nothing will be returned. Otherwise, if there isn't already an address for this contact but one was found in general (i.e., if not None), 
        
        
        :param self: Represent the instance of the class
        :return: Nothing
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found\033[0m")
                return
            elif record.address is None:
                self.add_address(record)
                self.console.print(self.table_print(record))
                return
            else:
                print("\033[91mThis contact has address.\033[0m")
                return

    def add_birthday(self, record: Record):
        """
        The add_birthday function adds a birthday to the record.
            Args:
                self (ABC): The ABC class.
                record (Record): The Record class.
        
        :param self: Refer to the object itself
        :param record: Record: Pass the record object to the function
        :return: None
        :doc-author: Trelent
        """
        while True:
            try:
                print(
                    "\033[38;2;10;235;190mEnter the date of birth or press ENTER to skip.\033[0m"
                )
                birth = input("Enter date of birth. Correct format: YYYY.MM.DD=> ")
                if birth:
                    record.add_birthday(birth)
                    self.save_record(record)
                    print(
                        f"\033[38;2;10;235;190mThe date of birth {birth} has been added.\033[0m"
                    )
                    return
                else:
                    return
            except ValueError as e:
                print(e)

    @input_error
    def add_birthday_menu(self):
        """
        The add_birthday_menu function is used to add a birthday to a contact.
        It takes the self parameter, which is an instance of the AddressBook class.
        The function then enters into a while loop that will continue until it returns or breaks out of it.
        Inside this loop, we call the find_record method on our self object and assign its return value to record variable. 
        If this return value evaluates as False (meaning no record was found), we print out an error message and break out of the loop by returning from our function.
        
        :param self: Access the attributes and methods of the class
        :return: None
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found.\033[0m")
                return
            elif record.birthday is None:
                self.add_birthday(record)
                self.console.print(self.table_print(record))
                return
            else:
                print("\033[91mThis contact has date of birth.\033[0m")
                return

    @input_error
    def add_email(self, record: Record):
        """
        The add_email function adds an email to a record.
            Args:
                self (ABC): The ABC class.
                record (Record): A Record object.
        
        :param self: Refer to the instance of the class
        :param record: Record: Pass the record object to the function
        :return: None
        :doc-author: Trelent
        """
        while True:
            try:
                print(
                    "\033[38;2;10;235;190mEnter the email or press ENTER to skip.\033[0m"
                )
                email = input("Enter email=> ")
                if email:
                    record.add_email(email)
                    self.save_record(record)
                    print(
                        f"\033[38;2;10;235;190mThe email {email} has been added.\033[0m"
                    )
                    return
                else:
                    return
            except ValueError as e:
                print(e)

    @input_error
    def add_email_menu(self):
        """
        The add_email_menu function is used to add an email address to a contact.
        It takes the user through a series of prompts, and then adds the email address
        to the contact's record.
        
        :param self: Access the attributes and methods of the class
        :return: None
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found.\033[0m")
                return
            elif record.email is None:
                self.add_email(record)
                self.console.print(self.table_print(record))
                return
            else:
                print("\033[91mThis contact has email.\033[0m")
                return

    @input_error
    def add_phone(self, record: Record):
        """
        The add_phone function adds a phone number to the record.
            Args:
                self (AddressBook): The AddressBook object.
                record (Record): The Record object.
        
        :param self: Reference the current instance of a class
        :param record: Record: Pass the record object from the main menu to this function
        :return: None
        :doc-author: Trelent
        """
        count_phone = 1
        while True:
            try:
                print(
                    f"\033[38;2;10;235;190mPlease enter the Phone Number {count_phone}, or press ENTER to skip.\033[0m"
                )
                phone = input("Enter phone=> ")
                if phone:
                    record.add_phone(phone)
                    self.save_record(record)
                    print(
                        f"\033[38;2;10;235;190mThe phone number {phone} has been added.\033[0m"
                    )
                    count_phone += 1
                else:
                    return
            except ValueError as e:
                print(e)

    @input_error
    def add_phone_menu(self):
        """
        The add_phone_menu function is a function that allows the user to add a phone number to an existing contact.
        The function first prompts the user for the name of an existing contact, and then searches through all contacts in
        the address book until it finds one with that name. If no such contact exists, it prints out an error message and returns.
        Otherwise, it calls another function called add_phone which adds a new phone number to this record's list of phones.
        
        :param self: Access the attributes and methods of the class
        :return: The record that was found
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found.\033[0m")
                return
            self.add_phone(record)
            self.console.print(self.table_print(record))
            return


class EditAssistant(ContactAssistant):
    """ menu for editing information to the contact book """
    def __init__(self):
        super().__init__()

    def handler(self):
        """
        The handler function is the main function of this module. It allows you to edit a record in your address book.
        It takes as input the name of a record and then asks you what do you want to change about it:
        name, phone number, birthday, email or address. After that it calls another handler function which will ask for new data.
        
        :param self: Access the class attributes
        :return: The class of the next menu
        :doc-author: Trelent
        """
        exit_menu = ExitAssistant()
        commands_text = "What do you want to change? Please choose:"
        commands_menu = {
            "NAME": [self.edit_name, "cyan"],
            "PHONE": [self.edit_phone, "blue"],
            "BIRTHDAY": [self.edit_birthday, "green"],
            "EMAIL": [self.edit_email, "blue"],
            "ADDRESS": [self.edit_address, "yellow"],
            "RETURN TO MAIN MENU": [Assistant, ""],
            "EXIT": [exit_menu.handler, ""],
        }
        self.table_menu(commands_menu, commands_text)
        result = self.handler_user_input(commands_menu)
        if result in commands_menu:
            commands_menu[result][0]()
            return

    @input_error
    def edit_address(self):
        """
        The edit_address function allows the user to edit an address of a contact.
        The function first finds the record that is being edited, and if it does not exist,
        it will return an error message. If it does exist, then the add_address function from AddAssistant is called on that record. 
        Then save_record saves this new information into the file and prints out what was changed.
        
        :param self: Access the attributes and methods of the class
        :return: A record
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found.\033[0m")
                return
            AddAssistant.add_address(record)
            self.save_record(record)
            print("\033[38;2;10;235;190mYou changed the contact:\n\033[0m")
            self.console.print(self.table_print(record))
            return

    @input_error
    def edit_birthday(self):
        """
        The edit_birthday function allows the user to edit a contact's birthday.
        The function first finds the record of the contact whose birthday is being edited, and then calls on AddAssistant.add_birthday() to change it.
        
        :param self: Access the attributes and methods of a class
        :return: None
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found.\033[0m")
                return
            self.console.print(self.table_print(record))
            AddAssistant.add_birthday(record)
            self.save_record(record)
            print("\033[38;2;10;235;190mYou changed the contact:\n\033[0m")
            self.console.print(self.table_print(record))
            return

    @input_error
    def edit_email(self):
        """
        The edit_email function allows the user to edit an email address of a contact.
        The function first finds the record that is being edited, and if it does not exist,
        it will return an error message. If it does exist, then the add_email function from AddAssistant 
        is called to allow for editing of emails. The save_record function is then called to save any changes made.
        
        :param self: Access the attributes and methods of the class
        :return: The edited record
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found.\033[0m")
                return
            AddAssistant.add_email(record)
            self.save_record(record)
            print("\033[38;2;10;235;190mYou changed the contact:\n\033[0m")
            self.console.print(self.table_print(record))
            return

    @input_error
    def edit_name(self):
        """
        The edit_name function allows the user to change the name of a contact.
            The function first prompts for a record, and if it is found, asks for new name.
            If there is no input from the user, then nothing happens and we return to main menu.
            Otherwise, we pop out old_name from phone_book data dictionary and add new_name as key with same value as old one had. 
        
        
        :param self: Refer to the object itself
        :return: None
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found.\033[0m")
                return
            new_name = input("Enter new name=> ")
            if new_name:
                old_name = record.name.value
                self.phone_book.data[new_name] = self.phone_book.data.pop(old_name)
                record.name.value = new_name
                self.save_record(record)
                print(
                    f"\033[38;2;10;235;190mName changed successfully from  {old_name} to {new_name}.\n\033[0m"
                )
                self.console.print(self.table_print(record))
                return
            else:
                return

    @input_error
    def edit_phone(self):
        """
        The edit_phone function allows the user to edit a phone number in an existing contact.
        The function first prompts the user for a name, and then searches through all contacts with that name.
        If no such contact exists, it prints an error message and returns None. If there is only one such contact, 
        it asks for the old phone number (the one to be changed) and then asks for the new phone number (the replacement). 
        It then calls record's edit_phone method on these two numbers; if this method returns None, it means that there was no match found between old_phone and any of record's phones;
        
        :param self: Represent the instance of the class
        :return: The edited record
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found.\033[0m")
                return
            self.console.print(self.table_print(record))
            old_phone = input("Enter the phone number you want to change=> ")
            new_phone = input("Enter the new phone number=> ")
            result = record.edit_phone(old_phone, new_phone)
            if result is None:
                print(f"\033[91mPhone: {old_phone} not found!\033[0m")
                return
            self.save_record(record)
            print("\033[38;2;10;235;190mYou changed the contact:\n\033[0m")
            self.console.print(self.table_print(record))
            return


class DeleteAssistant(ContactAssistant):
    """ menu for deleting information to the contact book """
    def __init__(self):
        super().__init__()

    def handler(self):
        """
        The handler function is the main function of this class. It displays a menu with options to delete contact, phone, birthday, email or address.
        It also has an option to return to the main menu and exit.
        
        :param self: Access the instance of the class
        :return: The name of the function that will be called
        :doc-author: Trelent
        """
        exit_menu = ExitAssistant()
        commands_text = "What do you want to delete? Please choose:"
        commands_menu = {
            "CONTACT": [self.delete_contact, "cyan"],
            "PHONE": [self.delete_phone, "blue"],
            "BIRTHDAY": [self.delete_birthday, "green"],
            "EMAIL": [self.delete_email, "blue"],
            "ADDRESS": [self.delete_address, "yellow"],
            "RETURN TO MAIN MENU": [Assistant, ""],
            "EXIT": [exit_menu.handler, ""],
        }
        self.table_menu(commands_menu, commands_text)
        result = self.handler_user_input(commands_menu)
        if result in commands_menu:
            commands_menu[result][0]()
            return

    @input_error
    def delete_address(self):
        """
        The delete_address function is used to remove the address of a contact.
        It takes in an argument self, which refers to the class AddressBook.
        The function then uses a while loop that will continue until it is broken out of by returning from the function. 
        Inside this while loop, we call on another function called find_record(), which returns either None or a record object (a contact). 
        If no record was found, we print out an error message and return from this delete_address() function. If there was indeed a record found, 
        we set its address attribute equal to None and save it using our save_
        
        :param self: Access the instance of the class
        :return: None
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found.\033[0m")
                return
            record.address = None
            self.save_record(record)
            print("\033[38;2;10;235;190mThe address was removed.\033[0m")
            self.console.print(self.table_print(record))
            return

    @input_error
    def delete_birthday(self):
        """
        The delete_birthday function is used to delete the birthday of a contact.
        It takes in an argument self, which is the address book object itself.
        The function then asks for a record to be found and if it exists, sets its birthday attribute to None.
        
        :param self: Access the attributes and methods of the class
        :return: The record with the deleted birthday
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found.\033[0m")
                return
            record.birthday = None
            self.save_record(record)
            print("\033[38;2;10;235;190mThe date of birth was removed.\033[0m")
            self.console.print(self.table_print(record))
            return

    @input_error
    def delete_contact(self):
        """
        The delete_contact function is used to delete a contact from the phone book.
        The function first asks for the name of the contact that you want to delete, and then it will ask if you really want to delete this contact. If yes, then it will be deleted.
        
        :param self: Represent the instance of the class
        :return: A boolean value
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found.\033[0m")
                return
            self.console.print(self.table_print(record))
            print(
                "\033[91mDo you really want to delete this contact? Please enter the number: 1.YES or press ENTER to skip.\033[0m"
            )
            res = input("Enter your text=>  ").lower()
            if res in ("1", "yes"):
                self.phone_book.delete(record.name.value)
                print(
                    f"\033[38;2;10;235;190mThe contact {record.name.value} was removed.\033[0m"
                )
                self.phone_book.write_to_file()
                return
            else:
                return

    @input_error
    def delete_email(self):
        """
        The delete_email function is used to delete the email of a contact.
        It takes in an argument self, which is the instance of AddressBook class.
        The function first finds a record using find_record() method and if it does not exist, it prints out that the contact was not found and returns nothing. 
        If it exists, then we set its email attribute to None (which means no value) and save this change using save_record() method. 
        Then we print out that the email was removed successfully along with printing out all information about this record.
        
        :param self: Access the attributes and methods of the class
        :return: The email of the contact
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found.\033[0m")
                return
            record.email = None
            self.save_record(record)
            print("\033[38;2;10;235;190mThe email was removed.\033[0m")
            self.console.print(self.table_print(record))
            return

    @input_error
    def delete_phone(self):
        """
        The delete_phone function allows the user to delete a phone number from an existing contact.
        The function first prompts the user for a name, and then searches through all contacts in the address book
        for that name. If no contact is found, it prints an error message and returns to main menu. Otherwise, it prints out 
        the information of that contact (using table_print) and asks for which phone number they would like to delete. 
        If there are multiple numbers associated with this person's record, they will be printed out as well so that 
        the user can choose which one they want deleted.
        
        :param self: Represent the instance of the class
        :return: The record that was deleted
        :doc-author: Trelent
        """
        while True:
            record = self.find_record()
            if not record:
                print("\033[91mThe contact was not found.\033[0m")
                return
            self.console.print(self.table_print(record))
            phone = input("Enter phone=> ")
            record.remove_phone(phone)
            print(f"\033[38;2;10;235;190mThe phone number {phone} was removed.\033[0m")
            self.save_record(record)
            print("\033[38;2;10;235;190mYou changed the contact:\n.\033[0m")
            self.console.print(self.table_print(record))
            return


class BirthAssistant(ContactAssistant):
    """ menu for working with birthdays in the contact book """
    def __init__(self):
        super().__init__()

    def handler(self):
        """
        The handler function is the entry point for your skill. It takes in a
        `request_obj`, which contains the request body, and returns a response body,
        which can be either `str` or `dict`.
        
        :param self: Represent the instance of the class
        :return: The menu object that you need to display
        :doc-author: Trelent
        """
        if os.path.isfile(self.phone_book.file):
            self.phone_book.read_from_file()
        exit_menu = ExitAssistant()
        commands_text = "How can I help you? Please choose:"
        commands_menu = {
            "FOR THIS DAY": [self.birthdays_for_date_menu, "blue"],
            "THIS WEEK": [self.get_birthdays_per_week_menu, "blue"],
            "FOR A FEW DAYS": [self.birthday_in_given_days_menu, "blue"],
            "RETURN TO MAIN MENU": [Assistant, ""],
            "EXIT": [exit_menu.handler, ""],
        }
        self.table_menu(commands_menu, commands_text)
        result = self.handler_user_input(commands_menu)
        if result in commands_menu:
            commands_menu[result][0]()
            return

    def birthdays_for_date(self, day):
        """
        The birthdays_for_date function takes a date as an argument and returns the names of all contacts whose birthdays are on that day.
        The function is called by the birthday_reminder function, which prints out a list of all contacts who have birthdays today.
        
        :param self: Represent the instance of the class
        :param day: Get the date of birthdays for that day
        :return: A list of names whose birthdays are on the given date
        :doc-author: Trelent
        """
        date = datetime.strptime(day, "%Y.%m.%d").date()
        date_today = date.today()
        contact_birth = []
        for n, rec in self.phone_book.data.items():
            name = n
            if rec.birthday:
                birth = rec.birthday.value.replace(year=date_today.year)
                if birth == date:
                    contact_birth.append(name)
        if len(contact_birth) == 0:
            print("\033[38;2;10;235;190mNo Birthday this day.\033[0m")
            return None
        return contact_birth

    def birthdays_for_date_menu(self):
        """
        The birthdays_for_date_menu function is used to display the birthdays of all contacts in the phone book.
        The function takes a parameter self, which is an instance of PhoneBook class.
        If there are no contacts in the phone book, then a message about this will be displayed on the screen.
        Otherwise, if there are any contacts with birthdays today or tomorrow (depending on what day it is), 
        then they will be displayed using Table.
        
        :param self: Represent the instance of the class
        :return: A table with the names of people whose birthday is today
        :doc-author: Trelent
        """
        table = Table(
            title="Birthdays information",
            style="cyan",
            title_style="bold magenta",
            width=100,
        )
        table.add_column("Name", style="red", justify="center")
        today_data = datetime.today().date()
        today_data_str = today_data.strftime("%Y.%m.%d")
        if not self.phone_book:
            print("\033[91mNo contacts.\033[0m")
            return
        else:
            birth = self.birthdays_for_date(today_data_str)
            if birth:
                s = ""
                for el in birth:
                    s += "| " + el + " |"
                table.add_row(s)
                self.console.print(table)

    def get_birthdays_per_week(self):
        """
        The get_birthdays_per_week function takes the phone_book.data dictionary and iterates through it,
            checking if there is a birthday value for each record in the dictionary. If there is a birthday value,
            then that name and birthdate are added to the list of birthdays per week. The function then checks if 
            any of those dates fall within 7 days from today's date (including today). If they do, they are added to 
            another list called users which contains all of the names with their corresponding day of week as keys.
        
        :param self: Represent the instance of the class
        :return: A dictionary with the days of the week as keys and a list of names and birthdays as values
        :doc-author: Trelent
        """
        date_today = date.today()
        birthday_per_week = []
        for n, rec in self.phone_book.data.items():
            if rec.birthday:
                name = f"{n}: {rec.birthday.value}"
                birth = rec.birthday.value.replace(year=date_today.year)
                if birth < date_today - timedelta(days=1):
                    birth = birth.replace(year=date_today.year + 1)
                day_week = birth.isoweekday()
                end_date = date_today + timedelta(days=7)
                if date_today <= birth <= end_date:
                    birthday_per_week.append([name, birth, day_week])
        if len(birthday_per_week) == 0:
            print("\033[38;2;10;235;190mNo Birthday this week.\033[0m")
            return None
        users = defaultdict(list)
        for item in birthday_per_week:
            if item[2] == 1:
                users["Monday"].append(item[0])
            if item[2] == 2:
                users["Tuesday"].append(item[0])
            if item[2] == 3:
                users["Wednesday"].append(item[0])
            if item[2] == 4:
                users["Thursday"].append(item[0])
            if item[2] == 5:
                users["Friday"].append(item[0])
            if item[2] == 6:
                users["Saturday"].append(item[0])
            if item[2] == 7:
                users["Sunday"].append(item[0])
        return {key: value for key, value in users.items() if value}

    def get_birthdays_per_week_menu(self):
        """
        The get_birthdays_per_week_menu function prints a table with the birthdays of all contacts in the phone book.
        The function takes no arguments and returns nothing.
        
        :param self: Represent the instance of the class
        :return: The table with the information about birthdays per week
        :doc-author: Trelent
        """
        table = Table(
            title="Birthdays information",
            style="cyan",
            title_style="bold magenta",
            width=100,
        )
        table.add_column("Date of birth", style="bold green", justify="center")
        table.add_column("Day of the week", style="red", justify="center")
        table.add_column("Names", style="bold blue", justify="center")
        if not self.phone_book:
            print("\033[91mNo contacts.\033[0m")
            return
        birthdays = self.get_birthdays_per_week()
        if birthdays:
            for k, v in birthdays.items():
                v_1 = ", ".join(p for p in v)
                table.add_row(k, v_1)
            self.console.print(table)

    def birthday_in_given_days(self, value):
        """
        The birthday_in_given_days function takes a value as an argument and returns a list of contacts whose birthday is within the given number of days.
        The function first creates two variables, date_today and date_value. The variable date_today is assigned to today's date using the datetime module's .date() method.
        The variable data_value is assigned to today's day plus the value passed in as an argument (the number of days). Next, we create an empty list called contact_birth which will be used later on in this function to store all contacts whose birthday falls within the given period. We then iterate through each record in our
        
        :param self: Access the attributes and methods of a class
        :param value: Determine the number of days in which we want to find birthdays
        :return: A list of strings
        :doc-author: Trelent
        """
        date_today = date.today()
        date_value = date_today + timedelta(days=value)
        contact_birth = []
        for n, rec in self.phone_book.data.items():
            name = n
            if rec.birthday:
                birth = rec.birthday.value.replace(year=date_today.year)
                if birth < date_today - timedelta(days=1):
                    birth = birth.replace(year=date_today.year + 1)
                if date_today <= birth <= date_value:
                    contact_birth.append(
                        f"{name}; {rec.birthday.value}; {rec.days_to_birthday()}"
                    )

        if len(contact_birth) == 0:
            print(
                "\033[38;2;10;235;190mNo Birthday during this period.\033[0m"
            )
            return None
        return contact_birth

    def birthday_in_given_days_menu(self):
        """
        The birthday_in_given_days_menu function displays a list of contacts whose birthday is in the specified number of days.
        The function takes one argument: self, which is an instance of the PhoneBook class.
        The function returns nothing.
        
        :param self: Access the attributes and methods of a class
        :return: The list of contacts whose birthday is in the specified number of days
        :doc-author: Trelent
        """
        table = Table(
            title="Birthdays information",
            style="cyan",
            title_style="bold magenta",
            width=100,
        )
        table.add_column("Name", style="red", justify="center")
        table.add_column("Date of birth", style="bold blue", justify="center")
        table.add_column("Days to birthday", style="bold blue", justify="center")
        if not self.phone_book:
            print("\033[91mNo contacts.\033[0m")
            return
        while True:
            print(
                "\033[38;2;10;235;190mEnter the required number of days (no more than one year) or press ENTER to skip.\033[0m"
            )
            item_number = input("\033[38;2;10;235;190mEnter the number=> \033[0m")
            if item_number:
                if item_number.isdigit() and int(item_number) < 365:
                    item_number = int(item_number)
                    days_birth = self.birthday_in_given_days(item_number)
                    if days_birth:
                        for elem in days_birth:
                            item = elem.split(";")
                            table.add_row(item[0], item[1], item[2])
                        self.console.print(table)
                        return
                elif item_number.isalpha():
                    print(f"\033[91mYou entered letters: {item_number}\033[0m")
                else:
                    print(
                        f"\033[91mYou entered a number greater than one year: {item_number}\033[0m"
                    )
            return


class NotesAssistant(Assistant):
    """ menu for working with notes """
    def __init__(self):
        super().__init__()
        self.colors = "cyan"
        self.notes = []
        self.file = "Save_Notes.bin"

    def handler(self):
        """
        The handler function is the main function of this module.
        It will be called by the main menu and it will show a list of options to choose from.
        The user can select one option and then he/she will be redirected to another menu or function.
        
        :param self: Represent the instance of the class
        :return: The function that will be executed
        :doc-author: Trelent
        """
        if os.path.isfile(self.file):
            self.note_read_from_file()
        exit_menu = ExitAssistant()
        commands_text = "How can I assist you? Please select an option:"
        commands_menu = {
            "ADD NOTE": [self.note_add_menu, "cyan"],
            "EDIT NOTE": [self.note_charge_menu, "blue"],
            "DELETE NOTE": [self.note_delete_menu, "red"],
            "SEARCH NOTE": [self.note_search_menu, "blue"],
            "SHOW ALL NOTE": [self.note_show_menu, "blue"],
            "RETURN TO MAIN MENU": [Assistant, ""],
            "EXIT": [exit_menu.handler, ""],
        }
        self.table_menu(commands_menu, commands_text)
        result = self.handler_user_input(commands_menu)
        if result in commands_menu:
            commands_menu[result][0]()
            return

    def table_print_note(self):
        """
        The table_print_note function is a function that prints the content and tags of a note.
        The table_print_note function takes in one parameter, self. The self parameter represents the object itself.
        
        :param self: Represent the instance of the class
        :return: A table with the note's content and tags
        :doc-author: Trelent
        """
        table = Table(
            title="Note Information",
            style="cyan",
            title_style="bold magenta",
            width=100,
        )
        table.add_column("Content", style="bold green", justify="center")
        table.add_column("Tags", style="bold blue", justify="center")
        table.add_row(
            str(self.notes.content),
            str(self.note.tags),
        )
        return table

    def add_note(self, content, tags=None):
        """
        The add_note function adds a note to the address book.
        
        :param self: Access the instance of the class
        :param content: Store the content of the note
        :param tags: Set a default value for the tags parameter
        :return: None
        :doc-author: Trelent
        """
        if tags is None:
            tags = []
        note = Note(content, tags)
        self.notes.append(note)

    def note_add_menu(self):
        """
        The note_add_menu function allows the user to add a note to their address book.
        The function takes in two arguments: self and content. The first argument, self, is the instance of AddressBook that is being used by the user. The second argument, content, is a string that contains all of the text for this particular note.
        
        :param self: Access the attributes and methods of the class in python
        :return: None
        :doc-author: Trelent
        """
        content = input("Enter your text for the note: ")
        tags = input(
            "Enter tags separated by commas (or press Enter if no tags): "
        ).split(",")
        self.add_note(content, tags)
        self.note_write_to_file()

    def search_notes_by_tag(self, tag):
        """
        The search_notes_by_tag function takes a tag as an argument and returns all notes that have the given tag.
        
        :param self: Refer to the object itself
        :param tag: Search for notes that have a specific tag
        :return: A list of notes that contain the tag
        :doc-author: Trelent
        """
        return [note for note in self.notes if tag in note.tags]

    def display_all_notes(self):
        """
        The display_all_notes function displays all the notes in a table format.
            The function takes one argument, self, which is an instance of the Notebook class.
            The function first creates a Table object with title &quot;Note Information&quot;, style &quot;cyan&quot;, title_style &quot;bold magenta&quot; and width 100. 
            It then adds two columns to this table: Content and Tags with styles bold blue and justify center for both columns. 
            If there are no notes in the notebook (self), it prints out that list empty using escape sequences to make it red text on white background (\033[91mList empty\
        
        :param self: Refer to the object itself
        :return: A table of all notes in the list
        :doc-author: Trelent
        """
        table = Table(
            title="Note Information",
            style="cyan",
            title_style="bold magenta",
            width=100,
        )
        table.add_column("Content", style="bold blue", justify="center")
        table.add_column("Tags", style="bold blue", justify="center")
        if not self.notes:
            print("\033[91mList empty.\033[0m")
        else:
            for i, note in enumerate(self.notes, 1):
                table.add_row(str(note.content), str(note.tags))
            self.console.print(table)

    def edit_note_content(self, tag, new_content):
        """
        The edit_note_content function allows the user to edit a note's content.
            The function takes in two parameters: self and tag.
            It then iterates through all of the notes in the address book, checking if each note has a tag that matches with what was inputted by the user. If it does not match, an error message is printed out saying that it is invalid. If there is a match, then we update its content to whatever was inputted by the user.
        
        :param self: Represent the instance of the class
        :param tag: Identify the note that needs to be edited
        :param new_content: Update the content of a note
        :return: A string
        :doc-author: Trelent
        """
        for note in self.notes:
            if tag not in note.tags:
                print("\033[91mInvalid note index.\033[0m")
            if tag in note.tags:
                note.content = new_content
                print("\033[92mNote update successfully.\033[0m")

    def search_and_sort_notes(self, keyword):
        """
        The search_and_sort_notes function takes a keyword as an argument and searches through the notes in the address book for that keyword.
        It then returns a list of all notes containing that keyword, sorted by tag.
        
        :param self: Access the attributes and methods of the class
        :param keyword: Search for notes that contain the keyword in their tags
        :return: A list of notes that match the keyword
        :doc-author: Trelent
        """
        found_notes = [note for note in self.notes if keyword in note.tags]
        sorted_notes = sorted(found_notes, key=lambda x: x.tags)
        return sorted_notes

    def delete_note_by_index(self, tag):
        """
        The delete_note_by_index function takes in a tag and deletes the note with that tag.
        If no such note exists, it prints an error message.
        
        :param self: Refer to the object itself
        :param tag: Identify the note to be deleted
        :return: A string
        :doc-author: Trelent
        """
        initial_len = len(self.notes)
        self.notes = [note for note in self.notes if tag not in note.tags]
        if len(self.notes) == initial_len:
            print(f'\033[91mNo note found with tag "{tag}".\033[0m')
        else:
            print(f'\033[92mNote with tag "{tag}" deleted successfully.\033[0m')

    def note_charge_menu(self):
        """
        The note_charge_menu function allows the user to edit a note's content.
        The function takes in two arguments: self and index. The first argument, self, is an instance of the Note class that contains all of the attributes and methods for a note object. The second argument, index, is an integer that represents which note in the list of notes will be edited.
        
        :param self: Reference the object that is calling the function
        :return: None
        :doc-author: Trelent
        """
        index = input("Enter tag of the note to edit: ")
        new_content = input("Enter new text for the note: ")
        self.edit_note_content(index, new_content)
        self.note_write_to_file()

    def note_delete_menu(self):
        """
        The note_delete_menu function is a function that allows the user to delete notes from their address book.
        The user enters the tag of the note they wish to delete, and then it is deleted.
        
        :param self: Represent the instance of the class
        :return: The note_write_to_file function which writes the notes to a file
        :doc-author: Trelent
        """
        index = input("Enter tag of the note to delete: ")
        self.delete_note_by_index(index)
        self.note_write_to_file()

    def note_search_menu(self):
        """
        The note_search_menu function is a function that allows the user to search for notes by tag.
        The user will be prompted to enter a tag, and then the program will search through all of the notes in 
        the address book and return any note with that tag. The returned notes are sorted by date created.
        
        :param self: Access the instance attributes and methods of a class
        :return: A table of notes that match the tag
        :doc-author: Trelent
        """
        table = Table(
            title="Note Information",
            style="cyan",
            title_style="bold magenta",
            width=100,
        )
        table.add_column("Content", style="bold blue", justify="center")
        table.add_column("Tags", style="bold blue", justify="center")
        tag_to_search = input("Enter tag for search and sort: ")
        sorted_notes = self.search_and_sort_notes(tag_to_search)
        if sorted_notes:
            print(
                f'\033[92mFound and Sorted Notes with Tag "{tag_to_search}":\033[0m'
            )
            for note in sorted_notes:
                table.add_row(str(note.content), str(note.tags))
            self.console.print(table)
        else:
            print("\033[91mNothing to sort!\033[0m")

    def note_show_menu(self):
        """
        The note_show_menu function displays all the notes in the address book.
        
        
        :param self: Refer to the current instance of a class
        :return: The value of the display_all_notes function
        :doc-author: Trelent
        """
        self.display_all_notes()

    def note_write_to_file(self):
        """
        The note_write_to_file function writes the notes to a file.
            
        
        :param self: Represent the instance of the class
        :return: Nothing
        :doc-author: Trelent
        """
        with open(self.file, "wb") as file:
            pickle.dump(self.notes, file)

    def note_read_from_file(self):
        """
        The note_read_from_file function reads the notes from a file and returns them.
            
        
        :param self: Represent the instance of the class
        :return: The notes that were read from the file
        :doc-author: Trelent
        """
        with open(self.file, "rb") as file:
            self.notes = pickle.load(file)
        return self.notes

    def exit(self):
        """
        The exit function is used to exit the program.
        It writes all notes to a file and then exits.
        
        :param self: Represent the instance of the class
        :return: True
        :doc-author: Trelent
        """
        self.note_write_to_file()
        return True


class GoodiesAssistant(Assistant):
    """ menu for working with additional goodies """
    def __init__(self):
        super().__init__()

    def handler(self):
        """
        The handler function is the main function of this module.
        It takes no arguments and returns nothing.
        The handler function will print a menu to the console, then prompt for user input.
        If the user enters an invalid command, it will re-prompt until valid input is received.
        
        :param self: Refer to the current instance of a class
        :return: The assistant class
        :doc-author: Trelent
        """
        anecdote_menu = AnecdotesAssistant()
        birth_menu = BirthAssistant()
        exit_menu = ExitAssistant()
        commands_text = "How can I assist you? Please select an option:"
        commands_menu = {
            "WEATHER": [self.weather_menu, "blue"],
            "ANECDOTES": [anecdote_menu.handler, "blue"],
            "BIRTH MENU": [birth_menu.handler, "bold green"],
            "RETURN TO MAIN MENU": [Assistant, ""],
            "EXIT": [exit_menu.handler, ""],
        }
        self.table_menu(commands_menu, commands_text)
        result = self.handler_user_input(commands_menu)
        if result in commands_menu:
            commands_menu[result][0]()
            return

    def get_weather(self, api_key, city):
        """
        The get_weather function takes in two arguments: an API key and a city.
        It then uses the requests library to make a GET request to the OpenWeatherMap API,
        which returns weather data for that city. The function parses this data and prints it out.
        
        :param self: Refer to the class itself
        :param api_key: Access the api
        :param city: Get the weather of a specific city
        :return: The temperature and description of the weather
        :doc-author: Trelent
        """
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"q": city, "appid": api_key, "units": "metric"}

        response = requests.get(url, params=params)

        if response.status_code == 200:
            weather_data = response.json()
            temperature = weather_data["main"]["temp"]
            description = weather_data["weather"][0]["description"]
            print(
                f"\033[38;2;10;235;190mThe weather in {city}: \
                {temperature}°C, {description}\033[0m"
            )
        else:
            print(
                f"\033[91mFailed to get weather. Code status: \
                {response.status_code}\033[0m"
            )

    def weather_menu(self):
        """
        The weather_menu function is a function that allows the user to input their city in English and then it will display the weather for that city.
        
        
        :param self: Access the class attributes and methods
        :return: The get_weather function with the parameters api_key and city
        :doc-author: Trelent
        """
        api_key = "43a8f3599db25559dcfc8b220a2adb8d"
        city = input("Please enter your city in English: ")
        self.get_weather(api_key, city)


class AnecdotesAssistant(Assistant):
    """ anecdotes menu """
    def __init__(self):
        super().__init__()

    def handler(self):
        """
        The handler function is the main function of the Assistant class.
        It displays a menu with options for user to choose from, and then calls
        the appropriate method based on user's choice.
        
        :param self: Represent the instance of the class
        :return: The main menu
        :doc-author: Trelent
        """
        exit_menu = ExitAssistant()
        commands_text = "How can I assist you? Please select an option:"
        commands_menu = {
            "Українською мовою": [self.anecdotes_ua_menu, 6, 1, "blue"],
            "English language": [self.anecdotes_en_menu, 6, 1, "yellow"],
            "RETURN TO MAIN MENU": [Assistant, ""],
            "EXIT": [exit_menu.handler, ""],
        }
        self.table_menu(commands_menu, commands_text)
        result = self.handler_user_input(commands_menu)
        if result in commands_menu:
            commands_menu[result][0]()
            return

    def get_joke(self):
        """
        The get_joke function takes in a string and returns the joke associated with that string.
            The function uses the requests library to make an API call to https://api.chucknorris.io/jokes/random, which is a free API for getting random Chuck Norris jokes.
        
        :param self: Represent the instance of the class
        :return: A joke from the chuck norris api
        :doc-author: Trelent
        """
        url = "https://api.chucknorris.io/jokes/random"
        response = requests.get(url)
        joke_data = response.json()
        return joke_data["value"]

    def translate_to_ukrainian(self, text):
        """
        The translate_to_ukrainian function takes a string as an argument and returns the translation of that string into Ukrainian.
        The function uses the Translator class from googletrans library to translate text.
        
        :param self: Represent the instance of the class
        :param text: Pass the text to be translated into the function
        :return: A translation of the text into ukrainian
        :doc-author: Trelent
        """
        translator = Translator()
        translation = translator.translate(text, dest="uk")
        return translation.text

    def anecdotes_ua_menu(self):
        """
        The anecdotes_ua_menu function is a method of the ABC class. It prints out a joke in Ukrainian,
        translated from English using the translate_to_ukrainian function.
        
        :param self: Refer to the current class instance
        :return: A joke in ukrainian
        :doc-author: Trelent
        """
        joke = self.get_joke()
        translated_joke = self.translate_to_ukrainian(joke)
        print(f"\033[38;2;10;235;190m{translated_joke}\033[0m")

    def anecdotes_en_menu(self):
        """
        The anecdotes_en_menu function is a function that prints out a joke in English.
        It uses the get_joke() method from the Jokes class to retrieve an English joke, and then it prints it out.
        
        :param self: Access the attributes and methods of a class
        :return: A joke
        :doc-author: Trelent
        """
        joke = self.get_joke()
        print(f"\033[38;2;10;235;190m{joke}\033[0m")


class ExitAssistant(Assistant):
    """ exit menu """
    def __init__(self):
        super().__init__()

    def handler(self):
        """
        The handler function is a function that will be called when the user
        presses Ctrl-C. It can be used to clean up resources, or stop background
        threads, or just generally end the program in an orderly fashion.
        
        :param self: Represent the instance of the class
        :return: A function that will be called
        :doc-author: Trelent
        """
        ContactAssistant.exit
        NotesAssistant.exit
        print(colored("Good bye!", self.colors))
        exit()


if __name__ == "__main__":
    pass
