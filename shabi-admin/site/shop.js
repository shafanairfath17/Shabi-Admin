(() => {
"use strict";
const IG_PROFILE = "https://www.instagram.com/shabi_jewels/", IG_DM = "https://ig.me/m/shabi_jewels";
const el = (t, c, x) => { const e = document.createElement(t); if (c) e.className = c; if (x != null) e.textContent = x; return e; };
const svg = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6"/></svg>';
const api = async url => { const r = await fetch(url, { headers: { Accept: "application/json" } }); if (!r.ok) throw new Error(r.status); return r.json(); };

let toastEl;
function toast(msg, kind) {            // one toast at a time, with close button
  if (toastEl) toastEl.remove();
  const t = toastEl = el("div", "toast " + (kind || ""), msg); t.setAttribute("role", "status");
  const x = el("button", "toast-x", "×"); x.type = "button"; x.setAttribute("aria-label", "Close"); t.appendChild(x);
  const close = () => { t.classList.add("out"); setTimeout(() => t.remove(), 300); };
  x.onclick = close; document.body.appendChild(t); setTimeout(close, 4500);
}

function select(label, opts, id) {
  if (!opts || opts.length < 2) return null;
  const l = el("label", null, label + " "), s = el("select"); s.id = id; s.setAttribute("aria-label", label);
  opts.forEach(o => s.appendChild(new Option(o, o))); l.appendChild(s); return l;
}

function openViewer(v, p) {            // gallery with thumbnails
  const big = v.querySelector(".big"), th = v.querySelector(".thumbs"); th.textContent = "";
  const show = i => { big.src = p.images[i].url; big.alt = p.images[i].alt; };
  show(0);
  if (p.images.length > 1) p.images.forEach((im, i) => { const b = el("button"); b.type = "button"; b.setAttribute("aria-label", "Photo " + (i + 1)); const t = el("img"); t.src = im.url; t.alt = ""; b.appendChild(t); b.onclick = () => show(i); th.appendChild(b); });
  v.showModal();
}

function card(p, i, viewer) {
  const out = p.stock === "out_of_stock", c = el("article", "pcard"); c.style.animationDelay = i * 80 + "ms";
  const b = el("button", "pimg"); b.type = "button"; b.setAttribute("aria-label", "Preview " + p.name);
  b.appendChild(el("span", "ph", "Shabi"));
  if (p.img) { const im = el("img"); im.src = p.img; im.alt = p.images[0].alt; im.loading = "lazy"; im.onerror = () => im.remove(); b.appendChild(im); b.onclick = () => openViewer(viewer, p); }
  else { b.disabled = true; b.style.cursor = "default"; }
  if (out) b.appendChild(el("span", "soon oos", "Out of Stock"));
  const body = el("div", "pbody");
  body.append(el("h3", null, p.name), el("div", "price", p.price != null ? "₹" + p.price : "DM for price"), el("span", "stock " + p.stock, p.label));
  if (p.desc) body.appendChild(el("p", null, p.desc));
  const dl = el("dl"); [["Material", p.material], ["Care", p.care]].forEach(([k, v]) => v && dl.append(el("dt", null, k), el("dd", null, v))); body.appendChild(dl);
  const col = select("Colour", p.colors, "c" + i), siz = select("Size", p.sizes, "s" + i);
  [col, siz].forEach(x => x && body.appendChild(x));
  const a = el(out ? "button" : "a", "btn " + (out ? "btn-line" : "btn-gold"), out ? "Out of Stock" : "Order via Instagram");
  if (out) { a.type = "button"; a.setAttribute("aria-disabled", "true"); a.onclick = () => toast(p.name + " is currently out of stock. DM us to be notified.", "warn"); }
  else {
    a.href = IG_DM; a.target = "_blank"; a.rel = "noopener noreferrer";
    a.addEventListener("click", () => {
      const parts = [p.name]; if (col) parts.push(col.querySelector("select").value); if (siz) parts.push("size " + siz.querySelector("select").value);
      const msg = "Hi Shabi Jewels! I'd like to order: " + parts.join(", ") + (p.price != null ? " (₹" + p.price + ")" : "");
      if (navigator.clipboard) navigator.clipboard.writeText(msg).then(() => toast("Order message copied. Paste it in the Instagram DM.", "ok"), () => toast("Open the DM and mention: " + p.name));
    });
  }
  body.appendChild(a); c.append(b, body); return c;
}

async function renderCollection() {
  const grid = document.getElementById("grid"); if (!grid) return;
  const slug = grid.dataset.collection || new URLSearchParams(location.search).get("c"), viewer = document.getElementById("viewer");
  viewer.addEventListener("click", e => { if (e.target === viewer || e.target.classList.contains("x")) viewer.close(); });
  const nav = document.getElementById("nav"); addEventListener("scroll", () => nav.classList.toggle("scrolled", scrollY > 40), { passive: true });
  const yr = document.getElementById("yr"); if (yr) yr.textContent = new Date().getFullYear();
  try {
    if (!slug || !/^[a-z0-9-]+$/.test(slug)) throw new Error("bad slug");
    const d = await api("/api/collections/" + slug + "/");
    document.title = d.category.name + " | Shabi Jewels";
    if (!grid.dataset.collection) { const h = document.querySelector(".shop h2"), e = document.querySelector(".shop .eyebrow"); if (h) h.textContent = d.category.name; if (e) e.textContent = d.category.name; }
    grid.textContent = "";
    if (!d.products.length) return grid.appendChild(el("p", "state", "New pieces are coming soon. Follow us on Instagram for updates."));
    d.products.forEach((p, i) => grid.appendChild(card(p, i, viewer)));
  } catch (e) { grid.textContent = ""; grid.appendChild(el("p", "state", "Sorry, this collection could not be loaded. Please refresh, or DM us on Instagram.")); }
}

const ICONS = {
  rings: '<svg viewBox="0 0 64 64"><circle cx="32" cy="41" r="14"/><path d="M25 24l7-9 7 9-7 7z"/></svg>',
  bracelets: '<svg viewBox="0 0 64 64"><path d="M8 30c8 8 40 8 48 0"/><circle cx="16" cy="36" r="2"/><circle cx="26" cy="39" r="2"/><circle cx="38" cy="39" r="2"/><circle cx="48" cy="36" r="2"/></svg>',
  necklaces: '<svg viewBox="0 0 64 64"><path d="M10 10c0 18 10 28 22 28s22-10 22-28"/><path d="M32 38v6"/><path d="M32 44l-5 6 5 6 5-6z"/></svg>'
};
const DESC = { rings: "Minimal & stackable", bracelets: "Dainty & everyday", necklaces: "Pendants & chains" };
async function renderCategories() {    // home page cards follow the admin's collections
  const box = document.querySelector(".cats"); if (!box) return;
  try {
    const d = await api("/api/categories/"); if (!d.categories.length) return;
    const frag = document.createDocumentFragment();
    d.categories.forEach(c => {
      const a = el("a", "cat reveal in"); a.href = c.url; a.setAttribute("aria-label", "Browse " + c.name);
      if (c.cover) { a.classList.add("hasimg"); const im = el("img"); im.src = c.cover; im.alt = c.name; im.loading = "lazy"; a.appendChild(im); }
      else a.insertAdjacentHTML("afterbegin", ICONS[c.slug] || ICONS.rings);
      a.append(el("small", null, c.description || DESC[c.slug] || ""), el("h3", null, c.name)); frag.appendChild(a);
    });
    box.textContent = ""; box.appendChild(frag);
  } catch (e) { /* keep the built-in cards */ }
}

function igButton() {
  const a = el("a", "ig-side"); a.href = IG_PROFILE; a.target = "_blank"; a.rel = "noopener noreferrer";
  a.setAttribute("aria-label", "Follow Shabi Jewels on Instagram (opens in a new tab)");
  a.innerHTML = svg; a.appendChild(el("span", null, "Follow us on Instagram")); document.body.appendChild(a);
}
igButton(); renderCategories(); renderCollection();
})();
