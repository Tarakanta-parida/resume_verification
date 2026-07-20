from typing import Dict, Any

SAMPLE_JDS: Dict[str, str] = {
    "software_engineer": """Role: Senior Software Engineer (Frontend/Fullstack)

Requirements:
- 3+ years of experience with React, TypeScript, and modern frontend state management (Redux, Zustand).
- Deep experience in designing and building RESTful APIs using Node.js and Express.
- Solid understanding of database systems: PostgreSQL, MySQL, and Redis caching.
- Familiarity with cloud services (AWS EC2, S3, RDS) and CI/CD pipelines (GitHub Actions, Docker).
- Proven track record of optimizing web application performance, core web vitals, and system design.
- Excellent collaboration skills and experience working in Agile/Scrum environments.""",

    "data_analyst": """Role: Data Analyst (BI & Analytics)

Requirements:
- Strong knowledge of SQL for query optimization, data aggregation, and joining complex tables.
- 2+ years of experience writing Python scripts for data manipulation (Pandas, NumPy).
- Expertise in creating interactive dashboards and reports using Tableau or Power BI.
- Experience with statistical analysis, hypothesis testing, and regression modeling.
- Ability to clean messy data sources and perform Exploratory Data Analysis (EDA).
- Good business communication skills to translate complex data insights to stakeholders.""",

    "product_manager": """Role: Product Manager (Growth & Analytics)

Requirements:
- 3+ years of experience managing software products through the entire product lifecycle.
- Strong product roadmap planning, backlog grooming, and Agile/Scrum execution skills.
- Experience with analytics tools (Google Analytics, Mixpanel) and SQL to pull product metrics.
- Track record of defining clear product requirements (PRDs) and user stories.
- Proven experience conducting user research, A/B testing, and usability testing.
- Strong stakeholder management skills to align engineering, design, and business teams.""",

    "marketing_specialist": """Role: Digital Marketing Specialist

Requirements:
- 2+ years of experience in managing Paid Ads (PPC, Google Ads, Meta Ads) and budgets.
- Proven SEO expertise (keyword research, on-page optimization, backlink strategies).
- Deep experience using analytics platforms: Google Analytics 4 (GA4) and Google Search Console.
- Ability to write copy for email campaigns, blog posts, and advertisements.
- Experience running email marketing campaigns using Mailchimp or HubSpot.
- Strong analytical skills to track ROI, click-through rates, and conversion metrics."""
}

