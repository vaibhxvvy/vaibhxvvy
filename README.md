<!--
  vaibhxvvy — custom dark multipage profile
  tabs: About / Stack / Pipeline / Projects / Stats
  palette: BG #0A0A0F / Surface #11131A / Border #1C1E2A / Primary #7A5CFA / Accent #00D9FF
  if tabs are sanitized, fallback anchor nav below still works
-->

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0A0A0F&height=170&section=header&text=vaibhav%20surthi&fontSize=40&fontColor=7A5CFA&animation=fadeIn&desc=ML%20%E2%80%A2%20Systems%20%E2%80%A2%20Pipelines&descAlignY=74&descAlign=50" alt="vaibhav surthi header"/>
</p>

<p align="center">
  <a href="https://github.com/vaibhxvvy">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=21&duration=2200&pause=1000&color=7A5CFA&center=true&vCenter=true&width=700&height=48&lines=ML%2FData+Science+focused+on+systems+not+just+models;Design+pipelines+that+turn+data+into+decisions;Automation+%26+decision+engines+in+production" alt="typing intro"/>
  </a>
</p>

<p align="center">
  <a href="https://instagram.com/vaibhxvvy"><img src="https://img.shields.io/badge/Instagram-%23E4405F.svg?style=flat-square&logo=Instagram&logoColor=white" alt="instagram"/></a>
  <a href="https://linkedin.com/in/vaibhavsurthi"><img src="https://img.shields.io/badge/LinkedIn-%230077B5.svg?style=flat-square&logo=linkedin&logoColor=white" alt="linkedin"/></a>
  <a href="mailto:vaibhavsurthi08@gmail.com"><img src="https://img.shields.io/badge/Email-D14836?style=flat-square&logo=gmail&logoColor=white" alt="email"/></a>
  <img src="https://komarev.com/ghpvc/?username=vaibhxvvy&style=flat-square&color=7A5CFA&label=views" alt="profile views"/>
</p>

<p align="center">
  <img src="assets/divider.svg" width="100%" alt="divider"/>
</p>

<!-- ===================== TABS (CSS tab trick) ===================== -->
<div align="center">

