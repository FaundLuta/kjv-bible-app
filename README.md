# KJV Bible App

A modern desktop Bible study application built with Python and Tkinter, featuring the King James Version (KJV) translation with an intuitive interface for reading, searching, and saving favorite verses.

## Features

- 📖 **Complete KJV Bible** - Access all books and chapters of the King James Version
- 🔍 **Search Functionality** - Quickly find verses by keyword or reference
- 💾 **Save Favorite Verses** - Bookmark and organize verses for later study
- 🎨 **Multiple Themes** - Choose between Dark, Light, and Sepia themes for comfortable reading
- 📝 **Study Notes** - Add personal notes to saved verses
- 🔤 **Adjustable Font Size** - Customize text size for better readability
- 📋 **Copy to Clipboard** - Easily share verses with others
- 💡 **Persistent Data** - Your saved verses and preferences are automatically saved

## Screenshots

![Bible App Interface](download%20(1).jfif)

## System Requirements

- Python 3.7 or higher
- tkinter (usually included with Python)
- Windows, macOS, or Linux

## Installation

### From Source

1. **Clone the repository:**
   ```bash
   git clone https://github.com/FaundLuta/kjv-bible-app.git
   cd kjv-bible-app
   ```

2. **Install Python** (if not already installed):
   - Download from [python.org](https://www.python.org)

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** tkinter typically comes with Python, but on some Linux systems you may need to install it separately:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-tk
   
   # Fedora
   sudo dnf install python3-tkinter
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

## File Structure

```
kjv-bible-app/
├── app.py              # Main application code
├── KJV.json           # Complete KJV Bible data
├── app_icon.ico       # Application icon
├── download (1).jfif  # Screenshot/promotional image
├── requirements.txt   # Python dependencies
├── README.md          # This file
└── .gitignore         # Git ignore rules
```

## Usage

### Navigation
- Click on book names to select books from the Old Testament or New Testament
- Choose chapters from the dropdown menu
- Read verses in the main text area

### Search
- Use the search bar to find verses by keyword, book name, or verse reference
- Results will highlight matching verses

### Saving Verses
- Click "Save" to add a verse to your favorites
- Add personal notes to your saved verses
- Access saved verses from the sidebar

### Customization
- Switch themes using the theme selector in the header
- Adjust font size using the font size controls
- Your preferences are automatically saved

## Features Explained

### Dark Theme
Ideal for reading in low-light environments with a comfortable dark interface.

### Light Theme
Classic light background for daytime reading and printing.

### Sepia Theme
Warm, vintage-style background reminiscent of old book pages.

## Data Persistence

Your study data is automatically saved to a file in your user directory:
- **Location:** `~/bible_study_data.json`
- **Contents:** Saved verses and personal notes

## Known Limitations

- tkinter may have limited styling options on some platforms
- Large searches may take a moment to complete

## Future Enhancements

- [ ] Multiple Bible translations
- [ ] Commentary support
- [ ] Verse comparison between translations
- [ ] Export study notes to PDF
- [ ] Dark mode for eyes comfort optimization
- [ ] Cross-references between verses

## License

This project is provided as-is for personal use. The King James Version of the Bible is in the public domain.

## Contributing

Feel free to fork this project, make improvements, and submit pull requests!

## Support

If you encounter any issues or have suggestions for improvement, please create an issue in the repository.

## Author

**faundln** © 2026

---

**Disclaimer:** This application is designed for personal Bible study. The King James Version used in this application is in the public domain.
