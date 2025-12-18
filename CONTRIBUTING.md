# Contributing to Quantitative Finance Portfolio

Thank you for your interest in contributing to the Quantitative Finance Portfolio! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Maintain professional standards

## Getting Started

1. **Fork the repository** and clone your fork
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"
   ```

## Development Workflow

1. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Write tests** for new functionality:
   - Add tests in the `tests/` directory
   - Ensure all tests pass: `pytest tests/ -v`

4. **Run linting**:
   ```bash
   flake8 .
   black --check .
   ```

5. **Commit your changes**:
   ```bash
   git commit -m "Add: Description of your changes"
   ```

6. **Push and create a Pull Request**

## Coding Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Maximum line length: 127 characters

### Code Formatting

We use `black` for code formatting:
```bash
black .
```

### Linting

We use `flake8` for linting:
```bash
flake8 .
```

### Documentation

- All functions and classes must have docstrings
- Use Google-style docstrings:
  ```python
  def function_name(param1: type, param2: type) -> return_type:
      """
      Brief description.
      
      Args:
          param1: Description of param1
          param2: Description of param2
          
      Returns:
          Description of return value
      """
  ```

## Testing

- Write unit tests for all new functionality
- Aim for high test coverage (>80%)
- Run tests before submitting:
  ```bash
  pytest tests/ -v --cov=.
  ```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update `FEATURES_TRACKING.md` if adding new features
5. Write a clear PR description explaining:
   - What changes were made
   - Why they were made
   - How to test the changes

## Adding New Features

When adding new quantitative finance features:

1. **Create the module** in the appropriate directory:
   - `models/` for financial models
   - `strategies/` for trading strategies
   - `analysis/` for analysis tools
   - `utils/` for utility functions

2. **Add comprehensive docstrings** explaining:
   - What the function/class does
   - Parameters and return values
   - Mathematical formulas if applicable
   - Usage examples

3. **Write unit tests** demonstrating correctness

4. **Update documentation**:
   - Add to `README.md` if it's a major feature
   - Update `FEATURES_TRACKING.md`

5. **Add examples** in `examples/` if appropriate

## Reporting Issues

When reporting bugs or requesting features:

- Use clear, descriptive titles
- Provide steps to reproduce (for bugs)
- Include expected vs actual behavior
- Add code examples if relevant
- Specify Python version and dependencies

## Questions?

Feel free to open an issue for questions or discussions about contributions.

Thank you for contributing!
