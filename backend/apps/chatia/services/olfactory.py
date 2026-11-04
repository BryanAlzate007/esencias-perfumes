import re
import unicodedata

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from apps.perfumes.models import Perfume


FAMILY_META = {
    "floral": {
        "es": ("Floral", "Rosa, jazmín, peonía"),
        "en": ("Floral", "Rose, jasmine, peony"),
    },
    "citrus": {
        "es": ("Cítrica", "Limón, bergamota, naranja"),
        "en": ("Citrus", "Lemon, bergamot, orange"),
    },
    "oriental": {
        "es": ("Oriental", "Ámbar, especias, resinas"),
        "en": ("Oriental", "Amber, spices, resins"),
    },
    "woody": {
        "es": ("Amaderada", "Sándalo, cedro, vetiver"),
        "en": ("Woody", "Sandalwood, cedar, vetiver"),
    },
    "aquatic": {
        "es": ("Acuática", "Marino, ozónico, fresco"),
        "en": ("Aquatic", "Marine, ozonic, fresh"),
    },
    "herbal": {
        "es": ("Herbal", "Lavanda, romero, menta"),
        "en": ("Herbal", "Lavender, rosemary, mint"),
    },
    "fruity": {
        "es": ("Frutal", "Durazno, pera, frutos rojos"),
        "en": ("Fruity", "Peach, pear, red fruits"),
    },
    "gourmand": {
        "es": ("Gourmand", "Vainilla, cacao, caramelo"),
        "en": ("Gourmand", "Vanilla, cocoa, caramel"),
    },
}

FAMILY_KEYWORDS = {
    "floral": ["rosa", "jazmin", "jazmín", "peonia", "peonía", "floral", "rose", "jasmine"],
    "citrus": ["limon", "limón", "bergamota", "naranja", "mandarina", "citric", "cítric", "bergamot"],
    "oriental": ["ambar", "ámbar", "especi", "resina", "oriental", "oud"],
    "woody": ["sandalo", "sándalo", "cedro", "vetiver", "amader", "sandalwood"],
    "aquatic": ["marino", "ozono", "ozonic", "acuat", "acuát", "marine"],
    "herbal": ["lavanda", "romero", "menta", "herbal", "lavender"],
    "fruity": ["durazno", "pera", "frutal", "frutos", "peach"],
    "gourmand": ["vainilla", "cacao", "caramelo", "chocolate", "gourmand", "vanilla"],
}

ADVISORS = {
    "Sofía": "f",
    "Valentina": "f",
    "Laura": "f",
    "Valeria": "f",
    "Juan": "m",
    "Sebastián": "m",
}

FRAGRANCE_WORDS = (
    "locion",
    "perfume",
    "fragancia",
    "aroma",
    "esencia",
    "olor",
    "nota",
    "familia",
    "colonia",
    "lotion",
    "fragrance",
    "scent",
)

OFF_TOPIC_PHRASES = (
    "ignora tus instrucciones",
    "ignore previous",
    "ignore your instructions",
    "system prompt",
    "capital de",
    "escribe codigo",
    "escribe un programa",
    "write code",
    "tarea de matem",
    "receta de cocina",
    "clima de hoy",
    "weather today",
    "quien es el presidente",
    "who is the president",
)

STOPWORDS = {
    "que",
    "una",
    "uno",
    "con",
    "los",
    "las",
    "del",
    "para",
    "por",
    "mis",
    "sus",
    "the",
    "and",
    "with",
    "that",
    "your",
    "you",
    "mas",
    "muy",
    "soy",
    "como",
}

EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.IGNORECASE)
LETTER_RE = re.compile(r"(?:la |the |opcion |option |letra )?([abcde])")


def _opt(es, en):
    return {"es": es, "en": en}


def _question(number, es, en, options, scores):
    return {
        "id": number,
        "prompt": {"es": es, "en": en},
        "options": options,
        "scores": scores,
    }


