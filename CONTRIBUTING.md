# Contributing to Orbit

Thank you for considering contributing to Orbit! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Your system information (distro, Python version, GTK version)
- Screenshots if applicable

### Suggesting Features

Feature requests are welcome! Please:
- Check if the feature has already been requested
- Provide a clear use case
- Explain how it would benefit users

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**: `git commit -m "Add amazing feature"`
6. **Push to your fork**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise
- Comment complex logic

### Testing

- Test your changes on your system
- If possible, test on multiple distributions
- Ensure no regressions in existing functionality

### Adding Package Manager Support

To add support for a new package manager:

1. Create a new adapter in `adapters/` (e.g., `adapters/newpm.py`)
2. Inherit from `PackageAdapter` base class
3. Implement all required methods:
   - `get_installed_apps()`
   - `update_app()`
   - `remove_app()`
   - `search_apps()`
4. Register the adapter in `manager.py`
5. Add appropriate color hint in `ui/style.css`
6. Update documentation

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/orbit.git
cd orbit

# Create a virtual environment (optional)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run Orbit
python3 main.py
```

## Project Structure

- `main.py` - Application entry point
- `manager.py` - Core package management logic
- `models.py` - Data models
- `adapters/` - Package manager adapters
- `ui/` - User interface components
- `utils/` - Utility modules

## Questions?

Feel free to open an issue for any questions about contributing!

---

**Thank you for helping make Orbit better!** 🚀
