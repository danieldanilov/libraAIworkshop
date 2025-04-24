#!/usr/bin/env python3
import os
import re
import sys
from datetime import datetime


def split_markdown_file(input_file, num_files=5):
    """
    Split a large markdown file into multiple smaller files at YAML frontmatter boundaries.

    Args:
        input_file (str): Path to the input markdown file
        num_files (int): Number of files to split into

    Returns:
        list: Paths to the created output files
    """
    print(f"Splitting {input_file} into {num_files} files...")

    # Read the entire file
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Pattern to match YAML frontmatter blocks
    # Matches "---" followed by any content until another "---"
    yaml_pattern = re.compile(r"---\s*?\n(.*?)\n---", re.DOTALL)

    # Find all matches
    yaml_matches = list(yaml_pattern.finditer(content))
    total_sections = len(yaml_matches)

    print(f"Found {total_sections} content sections with YAML frontmatter")

    if total_sections < num_files:
        print(
            f"Warning: Cannot split into {num_files} files as there are only {total_sections} sections."
        )
        num_files = total_sections

    # Calculate sections per file (approximately)
    sections_per_file = total_sections // num_files
    remainder = total_sections % num_files

    # Get the base filename without extension
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.dirname(input_file)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create output files
    output_files = []
    current_section = 0

    for i in range(num_files):
        # Calculate how many sections to include in this file
        sections_in_this_file = sections_per_file
        if i < remainder:
            sections_in_this_file += 1

        # Create output filename
        output_file = os.path.join(
            output_dir, f"{base_filename}_part{i+1}_of_{num_files}_{timestamp}.md"
        )
        output_files.append(output_file)

        # If this is the first file, start from the beginning
        if i == 0:
            start_pos = 0
        else:
            # Start from the position of the current section's YAML block
            start_pos = yaml_matches[current_section].start()

        # Increment the current section counter
        current_section += sections_in_this_file

        # If this is the last file, go to the end
        if i == num_files - 1:
            end_pos = len(content)
        else:
            # End at the position of the next section's YAML block
            end_pos = yaml_matches[current_section].start()

        # Extract content for this file
        file_content = content[start_pos:end_pos]

        # Write to output file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(file_content)

        print(f"Created: {output_file} ({len(file_content) // 1024}KB)")

    return output_files


if __name__ == "__main__":
    # Check if file path is provided as argument
    if len(sys.argv) < 2:
        print("Usage: python split_markdown.py <markdown_file> [number_of_files]")
        sys.exit(1)

    input_file = sys.argv[1]

    # Check if the file exists
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} does not exist.")
        sys.exit(1)

    # Get number of files to split into (default is 5)
    num_files = 5
    if len(sys.argv) > 2:
        try:
            num_files = int(sys.argv[2])
            if num_files <= 0:
                raise ValueError("Number of files must be positive")
        except ValueError:
            print("Error: Number of files must be a positive integer.")
            sys.exit(1)

    # Split the file
    output_files = split_markdown_file(input_file, num_files)

    print(f"\nSuccessfully split {input_file} into {len(output_files)} files.")
    print("Output files:")
    for file in output_files:
        print(f"- {file}")
