import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Button
import copy
from collections import deque


domains = {
    "X": [1, 2],
    "Y": [1, 2],
    "Z": [1, 2]
}


def constraint(x, y, a, b):
    if x == "X" and y == "Y":
        return a < b
    if x == "Y" and y == "X":
        return b < a
    if x == "Y" and y == "Z":
        return a == b
    if x == "Z" and y == "Y":
        return a == b
    return True


queue = deque([
    ("X", "Y"),
    ("Y", "X"),
    ("Y", "Z"),
    ("Z", "Y")
])

neighbors = {
    "X": ["Y"],
    "Y": ["X", "Z"],
    "Z": ["Y"],
}

def revise(x, y):
    revised        = False
    values_to_remove = []

    for a in domains[x]:
        possible = False
        for b in domains[y]:
            if constraint(x, y, a, b):
                possible = True
                break
        if not possible:
            values_to_remove.append(a)

    for value in values_to_remove:
        domains[x].remove(value)
        revised = True
        print(f"  Suppression de {value} dans D({x})")

    return revised, values_to_remove  

# ── Liste des étapes pour la visualisation ──
steps = []

def save_step(step_type, arc, queue_snapshot, removed=[], propagated=[], title="", desc=""):
    """Enregistre un instantané de l'état courant."""
    steps.append({
        "type":       step_type,
        "arc":        arc,
        "domains":    copy.deepcopy(domains),
        "queue":      list(queue_snapshot),
        "removed":    list(removed),
        "propagated": list(propagated),
        "title":      title,
        "desc":       desc,
    })

# ── Étape 0 : état initial ──
save_step(
    "initial", None, queue,
    title="ÉTAT INITIAL",
    desc=f"Domaines : D(X)={domains['X']}  D(Y)={domains['Y']}  D(Z)={domains['Z']}\n"
         f"File Q initiale : {list(queue)}"
) 

# ════════════════════════════════
#  ALGORITHME AC3
# ════════════════════════════════
while queue:

    x, y = queue.popleft()

    print(f"\nTraitement : ({x},{y})")
    print(f"Domaines avant : {domains}")

    # Sauvegarde "traitement de l'arc"
    save_step(
        "examine", (x, y), [( x, y)] + list(queue),
        title=f"TRAITEMENT — Arc ({x},{y})",
        desc=f"Arc ({x},{y}) extrait de la file.\n"
             f"→ Appel de Revise({x},{y})\n"
             f"D({x}) = {domains[x]}    D({y}) = {domains[y]}"
    )

    revised, removed = revise(x, y)

    if revised:
        if len(domains[x]) == 0:
            save_step(
                "failure", (x, y), list(queue), removed=removed,
                title="ÉCHEC — Domaine vide !",
                desc=f"D({x}) est vide après suppression de {removed}.\n"
                     f"Le CSP est INSATISFAISABLE."
            )
            print("Echec : domaine vide")
            break

        # Propagation : réinsertion des arcs voisins
        new_arcs = []
        for xk in neighbors[x]:
            if xk != y:
                new_arc = (xk, x)
                if new_arc not in queue:
                    queue.append(new_arc)
                    new_arcs.append(new_arc)

        save_step(
            "revise", (x, y), list(queue),
            removed=removed, propagated=new_arcs,
            title=f"SUPPRESSION — Arc ({x},{y})",
            desc=f"Valeur(s) supprimée(s) de D({x}) : {removed}\n"
                 f"D({x}) = {domains[x]}\n"
                 + (f"Arcs réinsérés dans Q : {new_arcs}" if new_arcs else "Aucun arc réinséré.")
        )
    else:
        save_step(
            "no_change", (x, y), list(queue),
            title=f"AUCUNE MODIFICATION — Arc ({x},{y})",
            desc=f"Revise({x},{y}) : aucune valeur supprimée.\n"
                 f"D({x}) = {domains[x]}  (inchangé)"
        )

    print(f"Domaines après  : {domains}")

