import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ArrowUp, Check, ChevronDown, FileText, FolderOpen, Gauge, LoaderCircle, Plus, Search, ShieldCheck, Sparkles, Upload, X } from 'lucide-react';
import './styles.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function App() {
  const [documents, setDocuments] = useState([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef(null);

  const loadDocuments = () => fetch(`${API}/documents`).then((r) => r.ok ? r.json() : []).then(setDocuments).catch(() => setDocuments([]));
  useEffect(() => { loadDocuments(); }, []);

  async function upload(file) {
    if (!file) return;
    setUploading(true);
    const data = new FormData(); data.append('file', file);
    await fetch(`${API}/documents/upload`, { method: 'POST', body: data });
    await loadDocuments(); setUploading(false);
  }

  async function ask(event) {
    event.preventDefault(); if (!question.trim() || loading) return;
    setLoading(true); setAnswer(null);
    const response = await fetch(`${API}/query`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ question }) });
    setAnswer(response.ok ? await response.json() : { answer: 'The API is not reachable. Start the FastAPI server and try again.', citations: [] }); setLoading(false);
  }

  return <div className="app-shell">
    <header className="topbar"><div className="brand"><span className="brand-mark"><Sparkles size={16}/></span><span>Trace<span className="brand-accent">RAG</span></span></div><div className="topbar-right"><span className="status"><span className="pulse"/>System operational</span><button className="icon-button" title="New session" onClick={() => {setAnswer(null);setQuestion('')}}><Plus size={18}/></button><div className="avatar">PP</div></div></header>
    <main className="workspace">
      <aside className="sidebar"><div className="eyebrow">Workspace</div><div className="workspace-name">Acme knowledge base <ChevronDown size={15}/></div><nav><a className="active"><Search size={16}/>Ask anything</a><a><FolderOpen size={16}/>Documents <span className="nav-count">{documents.length}</span></a></nav><div className="sidebar-divider"/><div className="eyebrow">Indexed sources</div><div className="doc-list">{documents.length ? documents.map((doc) => <div className="doc-item" key={doc.name}><FileText size={16}/><div><strong>{doc.name}</strong><small>{doc.chunks} chunks</small></div><Check className="doc-check" size={14}/></div>) : <div className="empty-docs">No documents yet.<br/>Add a source to begin.</div>}</div><button className="add-source" onClick={() => inputRef.current?.click()}><Upload size={15}/> Add source</button><input ref={inputRef} type="file" accept=".pdf,.txt,.md,.csv" hidden onChange={(e) => upload(e.target.files[0])}/><div className="sidebar-foot"><ShieldCheck size={15}/><span>Citations are always<br/>linked to source text.</span></div></aside>
      <section className="content"><div className="content-head"><div><div className="eyebrow">Production RAG / Query</div><h1>Ask your <em>company.</em></h1><p className="subhead">Grounded answers from your internal knowledge base.</p></div><div className="retrieval-badge"><span className="badge-dot"/>Hybrid retrieval <strong>BM25 + dense</strong></div></div>
        {!answer && !loading && <div className="prompt-area"><div className="prompt-orbit"><div className="orbit-core"><Sparkles size={28}/></div><span className="orbit-label label-one">Search</span><span className="orbit-label label-two">Reason</span><span className="orbit-label label-three">Cite</span></div><p className="hint">Ask a question about your indexed documents</p></div>}
        {loading && <div className="loading-state"><LoaderCircle className="spin" size={26}/><span>Searching across {documents.reduce((sum, doc) => sum + doc.chunks, 0)} indexed chunks...</span></div>}
        {answer && <div className="answer-panel"><div className="answer-kicker"><span className="answer-icon"><Sparkles size={15}/></span> Answer <span className="answer-meta"><Gauge size={14}/> {answer.latency_ms}ms · {answer.retrieval_mode}</span></div><div className="answer-text">{answer.answer}</div><div className="sources-head"><span>Evidence used</span><span className="source-count">{answer.citations.length} sources</span></div><div className="sources">{answer.citations.map((source, index) => <details className="source" key={`${source.document}-${index}`} open={index === 0}><summary><span className="source-number">0{index + 1}</span><span className="source-name">{source.document}{source.page ? ` · page ${source.page}` : ''}</span><span className="source-score">{Math.round(source.score * 100)}% match <ChevronDown size={15}/></span></summary><p>{source.snippet}</p></details>)}</div></div>}
        <form className="composer" onSubmit={ask}><div className="composer-label"><span className="label-key">QUERY</span><span>⌘ Enter to run</span></div><div className="input-row"><textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="e.g. What is our remote work policy?" rows="2"/><button className="send-button" type="submit" disabled={!question.trim() || loading} title="Ask question"><ArrowUp size={20}/></button></div><div className="composer-foot"><span><span className="green-dot"/> Answers restricted to indexed sources</span><span>Local mode</span></div></form>
      </section>
    </main>
    {uploading && <div className="toast"><LoaderCircle className="spin" size={16}/> Indexing document...</div>}
  </div>
}

export default App;

createRoot(document.getElementById('root')).render(<App />);