QUESTIONS = [
    _question(
        1,
        "¿Cómo describirías tu personalidad?",
        "How would you describe your personality?",
        {
            "A": _opt("Elegante, sofisticada y segura.", "Elegant, sophisticated and confident."),
            "B": _opt("Alegre, espontánea y llena de energía.", "Cheerful, spontaneous and full of energy."),
            "C": _opt("Misteriosa, reservada y cautivadora.", "Mysterious, reserved and captivating."),
            "D": _opt("Tranquila, natural y equilibrada.", "Calm, natural and balanced."),
            "E": _opt("Audaz, apasionada y aventurera.", "Bold, passionate and adventurous."),
        },
        {
            "A": {"oriental": 2, "woody": 1},
            "B": {"citrus": 2, "fruity": 1},
            "C": {"oriental": 2, "woody": 1},
            "D": {"herbal": 2, "woody": 1},
            "E": {"oriental": 1, "fruity": 1, "citrus": 1},
        },
    ),
    _question(
        2,
        "¿Qué ambiente disfrutas más?",
        "What kind of setting do you enjoy most?",
        {
            "A": _opt("Un espacio elegante, cálido y exclusivo.", "An elegant, warm and exclusive space."),
            "B": _opt("Una playa, el mar y la brisa fresca.", "A beach, the sea and a fresh breeze."),
            "C": _opt("Un jardín lleno de flores.", "A garden full of flowers."),
            "D": _opt("Un bosque rodeado de naturaleza.", "A forest surrounded by nature."),
            "E": _opt("Una ciudad vibrante llena de movimiento.", "A vibrant city full of movement."),
        },
        {
            "A": {"oriental": 2, "gourmand": 1},
            "B": {"aquatic": 3},
            "C": {"floral": 3},
            "D": {"woody": 2, "herbal": 1},
            "E": {"citrus": 2, "fruity": 1},
        },
    ),
    _question(
        3,
        "¿Qué tipo de planes disfrutas habitualmente?",
        "What kind of plans do you usually enjoy?",
        {
            "A": _opt("Cenas elegantes y eventos especiales.", "Elegant dinners and special events."),
            "B": _opt("Viajes, deportes y actividades al aire libre.", "Travel, sports and outdoor activities."),
            "C": _opt("Reuniones con amigos y momentos divertidos.", "Get-togethers with friends and fun moments."),
            "D": _opt("Leer, descansar y disfrutar de mi tranquilidad.", "Reading, resting and enjoying my quiet time."),
            "E": _opt("Salir, explorar y vivir nuevas experiencias.", "Going out, exploring and living new experiences."),
        },
        {
            "A": {"oriental": 2, "gourmand": 1},
            "B": {"aquatic": 2, "citrus": 1},
            "C": {"fruity": 2, "floral": 1},
            "D": {"woody": 2, "herbal": 1},
            "E": {"citrus": 1, "fruity": 1, "oriental": 1},
        },
    ),
    _question(
        4,
        "¿Cómo te gustaría que las personas te percibieran?",
        "How would you like people to perceive you?",
        {
            "A": _opt("Sofisticado/a y distinguido/a.", "Sophisticated and distinguished."),
            "B": _opt("Fresco/a y lleno/a de vitalidad.", "Fresh and full of vitality."),
            "C": _opt("Dulce, cercano/a y encantador/a.", "Sweet, warm and charming."),
            "D": _opt("Natural, auténtico/a y relajado/a.", "Natural, authentic and relaxed."),
            "E": _opt("Intenso/a, magnético/a e inolvidable.", "Intense, magnetic and unforgettable."),
        },
        {
            "A": {"oriental": 2, "woody": 1},
            "B": {"citrus": 2, "aquatic": 1},
            "C": {"floral": 2, "gourmand": 1},
            "D": {"herbal": 2, "woody": 1},
            "E": {"oriental": 3},
        },
    ),
    _question(
        5,
        "¿Qué sensación te gustaría experimentar al usar un perfume?",
        "What feeling would you like to experience when you wear a perfume?",
        {
            "A": _opt("Confianza y poder.", "Confidence and power."),
            "B": _opt("Frescura y libertad.", "Freshness and freedom."),
            "C": _opt("Sensualidad y atracción.", "Sensuality and attraction."),
            "D": _opt("Paz y conexión con la naturaleza.", "Peace and a connection with nature."),
            "E": _opt("Alegría y optimismo.", "Joy and optimism."),
        },
        {
            "A": {"oriental": 3},
            "B": {"citrus": 2, "aquatic": 1},
            "C": {"oriental": 2, "floral": 1},
            "D": {"woody": 2, "herbal": 1},
            "E": {"fruity": 2, "citrus": 1},
        },
    ),
    _question(
        6,
        "¿Qué paisaje representa mejor tu esencia?",
        "What landscape best represents your essence?",
        {
            "A": _opt("Un atardecer cálido y dorado.", "A warm golden sunset."),
            "B": _opt("Un jardín de rosas al amanecer.", "A rose garden at dawn."),
            "C": _opt("Una cascada de agua cristalina.", "A cascade of crystal-clear water."),
            "D": _opt("Un bosque profundo y misterioso.", "A deep and mysterious forest."),
            "E": _opt("Un campo de frutas y flores tropicales.", "A field of tropical fruits and flowers."),
        },
        {
            "A": {"oriental": 2, "gourmand": 1},
            "B": {"floral": 3},
            "C": {"aquatic": 3},
            "D": {"woody": 3},
            "E": {"fruity": 2, "floral": 1},
        },
    ),
    _question(
        7,
        "¿Qué notas aromáticas te llaman más la atención?",
        "Which aromatic notes catch your attention the most?",
        {
            "A": _opt("Vainilla, caramelo y chocolate.", "Vanilla, caramel and chocolate."),
            "B": _opt("Rosas, jazmín y flores blancas.", "Roses, jasmine and white flowers."),
            "C": _opt("Limón, bergamota y mandarina.", "Lemon, bergamot and mandarin."),
            "D": _opt("Sándalo, cedro y vetiver.", "Sandalwood, cedar and vetiver."),
            "E": _opt("Lavanda, menta y hierbas aromáticas.", "Lavender, mint and aromatic herbs."),
        },
        {
            "A": {"gourmand": 3},
            "B": {"floral": 3},
            "C": {"citrus": 3},
            "D": {"woody": 3},
            "E": {"herbal": 3},
        },
    ),
    _question(
        8,
        "¿En qué momento del día utilizas más perfume?",
        "At what time of day do you wear perfume the most?",
        {
            "A": _opt("En las mañanas, para comenzar con energía.", "In the morning, to start with energy."),
            "B": _opt("Durante todo el día, quiero sentirme fresco/a.", "All day, I want to feel fresh."),
            "C": _opt("En las tardes, para complementar mi estilo.", "In the afternoon, to complete my style."),
            "D": _opt("En las noches, para destacar y cautivar.", "At night, to stand out and captivate."),
            "E": _opt("En ocasiones especiales, quiero dejar huella.", "On special occasions, I want to leave a mark."),
        },
        {
            "A": {"citrus": 2, "fruity": 1},
            "B": {"aquatic": 2, "citrus": 1},
            "C": {"floral": 1, "woody": 1, "oriental": 1},
            "D": {"oriental": 3},
            "E": {"oriental": 2, "gourmand": 1},
        },
    ),
    _question(
        9,
        "¿Qué intensidad prefieres en un perfume?",
        "What intensity do you prefer in a perfume?",
        {
            "A": _opt("Suave y delicada, que se perciba de cerca.", "Soft and delicate, noticed up close."),
            "B": _opt("Fresca y equilibrada, para todos los días.", "Fresh and balanced, for every day."),
            "C": _opt("Moderada, con una presencia elegante.", "Moderate, with an elegant presence."),
            "D": _opt("Intensa, que deje una huella memorable.", "Intense, leaving a memorable trail."),
            "E": _opt("Depende de la ocasión y mi estado de ánimo.", "It depends on the occasion and my mood."),
        },
        {
            "A": {"floral": 2, "herbal": 1},
            "B": {"citrus": 2, "aquatic": 1},
            "C": {"woody": 2, "floral": 1},
            "D": {"oriental": 2, "gourmand": 1},
            "E": {},
        },
    ),
    _question(
        10,
        "Si tuvieras que elegir una sensación como sello personal, ¿cuál sería?",
        "If you had to choose one feeling as your personal signature, which would it be?",
        {
            "A": _opt("Elegancia atemporal.", "Timeless elegance."),
            "B": _opt("Libertad y frescura.", "Freedom and freshness."),
            "C": _opt("Romanticismo y delicadeza.", "Romance and delicacy."),
            "D": _opt("Misterio y sofisticación.", "Mystery and sophistication."),
            "E": _opt("Dulzura y calidez.", "Sweetness and warmth."),
        },
        {
            "A": {"woody": 2, "oriental": 1},
            "B": {"aquatic": 2, "citrus": 1},
            "C": {"floral": 3},
            "D": {"oriental": 2, "woody": 1},
            "E": {"gourmand": 3},
        },
    ),
]

