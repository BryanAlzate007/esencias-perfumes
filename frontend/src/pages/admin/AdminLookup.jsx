import { useEffect, useState } from "react";
import { Alert, Button, Form, Modal, Table } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { Link, Navigate, useParams } from "react-router-dom";
import RelationSelect from "../../components/RelationSelect/RelationSelect";
import {
  createContainer,
  createMainChord,
  createProfilePerson,
  deleteContainer,
  deleteMainChord,
  deleteProfilePerson,
  listContainers,
  listMainChords,
  listProfilePersons,
  updateContainer,
  updateMainChord,
  updateProfilePerson,
} from "../../services/lookups";

const RESOURCES = {
  acordes: {
    titleKey: "admin.mainChords",
    columns: [
      { key: "name", labelKey: "auth.name" },
      { key: "description", labelKey: "admin.description" },
    ],
    fields: [
      { name: "name", labelKey: "auth.name", required: true },
      { name: "description", labelKey: "admin.description", type: "textarea", required: true },
    ],
    list: listMainChords,
    create: createMainChord,
    update: updateMainChord,
    remove: deleteMainChord,
  },
  envases: {
    titleKey: "admin.containers",
    columns: [
      { key: "name", labelKey: "auth.name" },
      { key: "type", labelKey: "admin.type" },
      { key: "color", labelKey: "admin.color" },
    ],
    fields: [
      { name: "name", labelKey: "auth.name", required: true, col: "col-md-6" },
      { name: "type", labelKey: "admin.type", required: true, col: "col-md-6" },
      { name: "image_url", labelKey: "admin.imageUrl", required: true },
      { name: "size", labelKey: "admin.size", required: true, col: "col-md-4" },
      { name: "weight", labelKey: "admin.weight", required: true, col: "col-md-4" },
      { name: "volume", labelKey: "admin.volume", required: true, col: "col-md-4" },
      { name: "material", labelKey: "admin.material", required: true, col: "col-md-6" },
      { name: "color", labelKey: "admin.color", required: true, col: "col-md-6" },
      { name: "main_chords", labelKey: "admin.mainChords", type: "chords" },
      { name: "description", labelKey: "admin.description", type: "textarea", required: true },
      { name: "is_active", labelKey: "admin.active", type: "checkbox" },
    ],
    list: listContainers,
    create: createContainer,
    update: updateContainer,
    remove: deleteContainer,
  },
  perfiles: {
    titleKey: "admin.personalProfile",
    columns: [
      { key: "name", labelKey: "auth.name" },
      { key: "description", labelKey: "admin.description" },
    ],
    fields: [
      { name: "name", labelKey: "auth.name", required: true },
      { name: "description", labelKey: "admin.description", type: "textarea", required: true },
    ],
    list: listProfilePersons,
    create: createProfilePerson,
    update: updateProfilePerson,
    remove: deleteProfilePerson,
  },
};

function emptyForm(fields) {
  return Object.fromEntries(
    fields.map((field) => {
      if (field.type === "chords") {
        return [field.name, []];
      }
      if (field.type === "checkbox") {
        return [field.name, true];
      }
      return [field.name, ""];
    }),
  );
}

function formFromItem(fields, item) {
  return Object.fromEntries(
    fields.map((field) => {
      const value = item[field.name];
      if (field.type === "chords") {
        return [field.name, value || []];
      }
      if (field.type === "checkbox") {
        return [field.name, Boolean(value)];
      }
      return [field.name, value ?? ""];
    }),
  );
}

export default function AdminLookup() {
  const { section } = useParams();
  const resource = RESOURCES[section];
  if (!resource) {
    return <Navigate to="/admin/configuraciones" replace />;
  }
  return <LookupScreen key={section} resource={resource} />;
}

function LookupScreen({ resource }) {
  const { t } = useTranslation();
  const initialForm = emptyForm(resource.fields);
  const [rows, setRows] = useState([]);
  const [chords, setChords] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [editingId, setEditingId] = useState(null);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  const needsChords = resource.fields.some((field) => field.type === "chords");

  async function load() {
    const requests = [resource.list()];
    if (needsChords) {
      requests.push(listMainChords());
    }
    const [data, chordData] = await Promise.all(requests);
    setRows(data);
    if (chordData) {
      setChords(chordData.map((chord) => ({ value: chord.id, label: chord.name })));
    }
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
    setForm(initialForm);
    setError("");
    setOpen(true);
  }

  function openEdit(item) {
    setEditingId(item.id);
    setForm(formFromItem(resource.fields, item));
    setError("");
    setOpen(true);
  }

  function closeModal() {
    setOpen(false);
    setEditingId(null);
    setForm(initialForm);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    try {
      if (editingId) {
        await resource.update(editingId, form);
      } else {
        await resource.create(form);
      }
      closeModal();
      await load();
    } catch {
      setError(t("common.error"));
    }
  }

  async function handleDelete(id) {
    await resource.remove(id);
    await load();
  }

  return (
    <>
      <Link to="/admin/configuraciones" className="perfume-settings-back">
        {t("nav.settings")}
      </Link>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h2 mb-0">{t(resource.titleKey)}</h1>
        <Button variant="dark" onClick={openCreate}>
          {t("admin.add")}
        </Button>
      </div>
      {error && !open && <Alert variant="danger">{error}</Alert>}
      <Table responsive hover>
        <thead>
          <tr>
            {resource.columns.map((column) => (
              <th key={column.key}>{t(column.labelKey)}</th>
            ))}
            <th></th>
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 && (
            <tr>
              <td colSpan={resource.columns.length + 1} className="text-body-secondary">
                {t("admin.emptyLookup")}
              </td>
            </tr>
          )}
          {rows.map((item) => (
            <tr key={item.id}>
              {resource.columns.map((column) => (
                <td key={column.key}>{item[column.key]}</td>
              ))}
              <td className="text-end">
                <Button size="sm" variant="outline-secondary" className="me-2" onClick={() => openEdit(item)}>
                  {t("admin.edit")}
                </Button>
                <Button size="sm" variant="outline-danger" onClick={() => handleDelete(item.id)}>
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
            <Modal.Title>{editingId ? t("admin.edit") : t("admin.add")}</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            {error && open && <Alert variant="danger">{error}</Alert>}
            <div className="row g-3">
              {resource.fields.map((field) => (
                <Form.Group className={field.col || "col-12"} key={field.name}>
                  {field.type === "checkbox" ? (
                    <Form.Check name={field.name} checked={form[field.name]} onChange={update} label={t(field.labelKey)} />
                  ) : (
                    <>
                      <Form.Label htmlFor={`lookup-${field.name}`}>{t(field.labelKey)}</Form.Label>
                      {field.type === "chords" ? (
                        <RelationSelect
                          multiple
                          inputId={`lookup-${field.name}`}
                          options={chords}
                          value={form[field.name]}
                          onChange={(next) => setForm((current) => ({ ...current, [field.name]: next }))}
                        />
                      ) : (
                        <Form.Control
                          id={`lookup-${field.name}`}
                          name={field.name}
                          as={field.type === "textarea" ? "textarea" : "input"}
                          rows={field.type === "textarea" ? 3 : undefined}
                          value={form[field.name]}
                          onChange={update}
                          required={field.required}
                        />
                      )}
                    </>
                  )}
                </Form.Group>
              ))}
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
