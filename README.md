# Travian Legends Bot

An automated bot for Travian Legends that handles farming and oasis raiding operations.

## Features

- **Farm List Automation**
  - Automated sending of farm lists with configurable delays
  - Random timing variations to avoid detection
  - Auto-recovery from session timeouts
  - Configurable stop time (default: 9 AM)

- **Oasis Raiding**
  - Smart oasis selection based on distance
  - Animal detection to avoid losses
  - Configurable maximum raid distance
  - Support for multiple unit types
  - Hero raiding capability
  - Automatic troop availability checking

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/travian_legends_bots.git
cd travian_legends_bots
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your credentials:
```env
TRAVIAN_USERNAME=your_username
TRAVIAN_PASSWORD=your_password
```

4. Run the launcher:
```bash
cd API_based_automations/travian_bot
python launcher.py
```

## Usage

The bot provides several operation modes through an interactive launcher:

1. **One-time Farm + Raid** - Executes one round of farming and raiding
2. **Infinite Safe Loop** - Continuously farms and raids with safety checks
3. **Reset Raid Plan** - Clears the saved raid configuration
4. **Setup New Raid Plan** - Interactive setup for a new raiding strategy
5. **Update Identity** - Updates village and player information
6. **Hero Operations** - Manages hero-related activities

## Configuration

- Farm list delays and burst counts can be configured in `raid_list_main.py`
- Raid settings (units, group sizes, max distance) are stored in `database/saved_raid_plan.json`
- Village and player information is stored in `database/identity.json`

## Safety Features

- Distance-based raid targeting
- Animal presence detection
- Automatic session recovery
- Random timing variations
- Safe shutdown at specified time

## Contributing

Feel free to submit issues and pull requests.

## Disclaimer

This is an unofficial bot for Travian Legends. Use at your own risk. The authors are not responsible for any consequences of using this bot.

## License

MIT License
