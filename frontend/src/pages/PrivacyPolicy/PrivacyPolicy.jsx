import { useTranslation } from "react-i18next";
import { privacyContent } from "./privacyContent";
import "./PrivacyPolicy.css";

export default function PrivacyPolicy() {
  const { i18n } = useTranslation();
  const language = (i18n.resolvedLanguage || i18n.language || "es").startsWith("en") ? "en" : "es";
  const policy = privacyContent[language];

  return (
    <article className="privacy-policy">
      <h1 className="h2 mb-2">{policy.title}</h1>
      <p className="text-body-secondary">{policy.updated}</p>
      <p>{policy.intro}</p>
      {policy.sections.map((section) => (
        <section key={section.title}>
          <h2>{section.title}</h2>
          {section.paragraphs.map((paragraph) => (
            <p key={paragraph}>{paragraph}</p>
          ))}
        </section>
      ))}
    </article>
  );
}
