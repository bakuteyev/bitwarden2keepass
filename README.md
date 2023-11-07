# bitwarden2keepass

## Overview
Developed by me, Anton Bakuteev, `bitwarden2keepass` is a Python package tailored for securely migrating and backing up password data from Bitwarden to KeePass. This tool is ideal for users who are transitioning between these password managers or need a dependable solution for backing up their Bitwarden vaults.

Compared to other packages, this one copies all custom attributes and maintains the folder structure.

Explore my other projects, including AI/ML applications, websites, and Telegram bots, at [sometechnologies.com](https://sometechnologies.com).

## Key Features
- **Command-Line Interface**: Designed for simplicity, facilitating effortless data migration and backup.
- **Migration and Backup**: Efficiently transfers data from Bitwarden to KeePass, while also providing a backup solution for Bitwarden data.
- **Secure Data Handling**: Prioritizes the safety and privacy of your data throughout the migration and backup process.
- **Customizable Paths**: Allows flexibility for users to specify file paths and other parameters.

## Requirements
- Python 3.9 or later.
- Bitwarden CLI installed and configured on your machine.

## Installation
Install `bitwarden2keepass` using pip:
```bash
pip install git+https://github.com/bakuteyev/bitwarden2keepass
```

## Usage
After installation, run the package using:
```bash
bitwarden2keepass --master_password <Your_Bitwarden_Master_Password>
```
Replace `<Your_Bitwarden_Master_Password>` with your actual Bitwarden master password.

## How It Works
1. **Unlock Bitwarden Vault**: Uses your master password to unlock the Bitwarden vault.
2. **Export and Convert Data**: Exports data from Bitwarden and converts it into KeePass format.
3. **Create Backups**: Optionally creates backups of the Bitwarden vault.
4. **Ensures Security**: Automatically removes any temporary files after completion.

## Contributing
Contributions are always welcome! Please feel free to fork the repository, make improvements, and submit pull requests.

## License
This project is available under the [MIT License](https://github.com/bakuteyev/bitwarden2keepass/blob/main/LICENSE).

## Support and Contact
For support, queries, or suggestions, please open an issue in the GitHub repository or contact me directly at [bakuteyev@gmail.com](mailto:bakuteyev@gmail.com).

## Acknowledgements
Special thanks to the Bitwarden and KeePass communities for their excellent tools that have inspired this project.