# État final
save_step(
    "final", None, [],
    title="ÉTAT FINAL — CSP Arc-Consistant ✓",
    desc=f"File Q vide. Tous les domaines sont stables.\n"
         f"D(X)={domains['X']}   D(Y)={domains['Y']}   D(Z)={domains['Z']}"
)

print("\nRésultat final")
print(domains)

# ════════════════════════════════════════════════════════
#  VISUALISATION MATPLOTLIB
# ════════════════════════════════════════════════════════

# ── Couleurs ──
C_BG    = "#1C2833"
C_PANEL = "#2C3E50"
C_TEXT  = "#ECF0F1"
C_NODE  = "#2E86C1"
C_ACT   = "#E67E22"   # arc/nœud actif (orange)
C_GREEN = "#27AE60"   # propagation / OK
C_RED   = "#E74C3C"   # suppression / échec
C_GREY  = "#5D6D7E"   # arcs inactifs

# ── Positions fixes des nœuds ──
#   X  en haut à gauche, Y  en haut à droite, Z  en bas au centre
NODE_POS = {
    "X": (0.25, 0.72),
    "Y": (0.75, 0.72),
    "Z": (0.50, 0.28),
}

# Tous les arcs possibles et leurs étiquettes de contrainte
ALL_ARCS = [("X","Y"), ("Y","X"), ("Y","Z"), ("Z","Y")]
ARC_LABEL = {
    ("X","Y"): "X<Y", ("Y","X"): "Y>X",
    ("Y","Z"): "Y=Z", ("Z","Y"): "Z=Y",
}

def _draw_arrow(ax, u, v, color, lw, alpha, label=""):
    """Dessine une flèche entre deux nœuds avec une légère déviation."""
    x0, y0 = NODE_POS[u]
    x1, y1 = NODE_POS[v]
    dx, dy  = x1 - x0, y1 - y0
    L = (dx**2 + dy**2) ** 0.5
    # Perpendiculaire pour séparer les doubles arcs
    px, py = -dy / L * 0.06, dx / L * 0.06
    r = 0.10           # rayon du cercle du nœud (en coordonnées axes)

    ax.annotate(
        "", xy=(x1 + px - dx/L*r, y1 + py - dy/L*r),
        xytext=(x0 + px + dx/L*r, y0 + py + dy/L*r),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                        alpha=alpha, mutation_scale=14),
    )
    if label:
        mx, my = (x0+x1)/2 + px*2, (y0+y1)/2 + py*2
        ax.text(mx, my, label, fontsize=7, color=color, alpha=alpha,
                ha="center", va="center", fontweight="bold")


def draw_graph(ax, step):
    """Panneau gauche : graphe de contraintes."""
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")

    arc        = step["arc"]
    propagated = step["propagated"]
    domains_s  = step["domains"]
    domains_b  = step.get("domains_before", domains_s)

    # ── Arcs ──
    for (u, v) in ALL_ARCS:
        if arc == (u, v):
            col, lw, alpha = C_ACT, 2.8, 1.0
        elif (u, v) in propagated:
            col, lw, alpha = C_GREEN, 2.2, 1.0
        else:
            col, lw, alpha = C_GREY, 1.0, 0.45
        _draw_arrow(ax, u, v, col, lw, alpha, label=ARC_LABEL[(u, v)])

    # ── Nœuds ──
    for node, (nx, ny) in NODE_POS.items():
        is_active = arc is not None and node in arc
        fc = C_ACT if is_active else C_NODE
        circle = plt.Circle((nx, ny), 0.10, color=fc, zorder=5)
        ax.add_patch(circle)
        ax.text(nx, ny, node, ha="center", va="center",
                fontsize=15, fontweight="bold", color="white", zorder=6)

        # ── Domaine sous le nœud ──
        d_now = domains_s[node]
        # Toutes les valeurs qui étaient là au début (1,2)
        all_vals = [1, 2]
        removed_here = step["removed"] if arc and node == arc[0] else []

        txt_x = nx - 0.10
        ax.text(txt_x, ny - 0.17, f"D({node})={{", fontsize=8,
                color=C_TEXT, ha="center", va="center")

        for i, val in enumerate(all_vals):
            cx = nx - 0.04 + i * 0.08
            cy = ny - 0.17
            if val in removed_here:
                col_v = C_RED
                ax.plot([cx-0.025, cx+0.025], [cy, cy],
                        color=C_RED, lw=2, zorder=7)   # barre de suppression
            elif val in d_now:
                col_v = C_GREEN
            else:
                col_v = C_RED
            ax.text(cx, cy, str(val), fontsize=9,
                    color=col_v, fontweight="bold", ha="center", va="center", zorder=6)

        ax.text(nx + 0.10, ny - 0.17, "}", fontsize=8,
                color=C_TEXT, ha="center", va="center")

    ax.set_title("Graphe de Contraintes", color=C_TEXT,
                 fontsize=10, fontweight="bold", pad=4)


