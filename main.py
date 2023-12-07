import requests
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import checkboxlist_dialog
from prompt_toolkit.shortcuts import button_dialog
from prompt_toolkit.styles import Style
import requests
import os
import subprocess
import shutil



class ModuleManager:
    def __init__(self, repo_url, modules_dir=""):
        self.repo_url = repo_url
        self.modules_dir = modules_dir
        self.modules = []
        self.active_processes = {}

    def is_dependency_installed(self, dependency):
        """Check if a dependency is already installed."""
        return shutil.which(dependency) is not None

    def fetch_modules(self):
        try:
            response = requests.get(self.repo_url)
            response.raise_for_status()  # Raises HTTPError for bad requests
            files = response.json()
            self.modules = [file['name'] for file in files if file['type'] == 'file']
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error fetching modules: {e}")
            return False

    def download_module(self, module_name):
        # Fetch the JSON metadata first to get the download URL
        self.fetch_modules()
        metadata_url = f"{self.repo_url}/{module_name}"
        metadata_response = requests.get(metadata_url)
        if metadata_response.status_code == 200:
            download_url = metadata_response.json().get("download_url")
            if download_url:
                # Fetch the actual script content
                script_response = requests.get(download_url)
                if script_response.status_code == 200:
                    module_path = os.path.join(self.modules_dir, module_name)
                    with open(module_path, 'w') as file:
                        file.write(script_response.text)
                    return module_path
                else:
                    print(f"Failed to download the content of {module_name}")
            else:
                print(f"Download URL not found for {module_name}")
        else:
            print(f"Failed to fetch metadata for {module_name}")
        return None

    def parse_help_info(self, module_path):
        help_info = {}
        with open(module_path, 'r') as file:
            for line in file:
                if line.startswith('# Help:'):
                    _, info = line.split(':', 1)
                    key, desc = info.split('-', 1)
                    help_info[key.strip()] = desc.strip()
        return help_info

    def parse_follow_log_flag(self, module_path):
        with open(module_path, 'r') as file:
            for line in file:
                if line.startswith('# Follow_log:'):
                    return line.strip().split(':')[1].strip().lower() == 'true'
        return False

    def parse_dependencies(self, module_path):
        dependencies = []
        with open(module_path, 'r') as file:
            for line in file:
                if line.startswith('# Dependencies:'):
                    dependencies = line.strip().split(':')[1].split()
                    break
        return dependencies

    def parse_silent_flag(self, module_path):
        with open(module_path, 'r') as file:
            for line in file:
                if line.startswith('# Silent:'):
                    return line.strip().split(':')[1].strip().lower() == 'true'
        return False

    def parse_logfile_path(self, module_path):
        with open(module_path, 'r') as file:
            for line in file:
                if line.startswith('# Logfile:'):
                    return line.strip().split(':')[1].strip()
        return None

    def parse_inputs(self, module_path):
        inputs = []
        with open(module_path, 'r') as file:
            for line in file:
                if line.startswith('# Inputs:'):
                    inputs = line.strip().split(':')[1].split(',')
                    break
        return [input.strip() for input in inputs]

    def install_dependencies(self, dependencies):
        for dep in dependencies:
            if not self.is_dependency_installed(dep):
                print(f"Installing dependency: {dep}")
                # Modify this command to suit your OS and dependency manager
                subprocess.run(['sudo', 'apt-get', 'install', '-y', dep], check=True)
            else:
                print(f"Dependency '{dep}' is already installed.")

    def install_module(self, module_name):
        module_path = self.download_module(module_name)
        if module_path:
            dependencies = self.parse_dependencies(module_path)
            self.install_dependencies(dependencies)
            # Add any further installation logic here (like setting permissions)
            print(f"Module {module_name} installed successfully.")

    def show_and_select_modules(self):
        # Display a checkbox list dialog for module selection
        selected_modules = checkboxlist_dialog(
            title="Available Modules",
            text="Select modules to install:",
            values=[(module, module) for module in self.modules]
        ).run()

        return selected_modules

    def list_installed_modules(self):
        # List all files in the modules directory
        return [f for f in os.listdir(self.modules_dir) if os.path.isfile(os.path.join(self.modules_dir, f))]

    def launch_module(self, module_name, args):
        module_path = os.path.join(self.modules_dir, module_name)
        if os.path.exists(module_path):
            is_silent = self.parse_silent_flag(module_path)
            logfile_path = self.parse_logfile_path(module_path)

            with open(logfile_path, 'a') if is_silent and logfile_path else subprocess.DEVNULL as logfile:
                process = subprocess.Popen(["bash", module_path] + args,
                                           stdout=logfile, stderr=logfile,
                                           start_new_session=True)
            self.active_processes[module_name] = process
            print(f"Module {module_name} launched.")
            follow_log = self.parse_follow_log_flag(module_path)
            if follow_log and logfile_path:
                tmux_command = f"tmux new-window 'tail -f {logfile_path}'"
                subprocess.Popen(tmux_command, shell=True)
                print(f"Following log in new tmux window: {logfile_path}")
            if is_silent and logfile_path:
                print(f"Logging output to {logfile_path}")
            return True
        else:
            print(f"Module {module_name} not found.")
            return False

    def stop_module(self, module_name):
        process = self.active_processes.get(module_name)
        if process:
            process.terminate()
            print(f"Module {module_name} stopped.")
            del self.active_processes[module_name]
        else:
            print(f"No running module named {module_name}.")

    def remove_module(self, module_name):
        module_path = os.path.join(self.modules_dir, module_name)
        if os.path.exists(module_path):
            os.remove(module_path)
            print(f"Module {module_name} has been removed.")
            return True
        else:
            print(f"Module {module_name} not found.")
            return False



