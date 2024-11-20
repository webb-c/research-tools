from semanticscholar import SemanticScholar
import argparse
from tabulate import tabulate


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=str, default=None)
    parser.add_argument("--query", type=str, default=None)
    parser.add_argument("--limit", type=int, default=10)
    
    args = parser.parse_args()
    sch = SemanticScholar()

    if args.query is not None:
        results = sch.search_paper(args.query, limit=args.limit)
        
        # 검색 결과를 테이블 형식으로 표시
        table_data = []
        for item in results.items:
            table_data.append([
                item.title,
                item.year,
                item.venue or "N/A",
                item.citationCount
            ])
        
        print("\n" + "="*100 + "\n")
        print(tabulate(
            table_data,
            headers=["Title", "Year", "Venue", "Citations"],
            tablefmt="grid",
            maxcolwidths=[50, 10, 20, 10]
        ))
        print("\n" + "="*100 + "\n")
            
    elif args.id is not None:
        results = sch.get_recommended_papers(args.id, limit=args.limit)
        
        # 추천 논문 목록을 테이블 형식으로 표시
        table_data = []
        for i, item in enumerate(results, 1):
            table_data.append([i, item.title])
            
        print("\n" + "="*80 + "\n")
        print("📚 Recommended Papers:")
        print(tabulate(
            table_data,
            headers=["No.", "Title"],
            tablefmt="grid",
            maxcolwidths=[5, 70]
        ))
        print("\n" + "="*80 + "\n")