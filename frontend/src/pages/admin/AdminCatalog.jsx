import { useEffect, useState } from "react";
import { Alert, Button, Form, Modal, Table } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import RelationSelect from "../../components/RelationSelect/RelationSelect";
import { listMainChords, createPerfume, deletePerfume, listPerfumes, updatePerfume } from "../../services/perfumes";

const emptyForm = {
  name: "",
  brand: "",
  description: "",
  notes: "",
  image_url: "",
  price: "",
  price_usd: "",
  color: "",
  main_chords: [],
  is_active: true,
};

export default function AdminCatalog() {
  const { t } = useTranslation();
  const [perfumes, setPerfumes] = useState([]);
  const [chords, setChords] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    const [data, chordData] = await Promise.all([listPerfumes(), listMainChords()]);
    setPerfumes(data.results || []);
    setChords(chordData.map((chord) => ({ value: chord.id, label: chord.name })));
  }

  useEffect(() => {
    load().catch(() => setError(t("common.error")));
  }, [t]);

  function update(event) {
    const { name, value, type, checked } = event.target;
    setForm((current) => ({ ...current, [name]: type === "checkbox" ? checked : value }));
  }

  function openCreate() {
    setEditingId(null);
    setForm(emptyForm);
    setError("");
    setOpen(true);
  }

  function openEdit(perfume) {
    setEditingId(perfume.id);
    setForm({
      name: perfume.name,
      brand: perfume.brand,
      description: perfume.description,
      notes: perfume.notes || "",
      image_url: perfume.image_url,
      price: perfume.price,
      price_usd: perfume.price_usd ?? "",
      color: perfume.color || "",
      main_chords: perfume.main_chords || [],
      is_active: perfume.is_active,
    });
    setError("");
    setOpen(true);
  }

  function closeModal() {
    setOpen(false);
    setEditingId(null);
    setForm(emptyForm);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    const payload = {
      ...form,
      price: Number(form.price),
      price_usd: form.price_usd === "" ? null : Number(form.price_usd),
    };
    try {
      if (editingId) {
        await updatePerfume(editingId, payload);
      } else {
        await createPerfume(payload);
      }
      closeModal();
      await load();
    } catch {
      setError(t("common.error"));
    }
  }

  async function handleDelete(id) {
    await deletePerfume(id);
    await load();
  }

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h2 mb-0">{t("admin.catalogTitle")}</h1>
        <Button variant="dark" onClick={openCreate}>
          {t("admin.newPerfume")}
        </Button>
      </div>
      {error && !open && <Alert variant="danger">{error}</Alert>}
      <Table responsive hover>
        <thead>
          <tr>
            <th>{t("auth.name")}</th>
            <th>{t("admin.brand")}</th>
            <th>{t("admin.price")}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {perfumes.map((perfume) => (
            <tr key={perfume.id}>
              <td>{perfume.name}</td>
              <td>{perfume.brand}</td>
              <td>${Number(perfume.price).toFixed(2)}</td>
              <td className="text-end">
                <Button size="sm" variant="outline-secondary" className="me-2" onClick={() => openEdit(perfume)}>
                  {t("admin.edit")}
                </Button>
                <Button size="sm" variant="outline-danger" onClick={() => handleDelete(perfume.id)}>
                  {t("common.delete")}
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      <Modal show={open} onHide={closeModal} centered scrollable>
        <Form onSubmit={handleSubmit}>
          <Modal.Header closeButton>
            <Modal.Title>{editingId ? t("admin.edit") : t("admin.newPerfume")}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {error && open && <Alert variant="danger">{error}</Alert>}
            <div className="row g-3">
              <Form.Group className="col-md-6">
                <Form.Label>{t("auth.name")}</Form.Label>
                <Form.Control name="name" value={form.name} onChange={update} required />
              </Form.Group>
              <Form.Group className="col-md-6">
                <Form.Label>{t("admin.brand")}</Form.Label>
                <Form.Control name="brand" value={form.brand} onChange={update} required />
              </Form.Group>
              <Form.Group className="col-12">
                <Form.Label>{t("admin.imageUrl")}</Form.Label>
                <Form.Control name="image_url" value={form.image_url} onChange={update} required />
              </Form.Group>
              <Form.Group className="col-md-4">
                <Form.Label>{t("admin.price")}</Form.Label>
                <Form.Control name="price" type="number" min="0" step="0.01" value={form.price} onChange={update} required />
              </Form.Group>
              <Form.Group className="col-md-4">
                <Form.Label>{t("admin.priceUsd")}</Form.Label>
                <Form.Control name="price_usd" type="number" min="0" step="0.01" value={form.price_usd} onChange={update} />
              </Form.Group>
              <Form.Group className="col-md-4">
                <Form.Label>{t("admin.color")}</Form.Label>
                <Form.Control name="color" value={form.color} onChange={update} />
              </Form.Group>
              <Form.Group className="col-12">
                <Form.Label>{t("admin.notes")}</Form.Label>
                <Form.Control name="notes" value={form.notes} onChange={update} />
              </Form.Group>
              <Form.Group className="col-12">
                <Form.Label htmlFor="perfume-chords">{t("admin.mainChords")}</Form.Label>
                <RelationSelect
                  multiple
                  inputId="perfume-chords"
                  options={chords}
                  value={form.main_chords}
                  onChange={(mainChords) => setForm((current) => ({ ...current, main_chords: mainChords }))}
                />
              </Form.Group>
              <Form.Group className="col-12">
                <Form.Label>{t("admin.description")}</Form.Label>
                <Form.Control as="textarea" rows={3} name="description" value={form.description} onChange={update} required />
              </Form.Group>
              <Form.Group className="col-12">
                <Form.Check name="is_active" checked={form.is_active} onChange={update} label={t("admin.active")} />
              </Form.Group>
            </div>
          </Modal.Body>
          <Modal.Footer>
            <Button type="button" variant="outline-secondary" onClick={closeModal}>
              {t("admin.cancel")}
            </Button>
            <Button type="submit" variant="dark">
              {t("admin.save")}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
}