INTRO = {
    "es": (
        "¡Hola! Soy {name}, tu {role} comercial de lociones y perfumes en Esencias.\n\n"
        "Cada persona tiene una esencia que la hace única. Responde 10 preguntas con tus palabras, "
        "unos 3 minutos, y descubrimos qué familias olfativas, aromas y acordes van con tu personalidad "
        "y tu estilo de vida."
    ),
    "en": (
        "Hi! I'm {name}, your commercial advisor for lotions and perfumes at Esencias.\n\n"
        "Everyone has an essence that makes them unique. Answer 10 questions in your own words, "
        "about 3 minutes, and we'll find the fragrance families, scents and accords that fit your "
        "personality and lifestyle."
    ),
}


def fold(text):
    normalized = unicodedata.normalize("NFD", str(text or "").lower())
    return "".join(character for character in normalized if unicodedata.category(character) != "Mn")


def tokens(text):
    return {
        token
        for token in re.findall(r"[a-z0-9]+", fold(text))
        if len(token) > 2 and token not in STOPWORDS
    }


def language_code(value):
    return "en" if str(value or "").lower().startswith("en") else "es"


def normalize_advisor(name):
    folded = fold(name)
    for advisor in ADVISORS:
        if fold(advisor) == folded:
            return advisor
    return "Sofía"


