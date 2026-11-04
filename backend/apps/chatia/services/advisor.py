import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone

from apps.chatia.models import ChatIA, Message, OlfactoryTest, PerfumeOlfactoryProfile

from .gemini import GeminiService
from .olfactory import (
    clean_bridge,
    clearly_off_topic,
    confirmation_text,
    default_bridge,
    email_ask,
    email_body,
    email_subject,
    explicit_letter,
    extract_email,
    hidden_options,
    invalid_email_text,
    keyword_choice,
    language_code,
    normalize_advisor,
    question_by_number,
    question_prompt,
    rank,
    recommend_perfumes,
    refusal_text,
    clarify_text,
    summary_text,
    tally,
    welcome_text,
)

logger = logging.getLogger(__name__)


class UnknownChat(Exception):
    pass


def handle_message(*, chat_id, message, advisor, language, user):
    message = " ".join(str(message or "").split())
    if not message:
        raise ValueError("empty message")
    with transaction.atomic():
        if chat_id:
            chat = ChatIA.objects.select_for_update().filter(public_id=chat_id).first()
            if chat is None:
                raise UnknownChat
            if user is not None and chat.user_id is None:
                chat.user = user
                chat.save(update_fields=["user"])
        else:
            chat = _create_chat(advisor, language, user)
        test = _ensure_test(chat, user)
        Message.objects.create(chatia=chat, role=Message.Role.USER, content=message)
        reply = _advance(chat, test, message)
        Message.objects.create(chatia=chat, role=Message.Role.ASSISTANT, content=reply)
    test.refresh_from_db()
    return {
        "response": reply,
        "chat_id": str(chat.public_id),
        "phase": _phase(test),
    }


def _create_chat(advisor, language, user):
    language = language_code(language)
    name = normalize_advisor(advisor)
    chat = ChatIA.objects.create(
        user=user,
        name=name,
        advisor_name=name,
        language=language,
        description="Test olfativo",
    )
    Message.objects.create(
        chatia=chat,
        role=Message.Role.ASSISTANT,
        content=welcome_text(name, language),
    )
    OlfactoryTest.objects.create(chat=chat, user=user, current_question=1)
    return chat


def _ensure_test(chat, user):
    test = getattr(chat, "olfactory_test", None)
    if test is None:
        test = OlfactoryTest.objects.create(chat=chat, user=user, current_question=1)
    elif user is not None and test.user_id is None:
        test.user = user
        test.save(update_fields=["user"])
    return test


def _advance(chat, test, message):
    language = language_code(chat.language)
    if test.status == OlfactoryTest.Status.COMPLETED:
        return _advise(chat, test, message, language)
    if test.status == OlfactoryTest.Status.AWAITING_EMAIL:
        return _capture_email(chat, test, message, language)
    return _answer_question(chat, test, message, language)


def _answer_question(chat, test, message, language):
    question = question_by_number(test.current_question)
    prompt = question_prompt(question["id"], language)
    if clearly_off_topic(message):
        return f"{refusal_text(language)}\n\n{prompt}"

    letter = explicit_letter(message)
    classification = {"choice": letter, "off_topic": False, "bridge": ""}
    if letter is None:
        classification = GeminiService().classify(
            language=language,
            question_prompt=prompt,
            hidden_options=hidden_options(question, language),
            message=message,
        )
    keyword = keyword_choice(question, message)
    if classification["off_topic"] and keyword is None:
        return f"{refusal_text(language)}\n\n{prompt}"

    choice = letter or classification["choice"] or keyword
    if choice is None:
        return f"{clarify_text(language)}\n\n{prompt}"

    answers = dict(test.answers or {})
    answers[str(question["id"])] = {"choice": choice, "text": message[:2000]}
    test.answers = answers
    bridge = clean_bridge(classification.get("bridge"), question) or default_bridge(language)

    if question["id"] >= 10:
        return _finish_questions(test, language, bridge)

    test.current_question = question["id"] + 1
    test.save(update_fields=["answers", "current_question", "updated_at"])
    return f"{bridge}\n\n{question_prompt(test.current_question, language)}"


