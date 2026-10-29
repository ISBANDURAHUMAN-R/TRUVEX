# Contributing to TruVex AI

Thank you for your interest in contributing to **TruVex AI – AI Against Misinformation & Digital Trust**! We welcome contributions to improve fact-checking accuracy, expand source detection, optimize search pipelines, and enhance UI accessibility.

---

## 🛠️ Development Setup

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/TRUVEX.git
   cd TRUVEX
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   # Windows:
   .\.venv\Scripts\activate
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install pytest pytest-asyncio ruff
   ```

4. **Run the test suite:**
   ```bash
   pytest tests -v
   ```

5. **Start the local server:**
   ```bash
   python run.py
   ```

---

## 📋 Guidelines

- **Code Style**: Ensure code follows PEP 8. Format with `ruff` or `black`.
- **Anti-Hallucination Policy**: TruVex AI strictly uses verifiable, live-retrieved web URLs. Never hardcode fabricated URLs or citations in models.
- **Tests**: Add test cases in `tests/` for new features or bug fixes.
- **Commit Messages**: Use conventional commits (e.g., `feat:`, `fix:`, `docs:`, `refactor:`, `test:`).

---

## 📬 Submitting Changes

1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Commit your changes: `git commit -m "feat: description of change"`
3. Push to your branch: `git push origin feature/your-feature-name`
4. Open a Pull Request on GitHub with a clear summary of your changes.
