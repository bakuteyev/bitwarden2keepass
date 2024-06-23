"""Convert Bitwarden data to KeePass.

This script converts Bitwarden data to KeePass. It requires the Bitwarden CLI to be \
    installed and logged in. It also requires the PyKeePass library to be installed.

Example:
    $ python convert.py --master_password <master_password>\
        --export_path bitwarden_export.json\
        --keepass_path export.kdbx
"""

import os
import subprocess
import json
import logging
import argparse
from typing import Any, Dict
from pykeepass import create_database, PyKeePass
import pykeepass as pk
# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def parse_args():
    """Parse command line arguments.

    Returns:
        argparse.Namespace: An object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Transfer data from Bitwarden to KeePass.")
    parser.add_argument("--master_password", required=True,
                        help="Master password for Bitwarden")
    parser.add_argument("--export_path", default='bitwarden_export.json',
                        help="Bitwarden export JSON file path (default: bitwarden_export.json)")
    parser.add_argument("--keepass_path", default='export.kdbx',
                        help="KeePass database file path (default: export.kdbx)")
    return parser.parse_args()


def run_command(command: list, user_input: str = None) -> str:
    """Run a system command with subprocess.

    Args:
        command (list): The command to run as a list of strings.
        user_input (str, optional): The input to pass to the command. Defaults to None.

    Returns:
        str: The output of the command as a string.

    Raises:
        subprocess.CalledProcessError: If the command returns a non-zero exit code.
    """
    try:
        process = subprocess.run(command, capture_output=True,
                                 text=True, input=user_input, encoding='utf-8', check=True)
        return process.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error("Command failed: %s", e)
        raise


def export_bitwarden_vault(session_key: str, export_path: str):
    """Export Bitwarden vault to a JSON file.

    Args:
        session_key (str): The Bitwarden session key.
        export_path (str): The path to the exported JSON file.

    Raises:
        subprocess.CalledProcessError: If the command returns a non-zero exit code.
    """
    os.environ['BW_SESSION'] = session_key
    logging.info("Exporting Bitwarden vault...")
    run_command(['bw', 'export', '--output', export_path, '--format', 'json'])
    logging.info("Export completed successfully.")


def load_bitwarden_data(export_path: str) -> dict:
    """Load Bitwarden data from the exported file.

    Args:
        export_path (str): The path to the exported Bitwarden data file.

    Returns:
        dict: A dictionary containing the Bitwarden data.
    """
    logging.info("Loading Bitwarden data...")
    try:
        with open(export_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        logging.error("Failed to load data: %s", e)
        raise


def unlock_bitwarden(master_password: str) -> str:
    """Unlock Bitwarden vault and return session key.

    Args:
        master_password (str): The master password for the Bitwarden vault.

    Returns:
        str: The session key for the unlocked Bitwarden vault.
    """
    logging.info("Unlocking Bitwarden vault...")
    return run_command(['bw', 'unlock', master_password, '--raw'], master_password)


def find_or_create_group(kp: PyKeePass, folder_name: str):
    """Find or create a group in KeePass based on folder name.

    Args:
        kp (PyKeePass): The PyKeePass instance to search for the group in.
        folder_name (str): The name of the folder to find or create.

    Returns:
        The PyKeePass group object that was found or created.
    """
    current_group = kp.root_group
    for group_name in folder_name.split('/'):
        if group_name:
            sub_group = kp.find_groups(name=group_name, first=True) or kp.add_group(
                current_group, group_name)
            current_group = sub_group
    return current_group


def delete_exported_json(export_path: str):
    """Remove the exported JSON file for security.

    Args:
        export_path (str): The path to the exported JSON file.

    Returns:
        None
    """
    try:
        os.remove(export_path)
        logging.info("Deleted the exported JSON file.")
    except OSError as e:
        logging.error("Error deleting the exported JSON file: %s", e)


def update_or_create_entry(
    kp: PyKeePass,
    entry_group: pk.group.Group,
    item: Dict[str, Any]
) -> None:
    """
    Update or create an entry in KeePass.

    Adds fields as custom attributes and handles OTP.

    Args:
        kp (PyKeePass): The PyKeePass instance.
        entry_group (pk.group.Group): The KeePass group to add the entry to.
        item (Dict[str, Any]): The Bitwarden item to convert to a KeePass entry.

    Returns:
        None
    """
    title = item.get('name', 'No Title')
    username = item.get('login', {}).get('username', '') or ''
    password = item.get('login', {}).get('password', '') or ''
    url_list = item.get('login', {}).get('uris', [])
    url = url_list[0].get('uri', '') if url_list else ''
    notes = item.get('notes', '') or ''
    
    # Extract OTP information
    otp = item.get('login', {}).get('totp', '')

    # Check if an entry with the same title and username already exists
    existing_entry = kp.find_entries(
        title=title, username=username, group=entry_group, first=True)
    
    if existing_entry:
        # Update existing entry
        existing_entry.username = username
        existing_entry.password = password
        existing_entry.url = url
        existing_entry.notes = notes
        if otp:
            existing_entry.otp = otp
    else:
        # Create a new entry in KeePass
        kp.add_entry(
            entry_group,
            title=title,
            username=username,
            password=password,
            url=url,
            notes=notes,
            otp=otp
        )

    # Handle additional attributes
    entry = existing_entry or kp.find_entries(
        title=title, username=username, group=entry_group, first=True)
    for attribute in item.get('fields', []):
        attr_name = attribute.get('name', '')
        attr_value = attribute.get('value', '')
        is_hidden = attribute.get('type') == 1  # Assuming type 1 is hidden
        if attr_name and attr_value:
            entry.set_custom_property(
                attr_name, attr_value, protect=is_hidden)


def transfer_data_to_keepass(
        kp: PyKeePass,
        bitwarden_data: Dict[str, Any],
        folder_id_to_name: Dict[str, str]
) -> None:
    """Transfer data from Bitwarden to KeePass.

    Args:
        kp (PyKeePass): The PyKeePass instance.
        bitwarden_data (Dict[str, Any]): The Bitwarden data to transfer.
        folder_id_to_name (Dict[str, str]): A dictionary mapping folder IDs to names.

    Returns:
        None
    """
    for item in bitwarden_data['items']:
        folder_id = item.get('folderId')
        folder_path = folder_id_to_name.get(folder_id, '')
        entry_group = find_or_create_group(kp, folder_path)
        update_or_create_entry(kp, entry_group, item)


def main():
    """Main function.

    This function is the entry point of the program. It parses the command \
    line arguments, unlocks the Bitwarden vault, exports the vault data, creates \
    a KeePass database, transfers the data from Bitwarden to KeePass, saves the KeePass \
    database, and deletes the exported JSON file. If any error occurs, it logs the error message.

    Args:
        None

    Returns:
        None
    """
    args = parse_args()

    try:
        session_key = unlock_bitwarden(args.master_password)
        export_bitwarden_vault(session_key, args.export_path)
        bitwarden_data = load_bitwarden_data(args.export_path)

        kp = create_database(args.keepass_path, password=args.master_password)
        folder_id_to_name = {folder['id']: folder['name']
                             for folder in bitwarden_data['folders']}
        transfer_data_to_keepass(kp, bitwarden_data, folder_id_to_name)
        kp.save()
        logging.info("KeePass database saved successfully.")
        delete_exported_json(args.export_path)
    except subprocess.CalledProcessError:
        logging.error("Failed to process Bitwarden export.")
    except json.JSONDecodeError:
        logging.error("Failed to parse Bitwarden export file.")
    except OSError as e:
        logging.error("File operation error: %s", e)
    except Exception as e:  # pylint: disable=broad-except
        logging.error("An unexpected error occurred: %s", e)


if __name__ == "__main__":
    main()
