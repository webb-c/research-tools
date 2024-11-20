from semanticscholar import SemanticScholar
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=str, default=None)
    parser.add_argument("--query", type=str, default=None)
    parser.add_argument("--limit", type=int, default=10)
    
    args = parser.parse_args()

    sch = SemanticScholar()
    
    if args.query is not None:
        results = sch.search_paper(args.query, limit=args.limit)
        for item in results.items:
            print(f"{item.title} is published in {item.year}, {item.venue}.\nwith citation count {item.citationCount}")
            print()
            
        for item in results.items:
            print(item.title)
            
    elif args.id is not None:
        results = sch.get_recommended_papers(args.id, limit=args.limit)
        for item in results:
            print(item.title)