class MyApp:
    def __init__(self):
        self.session = PromptSession()
        self.module_manager = ModuleManager(
            repo_url="https://api.github.com/repos/mavedirra-01/pi-turtle/contents/modules",
            modules_dir="/opt/pi-turtle/modules"
        )
        self.commands = ["fetch", "install"]
        self.commands += ["list", "launch"]
        self.commands += ["remove", "stop", "exit"]
        self.command_completer = WordCompleter(self.commands)
        self.style = Style.from_dict({
            '': '#4caf50 bold',  # Default text color
            'output': '#34b7eb',  # Output messages
            'error': '#ff6347 bold',  # Error messages
            'prompt': '#00b0ff bold'  # Prompt messages
        })

    def print_output(self, message):
        print(f'[\x1b[34moutput\x1b[0m] {message}')

    def print_error(self, message):
        print(f'[\x1b[31merror\x1b[0m] {message}')

    def select_and_remove_module(self):
        installed_modules = self.module_manager.list_installed_modules()
        if not installed_modules:
            print("No installed modules found.")
            return

        selected_module = checkboxlist_dialog(
            title="Remove Module",
            text="Select a module to remove:",
            values=[(module, module) for module in installed_modules]
        ).run()

        if selected_module:
            module_name = selected_module[0]
            self.module_manager.remove_module(module_name)

    def select_and_stop_module(self):
        if not self.module_manager.active_processes:
            print("No active modules to stop.")
            return

        selected_module = button_dialog(
            title="Stop Module",
            text="Select a module to stop:",
            buttons=[(module, module) for module in self.module_manager.active_processes.keys()]
        ).run()

        if selected_module:
            self.module_manager.stop_module(selected_module)



    def select_and_launch_module(self):
        installed_modules = self.module_manager.list_installed_modules()
        if not installed_modules:
            print("No installed modules found.")
            return

        # Display a numbered list of installed modules
        module_menu = {str(i + 1): module for i, module in enumerate(installed_modules)}
        for key, module in module_menu.items():
            print(f"{key}: {module}")

        # User selects a module by number
        module_choice = self.session.prompt("Select a module to launch: ")
        module_name = module_menu.get(module_choice)
        if module_name:
            module_path = os.path.join(self.module_manager.modules_dir, module_name)
            inputs = self.module_manager.parse_inputs(module_path)
            help_info = self.module_manager.parse_help_info(module_path)

            args = []
            for input in inputs:
                prompt_text = f"{input}: "
                if input in help_info:
                    prompt_text += f"({help_info[input]}) "
                user_input = self.session.prompt(prompt_text)
                args.append(user_input)

            self.module_manager.launch_module(module_name, args)
        else:
            print("Invalid module selection.")


    def run(self):
        while True:
            try:
                user_input = self.session.prompt("Pi-Turtle> ", style=self.style, completer=self.command_completer)
                if user_input == "exit":
                    break
                elif user_input == "fetch":
                    self.module_manager.fetch_modules()
                    print("Modules fetched: ", self.module_manager.modules)
                elif user_input == "stop":
                    self.select_and_stop_module()
                elif user_input == "install":
                    selected_modules = self.module_manager.show_and_select_modules()
                    for module in selected_modules:
                        self.module_manager.install_module(module)
                elif user_input == "remove":
                    self.select_and_remove_module()
                elif user_input == "list":
                    installed_modules = self.module_manager.list_installed_modules()
                    print("Installed modules:", installed_modules)
                elif user_input == "launch":
                    self.select_and_launch_module()
            except KeyboardInterrupt:
                self.print_error("Ctrl+C detected! use 'exit' to quit.")
                continue
            except EOFError:
                break
            except Exception as e:
                self.print_error(f"An error occurred: {e}")



if __name__ == "__main__":
    app = MyApp()
    app.run()
