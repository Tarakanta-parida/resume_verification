import re
from typing import Dict, List, Set, Any

TAXONOMY = {
    "Technical Skills": [
        "javascript", "typescript", "python", "java", "c++", "c#", "ruby", "php", "swift", "go", "rust",
        "sql", "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle", "cassandra", "dynamodb", "firebase",
        "react", "angular", "vue", "next.js", "svelte", "jquery", "node.js", "express", "django", "flask",
        "spring boot", "laravel", "fastapi", "graphql", "rest api", "apis", "backend", "frontend", "fullstack",
        "docker", "kubernetes", "jenkins", "github actions", "ci/cd", "git", "linux", "aws", "azure", "gcp",
        "system design", "microservices", "oop", "algorithms", "data structures", "html", "css", "sass", "bootstrap", "tailwind"
    ],
    "Analytics & Data": [
        "tableau", "power bi", "excel", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "statistics",
        "data warehousing", "snowflake", "bigquery", "data visualization", "eda", "data cleaning", "regression",
        "machine learning", "deep learning", "nlp", "artificial intelligence", "r programming", "data pipelines", "elt", "etl"
    ],
    "Management & Methodologies": [
        "product roadmap", "agile", "scrum", "jira", "trello", "prd", "user stories", "user research", "ab testing",
        "stakeholder management", "project management", "sdlc", "scrum master", "backlog grooming", "sprint planning",
        "business analysis", "cross-functional", "kanban", "product life cycle"
    ],
    "Marketing & Tools": [
        "seo", "sem", "ppc", "google analytics", "ga4", "mailchimp", "hubspot", "copywriting", "content marketing",
        "social media", "canva", "crm", "campaign management", "roi", "cro", "conversion rate", "marketing automation"
    ]
}

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "arent", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "cant", "cannot",
    "could", "couldnt", "did", "didnt", "do", "does", "doesnt", "doing", "dont", "down", "during", "each", "few",
    "for", "from", "further", "had", "hadnt", "has", "hasnt", "have", "havent", "having", "he", "hed", "hell",
    "hes", "her", "here", "heres", "hers", "herself", "him", "himself", "his", "how", "hows", "i", "id", "ill",
    "im", "ive", "if", "in", "into", "is", "isnt", "it", "its", "itself", "lets", "me", "more", "most", "mustnt",
    "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours",
    "ourselves", "out", "over", "own", "same", "shant", "she", "shed", "shell", "shes", "should", "shouldnt", "so",
    "some", "such", "than", "that", "thats", "the", "their", "theirs", "them", "themselves", "then", "there",
    "theres", "these", "they", "theyd", "theyll", "theyre", "theyve", "this", "those", "through", "to", "too",
    "under", "until", "up", "very", "was", "wasnt", "we", "wed", "well", "were", "weve", "werent", "what", "whats",
    "when", "whens", "where", "wheres", "which", "while", "who", "whos", "whom", "why", "whys", "with", "wont",
    "would", "wouldnt", "you", "youd", "youll", "youre", "youve", "your", "yours", "yourself", "yourselves"
}

SKILLS_LOOKUP = set()
for cat, items in TAXONOMY.items():
    for item in items:
        SKILLS_LOOKUP.add(item)


def clean_text(text: str) -> str:
    """Removes punctuation and standardizes spacing."""
    text = text.lower()
    text = re.sub(r'[^\w\s#+.-]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()


def extract_keywords_from_text(text: str) -> Set[str]:
    """Extracts valid candidate keywords based on taxonomy and text content."""
    cleaned = clean_text(text)
    words = set(cleaned.split(' '))
    extracted = set()

    for category, terms in TAXONOMY.items():
        for term in terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, cleaned):
                extracted.add(term)

    for word in words:
        if len(word) > 2 and word not in STOP_WORDS and not word.isdigit():
            if word in SKILLS_LOOKUP:
                extracted.add(word)

    return extracted


def calculate_ats_metrics(resume_text: str, jd_text: str) -> Dict[str, Any]:
    """Computes keyword overlap, missing keywords, section scores, and formatting issues."""
    resume_cleaned = clean_text(resume_text)
    jd_keywords = extract_keywords_from_text(jd_text)

    if not jd_keywords:
        jd_keywords = {"agile", "project management", "collaboration", "communication"}

    matched_keywords = []
    missing_keywords = []

    for kw in jd_keywords:
        pattern = r'\b' + re.escape(kw) + r'\b'
        if re.search(pattern, resume_cleaned):
            matched_keywords.append(kw.upper())
        else:
            missing_keywords.append(kw.upper())

    resume_lower = resume_text.lower()
    sections = {
        "Summary": any(x in resume_lower for x in ["summary", "profile", "objective"]),
        "Skills": any(x in resume_lower for x in ["skills", "competencies", "technologies"]),
        "Experience": any(x in resume_lower for x in ["experience", "employment", "work history"]),
        "Education": any(x in resume_lower for x in ["education", "academic"])
    }
    section_score = round(sum(1 for val in sections.values() if val) / len(sections) * 100)

    total_keywords = len(jd_keywords)
    matched_count = len(matched_keywords)
    keyword_score = round((matched_count / total_keywords) * 100) if total_keywords > 0 else 100

    original_score = round((keyword_score * 0.7) + (section_score * 0.3))
    potential_score = round((100 * 0.7) + (section_score * 0.3))

    has_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text))
    has_phone = bool(re.search(r'\+?[0-9\s\-()]{7,18}', resume_text))

    formatting_issues = []
    if not has_email:
        formatting_issues.append("Missing email address contact info.")
    if not has_phone:
        formatting_issues.append("Missing phone contact info.")
    if len(resume_text.split()) < 100:
        formatting_issues.append("Resume length is unusually short (less than 100 words).")

    return {
        "original_score": original_score,
        "potential_score": potential_score,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "sections_found": sections,
        "section_score": section_score,
        "formatting_issues": formatting_issues
    }
