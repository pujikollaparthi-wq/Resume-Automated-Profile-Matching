"""
Sample Resumes and Job Descriptions for instant 1-click testing and demonstrations.
"""

SAMPLE_RESUMES = {
    "ml_senior": {
        "id": "ml_senior",
        "name": "Alex Morgan",
        "title": "Senior AI & NLP Engineer",
        "experience": "5+ years",
        "text": """Alex Morgan
Email: alex.morgan@ai-lab.io | Phone: +1 (555) 234-5678 | San Francisco, CA
LinkedIn: linkedin.com/in/alexmorgan-ai | GitHub: github.com/alexmorgan-ai

PROFESSIONAL SUMMARY:
Senior AI & Machine Learning Engineer with 5+ years of experience specializing in Natural Language Processing (NLP), Transformer architectures, and scalable production AI pipelines. Expert in training and deploying PyTorch models with FastAPI and Docker.

CORE SKILLS:
- Languages: Python, SQL, Bash, C++
- AI / ML: Machine Learning, Deep Learning, NLP, Natural Language Processing, Transformers, PyTorch, Scikit-Learn, Pandas, NumPy, HuggingFace, LLM, LangChain
- Cloud & MLOps: Docker, Kubernetes, AWS, EC2, S3, CI/CD, Git, Linux
- Frameworks & APIs: FastAPI, Flask, REST API, Microservices

WORK EXPERIENCE:
Senior Machine Learning Engineer | CogniTech AI (2022 - Present)
- Engineered enterprise NLP document analysis pipelines utilizing BERT and Transformer models, improving classification accuracy by 28%.
- Developed scalable microservices in Python using FastAPI and Docker deployed on AWS Kubernetes clusters.
- Implemented TF-IDF and semantic vector embeddings for candidate profile matching and search retrieval.
- Reduced model inference latency by 42% utilizing PyTorch optimization and ONNX runtime.

Machine Learning Engineer | DataCore Systems (2019 - 2022)
- Built automated text extraction and sentiment analysis systems handling 2M+ records daily.
- Implemented Scikit-Learn classifiers and predictive pipelines with automated CI/CD deployment via GitHub Actions.
- Mentored junior engineers in ML best practices and reproducible data science pipelines.

EDUCATION:
M.S. in Computer Science (Machine Learning Specialization) | University of California, Berkeley
B.S. in Computer Science | University of Washington"""
    },
    "fullstack_dev": {
        "id": "fullstack_dev",
        "name": "Priya Sharma",
        "title": "Senior Full Stack Python & React Developer",
        "experience": "4+ years",
        "text": """Priya Sharma
Email: priya.sharma@cloudtech.dev | Phone: +1 (555) 987-6543 | Austin, TX
GitHub: github.com/priyasharma-dev | Portfolio: priyasharma.io

PROFESSIONAL SUMMARY:
Dynamic Full Stack Developer with 4+ years of expertise architecting scalable cloud web applications using Python (FastAPI, Django), React, modern JavaScript/TypeScript, and PostgreSQL. Proven track record delivering responsive UIs and robust REST APIs.

CORE SKILLS:
- Languages: Python, JavaScript, TypeScript, SQL, HTML5, CSS3, HTML, CSS
- Frontend: React, Redux, TailwindCSS, Bootstrap, Vite, Responsive Design
- Backend: FastAPI, Django, Flask, Node.js, Express, REST API, RESTful APIs, WebSockets
- Databases: PostgreSQL, MySQL, Redis, MongoDB
- DevOps & Tools: Docker, Git, GitHub, Linux, CI/CD, Postman, Agile, Scrum

EXPERIENCE:
Senior Full Stack Engineer | ApexCloud Solutions (2022 - Present)
- Designed and maintained customer-facing web portals utilizing React, TypeScript, and FastAPI with PostgreSQL backend.
- Developed real-time streaming notifications using WebSockets and Redis Pub/Sub, boosting user engagement by 35%.
- Containerized development environments with Docker and configured automated GitHub Actions CI/CD pipelines.
- Spearheaded migration of legacy REST APIs to high-performance asynchronous FastAPI endpoints.

Software Engineer | NexaDigital (2020 - 2022)
- Built interactive dashboard UI components in React and modern CSS for financial analytics.
- Created robust relational database schemas and optimized complex SQL queries in PostgreSQL.
- Collaborated in cross-functional Agile Scrum teams conducting sprint planning and code reviews.

EDUCATION:
B.Tech in Information Technology | National Institute of Technology (NIT)"""
    },
    "devops_eng": {
        "id": "devops_eng",
        "name": "Marcus Vance",
        "title": "Cloud DevOps & Platform Engineer",
        "experience": "4+ years",
        "text": """Marcus Vance
Email: marcus.vance@infraops.net | Phone: +1 (555) 345-6789 | Seattle, WA
GitHub: github.com/marcusvance | Certifications: AWS Certified Solutions Architect, CKA

SUMMARY:
Cloud Infrastructure and Platform Engineer with 4+ years specializing in automated cloud architecture on AWS, container orchestration with Kubernetes, and Infrastructure as Code with Terraform and Ansible.

TECHNICAL SKILLS:
- Cloud: AWS, EC2, S3, ECS, EKS, CloudFormation, Azure
- Containers & Orchestration: Docker, Kubernetes, Helm
- IaC & Automation: Terraform, Ansible, Bash, Shell, Python scripting
- CI/CD & VCS: Jenkins, GitHub Actions, GitLab CI, Git
- Monitoring & OS: Prometheus, Grafana, Linux, Ubuntu, Nginx, Microservices

WORK EXPERIENCE:
Cloud DevOps Engineer | OmniScale Infrastructure (2022 - Present)
- Automated deployment of multi-region AWS cloud infrastructure using Terraform modules, reducing provisioning time by 75%.
- Managed Kubernetes production clusters hosting 50+ microservices with zero-downtime rolling deployments.
- Implemented continuous integration pipelines in GitHub Actions and Jenkins for automated test suites and Docker builds.
- Configured Prometheus and Grafana alerting monitoring system, maintaining 99.99% service availability.

DevOps Systems Administrator | CloudMatrix (2020 - 2022)
- Maintained fleet of 100+ Linux enterprise servers, automating security patching using Ansible and Bash.
- Deployed Nginx reverse proxies, SSL certificates, and optimized network routing.

EDUCATION:
B.S. in Network Engineering | Oregon State University"""
    },
    "junior_intern": {
        "id": "junior_intern",
        "name": "Jordan Lee",
        "title": "Junior Web Developer",
        "experience": "1 year",
        "text": """Jordan Lee
Email: jordan.lee@mail.com | Phone: +1 (555) 789-0123 | Chicago, IL
GitHub: github.com/jordanlee-dev

SUMMARY:
Enthusiastic Junior Developer with 1 year of foundational experience in HTML, CSS, JavaScript, and basic Python scripting. Eager to contribute to web projects and learn modern frameworks.

SKILLS:
- HTML5, CSS3, JavaScript, Git, Python basics, Problem Solving

EXPERIENCE:
Junior Web Developer Intern | LocalWeb Agency (2023 - 2024)
- Assisted senior developers in designing static client landing pages using HTML5, CSS, and basic JavaScript.
- Maintained code repositories using Git and GitHub.
- Performed browser testing and responsive layout adjustments.

EDUCATION:
Associate Degree in Web Development | City College of Chicago (2023)"""
    }
}