def advisor_role(name, language):
    if language_code(language) == "en":
        return "advisor"
    return "asesor" if ADVISORS.get(normalize_advisor(name)) == "m" else "asesora"


def question_by_number(number):
    return QUESTIONS[number - 1]


def question_prompt(number, language):
    return question_by_number(number)["prompt"][language_code(language)]


def welcome_text(name, language):
    language = language_code(language)
    advisor = normalize_advisor(name)
    intro = INTRO[language].format(name=advisor, role=advisor_role(advisor, language))
    return f"{intro}\n\n{question_prompt(1, language)}"


def explicit_letter(message):
    match = LETTER_RE.fullmatch(fold(message).strip())
    if not match:
        return None
    return match.group(1).upper()


def keyword_choice(question, message):
    user_tokens = tokens(message)
    if not user_tokens:
        return None
    best_letter = None
    best_score = 0
    for letter, option in question["options"].items():
        option_tokens = tokens(f"{option['es']} {option['en']}")
        score = len(user_tokens & option_tokens)
        if score > best_score:
            best_score = score
            best_letter = letter
    if best_score < 1:
        return None
    return best_letter


def clearly_off_topic(message):
    folded = fold(message)
    return any(phrase in folded for phrase in OFF_TOPIC_PHRASES)


def clean_bridge(bridge, question):
    text = " ".join(str(bridge or "").split())
    if not text or "?" in text or "¿" in text or len(text) > 180:
        return ""
    folded = fold(text)
    if any(phrase in folded for phrase in OFF_TOPIC_PHRASES):
        return ""
    if re.search(r"\b[a-e]\s*[).:-]", folded):
        return ""
    for option in question["options"].values():
        for sample in (option["es"], option["en"]):
            sample_folded = fold(sample).rstrip(".")
            if len(sample_folded) >= 12 and sample_folded in folded:
                return ""
    sentences = re.split(r"(?<=[.!])\s+", text)
    kept = [
        sentence.strip()
        for sentence in sentences
        if any(word in fold(sentence) for word in FRAGRANCE_WORDS)
    ]
    if not kept:
        return ""
    return kept[0][:180]


