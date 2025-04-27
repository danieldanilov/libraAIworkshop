# Project Planning: Libra AI Workshop Repository

## Goals
- Serve as a central repository for materials, scripts, and examples from the Libra AI Workshop.
- Demonstrate practical applications of AI tools (ChatGPT, Perplexity, Cursor) for enhancing productivity, particularly in support engineering.
- Provide examples of prompt engineering techniques.
- Showcase script examples for automating tasks (e.g., website analysis, file organization).
- Illustrate methods for using AI in complex troubleshooting scenarios.

## Architecture & Content
- **`README.md`**: High-level overview of the workshop and repository contents.
- **`PLANNING.md`** (this file): Project goals, structure, setup instructions, and decisions.
- **`TASK.md`**: Log of tasks performed and discovered during work.
- **`Scripts/`**: Contains example Python scripts discussed in the workshop.
  - `woo_analysis_with_ai.py`: Analyzes WooCommerce sites using web scraping and AI.
  - `extract_woo_plugins_from_website.py`: Helper script for `woo_analysis_with_ai.py`.
  - `organize_obsidian_attachments.py`: Example script for file organization (Note: Actual implementation may vary based on workshop discussion).
- **`Documents/`**: Workshop notes, prompt examples, or other related documents.
- **`Support Interactions/`**: Example directory structure for organizing troubleshooting data (logs, screenshots, notes).
- **`requirements.txt`**: Python dependencies for the scripts.

## Naming Conventions
- Use descriptive names for files and directories.
- Follow Python PEP 8 guidelines for scripts.

## Constraints
- Python scripts require Python 3.x.
- Specific scripts (like `woo_analysis_with_ai.py`) may require API keys (e.g., `OPENAI_API_KEY`).

## Setup (for Python Scripts)
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate` (Linux/macOS) or `.\venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env.local` file inside the `Scripts` directory *if using scripts requiring API keys*.
6. Add necessary API keys to `Scripts/.env.local` (e.g., `OPENAI_API_KEY=your_key_here`).

## Decisions
- **API Key Management:** The `woo_analysis_with_ai.py` script explicitly looks for the `OPENAI_API_KEY` in a file named `.env.local` located within the `Scripts` directory. This keeps the key close to the script that uses it. *Other scripts requiring keys should follow a similar pattern unless otherwise specified.*
- **Documentation Focus:** Keep `README.md` high-level, `PLANNING.md` for structure/setup, and `TASK.md` for ongoing work log.
- **Workshop Structure (`LibraWorkshopAI`):** Added clear learning objectives, brief interactive/demonstration points (prompting, vibe coding), enhanced warnings section with verification steps, and a commitment-focused takeaway question to improve engagement within the 1-hour hybrid format. (July 29, 2024)