import json
import os
import re
import time
from typing import Optional

from bs4 import BeautifulSoup
from google import genai
from playwright.sync_api import sync_playwright
from typing_extensions import TypedDict

# --- CONFIGURATION (USER TO EDIT) ---
# Paste your Gemini API Key here
GEMINI_API_KEY = "AIzaSyBTkGmHzNe2mxcpBQGgVLQWdp6gBqeBSRw"

# The URL of the company's careers page
CAREERS_PAGE_URL = "https://apply.workable.com/constructor-1/"  # Example

# Description of the job you are looking for
USER_JOB_DESCRIPTION = """
I am looking for a Backend Engineer role that uses Python.
I have 5 years of experience in software engineering.
"""

# Directory to save the downloaded job descriptions
OUTPUT_DIRECTORY = "downloaded_jobs"

# Model to use
AI_MODEL = "gemini-flash-latest"

# --- CONFIGURATION (USER TO EDIT) END ---


class JobListing(TypedDict):
    title: str
    url: str
    location: Optional[str]


class PaginationAction(TypedDict):
    has_more: bool
    action_type: str  # 'click', 'scroll', 'none'
    selector: Optional[str]
    description: Optional[str]


class JobAnalysis(TypedDict):
    is_relevant: bool
    reasoning: str
    match_score: int
    job_description_summary: str
    requirements: list[str]
    key_responsibilities: list[str]
    tech_stack: list[str]
    salary_range: Optional[str]
    perks: list[str]
    application_process: Optional[str]
    published_date: Optional[str]


