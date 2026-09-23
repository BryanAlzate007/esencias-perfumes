import Select from "react-select";
import { useTranslation } from "react-i18next";
import "./RelationSelect.css";

export default function RelationSelect({ multiple = false, options, value, onChange, inputId, placeholder }) {
  const { t } = useTranslation();
  const selected = multiple
    ? options.filter((option) => value.includes(option.value))
    : options.find((option) => option.value === value) || null;

  return (
    <Select
      inputId={inputId}
      classNamePrefix="select2"
      isMulti={multiple}
      isClearable={!multiple}
      closeMenuOnSelect={!multiple}
      options={options}
      value={selected}
      placeholder={placeholder || t("admin.search")}
      noOptionsMessage={() => t("admin.noOptions")}
      menuPortalTarget={document.body}
      menuPosition="fixed"
      onChange={(next) => {
        if (multiple) {
          onChange((next || []).map((option) => option.value));
          return;
        }
        onChange(next ? next.value : "");
      }}
    />
  );
}
