from semanticscholar import SemanticScholar
import pandas as pd
import requests
import argparse
import time
from urllib.parse import urlparse
import re

def normalize_title(title):
    """제목을 소문자로 변환하고, 특수 문자를 제거하여 정규화합니다.
    """
    if not isinstance(title, str):
        return ''
    title = title.lower()
    title = re.sub(r'[^a-z0-9\s]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title


def extract_doi(url):
    doi_pattern = r'10.\d{4,9}/[-._;()/:A-Z0-9]+'
    match = re.search(doi_pattern, url, re.IGNORECASE)
    if match:
        return match.group(0)
    return None



def get_paper_info_by_title(title):
    sch = SemanticScholar()
    results = sch.search_paper(title, limit=1, fields=['title','year','authors','url','citationStyles', 'paperId', 'citationCount', 'publicationVenue'])
    if normalize_title(results[0].title) != normalize_title(title):
        print(f"title mismatch: {title} != {results[0].title}")
        return 
    
    paper = results[0]
    return paper
    
    
def make_row_from_info(paper):
    
    authors = [item.name for item in paper.authors]

    return {
        'Title': paper.title,
        'Authors': authors,
        'Venue': paper.publicationVenue['name'],
        'Year': paper.year,
        'CitationCount': paper.citationCount,
        'URL': paper.url,
        'Bibtex': paper.citationStyles["bibtex"],
        'paperId': paper.paperId,
    }
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='data/papers.csv')
    parser.add_argument('--output', type=str, default=None)
    args = parser.parse_args()
    
    if args.output is None:
        args.output = args.input
    
    INPUT_FILE = args.input
    OUTPUT_FILE = args.output
    
    # Semantic Scholar API 기본 URL
    API_URL = "https://api.semanticscholar.org/graph/v1/paper/"
    
    if INPUT_FILE.endswith('.csv'):
        df = pd.read_csv(INPUT_FILE)
    elif INPUT_FILE.endswith(('.xls', '.xlsx')):
        df = pd.read_excel(INPUT_FILE)
    else:
        raise ValueError("지원되지 않는 파일 형식입니다. CSV 또는 엑셀 파일을 사용하세요.")

    if 'CitationCount' not in df.columns:
        df['CitationCount'] = None
    
    for index, row in df.iterrows():
        paper_title = row['Title']
    
        try:
            paper = get_paper_info_by_title(paper_title)
            paper_info = make_row_from_info(paper)
            print(f"index {index}: '{paper_info['Title']}' citation count = {paper_info['CitationCount']}")
            
            for key in paper_info.keys():
                if key in df.columns:
                    value = paper_info[key]
                    if isinstance(value, list):
                        value = ', '.join(value)
                    if df.at[index, key] is None:
                        df.at[index, key] = value
                
        except Exception as e:
            print(f"Error processing paper '{paper_title}': {str(e)}")

    if OUTPUT_FILE.endswith('.csv'):
        df.to_csv(OUTPUT_FILE, index=False)
    elif OUTPUT_FILE.endswith(('.xls', '.xlsx')):
        df.to_excel(OUTPUT_FILE, index=False)
    else:
        raise ValueError("file type error")

    print("citation count update completed")