SAMPLE_RESUMES: Dict[str, Dict[str, Any]] = {
    "software_engineer": {
        "personalInfo": {
            "name": "Alex Johnson",
            "email": "alex.johnson@email.com",
            "phone": "+1 (555) 019-2834",
            "github": "github.com/alexj-dev",
            "linkedin": "linkedin.com/in/alexjohnson"
        },
        "summary": "Motivated Software Developer with experience in building web applications. Proficient in JavaScript and React. Looking to join a fast-paced development team to contribute to scalable products and learn new technologies.",
        "skills": ["JavaScript", "HTML", "CSS", "React", "Node.js", "Express", "Git", "SQL", "MongoDB"],
        "experience": [
            {
                "role": "Software Developer",
                "company": "WebTech Solutions",
                "duration": "2024 - Present",
                "bullets": [
                    "Built and maintained React web applications for client projects.",
                    "Worked on REST APIs using Node.js and Express to connect frontend to database.",
                    "Collaborated with QA engineers to debug code and resolve frontend layout issues.",
                    "Participated in daily standups and sprint planning sessions with the engineering team."
                ]
            },
            {
                "role": "Junior Web Developer",
                "company": "DevLaunch Studio",
                "duration": "2023 - 2024",
                "bullets": [
                    "Assisted in developing client websites using HTML, CSS, and basic JavaScript.",
                    "Wrote unit tests for components to ensure code reliability.",
                    "Fixed bugs in CSS styling to align interfaces with design specifications."
                ]
            }
        ],
        "projects": [
            {
                "name": "TaskTracker App",
                "description": "A task management tool built with React. Features include dashboard updates, drag-and-drop tasks, and user authentication.",
                "bullets": [
                    "Created the frontend dashboard layout and user login flow.",
                    "Integrated MongoDB for storing tasks and user records."
                ]
            }
        ],
        "education": [
            {
                "degree": "B.S. in Computer Science",
                "school": "State University",
                "year": "2023"
            }
        ],
        "certifications": []
    },

    "data_analyst": {
        "personalInfo": {
            "name": "Sarah Miller",
            "email": "sarah.m@email.com",
            "phone": "+1 (555) 038-4921",
            "github": "github.com/sarahm-data",
            "linkedin": "linkedin.com/in/sarahmiller-data"
        },
        "summary": "Detail-oriented individual interested in working with data. Familiar with basic SQL and Excel. Seeking a Data Analyst role to help teams make decisions using data analytics.",
        "skills": ["SQL", "Excel", "Python", "Tableau", "Data Entry", "Microsoft Word", "HTML"],
        "experience": [
            {
                "role": "Junior Analyst",
                "company": "Retail Corp",
                "duration": "2024 - Present",
                "bullets": [
                    "Ran SQL queries to pull weekly sales figures and put them in reports.",
                    "Used Excel spreadsheets to format lists and clean up duplicate rows.",
                    "Helped make basic Tableau charts showing category performance.",
                    "Sent monthly slide decks to the store operations team."
                ]
            },
            {
                "role": "Data Assistant",
                "company": "Insight Data Services",
                "duration": "2023 - 2024",
                "bullets": [
                    "Entered data into tables and double-checked records for accuracy.",
                    "Created charts and tables for client summaries."
                ]
            }
        ],
        "projects": [
            {
                "name": "Sales Data Cleanup",
                "description": "Cleaned a sales dataset using Python and summarized the findings in a chart.",
                "bullets": [
                    "Used a Python script to find and replace missing values in a CSV.",
                    "Plotted the monthly sales trend using a basic bar chart."
                ]
            }
        ],
        "education": [
            {
                "degree": "B.A. in Statistics",
                "school": "City College",
                "year": "2023"
            }
        ],
        "certifications": []
    },

    "product_manager": {
        "personalInfo": {
            "name": "David Chen",
            "email": "david.chen@email.com",
            "phone": "+1 (555) 049-5832",
            "linkedin": "linkedin.com/in/davidchen-pm"
        },
        "summary": "Product-minded professional with experience coordinating software releases and gathering user feedback. Looking to drive product strategy as a Product Manager.",
        "skills": ["Product Planning", "Agile", "Jira", "User Feedback", "Wireframing", "Roadmapping"],
        "experience": [
            {
                "role": "Associate Product Manager",
                "company": "SaaS Platform Inc.",
                "duration": "2024 - Present",
                "bullets": [
                    "Gathered feature requests from support teams and prioritized tickets in Jira.",
                    "Drafted feature documentation and user guide release notes.",
                    "Held weekly sync meetings with engineering leads to track sprint velocity."
                ]
            }
        ],
        "projects": [
            {
                "name": "Customer Feedback Portal",
                "description": "Designed feedback intake workflow for web app users.",
                "bullets": ["Mapped out user journey maps and wireframes."]
            }
        ],
        "education": [
            {
                "degree": "B.S. in Business Administration",
                "school": "Tech University",
                "year": "2022"
            }
        ],
        "certifications": ["Certified Scrum Product Owner (CSPO)"]
    },

    "marketing_specialist": {
        "personalInfo": {
            "name": "Emily Vance",
            "email": "emily.vance@email.com",
            "phone": "+1 (555) 077-8812",
            "linkedin": "linkedin.com/in/emilyvance-mkt"
        },
        "summary": "Creative digital marketing specialist with experience in social media management, email newsletters, and ad copy creation.",
        "skills": ["SEO", "Copywriting", "Google Analytics", "Mailchimp", "Canva", "Social Media"],
        "experience": [
            {
                "role": "Marketing Coordinator",
                "company": "Growth Agency",
                "duration": "2023 - Present",
                "bullets": [
                    "Managed social media calendars across Twitter and LinkedIn.",
                    "Wrote monthly email newsletters sent to 10k+ subscribers.",
                    "Monitored website traffic metrics using Google Analytics."
                ]
            }
        ],
        "projects": [],
        "education": [
            {
                "degree": "B.A. in Communications",
                "school": "State College",
                "year": "2023"
            }
        ],
        "certifications": ["Google Analytics Certification"]
    }
}