def draw_queue(ax, step):
    """Panneau centre : file Q."""
    ax.set_facecolor(C_PANEL)
    ax.axis("off")
    ax.set_title("File Q", color=C_TEXT, fontsize=10, fontweight="bold", pad=4)

    queue_s    = step["queue"]
    arc        = step["arc"]
    propagated = step["propagated"]

    ax.text(0.5, 0.95, "Q =", transform=ax.transAxes,
            ha="center", va="top", fontsize=11, color=C_TEXT, fontweight="bold")

    if not queue_s:
        ax.text(0.5, 0.50, "∅  (vide)", transform=ax.transAxes,
                ha="center", va="center", fontsize=13, color=C_GREY)
        return

    box_h = min(0.11, 0.78 / len(queue_s))
    for i, a in enumerate(queue_s):
        y = 0.84 - i * (box_h + 0.025)
        if a == arc:
            fc, tc = C_ACT, "white"
        elif a in propagated:
            fc, tc = C_GREEN, "white"
        else:
            fc, tc = "#34495E", C_TEXT

        rect = mpatches.FancyBboxPatch(
            (0.15, y), 0.70, box_h,
            boxstyle="round,pad=0.01", fc=fc, ec="#7F8C8D", lw=1.2,
            transform=ax.transAxes, clip_on=True
        )
        ax.add_patch(rect)
        ax.text(0.50, y + box_h/2, f"({a[0]},{a[1]})",
                transform=ax.transAxes, ha="center", va="center",
                fontsize=10, fontweight="bold", color=tc)
        # Petite flèche "tête de file"
        if i == 0:
            ax.text(0.90, y + box_h/2, "◄",
                    transform=ax.transAxes, ha="center", va="center",
                    fontsize=11, color=C_ACT)


def draw_info(ax, step):
    """Panneau droit : informations textuelles."""
    ax.set_facecolor(C_PANEL)
    ax.axis("off")

    badge_col = {
        "initial":   "#2E86C1",
        "examine":   "#E67E22",
        "revise":    "#E74C3C",
        "no_change": "#27AE60",
        "final":     "#1E8449",
        "failure":   "#922B21",
    }.get(step["type"], "#7F8C8D")

    # Badge titre
    rect = mpatches.FancyBboxPatch(
        (0.03, 0.82), 0.94, 0.15,
        boxstyle="round,pad=0.02", fc=badge_col, ec="none",
        transform=ax.transAxes
    )
    ax.add_patch(rect)
    ax.text(0.50, 0.895, step["title"], transform=ax.transAxes,
            ha="center", va="center", fontsize=9,
            fontweight="bold", color="white", wrap=True)

    # Description (word-wrap simple)
    lines = step["desc"].split("\n")
    for j, line in enumerate(lines[:6]):
        ax.text(0.05, 0.72 - j*0.11, line, transform=ax.transAxes,
                ha="left", va="top", fontsize=8.5, color=C_TEXT)

    # Résumé domaines en bas
    ax.text(0.05, 0.10, "Domaines actuels :", transform=ax.transAxes,
            ha="left", fontsize=8, color="#95A5A6")
    dom = step["domains"]
    ax.text(0.05, 0.03,
            f"D(X)={{{','.join(map(str,dom['X']))}}}   "
            f"D(Y)={{{','.join(map(str,dom['Y']))}}}   "
            f"D(Z)={{{','.join(map(str,dom['Z']))}}}",
            transform=ax.transAxes, ha="left", va="bottom",
            fontsize=9, fontweight="bold", color=C_TEXT)


