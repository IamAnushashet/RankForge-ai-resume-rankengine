import React, { useEffect, useMemo, useState, useRef } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  BarChart3,
  CheckCircle2,
  Download,
  Gauge,
  LayoutDashboard,
  ListOrdered,
  Play,
  Search,
  ShieldCheck,
  Sparkles,
  UserRoundSearch,
  AlertCircle,
  Clock,
  Terminal,
  Settings as SettingsIcon,
  ChevronRight,
  Target
} from "lucide-react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import "./styles.css";

const API = "http://127.0.0.1:8000";

type TopRow = {
  candidate_id: string;
  rank: number;
  score: number;
  reasoning: string;
};

type Metrics = {
  totalCandidates: number;
  topScore: number;
  averageScore: number;
  pipelineRuntime: string;
  scoreDistribution: Record<string, number>[];
  explainability: { name: string; average: number; weight: number; contribution: number }[];
};

type CandidateDetail = {
  candidate: any;
  score: any;
  ranking: TopRow;
  explanation?: any;
};

type Page = "Dashboard" | "Leaderboard" | "Explorer" | "Explainability" | "Submission" | "Settings";

const pages: { name: Page; icon: React.ReactNode }[] = [
  { name: "Dashboard", icon: <LayoutDashboard size={18} /> },
  { name: "Leaderboard", icon: <ListOrdered size={18} /> },
  { name: "Explorer", icon: <UserRoundSearch size={18} /> },
  { name: "Explainability", icon: <BarChart3 size={18} /> },
  { name: "Submission", icon: <ShieldCheck size={18} /> },
  { name: "Settings", icon: <SettingsIcon size={18} /> }
];