def _finish_questions(test, language, bridge):
    totals = tally(test.answers)
    primary, secondary = rank(totals)
    test.scores = totals
    test.primary_family = primary
    test.secondary_families = secondary
    test.status = OlfactoryTest.Status.AWAITING_EMAIL
    test.save(update_fields=[
        "answers",
        "scores",
        "primary_family",
        "secondary_families",
        "status",
        "updated_at",
    ])
    products = recommend_perfumes([primary, *secondary])
    story = summary_text(language, primary, secondary, products, ask_email=True)
    return f"{bridge}\n\n{story}"


def _capture_email(chat, test, message, language):
    email = extract_email(message)
    if not email:
        if clearly_off_topic(message):
            return f"{refusal_text(language)}\n\n{email_ask(language)}"
        return f"{invalid_email_text(language)}\n\n{email_ask(language)}"

    previous = (test.email or "").lower()
    if previous and previous != email and test.email_sent_at is None:
        PerfumeOlfactoryProfile.objects.filter(email=previous).delete()

    totals = test.scores or tally(test.answers)
    primary = test.primary_family
    secondary = list(test.secondary_families or [])
    if not primary:
        primary, secondary = rank(totals)
        test.primary_family = primary
        test.secondary_families = secondary
    products = recommend_perfumes([primary, *secondary])
    linked_user = _matching_user(chat.user, email)
    profile, _created = PerfumeOlfactoryProfile.objects.update_or_create(
        email=email,
        defaults={
            "test": test,
            "primary_family": primary,
            "secondary_families": secondary,
            "floral_score": totals.get("floral", 0),
            "citrus_score": totals.get("citrus", 0),
            "oriental_score": totals.get("oriental", 0),
            "woody_score": totals.get("woody", 0),
            "aquatic_score": totals.get("aquatic", 0),
            "herbal_score": totals.get("herbal", 0),
            "fruity_score": totals.get("fruity", 0),
            "gourmand_score": totals.get("gourmand", 0),
            **({"user": linked_user} if linked_user is not None else {}),
        },
    )
    sent = _send_result(language, email, primary, secondary, products)
    now = timezone.now()
    test.email = email
    test.status = OlfactoryTest.Status.COMPLETED
    test.completed_at = now
    test.email_sent_at = now if sent else None
    test.save(update_fields=[
        "email",
        "primary_family",
        "secondary_families",
        "status",
        "completed_at",
        "email_sent_at",
        "updated_at",
    ])
    chat.email = email
    chat.save(update_fields=["email", "updated_at"])
    profile.test = test
    profile.save(update_fields=["test"])
    return confirmation_text(language, email, sent, primary, secondary, products)


def _advise(chat, test, message, language):
    if clearly_off_topic(message):
        return refusal_text(language)
    products = recommend_perfumes([test.primary_family, *(test.secondary_families or [])])
    story = summary_text(
        language,
        test.primary_family,
        list(test.secondary_families or []),
        products,
        ask_email=False,
    )
    recent = list(chat.messages.order_by("-id")[:12])
    recent.reverse()
    transcript = "\n".join(
        f"{'Cliente' if item.role == Message.Role.USER else 'Asesor'}: {item.content}"
        for item in recent
    )
    reply = GeminiService().advise(
        language=language,
        advisor=chat.advisor_name,
        story=story,
        transcript=transcript,
    )
    cleaned = " ".join(str(reply or "").split())
    if not cleaned or cleaned.startswith("{") or len(cleaned) > 1800 or clearly_off_topic(cleaned):
        if language == "en":
            return f"{story}\n\nTell me the occasion and I'll stay on a lotion from your family."
        return f"{story}\n\nCuéntame la ocasión y seguimos con una loción de tu familia."
    return cleaned


def _matching_user(user, email):
    if user is None:
        return None
    if (user.email or "").strip().lower() == email:
        return user
    return None


def _send_result(language, email, primary, secondary, products):
    if not settings.EMAIL_HOST or not settings.EMAIL_HOST_PASSWORD:
        logger.error("El perfil olfativo quedó guardado, pero el correo del sitio no está configurado.")
        return False
    mail = EmailMessage(
        subject=email_subject(language),
        body=email_body(language, primary, secondary, products),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    try:
        mail.send(fail_silently=False)
    except Exception:
        logger.exception("No se pudo enviar el perfil olfativo.")
        return False
    return True


def _phase(test):
    if test.status == OlfactoryTest.Status.COMPLETED:
        return "done"
    if test.status == OlfactoryTest.Status.AWAITING_EMAIL:
        return "email"
    return "question"