class JobAgent:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def detect_pagination(self, page_content: str) -> PaginationAction:
        """
        Analyzes HTML to find how to load more jobs (Next button, Load More, etc.)
        """
        print("🤖 Agent: Looking for pagination controls...")

        soup = BeautifulSoup(page_content, "html.parser")
        # Simplify DOM for token efficiency, focusing on buttons and links
        for tag in soup(["script", "style", "svg", "path", "meta", "link"]):
            tag.decompose()

        # We need to be careful not to strip too much, as structural context helps.
        # But we mostly care about interactive elements at the bottom of lists.
        # Let's take the last 50k characters.
        cleaned_text = str(soup)[:50000]

        prompt = f"""
        You are an expert web automaton.
        Analyze the HTML to find the mechanism to load more jobs.

        Look for:
        1. Partial text matches like "Load More", "Show More", "Next Page", "View all jobs", a generic arrow icon button, or pagination numbers.
        2. Infinite scroll indicators (though usually handled by 'scroll' action).

        HTML Snippet (bottom of page):
        {cleaned_text}

        Return a JSON object with:
        - has_more: true if you see a clear way to load more.
        - action_type: "click" if there is a button/link, "scroll" if it looks like infinite scroll, "none" otherwise.
        - selector: A precise CSS selector for the button/link (e.g. "button.load-more", "a[aria-label='Next']"). ONE element only.
        - description: Short reasoning.
        """

        try:
            response = self.client.models.generate_content(
                model=AI_MODEL,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PaginationAction,
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error detecting pagination: {e}")
            return {
                "has_more": False,
                "action_type": "none",
                "selector": None,
                "description": "Error",
            }

    def extract_jobs_from_html(
        self, page_content: str, base_url: str
    ) -> list[JobListing]:
        """
        Uses Gemini to parse raw HTML and extract a list of job postings.
        """
        print("🤖 Agent: Analyzing page content to extract jobs...")

        # We clean the HTML slightly to reduce token usage, removing scripts and styles
        soup = BeautifulSoup(page_content, "html.parser")
        for script in soup(["script", "style", "svg", "footer", "nav"]):
            script.decompose()

        cleaned_text = soup.get_text(separator="\n")
        # Removing excessive whitespace
        cleaned_text = re.sub(r"\n+", "\n", cleaned_text).strip()

        # Gemini 1.5 Flash has a massive context window (1M tokens),
        # so we can pass the entire cleaned text without truncation.
        prompt = f"""
        You are an expert web scraper.
        Your goal is to extract job listings from the text content of a careers page.

        Base URL for relative links: {base_url}

        Text Content:
        {cleaned_text}

        Extract all job listings found.
        Ensure URLs are absolute.
        """

        try:
            response = self.client.models.generate_content(
                model=AI_MODEL,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=list[JobListing],
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error parsing jobs with Gemini: {e}")
            # return []
            raise e

    def analyze_relevance(
        self, job_title: str, job_description: str, user_criteria: str
    ) -> JobAnalysis:
        """
        Uses Gemini to determine if a full job description matches the user's criteria.
        """

        prompt = f"""
        You are a personalized career coach.
        Match the following job against the user's criteria.

        User Criteria:
        {user_criteria}

        Job Title: {job_title}

        Job Description:
        {job_description}

        Analyze the job in detail and populate the following fields:
        - is_relevant: bool
        - reasoning: str (why it matches or not)
        - match_score: int (0-100)
        - job_description_summary: str (concise summary)
        - requirements: list[str]
        - key_responsibilities: list[str]
        - tech_stack: list[str]
        - salary_range: str (if available, else null)
        - perks: list[str]
        - application_process: str (summary of steps)
        - published_date: str (if available)

        Determine if this job is relevant. Be strict but fair.
        """

        try:
            response = self.client.models.generate_content(
                model=AI_MODEL,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json", response_schema=JobAnalysis
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error analyzing job {job_title}: {e}")
            return {
                "is_relevant": False,
                "reasoning": "Error in analysis",
                "match_score": 0,
                "job_description_summary": "",
                "requirements": [],
                "key_responsibilities": [],
                "tech_stack": [],
                "salary_range": None,
                "perks": [],
                "application_process": None,
                "published_date": None,
            }


# from pprint import pprint as pp
# from src.core.business_logic.poc import *
# job_agent = JobAgent(api_key=GEMINI_API_KEY)
# p = sync_playwright().start()
# browser = p.chromium.launch(headless=True)
# page = browser.new_page()
# page.context.set_default_timeout(0)
# page.goto(CAREERS_PAGE_URL)
# content = page.content()
# base_url = page.url
# pagination = job_agent.detect_pagination(content)
# page.click(pagination["selector"], timeout=5000, force=True)
# p.stop()
def main():
    print(f"🚀 Starting Job Agent for: {CAREERS_PAGE_URL}")
    job_agent = JobAgent(api_key=GEMINI_API_KEY)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 1. Go to Careers Page
        print("🌐 Navigating to careers page...")

        # remove timeout
        page.context.set_default_timeout(0)

        page.goto(CAREERS_PAGE_URL)

        all_collected_jobs = {}  # Key: URL, Value: JobListing
        max_pages = 5
        current_page = 1

        while current_page <= max_pages:
            print(f"\n📄 Processing Page {current_page}...")

            content = page.content()
            base_url = page.url

            # 2. Extract Jobs from current view
            jobs = job_agent.extract_jobs_from_html(
                page_content=content,
                base_url=base_url,
            )

            new_jobs_count = 0
            for job in jobs:
                if job["url"] not in all_collected_jobs:
                    all_collected_jobs[job["url"]] = job
                    new_jobs_count += 1

            print(f"   found {len(jobs)} jobs on this page ({new_jobs_count} new).")

            # 3. Check for Pagination
            pagination = job_agent.detect_pagination(content)

            if pagination["has_more"]:
                print(
                    f"   👉 Next Action: {pagination['action_type']} - "
                    f"{pagination['description']}"
                )

                if pagination["action_type"] == "click" and pagination["selector"]:
                    print(f"   🖱️ Clicking: {pagination['selector']}")
                    page.click(pagination["selector"], force=True)
                    # Wait for content
                    time.sleep(3)

                elif pagination["action_type"] == "scroll":
                    print("   📜 Scrolling to bottom...")
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                else:
                    print("   ⚠️ Unknown action type, stopping pagination.")
                    break

                current_page += 1

            else:
                print("   🛑 No more pages detected.")
                break

        total_jobs = list(all_collected_jobs.values())
        print(f"\n✅ Total Unique Jobs Found: {len(total_jobs)}")

        relevant_jobs = []
        ignored_jobs = []

        # Ensure output directory exists
        if not os.path.exists(OUTPUT_DIRECTORY):
            os.makedirs(OUTPUT_DIRECTORY)

        # 4. Process Each Job
        print("\n🔍 Analyzing job relevance (this may take a moment)...")
        for i, job in enumerate(total_jobs):
            title = job.get("title", "Unknown Title")
            url = job.get("url", "")

            if not url:
                print(f"      ⚠️ Skipping job with no URL. Title: {title}")
                continue

            print(f"   [{i + 1}/{len(total_jobs)}] Checking: {title}...")

            try:
                # Visit job page
                page.goto(url)
                time.sleep(1)  # simple rate limit

                job_content_html = page.content()
                soup_job = BeautifulSoup(job_content_html, "html.parser")
                for tag in soup_job(["script", "style", "nav", "footer"]):
                    tag.decompose()
                job_raw_text = soup_job.get_text(separator="\n").strip()

                # Analyze Content
                analysis = job_agent.analyze_relevance(
                    job_title=title,
                    job_description=job_raw_text,
                    user_criteria=USER_JOB_DESCRIPTION,
                )

                if analysis.get("match_score", 0) > 80:
                    score = analysis.get("match_score", 0)
                    reasoning = analysis.get("reasoning", "")
                    print(f"      🎯 MATCH! Score: {score}/100. Reason: {reasoning}")

                    # 4. Download/Save
                    safe_title = re.sub(r"[^a-zA-Z0-9]", "_", title).lower()
                    filename = f"{score}_{safe_title}.txt"
                    filepath = os.path.join(OUTPUT_DIRECTORY, filename)

                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(f"TITLE: {title}\n")
                        f.write(f"URL: {url}\n")
                        f.write(f"MATCH SCORE: {score}\n")
                        f.write(f"REASONING: {reasoning}\n")
                        f.write(f"PUBLISHED: {analysis.get('published_date', 'N/A')}\n")
                        f.write("-" * 40 + "\n")
                        f.write(f"SUMMARY: {analysis.get('job_description_summary')}\n")

                        f.write("\nTECH STACK:\n")
                        for item in analysis.get("tech_stack", []):
                            f.write(f"- {item}\n")

                        f.write("\nREQUIREMENTS:\n")
                        for item in analysis.get("requirements", []):
                            f.write(f"- {item}\n")

                        f.write("\nKEY RESPONSIBILITIES:\n")
                        for item in analysis.get("key_responsibilities", []):
                            f.write(f"- {item}\n")

                        f.write(
                            "\nSALARY: "
                            f"{analysis.get('salary_range', 'Not specified')}\n"
                        )

                        f.write("\nPERKS:\n")
                        for item in analysis.get("perks", []):
                            f.write(f"- {item}\n")

                        f.write(
                            "\nAPPLICATION PROCESS: "
                            f"{analysis.get('application_process', 'N/A')}\n"
                        )
                        f.write("-" * 40 + "\n\n")
                        f.write("--- RAW CONTENT ---\n")
                        f.write(job_raw_text)

                    relevant_jobs.append(job)
                else:
                    reason = analysis.get("reasoning")
                    print(
                        f"      ❌ Not relevant. "
                        f"Match Score: {analysis.get('match_score')}/100. "
                        f"Reason: {reason}"
                    )
                    ignored_jobs.append({"title": title, "url": url, "reason": reason})

            except Exception as e:
                print(f"      ⚠️ Error processing {url}: {e}")
                continue

        browser.close()

    print("\n" + "=" * 50)
    print(f"🎉 Done! Found {len(relevant_jobs)} relevant jobs.")

    # Save summary of ignored jobs
    if ignored_jobs:
        summary_path = os.path.join(OUTPUT_DIRECTORY, "_ignored_jobs_summary.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("--- JOBS MARKED AS NOT RELEVANT ---\n\n")
            for job in ignored_jobs:
                f.write(f"TITLE: {job['title']}\n")
                f.write(f"URL: {job['url']}\n")
                f.write(f"REASON: {job['reason']}\n")
                f.write("-" * 30 + "\n")
        print(f"📄 Ignored jobs summary saved to '{summary_path}'")

    if relevant_jobs:
        print(f"📂 Relevant job files saved in '{OUTPUT_DIRECTORY}' directory.")


if __name__ == "__main__":
    main()
