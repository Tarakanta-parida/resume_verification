import { create } from 'zustand';

export interface PersonalInfo {
  name: string;
  email: string;
  phone: string;
  github?: string;
  linkedin?: string;
}

export interface Experience {
  role: string;
  company: string;
  duration: string;
  bullets: string[];
}

export interface Project {
  name: string;
  description: string;
  bullets: string[];
}

export interface Education {
  degree: string;
  school: string;
  year: string;
}

export interface ResumeData {
  personalInfo: PersonalInfo;
  summary: string;
  skills: string[];
  experience: Experience[];
  projects: Project[];
  education: Education[];
  certifications?: string[];
}

interface ResumeState {
  theme: 'dark' | 'light';
  currentTab: 'dashboard' | 'analysis' | 'comparer' | 'report';
  originalResume: ResumeData | null;
  optimizedResume: ResumeData | null;
  originalScore: number;
  optimizedScore: number;
  matchedKeywords: string[];
  missingKeywords: string[];
  sectionsFound: Record<string, boolean>;
  sectionScore: number;
  formattingIssues: string[];
  
  resumeName: string;
  jdText: string;
  
  resumeId: number | null;
  jdId: number | null;
  resultId: number | null;
  
  isOptimized: boolean;
  isLoading: boolean;
  loadingStep: string;
  loadingSub: string;
  
  toggleTheme: () => void;
  setCurrentTab: (tab: 'dashboard' | 'analysis' | 'comparer' | 'report') => void;
  setJdText: (text: string) => void;
  loadSampleProfile: (profileKey: string) => void;
  uploadResumeFile: (file: File) => Promise<void>;
  removeResumeFile: () => void;
  runOptimization: () => Promise<void>;
  resetAll: () => void;
}

const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      return 'https://resumatch-backend-22e5.onrender.com/api/v1';
    }
  }
  return 'http://localhost:8080/api/v1';
};

export const API_BASE_URL = getApiBaseUrl();