SAMPLE_JOBS = {
    "ml_engineer": {
        "id": "ml_engineer",
        "title": "Senior Machine Learning Engineer",
        "company": "DeepLogic AI",
        "department": "Artificial Intelligence / Data Science",
        "experience_required": "4+ years",
        "skills": ["Python", "Machine Learning", "NLP", "PyTorch", "Scikit-Learn", "FastAPI", "Docker", "AWS", "Transformers", "Git"],
        "description": """We are seeking a Senior Machine Learning Engineer to design, deploy, and scale production AI systems and NLP pipelines.
Responsibilities:
- Build and fine-tune transformer models, LLMs, and NLP architectures using PyTorch and HuggingFace.
- Implement feature extraction, TF-IDF vectorization, semantic embeddings, and vector databases.
- Develop scalable REST APIs with FastAPI and Docker for model inference.
- Collaborate with MLOps pipelines using CI/CD, Kubernetes, and AWS cloud services.
Requirements:
- Strong proficiency in Python, NumPy, Pandas, Scikit-Learn, and PyTorch or TensorFlow.
- Experience with Natural Language Processing (NLP), tokenization, text embeddings, and Transformers.
- Familiarity with Docker, Kubernetes, AWS, Git, and RESTful APIs.
- Excellent problem-solving skills and teamwork."""
    },
    "fullstack_dev": {
        "id": "fullstack_dev",
        "title": "Full Stack Python & React Developer",
        "company": "CloudVenture Technologies",
        "department": "Software Engineering",
        "experience_required": "3+ years",
        "skills": ["Python", "React", "JavaScript", "FastAPI", "PostgreSQL", "Docker", "HTML", "CSS", "Git", "REST API"],
        "description": """We are looking for a versatile Full Stack Developer to build modern cloud applications.
Responsibilities:
- Build responsive frontend dashboards with React, JavaScript, modern CSS, and HTML5.
- Develop high-performance backend microservices with Python, FastAPI or Django, and PostgreSQL.
- Implement user authentication, role-based access control, and RESTful APIs.
- Deploy applications using Docker, Linux, and automated CI/CD pipelines.
Requirements:
- Hands-on experience with Python, React, JavaScript, HTML, CSS, and TypeScript.
- Strong knowledge of relational databases (PostgreSQL or MySQL) and Redis caching.
- Familiarity with Git, Docker, REST APIs, and Agile development methodology.
- Strong communication and analytical mindset."""
    },
    "devops_eng": {
        "id": "devops_eng",
        "title": "Cloud DevOps & Platform Engineer",
        "company": "OmniScale Infrastructure",
        "department": "DevOps & Infrastructure",
        "experience_required": "3-5 years",
        "skills": ["AWS", "Docker", "Kubernetes", "Terraform", "Linux", "CI/CD", "GitHub Actions", "Python", "Bash"],
        "description": """Join our platform team as a Cloud DevOps Engineer to automate and scale our infrastructure.
Responsibilities:
- Architect reliable cloud infrastructure on AWS and Azure using Terraform and Ansible.
- Manage Kubernetes clusters, Helm charts, and containerized microservices.
- Design CI/CD release pipelines with GitHub Actions and Jenkins.
- Monitor system reliability, Linux systems performance, and automated logging.
Requirements:
- Deep expertise in AWS, Docker, Kubernetes, Terraform, Linux, and Bash scripting.
- Experience with CI/CD tools (GitHub Actions, Jenkins) and Python automation.
- Knowledge of cloud networking, security, and Git."""
    }
}
