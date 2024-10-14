# ConsoleBotAssistant

ConsoleBotAssistant is an intelligent console assistant designed for effective management of your contacts, notes, and providing information about the weather and jokes. The project is implemented using the principles of Object-Oriented Programming (OOP) and abstract classes.

## Key Features

- **Contact Management**: 
  - Stores contacts with names, addresses, phone numbers, emails, and birthdays.
  - Displays a list of contacts with upcoming birthdays within a specified period.
  - Validates the entered phone numbers and emails.
  - Searches for and edits contacts.

- **Note Management**: 
  - Stores notes with textual information.
  - Searches and sorts notes by keywords (tags).
  - Edits and deletes notes.
  - Adds tags to notes to describe the topic and content.

- **Weather**: 
  - Retrieves current weather information for a specified location.

- **Jokes**: 
  - Provides random jokes to lighten the mood.

## Technologies

- Python 3.11+
- Libraries: rich, prompt-toolkit, questionary, termcolor, requests, googletrans
- Docker (optional)

## Installation

1. Clone the repository:

    ```git clone https://github.com/Alona7777/ConsoleBotAssistant.git```


2. Navigate to the project directory:

    ```cd ConsoleBotAssistant```


3. Install Poetry (if not already installed):

    ```pip install poetry```


4. Install the dependencies using Poetry:

    ```poetry install```


5. Activate the virtual environment:

    ```poetry shell```

6. Run the main script:

    ```python main.py```    


### Option 2: Docker Installation

If you prefer to use Docker, you can use the provided Dockerfile:

1. Clone the repository:

    ```git clone https://github.com/Alona7777/ConsoleBotAssistant.git```


2. Navigate to the project directory:

    ```cd ConsoleBotAssistant```   


3. Build the Docker image:

    ```docker build -t consolebotassistant .```   


4. Run the Docker container:

    ```docker run -it consolebotassistant
    ```

The application will start automatically when you run the Docker container.

Follow the instructions in the console interface to use the various features of the assistant.


## Project Structure


- `bot_assistant/`: Main package directory for the assistant functionality
- `tests/`: Directory for test files
- `.vscode/`: VS Code configuration directory
- `Dockerfile`: Contains instructions for building the Docker image
- `assistant.py`: Core assistant logic
- `pyproject.toml`: Project configuration and dependencies (Poetry)
- `README.md`: Project documentation and overview
- `record.py`: Likely contains record-related functionality
- `poetry.lock`: Lock file for Poetry dependencies
- `main.py`: Entry point of the application

## OOP Features

The project demonstrates the use of key OOP principles:

- **Abstraction**: Use of abstract base classes to define common interfaces for different types of assistants.
  Example: The `AssistantBot` abstract class defines a common `handler` method for all assistant types.

- **Inheritance**: Implementation of specific assistant classes based on the abstract `AssistantBot` class.
  Example: `Assistant`, `ContactAssistant`, `NotesAssistant`, and `GoodiesAssistant` classes inherit from `AssistantBot`.

- **Polymorphism**: Different implementations of the `handler` method in concrete assistant classes, allowing for uniform treatment of different assistant types.
  Example: Each assistant class (`ContactAssistant`, `NotesAssistant`, etc.) implements its own version of the `handler` method.

- **Encapsulation**: Organizing code into classes, each responsible for its own data and behavior.
  Example: The `Assistant` class encapsulates the main menu logic, while `AddressBook` encapsulates contact management functionality.

Here's a simplified example illustrating these principles based on your code structure:

```python
from abc import ABC, abstractmethod
from collections import UserDict

class AssistantBot(ABC):
    @abstractmethod
    def handler(self):
        pass

class Assistant(AssistantBot):
    def __init__(self):
        self.colors = "cyan"
        self.console = Console()

    def handler(self):
        # Main menu logic
        commands_menu = {
            "CONTACT MENU": [ContactAssistant, "yellow"],
            "NOTE": [NotesAssistant, "blue"],
            "GOODIES MENU": [GoodiesAssistant, "bold green"],
            "EXIT": [ExitAssistant, "red"],
        }
        # ... (menu display and user input handling)

class ContactAssistant(AssistantBot):
    def handler(self):
        # Contact management logic
        pass

class NotesAssistant(AssistantBot):
    def handler(self):
        # Note management logic
        pass

class AddressBook(UserDict):
    # Contact storage and management functionality
    pass

# Usage
main_assistant = Assistant()
main_assistant.handler()