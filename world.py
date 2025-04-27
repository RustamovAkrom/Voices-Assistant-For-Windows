from core.command_manager import execute_command
from core.text_analyzer import extract_commands


commands = extract_commands("привет открой браузер запусти музыку и найти кто такой Линукс Торвальдс")

for command, args in commands:
    print(f"Command: {command}, Args: {args}")
    
    execute_command(command, args)

# print(commands)

# output = execute_command("handlers.great_handler.GreatHandler")

# print(output)