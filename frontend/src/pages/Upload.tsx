import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

type UploadStatus = "idle" | "uploading" | "processing" | "ready" | "error"

export default function Upload() {
  const navigate = useNavigate();
  const [filename, setFilename] = useState<string>();
  const [uploadStatus, setUploadStatus] = useState<UploadStatus>("idle")
  const [documentId, setDocumentId] = useState<string | null>(null)


  function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    setFilename(event.target.files?.[0]?.name);
  }

  useEffect(() => {
    if (uploadStatus !== "processing" || !documentId) return
    let timer: ReturnType<typeof setTimeout>;
    const poll = async() => {
      try {
        const res = await fetch(`http://localhost:8000/status/${documentId}`)
        if (res.ok) {
          const { status } = await res.json()
          setUploadStatus(status)
  
          if (status === "ready") {
            navigate("/ask")
          } else {
            timer = setTimeout(poll, 3000)
          }
        } else {
          setUploadStatus("error")
        }
      } catch (e) {
        setUploadStatus("error")
      }
    }
    poll();
    return () => clearTimeout(timer)
  }, [uploadStatus, documentId, navigate])

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formdata = new FormData(event.currentTarget);
    const file = formdata.get("file") as File;
    if (!(file instanceof File)) return;
    const body = new FormData();
    body.append("file", file);
    setUploadStatus("uploading")
    try {
      const res = await fetch("http://localhost:8000/upload", { method: "POST", body });
      if (res.ok) {
          const { document_id } = await res.json()
          setDocumentId(document_id)
          setUploadStatus("processing")
        } else {
          setUploadStatus("error")
        }
    } catch (e) {
      setUploadStatus("error")
    }
  }

  return (
    <div className="min-h-screen flex flex-col gap-4 items-center justify-center px-4">
      {uploadStatus === "idle" && (
        <form onSubmit={handleSubmit} className="flex flex-col items-center gap-4 w-full max-w-sm">
          <label className="w-full h-32 border-2 border-dashed border-gray-200 rounded-2xl flex flex-col items-center justify-center cursor-pointer hover:border-red-300 hover:bg-red-50 transition-colors">
            {filename
              ? <span className="text-sm text-gray-700 font-medium px-4 text-center truncate w-full text-center">{filename}</span>
              : <>
                  <span className="text-sm text-gray-400">Click to choose a file</span>
                  <span className="text-xs text-gray-300 mt-1">PDF, DOCX, MD, TXT supported</span>
                </>
            }
            <input type="file" name="file" accept=".pdf,.md,.txt,.docx" className="hidden" onChange={handleFileChange} />
          </label>
          <button
            type="submit"
            disabled={!filename || uploadStatus !== "idle"}
            className="w-full h-11 bg-red-500 hover:bg-red-600 disabled:opacity-50 transition-colors text-white text-sm font-medium rounded-full cursor-pointer shadow-sm"
          >
            Upload
          </button>
        </form>
      )}
      {uploadStatus === "uploading" && (
        <div className="flex flex-col items-center gap-2 text-gray-500">
          <div className="w-6 h-6 border-2 border-gray-300 border-t-red-500 rounded-full animate-spin" />
          <p className="text-sm">Uploading...</p>
        </div>
      )}
      {uploadStatus === "processing" && (
        <div className="flex flex-col items-center gap-2 text-gray-500">
          <div className="w-6 h-6 border-2 border-gray-300 border-t-red-500 rounded-full animate-spin" />
          <p className="text-sm">Processing document...</p>
        </div>
      )}
      {uploadStatus === "error" && (
        <div className="flex flex-col items-center gap-2">
          <p className="text-sm text-red-500 font-medium">Something went wrong.</p>
          <button
            onClick={() => navigate("/upload")}
            className="text-xs text-gray-400 underline cursor-pointer"
          >
            Try again
          </button>
        </div>
      )}
    </div>
  )
}
