import { useEffect, useState } from "react";
import { Form, Table } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { listUsers, updateUser } from "../../services/auth";

export default function AdminUsers() {
  const { t } = useTranslation();
  const [users, setUsers] = useState([]);

  async function load() {
    const data = await listUsers();
    setUsers(data.results || []);
  }

  useEffect(() => {
    load().catch(() => setUsers([]));
  }, []);

  async function handleRole(id, role) {
    await updateUser(id, { role });
    await load();
  }

  return (
    <>
      <h1 className="h2 mb-4">{t("admin.usersTitle")}</h1>
      <Table responsive hover>
        <thead>
          <tr>
            <th>{t("auth.username")}</th>
            <th>{t("auth.email")}</th>
            <th>{t("admin.role")}</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>{user.email}</td>
              <td>
                <Form.Select value={user.role} onChange={(event) => handleRole(user.id, event.target.value)}>
                  <option value="customer">{t("admin.customer")}</option>
                  <option value="admin">{t("admin.admin")}</option>
                </Form.Select>
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </>
  );
}
