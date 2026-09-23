import { useState } from "react";
import { Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import "./AdvisorModal.css";

const WHATSAPP_NUMBER = String(import.meta.env.VITE_WHATSAPP_NUMBER || "").replace(/\D/g, "");

function WebIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" strokeWidth="1.6" />
      <ellipse cx="12" cy="12" rx="4.2" ry="9" fill="none" stroke="currentColor" strokeWidth="1.6" />
      <path d="M3.2 12h17.6M4.8 7.6h14.4M4.8 16.4h14.4" fill="none" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  );
}

function WhatsAppIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="currentColor"
        d="M12.04 2C6.58 2 2.15 6.4 2.15 11.83c0 1.74.46 3.44 1.34 4.94L2 22l5.39-1.41a10 10 0 0 0 4.65 1.18h.01c5.46 0 9.89-4.4 9.89-9.83C21.94 6.4 17.5 2 12.04 2zm5.76 13.92c-.24.68-1.4 1.3-1.94 1.38-.5.08-1.12.11-1.81-.11-.42-.14-.95-.31-1.64-.6-2.88-1.24-4.76-4.14-4.9-4.33-.14-.19-1.16-1.54-1.16-2.94s.73-2.08 1-2.37c.24-.28.64-.41 1.02-.41.12 0 .23 0 .33.01.3.01.45.03.65.5.24.58.82 2 .89 2.15.07.14.12.31.02.5-.09.19-.14.31-.28.48-.14.16-.29.36-.42.49-.14.14-.28.29-.12.56.16.28.72 1.18 1.54 1.91 1.06.94 1.95 1.23 2.23 1.37.28.14.44.12.6-.07.16-.19.69-.8.88-1.08.19-.28.37-.23.63-.14.26.09 1.64.77 1.92.91.28.14.47.21.54.33.07.12.07.68-.17 1.36z"
      />
    </svg>
  );
}

export default function AdvisorModal({ onWeb }) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(true);
  const message = encodeURIComponent(t("home.advisorWhatsappMessage"));
  const whatsappHref = WHATSAPP_NUMBER
    ? `https://wa.me/${WHATSAPP_NUMBER}?text=${message}`
    : `https://wa.me/?text=${message}`;

  function handleWeb() {
    setOpen(false);
    onWeb?.();
  }

  return (
    <Modal
      show={open}
      onHide={() => setOpen(false)}
      centered
      className="advisor-modal"
      backdropClassName="advisor-modal-backdrop"
    >
      <Modal.Header closeButton>
        <Modal.Title className="visually-hidden">{t("home.advisorTitle")}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <h2 className="advisor-modal-title">{t("home.advisorTitle")}</h2>
        <p className="advisor-modal-lead">{t("home.advisorLead")}</p>
        <div className="advisor-modal-actions">
          <button type="button" className="advisor-modal-button advisor-modal-button-solid" onClick={handleWeb}>
            <WebIcon />
            {t("home.advisorWeb")}
          </button>
          <a className="advisor-modal-button" href={whatsappHref} target="_blank" rel="noreferrer">
            <WhatsAppIcon />
            {t("home.advisorWhatsapp")}
          </a>
        </div>
      </Modal.Body>
    </Modal>
  );
}
