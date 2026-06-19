import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Button
import copy
from collections import defaultdict


variables = ["x1", "x2", "x3", "x4"]

domains = {
    "x1": [1, 2],
    "x2": [1, 2],
    "x3": [2, 3],
    "x4": [2, 3, 4, 5],
}

def find_maximum_matching(variables, domains):
    match_var = {}   # var  → val
    match_val = {}   # val  → var

    def augment(var, visited):
        for val in domains[var]:
            if val not in visited:
                visited.add(val)
                if val not in match_val or augment(match_val[val], visited):
                    match_var[var] = val
                    match_val[val] = var
                    return True
        return False

    for var in variables:
        augment(var, set())

    return match_var, match_val


def build_residual_graph(variables, domains, match_var, match_val):
    G = defaultdict(set)
    all_vals = sorted(set(v for d in domains.values() for v in d))
    coupled_vals = set(match_var.values())
    for var in variables:
        for val in domains[var]:
            node_val = f"v{val}"
            if match_var.get(var) == val:
                G[node_val].add(var)
            else:
                G[var].add(node_val)
    for val in all_vals:
        node_val = f"v{val}"
        if val not in coupled_vals:
            G["T"].add(node_val)
            G[node_val].add("T")
    return dict(G)


def tarjan_scc(graph):
    index_counter = [0]
    stack         = []
    lowlink       = {}
    index         = {}
    on_stack      = {}
    sccs          = []

    all_nodes = set(graph.keys())
    for neighbors in graph.values():
        all_nodes |= neighbors

    def strongconnect(v):
        index[v]   = lowlink[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack[v] = True

        for w in graph.get(v, []):
            if w not in index:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack.get(w, False):
                lowlink[v] = min(lowlink[v], index[w])

        if lowlink[v] == index[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    for v in all_nodes:
        if v not in index:
            strongconnect(v)

    return sccs

def regin_filter(variables, domains):
    steps          = []
    domains_orig   = copy.deepcopy(domains)

    steps.append({
        "step_num": 1,
        "type":    "bipartite",
        "title":   "ÉTAPE 1 — Graphe Biparti Initial",
        "desc":    ("Variables à gauche, valeurs à droite.\n"
                    "Chaque arc = valeur possible pour une variable.\n"
                    "But : trouver un couplage maximum."),
        "domains":        copy.deepcopy(domains_orig),
        "match_var":      {},
        "match_val":      {},
        "residual":       {},
        "sccs":           [],
        "node_to_scc":    {},
        "removed_edges":  [],
    })

    match_var, match_val = find_maximum_matching(variables, domains_orig)
    feasible = (len(match_var) == len(variables))

    matching_str = ", ".join(f"({v},{match_var[v]})" for v in variables if v in match_var)
    steps.append({
        "step_num": 2,
        "type":    "matching",
        "title":   "ÉTAPE 2 — Couplage Maximum (Matching)",
        "desc":    (f"M = {{{matching_str}}}\n"
                    + ("✓ Couplage complet — le CSP peut être satisfaisable."
                       if feasible else
                       "✗ Pas de couplage complet → CSP INSATISFAISABLE !")),
        "domains":        copy.deepcopy(domains_orig),
        "match_var":      copy.deepcopy(match_var),
        "match_val":      copy.deepcopy(match_val),
        "residual":       {},
        "sccs":           [],
        "node_to_scc":    {},
        "removed_edges":  [],
        "feasible":       feasible,
    })

    if not feasible:
        return steps, domains_orig

    residual = build_residual_graph(variables, domains_orig, match_var, match_val)

    residual_desc = ("Arcs de couplage M  :  valeur → variable  (vert)\n"
                     "Arcs hors couplage  :  variable → valeur  (bleu)\n"
                     "Nœud fictif T ↔ valeurs non couplées.")
    steps.append({
        "step_num": 3,
        "type":    "residual",
        "title":   "ÉTAPE 3 — Graphe de Résidu (Orienté)",
        "desc":    residual_desc,
        "domains":        copy.deepcopy(domains_orig),
        "match_var":      copy.deepcopy(match_var),
        "match_val":      copy.deepcopy(match_val),
        "residual":       residual,
        "sccs":           [],
        "node_to_scc":    {},
        "removed_edges":  [],
    })

    sccs = tarjan_scc(residual)
    node_to_scc = {}
    for i, scc in enumerate(sccs):
        for node in scc:
            node_to_scc[node] = i

    removed_edges   = []
    filtered_domains = copy.deepcopy(domains_orig)

    for var in variables:
        to_remove = []
        for val in domains_orig[var]:
            if match_var.get(var) != val:         
                s_var = node_to_scc.get(var,    -1)
                s_val = node_to_scc.get(f"v{val}", -2)
                if s_var != s_val:                 
                    removed_edges.append((var, val))
                    to_remove.append(val)
        for v in to_remove:
            if v in filtered_domains[var]:
                filtered_domains[var].remove(v)
        if to_remove:
            print(f"Suppression de {to_remove} dans D({var})")

    scc_desc_lines = []
    for i, scc in enumerate(sccs):
        nodes_clean = [n for n in scc if n != "T"]
        if nodes_clean:
            scc_desc_lines.append(f"SCC{i+1} : {{{', '.join(nodes_clean)}}}")

    filter_desc = ("Tarjan identifie les SCC.\n"
                   "Arc supprimé si hors couplage ET hors SCC commune.\n"
                   + "\n".join(scc_desc_lines[:4]) + "\n"
                   + "Domaines après filtrage :\n"
                   + "  ".join(f"D({v})={{{','.join(map(str,filtered_domains[v]))}}}"
                                for v in variables))

    steps.append({
        "step_num": 4,
        "type":    "scc_filter",
        "title":   "ÉTAPE 4 — SCC & Filtrage Final",
        "desc":    filter_desc,
        "domains":        filtered_domains,
        "domains_before": copy.deepcopy(domains_orig),
        "match_var":      copy.deepcopy(match_var),
        "match_val":      copy.deepcopy(match_val),
        "residual":       residual,
        "sccs":           sccs,
        "node_to_scc":    node_to_scc,
        "removed_edges":  removed_edges,
    })

    return steps, filtered_domains

steps, filtered_domains = regin_filter(variables, domains)

print(f"\n→ {len(steps)} étapes capturées.")
print("\nTableau comparatif domaines :")
print(f"{'Variable':<10} {'Avant':>15} {'Après':>15} {'Supprimé':>15}")
print("-" * 57)
for var in variables:
    d_av  = domains[var]
    d_ap  = filtered_domains[var]
    suppr = [v for v in d_av if v not in d_ap]
    print(f"{var:<10} {str(d_av):>15} {str(d_ap):>15} {str(suppr) if suppr else '-':>15}")


# ════════════════════════════════════════════════════════
#  VISUALISATION MATPLOTLIB
# ════════════════════════════════════════════════════════

# ── Couleurs ──
C_BG      = "#1C2833"
C_PANEL   = "#2C3E50"
C_TEXT    = "#ECF0F1"
C_VAR     = "#2E86C1"   # nœuds variables
C_VAL     = "#E67E22"   # nœuds valeurs
C_MATCH   = "#27AE60"   # arcs / nœuds du couplage
C_RESIDM  = "#27AE60"   # arcs résidu couplage (vert)
C_RESIDNM = "#3498DB"   # arcs résidu hors couplage (bleu)
C_RED     = "#E74C3C"   # suppression
C_GREY    = "#5D6D7E"
C_T_NODE  = "#7D3C98"   # nœud fictif T

# Palette SCC
SCC_COLORS = ["#8E44AD", "#16A085", "#D35400", "#1A5276", "#7B241C", "#1E8449"]


def get_positions(variables, domains_orig):
    """Calcule les positions (x,y) du graphe biparti."""
    all_vals = sorted(set(v for d in domains_orig.values() for v in d))
    n_var    = len(variables)
    n_val    = len(all_vals)

    var_pos = {
        var: (0.18, 0.92 - i * (0.80 / max(n_var - 1, 1)))
        for i, var in enumerate(variables)
    }
    val_pos = {
        val: (0.72, 0.92 - i * (0.80 / max(n_val - 1, 1)))
        for i, val in enumerate(all_vals)
    }
    # Nœud fictif T tout en bas à droite
    t_pos = (0.72, -0.05)

    return var_pos, val_pos, t_pos, all_vals


def draw_arrow_bp(ax, x0, y0, x1, y1, color, lw, alpha, style="-|>", ls="-"):
    """Flèche entre deux points (coords axes)."""
    ax.annotate(
        "", xy=(x1, y1), xytext=(x0, y0),
        arrowprops=dict(
            arrowstyle=style, color=color, lw=lw,
            alpha=alpha, linestyle=ls, mutation_scale=12,
            shrinkA=10, shrinkB=10,
        ),
        xycoords="axes fraction", textcoords="axes fraction",
    )


def draw_node(ax, x, y, label, fc, fontsize=10, r=0.045):
    circle = plt.Circle((x, y), r,
                         color=fc, zorder=5,
                         transform=ax.transAxes, clip_on=False)
    ax.add_patch(circle)
    ax.text(x, y, label, transform=ax.transAxes,
            ha="center", va="center", fontsize=fontsize,
            fontweight="bold", color="white", zorder=6)


def draw_bipartite(ax, step, variables, domains_orig):
    """
    Panneau principal : graphe biparti coloré selon l'étape.
    """
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 1); ax.set_ylim(-0.12, 1.05)
    ax.axis("off")

    stype         = step["type"]
    match_var     = step["match_var"]
    residual      = step["residual"]
    removed_edges = step["removed_edges"]
    node_to_scc   = step["node_to_scc"]
    sccs          = step["sccs"]
    d_now         = step["domains"]

    var_pos, val_pos, t_pos, all_vals = get_positions(variables, domains_orig)

    # ════ ARCS ════
    for var in variables:
        for val in domains_orig[var]:
            vx, vy   = var_pos[var]
            dx, dy   = val_pos[val]
            in_match = (match_var.get(var) == val)
            removed  = (var, val) in removed_edges

            if stype == "bipartite":
                col, lw, alpha, style, ls = C_GREY, 1.2, 0.7, "-", "-"

            elif stype == "matching":
                if in_match:
                    col, lw, alpha, style, ls = C_MATCH, 2.5, 1.0, "-|>", "-"
                else:
                    col, lw, alpha, style, ls = C_GREY, 1.0, 0.35, "-", "-"

            elif stype == "residual":
                # Arcs de résidu : sens inversé pour couplage
                if in_match:
                    # val → var  (on dessine de val vers var)
                    col, lw, alpha, style = C_RESIDM, 2.2, 1.0, "-|>"
                    draw_arrow_bp(ax, dx, dy, vx, vy, col, lw, alpha, style)
                    continue
                else:
                    col, lw, alpha, style, ls = C_RESIDNM, 1.5, 0.8, "-|>", "-"

            elif stype == "scc_filter":
                if removed:
                    col, lw, alpha, style, ls = C_RED, 2.0, 0.9, "-|>", "--"
                elif in_match:
                    # SCC couleur ou vert couplage
                    s = node_to_scc.get(var, -1)
                    col = SCC_COLORS[s % len(SCC_COLORS)] if s >= 0 else C_MATCH
                    lw, alpha, style, ls = 2.5, 1.0, "-|>", "-"
                else:
                    s1 = node_to_scc.get(var,      -1)
                    s2 = node_to_scc.get(f"v{val}", -2)
                    if s1 == s2 and s1 >= 0:
                        col = SCC_COLORS[s1 % len(SCC_COLORS)]
                        lw, alpha, style, ls = 2.0, 0.9, "-|>", "-"
                    else:
                        col, lw, alpha, style, ls = C_GREY, 0.8, 0.2, "-", "-"
            else:
                col, lw, alpha, style, ls = C_GREY, 1.0, 0.5, "-", "-"

            draw_arrow_bp(ax, vx, vy, dx, dy, col, lw, alpha, style, ls)

    # Arcs du résidu vers T (nœud fictif) à l'étape résidu/scc
    if stype in ("residual", "scc_filter"):
        coupled_vals = set(match_var.values())
        for val in all_vals:
            if val not in coupled_vals:
                vx2, vy2 = val_pos[val]
                tx, ty   = t_pos
                s_val = node_to_scc.get(f"v{val}", -1)
                s_t   = node_to_scc.get("T",      -2)
                if stype == "scc_filter" and s_val == s_t and s_val >= 0:
                    col = SCC_COLORS[s_val % len(SCC_COLORS)]
                else:
                    col = C_T_NODE
                draw_arrow_bp(ax, vx2, vy2, tx, ty, col, 1.2, 0.7, "-|>")
                draw_arrow_bp(ax, tx, ty, vx2, vy2, col, 1.2, 0.7, "-|>")

    # ════ NŒUDS VARIABLES ════
    for var in variables:
        vx, vy = var_pos[var]
        s = node_to_scc.get(var, -1)
        if stype == "scc_filter" and s >= 0:
            fc = SCC_COLORS[s % len(SCC_COLORS)]
        else:
            fc = C_VAR
        draw_node(ax, vx, vy, var, fc, fontsize=9)

        # Domaine à gauche du nœud
        d_var = d_now.get(var, [])
        ax.text(vx - 0.12, vy, f"D={{{','.join(map(str,d_var))}}}",
                transform=ax.transAxes, ha="right", va="center",
                fontsize=8, color=C_TEXT)

    # ════ NŒUDS VALEURS ════
    for val in all_vals:
        dx, dy   = val_pos[val]
        in_match = val in match_var.values()
        s = node_to_scc.get(f"v{val}", -1)
        if stype == "scc_filter" and s >= 0:
            fc = SCC_COLORS[s % len(SCC_COLORS)]
        elif stype in ("matching", "residual") and in_match:
            fc = C_MATCH
        else:
            fc = C_VAL
        draw_node(ax, dx, dy, str(val), fc, fontsize=9)

    # Nœud fictif T
    if stype in ("residual", "scc_filter"):
        s_t = node_to_scc.get("T", -1)
        fc_t = SCC_COLORS[s_t % len(SCC_COLORS)] if (stype == "scc_filter" and s_t >= 0) else C_T_NODE
        draw_node(ax, t_pos[0], t_pos[1], "T", fc_t, fontsize=9, r=0.040)
        ax.text(t_pos[0] + 0.10, t_pos[1], "(fictif)", transform=ax.transAxes,
                ha="left", va="center", fontsize=7, color=C_GREY)

    # Étiquettes colonnes
    ax.text(0.18, 1.00, "Variables", transform=ax.transAxes,
            ha="center", fontsize=10, fontweight="bold", color=C_VAR)
    ax.text(0.72, 1.00, "Valeurs",   transform=ax.transAxes,
            ha="center", fontsize=10, fontweight="bold", color=C_VAL)

    ax.set_title(step["title"], color=C_TEXT, fontsize=10, fontweight="bold", pad=6)


def draw_info(ax, step, variables, domains_orig, filtered_domains):
    """Panneau droit : explication + légende SCC."""
    ax.set_facecolor(C_PANEL)
    ax.axis("off")

    badge_col = {
        "bipartite":  "#2E86C1",
        "matching":   "#27AE60",
        "residual":   "#8E44AD",
        "scc_filter": "#E74C3C",
    }.get(step["type"], "#7F8C8D")

    # Badge titre
    rect = mpatches.FancyBboxPatch(
        (0.03, 0.84), 0.94, 0.14,
        boxstyle="round,pad=0.02", fc=badge_col, ec="none",
        transform=ax.transAxes
    )
    ax.add_patch(rect)
    ax.text(0.50, 0.91, step["title"], transform=ax.transAxes,
            ha="center", va="center", fontsize=8.5,
            fontweight="bold", color="white")

    # Description
    lines = step["desc"].split("\n")
    for j, line in enumerate(lines[:7]):
        ax.text(0.05, 0.78 - j * 0.095, line, transform=ax.transAxes,
                ha="left", va="top", fontsize=8, color=C_TEXT)

    # ── Tableau comparatif (étape finale) ──
    if step["type"] == "scc_filter":
        ax.text(0.05, 0.12, "Tableau comparatif :", transform=ax.transAxes,
                ha="left", fontsize=8, color="#95A5A6", fontweight="bold")
        header = f"{'Var':<5} {'Avant':>9} {'Après':>9}"
        ax.text(0.05, 0.06, header, transform=ax.transAxes,
                ha="left", fontsize=7.5, color=C_GREY,
                fontfamily="monospace")
        d_before = step.get("domains_before", domains_orig)
        for i, var in enumerate(variables):
            d_av = d_before.get(var, [])
            d_ap = filtered_domains.get(var, d_av)
            suppr = [v for v in d_av if v not in d_ap]
            col   = C_RED if suppr else C_MATCH
            line  = f"{var:<5} {str(d_av):>9} {str(d_ap):>9}"
            ax.text(0.05, -0.01 - i * 0.06, line, transform=ax.transAxes,
                    ha="left", fontsize=7.5, color=col, fontfamily="monospace")

    # ── Légende SCC colorée ──
    if step["type"] == "scc_filter":
        sccs        = step["sccs"]
        node_to_scc = step["node_to_scc"]
        scc_shown   = {}
        for node, idx in node_to_scc.items():
            if node not in ("T",) and idx not in scc_shown:
                scc_shown[idx] = []
            if node != "T" and idx in scc_shown:
                scc_shown[idx].append(node)


# ════════════════════════════════════════════════════════
#  APPLICATION INTERACTIVE
# ════════════════════════════════════════════════════════

class ReginApp:
    def __init__(self, steps, variables, domains_orig, filtered_domains):
        self.steps            = steps
        self.variables        = variables
        self.domains_orig     = domains_orig
        self.filtered_domains = filtered_domains
        self.idx              = 0

        self.fig = plt.figure(figsize=(13, 7), facecolor=C_BG)
        self.fig.canvas.manager.set_window_title(
            "Exercice 2 — AllDifferent (Algorithme de Régin)"
        )

        gs = gridspec.GridSpec(
            1, 2,
            left=0.03, right=0.97, top=0.90, bottom=0.12,
            wspace=0.28, width_ratios=[2, 1]
        )
        self.ax_main = self.fig.add_subplot(gs[0, 0])
        self.ax_info = self.fig.add_subplot(gs[0, 1])

        # Compteur d'étapes
        self.counter = self.fig.text(
            0.50, 0.96, "", ha="center", va="top",
            fontsize=11, color=C_TEXT, fontweight="bold"
        )

        # Barre de progression
        self.ax_pb = self.fig.add_axes([0.04, 0.055, 0.92, 0.025])
        self.ax_pb.axis("off")

        # Boutons navigation
        ax_p = self.fig.add_axes([0.33, 0.010, 0.13, 0.042])
        ax_n = self.fig.add_axes([0.54, 0.010, 0.13, 0.042])
        self.btn_p = Button(ax_p, "◄ Précédent", color=C_PANEL, hovercolor="#3D5166")
        self.btn_n = Button(ax_n, "Suivant ►",   color=C_PANEL, hovercolor="#3D5166")
        self.btn_p.label.set_color(C_TEXT); self.btn_n.label.set_color(C_TEXT)
        self.btn_p.on_clicked(self._prev)
        self.btn_n.on_clicked(self._next)

        self._render()
        plt.show()

    def _render(self):
        step = self.steps[self.idx]
        self.ax_main.cla()
        self.ax_info.cla()

        draw_bipartite(self.ax_main, step, self.variables, self.domains_orig)
        draw_info(self.ax_info, step, self.variables,
                  self.domains_orig, self.filtered_domains)

        n = len(self.steps)
        self.counter.set_text(f"Étape  {self.idx + 1} / {n}")

        # Barre de progression
        self.ax_pb.cla(); self.ax_pb.axis("off")
        frac = (self.idx + 1) / n
        self.ax_pb.add_patch(mpatches.FancyBboxPatch(
            (0, 0), frac, 1, boxstyle="square,pad=0",
            fc="#8E44AD", ec="none", transform=self.ax_pb.transAxes
        ))
        self.ax_pb.text(frac / 2, 0.5, f"{int(frac * 100)} %",
                        transform=self.ax_pb.transAxes,
                        ha="center", va="center", fontsize=7, color="white")

        self.fig.canvas.draw_idle()

    def _next(self, _):
        if self.idx < len(self.steps) - 1:
            self.idx += 1; self._render()

    def _prev(self, _):
        if self.idx > 0:
            self.idx -= 1; self._render()


# ── Lancement ──
domains_orig = copy.deepcopy(domains)
ReginApp(steps, variables, domains_orig, filtered_domains)
