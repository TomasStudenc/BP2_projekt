# ==========================================================
# TSP tool
# tento kód obsahuje GUI a vyzualizáciu výsledkov
# táto časť sa používa na nastavovanie hyperparametrov
# importované BP2_*** knižnice sú mnou vytvorené algoritmy ktoré sa volajú na spúštanie simulácií
# ==========================================================
import BP2_GA  # GA algoritmus
import BP2_ABC # ABC algoritmus
import BP2_ACO # ACO algoritmus
import BP2_PSO # PSO algoritmus
import BP2_FFA # FFA algoritmus
import threading
import queue
import time          # knižnica na čas – používa sa na zistenie času behu algoritmov
import matplotlib    # používa sa na vyzualizáciu výsledkov
import matplotlib.pyplot as plt  # využíva sa na vyzualizáciu výsledkov
import tkinter as tk # využíva sa na GUI
import random        # knižnica na generovanie náhodných hodnôt
from tkinter import filedialog, messagebox  # využíva sa na GUI
import customtkinter as ctk  # krajšie GUI a úprava buttonov
from PIL import Image, ImageTk  # importovanie vlastných obrázkov na pozadie

# ----- Settings -----
size = 500  # definuje velkosť kresliacej plochy
cords = []  # zoznam koordinácií bodov v priestore
cities = 0  # počet vrcholov grafu
background_path = None  # definovaná path na pozadie
bg_preview  = None  # holder pre importovaný obrázok
bg_image_id = None  # id obrázka na mazanie

# holdery na výsledky simulácií
ant_count         = 0  # velkosť populácie pri ACO
pop_size          = 0  # velkosť populácie pri GA
bee_count         = 0  # velkosť populácie pri ABC
particle_count    = 0  # velkosť populácie pri PSO
firefly_count     = 0  # velkosť populácie pri FFA
best_tour_gen_aco = 0  # najlepšia generácia pri ACO
best_tour_gen_ga  = 0  # najlepšia generácia pre GA
best_tour_gen_abc = 0  # najlepšia generácia pri ABC
best_tour_gen_pso = 0  # najlepšia generácia pri PSO
best_tour_gen_ffa = 0  # najlepšia generácia pri FFA

current_color = "#0000FF"  # predvolená farba vrcholov

# Farebná paleta pre každý algoritmus (konzistentná v celom programe)
ALGO_COLORS = {
    "ACO": "red",
    "GA":  "green",
    "ABC": "magenta",
    "PSO": "blue",
    "FFA": "darkorange",
}

