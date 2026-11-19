from yojana_mitra.explain import _extractive_answer, schemes_named_in


def test_scheme_named_in_question_prefers_most_specific_name():
    assert schemes_named_in("How do I apply for PM-KISAN?") == ["pm_kisan"]
    assert schemes_named_in("pm kisan maan dhan pension age") == ["pm_kisan_maandhan"]
    assert schemes_named_in("What documents do I need for Talliki Vandanam?") == ["talliki_vandanam"]
    assert schemes_named_in("Who can get a pension?") == []


def test_offline_answer_skips_title_prefix_and_prefers_amounts():
    title = "PM Internship Scheme"
    chunks = [
        {"title": title, "text": f"{title} (పీఎం ఇంటర్న్‌షిప్ పథకం) - how to apply: Step 1: Register on the portal."},
        {"title": title, "text": f"{title} (పీఎం ఇంటర్న్‌షిప్ పథకం) - benefits: 12 months of real work experience. "
                                 "Monthly stipend of ₹5,000 plus a one-time grant of ₹6,000."},
    ]
    ans = _extractive_answer("How much money does PM Internship give?", chunks)
    assert "- benefits:" not in ans and "(పీఎం" not in ans
    assert "₹5,000" in ans


def test_offline_answer_does_not_repeat_the_same_sentence():
    title = "NTR Bharosa Pension – Widows"
    same = "Widows aged 18 and above are eligible for the widow pension."
    chunks = [{"title": title, "text": f"{title}. {same}"},
              {"title": title, "text": f"{title} - eligibility: {same} Pension is paid on the 1st of every month."}]
    ans = _extractive_answer("Who can get the widow pension?", chunks)
    assert ans.count(same) == 1
