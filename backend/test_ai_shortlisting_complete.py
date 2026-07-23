#!/usr/bin/env python3
"""
Complete end-to-end test of AI-powered shortlisting functionality.
Tests:
1. Authentication
2. Get existing job and candidates (from seeded data)
3. Fetch AI rankings for a job
4. Verify explainability insights
"""
import asyncio
import httpx
import json
from pprint import pprint

API_BASE = "http://localhost:8000/api/v1"

async def test_ai_shortlisting():
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("=" * 70)
        print("🚀 ATS AI-POWERED SHORTLISTING TEST")
        print("=" * 70)
        
        # Step 1: Login
        print("\n1️⃣  AUTHENTICATING AS ADMIN...")
        login_res = await client.post(
            f"{API_BASE}/auth/login",
            json={"email": "admin@techcorp.com", "password": "password123"}
        )
        
        if login_res.status_code != 200:
            print(f"❌ Login failed: {login_res.status_code}")
            print(login_res.text)
            return
        
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Authentication successful")
        
        # Step 2: List jobs
        print("\n2️⃣  FETCHING AVAILABLE JOBS...")
        jobs_res = await client.get(f"{API_BASE}/candidates/jobs", headers=headers)
        
        if jobs_res.status_code != 200:
            print(f"❌ Failed to list jobs: {jobs_res.status_code}")
            print(jobs_res.text)
            return
        
        jobs = jobs_res.json()
        if not jobs:
            print("❌ No jobs found")
            return
        
        print(f"✅ Found {len(jobs)} jobs:")
        for job in jobs:
            print(f"   - {job['title']} (ID: {job['id']})")
        
        # Use first job for testing
        job_id = jobs[0]["id"]
        job_title = jobs[0]["title"]
        print(f"\n   📍 Using job: {job_title} (ID: {job_id})")
        
        # Step 3: Get rankings for the job
        print("\n3️⃣  FETCHING AI RANKINGS FOR JOB...")
        rankings_res = await client.get(
            f"{API_BASE}/rankings/candidates/for-job/{job_id}",
            headers=headers
        )
        
        if rankings_res.status_code != 200:
            print(f"❌ Failed to fetch rankings: {rankings_res.status_code}")
            print(rankings_res.text)
            return
        
        rankings = rankings_res.json()
        if not rankings:
            print("⚠️  No candidates ranked for this job")
        else:
            print(f"✅ Got {len(rankings)} candidates ranked:")
            print("\n" + "="*70)
            print("AI SHORTLIST RANKINGS")
            print("="*70)
            
            for idx, ranking in enumerate(rankings, 1):
                print(f"\n🏆 Rank #{idx}: {ranking.get('candidate_name', 'N/A')} ({ranking.get('candidate_email', 'N/A')})")
                print(f"   📊 Match Score:  {round(ranking.get('match_score', 0) * 100, 1)}%")
                print(f"   💯 Confidence:   {round(ranking.get('confidence', 0) * 100, 1)}%")
                if 'embedding_similarity' in ranking:
                    print(f"   🔍 Semantic Sim: {round(ranking['embedding_similarity'] * 100, 1)}%")
                print(f"   Application ID: {ranking.get('application_id', 'N/A')}")
                print("-" * 70)
        
        # Step 4: Get explainability for top candidate
        if rankings and len(rankings) > 0:
            print("\n4️⃣  FETCHING AI INSIGHTS FOR TOP CANDIDATE...")
            top_candidate = rankings[0]
            candidate_id = top_candidate['candidate_id']
            
            explain_res = await client.get(
                f"{API_BASE}/rankings/explain/{candidate_id}/{job_id}",
                headers=headers
            )
            
            if explain_res.status_code == 200:
                explain_data = explain_res.json()
                print(f"✅ Got explanations for: {top_candidate['candidate_name']}")
                print("\n" + "="*70)
                print("EXPLAINABILITY INSIGHTS")
                print("="*70)
                
                # Print summary
                if 'summary' in explain_data:
                    print(f"\n📋 SUMMARY:\n{explain_data['summary']}")
                
                # Print strengths
                if 'strengths' in explain_data and explain_data['strengths']:
                    print(f"\n✅ STRENGTHS:")
                    for strength in explain_data['strengths']:
                        print(f"   • {strength}")
                
                # Print weaknesses
                if 'weaknesses' in explain_data and explain_data['weaknesses']:
                    print(f"\n⚠️  WEAKNESSES:")
                    for weakness in explain_data['weaknesses']:
                        print(f"   • {weakness}")
                
                # Print skill analysis
                if 'skill_analysis' in explain_data:
                    print(f"\n🛠️  SKILL ANALYSIS:")
                    print(f"   {explain_data['skill_analysis']}")
                
                # Print recommendations
                if 'recommendations' in explain_data:
                    print(f"\n💡 RECOMMENDATIONS:")
                    print(f"   {explain_data['recommendations']}")
            else:
                print(f"⚠️  Could not fetch explanations: {explain_res.status_code}")
                print(explain_res.text)
        
        # Step 5: Get match score breakdown
        if rankings and len(rankings) > 0:
            print("\n5️⃣  FETCHING MATCH SCORE BREAKDOWN...")
            top_candidate = rankings[0]
            candidate_id = top_candidate['candidate_id']
            
            score_res = await client.get(
                f"{API_BASE}/rankings/match-score/{candidate_id}/{job_id}",
                headers=headers
            )
            
            if score_res.status_code == 200:
                score_data = score_res.json()
                print(f"✅ Got score breakdown:")
                print("\n" + "="*70)
                print("SCORE BREAKDOWN")
                print("="*70)
                
                print(f"\nTotal Score: {round(score_data.get('total_score', 0) * 100, 1)}%")
                
                if 'component_scores' in score_data:
                    print("\nComponent Breakdown:")
                    for component, score in score_data['component_scores'].items():
                        print(f"  • {component}: {round(score * 100, 1)}%")
                
                if 'feature_scores' in score_data:
                    print("\nFeature Scores:")
                    for feature, score in score_data['feature_scores'].items():
                        print(f"  • {feature}: {round(score * 100, 1)}%")
            else:
                print(f"⚠️  Could not fetch score breakdown: {score_res.status_code}")
                print(score_res.text)
        
        print("\n" + "="*70)
        print("✅ TEST COMPLETED SUCCESSFULLY")
        print("="*70)

if __name__ == "__main__":
    asyncio.run(test_ai_shortlisting())
