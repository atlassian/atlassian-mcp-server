"""Boards: an interactive board of work items to select and start sessions from. CSS: board.css.

The page carries its data and renders the cards in the browser, so the filter, the toggles, selection, the dock
and the live refresh all work on the same list. The board scrolls inside its own box, never the page.
"""
import json

from .icons import icon
from .links import e

# Cards, selection, the filter and toggles, one command per selected item, Copy, and the live refresh through
# window.claude.use("mcp") with one searchJiraIssuesUsingJql read. DATA and CONNECTOR come first.
BOARD_JS = r'''
const $ = id => document.getElementById(id);
const sel = new Set();
let issues = DATA.issues;
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const url = k => `${DATA.site}/browse/${k}`;
function prompt(i) {
  return `Work on Jira ${i.key}: ${i.summary}. Read ${url(i.key)} first (description, comments, linked work) using the Atlassian MCP. Plan the change, make it on a new branch, run the tests, and summarise what you did. Don't transition or comment on the work item until I say so.`;
}
const sh = s => `'${s.replace(/'/g, `'\\''`)}'`;
function command(i) {
  const repo = $("repo").value.trim();
  return `${repo ? `cd ${repo.startsWith("~/") ? "~/" + sh(repo.slice(2)) : sh(repo)} && ` : ""}claude ${sh(prompt(i))}`;
}
function render() {
  const q = $("filter").value.toLowerCase(), hd = $("hidedone").checked, he = $("hideepics").checked;
  const cols = hd ? DATA.columns.filter(c => !c.done) : DATA.columns;
  $("cols").style.setProperty("--n", cols.length);
  $("cols").innerHTML = cols.map(c => {
    const list = issues.filter(i => c.statuses.includes(i.status) && !(he && i.type === "Epic") &&
      (!q || (i.key + " " + i.summary).toLowerCase().includes(q)));
    return `<section class="board-col" aria-label="${esc(c.name)}"><h2 class="board-col__head"><span>${esc(c.name)}</span><span class="board-col__count">${list.length}</span></h2>` +
      (list.map(i => `<div class="board-card${i.type === "Epic" ? " board-card--epic" : ""}">
        <button type="button" class="board-card__title" data-k="${esc(i.key)}" aria-pressed="${sel.has(i.key)}">${esc(i.summary)}</button>
        <span class="board-card__meta"><span class="board-card__key">${esc(i.key)}</span><span class="tag board-card__type" data-type="${esc(i.type)}">${esc(i.type)}</span>
        <span>${esc(i.assignee || "Unassigned")}</span><a class="board-card__open" href="${esc(url(i.key))}" target="_blank" rel="noopener">Open<span class="visually-hidden"> ${esc(i.key)} in a new tab</span></a></span></div>`).join("")
        || `<div class="board-col__empty">Nothing here</div>`) + `</section>`;
  }).join("");
  dock();
}
function dock() {
  const picked = issues.filter(i => sel.has(i.key));
  $("dock").hidden = picked.length === 0;
  $("count").textContent = `${picked.length} work item${picked.length === 1 ? "" : "s"} selected`;
  $("out").value = picked.map(command).join("\n\n");
}
async function copy(text, what) {
  try { await navigator.clipboard.writeText(text); $("copied").textContent = `Copied ${what}.`; }
  catch { $("out").value = text; $("out").select(); $("copied").textContent = `Copy blocked here: the ${what} are selected, press Ctrl/Cmd+C.`; }
}
$("cols").addEventListener("click", e => {
  const c = e.target.closest("[data-k]"); if (!c) return;
  sel.has(c.dataset.k) ? sel.delete(c.dataset.k) : sel.add(c.dataset.k);
  render();
});
["filter", "hidedone", "hideepics"].forEach(id => $(id).addEventListener("input", render));
$("repo").addEventListener("input", dock);
$("clear").onclick = () => { sel.clear(); render(); };
$("copyall").onclick = () => copy(issues.filter(i => sel.has(i.key)).map(command).join("\n\n"), "commands");
$("copyprompt").onclick = () => copy(issues.filter(i => sel.has(i.key)).map(prompt).join("\n\n"), "prompts");
function setState(live, text) { $("state").classList.toggle("board-state--live", live); $("statetext").textContent = text; }
async function refresh(mcp) {
  const res = await mcp.callTool(CONNECTOR, "searchJiraIssuesUsingJql", {
    cloudId: DATA.cloudId, jql: DATA.jql, maxResults: 100,
    fields: ["summary", "status", "issuetype", "priority", "assignee"] }, {cache: {refresh: true}});
  const nodes = res.payload?.issues?.nodes ?? res.payload?.issues ?? [];
  issues = nodes.map(n => ({ key: n.key, summary: n.fields.summary, status: n.fields.status?.name,
    type: n.fields.issuetype?.name, priority: n.fields.priority?.name, assignee: n.fields.assignee?.displayName }));
  setState(true, "Live, updated " + new Date().toLocaleTimeString([], {hour: "2-digit", minute: "2-digit"}));
  render();
}
let bridge = null;
$("refresh").onclick = async () => {
  if (!bridge) return setState(false, "Live refresh needs the Atlassian connector in Claude");
  try { await refresh(bridge); } catch (e) {
    const m = {needs_reauth: "Reconnect Atlassian in claude.ai Settings, then Connectors", server_not_connected: "Add Atlassian in claude.ai Settings, then Connectors"}[e.code];
    setState(false, m || "Couldn't refresh just now; showing the snapshot");
  }
};
setState(false, "Snapshot " + DATA.builtAt);
render();
(window.claude?.use ? window.claude.use("mcp") : Promise.resolve(null)).then(m => { bridge = m; if (m) $("refresh").click(); }).catch(() => {});
'''


