#!/usr/bin/env python3
import os
import re
import sys
import shutil
from datetime import datetime


def count_words(text):
    """Count the number of words in a text string."""
    # Split by whitespace and count non-empty strings
    return len([word for word in text.split() if word.strip()])


def split_markdown_by_word_count(input_file, output_dir, max_words=300000):
    """
    Split a large markdown file into multiple smaller files at YAML frontmatter boundaries,
    ensuring no file exceeds the maximum word count.

    Args:
        input_file (str): Path to the input markdown file
        output_dir (str): Directory to save output files
        max_words (int): Maximum number of words per file

    Returns:
        list: Paths to the created output files
    """
    print(f"\nProcessing: {input_file}")

    # Read the entire file
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # First check if the file already meets the word limit
    total_word_count = count_words(content)
    if total_word_count <= max_words:
        print(
            f"  Skipping split: File is already under the word limit ({total_word_count} words)."
        )
        # Create a copy in the output directory
        output_file = os.path.join(output_dir, os.path.basename(input_file))
        shutil.copy2(input_file, output_file)
        print(f"  Copied to: {os.path.basename(output_file)}")
        return [output_file]

    print(
        f"  Splitting file ({total_word_count} words, max {max_words} words per file)..."
    )

    # Pattern to match YAML frontmatter blocks
    # Matches "---" followed by any content until another "---"
    yaml_pattern = re.compile(r"(---\s*?\n.*?\n---.*?)(?=\n---|\Z)", re.DOTALL)

    # Find all sections (each with frontmatter and content)
    sections = yaml_pattern.findall(content)
    total_sections = len(sections)

    print(f"  Found {total_sections} content sections with YAML frontmatter")

    # Get the base filename without extension
    base_filename = os.path.splitext(os.path.basename(input_file))[0]

    # Create output files
    output_files = []
    current_file_content = ""
    current_word_count = 0
    file_number = 1

    for i, section in enumerate(sections):
        section_word_count = count_words(section)

        # Check if adding this section would exceed the word limit
        if (
            current_word_count + section_word_count > max_words
            and current_word_count > 0
        ):
            # Save the current file
            output_file = os.path.join(
                output_dir, f"{base_filename}_wordlimit_{file_number}.md"
            )
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(current_file_content)

            output_files.append(output_file)
            print(
                f"  Created: {os.path.basename(output_file)} ({current_word_count} words)"
            )

            # Start a new file
            current_file_content = section
            current_word_count = section_word_count
            file_number += 1
        else:
            # Add section to current file
            current_file_content += section if i == 0 else f"\n{section}"
            current_word_count += section_word_count

        # Status update for large files
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{total_sections} sections...")

    # Save the last file if there's content
    if current_file_content:
        output_file = os.path.join(
            output_dir, f"{base_filename}_wordlimit_{file_number}.md"
        )
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(current_file_content)

        output_files.append(output_file)
        print(
            f"  Created: {os.path.basename(output_file)} ({current_word_count} words)"
        )

    return output_files


def process_directory(directory_path, max_words=300000):
    """Process all markdown files in a directory."""
    markdown_files = [
        os.path.join(directory_path, f)
        for f in os.listdir(directory_path)
        if f.endswith(".md") and os.path.isfile(os.path.join(directory_path, f))
    ]

    if not markdown_files:
        print(f"No markdown files found in {directory_path}")
        return

    print(f"Found {len(markdown_files)} markdown files to process")

    # Create timestamped output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_base_dir = os.path.join(directory_path, "split_by_words")
    os.makedirs(output_base_dir, exist_ok=True)

    output_dir = os.path.join(output_base_dir, f"output_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    print(f"Created output directory: {output_dir}")

    total_output_files = []
    for md_file in markdown_files:
        output_files = split_markdown_by_word_count(md_file, output_dir, max_words)
        total_output_files.extend(output_files)

    print(f"\nAll files processed and saved to: {output_dir}")
    print(f"Total files in output directory: {len(total_output_files)}")


if __name__ == "__main__":
    # Set default directory to the script's location
    default_dir = os.path.dirname(os.path.abspath(__file__))

    # Parse arguments
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isdir(path):
            target_dir = path
        elif os.path.isfile(path):
            # Process a single file
            max_words = 300000
            if len(sys.argv) > 2:
                try:
                    max_words = int(sys.argv[2])
                except ValueError:
                    print("Error: Maximum words must be a positive integer.")
                    sys.exit(1)

            # Create timestamped output directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            parent_dir = os.path.dirname(path)
            output_base_dir = os.path.join(parent_dir, "split_by_words")
            os.makedirs(output_base_dir, exist_ok=True)

            output_dir = os.path.join(output_base_dir, f"output_{timestamp}")
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created output directory: {output_dir}")

            output_files = split_markdown_by_word_count(path, output_dir, max_words)
            if output_files:
                print(f"\nProcessed file saved to: {output_dir}")
            sys.exit(0)
        else:
            print(f"Error: {path} is not a valid file or directory.")
            sys.exit(1)
    else:
        target_dir = default_dir

    # Get maximum words per file (default is 300000)
    max_words = 300000
    if len(sys.argv) > 2 and os.path.isdir(sys.argv[1]):
        try:
            max_words = int(sys.argv[2])
            if max_words <= 0:
                raise ValueError("Maximum words must be positive")
        except ValueError:
            print("Error: Maximum words must be a positive integer.")
            sys.exit(1)

    print(f"Processing all markdown files in: {target_dir}")
    print(f"Maximum words per file: {max_words}")

    # Process the directory
    process_directory(target_dir, max_words)
