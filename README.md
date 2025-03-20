# Paper Genie

Paper Genie is a lightweight application I developed during my A-levels to streamline the process of downloading past papers for exam preparation.

## Features
- Quickly search and download past papers.
- Scrapes data from [GCE Guide](https://papers.gceguide.cc/).
- Custom API built to interact efficiently with the website.

## Dependencies
Paper Genie relies on the following external libraries:

- `tkinter` (for the GUI)
- `PIL` (for image processing in Tkinter)
- `customtkinter` (for enhanced UI elements)
- `beautifulsoup4` (for web scraping)
- `requests` (for sending HTTP requests)
- `shutil` (for file operations)
- `asyncio` (for asynchronous programming)
- `aiohttp` (for async HTTP requests)
- `aiofiles` (for async file handling)

## How It Works
1. The app scrapes [GCE Guide](https://papers.gceguide.cc/) to fetch the required past papers.
2. It sends HTTP requests to retrieve available documents.
3. Downloads and organizes the papers efficiently for easy access.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Cinammonsniper/paper-genie.git
   ```
2. Acrivate the virtual enviroment:
   ```bash
   ./bin/activate
   ```
2. Run the application:
   ```bash
   python GUI.py
   ```

## License
This project is open-source and available under the [MIT License](LICENSE).

## Contributions
Feel free to submit pull requests or open issues if you find any bugs or have feature suggestions.

---

