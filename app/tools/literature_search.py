import time
from typing import List, Dict
from urllib.parse import urlencode
from urllib.request import urlopen
import xml.etree.ElementTree as ET

from app.utils.config import get_env_variable


NCBI_EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def _build_common_params() -> Dict[str, str]:
    tool = get_env_variable("NCBI_TOOL", "cardiology_agent")
    email = get_env_variable("NCBI_EMAIL", "developer@example.com")
    return {
        "tool": tool,
        "email": email,
    }


def _esearch_pubmed(query: str, retmax: int = 8) -> List[str]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "xml",
        "retmax": str(retmax),
        "sort": "relevance",
        **_build_common_params(),
    }
    url = NCBI_EUTILS_BASE + "esearch.fcgi?" + urlencode(params)

    with urlopen(url, timeout=20) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    id_list = root.find("IdList")
    if id_list is None:
        return []

    return [elem.text for elem in id_list.findall("Id") if elem.text]


def _esummary_pubmed(pubmed_ids: List[str]) -> List[Dict[str, str]]:
    if not pubmed_ids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "xml",
        **_build_common_params(),
    }
    url = NCBI_EUTILS_BASE + "esummary.fcgi?" + urlencode(params)

    with urlopen(url, timeout=20) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    results = []

    for docsum in root.findall(".//DocSum"):
        article = {
            "title": "",
            "pubdate": "",
            "source": "",
            "authors": "",
            "pubmed_id": "",
        }

        uid_elem = docsum.find("Id")
        if uid_elem is not None and uid_elem.text:
            article["pubmed_id"] = uid_elem.text

        for item in docsum.findall("Item"):
            name = item.attrib.get("Name", "")
            value = item.text or ""

            if name == "Title":
                article["title"] = value
            elif name == "PubDate":
                article["pubdate"] = value
            elif name == "Source":
                article["source"] = value
            elif name == "AuthorList":
                authors = [child.text for child in item.findall("Item") if child.text]
                article["authors"] = ", ".join(authors[:3])

        results.append(article)

    return results


def _efetch_pubmed_abstracts(pubmed_ids: List[str]) -> Dict[str, str]:
    if not pubmed_ids:
        return {}

    params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "xml",
        **_build_common_params(),
    }
    url = NCBI_EUTILS_BASE + "efetch.fcgi?" + urlencode(params)

    with urlopen(url, timeout=30) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)
    abstract_map: Dict[str, str] = {}

    for article in root.findall(".//PubmedArticle"):
        pmid_elem = article.find(".//MedlineCitation/PMID")
        if pmid_elem is None or not pmid_elem.text:
            continue

        pmid = pmid_elem.text
        abstract_texts = []

        for abstract_text in article.findall(".//Abstract/AbstractText"):
            label = abstract_text.attrib.get("Label")
            text = "".join(abstract_text.itertext()).strip()
            if not text:
                continue

            if label:
                abstract_texts.append(f"{label}: {text}")
            else:
                abstract_texts.append(text)

        abstract_map[pmid] = " ".join(abstract_texts).strip()

    return abstract_map


def _compute_relevance_score(article: Dict[str, str], query: str) -> int:
    """
    Improved keyword scoring with bonuses for review/guideline-style evidence
    and penalties for less useful case-report-like results.
    """
    title = article.get("title", "").lower()
    source = article.get("source", "").lower()
    pubdate = article.get("pubdate", "").lower()
    text = f"{title} {source} {pubdate}"
    q = query.lower()

    score = 0

    core_terms = {
        "atrial fibrillation": 6,
        "arrhythmia": 4,
        "palpitations": 4,
        "chest pain": 3,
        "monitoring": 3,
        "ambulatory": 3,
        "evaluation": 4,
        "workup": 3,
        "guideline": 6,
        "review": 5,
        "management": 4,
        "consensus": 5,
        "statement": 4,
    }

    for term, weight in core_terms.items():
        if term in title:
            score += weight + 2
        elif term in text and term in q:
            score += weight
        elif term in text:
            score += max(1, weight // 2)

    preferred_phrases = [
        "a review",
        "guideline",
        "scientific statement",
        "consensus statement",
        "clinical practice guideline",
        "management of",
        "evaluation of",
    ]
    for phrase in preferred_phrases:
        if phrase in title:
            score += 5

    weaker_patterns = [
        "case report",
        "rare encounter",
        "rare case",
        "single-center",
        "single centre",
    ]
    for pattern in weaker_patterns:
        if pattern in title:
            score -= 6

    preferred_sources = [
        "jama",
        "circulation",
        "eur heart j",
        "european heart journal",
        "jacc",
        "heart rhythm",
    ]
    for src in preferred_sources:
        if src in source:
            score += 2

    return score


def _truncate_text(text: str, max_chars: int = 400) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _rank_and_filter_results(
    results: List[Dict[str, str]],
    query: str,
    top_n: int = 2,
) -> List[Dict[str, str]]:
    for article in results:
        article["relevance_score"] = _compute_relevance_score(article, query)

    ranked = sorted(results, key=lambda x: x.get("relevance_score", 0), reverse=True)

    filtered = [r for r in ranked if r.get("relevance_score", 0) >= 4]
    return filtered[:top_n]


def format_literature_results(results: List[Dict[str, str]]) -> str:
    if not results:
        return "Literature search result: No relevant PubMed results were found."

    lines = ["Literature search result:"]
    for i, item in enumerate(results, start=1):
        snippet = item.get("abstract_snippet", "No abstract available.")
        score = item.get("relevance_score", 0)
        lines.append(
            f"- Result {i}: Title: {item['title'] or 'N/A'} | "
            f"Source: {item['source'] or 'N/A'} | "
            f"PubDate: {item['pubdate'] or 'N/A'} | "
            f"Authors: {item['authors'] or 'N/A'} | "
            f"PMID: {item['pubmed_id'] or 'N/A'} | "
            f"RelevanceScore: {score}"
        )
        lines.append(f"  Abstract snippet: {snippet}")

    return "\n".join(lines)


def search_literature(query: str, retmax: int = 8) -> str:
    if not query.strip():
        return "Literature search result: Empty query provided."

    time.sleep(0.34)
    pubmed_ids = _esearch_pubmed(query, retmax=retmax)

    if not pubmed_ids:
        return "Literature search result: No relevant PubMed results were found."

    time.sleep(0.34)
    summaries = _esummary_pubmed(pubmed_ids)

    ranked_results = _rank_and_filter_results(summaries, query=query, top_n=2)

    if not ranked_results:
        return "Literature search result: No relevant PubMed results were found."

    best_ids = [item["pubmed_id"] for item in ranked_results if item.get("pubmed_id")]

    time.sleep(0.34)
    abstract_map = _efetch_pubmed_abstracts(best_ids)

    for item in ranked_results:
        abstract = abstract_map.get(item["pubmed_id"], "")
        item["abstract_snippet"] = (
            _truncate_text(abstract, max_chars=400) if abstract else "No abstract available."
        )

    return format_literature_results(ranked_results)