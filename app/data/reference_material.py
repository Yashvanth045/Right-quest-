"""
Condensed reference material sourced from:
  - Consumer Protection Act, 2019 / Ministry of Consumer Affairs (consumeraffairs.gov.in)
  - Citizen Rights Protection Council (crpc.in)
  - The Information Technology Act, 2000

Fed into the AI prompt in app/services/ai_service.py so generated questions
are grounded in real material rather than invented from scratch.
"""

REFERENCE_MATERIAL = {
    "Consumer Rights": """
Consumer Rights (Ministry of Consumer Affairs, India):
- Right to Safety: protection against goods/services hazardous to life and property.
- Right to be Informed: right to know quality, quantity, potency, purity, standard and
  price of goods, to guard against unfair trade practices.
- Right to Choose: assured access to a variety of goods/services at competitive prices.
- Right to be Heard: consumer interests receive due consideration at appropriate forums;
  right to be represented in relevant committees.
- Right to Seek Redressal: right to fair settlement of genuine grievances against unfair
  trade practices or exploitation.
- Right to Consumer Education: right to acquire knowledge and skill to be an informed
  consumer throughout life; ignorance (especially among rural consumers) causes
  exploitation.
Source: Consumer Protection Act, 2019.
""",
    "Citizen Rights": """
Civil / Citizen Rights (Citizen Rights Protection Council):
- Right of Life: the State must provide for personal safety; includes right to
  self-defense and prevention of suicide.
- Right to Liberty: free movement; no arbitrary detention; a person arrested in India
  must ordinarily be produced before the nearest magistrate within 24 hours of arrest.
- Right to Property: recognized as important for incentive to work and social good,
  though not absolute.
- Right to Contract: citizens can live, work, earn, and freely contract on the basis of
  equality with other citizens.
- Right to Freedom of Speech: citizens may freely criticize the policies and actions of
  authorities; no society functions without free expression.
- Freedom of Press: right to publish what one may lawfully speak.
- Right to Form Association: citizens may form political, cultural, educational,
  philanthropic or religious associations.
- Right to Religion and Conscience: complete liberty of belief and worship; the State
  does not interfere with citizens' religion.
- Right to Culture and Language: citizens may preserve their own language, script and
  culture, and are free to be educated in any institution in the country.
- Right to Equality: absence of legal discrimination on grounds of religion, race,
  language, caste or sex; equal protection of law for all.
- Right to Family: includes right to marriage, custody and control of children, and
  right of inheritance.
- These civil rights are not absolute -- they may be restricted in the interest of the
  State, e.g. during war or a national emergency.
""",
    "Digital Rights": """
Digital Rights & the Information Technology Act, 2000 (India):
- Section 43: unauthorised access, downloading data, introducing viruses, or damaging a
  computer/computer system makes a person liable to pay damages by way of compensation.
- Section 43A: a body corporate that is negligent in maintaining reasonable security
  practices for sensitive personal data it holds is liable to pay compensation for any
  resulting wrongful loss.
- Section 66: dishonestly or fraudulently doing any act referred to in Section 43 is
  punishable with imprisonment up to 3 years or fine up to five lakh rupees, or both.
- Section 66C: punishment for identity theft -- fraudulent or dishonest use of another
  person's electronic signature, password, or unique identification feature.
- Section 66D: punishment for cheating by personation using a computer resource or
  communication device (e.g. impersonating a bank via SMS/email/link).
- Section 66E: punishment for violation of privacy, e.g. capturing or transmitting the
  image of a person's private area without consent.
- Section 66F: cyber terrorism -- acts intended to threaten India's unity, security or
  sovereignty via computer resources; punishable up to life imprisonment.
- Section 69B / 70B: establishes CERT-In (Indian Computer Emergency Response Team) as
  the national agency for cyber incident response, alerts, and coordination.
- Section 79: intermediaries (platforms, ISPs) are generally exempt from liability for
  third-party content if they observe due diligence and act on notice.
- Reporting: cybercrime in India can be reported at cybercrime.gov.in or via the 1930
  national cybercrime helpline.
""",
    "Fundamental Rights": """
Fundamental rights principles commonly taught alongside civil and digital rights:
- Equality before the law regardless of gender, race, religion or background.
- Freedom of expression, balanced with reasonable restrictions (e.g. incitement,
  defamation).
- Right to a fair hearing/legal representation if accused of an offence.
- Right to safe working conditions and fair treatment in the workplace.
""",
}


def get_reference_text(category: str) -> str:
    """Return the reference excerpt for a category, or a combined excerpt for
    'Mixed Rights' / unrecognised categories so generation still has grounding."""
    if category in REFERENCE_MATERIAL:
        return REFERENCE_MATERIAL[category].strip()

    return "\n\n".join(text.strip() for text in REFERENCE_MATERIAL.values())
