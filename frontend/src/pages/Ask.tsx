import { useState } from "react";

type Source = {
    filename: string
    page_number: number
    section_title: string | null
    content: string
    similarity: number
}

export default function Ask() {
    const [answer, setAnswer] = useState<string>();
    const [sources, setSources] = useState<Source[]>([]);
    const [showSources, setShowSources] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(false);

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setAnswer("");
        setSources([]);
        setShowSources(false);
        setLoading(true);
        const formdata = new FormData(event.currentTarget);
        const question = formdata.get("text") as string;
        const res = await fetch(`http://localhost:8000/ask?question=${encodeURIComponent(question)}`, {
            method: "POST",
        });
        const utf8decoder = new TextDecoder();
        const reader = res.body?.getReader();
        if (!reader) { setLoading(false); return; }
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
        setLoading(false);
    }

    return (
        <div className="min-h-screen flex flex-col gap-8 items-center justify-center px-4 py-12">
            <form onSubmit={handleSubmit} className="flex gap-3 w-full max-w-2xl">
                <input
                    type="text"
                    name="text"
                    placeholder="What is this document about?"
                    className="w-full h-11 border border-gray-200 rounded-full px-5 text-sm shadow-sm focus:outline-none focus:ring-2 focus:ring-red-300"
                />
                <button type="submit" disabled={loading} className="bg-red-500 hover:bg-red-600 disabled:opacity-60 transition-colors h-11 px-6 text-white text-sm font-medium rounded-full cursor-pointer whitespace-nowrap shadow-sm">
                    {loading ? "Thinking..." : "Ask"}
                </button>
            </form>

            {loading && !answer && (
                <div className="w-full max-w-2xl flex flex-col gap-2">
                    <div className="h-3 bg-gray-200 rounded-full animate-pulse w-3/4 mx-auto" />
                    <div className="h-3 bg-gray-200 rounded-full animate-pulse w-1/2 mx-auto" />
                </div>
            )}
            {answer && (
                <p className="w-full max-w-2xl text-gray-700 leading-relaxed italic text-center">{answer}</p>
            )}

            {sources.length > 0 && (
                <div className="w-full max-w-2xl flex flex-col items-center gap-4">
                    <button
                        onClick={() => setShowSources(prev => !prev)}
                        className="px-5 py-2 rounded-full bg-red-500 hover:bg-red-600 transition-colors text-white text-sm font-medium cursor-pointer"
                    >
                        {showSources ? "Hide Sources" : `Show ${sources.length} Sources`}
                    </button>

                    {showSources && (
                        <div className="grid grid-cols-2 gap-3 w-full">
                            {sources.map((source, i) => (
                                <div key={i} className="flex flex-col gap-2 rounded-xl p-4 bg-red-50 border border-red-100">
                                    <p className="line-clamp-3 text-sm text-gray-700 leading-relaxed">{source.content}</p>
                                    <div className="flex flex-col gap-0.5 pt-2 border-t border-red-100">
                                        <span className="text-xs font-medium text-gray-600 truncate">{source.filename}</span>
                                        <div className="flex items-center justify-between text-xs text-gray-400">
                                            <span>{source.section_title ?? `Page ${source.page_number}`}</span>
                                            <span className="font-mono">{(source.similarity * 100).toFixed(0)}% match</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
