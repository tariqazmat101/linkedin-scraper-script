import hashlib
import re

from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, ExperienceLevelFilters
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters


# You first to install linkedin-jobs-scraper package, run pip install linkedin-jobs-scraper
# blog post at https://tariq101.netlify.app/


# Prints out event data to the console
# @params event:EventData, case: String denoting the case(Good,Bad,Best,etc)
def printout(data, case):
    print(case)
    # print(set(other.findall(txt)))
    print(data.link)
    print(data.apply_link)
    print(data.description)
    print('-------------------------------------------------------')


# returns the number of distinct matches for a given regex expresion
def distinctMatches(array):
    return len(set((array)))


hashes = set()


# Checks if the given ad has already been scraped
def isDuplicateAd(ad: EventData):
    # Create a unique string
    Hashstring = ad.company
    Hashstring += ad.place
    Hashstring += ad.title
    Hashstring += ad.employment_type
    Hashstring += ad.job_function

    # Compute the hash
    md5Hash = hashlib.md5(Hashstring.encode()).hexdigest()

    if md5Hash in hashes:
        return True
    else:
        hashes.add(md5Hash)
        return False


def on_data(data: EventData):
    # Why does this look like a code smell?
    amazon = distinctMatches(re.compile(r'\b(amazon|aws)\b', flags=re.I).findall(data.description))
    tools = distinctMatches(re.compile(r'\b(terraform|docker|linux|ansible)\b', flags=re.I).findall(data.description))
    language = distinctMatches( re.compile(r'\b(node(js)?|Typescript|javascript|python|bash)\b', flags=re.I).findall(data.description))
    location = distinctMatches( re.compile(r'\b(Canada|sponser|remote|graduated?)\b', flags=re.I).findall(data.description))
    # This matches for yearsOfexperience of experience, see https://regex101.com/r/KwngR1/2
    yearsOfexperience = distinctMatches( re.compile(r"(\d+(?:-\d+)?\+?)\s*(or more|to)?(yearsOfexperience?)", flags=re.I).findall(data.description))
    # Matches only for 3-9 year of experience
    entryLevelYears = distinctMatches( re.compile(r"([3-9](?:-[3-9])?\+?)\s*(or more|to)?(yearsOfexperience?)", flags=re.I).findall(data.description))
    # special regex
    graduate = distinctMatches(re.compile(r"graduated?", flags=re.I).findall(data.description))

    # Check if the ad is a duplicate
    if (isDuplicateAd(data)): return
    #Exclude postings containing titles with sr. or senior
    if bool(re.compile(r'(sr.?|senior)', flags=re.I).findall(data.title)): return
    #Exclude postings containing irrelevant keywords
    if re.compile(r"\b(C|Ruby|PHP)\b", flags=re.I).findall(data.description): return

    if   (amazon) >= 1 and (tools) >= 3 and (language) >= 1 and (location) > 0 and not bool(yearsOfexperience):
        printout(data, "Perfect case")
    elif (amazon) >= 1 and (tools) >= 2 and (language) >= 1 and (location) >= 0 and not bool(yearsOfexperience):
        printout(data, "Best case")
        # parse for 'graduate/graduated' token in the advert
    elif (amazon) >= 1 and (tools) >= 1 and (language) >= 1 and (location) >= 0 and bool(graduate):
        # Special case for university graduate jobs
        printout(data, "graduate")
    elif (amazon) >= 1 and (tools) >= 1 and (language) >= 1 and (location) >= 0 and not bool(entryLevelYears):
        printout(data, "Jobs with 1-3 years, mediocore jobs at best")


def on_error(error):
    print('[ON_ERROR]', error)


def on_end():
    print('[ON_END]')


scraper = LinkedinScraper(
    chrome_options=None,  # You can pass your custom Chrome options here
    headless=True,  # Overrides headless mode only if chrome_options is None
    max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
    slow_mo=0.6,  # Slow down the scraper to avoid 'Too many requests (429)' errors
)

# Add event listeners
scraper.on(Events.DATA, on_data)
scraper.on(Events.ERROR, on_error)
scraper.on(Events.END, on_end)

limit = 9000
queries = [
    Query(
        query='Cloud Engineer',
        options=QueryOptions(
            locations=['Canada', "United-States"],
            optimize=False,
            limit=limit,
            filters=QueryFilters(
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.MONTH,
                experience=[ExperienceLevelFilters.INTERNSHIP, ExperienceLevelFilters.ASSOCIATE,
                            ExperienceLevelFilters.ENTRY_LEVEL]
            )
        )
    ),
    Query(
        query='Cloud architect',
        options=QueryOptions(
            locations=['Canada', 'United-States'],
            optimize=False,
            limit=limit,
            filters=QueryFilters(
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.MONTH,
                experience=[ExperienceLevelFilters.INTERNSHIP, ExperienceLevelFilters.ASSOCIATE,
                            ExperienceLevelFilters.ENTRY_LEVEL]
            )
        )
    ),
    Query(
        query='Devops Engineer',
        options=QueryOptions(
            locations=['Canada', 'United-States'],
            optimize=False,
            limit=limit,
            filters=QueryFilters(
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.MONTH,
                experience=[ExperienceLevelFilters.INTERNSHIP, ExperienceLevelFilters.ASSOCIATE,
                            ExperienceLevelFilters.ENTRY_LEVEL]
            )
        )
    )
]

scraper.run(queries)
