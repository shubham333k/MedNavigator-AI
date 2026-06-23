"""
PubMed API fetcher.
Retrieves abstracts from NCBI PubMed for ingestion into the knowledge base.
"""

import logging
import time
from typing import List, Dict, Any, Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
PUBMED_SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"


class PubMedFetcher:
    """Fetches and parses PubMed abstracts for RAG ingestion."""

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.ncbi_api_key
        self.email = settings.ncbi_email
        self._base_params = {}
        if self.api_key:
            self._base_params["api_key"] = self.api_key

    async def search(
        self,
        query: str,
        max_results: int = 10,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[str]:
        """
        Search PubMed and return a list of PMIDs.

        Args:
            query: PubMed search query
            max_results: Maximum number of results to return
            date_from: Start date (YYYY/MM/DD)
            date_to: End date (YYYY/MM/DD)

        Returns:
            List of PubMed IDs (PMIDs)
        """
        params = {
            **self._base_params,
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
        }

        if date_from:
            params["mindate"] = date_from
        if date_to:
            params["maxdate"] = date_to
        if date_from or date_to:
            params["datetype"] = "pdat"

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(PUBMED_SEARCH_URL, params=params)
            response.raise_for_status()

        data = response.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])

        logger.info(f"PubMed search '{query}': found {len(pmids)} results")
        return pmids

    async def fetch_abstracts(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch abstracts and metadata for a list of PMIDs.

        Returns list of dicts with title, abstract, authors, journal, date, etc.
        """
        if not pmids:
            return []

        params = {
            **self._base_params,
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "rettype": "abstract",
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(PUBMED_FETCH_URL, params=params)
            response.raise_for_status()

        articles = self._parse_xml_response(response.text)
        logger.info(f"Fetched {len(articles)} abstracts from PubMed")
        return articles

    def _parse_xml_response(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parse PubMed XML response into structured data."""
        import xml.etree.ElementTree as ET

        articles = []
        try:
            root = ET.fromstring(xml_text)

            for article_elem in root.findall(".//PubmedArticle"):
                try:
                    # Extract article details
                    medline = article_elem.find(".//MedlineCitation")
                    if medline is None:
                        continue

                    pmid_elem = medline.find(".//PMID")
                    pmid = pmid_elem.text if pmid_elem is not None else "unknown"

                    article = medline.find(".//Article")
                    if article is None:
                        continue

                    # Title
                    title_elem = article.find(".//ArticleTitle")
                    title = title_elem.text if title_elem is not None else "Untitled"

                    # Abstract
                    abstract_parts = []
                    abstract_elem = article.find(".//Abstract")
                    if abstract_elem is not None:
                        for text_elem in abstract_elem.findall(".//AbstractText"):
                            label = text_elem.get("Label", "")
                            text = text_elem.text or ""
                            if label:
                                abstract_parts.append(f"**{label}**: {text}")
                            else:
                                abstract_parts.append(text)

                    abstract = "\n\n".join(abstract_parts) if abstract_parts else ""

                    # Authors
                    author_list = article.find(".//AuthorList")
                    authors = []
                    if author_list is not None:
                        for author in author_list.findall(".//Author"):
                            last = author.find("LastName")
                            first = author.find("ForeName")
                            if last is not None:
                                name = last.text
                                if first is not None:
                                    name += f" {first.text}"
                                authors.append(name)

                    # Journal
                    journal_elem = article.find(".//Journal/Title")
                    journal = journal_elem.text if journal_elem is not None else ""

                    # Publication date
                    pub_date = article.find(".//Journal/JournalIssue/PubDate")
                    date_str = ""
                    if pub_date is not None:
                        year = pub_date.find("Year")
                        month = pub_date.find("Month")
                        if year is not None:
                            date_str = year.text
                            if month is not None:
                                date_str += f"/{month.text}"

                    articles.append({
                        "pmid": pmid,
                        "title": title,
                        "abstract": abstract,
                        "authors": ", ".join(authors[:5]),
                        "journal": journal,
                        "publication_date": date_str,
                        "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        "source_type": "pubmed",
                    })

                except Exception as e:
                    logger.warning(f"Error parsing article: {e}")
                    continue

        except ET.ParseError as e:
            logger.error(f"XML parse error: {e}")

        return articles

    async def search_and_fetch(
        self,
        query: str,
        max_results: int = 10,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search PubMed and fetch all abstracts in one call."""
        pmids = await self.search(query, max_results, date_from, date_to)
        if not pmids:
            return []
        return await self.fetch_abstracts(pmids)


def get_pubmed_fetcher() -> PubMedFetcher:
    """Get a PubMed fetcher instance."""
    return PubMedFetcher()
