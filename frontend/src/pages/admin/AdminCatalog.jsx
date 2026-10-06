import { useEffect, useState } from "react";
import { Alert, Button, Form, Modal, Table } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import ImageDropzone from "../../components/ImageDropzone/ImageDropzone";
import RelationSelect from "../../components/RelationSelect/RelationSelect";
import { listMainChords, createPerfume, deletePerfume, listPerfumes, updatePerfume } from "../../services/perfumes";

const CATALOGS = [
  { value: "caballero", labelKey: "admin.catalogCaballero" },
  { value: "dama", labelKey: "admin.catalogDama" },
  { value: "arabe", labelKey: "admin.catalogArabe" },
];

const emptyForm = {
  name: "",
  brand: "",
  description: "",
  notes: "",
  catalog: "",
  price: "",
  price_usd: "",
  grams: 100,
  gram_price: "0",
  color: "",
  main_chords: [],
  is_active: true,
};

export default function AdminCatalog() {
  const { t } = useTranslation();
  const [perfumes, setPerfumes] = useState([]);
  const [chords, setChords] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [files, setFiles] = useState([]);
  const [existingImages, setExistingImages] = useState([]);
  const [removedImageIds, setRemovedImageIds] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
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

  function resetForm() {
    setEditingId(null);
    setForm(emptyForm);
    setFiles([]);
    setExistingImages([]);
    setRemovedImageIds([]);
  }

  function openCreate() {
    resetForm();
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
      catalog: perfume.catalog || "",
      price: perfume.price,
      price_usd: perfume.price_usd ?? "",
      grams: perfume.grams ?? 100,
      gram_price: perfume.gram_price ?? "0",
      color: perfume.color || "",
      main_chords: perfume.main_chords || [],
      is_active: perfume.is_active,
    });
    setFiles([]);
    setExistingImages(perfume.images || []);
    setRemovedImageIds([]);
    setError("");
    setOpen(true);
  }

  function closeModal() {
    setOpen(false);
    resetForm();
  }

  function buildPayload() {
    const payload = new FormData();
    payload.append("name", form.name);
    payload.append("brand", form.brand);
    payload.append("description", form.description);
    payload.append("notes", form.notes);
    payload.append("catalog", form.catalog);
    payload.append("price", form.price);
    payload.append("price_usd", form.price_usd);
    payload.append("grams", form.grams);
    payload.append("gram_price", form.gram_price);
    payload.append("color", form.color);
    payload.append("is_active", form.is_active ? "true" : "false");
    payload.append("main_chords", JSON.stringify(form.main_chords));
    files.forEach((file) => payload.append("images", file));
    removedImageIds.forEach((id) => payload.append("remove_image_ids", String(id)));
    return payload;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (saving) {
      return;
    }
    if (files.length + existingImages.length === 0) {
      setError(t("admin.imagesRequired"));
      return;
    }
    setSaving(true);
    setError("");
    try {
      const payload = buildPayload();
      if (editingId) {
        await updatePerfume(editingId, payload);
      } else {
        await createPerfume(payload);
      }
      closeModal();
      await load();
    } catch {
      setError(t("common.error"));
    } finally {
      setSaving(false);
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
            <th>{t("admin.perfumeCatalog")}</th>
            <th>{t("admin.price")}</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {perfumes.map((perfume) => (
            <tr key={perfume.id}>
              <td>{perfume.name}</td>
              <td>{perfume.brand}</td>
              <td>{t(CATALOGS.find((item) => item.value === perfume.catalog)?.labelKey || "admin.catalogPlaceholder")}</td>
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

      <Modal show={open} onHide={closeModal} centered scrollable size="lg">
        <Form onSubmit={handleSubmit}>
          <Modal.Header closeButton>
            <Modal.Title>{editingId ? t("admin.edit") : t("admin.newPerfume")}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {error && open && <Alert variant="danger">{error}</Alert>}
            <div className="row g-3">
              <Form.Group className="col-md-4">
                <Form.Label>{t("auth.name")}</Form.Label>
                <Form.Control name="name" value={form.name} onChange={update} required />
              </Form.Group>
              <Form.Group className="col-md-4">
                <Form.Label>{t("admin.brand")}</Form.Label>
                <Form.Control name="brand" value={form.brand} onChange={update} required />
              </Form.Group>
              <Form.Group className="col-md-4">
                <Form.Label>{t("admin.perfumeCatalog")}</Form.Label>
                <Form.Select name="catalog" value={form.catalog} onChange={update} required>
                  <option value="">{t("admin.catalogPlaceholder")}</option>
                  {CATALOGS.map((item) => (
                    <option key={item.value} value={item.value}>
                      {t(item.labelKey)}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
              <Form.Group className="col-12">
                <Form.Label>{t("admin.imageUrl")}</Form.Label>
                <ImageDropzone
                  files={files}
                  existing={existingImages}
                  onAdd={(images) => setFiles((current) => [...current, ...images])}
                  onRemoveFile={(index) => setFiles((current) => current.filter((_, itemIndex) => itemIndex !== index))}
                  onRemoveExisting={(id) => {
                    setExistingImages((current) => current.filter((image) => image.id !== id));
                    setRemovedImageIds((current) => [...current, id]);
                  }}
                  labels={{
                    hint: t("admin.dropzoneHint"),
                    primary: t("admin.primaryImage"),
                    remove: t("admin.removeImage"),
                  }}
                />
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
              <Form.Group className="col-md-4">
                <Form.Label>{t("cart.grams")}</Form.Label>
                <Form.Control name="grams" type="number" min="1" step="1" value={form.grams} onChange={update} required />
              </Form.Group>
              <Form.Group className="col-md-4">
                <Form.Label>{t("admin.gramPrice")}</Form.Label>
                <Form.Control name="gram_price" type="number" min="0" step="0.01" value={form.gram_price} onChange={update} required />
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
            <Button type="submit" variant="dark" disabled={saving}>
              {t("admin.save")}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </>
  );
}
