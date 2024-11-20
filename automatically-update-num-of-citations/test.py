from semanticscholar import SemanticScholar
sch = SemanticScholar()
paper = sch.get_paper('10.1093/mind/lix.236.433')
print(paper.title)