export const useResumeStore = create<ResumeState>((set, get) => ({
  theme: 'dark',
  currentTab: 'dashboard',
  originalResume: null,
  optimizedResume: null,
  originalScore: 0,
  optimizedScore: 0,
  matchedKeywords: [],
  missingKeywords: [],
  sectionsFound: {},
  sectionScore: 0,
  formattingIssues: [],
  
  resumeName: '',
  jdText: '',
  resumeId: null,
  jdId: null,
  resultId: null,
  isOptimized: false,
  isLoading: false,
  loadingStep: '',
  loadingSub: '',

  toggleTheme: () => {
    set(state => {
      const nextTheme = state.theme === 'dark' ? 'light' : 'dark';
      if (typeof window !== 'undefined') {
        document.documentElement.setAttribute('data-theme', nextTheme);
      }
      return { theme: nextTheme };
    });
  },

  setCurrentTab: (tab) => {
    set({ currentTab: tab });
  },

  setJdText: (text) => {
    set({ jdText: text });
  },

  loadSampleProfile: async (profileKey) => {
    if (!profileKey) {
      get().resetAll();
      return;
    }
    
    // Dynamically load templates.js contents if available, or fall back to standard Software Engineer mock
    try {
      // Inline mock templates matching our previous definitions
      const sampleJds: Record<string, string> = {
        software_engineer: `Role: Senior Software Engineer (Frontend/Fullstack)\n\nRequirements:\n- 3+ years of experience with React, TypeScript, and modern frontend state management (Redux, Zustand).\n- Deep experience in designing and building RESTful APIs using Node.js and Express.\n- Solid understanding of database systems: PostgreSQL, MySQL, and Redis caching.\n- Familiarity with cloud services (AWS EC2, S3, RDS) and CI/CD pipelines (GitHub Actions, Docker).\n- Proven track record of optimizing web application performance, core web vitals, and system design.\n- Excellent collaboration skills and experience working in Agile/Scrum environments.`,
        data_analyst: `Role: Data Analyst (BI & Analytics)\n\nRequirements:\n- Strong knowledge of SQL for query optimization, data aggregation, and joining complex tables.\n- 2+ years of experience writing Python scripts for data manipulation (Pandas, NumPy).\n- Expertise in creating interactive dashboards and reports using Tableau or Power BI.\n- Experience with statistical analysis, hypothesis testing, and regression modeling.\n- Ability to clean messy data sources and perform Exploratory Data Analysis (EDA).\n- Good business communication skills to translate complex data insights to stakeholders.`,
        product_manager: `Role: Product Manager (Growth & Analytics)\n\nRequirements:\n- 3+ years of experience managing software products through the entire product lifecycle.\n- Strong product roadmap planning, backlog grooming, and Agile/Scrum execution skills.\n- Experience with analytics tools (Google Analytics, Mixpanel) and SQL to pull product metrics.\n- Track record of defining clear product requirements (PRDs) and user stories.\n- Proven experience conducting user research, A/B testing, and usability testing.\n- Strong stakeholder management skills to align engineering, design, and business teams.`,
        marketing_specialist: `Role: Digital Marketing Specialist\n\nRequirements:\n- 2+ years of experience in managing Paid Ads (PPC, Google Ads, Meta Ads) and budgets.\n- Proven SEO expertise (keyword research, on-page optimization, backlink strategies).\n- Deep experience using analytics platforms: Google Analytics 4 (GA4) and Google Search Console.\n- Ability to write copy for email campaigns, blog posts, and advertisements.\n- Experience running email marketing campaigns using Mailchimp or HubSpot.\n- Strong analytical skills to track ROI, click-through rates, and conversion metrics.`
      };

      const sampleResumes: Record<string, ResumeData> = {
        software_engineer: {
          personalInfo: { name: "Alex Johnson", email: "alex.johnson@email.com", phone: "+1 (555) 019-2834", github: "github.com/alexj-dev", linkedin: "linkedin.com/in/alexjohnson" },
          summary: "Motivated Software Developer with experience in building web applications. Proficient in JavaScript and React. Looking to join a fast-paced development team to contribute to scalable products and learn new technologies.",
          skills: ["JavaScript", "HTML", "CSS", "React", "Node.js", "Express", "Git", "SQL", "MongoDB"],
          experience: [
            { role: "Software Developer", company: "WebTech Solutions", duration: "2024 - Present", bullets: ["Built and maintained React web applications for client projects.", "Worked on REST APIs using Node.js and Express to connect frontend to database.", "Collaborated with QA engineers to debug code and resolve frontend layout issues.", "Participated in daily standups and sprint planning sessions with the engineering team."] },
            { role: "Junior Web Developer", company: "DevLaunch Studio", duration: "2023 - 2024", bullets: ["Assisted in developing client websites using HTML, CSS, and basic JavaScript.", "Wrote unit tests for components to ensure code reliability.", "Fixed bugs in CSS styling to align interfaces with design specifications."] }
          ],
          projects: [
            { name: "TaskTracker App", description: "A task management tool built with React. Features include dashboard updates, drag-and-drop tasks, and user authentication.", bullets: ["Created the frontend dashboard layout and user login flow.", "Integrated MongoDB for storing tasks and user records."] }
          ],
          education: [{ degree: "B.S. in Computer Science", school: "State University", year: "2023" }]
        },
        data_analyst: {
          personalInfo: { name: "Sarah Miller", email: "sarah.m@email.com", phone: "+1 (555) 038-4921", github: "github.com/sarahm-data", linkedin: "linkedin.com/in/sarahmiller-data" },
          summary: "Detail-oriented individual interested in working with data. Familiar with basic SQL and Excel. Seeking a Data Analyst role to help teams make decisions using data analytics.",
          skills: ["SQL", "Excel", "Python", "Tableau", "Data Entry", "Microsoft Word", "HTML"],
          experience: [
            { role: "Junior Analyst", company: "Retail Corp", duration: "2024 - Present", bullets: ["Ran SQL queries to pull weekly sales figures and put them in reports.", "Used Excel spreadsheets to format lists and clean up duplicate rows.", "Helped make basic Tableau charts showing category performance.", "Sent monthly slide decks to the store operations team."] },
            { role: "Data Assistant", company: "Insight Data Services", duration: "2023 - 2024", bullets: ["Entered data into tables and double-checked records for accuracy.", "Created charts and tables for client summaries."] }
          ],
          projects: [
            { name: "Sales Data Cleanup", description: "Cleaned a sales dataset using Python and summarized the findings in a chart.", bullets: ["Used a Python script to find and replace missing values in a CSV.", "Plotted the monthly sales trend using a basic bar chart."] }
          ],
          education: [{ degree: "B.A. in Statistics", school: "City College", year: "2023" }]
        }
      };

      // Set preset state
      const jdText = sampleJds[profileKey] || '';
      const originalResume = sampleResumes[profileKey] || sampleResumes['software_engineer'];
      
      set({
        jdText,
        originalResume,
        resumeName: `${profileKey}_Sample_Resume.docx`,
        resumeId: 999, // mock ID for preloaded
        isOptimized: false
      });
    } catch (e) {
      console.error(e);
    }
  },

  uploadResumeFile: async (file) => {
    set({ isLoading: true, loadingStep: 'Uploading Resume...', loadingSub: 'Extracting document text and metadata' });
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch(`${API_BASE_URL}/resume/upload`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        const errData = await response.text();
        throw new Error(`Upload failed (${response.status}): ${errData}`);
      }
      const data = await response.json();
      
      set({
        resumeId: data.resume_id,
        resumeName: data.filename,
        originalResume: data.structured_json,
        isOptimized: false
      });
    } catch (err: any) {
      console.error(err);
      alert(`File upload failed. Error: ${err.message || 'Network error (Backend might be waking up)'}`);
    } finally {
      set({ isLoading: false });
    }
  },

  removeResumeFile: () => {
    set({
      resumeName: '',
      originalResume: null,
      resumeId: null,
      isOptimized: false,
      currentTab: 'dashboard'
    });
  },

  runOptimization: async () => {
    const { resumeId, jdText, originalResume } = get();
    if (!resumeId && !originalResume) return;
    
    set({ isLoading: true, loadingStep: 'Extracting Keywords...', loadingSub: 'Scanning job requirements and extracting missing keywords' });
    
    try {
      // 1. Send / Analyze JD
      const jdFormData = new FormData();
      jdFormData.append('raw_text', jdText);
      
      const jdResponse = await fetch(`${API_BASE_URL}/jd/analyze`, {
        method: 'POST',
        body: jdFormData
      });
      
      if (!jdResponse.ok) throw new Error('JD Analysis failed');
      const jdData = await jdResponse.json();
      const jdId = jdData.jd_id;
      
      set({ jdId, loadingStep: 'Optimizing Resume Sections...', loadingSub: 'Re-wording bullet points and embedding target skills' });
      
      // 2. Perform optimization call
      // If mock resumeId is 999, generate a local fallback mock or send sample ID
      const activeResumeId = resumeId === 999 ? 1 : resumeId;
      
      // Since resume upload needs to exist in DB for optimization, we upload original mock if needed
      let finalResumeId = activeResumeId;
      if (resumeId === 999) {
        // Upload sample resume json text representation
        const mockFile = new File([JSON.stringify(originalResume)], get().resumeName, { type: 'application/json' });
        const mockFormData = new FormData();
        mockFormData.append('file', mockFile);
        
        const uploadResp = await fetch(`${API_BASE_URL}/resume/upload`, {
          method: 'POST',
          body: mockFormData
        });
        if (uploadResp.ok) {
          const uploadData = await uploadResp.json();
          finalResumeId = uploadData.resume_id;
          set({ resumeId: finalResumeId });
        }
      }
      
      const optFormData = new FormData();
      optFormData.append('resume_id', String(finalResumeId));
      optFormData.append('jd_id', String(jdId));
      
      const optResponse = await fetch(`${API_BASE_URL}/optimize`, {
        method: 'POST',
        body: optFormData
      });
      
      if (!optResponse.ok) {
        if (optResponse.status === 404) throw new Error('Resume not found');
        throw new Error('Optimization failed');
      }
      const optData = await optResponse.json();
      
      set({
        resultId: optData.result_id,
        originalScore: optData.original_score,
        optimizedScore: optData.optimized_score,
        matchedKeywords: optData.matched_keywords,
        missingKeywords: optData.missing_keywords,
        originalResume: optData.original_resume,
        optimizedResume: optData.optimized_resume,
        sectionsFound: optData.sections_found,
        sectionScore: optData.section_score,
        formattingIssues: optData.formatting_issues,
        isOptimized: true,
        currentTab: 'analysis'
      });
    } catch (err: any) {
      console.error(err);
      if (err.message === 'Resume not found') {
        alert('Your session expired because the backend restarted. Please refresh the page and re-upload your resume PDF.');
      } else {
        alert('Optimization failed. Please check if the backend is running properly.');
      }
    } finally {
      set({ isLoading: false });
    }
  },

  resetAll: () => {
    set({
      originalResume: null,
      optimizedResume: null,
      originalScore: 0,
      optimizedScore: 0,
      matchedKeywords: [],
      missingKeywords: [],
      sectionsFound: {},
      sectionScore: 0,
      formattingIssues: [],
      resumeName: '',
      jdText: '',
      resumeId: null,
      jdId: null,
      resultId: null,
      isOptimized: false,
      currentTab: 'dashboard'
    });
  }
}));
