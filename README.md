# Travian Legends Bot

A bot for automating various tasks in Travian Legends, including oasis raiding, farm list management, and hero operations.

## Features

- **Farm List Operations**: Automated farm list sending with configurable delays
- **Oasis Raiding**: Smart raiding system that targets unoccupied oases
- **Hero Management**: Automated hero operations with health monitoring
- **Map Scanning**: Efficient scanning of nearby tiles for oasis detection

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd travian_legends_bots
   ```

2. **Navigate to Bot Directory**
   ```bash
   cd API_based_automations/travian_bot
   ```

3. **Create and Activate Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Linux/Mac
   .\venv\Scripts\activate    # On Windows
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Initial Setup Steps**
   ```bash
   # 1. Set up your identity (this will create database/identity.json and .env)
   python3 setup_identity.py
   # The script will ask for your credentials and create the .env file automatically
   
   # 2. Scan the map for oases (this will create unoccupied_oases directory)
   python3 scan_map.py
   
   # 3. Set up a raid plan (this will create database/saved_raid_plan.json)
   python3 launcher.py
   # Then select option 4: "Setup new raid plan interactively"
   # You'll be asked to:
   # - Select a village to raid from
   # - Choose which units to use (e.g., Imperians, Equites Imperatoris)
   # - Set the group size for each unit type
   ```

## Required Dependencies

- beautifulsoup4==4.13.4
- python-dotenv==1.1.0
- Requests==2.32.3
- tqdm==4.67.1

## Usage

1. **First Time Setup**
   - Run the launcher: `python3 launcher.py`
   - Choose "Setup Identity" option
   - Enter your Travian server URL, username, and password

2. **Available Operations**
   - Farm List Operations
   - Oasis Raiding
   - Hero Operations
   - Map Scanning

## Project Structure

```
API_based_automations/travian_bot/
├── analysis/           # Analysis tools
├── core/              # Core functionality
├── features/          # Feature implementations
├── identity_handling/ # Login and identity management
├── database/          # Configuration storage
│   ├── identity.json           # Created by setup_identity.py
│   └── saved_raid_plan.json    # Created by raid plan setup
├── unoccupied_oases/  # Created by scan_map.py
├── launcher.py        # Main entry point
├── requirements.txt   # Dependencies
└── setup_identity.py  # Identity setup script
```

## Troubleshooting

### Common Setup Issues

1. **Python Version**
   - Required: Python 3.8 or higher
   - Check version: `python3 --version`
   - If python3 command not found, install it:
     ```bash
     # On Ubuntu/Debian
     sudo apt update
     sudo apt install python3
     
     # On Windows
     # Download from python.org
     ```

2. **Virtual Environment**
   - If `venv` module is missing:
     ```bash
     # On Ubuntu/Debian
     sudo apt install python3-venv
     ```
   - If activation fails, ensure you're in the correct directory

3. **Dependency Issues**
   - If pip install fails, try upgrading pip:
     ```bash
     pip install --upgrade pip
     ```
   - For SSL errors, ensure certificates are up to date

4. **Missing Modules**
   - If you get "No module named 'core.hero_manager'" error:
     - The hero_manager.py file should be created in the core directory
     - It wraps the functionality from hero_runner.py

### Directory Structure
If any required directories are missing:
```bash
mkdir -p database logs unoccupied_oases
```

## Security Note

- Store your credentials in a `.env` file
- Never commit your `.env` file or identity information
- The `.gitignore` file is configured to prevent accidental commits of sensitive data

## Disclaimer

This bot is for educational purposes only. Use at your own risk and in accordance with Travian Legends' terms of service.

## License

This project is open source and available under the MIT License.
