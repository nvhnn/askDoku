import { useState } from "react";

type Source = {
    filename: string
    page_number: number
    section_title: string | null
}

export default function Ask() {
    const [answer, setAnswer] = useState<string>();
    const [sources, setSources] = useState<Source[]>([]);

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setAnswer("");
        setSources([]);
        const formdata = new FormData(event.currentTarget);
        const question = formdata.get("text") as string;
        const res = await fetch(`http://localhost:8000/ask?question=${encodeURIComponent(question)}`, {
            method: "POST",
        });
        const utf8decoder = new TextDecoder();
        const reader = res.body?.getReader();
        if (!reader) return;
        while (true) {
            const { done, value } = await reader?.read();
            if (done) break;
            const decodedValue = utf8decoder.decode(value);
            for (const line of decodedValue.split("\n\n")) {
                if (!line) continue;
                const response = line.slice(6);
                if (response === "DONE") break;
                response.startsWith("{") ? setSources(prev => [...prev, JSON.parse(response)]) : setAnswer(prev => prev + response)
            }
        }
    }

    return (
        <div className="h-screen flex flex-col gap-8 items-center justify-center">
            <form onSubmit={handleSubmit} className="flex gap-6 w-2/3">
                <input type="text" name="text" placeholder="What is this document about?" className="w-full h-10 border rounded-full text-center"/>
                <button type="submit" className="bg-red-500 w-1/5 text-white rounded-full cursor-pointer">Enter</button>
            </form>
            {answer && <p className="w-2/3 text-center italic">{answer}</p>}
            {sources.length > 0 && (
                <div className="flex flex-wrap gap-2 w-2/3 justify-center">
                    {sources.map((source, i) => (
                        <span
                            key={i}
                            title={source.section_title ?? undefined}
                            className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-700 text-sm rounded-full cursor-pointer hover:bg-red-200 transition-colors"
                        >
                            <span>{source.filename}</span>
                            <span className="text-red-400">·</span>
                            <span>p.{source.page_number}</span>
                            {source.section_title && (
                                <>
                                    <span className="text-red-400">·</span>
                                    <span>{source.section_title}</span>
                                </>
                            )}
                        </span>
                    ))}
                </div>
            )}
        </div>
    )
}
