"use client";

import { useState } from "react";

/* ─── Google Fonts injected via style tag ─────────────────────────────────── */
const FontStyle = () => (
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&display=swap');

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body, html { font-family: 'DM Sans', sans-serif; background: #ffffff; }

    .font-display { font-family: 'Playfair Display', serif; }

    /* Subtle dot grid background */
    .dot-bg {
      background-color: #ffffff;
      background-image:
        radial-gradient(circle, #e2e8f0 1px, transparent 1px),
        radial-gradient(at 15% 10%, rgba(99,102,241,0.05) 0, transparent 55%),
        radial-gradient(at 85% 8%,  rgba(139,92,246,0.04) 0, transparent 50%),
        radial-gradient(at 5%  85%, rgba(59,130,246,0.04) 0, transparent 50%),
        radial-gradient(at 92% 88%, rgba(236,72,153,0.03) 0, transparent 45%);
      background-size: 28px 28px, 100% 100%, 100% 100%, 100% 100%, 100% 100%;
    }

    /* Focus ring for inputs */
    .k-input { transition: border-color 0.18s, box-shadow 0.18s; }
    .k-input:focus {
      outline: none;
      border-color: #6366f1 !important;
      box-shadow: 0 0 0 3px rgba(99,102,241,0.14);
    }

    /* Card hover */
    .career-card { transition: transform 0.22s ease, box-shadow 0.22s ease; }
    .career-card:hover { transform: translateY(-5px); box-shadow: 0 24px 56px rgba(0,0,0,0.09) !important; }

    /* Stream pill */
    .stream-pill { transition: all 0.18s ease; cursor: pointer; }
    .stream-pill:hover { transform: translateY(-1px); }

    /* Spinner */
    @keyframes kspin { to { transform: rotate(360deg); } }
    .kspin { display: inline-block; animation: kspin 0.75s linear infinite; }

    /* Fade-up entrance */
    @keyframes kfadeup { from { opacity:0; transform:translateY(18px); } to { opacity:1; transform:translateY(0); } }
    .fade-up  { animation: kfadeup 0.4s ease both; }
    .delay-1  { animation-delay: 0.07s; }
    .delay-2  { animation-delay: 0.14s; }
    .delay-3  { animation-delay: 0.21s; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; }
    ::-webkit-scrollbar-track { background: #f8fafc; }
    ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 99px; }

    select { -webkit-appearance: none; appearance: none; }
    button { font-family: inherit; }
    input, select { font-family: inherit; }
  `}</style>
);

/* ─── Stream config ──────────────────────────────────────────────────────── */
const STREAMS = [
  { key: "Science",    label: "Science & Technology",       icon: "⚗️",  accent: "#0ea5e9", lightBg: "#f0f9ff", border: "#bae6fd", textColor: "#0369a1" },
  { key: "Commerce",   label: "Commerce & Finance",         icon: "📈",  accent: "#10b981", lightBg: "#ecfdf5", border: "#6ee7b7", textColor: "#047857" },
  { key: "Arts",       label: "Arts & Humanities",          icon: "🎨",  accent: "#8b5cf6", lightBg: "#f5f3ff", border: "#c4b5fd", textColor: "#6d28d9" },
  { key: "Vocational", label: "Vocational & Technical",     icon: "🔧",  accent: "#f59e0b", lightBg: "#fffbeb", border: "#fcd34d", textColor: "#b45309" },
  { key: "Government", label: "Government Jobs",            icon: "🏛️", accent: "#ef4444", lightBg: "#fff1f2", border: "#fecdd3", textColor: "#b91c1c" },
  { key: "Other",      label: "Creative & Emerging Fields", icon: "💡",  accent: "#6366f1", lightBg: "#eef2ff", border: "#c7d2fe", textColor: "#4338ca" },
];

type Career = { course: string; duration: string; exam: string; course_fee: string; jobs: string; salary: string; };
const getSM = (key: string) => STREAMS.find(s => s.key.toLowerCase() === key.toLowerCase()) ?? STREAMS[0];

/* ═══════════════════════════════════════════════════════════════════════════
   ROOT PAGE
═══════════════════════════════════════════════════════════════════════════ */
export default function Home() {
  const [user, setUser]               = useState<any>(null);
  const [isReg, setIsReg]             = useState(false);
  const [loginForm, setLoginForm]     = useState({ email: "", password: "" });
  const [regForm, setRegForm]         = useState({ name: "", email: "", password: "" });
  const [student, setStudent]         = useState({ name: "", stream: "Science", mobile: "", state: "" });
  const [result, setResult]           = useState<Career[]>([]);
  const [search, setSearch]           = useState("");
  const [loading, setLoading]         = useState(false);
  const [saved, setSaved]             = useState(false);
  const [activeStream, setActiveStream] = useState("");

  /* Auth */
  const handleLogin = async () => {
    try {
      const r = await fetch("http://localhost:8000/login", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(loginForm) });
      const d = await r.json();
      if (d.status === "success") setUser(d.user); else alert("Invalid Email or Password");
    } catch { alert("Backend not connected"); }
  };

  const handleRegister = async () => {
    try {
      const r = await fetch("http://localhost:8000/register", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(regForm) });
      const d = await r.json();
      alert(d.message);
      if (d.status === "success") setIsReg(false);
    } catch { alert("Register Error"); }
  };

  /* Student */
  const saveStudent = async () => {
    try {
      await fetch("http://localhost:8000/student", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({ ...student, user_id: user.id }) });
      setSaved(true); setTimeout(() => setSaved(false), 3000);
    } catch { alert("Error Saving Student"); }
  };

  /* Roadmap */
  const getRoadmap = async () => {
    setLoading(true); setResult([]); setSearch("");
    try {
      const r = await fetch("http://localhost:8000/roadmap", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({ stream: student.stream.toLowerCase() }) });
      const d = await r.json();
      setResult(d.data ?? []); setActiveStream(student.stream);
    } catch { alert("Error Generating Career Roadmap"); }
    setLoading(false);
  };

  const filtered = result.filter(i =>
    i.course.toLowerCase().includes(search.toLowerCase()) ||
    i.jobs.toLowerCase().includes(search.toLowerCase())
  );

  /* ══════════════════════════════════════════════════════════════════════
     AUTH SCREEN
  ══════════════════════════════════════════════════════════════════════ */
  if (!user) return (
    <>
      <FontStyle />
      <div className="dot-bg" style={{ minHeight:"100vh", display:"flex" }}>

        {/* ── LEFT PANEL ── */}
        <div style={{
          width: "44%", minHeight: "100vh",
          background: "linear-gradient(155deg, #1e1b4b 0%, #312e81 42%, #4338ca 100%)",
          display: "flex", flexDirection: "column", justifyContent: "space-between",
          padding: "52px 56px", position: "relative", overflow: "hidden"
        }}>
          {/* decorative blobs */}
          <div style={{ position:"absolute", top:-90, right:-90, width:320, height:320, borderRadius:"50%", background:"rgba(255,255,255,0.03)" }} />
          <div style={{ position:"absolute", bottom:-60, left:-60, width:280, height:280, borderRadius:"50%", background:"rgba(255,255,255,0.03)" }} />
          <div style={{ position:"absolute", top:"38%", left:"25%", width:200, height:200, borderRadius:"50%", background:"rgba(99,102,241,0.12)" }} />
          {/* dot pattern */}
          <div style={{ position:"absolute", inset:0, backgroundImage:"radial-gradient(circle, rgba(255,255,255,0.06) 1px, transparent 1px)", backgroundSize:"26px 26px" }} />

          <div style={{ position:"relative" }}>
            <div style={{ width:52, height:52, borderRadius:14, background:"rgba(255,255,255,0.1)", border:"1px solid rgba(255,255,255,0.15)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:26, marginBottom:24 }}>🎓</div>
            <p style={{ color:"rgba(199,210,254,0.65)", fontSize:11, fontWeight:800, letterSpacing:"0.14em", textTransform:"uppercase", marginBottom:10 }}>AI Career Guidance</p>
            <h1 className="font-display" style={{ color:"#fff", fontSize:42, lineHeight:1.18, marginBottom:20 }}>
              Shape Your<br/>Career Future
            </h1>
            <p style={{ color:"rgba(199,210,254,0.65)", fontSize:15, lineHeight:1.75, maxWidth:340 }}>
              Explore hundreds of career paths across Science, Commerce, Arts, Vocational, Government &amp; Creative fields — all verified and up-to-date.
            </p>
          </div>

          <div style={{ position:"relative" }}>
            <p style={{ color:"rgba(199,210,254,0.45)", fontSize:10, fontWeight:800, letterSpacing:"0.12em", textTransform:"uppercase", marginBottom:14 }}>6 Career Streams</p>
            <div style={{ display:"flex", flexWrap:"wrap", gap:8 }}>
              {STREAMS.map(s => (
                <span key={s.key} style={{ background:"rgba(255,255,255,0.08)", border:"1px solid rgba(255,255,255,0.12)", color:"rgba(224,231,255,0.82)", padding:"7px 14px", borderRadius:99, fontSize:12, fontWeight:600, display:"flex", alignItems:"center", gap:6 }}>
                  {s.icon} {s.key}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* ── RIGHT PANEL (form) ── */}
        <div style={{ flex:1, display:"flex", alignItems:"center", justifyContent:"center", padding:"40px 32px" }}>
          <div className="fade-up" style={{ width:"100%", maxWidth:420 }}>

            <h1 className="font-display" style={{ fontSize:34, fontWeight:900, color:"#111827", marginBottom:6 }}>
              {isReg ? "Create account" : "Welcome back"}
            </h1>
            <p style={{ color:"#6b7280", fontSize:14, fontWeight:400, marginBottom:36, lineHeight:1.6 }}>
              {isReg ? "Join Knowletive and start exploring your ideal career." : "Sign in to continue to your career dashboard."}
            </p>

            <div style={{ display:"flex", flexDirection:"column", gap:18 }}>
              {isReg && <KField label="Full Name" placeholder="Your full name" onChange={v => setRegForm({ ...regForm, name: v })} />}
              <KField label="Email Address" placeholder="you@email.com" type="email"
                onChange={v => isReg ? setRegForm({ ...regForm, email: v }) : setLoginForm({ ...loginForm, email: v })} />
              <KField label="Password" placeholder="••••••••" type="password"
                onChange={v => isReg ? setRegForm({ ...regForm, password: v }) : setLoginForm({ ...loginForm, password: v })} />
            </div>

            <button
              onClick={isReg ? handleRegister : handleLogin}
              style={{ width:"100%", marginTop:28, padding:"15px 0", borderRadius:14, background:"linear-gradient(135deg,#4f46e5,#7c3aed)", color:"#fff", fontWeight:700, fontSize:15, border:"none", cursor:"pointer", boxShadow:"0 10px 28px rgba(79,70,229,0.3)", letterSpacing:"0.01em" }}
            >
              {isReg ? "Create Account →" : "Sign In →"}
            </button>

            <div style={{ textAlign:"center", marginTop:24 }}>
              <span style={{ fontSize:13, color:"#9ca3af" }}>
                {isReg ? "Already have an account? " : "New here? "}
              </span>
              <span
                onClick={() => setIsReg(!isReg)}
                style={{ fontSize:13, color:"#4f46e5", fontWeight:700, cursor:"pointer" }}
              >
                {isReg ? "Sign in" : "Create a free account"}
              </span>
            </div>
          </div>
        </div>
      </div>
    </>
  );

  /* ══════════════════════════════════════════════════════════════════════
     DASHBOARD
  ══════════════════════════════════════════════════════════════════════ */
  const sm = getSM(activeStream);

  return (
    <>
      <FontStyle />
      <div className="dot-bg" style={{ minHeight:"100vh" }}>

        {/* ── NAVBAR ── */}
        <nav style={{
          position:"sticky", top:0, zIndex:50,
          background:"rgba(255,255,255,0.9)", backdropFilter:"blur(18px)",
          borderBottom:"1px solid #f1f5f9",
          boxShadow:"0 1px 24px rgba(0,0,0,0.04)"
        }}>
          <div style={{ maxWidth:1300, margin:"0 auto", padding:"0 28px", height:66, display:"flex", alignItems:"center", justifyContent:"space-between" }}>
            <div style={{ display:"flex", alignItems:"center", gap:12 }}>
              <div style={{ width:42, height:42, borderRadius:12, background:"linear-gradient(135deg,#4f46e5,#7c3aed)", display:"flex", alignItems:"center", justifyContent:"center", fontSize:21 }}>🎓</div>
              <span className="font-display" style={{ fontSize:21, fontWeight:900, color:"#111827" }}>Knowletive</span>
              <span style={{ background:"#eef2ff", color:"#4f46e5", fontSize:9, fontWeight:800, padding:"3px 10px", borderRadius:99, letterSpacing:"0.08em", textTransform:"uppercase" }}>AI Powered</span>
            </div>
            <div style={{ display:"flex", alignItems:"center", gap:16 }}>
              <div style={{ textAlign:"right" }}>
                <p style={{ fontSize:10, color:"#9ca3af", fontWeight:700, textTransform:"uppercase", letterSpacing:"0.08em" }}>Logged in as</p>
                <p style={{ fontSize:14, fontWeight:700, color:"#111827" }}>{user.name}</p>
              </div>
              <button
                onClick={() => { setUser(null); setResult([]); }}
                style={{ padding:"8px 18px", borderRadius:10, background:"#fff1f2", border:"1px solid #fecdd3", color:"#dc2626", fontSize:13, fontWeight:700, cursor:"pointer" }}
              >
                Logout
              </button>
            </div>
          </div>
        </nav>

        {/* ── MAIN ── */}
        <main style={{ maxWidth:1300, margin:"0 auto", padding:"40px 28px 64px", display:"flex", flexDirection:"column", gap:32 }}>

          {/* HERO BANNER */}
          <div className="fade-up" style={{
            borderRadius:28, padding:"48px 56px", position:"relative", overflow:"hidden",
            background:"linear-gradient(140deg, #1e1b4b 0%, #312e81 42%, #4338ca 100%)",
            boxShadow:"0 20px 60px rgba(67,56,202,0.22)"
          }}>
            <div style={{ position:"absolute", inset:0, backgroundImage:"radial-gradient(circle, rgba(255,255,255,0.05) 1px, transparent 1px)", backgroundSize:"24px 24px" }} />
            <div style={{ position:"absolute", top:-70, right:-70, width:300, height:300, borderRadius:"50%", background:"rgba(255,255,255,0.03)" }} />
            <div style={{ position:"absolute", bottom:-50, right:160, width:220, height:220, borderRadius:"50%", background:"rgba(99,102,241,0.18)" }} />
            <div style={{ position:"relative" }}>
              <p style={{ color:"rgba(199,210,254,0.7)", fontSize:11, fontWeight:800, letterSpacing:"0.14em", textTransform:"uppercase", marginBottom:12 }}>🎯 Career Guidance System</p>
              <h1 className="font-display" style={{ color:"#fff", fontSize:40, lineHeight:1.2, marginBottom:14 }}>
                Discover Your Perfect<br/>Career Path
              </h1>
              <p style={{ color:"rgba(199,210,254,0.68)", fontSize:15, maxWidth:580, lineHeight:1.75 }}>
                Enter student details, select a stream, and instantly explore hundreds of verified career options with entrance exams, fees, and salary insights.
              </p>
              <div style={{ display:"flex", flexWrap:"wrap", gap:10, marginTop:28 }}>
                {STREAMS.map(s => (
                  <span key={s.key} style={{ background:"rgba(255,255,255,0.09)", border:"1px solid rgba(255,255,255,0.14)", color:"rgba(224,231,255,0.88)", padding:"6px 14px", borderRadius:99, fontSize:12, fontWeight:600 }}>
                    {s.icon} {s.key}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* FORM CARD */}
          <div className="fade-up delay-1" style={{ background:"#ffffff", borderRadius:24, border:"1px solid #f0f4f8", boxShadow:"0 4px 36px rgba(0,0,0,0.055)", overflow:"hidden" }}>

            <div style={{ padding:"22px 36px", borderBottom:"1px solid #f8fafc", display:"flex", alignItems:"center", gap:14 }}>
              <div style={{ width:46, height:46, borderRadius:13, background:"#eef2ff", border:"1px solid #c7d2fe", display:"flex", alignItems:"center", justifyContent:"center", fontSize:22 }}>📋</div>
              <div>
                <h2 className="font-display" style={{ fontSize:20, fontWeight:700, color:"#111827" }}>Student Details</h2>
                <p style={{ fontSize:13, color:"#9ca3af" }}>Fill in to generate a personalised career roadmap</p>
              </div>
            </div>

            <div style={{ padding:"32px 36px" }}>
              {/* 2-col grid */}
              <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fit, minmax(210px, 1fr))", gap:20, marginBottom:28 }}>
                <KField label="Student Name *"  placeholder="Full name"        onChange={v => setStudent({ ...student, name: v })} />
                <KField label="Mobile Number *" placeholder="+91 00000 00000"  onChange={v => setStudent({ ...student, mobile: v })} />
                <KField label="State"           placeholder="e.g. Maharashtra" onChange={v => setStudent({ ...student, state: v })} />

                {/* Stream select */}
                <div>
                  <label style={{ display:"block", fontSize:11, fontWeight:700, color:"#6b7280", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:8 }}>Stream / Field</label>
                  <div style={{ position:"relative" }}>
                    <select
                      value={student.stream}
                      onChange={e => setStudent({ ...student, stream: e.target.value })}
                      className="k-input"
                      style={{ width:"100%", padding:"12px 40px 12px 16px", borderRadius:12, border:"1.5px solid #e5e7eb", background:"#fafafa", fontSize:14, fontWeight:600, color:"#111827", cursor:"pointer" }}
                    >
                      {STREAMS.map(s => <option key={s.key} value={s.key}>{s.icon} {s.label}</option>)}
                    </select>
                    <span style={{ position:"absolute", right:14, top:"50%", transform:"translateY(-50%)", pointerEvents:"none", color:"#9ca3af", fontSize:12 }}>▼</span>
                  </div>
                </div>
              </div>

              {/* Quick-select pills */}
              <div style={{ marginBottom:28 }}>
                <p style={{ fontSize:11, fontWeight:700, color:"#9ca3af", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:12 }}>Quick Select Stream</p>
                <div style={{ display:"flex", flexWrap:"wrap", gap:10 }}>
                  {STREAMS.map(s => {
                    const active = student.stream === s.key;
                    return (
                      <button
                        key={s.key}
                        className="stream-pill"
                        onClick={() => setStudent({ ...student, stream: s.key })}
                        style={{
                          display:"flex", alignItems:"center", gap:7,
                          padding:"9px 18px", borderRadius:12, fontSize:13, fontWeight:600, border:"1.5px solid",
                          ...(active
                            ? { background:s.lightBg, borderColor:s.border, color:s.textColor, boxShadow:`0 4px 16px ${s.accent}20` }
                            : { background:"#fafafa", borderColor:"#e5e7eb", color:"#6b7280" })
                        }}
                      >
                        <span style={{ fontSize:16 }}>{s.icon}</span>
                        {s.key}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Action buttons */}
              <div style={{ display:"flex", flexWrap:"wrap", gap:12 }}>
                <button
                  onClick={saveStudent}
                  style={{
                    display:"flex", alignItems:"center", gap:8,
                    padding:"12px 26px", borderRadius:12, fontSize:14, fontWeight:700, cursor:"pointer", border:"1.5px solid",
                    ...(saved
                      ? { background:"#ecfdf5", borderColor:"#6ee7b7", color:"#059669" }
                      : { background:"#f0fdf4", borderColor:"#bbf7d0", color:"#15803d" })
                  }}
                >
                  {saved ? "✅ Saved!" : "💾 Save Student"}
                </button>

                <button
                  onClick={getRoadmap}
                  disabled={loading}
                  style={{
                    display:"flex", alignItems:"center", gap:8,
                    padding:"12px 30px", borderRadius:12, fontSize:14, fontWeight:700, cursor:"pointer",
                    background:"linear-gradient(135deg,#4f46e5,#7c3aed)",
                    color:"#fff", border:"none",
                    boxShadow:"0 8px 26px rgba(79,70,229,0.28)",
                    opacity: loading ? 0.75 : 1
                  }}
                >
                  {loading
                    ? <><span className="kspin">⟳</span>&nbsp; Generating Roadmap...</>
                    : <><span>🚀</span> Generate Career Roadmap</>}
                </button>
              </div>
            </div>
          </div>

          {/* RESULTS */}
          {result.length > 0 && (
            <div className="fade-up delay-2">
              <div style={{ display:"flex", flexWrap:"wrap", alignItems:"center", justifyContent:"space-between", gap:16, marginBottom:24 }}>
                <div style={{ display:"flex", alignItems:"center", gap:16 }}>
                  <div style={{ width:58, height:58, borderRadius:16, background:sm.lightBg, border:`1.5px solid ${sm.border}`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:28 }}>
                    {sm.icon}
                  </div>
                  <div>
                    <h2 className="font-display" style={{ fontSize:26, fontWeight:800, color:"#111827" }}>{sm.label}</h2>
                    <p style={{ fontSize:13, color:"#6b7280", fontWeight:500 }}>
                      <span style={{ color:sm.textColor, fontWeight:800 }}>{result.length}</span> career options available
                    </p>
                  </div>
                </div>

                <div style={{ position:"relative" }}>
                  <span style={{ position:"absolute", left:14, top:"50%", transform:"translateY(-50%)", fontSize:15, color:"#9ca3af" }}>🔍</span>
                  <input
                    className="k-input"
                    style={{ paddingLeft:42, paddingRight:18, paddingTop:12, paddingBottom:12, borderRadius:12, border:"1.5px solid #e5e7eb", background:"#fff", fontSize:14, fontWeight:500, color:"#111827", width:290, boxShadow:"0 2px 8px rgba(0,0,0,0.04)" }}
                    placeholder="Search course or job role…"
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                  />
                </div>
              </div>

              {search && (
                <p style={{ fontSize:13, color:"#6b7280", marginBottom:20, fontWeight:500 }}>
                  Showing <span style={{ color:sm.textColor, fontWeight:800 }}>{filtered.length}</span> results for "<strong>{search}</strong>"
                </p>
              )}

              <div style={{ display:"grid", gridTemplateColumns:"repeat(auto-fill, minmax(320px, 1fr))", gap:20 }}>
                {filtered.map((item, idx) => (
                  <CareerCard key={idx} item={item} stream={activeStream} />
                ))}
              </div>

              {filtered.length === 0 && (
                <div style={{ textAlign:"center", padding:"80px 0" }}>
                  <div style={{ fontSize:52, marginBottom:14 }}>🔍</div>
                  <p style={{ fontSize:18, fontWeight:700, color:"#374151" }}>No results found</p>
                  <p style={{ fontSize:14, color:"#9ca3af", marginTop:6 }}>Try a different course or job keyword</p>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </>
  );
}

/* ══════════════════════════════════════════════════════════════════════════════
   CAREER CARD
══════════════════════════════════════════════════════════════════════════════ */
function CareerCard({ item, stream }: { item: Career; stream: string }) {
  const [exp, setExp] = useState(false);
  const sm = getSM(stream);
  const isGov = stream.toLowerCase() === "government";

  const rows = [
    { icon:"⏱️", label: isGov ? "Training Period"    : "Duration",      value: item.duration   },
    { icon:"📝", label: isGov ? "Exam / Recruitment" : "Entrance Exam", value: item.exam       },
    { icon:"💳", label: isGov ? "Exam Fee"           : "Course Fee",    value: item.course_fee },
    { icon:"💼", label: isGov ? "Sector"             : "Job Roles",     value: item.jobs       },
    { icon:"💰", label: isGov ? "Age Limit"          : "Salary",        value: item.salary     },
  ].filter(r => r.value && r.value !== "nan" && r.value !== "NaN" && r.value.trim() !== "");

  const preview = rows.slice(0, 3);
  const extra   = rows.slice(3);

  return (
    <div
      className="career-card"
      style={{ background:"#ffffff", borderRadius:20, border:"1px solid #f0f4f8", boxShadow:"0 2px 18px rgba(0,0,0,0.05)", overflow:"hidden" }}
    >
      <div style={{ height:4, background:`linear-gradient(90deg, ${sm.accent}, ${sm.accent}80)` }} />

      <div style={{ padding:"20px 22px 16px", borderBottom:"1px solid #f8fafc", display:"flex", alignItems:"flex-start", justifyContent:"space-between", gap:12 }}>
        <h3 className="font-display" style={{ fontSize:17, fontWeight:700, color:"#111827", lineHeight:1.3, flex:1 }}>{item.course}</h3>
        <div style={{ width:38, height:38, borderRadius:10, background:sm.lightBg, border:`1px solid ${sm.border}`, display:"flex", alignItems:"center", justifyContent:"center", fontSize:18, flexShrink:0 }}>{sm.icon}</div>
      </div>

      <div style={{ padding:"16px 22px", display:"flex", flexDirection:"column", gap:13 }}>
        {preview.map((r, i) => <DRow key={i} {...r} color={sm.textColor} />)}
        {exp && extra.map((r, i) => <DRow key={i} {...r} color={sm.textColor} />)}
      </div>

      {extra.length > 0 && (
        <div style={{ padding:"0 22px 20px" }}>
          <button
            onClick={() => setExp(!exp)}
            style={{ width:"100%", padding:"10px 0", borderRadius:11, background:sm.lightBg, border:`1px solid ${sm.border}`, color:sm.textColor, fontSize:12, fontWeight:700, cursor:"pointer" }}
          >
            {exp ? "▲ Show Less" : `▼ ${extra.length} More Details`}
          </button>
        </div>
      )}
    </div>
  );
}

function DRow({ icon, label, value, color }: { icon:string; label:string; value:string; color:string }) {
  return (
    <div style={{ display:"flex", gap:12, alignItems:"flex-start" }}>
      <span style={{ fontSize:15, flexShrink:0, marginTop:1 }}>{icon}</span>
      <div>
        <p style={{ fontSize:10, fontWeight:800, color:"#9ca3af", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:2 }}>{label}</p>
        <p style={{ fontSize:13, fontWeight:500, color:"#374151", lineHeight:1.55 }}>{value}</p>
      </div>
    </div>
  );
}

/* ── Shared field component ── */
function KField({ label, placeholder, type="text", onChange }: { label:string; placeholder:string; type?:string; onChange:(v:string)=>void }) {
  return (
    <div>
      <label style={{ display:"block", fontSize:11, fontWeight:700, color:"#6b7280", textTransform:"uppercase", letterSpacing:"0.08em", marginBottom:8 }}>{label}</label>
      <input
        type={type}
        placeholder={placeholder}
        className="k-input"
        style={{ width:"100%", padding:"12px 16px", borderRadius:12, border:"1.5px solid #e5e7eb", background:"#fafafa", fontSize:14, fontWeight:500, color:"#111827" }}
        onChange={e => onChange(e.target.value)}
      />
    </div>
  );
}