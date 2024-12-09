import pybtex.database
# from pathlib import Path
import datetime

preamble = """
<style>
.toggle-link {
  cursor: pointer;
  color: blue;
  text-decoration: underline;
}

.hidden-code {
  display: none;
  background-color: #f4f4f4;
  padding: 10px;
  margin-top: 5px;
  border-radius: 4px;
  position: relative;
}

.hidden-code.visible {
  display: block;
}

.copy-code-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  background-color: #e0e0e0;
  border: none;
  border-radius: 3px;
  padding: 3px 8px;
  cursor: pointer;
  font-size: 0.8em;
  display: none;
  transition: background-color 0.3s ease;
}

.hidden-code.visible .copy-code-btn {
  display: block;
}

.copy-code-btn:hover {
  background-color: #d0d0d0;
}

.copy-code-btn.copied {
  background-color: #90ee90;
}
</style>

<script>
function toggleCodeBlock(linkId, codeBlockId) {
  const codeBlock = document.getElementById(codeBlockId);
  codeBlock.classList.toggle('visible');
}

function copyCodeBlock(btnElement, codeBlockId) {
  // Select the <code> element inside the pre block
  const codeElement = document.querySelector(`#${codeBlockId} code`);
  
  if (codeElement) {
    // Extract the text content
    const codeText = codeElement.textContent;
    
    // Copy to clipboard
    navigator.clipboard.writeText(codeText).then(() => {
      // Change button text and style
      btnElement.textContent = 'Copied!';
      btnElement.classList.add('copied');
      
      // Revert back after 2 seconds
      setTimeout(() => {
        btnElement.textContent = 'Copy';
        btnElement.classList.remove('copied');
      }, 2000);
    }).catch(err => {
      console.error('Failed to copy: ', err);
    });
  }
}
</script>"""


def render(name):
    x = ' '.join(name.first_names + name.middle_names + name.prelast_names + name.last_names + name.lineage_names).strip()
    if x == "Alexander Ek":
        x = "**Alexander Ek**"
    return x


def categorize_publications(bib_file):
    """
    Read a .bib file and categorize publications.
    
    Args:
        bib_file (str): Path to the .bib file
    
    Returns:
        dict: Categorized publications
    """
    # Load the BibTeX database
    bib_data = pybtex.database.parse_file(bib_file)
    
    # Define publication categories
    categories = {
        'peer-reviewed_conference_publications': ['inproceedings', 'conference'],
        'journal_publications': ['article'],
        'theses': ['phdthesis', 'mastersthesis', 'thesis'],
        'book_chapters': ['incollection', 'book'],
        'workshops_and_symposia': ['unpublished'],
        'science_journalism': ['online'],
        'other': []
    }


    # Categorize publications
    categorized_pubs = {cat: [] for cat in categories}
    
    for entry_key, entry in bib_data.entries.items():
        
        publication_data = {
            'key': entry_key,
            'title': entry.fields.get('title', 'Untitled'),
            'authors': [render(name) for name in entry.persons['author']],
            'year': entry.fields.get('year', 'N/A'),
            'venue': entry.fields.get('journal', 
                        entry.fields.get('booktitle', '')),
            'publisher': entry.fields.get('publisher', ''),
            'series': entry.fields.get('series', ''),
            'volume': entry.fields.get('volume', ''),
            'pages': entry.fields.get('pages', ''),
            'doi': entry.fields.get('doi', ''),
            'url': entry.fields.get('url', ''),
            'note': entry.fields.get('note', ''),
            'type': entry.fields.get('type', ''),
            'school': entry.fields.get('school', ''),
            'bib': entry.to_string('bibtex').replace(r"\_", "_")
        }

        # Determine the category
        for cat, types in categories.items():
            if entry.type.lower() in types:
                categorized_pubs[cat].append(publication_data)
                break
        else:  # else branch of for-loop, not executed if for loop breaks
            categorized_pubs['other'].append(publication_data)
    
    # Sort publications within each category by year (descending)
    for cat in categorized_pubs:
        categorized_pubs[cat] = sorted(
            categorized_pubs[cat], 
            key=lambda x: x['year'], 
            reverse=True
        )
    
    return categorized_pubs

def generate_publications_page(bib_file, output_file='publications.qmd'):
    """
    Generate a Quarto markdown file with publications.
    
    Args:
        bib_file (str): Path to the .bib file
        output_file (str): Path to the output Quarto markdown file
    """
    # Categorize publications
    pubs = categorize_publications(bib_file)
    
    # Start building the Quarto markdown content
    content = []
    content.append('---')
    content.append('pagetitle: "Alexander Ek - News"')
    content.append('---')
    content.append(f'\nUpdated {datetime.date.today().strftime("%d %b %Y")}\n')
    content.append(preamble)
    
    # Generate sections for each category
    for category, publications in pubs.items():
        if not publications:
            continue
        
        # Convert category name to title case
        category_title = category.replace('_', ' ').title()
        
        content.append(f'### {category_title}\n')
        if "Conference" in category_title:
            content.append('*In computer science, the most important publication venues are generally conferences.*\n')
        if "Workshop" in category_title:
            content.append('*Papers later published in conferences or journals are listed with the publication entry above.*\n')
        
        # Generate bibliography entries
        for pub in publications:
            # Format authors
            authors = ', '.join(pub['authors'])
            
            # Start bibliography entry
            entry = f'{authors}. '
            entry += f'"{pub["title"].replace("{","").replace("}","")}". '

            if category == 'theses':    
                if pub['type']:
                    entry += f'*{pub["type"]}*. '
                if pub['school']:
                    entry += f'{pub["school"]}, '

            # Add what is available of venue, series, volume, publisher
            if pub['venue']:
                entry += f'In: *{pub["venue"].replace("{","").replace("}","")}*. '
            if pub['series']:
                entry += f'{pub["series"]}'
                if pub['volume']:
                    entry += f' vol. {pub["volume"]}'
                entry += f'. '
            if pub['publisher']:
                entry += f'{pub["publisher"].replace("{","").replace("}","")}, '

            # Add year and (if available) pages
            entry += f'{pub["year"]}'
            if pub['pages']:
                if "p" in pub['pages']:
                    entry += f', {pub["pages"]}'
                elif "-" in pub['pages']:
                    entry += f', pp. {pub["pages"]}'
                else:
                    entry += f', p. {pub["pages"]}'
            entry += f". "

            # Add note
            if pub['note']:
                entry += f'{pub["note"]}. '

            # Add DOI or URL if available
            if pub['doi']:
                entry += f'DOI: [{pub["doi"]}](https://doi.org/{pub["doi"]}). '
            elif pub['url']:
                entry += f'[Link]({pub["url"]}). '
            
            # entry += f'[bib]({pub["bib"]})'

            bib_button = f"""<span class="toggle-link" onclick="toggleCodeBlock('link-{pub['key']}', 'code-block-{pub['key']}')">bib</span>"""

            bib_block = f"""<div class="hidden-code" id="code-block-{pub['key']}"><button class="copy-code-btn" onclick="copyCodeBlock(this, 'code-block-{pub['key']}')">Copy</button><pre><code>{pub['bib']}</code></pre></div>"""
            
            content.append('::: {.hanging-indent .justify}\n' + entry + f'\n{bib_button}\n:::\n{bib_block}\n')
        
        content.append('\ \n')
        
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    print(f"Publications page generated: {output_file}")

# Example usage
if __name__ == '__main__':
    generate_publications_page('references.bib')