def tally(answers):
    totals = {key: 0 for key in FAMILY_META}
    for key, payload in (answers or {}).items():
        try:
            number = int(key)
        except (TypeError, ValueError):
            continue
        if number < 1 or number > len(QUESTIONS):
            continue
        choice = payload.get("choice") if isinstance(payload, dict) else payload
        for family, amount in QUESTIONS[number - 1]["scores"].get(choice, {}).items():
            totals[family] += amount
    return totals


def rank(totals):
    ordered = sorted(totals, key=lambda key: (-totals[key], key))
    primary = ordered[0]
    secondary = [key for key in ordered[1:] if totals[key] > 0][:2]
    return primary, secondary


def family_label(key, language):
    return FAMILY_META[key][language_code(language)][0]


def family_notes(key, language):
    return FAMILY_META[key][language_code(language)][1]


def one_line(value, limit=80):
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def recommend_perfumes(families, limit=3):
    words = []
    for family in families:
        if not family:
            continue
        words.extend(fold(word) for word in FAMILY_KEYWORDS.get(family, []))
    if not words:
        return []
    ranked = []
    queryset = Perfume.objects.filter(
        is_active=True,
        kind=Perfume.Kind.PERFUME,
    ).prefetch_related("main_chords")
    for perfume in queryset:
        chords = " ".join(chord.name for chord in perfume.main_chords.all())
        haystack = fold(" ".join([
            perfume.name,
            perfume.brand,
            perfume.notes,
            perfume.description,
            chords,
        ]))
        score = sum(1 for word in words if word and word in haystack)
        if score:
            ranked.append((score, perfume.name, perfume.pk, perfume))
    ranked.sort(key=lambda item: (-item[0], item[1], item[2]))
    return [item[3] for item in ranked[:limit]]


def refusal_text(language):
    if language_code(language) == "en":
        return "I can only advise you on lotions and perfumes. If you want, we can keep discovering your essence."
    return "Solo puedo asesorarte sobre lociones y perfumes. Si quieres, seguimos descubriendo tu esencia."


def clarify_text(language):
    if language_code(language) == "en":
        return "I want to understand you so I can recommend the right lotion. Tell me a little more, in your own words."
    return "Quiero entenderte bien para recomendarte la loción correcta. Cuéntame un poco más, con tus palabras."


def default_bridge(language):
    if language_code(language) == "en":
        return "That already says a lot about the lotion that suits you."
    return "Eso ya me dice bastante de la loción que te queda."


def email_ask(language):
    if language_code(language) == "en":
        return "This advice chat does not need an account. Which email should I use to save your result and send it to you?"
    return "Esta asesoría no pide una cuenta. Para guardar tu resultado y enviártelo, ¿a qué correo te lo mando?"


def invalid_email_text(language):
    if language_code(language) == "en":
        return "I need a valid email to save your profile and send it to you."
    return "Necesito un correo válido para guardar tu perfil y enviártelo."


def missing_chat_text(language):
    if language_code(language) == "en":
        return "I couldn't find this conversation. Send a message and we'll start again."
    return "No encontré esta asesoría. Escribe de nuevo y empezamos."