# ════════════════════════════════
#  APPLICATION INTERACTIVE
# ════════════════════════════════

class AC3App:
    def __init__(self, steps):
        self.steps = steps
        self.idx   = 0

        self.fig = plt.figure(figsize=(13, 6.5), facecolor=C_BG)
        self.fig.canvas.manager.set_window_title("Visualisation AC3")

        gs = gridspec.GridSpec(
            1, 3, left=0.04, right=0.96,
            top=0.88, bottom=0.12, wspace=0.28
        )
        self.ax_g = self.fig.add_subplot(gs[0, 0])
        self.ax_q = self.fig.add_subplot(gs[0, 1])
        self.ax_i = self.fig.add_subplot(gs[0, 2])

        # Compteur
        self.counter = self.fig.text(
            0.5, 0.95, "", ha="center", va="top",
            fontsize=11, color=C_TEXT, fontweight="bold"
        )

        # Barre de progression
        self.ax_pb = self.fig.add_axes([0.04, 0.055, 0.92, 0.025])
        self.ax_pb.axis("off")

        # Boutons
        ax_p = self.fig.add_axes([0.33, 0.01, 0.13, 0.042])
        ax_n = self.fig.add_axes([0.54, 0.01, 0.13, 0.042])
        self.btn_p = Button(ax_p, "◄ Précédent", color=C_PANEL, hovercolor="#3D5166")
        self.btn_n = Button(ax_n, "Suivant ►",   color=C_PANEL, hovercolor="#3D5166")
        self.btn_p.label.set_color(C_TEXT)
        self.btn_n.label.set_color(C_TEXT)
        self.btn_p.on_clicked(self._prev)
        self.btn_n.on_clicked(self._next)

        self._render()
        plt.show()

    def _render(self):
        step = self.steps[self.idx]
        # Ajoute les domaines "avant revise" pour la barre des supprimés
        if self.idx > 0:
            step["domains_before"] = self.steps[self.idx - 1]["domains"]

        for ax in (self.ax_g, self.ax_q, self.ax_i):
            ax.cla()

        draw_graph(self.ax_g, step)
        draw_queue(self.ax_q, step)
        draw_info(self.ax_i, step)

        n = len(self.steps)
        self.counter.set_text(f"Étape  {self.idx+1} / {n}")

        # Barre de progression
        self.ax_pb.cla(); self.ax_pb.axis("off")
        frac = (self.idx+1) / n
        self.ax_pb.add_patch(mpatches.FancyBboxPatch(
            (0,0), frac, 1, boxstyle="square,pad=0",
            fc="#2E86C1", ec="none", transform=self.ax_pb.transAxes
        ))
        self.ax_pb.text(frac/2, 0.5, f"{int(frac*100)} %",
                        transform=self.ax_pb.transAxes,
                        ha="center", va="center", fontsize=7, color="white")

        self.fig.canvas.draw_idle()

    def _next(self, _):
        if self.idx < len(self.steps)-1:
            self.idx += 1; self._render()

    def _prev(self, _):
        if self.idx > 0:
            self.idx -= 1; self._render()


# ── Lancement ──
print(f"\n→ {len(steps)} étapes capturées. Ouverture de la fenêtre…")
AC3App(steps)