async function getJson<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API}${path}`, options);

  if (!res.ok) {
    throw new Error(await res.text());
  }

  return res.json();
}

function Card({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <section className={`glass ${className}`}>{children}</section>;
}

function Stat({ label, value, icon, color = "#7dd3fc" }: { label: string; value: string | number; icon: React.ReactNode; color?: string }) {
  return (
    <Card className="stat">
      <div className="statIcon" style={{ backgroundColor: `${color}20`, color }}>{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </Card>
  );
}

function Dashboard({ metrics }: { metrics: Metrics | null }) {
  if (!metrics) return <EmptyState />;
  return (
    <div className="pageGrid animate-in">
      <div className="stats">
        <Stat label="Candidates" value={metrics.totalCandidates.toLocaleString()} icon={<UserRoundSearch />} />
        <Stat label="Top Score" value={metrics.topScore.toFixed(3)} icon={<Sparkles />} color="#f472b6" />
        <Stat label="Avg Score" value={metrics.averageScore.toFixed(3)} icon={<Target />} color="#34d399" />
        <Stat label="Runtime" value={metrics.pipelineRuntime} icon={<Clock />} color="#a78bfa" />
      </div>
      <Card className="chartCard wide">
        <h2>Score Distribution</h2>
        <ResponsiveContainer height={280}>
          <AreaChart data={metrics.scoreDistribution}>
            <defs>
              <linearGradient id="scoreFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7dd3fc" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#7dd3fc" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#243247" vertical={false} />
            <XAxis dataKey="score" stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={12} />
            <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: "8px" }} />
            <Area type="monotone" dataKey="count" stroke="#7dd3fc" strokeWidth={2} fill="url(#scoreFill)" />
          </AreaChart>
        </ResponsiveContainer>
      </Card>
      <Card className="chartCard">
        <h2>Ranking Logic</h2>
        <div className="pipeline-steps">
          {metrics.explainability.map((item, i) => (
             <div key={item.name} className="pipeline-step">
                <div className="step-num">{i+1}</div>
                <div className="step-info">
                   <strong>{item.name}</strong>
                   <div className="meter"><i style={{ width: `${item.weight * 100}%` }} /></div>
                </div>
                <span>{(item.weight * 100).toFixed(0)}%</span>
             </div>
          ))}
        </div>
      </Card>
      <Card className="chartCard">
        <h2>System Status</h2>
        <div className="system-status">
           <div className="log-line"><span className="tag ok">OK</span> Dataset Loaded: {metrics.totalCandidates} records</div>
           <div className="log-line"><span className="tag ok">OK</span> Model: all-MiniLM-L6-v2</div>
           <div className="log-line"><span className="tag info">INFO</span> CPU Batching Enabled</div>
           <div className="log-line"><span className="tag info">INFO</span> Parquet Cache Active</div>
        </div>
      </Card>
    </div>
  );
}

function Leaderboard({ rows, onSelect }: { rows: TopRow[]; onSelect: (id: string) => void }) {
  const [search, setSearch] = useState("");
  const visible = useMemo(() => 
    rows.filter(r => `${r.candidate_id} ${r.reasoning}`.toLowerCase().includes(search.toLowerCase())),
    [rows, search]
  );
  return (
    <Card className="tableCard animate-in">
      <div className="toolbar">
        <div className="searchBox">
          <Search size={18} />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search top 100 candidates..." />
        </div>
        <div className="submission-actions">
           <button className="btn-secondary"><Download size={16} /> Export CSV</button>
        </div>
      </div>
      <div className="tableWrap">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Candidate ID</th>
              <th>Score</th>
              <th>Reasoning Snippet</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {visible.map(row => (
              <tr key={row.candidate_id} onClick={() => onSelect(row.candidate_id)}>
                <td className="rank-cell">#{row.rank}</td>
                <td className="id-cell">{row.candidate_id}</td>
                <td>
                   <div className="score-pill">{(row.score * 100).toFixed(1)}</div>
                </td>
                <td className="reason-cell">{row.reasoning}</td>
                <td><ChevronRight size={16} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

function CandidateExplorer({ detail }: { detail: CandidateDetail | null }) {
  if (!detail) return <EmptyState message="Select a candidate from the leaderboard to view details." />;
  const profile = detail.candidate.profile ?? {};
  const radar = [
    { name: "Semantic", value: detail.explanation?.semantic_score || 0 },
    { name: "Retrieval", value: detail.explanation?.retrieval_score || 0 },
    { name: "Production", value: detail.explanation?.production_score || 0 },
    { name: "Career", value: detail.explanation?.career_score || 0 },
    { name: "Behavior", value: detail.explanation?.behavior_score || 0 },
    { name: "Trust", value: detail.explanation?.trust_score || 0 }
  ];

  return (
    <div className="explorer animate-in">
      <div className="explorer-main">
        <Card className="profile-header">
           <div className="badge">Rank #{detail.ranking.rank}</div>
           <h1>{profile.current_title || "Product Engineer"}</h1>
           <p className="headline">{profile.headline}</p>
           <div className="profile-meta">
              <span>{profile.location}, {profile.country}</span>
              <span>{profile.years_of_experience} Yrs Exp</span>
              <span>{profile.current_industry}</span>
           </div>
        </Card>
        
        <div className="info-grid">
           <Card>
              <h2>Decision Reasoning</h2>
              <p className="reason-text">{detail.ranking.reasoning}</p>
              <div className="tags">
                 {detail.explanation?.is_product_company ? <span className="tag-boost">Product Company</span> : null}
                 {detail.explanation?.is_open_source ? <span className="tag-boost">Open Source</span> : null}
                 {detail.explanation?.at_google ? <span className="tag-boost">MAANG Experience</span> : null}
              </div>
           </Card>
           
           <Card>
              <h2>Match Radar</h2>
              <ResponsiveContainer width="100%" height={240}>
                 <RadarChart data={radar}>
                    <PolarGrid stroke="#243247" />
                    <PolarAngleAxis dataKey="name" stroke="#94a3b8" fontSize={10} />
                    <Radar dataKey="value" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.6} />
                 </RadarChart>
              </ResponsiveContainer>
           </Card>
        </div>
        
        <Card>
           <h2>Capability Signals</h2>
           <div className="signal-bars">
              {[
                { label: "Production Evidence", val: detail.explanation?.production_evidence },
                { label: "Ownership Signal", val: detail.explanation?.ownership },
                { label: "Retrieval Tech", val: detail.explanation?.retrieval_evidence },
                { label: "Deployment Skills", val: detail.explanation?.deployment_evidence },
                { label: "Ranking Logic", val: detail.explanation?.ranking_evidence }
              ].map(s => (
                <div key={s.label} className="signal-row">
                   <span>{s.label}</span>
                   <div className="meter"><i style={{ width: `${(s.val || 0)*100}%` }} /></div>
                </div>
              ))}
           </div>
        </Card>
      </div>
      
      <div className="explorer-side">
         <Card className="scoring-breakdown">
            <h2>Score Breakdown</h2>
            <div className="score-total">
               <div className="big-score">{(detail.ranking.score * 100).toFixed(1)}</div>
               <span>Final Weighted Score</span>
            </div>
            <div className="breakdown-list">
               {radar.map(r => (
                  <div key={r.name} className="breakdown-item">
                     <span>{r.name}</span>
                     <strong>{(r.value * 100).toFixed(0)}</strong>
                  </div>
               ))}
            </div>
         </Card>
         
         <Card className="trust-card">
            <h2>Trust Discovery</h2>
            <div className="trust-stat">
               <ShieldCheck className={detail.explanation?.trust_score > 0.8 ? "text-green" : "text-yellow"} />
               <div>
                  <strong>{(detail.explanation?.trust_score * 100).toFixed(0)}% Trust</strong>
                  <small>Profile Verification Score</small>
               </div>
            </div>
         </Card>
      </div>
    </div>
  );
}

function Explainability({ metrics }: { metrics: Metrics | null }) {
  if (!metrics) return <EmptyState />;
  return (
    <div className="pageGrid animate-in">
      <Card className="chartCard wide">
        <h2>Factor Contributions (Global Mean)</h2>
        <ResponsiveContainer height={340}>
          <BarChart data={metrics.explainability}>
            <CartesianGrid stroke="#243247" vertical={false} />
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #1e293b" }} />
            <Bar dataKey="contribution" radius={[4, 4, 0, 0]}>
               {metrics.explainability.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={['#38bdf8', '#818cf8', '#fb7185', '#fbbf24', '#34d399', '#a78bfa', '#f472b6'][index % 7]} />
               ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Card>
      <div className="weightGrid">
        {metrics.explainability.map((item) => (
          <Card className="weightCard" key={item.name}>
            <span>{item.name} Factor</span>
            <strong>{(item.weight * 100).toFixed(0)}%</strong>
            <p>Weight allocated in final formula</p>
          </Card>
        ))}
      </div>
    </div>
  );
}

function Submission() {
  const [logs, setLogs] = useState<string[]>([
    "[SYSTEM] Monitoring active",
    "[SYSTEM] Ready for ranking run..."
  ]);

  const [running, setRunning] = useState(false);

  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({
      behavior: "smooth"
    });
  }, [logs]);

  async function startRun() {
    setRunning(true);

    setLogs(prev => [
      ...prev,
      "[RUN] Initializing Stage 1: Retrieval...",
      "[RUN] Loading pre-trained embeddings..."
    ]);

    try {
      const res = await getJson<any>(
        "/run",
        {
          method: "POST"
        }
      );

      setLogs(prev => [
        ...prev,
        "[RUN] Pipeline complete",
        `[RES] ${res.output}`
      ]);
    } catch (e) {
      setLogs(prev => [
        ...prev,
        `[ERR] ${String(e)}`
      ]);
    }

    setRunning(false);
  }

  async function validateCSV() {
    setLogs(prev => [
      ...prev,
      "[VALIDATE] Running validator..."
    ]);

    try {
      const res = await getJson<any>(
        "/validate",
        {
          method: "POST"
        }
      );

      setLogs(prev => [
        ...prev,
        res.valid
          ? "[VALID] submission.csv accepted"
          : `[INVALID] ${res.output}`
      ]);
    } catch (e) {
      setLogs(prev => [
        ...prev,
        `[ERR] ${String(e)}`
      ]);
    }
  }

  return (
    <div className="submission-page animate-in">

      <Card className="run-controls">

        <div className="header-with-icon">

          <ShieldCheck
            size={32}
            color="#34d399"
          />

          <div>
            <h1>Validation & Export</h1>

            <p>
              Finalize candidate ranking submission
            </p>
          </div>

        </div>

        <div className="action-btns">

          <button
            className={`btn-primary ${
              running ? "loading" : ""
            }`}
            onClick={startRun}
            disabled={running}
          >

            {
              running
              ? "Processing..."
              : <>
                  <Play size={18}/>
                  Execute Pipeline
                </>
            }

          </button>

          <button
            className="btn-secondary"
            onClick={validateCSV}
          >
            <ShieldCheck size={18}/>
            Validate CSV
          </button>

          <a
            href={`${API}/download`}
            className="btn-secondary"
          >
            <Download size={18}/>
            Download submission.csv
          </a>

        </div>

      </Card>

      <Card className="terminal-card">

        <div className="terminal-header">

          <Terminal size={14}/>

          <span>
            Ranking Engine Logs
          </span>

        </div>

        <div className="terminal-body">

          {
            logs.map((log, i) => (
              <div
                key={i}
                className="log-line"
              >
                {log}
              </div>
            ))
          }

          <div ref={logEndRef}/>

        </div>

      </Card>

    </div>
  );
}

function Settings() {
   return (
      <Card className="settings-page animate-in">
         <h2>Challenge Configuration</h2>
         <div className="settings-list">
            <div className="setting-item">
               <div>
                  <strong>Model Name</strong>
                  <p>HuggingFace Sentence Transformer</p>
               </div>
               <code>all-MiniLM-L6-v2</code>
            </div>
            <div className="setting-item">
               <div>
                  <strong>Ranking Strategy</strong>
                  <p>Multi-stage hybrid retrieval</p>
               </div>
               <code>TFIDF + Semantic</code>
            </div>
            <div className="setting-item">
               <div>
                  <strong>Offline Mode</strong>
                  <p>Inference without cloud APIs</p>
               </div>
               <span className="tag ok">ENABLED</span>
            </div>
         </div>
      </Card>
   )
}

function EmptyState({ message = "Launch the ranker to populate this dashboard." }: { message?: string }) {
  return <div className="empty-state"><Sparkles /> <p>{message}</p></div>;
}

function App() {
  const [page, setPage] = useState<Page>("Dashboard");
  const [rows, setRows] = useState<TopRow[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [detail, setDetail] = useState<CandidateDetail | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getJson<TopRow[]>("/top100"),
      getJson<Metrics>("/metrics")
    ]).then(([r, m]) => {
      setRows(r);
      setMetrics(m);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  async function selectCandidate(id: string) {
    setPage("Explorer");
    const data = await getJson<CandidateDetail>(`/candidate/${id}`);
    setDetail(data);
  }

  if (loading) return <div className="loader-screen">Initializing India Runs PoC...</div>;

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo"><Activity /></div>
          <span>RankForge</span>
        </div>
        <nav className="nav-menu">
          {pages.map((item) => (
            <button key={item.name} className={page === item.name ? "active" : ""} onClick={() => setPage(item.name)}>
              {item.icon} {item.name}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="version">PoC v2026.1.0</div>
        </div>
      </aside>
      
      <main className="main-content">
        <header className="top-header">
          <div className="breadcrumbs">
              <span>Main System</span> / <span>{page}</span>
          </div>
          <div className="header-actions">
              <div className="status-indicator">
                <div className="pulse"></div>
                Pipeline Ready
              </div>
          </div>
        </header>
        
        <div className="content-area">
          {page === "Dashboard" && <Dashboard metrics={metrics} />}
          {page === "Leaderboard" && <Leaderboard rows={rows} onSelect={selectCandidate} />}
          {page === "Explorer" && <CandidateExplorer detail={detail} />}
          {page === "Explainability" && <Explainability metrics={metrics} />}
          {page === "Submission" && <Submission />}
          {page === "Settings" && <Settings />}
        </div>
      </main>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
