CLUES = [
    {
        "id": 0,
        "riddle": "I am proof you paid; keep me safe after a purchase. What am I?",
        "hint": "You usually get me printed or emailed right after paying.",
        "answer": "receipt",
        "accepted": ["receipt", "invoice"],
        "reward": 10,
        "category": "Consumer Rights",
    },
    {
        "id": 1,
        "riddle": "Before escalating a complaint about a purchase, who should you contact first?",
        "hint": "Start with the business you bought from.",
        "answer": "the seller",
        "accepted": ["the seller", "seller", "shop", "the shop", "contact the seller", "store"],
        "reward": 10,
        "category": "Consumer Rights",
    },
    {
        "id": 2,
        "riddle": "What do citizens cast to help choose their leaders?",
        "hint": "It happens during an election.",
        "answer": "vote",
        "accepted": ["vote", "a vote", "ballot"],
        "reward": 10,
        "category": "Citizen Rights",
    },
    {
        "id": 3,
        "riddle": "What principle means treating everyone the same under the law?",
        "hint": "It starts with 'equal...'",
        "answer": "equality",
        "accepted": ["equality", "equal treatment", "equal rights"],
        "reward": 10,
        "category": "Fundamental Rights",
    },
    {
        "id": 4,
        "riddle": "What kind of information about you should companies protect online?",
        "hint": "It's information that identifies you.",
        "answer": "personal data",
        "accepted": ["personal data", "privacy", "personal information", "data"],
        "reward": 10,
        "category": "Digital Rights",
    },
    {
        "id": 5,
        "riddle": "If accused of a crime, who has the right to help defend you?",
        "hint": "They practice law.",
        "answer": "a lawyer",
        "accepted": ["a lawyer", "lawyer", "legal representation", "attorney"],
        "reward": 10,
        "category": "Legal Rights",
    },
    {
        "id": 6,
        "riddle": "What must your workplace provide to help keep you unharmed?",
        "hint": "It's about physical wellbeing at work.",
        "answer": "safety",
        "accepted": ["safety", "a safe environment", "safe working conditions"],
        "reward": 10,
        "category": "Workers' Rights",
    },
    {
        "id": 7,
        "riddle": "What should every child have free access to in most countries?",
        "hint": "It happens in schools.",
        "answer": "education",
        "accepted": ["education", "free education", "schooling"],
        "reward": 15,
        "category": "Education Rights",
    },
    {
        "id": 8,
        "riddle": "What 6-digit secret code should you never share with anyone claiming to be your bank?",
        "hint": "Banks send it by SMS to confirm a transaction.",
        "answer": "otp",
        "accepted": ["otp", "one time password", "one-time password"],
        "reward": 10,
        "category": "Digital Rights",
    },
    {
        "id": 9,
        "riddle": "What is the number of the IT Act section that punishes cheating by personation using a computer resource -- like a fake bank message?",
        "hint": "It's in the 60s, right after 66C.",
        "answer": "66d",
        "accepted": ["66d", "section 66d", "66-d"],
        "reward": 15,
        "category": "Digital Rights",
    },
    {
        "id": 10,
        "riddle": "What national portal should you visit to report a cybercrime in India?",
        "hint": "Its domain ends in .gov.in and starts with the word for online crime.",
        "answer": "cybercrime.gov.in",
        "accepted": ["cybercrime.gov.in", "cyber crime portal", "national cyber crime reporting portal"],
        "reward": 15,
        "category": "Digital Rights",
    },
    {
        "id": 11,
        "riddle": "Within how many hours must police ordinarily produce an arrested person before a magistrate in India?",
        "hint": "It's a full day, minus zero.",
        "answer": "24",
        "accepted": ["24", "24 hours", "twenty-four hours", "twenty four hours"],
        "reward": 10,
        "category": "Citizen Rights",
    },
]


class TreasureHuntGame:

    def total_clues(self) -> int:
        return len(CLUES)

    def get_clue(self, index: int):
        if index < 0 or index >= len(CLUES):
            return None

        clue = CLUES[index]

        return {
            "riddle": clue["riddle"],
            "hint": clue["hint"],
            "category": clue["category"],
        }

    def check_answer(self, index: int, answer: str) -> dict:
        if index < 0 or index >= len(CLUES):
            return {"error": "Clue not found."}

        clue = CLUES[index]
        submitted = str(answer).strip().lower()
        accepted_answers = clue.get("accepted", [clue["answer"]])

        correct = submitted in accepted_answers or submitted == clue["answer"]
        next_index = index + 1
        treasure_found = correct and next_index >= len(CLUES)

        return {
            "correct": correct,
            "points_earned": clue["reward"] if correct else 0,
            "next_index": next_index,
            "treasure_found": treasure_found,
            "category": clue["category"],
            "message": (
                "Correct! You found a rights clue."
                if correct
                else "Not quite. Check the hint and try again."
            ),
        }
