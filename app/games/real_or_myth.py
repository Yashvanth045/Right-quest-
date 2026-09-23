import random


STATEMENTS = [
    {
        "id": 1,
        "statement": "A consumer should keep proof of payment.",
        "answer": "real",
        "category": "Consumer Rights",
        "explanation": "Receipts and invoices help you prove a purchase if a dispute arises.",
    },
    {
        "id": 2,
        "statement": "Once you buy something, a shop never has to accept a return, even if it's faulty.",
        "answer": "myth",
        "category": "Consumer Rights",
        "explanation": "Most consumer protection laws require remedies (repair, replacement, or refund) for faulty goods.",
    },
    {
        "id": 3,
        "statement": "Citizens generally have the right to vote in elections.",
        "answer": "real",
        "category": "Citizen Rights",
        "explanation": "Voting is a core civic right that lets citizens choose their representatives.",
    },
    {
        "id": 4,
        "statement": "You must agree with the majority to take part in a public consultation.",
        "answer": "myth",
        "category": "Citizen Rights",
        "explanation": "Public consultations exist precisely so differing views can be heard, not just majority ones.",
    },
    {
        "id": 5,
        "statement": "Everyone has the right to equal treatment under the law, regardless of gender or race.",
        "answer": "real",
        "category": "Fundamental Rights",
        "explanation": "Equality before the law is a cornerstone of most constitutions and human rights frameworks.",
    },
    {
        "id": 6,
        "statement": "Freedom of speech means you can say anything with no legal consequences at all.",
        "answer": "myth",
        "category": "Fundamental Rights",
        "explanation": "Free speech is protected, but it usually has limits, such as incitement to violence or defamation.",
    },
    {
        "id": 7,
        "statement": "You generally have a right to know what personal data a company holds about you.",
        "answer": "real",
        "category": "Digital Rights",
        "explanation": "Many privacy laws grant individuals the right to access data companies hold on them.",
    },
    {
        "id": 8,
        "statement": "Once you accept an app's terms, the company can freely sell your data to anyone.",
        "answer": "myth",
        "category": "Digital Rights",
        "explanation": "Most privacy regulations require clear consent before personal data can be shared or sold.",
    },
    {
        "id": 9,
        "statement": "Workers have the right to a reasonably safe working environment.",
        "answer": "real",
        "category": "Workers' Rights",
        "explanation": "Workplace safety obligations are a standard part of labor law in most countries.",
    },
    {
        "id": 10,
        "statement": "An employer can change your agreed pay without your consent.",
        "answer": "myth",
        "category": "Workers' Rights",
        "explanation": "Pay is normally part of an employment agreement and can't be changed unilaterally.",
    },
    {
        "id": 11,
        "statement": "If accused of a crime, you generally have the right to legal representation.",
        "answer": "real",
        "category": "Legal Rights",
        "explanation": "The right to a defense/legal counsel is a widely recognized legal protection.",
    },
    {
        "id": 12,
        "statement": "Every child has a right to free basic education in most countries.",
        "answer": "real",
        "category": "Education Rights",
        "explanation": "Free, compulsory basic education is a right recognized in many national constitutions and treaties.",
    },
    {
        "id": 13,
        "statement": "As an Indian consumer, you have the right to be protected against goods and services that are hazardous to your life.",
        "answer": "real",
        "category": "Consumer Rights",
        "explanation": "This is the Right to Safety under India's consumer protection framework -- goods and services must meet immediate needs without compromising long-term safety.",
    },
    {
        "id": 14,
        "statement": "A consumer complaint is only worth pursuing if the financial loss is large.",
        "answer": "myth",
        "category": "Consumer Rights",
        "explanation": "The Right to Seek Redressal covers genuine grievances of any size -- a small individual complaint can still expose a practice that harms many other consumers.",
    },
    {
        "id": 15,
        "statement": "If arrested in India, the police must ordinarily produce you before a magistrate within 24 hours.",
        "answer": "real",
        "category": "Citizen Rights",
        "explanation": "This is part of the Right to Liberty -- it prevents arbitrary detention without judicial oversight.",
    },
    {
        "id": 16,
        "statement": "The right to equality means the State can restrict your rights based on religion, race, caste or sex if it's convenient.",
        "answer": "myth",
        "category": "Citizen Rights",
        "explanation": "Right to Equality specifically forbids the State from discriminating against citizens on grounds of religion, race, language, caste, or sex.",
    },
    {
        "id": 17,
        "statement": "Sending a fake message pretending to be someone's bank to trick them into revealing an OTP is a punishable offence in India.",
        "answer": "real",
        "category": "Digital Rights",
        "explanation": "This is 'cheating by personation using a computer resource', punishable under Section 66D of the Information Technology Act, 2000.",
    },
    {
        "id": 18,
        "statement": "If a company in India is careless with your personal data and it leaks, you have no legal recourse.",
        "answer": "myth",
        "category": "Digital Rights",
        "explanation": "Section 43A of the IT Act makes a company liable to pay compensation if negligence in maintaining reasonable security practices causes you wrongful loss.",
    },
    {
        "id": 19,
        "statement": "Impersonating someone else's digital identity, like using their password without permission, can lead to up to 3 years imprisonment in India.",
        "answer": "real",
        "category": "Digital Rights",
        "explanation": "Section 66C of the IT Act punishes identity theft -- fraudulent or dishonest use of another person's electronic signature, password, or unique identification feature.",
    },
    {
        "id": 20,
        "statement": "India has a dedicated national helpline and portal for reporting cybercrime.",
        "answer": "real",
        "category": "Digital Rights",
        "explanation": "The National Cyber Crime Reporting Portal (cybercrime.gov.in) and the 1930 helpline let citizens report incidents like phishing, hacking, and online fraud.",
    },
]


class RealOrMythGame:

    def get_random_statement(self, exclude_ids=None) -> dict:
        exclude_ids = exclude_ids or []
        available = [s for s in STATEMENTS if s["id"] not in exclude_ids]

        if not available:
            available = STATEMENTS

        statement = random.choice(available)

        return {
            "id": statement["id"],
            "statement": statement["statement"],
            "category": statement["category"],
        }

    def check_answer(self, statement_id, answer: str) -> dict:
        statement = next(
            (s for s in STATEMENTS if s["id"] == statement_id),
            None
        )

        if not statement:
            return {"error": "Statement not found."}

        is_correct = str(answer).strip().lower() == statement["answer"]

        return {
            "correct": is_correct,
            "points_earned": 10 if is_correct else 0,
            "explanation": statement["explanation"],
            "category": statement["category"],
        }
