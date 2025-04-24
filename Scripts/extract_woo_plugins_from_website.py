"""
WooCommerce Website Analyzer

This script analyzes WooCommerce-powered websites to detect plugins, themes, and custom functionality.
It crawls multiple pages on the site to build a comprehensive picture of the technologies used.

Features:
- Detects WooCommerce plugins from script and style references
- Identifies themes and child themes
- Discovers custom post types and taxonomies
- Analyzes HTML structure for plugin-specific patterns
- Detects custom functionality through data attributes and AJAX calls
- Examines REST API endpoints
- Identifies Gutenberg blocks and shortcodes
- Saves a detailed report for client presentations

Usage:
    python extract_woo_plugins_from_website.py https://example.com [pages_to_crawl]

Arguments:
    url - Target website URL
    pages_to_crawl - (Optional) Number of pages to crawl (default: 5)

Output:
    Creates a detailed report in the console and optionally saves to a file
"""

import requests
from bs4 import BeautifulSoup
import re
import argparse
import sys
import json
import time
from urllib.parse import urljoin, urlparse
from collections import defaultdict

# Initialize session for maintaining cookies
session = requests.Session()

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


class WooCommerceAnalyzer:
    def __init__(self, base_url, max_pages=5, verbose=False):
        self.base_url = base_url
        self.max_pages = max_pages
        self.verbose = verbose
        self.visited_urls = set()
        self.plugins_detected = set()
        self.themes_detected = set()
        self.main_theme = None
        self.child_theme = None
        self.custom_post_types = set()
        self.shortcodes = set()
        self.rest_endpoints = set()
        self.custom_data_attributes = set()
        self.ajax_calls = set()
        self.gutenberg_blocks = set()
        self.custom_code_indicators = []
        self.css_classes = set()
        # Regex patterns for WordPress directories (standard and non-standard)
        self.plugin_path_patterns = [
            r"/wp-content/plugins/([^/]+)/",  # Standard WP
            r"/app/plugins/([^/]+)/",  # Non-standard like popsigns.co
            r"/plugins/([^/]+)/",  # Another variant
            r"/wp/plugins/([^/]+)/",  # Another variant
        ]
        self.theme_path_patterns = [
            r"/wp-content/themes/([^/]+)/",  # Standard WP
            r"/app/themes/([^/]+)/",  # Non-standard like popsigns.co
            r"/themes/([^/]+)/",  # Another variant
            r"/wp/themes/([^/]+)/",  # Another variant
        ]
        # Known plugins with their descriptions (for better reporting)
        self.known_plugins = {
            "woocommerce": "WooCommerce - Core eCommerce functionality",
            "jetpack": "Jetpack - Security, performance, and marketing tools",
            "gravityforms": "Gravity Forms - Advanced forms and submissions",
            "elementor": "Elementor - Page builder",
            "js_composer": "WPBakery Page Builder (formerly Visual Composer)",
            "wp-super-cache": "WP Super Cache - Caching plugin",
            "w3-total-cache": "W3 Total Cache - Performance optimization",
            "akismet": "Akismet - Spam protection",
            "contact-form-7": "Contact Form 7 - Form handling",
            "wordpress-seo": "Yoast SEO - Search engine optimization",
            "revslider": "Revolution Slider - Slider plugin",
            "wc-product-bundles": "WooCommerce Product Bundles - Create bundles and composite products",
            "woocommerce-gateway-stripe": "WooCommerce Stripe Gateway - Payment processing",
            "woocommerce-gateway-paypal-express-checkout": "WooCommerce PayPal Checkout Gateway",
            "wc-ajax-product-filter": "AJAX Product Filters for WooCommerce",
            "wc-quantity-plus-minus-buttons": "Quantity Plus Minus Buttons for WooCommerce",
            "woocommerce-composite-products": "WooCommerce Composite Products",
            "woocommerce-bookings": "WooCommerce Bookings - Booking system",
            "woocommerce-subscriptions": "WooCommerce Subscriptions - Subscription functionality",
            "woocommerce-product-addons": "WooCommerce Product Add-ons",
            "woocommerce-photography": "WooCommerce Photography - Photo selling features",
            "woocommerce-memberships": "WooCommerce Memberships - Membership functionality",
            "klaviyo": "Klaviyo - Email marketing integration",
            "mailchimp-for-woocommerce": "Mailchimp for WooCommerce - Email marketing",
            "woocommerce-shipstation-integration": "WooCommerce ShipStation Integration",
            "woocommerce-square": "WooCommerce Square - Payment and POS integration",
            "ups-woocommerce-shipping": "UPS WooCommerce Shipping - Shipping integration",
            "woocommerce-gateway-authorize-net-cim": "Authorize.net Payment Gateway",
            "woocommerce-advanced-shipping": "WooCommerce Advanced Shipping - Complex shipping rules",
        }

    def fetch_page(self, url):
        """Fetch a page and return the BeautifulSoup object"""
        if url in self.visited_urls:
            return None

        try:
            if self.verbose:
                print(f"Fetching: {url}")
            response = session.get(url, headers=HEADERS, timeout=10)
            self.visited_urls.add(url)

            if response.status_code != 200:
                print(
                    f"Warning: Unable to access {url}. Status code: {response.status_code}"
                )
                return None

            return BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None

    def extract_links(self, soup, current_url):
        """Extract internal links from the page"""
        internal_links = []
        domain = urlparse(self.base_url).netloc

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            full_url = urljoin(current_url, href)

            # Skip external links, anchors, and non-HTTP(S) links
            if (
                urlparse(full_url).netloc != domain
                or href.startswith("#")
                or not full_url.startswith(("http://", "https://"))
            ):
                continue

            # Skip already visited URLs
            if full_url in self.visited_urls:
                continue

            internal_links.append(full_url)

        return internal_links

    def detect_plugins_from_html(self, soup, url):
        """Detect plugins from script and link tags"""
        # Get all script and link tags
        all_scripts = soup.find_all("script", src=True)
        all_links = soup.find_all("link", href=True)

        # Check for plugins in script tags
        for script in all_scripts:
            src = script["src"]
            self._check_asset_for_plugin(src)

            # Additional check for script IDs that might reveal plugins
            if script.get("id"):
                script_id = script.get("id")
                if "-js" in script_id:
                    potential_plugin = script_id.replace("-js", "")
                    if potential_plugin in self.known_plugins:
                        self.plugins_detected.add(
                            (potential_plugin, f"Script ID: {script_id}")
                        )

        # Check for plugins in link tags
        for link in all_links:
            href = link["href"]
            self._check_asset_for_plugin(href)

            # Additional check for link IDs that might reveal plugins
            if link.get("id"):
                link_id = link.get("id")
                if "-css" in link_id:
                    potential_plugin = link_id.replace("-css", "")
                    if potential_plugin in self.known_plugins:
                        self.plugins_detected.add(
                            (potential_plugin, f"Link ID: {link_id}")
                        )

        # Check for plugin-specific CSS classes
        for tag in soup.find_all(class_=True):
            classes = tag.get("class", [])
            for css_class in classes:
                self.css_classes.add(css_class)

                # Look for plugin-specific class patterns
                plugin_patterns = [
                    r"^wc-",  # WooCommerce
                    r"^yith-",  # YITH plugins
                    r"^elementor-",  # Elementor
                    r"^wp-block-",  # Gutenberg blocks
                    r"^et_",  # Divi
                    r"^fl-",  # Beaver Builder
                ]

                for pattern in plugin_patterns:
                    if re.match(pattern, css_class):
                        self._add_potential_plugin_from_pattern(pattern, css_class)

        # Check HTML comments for plugin footprints
        comments = soup.find_all(
            string=lambda text: isinstance(text, str)
            and text.strip().startswith("<!--")
        )
        for comment in comments:
            if "plugin" in comment.lower():
                self.custom_code_indicators.append(
                    f"HTML Comment: {comment.strip()[:100]}"
                )
                # Extract plugin name from comment if possible
                plugin_name_match = re.search(
                    r"plugin ['\"](.*?)['\"]", comment.lower()
                )
                if plugin_name_match:
                    self.plugins_detected.add(
                        (plugin_name_match.group(1), f"Comment: {comment[:50]}...")
                    )

        # Check for Gutenberg blocks
        gutenberg_patterns = [
            div
            for div in soup.find_all("div")
            if div.get("class")
            and any("wp-block-" in cls for cls in div.get("class", []))
        ]
        for block in gutenberg_patterns:
            block_name = [
                cls for cls in block.get("class", []) if cls.startswith("wp-block-")
            ]
            if block_name:
                self.gutenberg_blocks.add(block_name[0])

        # Check for custom post types in URLs
        links = soup.find_all("a", href=True)
        for link in links:
            href = link["href"]
            post_type_match = re.search(r"/([a-z0-9-_]+)/[a-z0-9-_]+/?$", href)
            if post_type_match and post_type_match.group(1) not in [
                "category",
                "tag",
                "product",
                "post",
                "page",
            ]:
                self.custom_post_types.add(post_type_match.group(1))

        # Check meta tags for plugin hints
        meta_tags = soup.find_all("meta")
        for meta in meta_tags:
            if meta.get("name") and "generator" in meta.get("name"):
                content = meta.get("content", "")
                if "plugin" in content.lower():
                    self.plugins_detected.add((content, "Meta Generator Tag"))

        # Direct HTML examination for certain plugin signatures
        # WooCommerce cart fragments
        if soup.find("div", {"class": "widget_shopping_cart_content"}):
            self.plugins_detected.add(("woocommerce", "Shopping Cart Widget"))

        # Check for WooCommerce product gallery
        if soup.find("div", {"class": "woocommerce-product-gallery"}):
            self.plugins_detected.add(("woocommerce", "Product Gallery"))

    def _check_asset_for_plugin(self, asset_url):
        """Check if an asset URL contains plugin references"""
        # Check for plugins using different possible path patterns
        for pattern in self.plugin_path_patterns:
            plugin_match = re.search(pattern, asset_url)
            if plugin_match:
                plugin_name = plugin_match.group(1)
                self.plugins_detected.add((plugin_name, asset_url))
                # If it's a custom plugin that contains the site name, mark as custom
                if "pop" in plugin_name.lower() or "sign" in plugin_name.lower():
                    self.custom_code_indicators.append(f"Custom Plugin: {plugin_name}")
                break

        # Check for themes using different possible path patterns
        for pattern in self.theme_path_patterns:
            theme_match = re.search(pattern, asset_url)
            if theme_match:
                theme_name = theme_match.group(1)
                self.themes_detected.add((theme_name, asset_url))

                # Check if it's a child theme
                if "-child" in theme_name:
                    parent_theme = theme_name.replace("-child", "")
                    if not any(
                        parent_theme == name for name, _ in self.themes_detected
                    ):
                        self.themes_detected.add(
                            (
                                parent_theme,
                                "Parent theme detected via child theme reference",
                            )
                        )
                break

    def _add_potential_plugin_from_pattern(self, pattern, css_class):
        """Add a potential plugin based on a CSS class pattern"""
        pattern_to_plugin = {
            r"^wc-": "WooCommerce",
            r"^yith-": "YITH Plugin",
            r"^elementor-": "Elementor",
            r"^wp-block-": "Gutenberg",
            r"^et_": "Divi",
            r"^fl-": "Beaver Builder",
        }

        if pattern in pattern_to_plugin:
            self.plugins_detected.add(
                (pattern_to_plugin[pattern], f"CSS Class: {css_class}")
            )

    def detect_custom_functionality(self, soup):
        """Detect potential custom functionality"""
        # Check for data attributes
        for tag in soup.find_all():
            for attr in tag.attrs:
                if attr.startswith("data-"):
                    # Exclude common plugin data attributes to focus on custom ones
                    if not any(
                        x in attr for x in ["elementor", "woocommerce", "product"]
                    ):
                        self.custom_data_attributes.add(f"{attr}={tag[attr]}")

        # Check for AJAX calls
        for script in soup.find_all("script"):
            script_text = script.text
            if script.string:
                # Look for admin-ajax.php usage
                if "admin-ajax.php" in script_text:
                    ajax_action = re.search(r"action=(['\"])([^'\"]+)\\1", script_text)
                    if ajax_action:
                        self.ajax_calls.add(f"AJAX action: {ajax_action.group(2)}")
                    else:
                        self.ajax_calls.add(
                            script_text.strip()[:100] + "..."
                            if len(script_text) > 100
                            else script_text
                        )

                # Look for WP REST API calls
                if "/wp-json/" in script_text:
                    rest_endpoint = re.search(
                        r"/wp-json/([^/\"']+)/([^/\"']+)", script_text
                    )
                    if rest_endpoint:
                        self.rest_endpoints.add(
                            f"{rest_endpoint.group(1)}/{rest_endpoint.group(2)}"
                        )

                # Look for shortcodes
                shortcode_matches = re.findall(
                    r"\[([a-zA-Z0-9_-]+)(?:\s+[^\]]+)?\]", script_text
                )
                for shortcode in shortcode_matches:
                    self.shortcodes.add(shortcode)

        # Look for inline JSON data (often used by plugins to pass data to JavaScript)
        for script in soup.find_all("script", {"type": "application/json"}):
            try:
                script_text = script.string
                if script_text:
                    json_data = json.loads(script_text)
                    self.custom_code_indicators.append(
                        f"JSON data block: {str(json_data)[:100]}..."
                    )
            except:
                pass

        # Look for script blocks with inline JavaScript that's not library code
        for script in soup.find_all("script"):
            if (
                script.get("src") is None
                and script.string
                and len(script.string.strip()) > 0
            ):
                # Skip if it looks like a common library
                script_text = script.string.strip()
                if (
                    len(script_text) > 100
                    and not "jQuery" in script_text[:100]
                    and not "function(" in script_text[:100]
                ):
                    self.custom_code_indicators.append(
                        f"Custom JS: {script_text[:100]}..."
                    )

    def analyze_site(self):
        """Main method to analyze the site"""
        if not self.base_url.startswith(("http://", "https://")):
            self.base_url = "https://" + self.base_url

        # Start with the homepage
        urls_to_visit = [self.base_url]
        pages_visited = 0

        while urls_to_visit and pages_visited < self.max_pages:
            current_url = urls_to_visit.pop(0)
            soup = self.fetch_page(current_url)

            if not soup:
                continue

            pages_visited += 1
            print(f"Analyzing page {pages_visited}/{self.max_pages}: {current_url}")

            # Extract data from this page
            self.detect_plugins_from_html(soup, current_url)
            self.detect_custom_functionality(soup)

            # Get more internal links to visit
            if pages_visited < self.max_pages:
                new_links = self.extract_links(soup, current_url)
                urls_to_visit.extend(new_links[: self.max_pages - pages_visited])

        # Try to determine main theme vs child theme
        theme_names = [name for name, _ in self.themes_detected]
        if len(theme_names) == 1:
            self.main_theme = theme_names[0]
        elif len(theme_names) > 1:
            # Look for child theme specifically
            child_themes = [name for name in theme_names if "-child" in name]
            if child_themes:
                self.child_theme = child_themes[0]
                parent_theme = self.child_theme.replace("-child", "")
                if parent_theme in theme_names:
                    self.main_theme = parent_theme
                else:
                    # If parent not found, use the first non-child theme
                    non_child_themes = [
                        name for name in theme_names if "-child" not in name
                    ]
                    if non_child_themes:
                        self.main_theme = non_child_themes[0]
                    else:
                        self.main_theme = theme_names[0]
            else:
                # No child theme detected, assume first is main
                self.main_theme = theme_names[0]
                if len(theme_names) > 1:
                    self.child_theme = theme_names[1]

    def generate_report(self, save_to_file=False):
        """Generate and optionally save a report of findings"""
        report = "\n🔍 **WooCommerce Website Analysis Report** 🔍\n"
        report += f"\nTarget Website: {self.base_url}"
        report += f"\nPages Analyzed: {len(self.visited_urls)}"

        # Plugins section
        if self.plugins_detected:
            report += "\n\n✅ **Detected Plugins:**"
            plugin_dict = defaultdict(list)
            for plugin, source in self.plugins_detected:
                plugin_dict[plugin].append(source)

            # Sort plugins alphabetically but with WooCommerce first
            sorted_plugins = sorted(plugin_dict.keys())
            if "woocommerce" in sorted_plugins:
                sorted_plugins.remove("woocommerce")
                sorted_plugins.insert(0, "woocommerce")

            for plugin in sorted_plugins:
                sources = plugin_dict[plugin]
                # Add description for known plugins
                if plugin.lower() in self.known_plugins:
                    report += f"\n- {plugin} - {self.known_plugins[plugin.lower()]}"
                else:
                    report += f"\n- {plugin}"

                if self.verbose:
                    for source in sources[:3]:  # Limit to 3 sources to avoid clutter
                        report += f"\n  - Found in: {source}"
        else:
            report += "\n\n❌ No plugins were detected from front-end assets."

        # Theme section
        if self.themes_detected:
            report += "\n\n🎨 **Detected Theme:**"
            if self.main_theme:
                report += f"\n- Main Theme: {self.main_theme}"
            if self.child_theme:
                report += f"\n- Child Theme: {self.child_theme}"

            if self.verbose:
                report += "\n\nTheme Assets:"
                for theme, asset in self.themes_detected:
                    report += f"\n- {asset}"
        else:
            report += "\n\n❌ No WordPress theme detected."

        # Custom plugins section
        custom_plugins = [
            item for item in self.custom_code_indicators if "Custom Plugin:" in item
        ]
        if custom_plugins:
            report += "\n\n🛠️ **Custom Plugins Detected:**"
            for plugin in custom_plugins:
                report += f"\n- {plugin.replace('Custom Plugin: ', '')}"

        # Gutenberg blocks
        if self.gutenberg_blocks:
            report += "\n\n📦 **Detected Gutenberg Blocks:**"
            for block in self.gutenberg_blocks:
                report += f"\n- {block}"

        # Custom post types
        if self.custom_post_types:
            report += "\n\n📋 **Detected Custom Post Types:**"
            for post_type in self.custom_post_types:
                report += f"\n- {post_type}"

        # REST API endpoints
        if self.rest_endpoints:
            report += "\n\n🔌 **Detected REST API Endpoints:**"
            for endpoint in self.rest_endpoints:
                report += f"\n- wp-json/{endpoint}"

        # Shortcodes
        if self.shortcodes:
            report += "\n\n🧩 **Detected Shortcodes:**"
            for shortcode in self.shortcodes:
                report += f"\n- [{shortcode}]"

        # Custom functionality section
        report += "\n\n⚡ **Potential Custom Functionality:**"

        if self.custom_data_attributes:
            report += "\n\nCustom Data Attributes:"
            for attr in list(self.custom_data_attributes)[:10]:  # Limit to 10
                report += f"\n- {attr}"
            if len(self.custom_data_attributes) > 10:
                report += f"\n- ... and {len(self.custom_data_attributes) - 10} more"

        if self.ajax_calls:
            report += "\n\nAJAX Calls (Potential Custom Features):"
            for ajax in self.ajax_calls:
                report += f"\n- {ajax}"

        custom_code_without_plugins = [
            item for item in self.custom_code_indicators if "Custom Plugin:" not in item
        ]
        if custom_code_without_plugins:
            report += "\n\nOther Custom Code Indicators:"
            for indicator in custom_code_without_plugins[:5]:  # Limit to 5
                report += f"\n- {indicator}"
            if len(custom_code_without_plugins) > 5:
                report += f"\n- ... and {len(custom_code_without_plugins) - 5} more"

        # CSS classes for identifying plugins
        if self.verbose and self.css_classes:
            report += "\n\n🔍 **Interesting CSS Classes:**"
            plugin_specific_classes = [
                cls
                for cls in self.css_classes
                if any(
                    cls.startswith(prefix)
                    for prefix in ["wc-", "yith-", "elementor-", "wp-block-"]
                )
            ]
            for cls in plugin_specific_classes[:20]:  # Limit to 20
                report += f"\n- {cls}"
            if len(plugin_specific_classes) > 20:
                report += f"\n- ... and {len(plugin_specific_classes) - 20} more"

        report += "\n\n🚀 **Analysis Complete!** 🚀"

        # Save report to file if requested
        if save_to_file:
            filename = f"woocommerce_analysis_{urlparse(self.base_url).netloc}_{int(time.time())}.txt"
            with open(filename, "w") as f:
                f.write(report)
            print(f"\nReport saved to {filename}")

        return report


def main():
    parser = argparse.ArgumentParser(description="WooCommerce Website Analyzer")
    parser.add_argument("url", help="Target website URL")
    parser.add_argument(
        "--pages", type=int, default=5, help="Number of pages to crawl (default: 5)"
    )
    parser.add_argument("--save", action="store_true", help="Save report to file")
    parser.add_argument(
        "--verbose", action="store_true", help="Show detailed information"
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    print(f"Starting analysis of {args.url}...")
    print(f"Will crawl up to {args.pages} pages.")

    analyzer = WooCommerceAnalyzer(args.url, max_pages=args.pages, verbose=args.verbose)
    analyzer.analyze_site()
    report = analyzer.generate_report(save_to_file=args.save)

    print(report)


if __name__ == "__main__":
    main()
