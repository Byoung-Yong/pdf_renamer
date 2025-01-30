import streamlit as st
import requests
import re
import pyperclip

def clean_title(title):
    """Clean title while preserving spaces, letters, and removing <sub> tags."""
    if not title:
        return None
    
    # Remove <sub> and </sub> tags
    title = re.sub(r'</?sub>', '', title)
    
    # Keep letters, numbers, and spaces only
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    
    # Normalize whitespace
    cleaned = ' '.join(cleaned.strip().split())
    
    return cleaned[:100]  # Limit to 100 characters


def fetch_metadata(doi):
    if not doi:
        return None
    try:
        url = f'https://api.crossref.org/works/{doi}/transform/application/vnd.citationstyles.csl+json'
        response = requests.get(url)
        if response.status_code != 200:
            return None
        data = response.json()
        issued = data.get('issued', {}).get('date-parts', [[]])
        pub_year = str(issued[0][0]) if issued and issued[0] else None
        journal = data.get('container-title-short') or data.get('short-container-title')
        journal = journal[0] if isinstance(journal, list) else journal
        authors = data.get('author', [])
        corr_author = authors[0].get('family') if authors else None
        title = data.get('title', [''])[0] if isinstance(data.get('title'), list) else data.get('title')
        
        return {
            'year': pub_year,
            'journal': re.sub(r'[^\w\s]', '', str(journal)) if journal else None,  # Remove special characters
            'author': re.sub(r'[^\w\s]', '', str(corr_author)) if corr_author else None,
            'title': clean_title(str(title)) if title else None
        }
    except Exception as e:
        print(f"Error fetching metadata for {doi}: {str(e)}")
        return None

def main():
    st.title("DOI Metadata Fetcher")
    
    doi = st.text_input("Enter DOI:")
    
    if st.button("Get a new filename"):
        if doi:
            metadata = fetch_metadata(doi)
            if metadata:
                # Generate the filename
                filename = f"{metadata['year']}_{metadata['journal']}_{metadata['author']}_{metadata['title']}.pdf"
                
                # Display the extracted information
                st.subheader("Paper Information:sunglasses:", divider="green")
                st.write( 
                            f"**Publication Year:** {metadata['year'] or 'N/A'}  \n"
                            f"**Journal Name:** {metadata['journal'] or 'N/A'}  \n"
                            f"**Corresponding Author:** {metadata['author'] or 'N/A'}  \n"
                            f"**Title:** {metadata['title'] or 'N/A'}", ) 
                st.subheader("New filename:")
                st.code(filename)
                pyperclip.copy(filename)

      
            else:
                st.error("Metadata not found.")
        else:
            st.error("Please enter a DOI.")

if __name__ == "__main__":
    main()

# 10.1039/d3ay00382e