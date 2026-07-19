from datetime import datetime
import json
import logging
import time

from . import config
from amon_hen.common.filesystem import setup_environment
from amon_hen.common.http import safe_json, http_get
from amon_hen.common.log_config import setup_logging

# Logging setup
logger = logging.getLogger(__name__)


def load_active_jobs():
    """
    Load currently active jobs.
    """
    with config.ACTIVE_FILE.open("r", encoding="utf-8") as file:
        logger.debug("Read from: %s", config.ACTIVE_FILE)

        return json.load(file)


def save_active_jobs(jobs):
    """
    Overwrite active_jobs.json with the latest active jobs.
    """
    with config.ACTIVE_FILE.open("w", encoding="utf-8") as file:
        json.dump(jobs, file, indent=2)

        logger.debug("Overwrote: %s", config.ACTIVE_FILE)


def append_removed_jobs(jobs):
    """
    Append removed jobs to removed_jobs.jsonl.
    """
    with config.REMOVED_FILE.open("a", encoding="utf-8") as f:
        for job in jobs:
            f.write(json.dumps(job) + "\n")

            logger.debug("Added %s to %s", job["title"], config.REMOVED_FILE)


def scrape_jobs(cid, ccid):
    """
    Identify listed jobs and relevant information.
    """
    index_url = config.INDEX_URL_TEMPLATE.format(
        cid=cid, ccid=ccid, timestamp=time.time(), n_top=config.N_TOP
    )
    response = http_get(index_url)

    data = safe_json(response)
    if data is None:
        return None

    jobs = []

    for job in data["jobRequisitions"]:
        posting_url = config.POSTING_URL_TEMPLATE.format(
            cid=cid,
            ccid=ccid,
            job_id=job["customFieldGroup"]["stringFields"][0]["stringValue"],
        )

        job_entry = {
            "title": job["requisitionTitle"],
            "link": posting_url,
            "date_posted": job["postDate"],
            "date_removed": "Not yet removed.",
            "location": job["requisitionLocations"][0]["nameCode"].get("shortName"),
            "adp_id": job["itemID"],
            "company_id": job["clientRequisitionID"],
            "link_id": job["customFieldGroup"]["stringFields"][0]["stringValue"],
        }
        jobs.append(job_entry)

    return jobs


def archive_posting(job, cid, ccid):
    """
    Archive a posting page into an .html file.
    """
    posting_url = config.JOB_URL_TEMPLATE.format(
        job_url_id=job["link_id"], cid=cid, ccid=ccid, timestamp=time.time()
    )
    response = http_get(posting_url)

    data = safe_json(response)
    if data is None:
        return False

    output = ""
    # Build the html archive file
    try:
        output += f"<div><h2>{data['requisitionTitle']}</h2></div>"
        output += "<div>"
        output += f"<p>{data['workLevelCode']['shortName']}<p>"
        if "stringValue" in data["customFieldGroup"]["stringFields"][5]:
            output += (
                f"<p>{data['customFieldGroup']['stringFields'][5]['stringValue']}</p>"
            )
        output += f"<span>{data['requisitionLocations'][0]['nameCode'].get('shortName')}</span>"
        output += "</div>"
        output += "<div>"
        output += "<p>Salary Range:</p>"
        output += f"<p>{data['customFieldGroup']['stringFields'][6]['stringValue']}</p>"
        output += "</div>"
        output += "<div>"
        output += data["requisitionDescription"]
        output += "</div>"
    except (KeyError, IndexError):
        logger.error("Malformed job entry: %s.", job["title"])

        return False

    try:
        with open(
            config.ARCHIVE_DIR / (data["itemID"] + ".html"), "w", encoding="utf-8"
        ) as file:
            file.write(output)

            logger.debug(
                "%s posting successfully archived (%s.html).",
                job["title"],
                job["adp_id"],
            )

            return True
        # Exception failure case
    except Exception as e:
        logger.error("%s posting failed to archive: %s.", job["title"], str(e))

        return False


def sync_jobs(cid, ccid):
    """
    Update active and removed job listings.
    """
    results = {"new_jobs": None, "removed_jobs": None}

    # Current scrape
    scraped_jobs = scrape_jobs(cid, ccid)

    if scraped_jobs is None:
        return results

    # Previous active jobs
    active_jobs = load_active_jobs()

    # Create lookup dictionaries
    active_by_id = {job["adp_id"]: job for job in active_jobs}

    scraped_by_id = {job["adp_id"]: job for job in scraped_jobs}

    # Create sets for comparisons
    active_ids = set(active_by_id.keys())
    scraped_ids = set(scraped_by_id.keys())

    # Compute changes
    new_ids = scraped_ids - active_ids
    removed_ids = active_ids - scraped_ids

    # Archive new job postings in /archive folder
    for job_id in new_ids:
        job = scraped_by_id[job_id]
        archive_posting(job, cid, ccid)

    # Add removed jobs to removed_jobs.json file
    removed_jobs = [active_by_id[job_id] for job_id in removed_ids]

    now = datetime.now()
    for job in removed_jobs:
        job["date_removed"] = now.isoformat()

    if removed_jobs:
        append_removed_jobs(removed_jobs)

    # Save latest snapshot
    save_active_jobs(scraped_jobs)

    results["new_jobs"] = [scraped_by_id[job_id] for job_id in new_ids]
    results["removed_jobs"] = removed_jobs

    return results


def adp_scraper(cid, ccid):
    """
    Find newly added and newly removed job postings and return them.
    """
    results = sync_jobs(cid, ccid)

    if results is None:
        return results
    new_jobs = results["new_jobs"]
    removed_jobs = results["removed_jobs"]

    # Log the new job postings
    logger.info("%d new job postings.", len(new_jobs))

    for job in new_jobs:
        logger.info("New job posting: %s", job["title"])

    # Log the removed job postings
    logger.info("%d removed job postings.", len(removed_jobs))
    for job in removed_jobs:
        logger.info("Removed job posting: %s", job["title"])

    return results


def run(cid, ccid):
    """
    Execute the adp_scraper workflow.
    """
    # Setup logging
    setup_logging()

    # Ensure environment is correctly setup
    setup_environment(directories=config.DIRS, files=config.FILES)

    logger.debug("Starting adp_scraper")
    logger.debug("Argument cid: %s", cid)
    logger.debug("Argument ccid: %s", ccid)

    results = adp_scraper(cid, ccid)

    logger.debug("Stopping adp_scraper")

    return results
