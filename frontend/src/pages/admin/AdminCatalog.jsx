import { useEffect, useState } from "react";
import { Alert, Button, Form, Table } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { createPerfume, deletePerfume, listPerfumes, updatePerfume } from "../../services/perfumes";

const emptyForm = {
  name: "",
  brand: "",
  description: "",
  notes: "",
  image_url: "",
  price: "",
  is_active: true,
};

export default function AdminCatalog() {
  const { t } = useTranslation();
  const [perfumes, setPerfumes] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  async function load() {
    const data = await listPerfumes();
    setPerfumes(data.results || []);
  }

  useEffect(() => {
    load().catch(() => setError(t("common.error")));
  }, [t]);

  function update(event) {
    const { name, value, type, checked } = event.target;
    setForm((current) => ({ ...current, [name]: type === "checkbox" ? checked : value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    const payload = { ...form, price: Number(form.price) };
    if (editingId) {
      await updatePerfume(editingId, payload);
    } else {
      await createPerfume(payload);
    }
    setForm(emptyForm);
    setEditingId(null);
    await load();
  }

  async function handleDelete(id) {
    await deletePerfume(id);
    await load();
  }

  return (
    <>
      <h1 className="h2 mb-4">{t("admin.catalogTitle")}</h1>
      {error && <Alert variant="danger">{error}</Alert>}
      <Form className="border rounded p-3 mb-4" onSubmit={handleSubmit}>
        <h2 className="h5 mb-3">{editingId ? t("admin.save") : t("admin.newPerfume")}</h2>
        <div className="row g-3">
          <Form.Group className="col-md-6">
            <Form.Label>{t("auth.name")}</Form.Label>
            <Form.Control name="name" value={form.name} onChange={update} required />
          </Form.Group>
          <Form.Group className="col-md-6">
            <Form.Label>Brand</Form.Label>
            <Form.Control name="brand" value={form.brand} onChange={update} required />
          </Form.Group>
          <Form.Group className="col-12">
            <Form.Label>URL</Form.Label>
            <Form.Control name="image_url" value={form.image_url} onChange={update} required />
          </Form.Group>
          <Form.Group className="col-md-4">
            <Form.Label>$</Form.Label>
            <Form.Control name="price" type="number" step="0.01" value={form.price} onChange={update} required />
          </Form.Group>
          <Form.Group className="col-12">
            <Form.Label>Notes</Form.Label>
            <Form.Control name="notes" value={form.notes} onChange={update} placeholder="Sándalo · Ámbar · Vainilla" />
          </Form.Group>
          <Form.Group className="col-12">
            <Form.Label>{t("home.subtitle")}</Form.Label>
            <Form.Control as="textarea" rows={3} name="description" value={form.description} onChange={update} required />
          </Form.Group>
        </div>
        <Button type="submit" variant="dark" className="mt-3">
          {t("admin.save")}
        </Button>
      </Form>
      <Table responsive hover>
        <thead>
          <tr>
            <th>{t("auth.name")}</th>
            <th>Brand</th>
            <th>$</th>
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
                <Button
                  size="sm"
                  variant="outline-secondary"
                  className="me-2"
                  onClick={() => {
                    setEditingId(perfume.id);
                    setForm({
                      name: perfume.name,
                      brand: perfume.brand,
                      description: perfume.description,
                      notes: perfume.notes || "",
                      image_url: perfume.image_url,
                      price: perfume.price,
                      is_active: perfume.is_active,
                    });
                  }}
                >
                  Edit
                </Button>
                <Button size="sm" variant="outline-danger" onClick={() => handleDelete(perfume.id)}>
                  {t("common.delete")}
                </Button>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </>
  );
}
