#by GPT4 20240313
import pandas as pd
import os
from markdown2 import markdown  # For converting text to Markdown, if necessary
import re

# Create the 'dida' directory if it doesn't exist
output_dir = '/output'
os.makedirs(output_dir, exist_ok=True)

# Read the CSV file, skipping the initial informational lines
dida_records = pd.read_csv('*.csv', skiprows=3)

# Filter out records with empty 'Content'
filtered_records = dida_records[dida_records['Content'].notna()]

# Function to sanitize file names (remove invalid characters)
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', '', name)  # Remove characters that are not allowed in file names

def create_markdown_files_without_ids(records, directory, max_title_length=100, max_total_length=255):
    successful_files = 0
    title_content_dict = {}

    # Helper function to remove emojis and non-text symbols from a string
    def remove_emojis(text):
        return re.sub(r'[^\w\s,]', '', text)  # Keep letters, numbers, whitespaces, and commas

    # Group and merge contents by title
    for _, row in records.iterrows():
        title = row['Title'] if pd.notna(row['Title']) else "Untitled"
        # Append new contents or create new title entries
        if title in title_content_dict:
            if row['Content'] not in title_content_dict[title]['contents']:
                title_content_dict[title]['contents'].append(row['Content'])
        else:
            title_content_dict[title] = {
                'row': row,
                'contents': [row['Content']] if pd.notna(row['Content']) else []
            }

    # Create Markdown files for each title
    for title, info in title_content_dict.items():
        row = info['row']
        contents = '\n\n'.join(info['contents'])

        # Construct and sanitize the file name
        sanitized_title = sanitize_filename(title)
        truncated_title = sanitized_title[:max_title_length] if len(sanitized_title) > max_title_length else sanitized_title
        file_name = f"{truncated_title}.md"
        if len(file_name) > max_total_length:
            file_name = file_name[:max_total_length - 4] + '.md'
        file_path = os.path.join(directory, file_name)

        # Build content without emojis in folder and list names
        folder_name = remove_emojis(row['Folder Name']) if pd.notna(row['Folder Name']) else ""
        list_name = remove_emojis(row['List Name']) if pd.notna(row['List Name']) else ""
        tag_line = f"#{folder_name.replace(' ', '')}/{list_name.replace(' ', '')}" if folder_name or list_name else ""

        # Combine markdown content
        content_lines = [
            contents if contents else "",
            tag_line
        ]
        md_content = '\n\n'.join(filter(None, content_lines))  # Combine non-empty lines

        # Write the markdown content to a file
        if md_content.strip():
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(md_content)
                successful_files += 1
            except Exception:
                continue  # Handle exceptions silently

    return successful_files, len(title_content_dict)  # Return the counts of created files and titles

# Apply the function without IDs in file names
total_files_without_ids, unique_titles_without_ids = create_markdown_files_without_ids(filtered_records, output_dir)
total_files_without_ids, unique_titles_without_ids
