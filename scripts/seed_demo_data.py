"""Seed demo jobs for the live portfolio demo on Railway."""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
import uuid

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.database import SessionLocal, create_tables
from backend.models.job import Job

DEMO_JOBS = [
    {
        "title": "Senior Data Scientist", "company": "Microsoft",
        "location": "Redmond, WA", "remote_type": "hybrid",
        "employment_type": "full-time", "seniority": "senior", "source": "linkedin",
        "description": "Join the AI/ML team to build large-scale recommendation systems...",
        "claude_score": 92, "claude_summary": "Exceptional match — strong Python, ML, and Azure background aligns perfectly.",
        "claude_reasoning": '["Strong Python and scikit-learn experience matches", "Azure ML experience is a direct match", "NLP background aligns with team focus"]',
        "status": "approved",
    },
    {
        "title": "ML Engineer", "company": "Amazon",
        "location": "Seattle, WA (Remote)", "remote_type": "remote",
        "employment_type": "full-time", "seniority": "mid", "source": "indeed",
        "description": "Build and deploy ML models at scale for Amazon Alexa...",
        "claude_score": 85, "claude_summary": "Strong fit — experience with PyTorch and model deployment is directly relevant.",
        "claude_reasoning": '["PyTorch experience matches", "Model deployment experience relevant", "Collaborative team environment fits background"]',
        "status": "pending_review",
    },
    {
        "title": "Data Engineer", "company": "Tableau (Salesforce)",
        "location": "Seattle, WA", "remote_type": "hybrid",
        "employment_type": "full-time", "seniority": "mid", "source": "linkedin",
        "description": "Design and build data pipelines using Spark, dbt, and Snowflake...",
        "claude_score": 78, "claude_summary": "Good match with solid SQL and Python skills, though Spark experience could be stronger.",
        "claude_reasoning": '["SQL and Python align well", "Data pipeline experience is relevant", "Spark knowledge gap noted but learnable"]',
        "status": "pending_review",
    },
    {
        "title": "AI Research Scientist", "company": "Apple",
        "location": "Cupertino, CA (On-site)", "remote_type": "onsite",
        "employment_type": "full-time", "seniority": "senior", "source": "linkedin",
        "description": "Research and develop novel ML algorithms for Apple Intelligence...",
        "claude_score": 65, "claude_summary": "Reasonable match, though the role requires heavy research publication experience.",
        "claude_reasoning": '["ML foundations are strong", "Research publication gap is a concern", "Location is 800+ miles — remote not offered"]',
        "status": "pending_review",
    },
    {
        "title": "Analytics Engineer", "company": "Stripe",
        "location": "Remote", "remote_type": "remote",
        "employment_type": "full-time", "seniority": "mid", "source": "indeed",
        "description": "Build analytics infrastructure with dbt, BigQuery, and Looker...",
        "claude_score": 72, "claude_summary": "Solid fit for the analytics stack — dbt and SQL experience translates well.",
        "claude_reasoning": '["SQL expertise is a strong match", "dbt experience applicable", "FinTech domain is new but not a blocker"]',
        "status": "rejected",
    },
    {
        "title": "Data Scientist — Applied ML", "company": "Meta",
        "location": "Menlo Park, CA (Hybrid)", "remote_type": "hybrid",
        "employment_type": "full-time", "seniority": "mid", "source": "linkedin",
        "description": "Apply ML to social graph problems, ranking, and feed optimization...",
        "claude_score": 80, "claude_summary": "Strong technical fit, location is a stretch but hybrid could work.",
        "claude_reasoning": '["Python and ML depth is a strong match", "Graph ML is nice-to-have, not required", "Hybrid may involve some California travel"]',
        "status": "applied",
    },
]


def seed():
    create_tables()
    db = SessionLocal()
    try:
        existing = db.query(Job).count()
        if existing > 0:
            print(f"[seed] {existing} jobs already exist — skipping seed")
            return

        for i, d in enumerate(DEMO_JOBS):
            job = Job(
                id=str(uuid.uuid4()),
                source=d["source"],
                external_id=f"demo_{i}",
                url=f"https://example.com/job/{i}",
                title=d["title"],
                company=d["company"],
                location=d["location"],
                remote_type=d["remote_type"],
                employment_type=d["employment_type"],
                seniority=d["seniority"],
                description=d["description"],
                scraped_at=datetime.utcnow() - timedelta(hours=i),
                claude_score=d["claude_score"],
                claude_summary=d["claude_summary"],
                claude_reasoning=d["claude_reasoning"],
                claude_red_flags="[]",
                status=d["status"],
            )
            db.add(job)
        db.commit()
        print(f"[seed] Inserted {len(DEMO_JOBS)} demo jobs")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
