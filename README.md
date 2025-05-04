# 🚀 Travian API Automation Project
## 🛠 Personal Reverse Engineering and Automation

> *Built out of curiosity, for personal use, and as an engineering challenge.* ⚙️

> A full early-game flow from login to launching raids.

## 🔑 Core Features

### 1. Login and Village Management
- Secure login with credentials stored in `.env`
- Auto-fetch all linked avatars and villages
- Session management and automatic reconnection

### 2. Map Scanning and Oasis Detection
- Scan thousands of tiles to detect nearby oases
- Local storage of scan results for fast reuse
- Automatic oasis analysis and distance sorting

### 3. Dual Raid Planning System
- Farm List Operations: Launch farm lists from villages
- Oasis Scanning: Automatically detect and raid nearby empty oases
- Power Analysis: Evaluate target strength and optimize troop deployment

### 4. Hero Operations
- Priority Targeting: Focus on closer and weaker oases first
- Health Management: Automatic health monitoring and regeneration
- Configurable Parameters: Customize power thresholds, distances, and health limits
- Continuous Operation: Run hero raiding operations continuously

## 🛠️ Technical Implementation

### API-based Automation
- Direct interaction with Travian's APIs and HTML endpoints
- GraphQL for account, avatar, and farm list management
- Classic POST/GET forms and HTML scraping for troop movements
- Dynamic bot protection field handling (tokens, checksums)

### Multi-threading
- Parallel processing for farm list operations
- Concurrent oasis scanning and raiding
- Thread-safe operation queue management

### Anti-Detection Measures
- Randomized delays between actions
- Human-like interaction patterns
- Request rate limiting

## 🎮 Usage

### Prerequisites
- Python 3.8 or higher
- Chrome browser installed
- Selenium WebDriver for Chrome

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/travian_bot.git
   cd travian_legend_bots/API_based_automations/travian_bot
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your identity:
   - Run the launcher
   - Select "Setup Identity" option
   - Enter your server URL, username, and password

### Running the Bot
1. Start the launcher:
   ```bash
   python launcher.py
   ```

2. Choose from available operations:
   - Farm List Burst + Raid Planner
   - Farm List Operations
   - Hero Raiding
   - Interactive Raid Planning

## 📁 Project Structure

```
travian_bot/
├── core/
│   ├── api/              # API interactions
│   ├── hero_manager.py   # Hero management
│   └── operation_queue.py # Operation management
├── features/
│   ├── hero/            # Hero operations
│   ├── raiding/         # Raiding features
│   └── farm/            # Farm operations
├── identity_handling/   # Identity management
├── database/           # Configuration storage
└── launcher.py         # Main entry point
```

## 🔧 Configuration

### Hero Raiding Settings
- Priority Radius: 1-20 fields
- Priority Max Power: 100-2000
- Normal Min Power: 100-2000
- Normal Max Power: 100-5000
- Min Health: 10-90%

### Farm List Settings
- Configure farm lists through the interactive setup
- Set resource thresholds and collection intervals

## 🔒 Security

- Credentials are stored locally in `database/identity.json`
- Never share your identity file or commit it to version control
- The bot includes `.gitignore` to prevent accidental credential commits
- Checksum bypass implementation for secure login

## 📚 Project Philosophy

This tool was never meant to be widely distributed:
- It's a personal technical exercise — a playground for reverse engineering, automation architecture, and real-world API handling
- It intentionally skips building a GUI to stay lightweight and focus on code quality and expandability
- It's not intended to fully replace manual gameplay, only to relieve repetitive tasks like early-game oasis farming

## ⚠️ Disclaimer

This bot is for educational purposes only. Use at your own risk and in accordance with Travian Legends' terms of service.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License
