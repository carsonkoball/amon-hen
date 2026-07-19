from hashlib import sha256
import json

from flask import render_template, request

from amon_hen.scripts import blue_list_tracker


def handle(script):
    new_listings = None
    removed_listings = None
    modified_listings = None
    relisted_listings = None

    if request.method == "POST":
        new_listings = []
        removed_listings = []
        modified_listings = []
        relisted_listings = []

        results = blue_list_tracker.run()

        for listing in results:
            old_listing = listing["old_listing"]
            if old_listing:
                old_listing_manufacturer = (
                    old_listing["manufacturer"]["mad_id"]
                    if old_listing["manufacturer"]["mad_id"]
                    else "None"
                )
                old_listing_type = old_listing["UXSCore"]["mad_coretype"]
                old_listing_product = old_listing["UXSCore"]["mad_id"]
                old_listing_string = f"{old_listing_type}: {old_listing_manufacturer} - {old_listing_product}"
                old_listing_hash = sha256(
                    json.dumps(old_listing, sort_keys=True).encode("utf-8")
                ).hexdigest()

            new_listing = listing["new_listing"]
            if new_listing:
                new_listing_manufacturer = (
                    new_listing["manufacturer"]["mad_id"]
                    if new_listing["manufacturer"]["mad_id"]
                    else "None"
                )
                new_listing_type = new_listing["UXSCore"]["mad_coretype"]
                new_listing_product = new_listing["UXSCore"]["mad_id"]
                new_listing_string = f"{new_listing_type}: {new_listing_manufacturer} - {new_listing_product}"
                new_listing_hash = sha256(
                    json.dumps(new_listing, sort_keys=True).encode("utf-8")
                ).hexdigest()

            # New listing
            if old_listing is None:
                new_listings.append(new_listing_string)
                continue

            # Removed listing
            if new_listing is None:
                removed_listings.append(old_listing_string)
                continue

            # Re-listed listing
            if old_listing_hash == new_listing_hash:
                relisted_listings.append(old_listing_string)
                continue

            # Modified listing
            modified_listings.append((new_listing_string, old_listing_string))

    return render_template(
        "blue_list_tracker.html",
        title=script["name"],
        description=script["description"],
        back_link_visibility="visible",
        new_listings=new_listings,
        removed_listings=removed_listings,
        relisted_listings=relisted_listings,
        modified_listings=modified_listings,
    )
