# Jay Malhotra

AI/ML engineer and founding engineer at an AI startup, currently doing a Master of Management Analytics at McGill University in Montreal. I build production software and applied ML systems, mostly in education, healthcare and finance.

---

## What I'm working on

- **[AsOf](https://github.com/JustJay7/asof)**: checks an AI assistant's answers against the policy version in force on the customer's date, built on IBM Db2. Bitemporal tables and native vector search find the right clause version in one query, a LangGraph pipeline corrects or holds wrong answers, and every decision goes into a hash-chained Db2 ledger. Released 0 of 121 wrong drafts on frozen test sets. Built solo for IBM Db2Hack 2026. [Demo video](https://www.youtube.com/watch?v=mntehVWQn8E)
- **Ayebot** (founding engineer): B2B SaaS platform that gives universities an AI assistant and a secure communication layer. Backend, Flutter Android app and Next.js admin dashboard are all in production, around 84,500 lines of code. Features include end-to-end encrypted 1:1 and group chat, meeting chat, and a RAG chatbot over faculty knowledge. Pilot signed with a private university in India.
- **[SkillGuard](https://github.com/JustJay7/skillguard)**: lets you review what your personal AI agent learns before it learns it. SkillGuard intercepts skills a Hermes agent stages for itself, runs NVIDIA SkillEvaluator checks and generated attack probes against the real agent inside an isolated OpenShell sandbox, has Nemotron review the recorded behavior, and only installs the skill after explicit human approval, with rejection and version rollback built in. In testing, a repaired skill completed 8/8 receipt tasks with no attack-directed actions, while the original followed attacks in 4 of 6 cases. Built for the [Nebius x NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/) (Personal AI track), running on Nebius Token Factory with 1,000+ passing tests. [Demo](https://skillguard-evidence-demo.jaymalhotra.chatgpt.site)
- **Risk-factor disclosure research**: testing whether year-over-year changes in the Item 1A "Risk Factors" section of SEC 10-K and 10-Q filings forecast future realized volatility and crash risk. I handle the NLP and ML side, my co-author handles the finance side.
- **[Olist late-delivery prediction](https://github.com/JustJay7/olist-late-delivery)**: leading a 7-person team building a model that flags late e-commerce deliveries at the moment an order is approved.

## Recent wins

- **Prize winner, BSRM x ALDO Retail Gen AI Hackathon (2026)**: built [Perfect Pair](https://github.com/JustJay7/perfect-pair) with team Code Reapers, an agentic returns prototype for ALDO that resolves customer returns, supports store decisions and investigates return patterns, running on Claude through AWS Bedrock. I owned the full technical implementation.

---

## Projects

- **[KidneyStone-X](https://github.com/JustJay7/KidneyStone-X)**: end-to-end diagnostic pipeline for kidney stones on CT scans, with an EfficientNet classifier, YOLOv11 detection, U-Net segmentation and LLM-generated clinical reports.
- **[LLM Evaluation Pipeline](https://github.com/JustJay7/llm-evaluation-pipeline)**: measures the reliability of chatbot responses with semantic relevance scoring, hallucination detection, completeness analysis, and per-stage latency and cost tracking.
- **[Unibot](https://github.com/JustJay7/Unibot)**: campus chatbot built with Flask, SQLite and a custom LSTM intent classifier, with real-time extraction of professor specializations.
- **[Inter-School Competition Web App](https://github.com/JustJay7/Inter-School-Competition-Web-Application)**: full-stack ASP.NET platform for running inter-school competitions, covering registration, scheduling, scoring and results.
- **[MyVPN](https://github.com/JustJay7/MyVPN)**: self-built VPN on DigitalOcean using OpenVPN UDP and TCP, benchmarked against PPTP.

---

## Experience

- **Trench Group**: Data Engineer, McGill MMA capstone project (2026)
- **Perpex**: Software Development Intern (Aug to Nov 2025)
- **SmartInternz**: Google Cloud Generative AI Intern (Jul to Aug 2025)

## Education

- **McGill University**: Master of Management Analytics (in progress)
- **Bennett University**: BCA with AI specialization, CGPA 9.28/10, multiple Dean's List mentions

## Stack

- **Languages:** Python, SQL, C#, JavaScript
- **ML / AI:** scikit-learn, pandas, YOLO, U-Net, LSTMs, RAG, LLMs, LangChain, LangGraph
- **App / Web:** FastAPI, Flask, Next.js, Flutter, ASP.NET
- **Agents / Security:** NVIDIA Nemotron, Hermes, SkillEvaluator, OpenShell, Harbor, Docker
- **Data:** IBM Db2, SQL Server, MySQL, SQLite, Neo4j
- **Cloud:** AWS Bedrock, Google Cloud, Nebius Token Factory, DigitalOcean

---

## Contact

[LinkedIn](https://www.linkedin.com/in/jay-malhotraa/)
