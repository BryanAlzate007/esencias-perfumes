import api from "./api";

function list(path) {
  return api.get(path).then(({ data }) => data);
}

function create(path, payload) {
  return api.post(path, payload).then(({ data }) => data);
}

function update(path, id, payload) {
  return api.patch(`${path}${id}/`, payload).then(({ data }) => data);
}

function remove(path, id) {
  return api.delete(`${path}${id}/`);
}

export function listMainChords() {
  return list("/main-chords/");
}

export function createMainChord(payload) {
  return create("/main-chords/", payload);
}

export function updateMainChord(id, payload) {
  return update("/main-chords/", id, payload);
}

export function deleteMainChord(id) {
  return remove("/main-chords/", id);
}

export function listContainers() {
  return list("/containers/");
}

export function createContainer(payload) {
  return create("/containers/", payload);
}

export function updateContainer(id, payload) {
  return update("/containers/", id, payload);
}

export function deleteContainer(id) {
  return remove("/containers/", id);
}

export function listProfilePersons() {
  return list("/profile-persons/");
}

export function createProfilePerson(payload) {
  return create("/profile-persons/", payload);
}

export function updateProfilePerson(id, payload) {
  return update("/profile-persons/", id, payload);
}

export function deleteProfilePerson(id) {
  return remove("/profile-persons/", id);
}