def board_state():
    """The snapshot or live state pill, for the right of the page header. The script keeps it up to date.

        k.header('Work board', d['boardName'], meta, counts=k.board_state())
    """
    return ('<span class="board-state" id="state" role="status"><span class="board-state__dot" aria-hidden="true"></span>'
            '<span id="statetext">Snapshot</span></span>')


def board(d):
    """The board: the toolbar (repo field, filter, Hide Done and Hide epics toggles, Refresh), the columns the
    script fills, the snapshot line, and the dock for the selected items' commands. Put board_state() in the
    header, and pass board_script(d) as the page's js.

    Data: {"site", "cloudId", "boardId", "boardName", "boardUrl", "jql", "connector", "builtAt", "columns": [{"name",
    "statuses", "done"}], "issues": [{"key", "summary", "status", "type", "priority", "assignee"}]}.

        k.page(d['boardName'], k.board(d), js=k.board_script(d), width='board')
    """
    tools = ('<div class="board-tools">'
             '<label class="board-field"><span>Repo or folder</span><input class="board-input" id="repo" type="text" placeholder="~/Projects/my-repo (optional)"></label>'
             '<label class="board-field"><span>Filter</span><input class="board-input" id="filter" type="text" placeholder="Key or text"></label>'
             '<label class="board-toggle"><input type="checkbox" id="hidedone" checked> Hide Done</label>'
             '<label class="board-toggle"><input type="checkbox" id="hideepics"> Hide epics</label>'
             f'<button class="btn" type="button" id="refresh">{icon("changes")}<span>Refresh from Jira</span></button></div>')
    cols = '<div class="board-scroll"><div class="board-cols" id="cols"></div></div>'
    note = (f'<p class="fine">Snapshot of board {e(d["boardId"])} built {e(d["builtAt"])} from Jira. '
            'Live refresh re-runs one JQL read with the viewer\'s own access.</p>')
    dock = ('<div class="board-dock" id="dock" hidden><div class="board-dock__in">'
            '<div class="board-dock__row"><b id="count"></b>'
            '<button class="btn btn--primary" type="button" id="copyall">Copy session commands</button>'
            '<button class="btn" type="button" id="copyprompt">Copy prompt only</button>'
            '<button class="btn btn--subtle" type="button" id="clear">Clear</button>'
            '<span class="fine" id="copied" role="status"></span></div>'
            '<textarea class="board-out" id="out" readonly aria-label="Session commands"></textarea>'
            '<p class="fine">Artifacts can\'t launch Claude sessions. Paste each line in a terminal (one session per work item), '
            'or paste the prompt into a new Claude Code session. Nothing is written to Jira.</p></div></div>')
    return f'{tools}{cols}{note}{dock}'


def board_script(d):
    """The board's page script, with the data and the connector's display name in front of it.

        board_script({"connector": "Atlassian Rovo", ...})
    """
    data = json.dumps(d, ensure_ascii=False).replace('</', '<\\/')
    connector = json.dumps(d.get('connector', 'Atlassian Rovo')).replace('</', '<\\/')
    return f'const DATA = {data};\nconst CONNECTOR = {connector};\n' + BOARD_JS
