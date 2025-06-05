# app/comparator.py

def compare_scores(ats_score, ai_score, jd_score):
    traditional_score = ats_score.get("score", 0)
    ai = ai_score if isinstance(ai_score, int) else 0
    jd = jd_score["score"] if jd_score and isinstance(jd_score, dict) else None

    messages = []
    if abs(traditional_score - ai) < 10:
        messages.append("Both traditional ATS and AI analysis are in strong agreement about your resume quality.")
    else:
        if traditional_score > ai:
            messages.append(
                f"Traditional scoring is higher ({traditional_score}) than AI ({ai}). "
                "This usually means your resume covers core sections and keywords, but could be lacking in context, formatting, or impact statements that the AI model looks for."
            )
        else:
            messages.append(
                f"AI scoring is higher ({ai}) than traditional ({traditional_score}). "
                "This usually means your resume demonstrates strengths (like achievements, clarity, leadership, or modern skills) that aren’t easily caught by keyword-based algorithms."
            )
    if jd is not None:
        if jd < 50:
            messages.append("Your resume has a low match with the job description. Consider adding more relevant keywords and skills.")
        elif jd < 80:
            messages.append("Your resume matches the JD reasonably well, but there’s room to tailor your skills and experience for a stronger fit.")
        else:
            messages.append("Your resume is highly aligned with the job description. Good job!")

    # Final recommendation
    if abs(traditional_score - ai) < 10:
        rec = "Both scoring methods are consistent. Use the AI suggestions to make further improvements."
    elif ai > traditional_score:
        rec = "Trust the AI score for final tweaks—focus on impactful statements, clarity, and modern best practices."
    else:
        rec = "Trust the traditional score for compliance, but review AI suggestions for advanced improvements."

    return {
        "traditional_vs_ai": " ".join(messages),
        "consistency": abs(traditional_score - ai) < 10,
        "recommendation": rec
    }