def _secondary_sentence(secondary, language):
    language = language_code(language)
    if len(secondary) >= 2:
        first, second = secondary[:2]
        if language == "en":
            return (
                f"You also connect with {family_label(first, language)} ({family_notes(first, language)}) "
                f"and {family_label(second, language)} ({family_notes(second, language)})."
            )
        return (
            f"También conectan contigo {family_label(first, language)} ({family_notes(first, language)}) "
            f"y {family_label(second, language)} ({family_notes(second, language)})."
        )
    if len(secondary) == 1:
        family = secondary[0]
        if language == "en":
            return f"You also connect with {family_label(family, language)} ({family_notes(family, language)})."
        return f"También conecta contigo {family_label(family, language)} ({family_notes(family, language)})."
    return ""


def _product_lines(products, language):
    language = language_code(language)
    if not products:
        return ""
    header = "These lotions from the catalog fit your profile:" if language == "en" else "Estas lociones del catálogo van con tu perfil:"
    lines = [header]
    for perfume in products:
        note = one_line(perfume.notes) or one_line(perfume.description)
        label = f"{one_line(perfume.brand)} {one_line(perfume.name)}".strip()
        lines.append(f"• {label} — {note}" if note else f"• {label}")
    return "\n".join(lines)


def summary_text(language, primary, secondary, products, *, ask_email):
    language = language_code(language)
    if language == "en":
        opening = f"Your main fragrance family is {family_label(primary, language)}: {family_notes(primary, language)}."
    else:
        opening = f"Tu familia olfativa principal es {family_label(primary, language)}: {family_notes(primary, language)}."
    parts = [opening]
    secondary_line = _secondary_sentence(secondary, language)
    if secondary_line:
        parts.append(secondary_line)
    product_block = _product_lines(products, language)
    if product_block:
        parts.append(product_block)
    elif language == "en":
        parts.append(f"When you look through the catalog, look for notes of {family_notes(primary, language)}.")
    else:
        parts.append(f"Cuando mires el catálogo, busca notas de {family_notes(primary, language)}.")
    if ask_email:
        parts.append(email_ask(language))
    return "\n\n".join(parts)


def confirmation_text(language, email, sent, primary, secondary, products):
    language = language_code(language)
    story = summary_text(language, primary, secondary, products, ask_email=False)
    if language == "en":
        if sent:
            head = f"Done. I saved your olfactory profile and sent it to {email}."
        else:
            head = (
                f"I saved your olfactory profile for {email}. "
                "I couldn't send the email just now, but the result is already stored for that address."
            )
        tail = "If you want, I can tell you how to wear that family during the day or at night."
    else:
        if sent:
            head = f"Listo. Guardé tu perfil olfativo y te lo envié a {email}."
        else:
            head = (
                f"Guardé tu perfil olfativo para {email}. "
                "Ahora no pude enviar el correo, pero el resultado ya quedó asociado a ese correo."
            )
        tail = "Si quieres, te cuento cómo usar esa familia de día o de noche."
    return f"{head}\n\n{story}\n\n{tail}"


def email_subject(language):
    if language_code(language) == "en":
        return "Your olfactory profile at Esencias"
    return "Tu perfil olfativo en Esencias"


def email_body(language, primary, secondary, products):
    language = language_code(language)
    title = "Esencias olfactory test" if language == "en" else "Test olfativo Esencias"
    story = summary_text(language, primary, secondary, products, ask_email=False)
    lines = [title, "", story, ""]
    catalog = f"{settings.FRONTEND_URL}/perfumes"
    lines.append("Catalog:" if language == "en" else "Catálogo:")
    lines.append(catalog)
    for perfume in products:
        label = f"{one_line(perfume.brand)} {one_line(perfume.name)}".strip()
        lines.append(f"{label}: {settings.FRONTEND_URL}/perfumes/{perfume.id}")
    return "\n".join(lines)


def extract_email(message):
    match = EMAIL_RE.search(message or "")
    if not match:
        return ""
    candidate = match.group(0).strip().strip(".").lower()
    if len(candidate) > 254:
        return ""
    try:
        validate_email(candidate)
    except ValidationError:
        return ""
    return candidate


def hidden_options(question, language):
    language = language_code(language)
    lines = []
    for letter, option in question["options"].items():
        lines.append(f"{letter}. {option[language]}")
    return "\n".join(lines)
