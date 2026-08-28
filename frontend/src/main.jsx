import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import * as THREE from 'three';
import { ArrowUp, Check, ChevronDown, FileText, FolderOpen, Gauge, LoaderCircle, Plus, Search, ShieldCheck, Sparkles, Upload, X } from 'lucide-react';
import './styles.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function Login({ onAuth }) {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const submit = async (event) => {
    event.preventDefault(); setError('');
    const response = await fetch(`${API}/auth/${mode}`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(form) });
    const body = await response.json();
    if (!response.ok) { setError(body.detail || 'Unable to authenticate'); return; }
    localStorage.setItem('tracerag_token', body.token); onAuth(body.email);
  };
  return <main className="auth-shell"><div className="auth-visual"><div className="auth-grid"/><div className="auth-orb"/><span className="auth-coordinate">37.7749° N / 122.4194° W</span><div className="auth-quote">Your knowledge,<br/><em>with a point of view.</em></div></div><section className="auth-panel"><div className="brand"><span className="brand-mark"><Sparkles size={16}/></span><span>Trace<span className="brand-accent">RAG</span></span></div><div className="auth-copy"><div className="eyebrow">Private knowledge workspace</div><h1>{mode === 'login' ? 'Welcome back.' : 'Create your workspace.'}</h1><p>Ask better questions of the information your team already owns.</p></div><form onSubmit={submit} className="auth-form"><label>Email address<input type="email" required value={form.email} onChange={e => setForm({...form,email:e.target.value})} placeholder="you@company.com"/></label><label>Password<input type="password" required minLength="8" value={form.password} onChange={e => setForm({...form,password:e.target.value})} placeholder="8+ characters"/></label>{error && <div className="form-error">{error}</div>}<button className="auth-submit" type="submit">{mode === 'login' ? 'Enter workspace' : 'Create account'} <ArrowUp size={17}/></button></form><button className="mode-switch" onClick={() => {setMode(mode === 'login' ? 'register' : 'login');setError('')}}>{mode === 'login' ? 'New to TraceRAG? Create an account' : 'Already have an account? Sign in'}</button><div className="auth-foot"><ShieldCheck size={14}/> Your workspace is private by default</div></section></main>;
}

function KnowledgeSpace({ count }) {
  const mountRef = useRef(null);
  useEffect(() => {
    const canvas = mountRef.current; const scene = new THREE.Scene(); const camera = new THREE.PerspectiveCamera(48, canvas.clientWidth / canvas.clientHeight, 0.1, 100); camera.position.z = 5;
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true }); renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
    const group = new THREE.Group(); scene.add(group); const geometry = new THREE.IcosahedronGeometry(.08, 1); const material = new THREE.MeshBasicMaterial({ color: 0xc9f66d });
    for (let index = 0; index < Math.max(count * 5, 12); index += 1) { const node = new THREE.Mesh(geometry, material); const angle = index * 2.4; const radius = .8 + (index % 5) * .23; node.position.set(Math.cos(angle) * radius, Math.sin(angle * 1.3) * .75, Math.sin(angle) * radius * .5); group.add(node); }
    const ring = new THREE.Mesh(new THREE.TorusGeometry(1.7, .008, 8, 80), new THREE.MeshBasicMaterial({ color: 0x61705b, transparent: true, opacity: .7 })); ring.rotation.x = 1.1; group.add(ring); let frame;
    const animate = () => { frame = requestAnimationFrame(animate); group.rotation.y += .0025; group.rotation.x = Math.sin(Date.now() * .0003) * .08; renderer.render(scene, camera); }; animate();
    return () => { cancelAnimationFrame(frame); renderer.dispose(); geometry.dispose(); material.dispose(); };
  }, [count]);
  return <canvas className="knowledge-space" ref={mountRef} aria-label="Three-dimensional indexed knowledge space"/>;
}

function App() {
  const [user, setUser] = useState(localStorage.getItem('tracerag_email'));
  const [documents, setDocuments] = useState([]);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef(null);

  const token = localStorage.getItem('tracerag_token'); const authHeaders = { Authorization: `Bearer ${token}` };
  const loadDocuments = () => fetch(`${API}/documents`, {headers: authHeaders}).then((r) => r.ok ? r.json() : []).then(setDocuments).catch(() => setDocuments([]));
  useEffect(() => { if (user) loadDocuments(); }, [user]);

  async function upload(file) {
    if (!file) return;
    setUploading(true);
    const data = new FormData(); data.append('file', file);
    await fetch(`${API}/documents/upload`, { method: 'POST', headers: authHeaders, body: data });
    await loadDocuments(); setUploading(false);
  }

  async function ask(event) {
    event.preventDefault(); if (!question.trim() || loading) return;
    setLoading(true); setAnswer(null);
    const response = await fetch(`${API}/query`, { method: 'POST', headers: {'Content-Type': 'application/json', ...authHeaders}, body: JSON.stringify({ question }) });
    setAnswer(response.ok ? await response.json() : { answer: 'The API is not reachable. Start the FastAPI server and try again.', citations: [] }); setLoading(false);
  }

  if (!user) return <Login onAuth={(email) => { localStorage.setItem('tracerag_email', email); setUser(email); }} />;
  return <div className="app-shell">
    <header className="topbar"><div className="brand"><span className="brand-mark"><Sparkles size={16}/></span><span>Trace<span className="brand-accent">RAG</span></span></div><div className="topbar-right"><span className="status"><span className="pulse"/>System operational</span><button className="icon-button" title="New session" onClick={() => {setAnswer(null);setQuestion('')}}><Plus size={18}/></button><div className="avatar">PP</div></div></header>
    <main className="workspace">
      <aside className="sidebar"><div className="eyebrow">Workspace</div><div className="workspace-name">Acme knowledge base <ChevronDown size={15}/></div><nav><a className="active"><Search size={16}/>Ask anything</a><a><FolderOpen size={16}/>Documents <span className="nav-count">{documents.length}</span></a></nav><div className="sidebar-divider"/><div className="eyebrow">Indexed sources</div><div className="doc-list">{documents.length ? documents.map((doc) => <div className="doc-item" key={doc.name}><FileText size={16}/><div><strong>{doc.name}</strong><small>{doc.chunks} chunks</small></div><Check className="doc-check" size={14}/></div>) : <div className="empty-docs">No documents yet.<br/>Add a source to begin.</div>}</div><button className="add-source" onClick={() => inputRef.current?.click()}><Upload size={15}/> Add source</button><input ref={inputRef} type="file" accept=".pdf,.txt,.md,.csv" hidden onChange={(e) => upload(e.target.files[0])}/><div className="sidebar-foot"><ShieldCheck size={15}/><span>Citations are always<br/>linked to source text.</span></div></aside>
      <section className="content"><div className="content-head"><div><div className="eyebrow">Production RAG / Query</div><h1>Ask your <em>company.</em></h1><p className="subhead">Grounded answers from your internal knowledge base.</p></div><div className="retrieval-badge"><span className="badge-dot"/>Hybrid retrieval <strong>BM25 + dense</strong></div></div>
        <KnowledgeSpace count={documents.length} />
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
