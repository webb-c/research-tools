# Research Tools

This repository support the various research helping tools.

- [automatically-update-num-of-citations](#automatically-update-num-of-citations)
- [get-citation-lists](#get-citation-lists)
- [sort-google-scholar](#sort-google-scholar)
- [search-good-paper](#search-good-paper)

<br>

## automatically-update-num-of-citations
> [!note]
> Save all reference lists to CSV file based on paper title (using semanticscholar)

#### Dependency
```bash
pip install semanticscholar
```

#### Useage
- `--input`: csv_file_path (CSV file **must** have a "Title" column.)
- `--output`: output_csv_file_path (*optional*)
- `--idx`: number of start row index (*optional*)

```bash
cd automatically-update-num-of-citations
python update_cite.py --input ${csv_file_path}
```

<br>

## search-good-paper
> [!note]
> Search papers by query or get paper recommendations based on paper ID (using semanticscholar)

#### Dependency
```bash
pip install semanticscholar
```

#### Useage
- `--query`: search query for search (*optional*)
- `--id`: paper id for recommendation (*optional*)
- `--limit`: number of paper (*optional*)

```bash
cd search-good-paper
python search.py --query ${search_query}
```

```bash
cd search-good-paper
python search.py --id ${paper_id}
```


<br>

## get-citation-lists
> [!note]
> Save papers ordered by citation count.

(reference: https://github.com/WittmannF/sort-google-scholar)

<br>

## sort-google-scholar
> [!note]
> Extract and save paper details (title, author, venue, year, citation count, bibtex) using paper titles from CSV file

<br>




