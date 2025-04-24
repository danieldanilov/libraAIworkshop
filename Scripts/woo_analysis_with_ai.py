"""
WooCommerce Website AI Analyzer

This script builds on the WooCommerce Website Analyzer to add AI interpretation of results.
It sends the analysis report to OpenAI's API and gets back a clear explanation of findings.

Features:
- All features of the original WooCommerce Website Analyzer
- AI-powered interpretation of results
- Clear explanations of detected plugins, themes, and custom functionality
- Recommendations for recreating similar functionality

Usage:
    python woo_analysis_with_ai.py [--pages N] [--verbose] [--save]

Arguments:
    --pages - (Optional) Number of pages to crawl (default: 5)
    --verbose - (Optional) Show detailed information
    --save - (Optional) Save results to a file

Output:
    Creates a detailed report in the console with AI interpretation
"""

import os
import sys
import argparse
import requests
import json
from urllib.parse import urlparse

# Import the WooCommerceAnalyzer from the existing script
from extract_woo_plugins_from_website import WooCommerceAnalyzer

# Add dotenv import
try:
    from dotenv import load_dotenv

    # Construct the path to .env.local relative to the script file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(script_dir, ".env.local")

    if os.path.exists(dotenv_path):
        # Load the .env.local file specifically
        load_dotenv(dotenv_path=dotenv_path, override=True)
        print(f"Loaded environment variables from {dotenv_path}")
    else:
        # If .env.local doesn't exist, load_dotenv() without path will check for a standard .env or system vars
        load_dotenv()
        print(
            f"Info: .env.local file not found at {dotenv_path}. Attempting to load from standard .env or system environment variables."
        )

except ImportError:
    print("python-dotenv library not found. Cannot load .env.local file.")
    print("Install it using: pip install python-dotenv")
    print("Relying solely on system environment variables for OPENAI_API_KEY.")


# Hardcoded URL to analyze - change this to analyze a different site
TARGET_URL = "https://danieldanilov.com/"


class AIWooCommerceAnalyzer:
    def __init__(self, url=TARGET_URL, max_pages=5, verbose=False):
        """Initialize with URL to analyze"""
        self.url = url
        # Load API key from environment variable
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print(
                "Warning: OPENAI_API_KEY not found in environment. AI features will likely fail."
            )
            # Optionally, raise an error or handle the missing key appropriately
            # raise ValueError("OPENAI_API_KEY must be set in the environment or .env.local file")
        self.max_pages = max_pages
        self.verbose = verbose
        self.analyzer = WooCommerceAnalyzer(url, max_pages=max_pages, verbose=verbose)

    def analyze(self):
        """Run the WooCommerce analysis and return the report"""
        print(f"Starting analysis of {self.url}...")
        self.analyzer.analyze_site()
        self.report = self.analyzer.generate_report(save_to_file=False)
        return self.report

    def get_ai_interpretation(self):
        """Send the analysis report to OpenAI and get back an interpretation"""
        if not hasattr(self, "report"):
            self.analyze()

        # Check if API key is available before proceeding
        if not self.api_key:
            return "Error: OpenAI API key not configured. Cannot get AI interpretation."

        # Create the prompt for the AI
        prompt = self._create_ai_prompt()

        # Send to OpenAI API
        try:
            response = self._call_openai_api(prompt)
            return response
        except Exception as e:
            return f"Error getting AI interpretation: {str(e)}"

    def _create_ai_prompt(self):
        """Create a prompt for the OpenAI API based on the analysis results"""
        domain = urlparse(self.url).netloc

        prompt = f"""You are a WordPress and WooCommerce expert. I've analyzed the website {domain} and found the following technologies.
Please interpret these findings and provide:
1. A clear explanation of what plugins and themes were detected
2. What likely custom functionality exists on the site
3. Recommendations for how someone could recreate similar functionality
4. Any potential challenges that might be encountered during recreation

Here's the technical analysis:

{self.report}

Please provide your expert interpretation in a clear, organized manner suitable for a client who wants to recreate similar functionality.
"""
        return prompt

    def _call_openai_api(self, prompt):
        """Call the OpenAI API with the given prompt"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        data = {
            "model": "gpt-4-turbo",  # You can use gpt-3.5-turbo if preferred
            "messages": [
                {
                    "role": "system",
                    "content": "You are a WordPress and WooCommerce expert analyzing website technologies.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.5,  # Lower temperature for more factual responses
            "max_tokens": 2000,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
        )

        if response.status_code != 200:
            error_info = response.json().get("error", {})
            error_message = error_info.get("message", "Unknown error")
            raise Exception(f"API Error (Code {response.status_code}): {error_message}")

        result = response.json()
        return result["choices"][0]["message"]["content"]


def main():
    """Main function to parse arguments and run the analyzer"""
    parser = argparse.ArgumentParser(description="WooCommerce Website AI Analyzer")
    parser.add_argument(
        "--pages", type=int, default=5, help="Number of pages to crawl (default: 5)"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed information"
    )
    parser.add_argument("--save", action="store_true", help="Save results to a file")

    args = parser.parse_args()

    # Create the analyzer with the hardcoded URL
    try:
        ai_analyzer = AIWooCommerceAnalyzer(
            url=TARGET_URL, max_pages=args.pages, verbose=args.verbose
        )

        # Run the analysis
        print("Running WooCommerce analysis...")
        report = ai_analyzer.analyze()

        # Get AI interpretation
        print("\nGetting AI interpretation of results...\n")
        interpretation = ai_analyzer.get_ai_interpretation()

        # Display results
        print("\n" + "=" * 80)
        print("TECHNICAL ANALYSIS REPORT")
        print("=" * 80)
        print(report)

        print("\n" + "=" * 80)
        print("AI INTERPRETATION & RECOMMENDATIONS")
        print("=" * 80)
        print(interpretation)

        # Save results if requested
        if args.save:
            domain = urlparse(TARGET_URL).netloc
            filename = f"ai_woocommerce_analysis_{domain}.txt"
            with open(filename, "w") as f:
                f.write("TECHNICAL ANALYSIS REPORT\n")
                f.write("=" * 80 + "\n")
                f.write(report)
                f.write("\n\nAI INTERPRETATION & RECOMMENDATIONS\n")
                f.write("=" * 80 + "\n")
                f.write(interpretation)
            print(f"\nResults saved to {filename}")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