# ==========================================================
#  Zobrazovanie výsledkov — dynamické pre 1 až 4 algoritmy
# ==========================================================
def display_comparison(coords, results_dict, params):
    """
    results_dict: { "ACO": tuple, "GA": tuple, ... } — len vybrané algoritmy (uppercase kľúče).
    Rozloženie je vždy pevné 2x4.  Prázdne route-sloty ostanú biele (axis off).
    """
    matplotlib.use("TkAgg")

    # ---- Normalizácia každého algoritmu na spoločný formát ----
    def normalize(name, data):
        if name == "ACO":
            tours, lengths, best_gen = data
            return tours[-1], lengths, lengths[-1], best_gen
        elif name == "GA":
            genome, dists, best_gen = data
            return genome + [genome[0]], dists, dists[-1], best_gen
        elif name == "ABC":
            route, dists, best_gen = data
            return route, dists, dists[-1], best_gen
        elif name == "PSO":
            genome, dists, best_gen = data
            return genome + [genome[0]], dists, dists[-1], best_gen
        elif name == "FFA":
            route, dists, best_gen = data
            return route, dists, dists[-1], best_gen
        return None, [], 0.0, 0

    normalized = {}
    for name, data in results_dict.items():
        route, dists, best_dist, best_gen = normalize(name, data)
        normalized[name] = {
            "route":     route,
            "distances": dists,
            "best_dist": best_dist,
            "best_gen":  best_gen,
        }

    names = list(results_dict.keys())  # zachová poradie výberu

    # ---- Pomocná funkcia na pozadie ----
    def load_bg(ax):
        try:
            if background_path is not None:
                bg = plt.imread(background_path)
                ax.imshow(bg, extent=[0, size, 0, size], zorder=0, aspect="auto")
        except Exception:
            ax.set_facecolor("lightgray")

    # ---- Pevné rozloženie 2 riadky x 4 stĺpce ----
    # Route sloty:  [0,0] [0,1] [1,0] [1,1]
    # Konvergencia: [0,2]   Tabuľka:  [1,2]
    # Parametre:    [0,3]             [1,3]
    route_slots = [(0, 0), (0, 1), (1, 0), (1, 1)]

    fig, axs = plt.subplots(2, 4, figsize=(20, 8))
    fig.canvas.manager.set_window_title(f"{' vs '.join(names)} — TSP Comparison")

    # ---- Vykreslenie trás ----
    for idx, name in enumerate(names):
        row, col = route_slots[idx]
        ax = axs[row, col]
        load_bg(ax)
        route = normalized[name]["route"]
        xs = [coords[i][0] for i in route]
        ys = [coords[i][1] for i in route]
        ax.plot(xs, ys, "-o", color=ALGO_COLORS[name], markersize=4, linewidth=1)
        for i, (x, y) in enumerate(coords):
            ax.text(x + 2, y + 2, str(i), fontsize=8)
        ax.set_xlim(0, size)
        ax.set_ylim(0, size)
        ax.set_title(f"{name}  (Best = {normalized[name]['best_dist']:.1f})")

    # Prázdne sloty — ostanú čisté (axis off = prázdna biela plocha)
    for idx in range(len(names), 4):
        row, col = route_slots[idx]
        axs[row, col].axis("off")

    # ---- Graf konvergencie [0, 2] ----
    ax_conv = axs[0, 2]
    ax_conv.set_title("Convergence Comparison", fontsize=11, fontweight="bold")
    ax_conv.set_xlabel("Generation")
    ax_conv.set_ylabel("Best Distance")
    ax_conv.grid(True, alpha=0.3)
    for name in names:
        ax_conv.plot(normalized[name]["distances"], "-",
                     color=ALGO_COLORS[name], lw=1.8, label=name)
    ax_conv.legend(loc="upper right", fontsize=8)

    # ---- Tabuľka výsledkov [1, 2] ----
    ax_table = axs[1, 2]
    ax_table.axis("off")
    ax_table.set_title("Summary Statistics", fontsize=11, fontweight="bold")

    summary = [(n, normalized[n]["best_dist"], normalized[n]["best_gen"]) for n in names]
    winner  = min(summary, key=lambda x: x[1])

    table_data = [["Algorithm", "Distance", "Conv. Gen"]]
    for nm, d, g in summary:
        marker = "★" if nm == winner[0] else ""
        table_data.append([f"{nm} {marker}", f"{d:.2f}", str(g)])

    table = ax_table.table(cellText=table_data, cellLoc="center", loc="center",
                           colWidths=[0.35, 0.35, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    for i in range(3):
        table[(0, i)].set_facecolor("#4CAF50")
        table[(0, i)].set_text_props(weight="bold", color="white")
    for idx2, (nm, _, _) in enumerate(summary, 1):
        if nm == winner[0]:
            for i in range(3):
                table[(idx2, i)].set_facecolor("#ffffcc")

    # ---- Textové bloky parametrov pre každý algoritmus ----
    algo_params_text = {
        "ACO": (
            f"ACO:\n"
            f"Generations:    {params.get('ACO generations')}\n"
            f"Ant count:      {params.get('Ant count')}\n"
            f"Alpha:          {params.get('Alpha')}\n"
            f"Beta:           {params.get('Beta')}\n"
            f"Evap. rate:     {params.get('Evaporation rate')}\n"
            f"Q:              {params.get('Q')}"
        ),
        "GA": (
            f"GA:\n"
            f"Generations:    {params.get('GA generations')}\n"
            f"Pop. size:      {params.get('Population size')}\n"
            f"Elit rate:      {params.get('Elit rate')}\n"
            f"Mutation rate:  {params.get('Mutation rate')}"
        ),
        "ABC": (
            f"ABC:\n"
            f"Generations:    {params.get('ABC generations')}\n"
            f"Bee count:      {params.get('Bee count')}\n"
            f"Employ rate:    {params.get('employ_rate')}\n"
            f"Scout rate:     {params.get('scout_rate')}"
        ),
        "PSO": (
            f"PSO:\n"
            f"Generations:    {params.get('PSO generations')}\n"
            f"Particle count: {params.get('Particle count')}\n"
            f"c1:             {params.get('c1')}\n"
            f"c2:             {params.get('c2')}\n"
            f"Weight:         {params.get('weight')}"
        ),
        "FFA": (
            f"FFA:\n"
            f"Generations:    {params.get('FFA generations')}\n"
            f"Firefly count:  {params.get('Firefly count')}\n"
            f"Alpha:          {params.get('FFA_Alpha')}\n"
            f"Beta0:          {params.get('Beta0')}\n"
            f"Gamma:          {params.get('Gamma')}"
        ),
    }

    # Prvé 2 algoritmy → vrchný panel [0,3]
    # Zvyšné 1–2 algoritmy → spodný panel [1,3]
    group1 = names[:2]
    group2 = names[2:]

    ax_p1 = axs[0, 3]
    ax_p1.axis("off")
    if group1:
        ax_p1.set_title(f"Parameters ({' & '.join(group1)})",
                        fontsize=11, fontweight="bold")
        ax_p1.text(0.5, 0.5,
                   "\n\n".join(algo_params_text[n] for n in group1),
                   fontsize=9, ha="center", va="center", wrap=True)

    ax_p2 = axs[1, 3]
    ax_p2.axis("off")
    if group2:
        ax_p2.set_title(f"Parameters ({' & '.join(group2)})",
                        fontsize=11, fontweight="bold")
        ax_p2.text(0.5, 0.5,
                   "\n\n".join(algo_params_text[n] for n in group2),
                   fontsize=9, ha="center", va="center", wrap=True)

    plt.tight_layout()
    manager = plt.get_current_fig_manager()
    try:
        manager.window.state("zoomed")
    except Exception:
        manager.full_screen_toggle()
    plt.show()


# ==========================================================
#  TKINTER GUI
# ==========================================================
if __name__ == "__main__":
    root = tk.Tk()
    ctk.set_appearance_mode("light")
    root.title("TSP Comparison Tool")
    root.state("zoomed")
    root.configure(bg="#f0f0f0")

    main_frame = tk.Frame(root, bg="#f0f0f0")
    main_frame.pack(padx=10, pady=10)

    # ==========================================================
    #  ĽAVÁ STRANA – Canvas + Log
    # ==========================================================
    left_frame = tk.Frame(main_frame, bg="white", relief=tk.RIDGE, borderwidth=2)
    left_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

    instruction_label = tk.Label(left_frame, text="Click to Add Cities",
                                  font=("Arial", 12, "bold"), bg="white", fg="#333")
    instruction_label.pack(pady=5)

    canvas = tk.Canvas(left_frame, width=size, height=size, bg="white")
    canvas.pack()

    # Color Slider
    color_frame = tk.Frame(left_frame, bg="white")
    color_frame.pack(pady=10, padx=10, fill="x")
    tk.Label(color_frame, text="Dot Color:", font=("Arial", 9, "bold"),
             bg="white").pack(side="left", padx=(0, 10))

    def wavelength_to_rgb(wavelength):
        if wavelength >= 380 and wavelength < 440:
            r = -(wavelength - 440) / (440 - 380); g = 0.0; b = 1.0
        elif wavelength >= 440 and wavelength < 490:
            r = 0.0; g = (wavelength - 440) / (490 - 440); b = 1.0
        elif wavelength >= 490 and wavelength < 510:
            r = 0.0; g = 1.0; b = -(wavelength - 510) / (510 - 490)
        elif wavelength >= 510 and wavelength < 580:
            r = (wavelength - 510) / (580 - 510); g = 1.0; b = 0.0
        elif wavelength >= 580 and wavelength < 645:
            r = 1.0; g = -(wavelength - 645) / (645 - 580); b = 0.0
        elif wavelength >= 645 and wavelength <= 780:
            r = 1.0; g = 0.0; b = 0.0
        else:
            r = 0.0; g = 0.0; b = 0.0
        if wavelength >= 380 and wavelength < 420:
            factor = 0.3 + 0.7 * (wavelength - 380) / (420 - 380)
        elif wavelength >= 700 and wavelength <= 780:
            factor = 0.3 + 0.7 * (780 - wavelength) / (780 - 700)
        else:
            factor = 1.0
        return f"#{int(r*factor*255):02x}{int(g*factor*255):02x}{int(b*factor*255):02x}"

    def update_color(*args):
        global current_color
        current_color = wavelength_to_rgb(color_slider.get())
        color_preview.config(bg=current_color)

    color_slider = tk.Scale(color_frame, from_=380, to=780, orient="horizontal",
                             length=350, command=update_color, bg="white",
                             showvalue=False, sliderlength=20, width=15)
    color_slider.set(470)
    color_slider.pack(side="left", padx=5)
    color_preview = tk.Label(color_frame, text="", width=8, height=1,
                              bg=current_color, relief="solid", borderwidth=2)
    color_preview.pack(side="left")
    update_color()

    info_label = tk.Label(left_frame, text=f"Cities: {cities}",
                           font=("Arial", 9, "bold"), bg="white", fg="#333")
    info_label.pack(pady=(0, 0))

    log_frame = tk.Frame(left_frame, bg="white")
    log_frame.pack(pady=(0, 5))
    log_scroll = tk.Scrollbar(log_frame)
    log_scroll.pack(side="right", fill="y")
    log_box = tk.Text(log_frame, height=8, width=58, font=("Consolas", 9),
                      bg="#fafafa", fg="black", relief="solid", bd=1,
                      wrap="word", yscrollcommand=log_scroll.set)
    log_box.pack(side="left", fill="both", expand=True)
    log_scroll.config(command=log_box.yview)

    def log_message(msg, color="black"):
        log_box.config(state="normal")
        log_box.insert("end", msg + "\n", ("color",))
        log_box.tag_configure("color", foreground=color)
        log_box.see("end")
        log_box.config(state="disabled")
        root.update_idletasks()

    def clear_log():
        log_box.config(state="normal")
        log_box.delete("1.0", "end")
        log_box.insert("end", "Ready.\n", ("gray",))
        log_box.config(state="disabled")

    log_message("Ready.\n", "gray")

    # ==========================================================
    #  PRAVÁ STRANA – Hyperparametre
    # ==========================================================
    right_frame = tk.Frame(main_frame, bg="#f0f0f0")
    right_frame.grid(row=0, column=1, sticky="n")

    entry_widgets = {}  # mapa param-key → Entry widget (pre všetky algoritmy)

    # ---------- INFO POPUP FUNKCIE ----------
    def show_info_aco():
        messagebox.showinfo("ACO Parameters", """Ant Colony Optimization:
    - ACO generations: Number of iterations.
    - Ant count: Number of ants constructing paths.
    - Alpha: Influence of pheromone trail.
    - Beta: Influence of visibility (distance).
    - Evaporation rate: Rate pheromones decay.
    - Q: Pheromone deposit amount.""")

    def show_info_ga():
        messagebox.showinfo("GA Parameters", """Genetic Algorithm:
    - GA generations: Number of iterations.
    - Population size: Number of solutions per generation.
    - Elite rate: Portion of best solutions kept.
    - Mutation rate: Probability of a random swap.""")

    def show_info_abc():
        messagebox.showinfo("ABC Parameters", """Artificial Bee Colony:
    - ABC generations: Number of iterations.
    - Bee count: Total bees in the colony.
    - employ_rate: Portion of employed bees.
    - scout_rate: Chance of random exploration.""")

    def show_info_pso():
        messagebox.showinfo("PSO Parameters", """Particle Swarm Optimization:
    - PSO generations: Number of iterations.
    - Particle count: Number of candidate solutions.
    - c1: Cognitive coefficient (self-learning).
    - c2: Social coefficient (group-learning).
    - weight: Inertia controlling momentum.""")

    def show_info_ffa():
        messagebox.showinfo("FFA Parameters", """Firefly Algorithm:
    - FFA generations: Number of iterations.
    - Firefly count: Size of the firefly population.
    - FFA_Alpha: Randomness step size (0 = no randomness).
    - Beta0: Maximum attractiveness at zero distance.
    - Gamma: Light absorption (higher = less attraction range).
    - FFA_seed: Random seed for reproducibility.""")

    def round_info_button(parent, command):
        return ctk.CTkButton(
            parent, text="ℹ", width=40, height=10, corner_radius=20,
            fg_color="#2196F3", hover_color="#1976D2", text_color="white",
            font=("Arial", 10, "bold"), command=command
        )

    # ---------- PARAM FRAMES ----------
    # Všetky framy sú vytvorené raz; viditeľnosť riadi refresh_param_layout()

    # --- ACO ---
    aco_frame = tk.LabelFrame(right_frame, text="ACO Parameters",
                               font=("Arial", 11, "bold"), bg="#e8f4f8",
                               relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    aco_defaults = {
        "ACO generations": 1000,
        "Ant count": 5,
        "Alpha": 1.0,
        "Beta": 2.0,
        "Evaporation rate": 0.1,
        "Q": 100.0,
        "ACO_seed": 173,
    }
    for i, (key, default) in enumerate(aco_defaults.items()):
        tk.Label(aco_frame, text=f"{key}:", bg="#e8f4f8",
                 font=("Arial", 9)).grid(row=i, column=0, sticky="w", pady=3)
        e = tk.Entry(aco_frame, width=12, font=("Arial", 9))
        e.insert(0, str(default))
        e.grid(row=i, column=1, padx=(5, 0), pady=3)
        entry_widgets[key] = e
    round_info_button(aco_frame, show_info_aco).grid(columnspan=2, pady=5)

    # --- GA ---
    ga_frame = tk.LabelFrame(right_frame, text="GA Parameters",
                              font=("Arial", 11, "bold"), bg="#f8f4e8",
                              relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    ga_defaults = {
        "GA generations": 1000,
        "Population size": 100,
        "Elit rate": 0.25,
        "Mutation rate": 0.1,
        "GA_seed": 173,
    }
    for i, (key, default) in enumerate(ga_defaults.items()):
        tk.Label(ga_frame, text=f"{key}:", bg="#f8f4e8",
                 font=("Arial", 9)).grid(row=i, column=0, sticky="w", pady=3)
        e = tk.Entry(ga_frame, width=12, font=("Arial", 9))
        e.insert(0, str(default))
        e.grid(row=i, column=1, padx=(5, 0), pady=3)
        entry_widgets[key] = e
    round_info_button(ga_frame, show_info_ga).grid(columnspan=2, pady=5)

    # --- ABC ---
    abc_frame = tk.LabelFrame(right_frame, text="ABC Parameters",
                               font=("Arial", 11, "bold"), bg="#f8e8f4",
                               relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    abc_defaults = {
        "ABC generations": 1000,
        "Bee count": 20,
        "employ_rate": 0.7,
        "scout_rate": 0.01,
        "ABC_seed": 173,
    }
    for i, (key, default) in enumerate(abc_defaults.items()):
        tk.Label(abc_frame, text=f"{key}:", bg="#f8e8f4",
                 font=("Arial", 9)).grid(row=i, column=0, sticky="w", pady=3)
        e = tk.Entry(abc_frame, width=12, font=("Arial", 9))
        e.insert(0, str(default))
        e.grid(row=i, column=1, padx=(5, 0), pady=3)
        entry_widgets[key] = e
    round_info_button(abc_frame, show_info_abc).grid(columnspan=2, pady=5)

    # --- PSO ---
    pso_frame = tk.LabelFrame(right_frame, text="PSO Parameters",
                               font=("Arial", 11, "bold"), bg="#e8f8f4",
                               relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    pso_defaults = {
        "PSO generations": 1000,
        "Particle count": 10,
        "c1": 1.5,
        "c2": 1.5,
        "weight": 0.9,
        "PSO_seed": 173,
    }
    for i, (key, default) in enumerate(pso_defaults.items()):
        tk.Label(pso_frame, text=f"{key}:", bg="#e8f8f4",
                 font=("Arial", 9)).grid(row=i, column=0, sticky="w", pady=3)
        e = tk.Entry(pso_frame, width=12, font=("Arial", 9))
        e.insert(0, str(default))
        e.grid(row=i, column=1, padx=(5, 0), pady=3)
        entry_widgets[key] = e
    round_info_button(pso_frame, show_info_pso).grid(columnspan=2, pady=5)

    # --- FFA ---
    # Pozor: kľúč "FFA_Alpha" — odlišný od ACO "Alpha" aby nedošlo ku konfliktu.
    # BP2_FFA.py musí čítať params.get("FFA_Alpha", 0.2)  nie  params.get("Alpha", 0.2)
    ffa_frame = tk.LabelFrame(right_frame, text="FFA Parameters",
                               font=("Arial", 11, "bold"), bg="#fff3e0",
                               relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    ffa_defaults = {
        "FFA generations": 1000,
        "Firefly count": 30,
        "FFA_Alpha": 0.2,
        "Beta0": 1.0,
        "Gamma": 1.0,
        "FFA_seed": 173,
    }
    for i, (key, default) in enumerate(ffa_defaults.items()):
        tk.Label(ffa_frame, text=f"{key}:", bg="#fff3e0",
                 font=("Arial", 9)).grid(row=i, column=0, sticky="w", pady=3)
        e = tk.Entry(ffa_frame, width=12, font=("Arial", 9))
        e.insert(0, str(default))
        e.grid(row=i, column=1, padx=(5, 0), pady=3)
        entry_widgets[key] = e
    round_info_button(ffa_frame, show_info_ffa).grid(columnspan=2, pady=5)

    # ==========================================================
    #  CONTROLS
    # ==========================================================
    controls_frame = tk.LabelFrame(right_frame, text="Controls",
                                    font=("Arial", 11, "bold"), bg="#f0f0f0",
                                    relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    controls_frame.columnconfigure(0, weight=1)
    controls_frame.columnconfigure(1, weight=1)

    # Mapa názov algoritmu → frame objekt
    ALL_ALGO_NAMES = ["ACO", "GA", "ABC", "PSO", "FFA"]
    algo_frame_map = {
        "ACO": aco_frame,
        "GA":  ga_frame,
        "ABC": abc_frame,
        "PSO": pso_frame,
        "FFA": ffa_frame,
    }

    # Sloty v gridu right_frame — poradie vypĺňania (ľavý stĺpec prvý)
    GRID_SLOTS = [(0, 0), (1, 0), (0, 1), (1, 1)]

    # Aktuálne vybrané algoritmy (lowercase)
    selected_algorithms = ["aco", "ga", "abc", "pso"]  # predvolené

    # ------------------------------------------------------------------
    #  refresh_param_layout — zobrazí len framy vybraných algoritmov
    # ------------------------------------------------------------------
    def refresh_param_layout():
        """Skryje všetky param-framy a znovu zobrazí len vybrané v poradí slotov."""
        for frame in algo_frame_map.values():
            frame.grid_remove()

        for idx, name in enumerate(selected_algorithms):
            row, col = GRID_SLOTS[idx]
            algo_frame_map[name.upper()].grid(row=row, column=col,
                                               padx=5, pady=5, sticky="n")

        # Controls frame tesne pod poslednou obsadenou zeradkou
        used_rows = [GRID_SLOTS[i][0] for i in range(len(selected_algorithms))]
        max_row   = max(used_rows) if used_rows else 0
        controls_frame.grid(row=max_row + 1, column=0, columnspan=2,
                             pady=(10, 0), sticky="ew")

    # Prvotné rozloženie
    refresh_param_layout()

    # ------------------------------------------------------------------
    #  open_algorithm_selector — farebný modálny popup
    # ------------------------------------------------------------------
    ALGO_UI_COLORS = {           # pozadie checkboxu = farba param framu
        "ACO": "#e8f4f8",
        "GA":  "#f8f4e8",
        "ABC": "#f8e8f4",
        "PSO": "#e8f8f4",
        "FFA": "#fff3e0",
    }

    def open_algorithm_selector():
        popup = tk.Toplevel(root)
        popup.title("Select Algorithms")
        popup.resizable(False, False)
        popup.grab_set()  # modálne — blokuje hlavné okno
        popup.configure(bg="#f0f0f0")

        tk.Label(popup, text="Select algorithms to compare",
                 font=("Arial", 13, "bold"), bg="#f0f0f0").pack(pady=(12, 2))
        tk.Label(popup, text="Minimum: 1  ·  Maximum: 4",
                 font=("Arial", 9), bg="#f0f0f0", fg="#666").pack(pady=(0, 8))

        vars_dict = {
            algo: tk.BooleanVar(value=(algo in selected_algorithms))
            for algo in [a.lower() for a in ALL_ALGO_NAMES]
        }

        # Živé počítadlo vybraných
        count_label = tk.Label(popup, text="", font=("Arial", 10, "bold"), bg="#f0f0f0")

        def update_count(*_):
            n = sum(v.get() for v in vars_dict.values())
            count_label.config(
                text=f"{n} / 4 selected",
                fg="#2e7d32" if 1 <= n <= 4 else "red"
            )

        # Checkboxy s farebnými riadkami
        cb_frame = tk.Frame(popup, bg="#f0f0f0")
        cb_frame.pack(padx=25, pady=2)

        for algo in [a.lower() for a in ALL_ALGO_NAMES]:
            bg = ALGO_UI_COLORS[algo.upper()]
            row_f = tk.Frame(cb_frame, bg=bg, relief="groove", borderwidth=1)
            row_f.pack(fill="x", pady=3, ipady=5, ipadx=8)
            vars_dict[algo].trace_add("write", update_count)
            tk.Checkbutton(row_f, text=f"  {algo.upper()}", variable=vars_dict[algo],
                           font=("Arial", 11), bg=bg,
                           activebackground=bg).pack(anchor="w")

        count_label.pack(pady=8)
        update_count()  # nastavenie správneho počtu hneď po otvorení

        def apply_selection():
            chosen = [k for k, v in vars_dict.items() if v.get()]
            if len(chosen) < 1:
                messagebox.showwarning("Selection Error",
                                       "Please select at least 1 algorithm.",
                                       parent=popup)
                return
            if len(chosen) > 4:
                messagebox.showwarning("Selection Error",
                                       "Maximum is 4 algorithms.",
                                       parent=popup)
                return

            selected_algorithms.clear()
            selected_algorithms.extend(chosen)

            refresh_param_layout()  # okamžitá aktualizácia hlavného okna

            popup.destroy()
            log_message(
                f"Algorithms: {', '.join(a.upper() for a in selected_algorithms)}",
                "blue"
            )

        tk.Button(popup, text="✔  Apply", command=apply_selection,
                  bg="#4CAF50", fg="white", font=("Arial", 11, "bold"),
                  width=14, relief="flat").pack(pady=(0, 14))

        # Vycentrovanie popupu
        popup.update_idletasks()
        pw = popup.winfo_reqwidth()
        ph = popup.winfo_reqheight()
        popup.geometry(
            f"{pw}x{ph}"
            f"+{root.winfo_x() + root.winfo_width()  // 2 - pw // 2}"
            f"+{root.winfo_y() + root.winfo_height() // 2 - ph // 2}"
        )

    # ==========================================================
    #  LOG QUEUE — thread-safe logging
    # ==========================================================
    log_queue = queue.Queue()

    def poll_log_queue():
        try:
            root.winfo_exists()
        except tk.TclError:
            return
        while True:
            try:
                msg, color = log_queue.get_nowait()
                log_message(msg, color)
            except queue.Empty:
                break
        root.after(100, poll_log_queue)

    def thread_log(msg, color="black"):
        log_queue.put((msg, color))

    # ==========================================================
    #  on_enter — spustenie simulácie
    # ==========================================================
    def on_enter():
        if len(cords) < 3:
            messagebox.showwarning("Not Enough Cities",
                                   "Please add at least 3 cities before running.")
            return
        if not selected_algorithms:
            messagebox.showwarning("No Algorithms",
                                   "Select at least 1 algorithm via 'Select Algorithms'.")
            return

        # Zbieranie parametrov zo všetkých entry widgetov
        params = {}
        for k, v in entry_widgets.items():
            raw = v.get()
            try:
                params[k] = float(raw) if "." in raw else int(raw)
            except ValueError:
                messagebox.showerror("Invalid Parameter",
                                     f"Invalid value for '{k}': '{raw}'")
                return

        clear_log()

        results = {algo: None for algo in selected_algorithms}
        errors  = {algo: None for algo in selected_algorithms}

        algo_functions = {
            "aco": BP2_ACO.ACO,
            "ga":  BP2_GA.GA,
            "abc": BP2_ABC.ABC,
            "pso": BP2_PSO.PSO,
            "ffa": BP2_FFA.FFA,
        }

        def make_runner(algo):
            """Vráti thread-funkciu pre daný algoritmus (closure)."""
            func  = algo_functions[algo]
            label = algo.upper()
            def run():
                thread_log(f"Running {label}...", "blue")
                try:
                    start = time.time()
                    results[algo] = func(cords, params)
                    elapsed = round(time.time() - start, 2)
                    thread_log(f"{label} finished successfully ✅  — {elapsed}s", "green")
                except ZeroDivisionError:
                    errors[algo] = "ZeroDivisionError"
                    thread_log(f"{label} ❌ — Two cities share the same position!", "red")
                except Exception as e:
                    errors[algo] = str(e)
                    thread_log(f"{label} ❌ failed — {e}", "red")
            return run

        def orchestrate():
            run_btn.config(state="disabled")

            threads = [
                threading.Thread(target=make_runner(algo), daemon=True)
                for algo in selected_algorithms
            ]

            overall_start = time.time()
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            total  = round(time.time() - overall_start, 2)
            failed = [a.upper() for a in selected_algorithms if errors[a] is not None]

            if failed:
                thread_log(
                    f"\nCompleted with errors in {total}s. Failed: {', '.join(failed)}",
                    "red"
                )
                thread_log("Fix the issues above and press Reset before retrying.", "red")
                run_btn.config(state="normal")
                return

            thread_log(
                f"\nAll algorithms finished in {total}s — displaying results...", "green"
            )
            root.after(0, lambda: _show_results(results, params))
            run_btn.config(state="normal")

        def _show_results(res, prm):
            try:
                # Uppercase kľúče pre display_comparison; preskočiť None výsledky
                selected_res = {
                    algo.upper(): res[algo]
                    for algo in selected_algorithms
                    if res[algo] is not None
                }
                display_comparison(cords, selected_res, prm)
                log_message("Results displayed successfully ✅", "green")
            except Exception as e:
                log_message(f"Results display failed ❌ — {e}", "red")

        threading.Thread(target=orchestrate, daemon=True).start()

    # ==========================================================
    #  OSTATNÉ FUNKCIE (Canvas, Generate, Reset, Background)
    # ==========================================================
    def upload_background():
        global background_path, bg_preview, bg_image_id
        path = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif")]
        )
        if path:
            background_path = path
            img = Image.open(path).resize((size, size))
            bg_preview = ImageTk.PhotoImage(img)
            if bg_image_id:
                canvas.delete(bg_image_id)
            bg_image_id = canvas.create_image(0, 0, anchor="nw", image=bg_preview)
            canvas.tag_lower(bg_image_id)

    def on_click(event):
        global cities
        x, y = event.x, event.y
        r = 6
        dot_id  = canvas.create_oval(x - r, y - r, x + r, y + r,
                                      fill=current_color, tags="city")
        text_id = canvas.create_text(x, y - 15, text=cities,
                                      tags="city", font=("Arial", 8))
        cords.append((x, size - y))
        city_shapes.append((dot_id, text_id))
        cities += 1
        info_label.config(text=f"Cities: {cities}")

    def undo(event=None):
        global cities
        if city_shapes:
            dot_id, text_id = city_shapes.pop()
            canvas.delete(dot_id)
            canvas.delete(text_id)
            cords.pop()
            cities -= 1
            info_label.config(text=f"Cities: {cities}")
            canvas.update()
        else:
            messagebox.showinfo("Undo", "No more cities to remove!")

    def generate_random_cities():
        global cities
        reset()
        try:
            n = int(generate_entry.get())
            if n < 3:
                messagebox.showwarning("Too Few Cities", "Please enter at least 3 cities.")
                return
            if n > 2500:
                messagebox.showwarning("Too Many Cities", "Maximum is 2500 cities.")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer.")
            return
        r = 6
        for _ in range(n):
            while True:
                x = random.randint(r, size - r)
                y = random.randint(r, size - r)
                if (x, size - y) not in cords:
                    break
            dot_id  = canvas.create_oval(x - r, y - r, x + r, y + r,
                                          fill=current_color, tags="city")
            text_id = canvas.create_text(x, y - 15, text=cities,
                                          tags="city", font=("Arial", 8))
            cords.append((x, size - y))
            city_shapes.append((dot_id, text_id))
            cities += 1
        info_label.config(text=f"Cities: {cities}")

    def reset():
        global cities, bg_preview, bg_image_id, background_path
        canvas.delete("city")
        if bg_image_id:
            canvas.delete(bg_image_id)
            bg_image_id = None
        background_path = None
        bg_preview = None
        cords.clear()
        city_shapes.clear()
        cities = 0
        clear_log()
        info_label.config(text=f"Cities: {cities}")

    # ==========================================================
    #  BUTTONS v controls_frame
    # ==========================================================
    button_style = {"font": ("Arial", 10, "bold"), "width": 20, "height": 1}

    run_btn = tk.Button(controls_frame, text="▶  Run Comparison",
                         command=on_enter, bg="#4CAF50", fg="white", **button_style)
    run_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    tk.Button(controls_frame, text="⚙  Select Algorithms",
              command=open_algorithm_selector,
              bg="#9C27B0", fg="white", **button_style).grid(
              row=0, column=1, padx=5, pady=5, sticky="ew")

    tk.Button(controls_frame, text="Upload Background",
              command=upload_background,
              bg="#2196F3", fg="white", **button_style).grid(
              row=1, column=0, padx=5, pady=5, sticky="ew")

    tk.Button(controls_frame, text="Reset Cities",
              command=reset,
              bg="#f44336", fg="white", **button_style).grid(
              row=1, column=1, padx=5, pady=5, sticky="ew")

    generate_frame = tk.Frame(controls_frame, bg="#f0f0f0")
    generate_frame.grid(row=2, column=0, columnspan=2, pady=5)

    tk.Label(generate_frame, text="Points:", font=("Arial", 9, "bold"),
             bg="#f0f0f0").pack(side="left", padx=(0, 5))
    generate_entry = tk.Entry(generate_frame, width=6, font=("Arial", 9))
    generate_entry.insert(0, "20")
    generate_entry.pack(side="left", padx=(0, 5))
    tk.Button(generate_frame, text="Generate Random",
              command=generate_random_cities,
              bg="#FF9800", fg="white",
              font=("Arial", 10, "bold"), height=1).pack(side="left")

    city_shapes = []
    canvas.bind("<Button-3>", undo)
    canvas.bind("<Button-1>", on_click)

    def on_close():
        root.after_cancel  # cancels pending after callbacks
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    poll_log_queue()
    root.mainloop()