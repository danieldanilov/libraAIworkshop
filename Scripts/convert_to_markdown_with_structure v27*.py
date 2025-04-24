import os
import xml.etree.ElementTree as ET
import html
import re
from datetime import datetime
from collections import defaultdict

# Directories
base_dir = os.path.expanduser("~/Documents/Github/webImportsWoo/")
html_dir = os.path.join(base_dir, "downloaded_docs/")
markdown_dir = os.path.join(base_dir, "markdown_docs/")


def ensure_directories_exist(*dirs):
    """Ensure all directories exist, creating them if necessary."""
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)


def clean_html_content(content):
    """
    Cleans up HTML content to Markdown-compatible format.
    """
    content = html.unescape(content)  # Decode HTML entities
    # Remove WordPress-style block comments and extra tags
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    content = re.sub(r"<(/?[^>]+)>", "", content)  # Remove remaining HTML tags
    # Convert specific HTML elements
    content = re.sub(r"\n{3,}", "\n\n", content)  # Collapse excessive line breaks
    return content.strip()


def parse_authors(root, namespaces):
    """
    Extracts authors' full names and usernames from the XML file.
    Returns a dictionary mapping usernames to full names.
    """
    authors = {}
    for author in root.findall("./channel/wp:author", namespaces):
        username = author.find("wp:author_login", namespaces).text
        first_name = author.find("wp:author_first_name", namespaces).text or ""
        last_name = author.find("wp:author_last_name", namespaces).text or ""
        full_name = f"{first_name} {last_name}".strip()
        if username and full_name:
            authors[username] = f"{full_name} ({username})"
    return authors


def format_date(pub_date):
    """
    Converts a publication date into ISO 8601 format.
    """
    try:
        dt = datetime.strptime(
            pub_date, "%a, %d %b %Y %H:%M:%S %z"
        )  # Parse original format
        return dt.isoformat()  # Convert to ISO 8601
    except ValueError:
        return "Invalid Date"


def is_afk_post(title, content):
    """
    Determines if a post is an AFK request based on its title or content.
    """
    if "AFK" in title.upper():  # Check for "AFK" in the title
        return True
    if "#afk" in content.lower():  # Check for the #afk tag
        return True
    # Check for date patterns in the title (e.g., 04Jul24 or 04Jul24 to 05Jul24)
    if re.search(r"\b\d{2}[A-Za-z]{3}\d{2}\b", title):
        return True
    if "to" in title and re.search(r"\b\d{2}[A-Za-z]{3}\d{2}\b", title):
        return True
    return False


def get_base_domain(filename):
    """Extract base domain name from filename."""
    # Remove any trailing numbers (e.g., domain.com-1 -> domain.com)
    return re.sub(r"-\d+$", "", filename.replace(".xml", ""))


def process_all_wordpress_files():
    """Process all WordPress XML files in the input directory."""
    # Dictionary to group files by base domain
    domain_files = defaultdict(list)

    # Group files by their base domain
    for filename in os.listdir(html_dir):
        if filename.endswith(".xml"):
            base_domain = get_base_domain(filename)
            domain_files[base_domain].append(filename)

    # Process each domain's files
    for base_domain, files in domain_files.items():
        print(f"Processing domain: {base_domain}")
        all_posts = []

        # Process each file for this domain
        for xml_file in files:
            posts = parse_wordpress_xml(xml_file, collect_only=True)
            all_posts.extend(posts)

        # Sort posts by date
        all_posts.sort(key=lambda x: x["date"])

        # Write combined output
        write_combined_markdown(base_domain, all_posts)


def parse_wordpress_xml(xml_filename, collect_only=False):
    """
    Parse WordPress XML and return posts data.
    If collect_only is True, returns list of posts instead of writing files.
    """
    try:
        tree = ET.parse(os.path.join(html_dir, xml_filename))
        root = tree.getroot()
    except (FileNotFoundError, ET.ParseError) as e:
        print(f"Error processing {xml_filename}: {e}")
        return [] if collect_only else None

    namespaces = {
        "content": "http://purl.org/rss/1.0/modules/content/",
        "wp": "http://wordpress.org/export/1.2/",
        "dc": "http://purl.org/dc/elements/1.1/",
    }

    authors = parse_authors(root, namespaces)
    posts = []

    for item in root.findall("./channel/item"):
        if item.find("wp:status", namespaces).text != "publish":
            continue

        title = item.find("title").text or "Untitled"
        content = item.find("content:encoded", namespaces).text or ""

        if is_afk_post(title, content):
            continue

        # Extract comments
        comments = []
        for comment in item.findall("wp:comment", namespaces):
            if comment.find("wp:comment_approved", namespaces).text == "1":
                comment_content = comment.find("wp:comment_content", namespaces).text
                comment_author = comment.find("wp:comment_author", namespaces).text
                comment_date = comment.find("wp:comment_date_gmt", namespaces).text
                comments.append(
                    {
                        "author": comment_author,
                        "date": comment_date,
                        "content": clean_html_content(comment_content or ""),
                    }
                )

        post_data = {
            "title": title,
            "link": item.find("link").text or "No Link",
            "author": authors.get(
                item.find("dc:creator", namespaces).text,
                f"Unknown Author ({item.find('dc:creator', namespaces).text})",
            ),
            "date": item.find("pubDate").text,
            "content": clean_html_content(content),
            "comments": comments,
        }

        posts.append(post_data)

    return posts if collect_only else None


def write_combined_markdown(domain_name, posts):
    """Write all posts for a domain to a single markdown file."""
    output_file = os.path.join(markdown_dir, f"{domain_name}.md")
    ensure_directories_exist(markdown_dir)

    with open(output_file, "w", encoding="utf-8") as f:
        for post in posts:
            # Write YAML frontmatter
            f.write("---\n")
            f.write(f"url: {post['link']}\n")
            f.write(f"title: {post['title']}\n")
            f.write(f"date_published: {format_date(post['date'])}\n")
            f.write(f"author: {post['author']}\n")
            f.write("---\n\n")

            # Write post content
            f.write(f"# {post['title']}\n\n")
            f.write(f"{post['content']}\n\n")

            # Write comments if present
            if post["comments"]:
                f.write("## Comments\n\n")
                for comment in post["comments"]:
                    f.write(f"**{comment['author']} - {comment['date']}**\n\n")
                    f.write(f"{comment['content']}\n\n")

            f.write("---\n\n")

    print(f"Created combined markdown file: {output_file}")


if __name__ == "__main__":
    process_all_wordpress_files()
