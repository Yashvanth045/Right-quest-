import random


class SnakesAndLadders:
    """Rights-themed Snakes & Ladders. Landing on certain squares teaches
    a short lesson spanning multiple categories of rights."""

    SNAKES = {
        17: 7,
        54: 34,
        62: 19,
        87: 49,
        98: 79,
    }

    LADDERS = {
        3: 22,
        8: 30,
        28: 55,
        40: 70,
        50: 69,
        63: 81,
    }

    # square -> (category, lesson)
    LESSONS = {
        7: ("Consumer Rights", "Consumers have the right to accurate product information."),
        19: ("Legal Rights", "Everyone has the right to a fair hearing before judgment."),
        22: ("Citizen Rights", "Citizens can take part in public decision-making, such as voting."),
        30: ("Fundamental Rights", "Everyone has the right to equal treatment under the law."),
        34: ("Consumer Rights", "Keep evidence, such as receipts, when making a complaint."),
        49: ("Workers' Rights", "Workers have the right to a safe working environment."),
        55: ("Fundamental Rights", "Equal treatment at work is a basic rights principle."),
        69: ("Digital Rights", "You have a right to know what personal data a company holds about you."),
        70: ("Digital Rights", "Protect your personal information when signing up for online services."),
        79: ("Legal Rights", "You have the right to legal representation if accused of a crime."),
        81: ("Citizen Rights", "Freedom of expression lets citizens voice opinions peacefully."),
        12: ("Digital Rights", "Never share your OTP -- doing so can enable identity theft under Section 66C of the IT Act, 2000."),
        45: ("Citizen Rights", "If arrested, you must ordinarily be produced before a magistrate within 24 hours."),
        60: ("Digital Rights", "Report phishing or cybercrime on cybercrime.gov.in or via the 1930 helpline."),
        90: ("Consumer Rights", "The Right to be Informed means you can insist on knowing a product's quality, quantity, and price before buying."),
        95: ("Digital Rights", "Companies must maintain reasonable security for your data -- Section 43A lets you claim compensation if negligence causes a breach."),
        100: ("Education Rights", "Every child has a right to free basic education in most countries."),
    }

    def move(self, current_position: int) -> dict:
        dice = random.randint(1, 6)
        new_position = min(current_position + dice, 100)

        event = None

        if new_position in self.SNAKES:
            new_position = self.SNAKES[new_position]
            event = "snake"
        elif new_position in self.LADDERS:
            new_position = self.LADDERS[new_position]
            event = "ladder"

        category, lesson = self.LESSONS.get(
            new_position,
            ("Rights", "Keep learning about your rights.")
        )

        return {
            "dice": dice,
            "position": new_position,
            "event": event,
            "category": category,
            "lesson": lesson,
            "completed": new_position == 100,
            "points_earned": 5,
        }