<style>
  input[name="tabs"]{display:none}
  .tab-label{
    display:inline-block;
    padding:8px 16px;
    margin: 4px 3px;
    border: 1px solid #1C1E2A;
    border-radius: 999px;
    background: #11131A;
    color: #8B8DA3;
    font-family: 'Fira Code', ui-monospace, monospace;
    font-size: 12.5px;
    letter-spacing: 0.4px;
    cursor: pointer;
    transition: all .22s ease;
    user-select: none;
  }
  .tab-label:hover{ border-color:#2A2E45; color:#E8E8EE; transform: translateY(-1px) }
  input#tab-about:checked ~ .labels label[for="tab-about"],
  input#tab-stack:checked ~ .labels label[for="tab-stack"],
  input#tab-pipeline:checked ~ .labels label[for="tab-pipeline"],
  input#tab-projects:checked ~ .labels label[for="tab-projects"],
  input#tab-stats:checked ~ .labels label[for="tab-stats"]{
    background: linear-gradient(135deg,#7A5CFA 0%, #5B8DEF 50%, #00D9FF 100%);
    color:#0A0A0F;
    border-color: transparent;
    font-weight: 800;
    box-shadow: 0 4px 20px rgba(122,92,250,0.35);
  }
  .page{ display:none; text-align:left; animation: fadeUp .42s ease; }
  @keyframes fadeUp{ from{ opacity:0; transform: translateY(8px)} to{ opacity:1; transform:none } }
  #tab-about:checked ~ #page-about,
  #tab-stack:checked ~ #page-stack,
  #tab-pipeline:checked ~ #page-pipeline,
  #tab-projects:checked ~ #page-projects,
  #tab-stats:checked ~ #page-stats{ display:block }

  /* cards */
  .grid2{ display:grid; grid-template-columns:1fr 1fr; gap:12px }
  @media(max-width:640px){ .grid2{grid-template-columns:1fr} }
  .card{
    background:#11131A;
    border:1px solid #1C1E2A;
    border-radius:14px;
    padding:14px 16px;
  }
  .card h4{ margin:0 0 6px 0; color:#E8E8EE; font-size:13px; letter-spacing:.4px }
  .card p{ margin:0; color:#8B8DA3; font-size:12.5px; line-height:1.5 }
  .pill{
    display:inline-block; font-size:11px; padding:3px 8px; border-radius:999px;
    background:#0A0A0F; border:1px solid #23263A; color:#8B8DA3; margin:2px 3px 0 0
  }
  .kicker{ color:#00D9FF; font-family:'Fira Code',monospace; font-size:11px; letter-spacing:1.2px; text-transform:uppercase; margin:0}
  .muted{ color:#8B8DA3 }
</style>

<input type="radio" name="tabs" id="tab-about" checked>
<input type="radio" name="tabs" id="tab-stack">
<input type="radio" name="tabs" id="tab-pipeline">
<input type="radio" name="tabs" id="tab-projects">
<input type="radio" name="tabs" id="tab-stats">

<div class="labels">
  <label class="tab-label" for="tab-about">◉ About</label>
  <label class="tab-label" for="tab-stack">⬡ Stack</label>
  <label class="tab-label" for="tab-pipeline">⇄ Pipeline</label>
  <label class="tab-label" for="tab-projects">⬢ Projects</label>
  <label class="tab-label" for="tab-stats">◈ Stats</label>
</div>

<!-- fallback anchor nav (always works, even if CSS is stripped) -->
<p class="muted" style="font-size:12px; margin:8px 0 0 0">
  <a href="#-about">About</a> · <a href="#-stack">Stack</a> · <a href="#-pipeline">Pipeline</a> · <a href="#-projects">Projects</a> · <a href="#-stats">Stats</a>
  <span style="opacity:.6"> — switch tabs above, or scroll</span>
</p>

<!-- ===================== PAGE: ABOUT ===================== -->
<div id="page-about" class="page">

<h3 id="-about">◉ About — systems, not just models</h3>

> 🧠 ML/Data Science focused on systems, not just models<br/>
> ⚙️ Design pipelines that turn data into decisions<br/>
> 📊 Work with real-world data and production constraints<br/>
> 🤖 Interested in automation and decision engines

<p class="muted" style="font-size:13px; line-height:1.6">
I build the boring parts that make ML actually useful — ingestion, validation, observability, and the decision layer. Models are the middle. Pipelines are the product.
</p>

<div class="grid2" style="margin:12px 0">

<div class="card">
<h4>🎯 What I do</h4>
<p>Ship end-to-end flows: <b style="color:#E8E8EE">Ingest → Validate → Model → Deploy → Monitor</b>. Optimize for latency, cost, and drift — not just accuracy.</p>
</div>

<div class="card">
<h4>🔍 What I'm exploring</h4>
<p>Agentic research workflows, RAG over private knowledge, and decision engines that close the loop without human babysitting.</p>
</div>

</div>

<div class="card" style="margin-bottom:10px">
<p class="kicker">Principles</p>
<p style="margin-top:6px">
<span class="pill">real data &gt; toy datasets</span>
<span class="pill">constraints are features</span>
<span class="pill">ship → measure → iterate</span>
<span class="pill">automate the toil</span>
<span class="pill">observable by default</span>
</p>
</div>

<p align="center" style="margin:10px 0 0 0">
  <a href="https://linkedin.com/in/vaibhavsurthi"><img src="https://img.shields.io/badge/DM_on_LinkedIn-0A0A0F?style=flat-square&logo=linkedin&logoColor=7A5CFA&labelColor=11131A&color=1C1E2A" alt="linkedin dm"/></a>
  <a href="mailto:vaibhavsurthi08@gmail.com"><img src="https://img.shields.io/badge/Say_hello-0A0A0F?style=flat-square&logo=gmail&logoColor=00D9FF&labelColor=11131A&color=1C1E2A" alt="email"/></a>
  <a href="https://instagram.com/vaibhxvvy"><img src="https://img.shields.io/badge/%40vaibhxvvy-0A0A0F?style=flat-square&logo=instagram&logoColor=E4405F&labelColor=11131A&color=1C1E2A" alt="ig"/></a>
</p>

</div>
<!-- ===================== PAGE: STACK ===================== -->
<div id="page-stack" class="page">

<h3 id="-stack">⬡ Stack — the pipeline toolkit</h3>

<p align="center">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=py,pytorch,tensorflow,sklearn,postgres,mongodb,mysql,supabase,git,github,vercel,figma,ts,js&theme=dark" alt="skillicons"/>
  </a>
</p>

<div class="grid2">

<div class="card">
<h4>◼ Languages</h4>
<p>
<img src="https://img.shields.io/badge/Python-0A0A0F?style=flat-square&logo=python&logoColor=7A5CFA&labelColor=11131A" alt="py"/>
<img src="https://img.shields.io/badge/TypeScript-0A0A0F?style=flat-square&logo=typescript&logoColor=00D9FF&labelColor=11131A" alt="ts"/>
<img src="https://img.shields.io/badge/SQL-0A0A0F?style=flat-square&logo=postgresql&logoColor=E8E8EE&labelColor=11131A" alt="sql"/>
</p>
<p class="muted" style="font-size:12px">Python-first. TS for shipping. SQL for truth.</p>
</div>

<div class="card">
<h4>◼ ML / Data</h4>
<p>
<img src="https://img.shields.io/badge/PyTorch-0A0A0F?style=flat-square&logo=pytorch&logoColor=EE4C2C&labelColor=11131A" alt="pt"/>
<img src="https://img.shields.io/badge/TensorFlow-0A0A0F?style=flat-square&logo=tensorflow&logoColor=FF6F00&labelColor=11131A" alt="tf"/>
<img src="https://img.shields.io/badge/scikit--learn-0A0A0F?style=flat-square&logo=scikit-learn&logoColor=F7931E&labelColor=11131A" alt="sk"/>
<img src="https://img.shields.io/badge/MLflow-0A0A0F?style=flat-square&logo=mlflow&logoColor=00D9FF&labelColor=11131A" alt="mlflow"/>
<br/>
<img src="https://img.shields.io/badge/NumPy-0A0A0F?style=flat-square&logo=numpy&logoColor=4DABCF&labelColor=11131A" alt="np"/>
<img src="https://img.shields.io/badge/Pandas-0A0A0F?style=flat-square&logo=pandas&logoColor=150458&labelColor=11131A" alt="pd"/>
<img src="https://img.shields.io/badge/SciPy-0A0A0F?style=flat-square&logo=scipy&logoColor=0C55A5&labelColor=11131A" alt="sp"/>
<img src="https://img.shields.io/badge/Matplotlib-0A0A0F?style=flat-square&logo=plotly&logoColor=E8E8EE&labelColor=11131A" alt="mpl"/>
<img src="https://img.shields.io/badge/Plotly-0A0A0F?style=flat-square&logo=plotly&logoColor=3F4F75&labelColor=11131A" alt="plotly"/>
</p>
</div>

<div class="card">
<h4>◼ Data / Infra</h4>
<p>
<img src="https://img.shields.io/badge/Postgres-0A0A0F?style=flat-square&logo=postgresql&logoColor=336791&labelColor=11131A" alt="pg"/>
<img src="https://img.shields.io/badge/MongoDB-0A0A0F?style=flat-square&logo=mongodb&logoColor=4ea94b&labelColor=11131A" alt="mongo"/>
<img src="https://img.shields.io/badge/MySQL-0A0A0F?style=flat-square&logo=mysql&logoColor=4479A1&labelColor=11131A" alt="mysql"/>
<img src="https://img.shields.io/badge/SQLite-0A0A0F?style=flat-square&logo=sqlite&logoColor=07405e&labelColor=11131A" alt="sqlite"/>
<img src="https://img.shields.io/badge/Supabase-0A0A0F?style=flat-square&logo=supabase&logoColor=3ECF8E&labelColor=11131A" alt="supa"/>
</p>
<p class="muted" style="font-size:12px">Pick the right store for the workload. No dogma.</p>
</div>

<div class="card">
<h4>◼ Ship</h4>
<p>
<img src="https://img.shields.io/badge/Git-0A0A0F?style=flat-square&logo=git&logoColor=F05033&labelColor=11131A" alt="git"/>
<img src="https://img.shields.io/badge/GitHub-0A0A0F?style=flat-square&logo=github&logoColor=E8E8EE&labelColor=11131A" alt="gh"/>
<img src="https://img.shields.io/badge/Vercel-0A0A0F?style=flat-square&logo=vercel&logoColor=E8E8EE&labelColor=11131A" alt="vercel"/>
<img src="https://img.shields.io/badge/Figma-0A0A0F?style=flat-square&logo=figma&logoColor=F24E1E&labelColor=11131A" alt="figma"/>
<img src="https://img.shields.io/badge/Framer-0A0A0F?style=flat-square&logo=framer&logoColor=00D9FF&labelColor=11131A" alt="framer"/>
</p>
<p class="muted" style="font-size:12px">Design to deploy without handoffs.</p>
</div>

</div>

<p align="center" style="margin:14px 0 4px 0">
  <img src="assets/pipeline.svg" width="100%" alt="pipeline diagram"/>
</p>
<p align="center" class="muted" style="font-size:11px; letter-spacing:.5px; text-transform:uppercase">the stack serves the pipeline — not the other way around</p>

</div>
<!-- ===================== PAGE: PIPELINE ===================== -->
<div id="page-pipeline" class="page">

<h3 id="-pipeline">⇄ Pipeline — how I think about building</h3>

<p align="center">
  <img src="assets/pipeline.svg" width="100%" alt="animated pipeline ingest validate model deploy monitor"/>
</p>

<div class="grid2">

<div class="card">
<p class="kicker">01 — Ingest</p>
<h4>Capture raw reality</h4>
<p>APIs, streams, scrapes, dumps. Idempotent, backfillable, schema-aware from day one. If you can't replay it, you don't own it.</p>
</div>

<div class="card">
<p class="kicker">02 — Validate</p>
<h4>Trust is a check</h4>
<p>Contract tests, expectations, anomaly gates. Data that fails validation never poisons the model. Alert noisy, block silently.</p>
</div>

<div class="card">
<p class="kicker">03 — Model</p>
<h4>Models are the middle</h4>
<p>Baseline → improve → retire. Eval on production slices, not leaderboard splits. Version everything: data, code, prompts.</p>
</div>

<div class="card">
<p class="kicker">04 — Deploy</p>
<h4>Ship small, ship often</h4>
<p>Feature flags, canaries, shadow traffic. The best model is the one that's actually serving.</p>
</div>

</div>

<div class="card" style="margin-top:12px; border-color:#2A2E45; background: linear-gradient(135deg, #11131A 0%, #13151F 100%)">
<p class="kicker">05 — Monitor ↺</p>
<h4>Observe → learn → loop</h4>
<p>Drift, latency, cost, business metric — same dashboard. Feedback becomes the next ingest. <span style="color:#7A5CFA">Closed loops beat open experiments.</span></p>
</div>

<p align="center" style="margin-top:12px">
  <img src="assets/divider.svg" width="100%" alt="divider"/>
</p>

<p class="muted" align="center" style="font-size:12.5px">
Built for <b style="color:#E8E8EE">real-world constraints</b> — not notebooks. Latency budgets, dirty data, and stakeholder deadlines are inputs, not excuses.
</p>

</div>
<!-- ===================== PAGE: PROJECTS ===================== -->
<div id="page-projects" class="page">

<h3 id="-projects">⬢ Projects — selected builds</h3>
<p class="muted" style="font-size:13px">Two systems I actually shipped. More on GitHub.</p>

<p align="center">
  <a href="https://github.com/vaibhxvvy/documentation-pro">
    <img src="https://github-readme-stats.vercel.app/api/pin/?username=vaibhxvvy&repo=documentation-pro&theme=transparent&bg_color=0A0A0F&title_color=7A5CFA&text_color=E8E8EE&icon_color=00D9FF&border_color=1C1E2A&border_radius=12&hide_border=false" alt="documentation-pro pin"/>
  </a>
  <a href="https://github.com/vaibhxvvy/fcuk-paywalls">
    <img src="https://github-readme-stats.vercel.app/api/pin/?username=vaibhxvvy&repo=fcuk-paywalls&theme=transparent&bg_color=0A0A0F&title_color=7A5CFA&text_color=E8E8EE&icon_color=00D9FF&border_color=1C1E2A&border_radius=12&hide_border=false" alt="fcuk-paywalls pin"/>
  </a>
</p>

<div class="grid2">

<div class="card">
<p class="kicker">Featured · Shell · ★3</p>
<h4><a href="https://github.com/vaibhxvvy/documentation-pro" style="color:#E8E8EE; text-decoration:none">documentation-pro</a></h4>
<p>Opinionated doc system — generate, lint, and ship handbooks the way code ships. <br/><span class="muted">Systems thinking applied to knowledge.</span></p>
<p style="margin-top:8px">
<span class="pill">docs-as-code</span><span class="pill">automation</span><span class="pill">DX</span>
</p>
<p style="margin-top:10px">
<a href="https://github.com/vaibhxvvy/documentation-pro"><img src="https://img.shields.io/badge/View_repo-11131A?style=flat-square&logo=github&logoColor=7A5CFA&labelColor=0A0A0F&color=1C1E2A" alt="view documentation-pro"/></a>
</p>
</div>

<div class="card">
<p class="kicker">Featured · TypeScript</p>
<h4><a href="https://github.com/vaibhxvvy/fcuk-paywalls" style="color:#E8E8EE; text-decoration:none">fcuk-paywalls</a></h4>
<p>FCUK PAYWALLS — open index of no-signup, in-browser, open-source tools. No accounts. No walls.</p>
<p style="margin-top:8px">
<span class="pill">open-source</span><span class="pill">no-signup</span><span class="pill">tooling</span>
</p>
<p style="margin-top:10px">
<a href="https://github.com/vaibhxvvy/fcuk-paywalls"><img src="https://img.shields.io/badge/View_repo-11131A?style=flat-square&logo=github&logoColor=00D9FF&labelColor=0A0A0F&color=1C1E2A" alt="view fcuk-paywalls"/></a>
</p>
</div>

</div>

<div class="card" style="margin-top:12px; text-align:center">
<p class="muted" style="font-size:12.5px">More: 
<a href="https://github.com/vaibhxvvy/portfolio" style="color:#7A5CFA">portfolio</a> ·
<a href="https://github.com/vaibhxvvy/agentic-research-assistant" style="color:#7A5CFA">agentic-research-assistant</a> ·
<a href="https://github.com/vaibhxvvy/rag-knowledge-assistant" style="color:#7A5CFA">rag-knowledge-assistant</a> ·
<a href="https://github.com/vaibhxvvy?tab=repositories" style="color:#00D9FF">all repos →</a>
</p>
</div>

</div>
<!-- ===================== PAGE: STATS ===================== -->
<div id="page-stats" class="page">

<h3 id="-stats">◈ Stats — activity</h3>

<p align="center">
  <a href="https://github.com/vaibhxvvy">
    <img src="https://github-readme-stats.vercel.app/api?username=vaibhxvvy&theme=transparent&bg_color=0A0A0F&title_color=7A5CFA&text_color=E8E8EE&icon_color=00D9FF&border_color=1C1E2A&hide_border=false&include_all_commits=true&count_private=true" alt="github stats"/>
  </a>
</p>

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=vaibhxvvy&theme=transparent&bg_color=0A0A0F&title_color=7A5CFA&text_color=E8E8EE&icon_color=00D9FF&border_color=1C1E2A&hide_border=false&include_all_commits=true&count_private=true&layout=compact" alt="top langs"/>
  <img src="https://streak-stats.demolab.com/?user=vaibhxvvy&theme=transparent&background=0A0A0F&border=1C1E2A&stroke=1C1E2A&ring=7A5CFA&fire=7A5CFA&currStreakNum=E8E8EE&currStreakLabel=7A5CFA&sideNums=E8E8EE&sideLabels=8B8DA3&dates=8B8DA3" alt="streak stats"/>
</p>

<p align="center">
  <img src="https://github-readme-activity-graph.vercel.app/graph?username=vaibhxvvy&theme=tokyo-night&bg_color=0A0A0F&color=E8E8EE&line=7A5CFA&point=00D9FF&area=true&hide_border=true" alt="activity graph"/>
</p>

<!-- snake (generated by workflow) — shows after first Action run -->
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/snake-dark.svg"/>
    <img src="assets/snake.svg" alt="contribution snake" width="100%"/>
  </picture>
</p>
<p align="center" class="muted" style="font-size:11px">snake animates your contribution graph — generated daily via <code>snake.yml</code></p>

<p align="center">
  <img src="assets/divider.svg" width="100%" alt="divider"/>
</p>

<!-- stats footer links -->
<p align="center" class="muted" style="font-size:12.5px">
  <a href="https://github.com/vaibhxvvy?tab=repositories" style="color:#7A5CFA">Repositories</a> ·
  <a href="https://github.com/vaibhxvvy?tab=stars" style="color:#7A5CFA">Stars</a> ·
  <a href="https://linkedin.com/in/vaibhavsurthi" style="color:#00D9FF">LinkedIn</a>
</p>

<!-- DONATE — last, as requested -->
<div class="card" align="center" style="margin-top:16px; background: linear-gradient(135deg, #11131A 0%, #0F1120 100%); border-color:#2A2E45">
<p class="kicker" style="color:#7A5CFA">Support</p>
<h4 style="margin:6px 0 4px 0">💰 You can help me by donating</h4>
<p class="muted" style="font-size:12.5px; margin-bottom:10px">If my work helped you — a coffee keeps the pipeline running.</p>
<a href="https://buymeacoffee.com/vaibhxvvy"><img src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-0A0A0F?style=for-the-badge&logo=buy-me-a-coffee&logoColor=ffdd00&labelColor=11131A&color=1C1E2A" alt="buy me a coffee"/></a>
<p style="margin-top:10px">
  <img src="https://komarev.com/ghpvc/?username=vaibhxvvy&style=flat-square&color=7A5CFA&label=views" alt="views bottom"/>
  <img src="https://img.shields.io/github/followers/vaibhxvvy?style=flat-square&label=follow&labelColor=11131A&color=1C1E2A" alt="followers"/>
</p>
</div>

</div>

</div> <!-- end tabs wrapper -->

<p align="center" style="margin-top:14px">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0A0A0F&height=110&section=footer&text=&animation=fadeIn" alt="footer wave"/>
</p>

<p align="center" class="muted" style="font-size:11px; letter-spacing:.4px">crafted for dark · custom palette 0A0A0F / 7A5CFA → 00D9FF · tabs are CSS-only, fallback anchors always work</p>
