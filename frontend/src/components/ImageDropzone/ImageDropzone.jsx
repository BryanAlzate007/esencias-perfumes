import { useEffect, useRef, useState } from "react";
import { mediaUrl } from "../../lib/media";
import "./ImageDropzone.css";

export default function ImageDropzone({ files, existing, onAdd, onRemoveFile, onRemoveExisting, labels }) {
  const inputRef = useRef(null);
  const [active, setActive] = useState(false);
  const [previews, setPreviews] = useState([]);

  useEffect(() => {
    const next = files.map((file) => ({ file, url: URL.createObjectURL(file) }));
    setPreviews(next);
    return () => {
      next.forEach((item) => URL.revokeObjectURL(item.url));
    };
  }, [files]);

  function addFiles(fileList) {
    const images = [...fileList].filter((file) => file.type.startsWith("image/"));
    if (images.length) {
      onAdd(images);
    }
  }

  function openPicker() {
    inputRef.current?.click();
  }

  return (
    <div>
      <div
        className={`image-dropzone${active ? " is-active" : ""}`}
        role="button"
        tabIndex={0}
        onClick={openPicker}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            openPicker();
          }
        }}
        onDragOver={(event) => {
          event.preventDefault();
          setActive(true);
        }}
        onDragLeave={() => setActive(false)}
        onDrop={(event) => {
          event.preventDefault();
          setActive(false);
          addFiles(event.dataTransfer.files);
        }}
      >
        <p className="image-dropzone-hint">{labels.hint}</p>
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          multiple
          hidden
          onChange={(event) => {
            addFiles(event.target.files);
            event.target.value = "";
          }}
        />
      </div>
      {(existing.length > 0 || previews.length > 0) && (
        <div className="image-dropzone-grid">
          {existing.map((image) => (
            <figure key={image.id} className="image-dropzone-item">
              <img src={mediaUrl(image.image)} alt={image.alt_text || ""} />
              {image.is_primary && <span className="image-dropzone-badge">{labels.primary}</span>}
              <button type="button" className="image-dropzone-remove" onClick={() => onRemoveExisting(image.id)}>
                {labels.remove}
              </button>
            </figure>
          ))}
          {previews.map((item, index) => (
            <figure key={item.url} className="image-dropzone-item">
              <img src={item.url} alt="" />
              {existing.length === 0 && index === 0 && <span className="image-dropzone-badge">{labels.primary}</span>}
              <button type="button" className="image-dropzone-remove" onClick={() => onRemoveFile(index)}>
                {labels.remove}
              </button>
            </figure>
          ))}
        </div>
      )}
    </div>
  );
}
