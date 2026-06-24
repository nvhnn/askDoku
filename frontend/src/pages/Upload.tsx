import { useNavigate } from "react-router-dom";

export default function Upload() {
  const navigate = useNavigate()

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formdata = new FormData(event.currentTarget);
    const file = formdata.get("file") as File;
    if (file instanceof File) {
      const body = new FormData();
      body.append("file", file);
      fetch("http://localhost:8000/upload", {
        method: "POST",
        body,
      })
      .then(res => res.ok ? navigate("/ask") : console.log("Failed to upload file"));
      {/* later add ui for error message replacing console.log */}
    }
  }

  return (
    <div className="h-screen flex flex-col gap-8 items-center justify-center">
      <form onSubmit={handleSubmit} className="flex gap-6 w-1/2 ml-25">
        <label className="w-60 h-10 border rounded-full flex items-center justify-center cursor-pointer">
          <span>Choose file</span>
          <input type="file" name="file" className="hidden" />
        </label>
        <button type="submit" className="bg-red-500 w-1/5 text-white rounded-full cursor-pointer">Upload</button>
      </form>
    </div>
  )
}
