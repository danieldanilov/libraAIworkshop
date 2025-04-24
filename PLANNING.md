# Project Planning: WooCommerce AI Analyzer

## Goals
- Analyze WooCommerce (and potentially general WordPress) websites to identify themes, plugins, and potential custom functionality.
- Utilize AI (OpenAI API) to interpret the analysis results and provide actionable recommendations.

## Architecture
- Core analysis logic resides in `Scripts/extract_woo_plugins_from_website.py`.
- AI integration and main execution flow are in `Scripts/woo_analysis_with_ai.py`.
- Dependencies are managed via `requirements.txt`.

## Naming Conventions
- (To be defined)

## Constraints
- Requires Python 3.x.
- Requires `OPENAI_API_KEY` to be set for AI features.

## Setup
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate` (Linux/macOS) or `.\venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env.local` file inside the `Scripts` directory.
6. Add your OpenAI API key to `Scripts/.env.local`: `OPENAI_API_KEY=your_key_here`

## Decisions
- **API Key Management:** The `woo_analysis_with_ai.py` script explicitly looks for the `OPENAI_API_KEY` in a file named `.env.local` located within the `Scripts` directory. This keeps the key close to the script that uses it.