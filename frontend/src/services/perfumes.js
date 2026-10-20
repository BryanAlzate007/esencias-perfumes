import api from "./api";

export { listMainChords } from "./lookups";

export async function listPerfumes() {
  const { data } = await api.get("/perfumes/");
  return data;
}

export async function listAllPerfumes() {
  const { data } = await api.get("/perfumes/", { params: { page: 1 } });
  if (Array.isArray(data)) {
    return data;
  }
  const first = data.results || [];
  if (!data.next || first.length === 0) {
    return first;
  }
  const pageCount = Math.ceil((data.count || first.length) / first.length);
  const rest = await Promise.all(
    Array.from({ length: pageCount - 1 }, (_, index) =>
      api
        .get("/perfumes/", { params: { page: index + 2 } })
        .then((response) => response.data.results || []),
    ),
  );
  return first.concat(...rest);
}

export async function getPerfume(id) {
  const { data } = await api.get(`/perfumes/${id}/`);
  return data;
}

export async function createPerfume(payload) {
  const { data } = await api.post("/perfumes/", payload);
  return data;
}

export async function updatePerfume(id, payload) {
  const { data } = await api.patch(`/perfumes/${id}/`, payload);
  return data;
}

export async function deletePerfume(id) {
  await api.delete(`/perfumes/${id}/`);
}

export async function downloadPerfumesExcel() {
  const { data } = await api.get("/perfumes/export/", { responseType: "blob" });
  const url = URL.createObjectURL(data);
  const link = document.createElement("a");
  link.href = url;
  link.download = "catalogo-perfumes.xlsx";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

export async function importPerfumesExcel(file) {
  const payload = new FormData();
  payload.append("file", file);
  const { data } = await api.post("/perfumes/import/", payload);
  return data;
}
