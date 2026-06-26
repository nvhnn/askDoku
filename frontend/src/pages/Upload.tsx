import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Upload() {
  const navigate = useNavigate();
  const [filename, setFilename] = useState<string>();
  const [loading, setLoading] = useState(false);

  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    setFilename(event.target.files?.[0]?.name);
  }

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formdata = new FormData(event.currentTarget);
    const file = formdata.get("file") as File;
    if (!(file instanceof File)) return;
    const body = new FormData();
    body.append("file", file);
    setLoading(true);
    fetch("http://localhost:8000/upload", { method: "POST", body })
      .then(res => res.ok ? navigate("/ask") : console.log("Failed to upload file"))
      .finally(() => setLoading(false));
  }

  return (
    <div className="min-h-screen flex flex-col gap-4 items-center justify-center px-4">
      <form onSubmit={handleSubmit} className="flex flex-col items-center gap-4 w-full max-w-sm">
        <label className="w-full h-32 border-2 border-dashed border-gray-200 rounded-2xl flex flex-col items-center justify-center cursor-pointer hover:border-red-300 hover:bg-red-50 transition-colors">
          {filename
            ? <span className="text-sm text-gray-700 font-medium px-4 text-center truncate w-full text-center">{filename}</span>
            : <>
                <span className="text-sm text-gray-400">Click to choose a file</span>
                <span className="text-xs text-gray-300 mt-1">PDF supported</span>
              </>
          }
          <input type="file" name="file" accept=".pdf" className="hidden" onChange={handleFileChange} />
        </label>
        <button
          type="submit"
          disabled={!filename || loading}
          className="w-full h-11 bg-red-500 hover:bg-red-600 disabled:opacity-50 transition-colors text-white text-sm font-medium rounded-full cursor-pointer shadow-sm"
        >
          {loading ? "Uploading..." : "Upload"}
        </button>
      </form>
    </div>
  )
}
