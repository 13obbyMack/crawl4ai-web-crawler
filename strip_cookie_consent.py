import os

# Directory containing your markdown files
output_dir = "./output"

# Define the phrases to look for
start_phrase = "By selecting"
end_phrases = ["targeted advertising", "less targeted advertising"]

# Count of files processed
processed_count = 0
failed_count = 0

# Process all markdown files in the directory
for filename in os.listdir(output_dir):
    if filename.endswith(".md"):
        file_path = os.path.join(output_dir, filename)
        
        try:
            # Read the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the start of the cookie consent text
            cookie_start_index = content.find(start_phrase)
            if cookie_start_index != -1:
                # Try to find the end of the cookie consent text
                for phrase in end_phrases:
                    end_index = content.find(phrase, cookie_start_index)
                    if end_index != -1:
                        # Calculate the full range to remove
                        end_index += len(phrase) + 1  # +1 for the period
                        
                        # Create new content by removing the cookie consent block
                        new_content = content[:cookie_start_index].rstrip() + content[end_index:].lstrip()
                        
                        # Write the cleaned content back to the file
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        processed_count += 1
                        print(f"Successfully processed {filename}")
                        break
                else:
                    failed_count = failed_count + 1
                    print(f"Could not find the end of the cookie consent text in {filename}")
            else:
                print(f"No cookie consent text found in {filename}")
        
        except Exception as e:
            failed_count = failed_count + 1
            print(f"Error processing {filename}: {str(e)}")

print(f"\nSummary: Successfully processed {processed_count} files, failed to process {failed_count} files.")