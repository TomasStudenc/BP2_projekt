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
import BP2_CSA # CSA algoritmus
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

# holdery na výsledky simulácií
ant_count         = 0  # velkosť populácie pri ACO
pop_size          = 0  # velkosť populácie pri GA
bee_count         = 0  # velkosť populácie pri ABC
particle_count    = 0  # velkosť populácie pri PSO
firefly_count     = 0  # velkosť populácie pri FFA
nest_count        = 0  # veľkosť populácie pri CSA
best_tour_gen_csa = 0  # najlepšia generácia pri CSA
best_tour_gen_aco = 0  # najlepšia generácia pri ACO
best_tour_gen_ga  = 0  # najlepšia generácia pre GA
best_tour_gen_abc = 0  # najlepšia generácia pri ABC
best_tour_gen_pso = 0  # najlepšia generácia pri PSO
best_tour_gen_ffa = 0  # najlepšia generácia pri FFA

current_color = "#FF6B00"  # predvolená farba vrcholov

# Farebná paleta pre každý algoritmus (konzistentná v celom programe)
ALGO_COLORS = {
    "ACO": "red",
    "GA":  "green",
    "ABC": "magenta",
    "PSO": "blue",
    "FFA": "darkorange",
    "CSA": "cyan",
}

#definovanie farieb pre light a dark mód pre matplot okno
MATPLOTLIB_THEMES = {
    "dark": {
        "axes.facecolor": "#1e1e1e",
        "figure.facecolor": "#1e1e1e",
        "axes.edgecolor": "white",
        "axes.labelcolor": "white",
        "xtick.color": "white",
        "ytick.color": "white",
        "text.color": "white",
        "grid.color": "#555555",
        "savefig.facecolor": "#1e1e1e",
        "savefig.edgecolor": "#1e1e1e",
        "legend.facecolor": "#2b2b2b",
        "legend.edgecolor": "white",
    },
    "light": {
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "axes.edgecolor": "black",
        "axes.labelcolor": "black",
        "xtick.color": "black",
        "ytick.color": "black",
        "text.color": "black",
        "grid.color": "#cccccc",
        "savefig.facecolor": "white",
        "savefig.edgecolor": "white",
        "legend.facecolor": "white",
        "legend.edgecolor": "black",
    }
}
#definovanie farieb pre light a dark mód pre hlavné GUI
THEMES = {
    "dark": {
        "bg_main": "#2b2b2b",
        "bg_frame": "#3a3a3a",
        "bg_left": "#1e1e1e",
        "bg_canvas": "#1e1e1e",
        "text": "white",
        "log_bg": "#111111"
    },
    "light": {
        "bg_main": "#f0f0f0",
        "bg_frame": "#ffffff",
        "bg_left": "#ffffff",
        "bg_canvas": "white",
        "text": "black",
        "log_bg": "#fafafa"
    }
}
#definovanie farieb pre light a dark mód pre pozadie algorithm frame
ALGO_FRAME_COLORS = {
    "dark": {
        "CSA": "#12343f",
        "ACO": "#14333f",
        "GA": "#3f3414",
        "ABC": "#3f1434",
        "PSO": "#143f34",
        "FFA": "#3f2a14",
        "CONTROLS": "#303030",
    },
    "light": {
        "CSA": "#d9f2ff",
        "ACO": "#d9faff",
        "GA": "#fff2c2",
        "ABC": "#ffd9ef",
        "PSO": "#d9fff2",
        "FFA": "#ffe6c2",
        "CONTROLS": "#f2f2f2",
    }
}
#definovanie farieb pre light a dark mód pre buttony v control frame
CONTROL_BUTTON_COLORS = {
    "dark": {
        "reset":   {"fg": "#b71c1c", "hover": "#7f0000", "text": "white"},
        "change":  {"fg": "#6a1b9a", "hover": "#38006b", "text": "white"},
        "start":   {"fg": "#1b5e20", "hover": "#003300", "text": "white"},
        "applybg": {"fg": "#f9a825", "hover": "#c17900", "text": "black"},
    },
    "light": {
        "reset":   {"fg": "#e53935", "hover": "#ab000d", "text": "white"},
        "change":  {"fg": "#8e24aa", "hover": "#5c007a", "text": "white"},
        "start":   {"fg": "#43a047", "hover": "#00701a", "text": "white"},
        "applybg": {"fg": "#ffeb3b", "hover": "#fdd835", "text": "black"},
    }
}

matplotlib.rcParams.update(MATPLOTLIB_THEMES["dark"])
# ==========================================================
#  Zobrazovanie výsledkov — dynamické pre 1 až 4 algoritmy
# ==========================================================
def display_comparison(coords, results_dict, params):
    matplotlib.use("TkAgg")

    #normalizovanie výsledkov
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
        elif name == "CSA":
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

    route_slots = [(0, 0), (0, 1), (1, 0), (1, 1)]
    fig, axs = plt.subplots(2, 4, figsize=(20, 8))
    fig.canvas.manager.set_window_title(f"{' vs '.join(names)} — TSP Comparison")

    #vykreslovanie trás
    for idx, name in enumerate(names):
        row, col = route_slots[idx]
        ax = axs[row, col]
        route = normalized[name]["route"]
        xs = [coords[i][0] for i in route]
        ys = [coords[i][1] for i in route]
        ax.plot(xs, ys, "-o", color=ALGO_COLORS[name], markersize=4, linewidth=1)
        for i, (x, y) in enumerate(coords):
            ax.text(x + 2, y + 2, str(i), fontsize=8, color=matplotlib.rcParams["text.color"])
        ax.set_xlim(0, size)
        ax.set_ylim(0, size)
        ax.set_title(
            f"{name}  (Best = {normalized[name]['best_dist']:.1f})",
            color=matplotlib.rcParams["text.color"]
        )
        ax.set_xticks([])
        ax.set_yticks([])

    #ak je menej ako 4 algoritmi vykresluje prázne sloty
    for idx in range(len(names), 4):
        row, col = route_slots[idx]
        axs[row, col].set_facecolor(matplotlib.rcParams["axes.facecolor"])
        axs[row, col].axis("off")

    #graf konvergencie
    ax_conv = axs[0, 2]
    ax_conv.set_title("Convergence Comparison", fontsize=11, fontweight="bold")
    ax_conv.set_xlabel("Generation")
    ax_conv.set_ylabel("Best Distance")
    ax_conv.grid(True, color=matplotlib.rcParams["grid.color"], alpha=0.3)
    for name in names:
        ax_conv.plot(normalized[name]["distances"], "-",
                     color=ALGO_COLORS[name], lw=1.8, label=name)
    ax_conv.legend(loc="upper right", fontsize=8)

    #tabulka výsledkov simulácií
    ax_table = axs[1, 2]
    ax_table.axis("off")
    ax_table.set_title("Summary Statistics", fontsize=11, fontweight="bold")

    summary = [(n, normalized[n]["best_dist"], normalized[n]["best_gen"]) for n in names]
    winner = min(summary, key=lambda x: x[1])

    table_data = [["Algorithm", "Distance", "Conv. Gen"]]
    for nm, d, g in summary:
        marker = "★" if nm == winner[0] else ""
        table_data.append([f"{nm} {marker}", f"{d:.2f}", str(g)])

    #vytvorenie tabulky
    table = ax_table.table(
        cellText=table_data,
        cellLoc="center",
        loc="center",
        colWidths=[0.35, 0.35, 0.3]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    #definovanie farieb bodla theme
    header_bg = "#4CAF50" if current_theme == "light" else "#2e7d32"
    header_fg = "black" if current_theme == "light" else "white"
    highlight = "#ffffcc" if current_theme == "light" else "#333333"
    text_color = matplotlib.rcParams["text.color"]
    cell_bg = matplotlib.rcParams["axes.facecolor"]

    for i in range(3):
        table[(0, i)].set_facecolor(header_bg)
        table[(0, i)].set_text_props(weight="bold", color=header_fg)

    for idx2, (nm, _, _) in enumerate(summary, 1):
        for i in range(3):
            table[(idx2, i)].set_facecolor(cell_bg)
            table[(idx2, i)].set_text_props(color=text_color)

        if nm == winner[0]:
            for i in range(3):
                table[(idx2, i)].set_facecolor(highlight)

    #hyperparametre algoritmov vypísané v matplot lib
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
        "CSA": (
        f"CSA:\n"
        f"Generations:    {params.get('CSA generations')}\n"
        f"Nest count:     {params.get('Nest count')}\n"
        f"pa:             {params.get('CSA_pa')}\n"
        f"Beta:           {params.get('CSA_beta')}\n"
        f"Step size:      {params.get('CSA_step')}"
    ),
    }

    group1 = names[:2]
    group2 = names[2:]

    ax_p1 = axs[0, 3]
    ax_p1.set_facecolor(matplotlib.rcParams["axes.facecolor"])
    if group1:
        ax_p1.set_title(f"Parameters ({' & '.join(group1)})",
                        fontsize=11, fontweight="bold")
        ax_p1.text(0.5, 0.5,
                   "\n\n".join(algo_params_text[n] for n in group1),
                   fontsize=9, ha="center", va="center", wrap=True)
    ax_p1.set_xticks([])
    ax_p1.set_yticks([])
    ax_p2 = axs[1, 3]
    ax_p2.set_facecolor(matplotlib.rcParams["axes.facecolor"])
    if group2:
        ax_p2.set_title(f"Parameters ({' & '.join(group2)})",
                        fontsize=11, fontweight="bold")
        ax_p2.text(0.5, 0.5,
                   "\n\n".join(algo_params_text[n] for n in group2),
                   fontsize=9, ha="center", va="center", wrap=True)
    ax_p2.set_xticks([])
    ax_p2.set_yticks([])

    plt.tight_layout(pad=0.2, w_pad=1.25, h_pad=0.3)
    manager = plt.get_current_fig_manager()
    try:
        manager.window.state("zoomed")
    except Exception:
        manager.full_screen_toggle()
    plt.show()


# ==========================================================
#  TKINTER GUI
# ==========================================================
#main používatelské rozhranie ktoré zabezpečuje interaktívne GUI spúštanie simulácií a nastavovanie parametrov
if __name__ == "__main__":
    root = tk.Tk()
    ctk.set_appearance_mode("dark")
    root.title("TSP Comparison Tool")
    root.state("zoomed")
    root.configure(bg="#f0f0f0")

    main_frame = tk.Frame(root, bg="#f0f0f0")
    main_frame.pack(padx=10, pady=10)
    current_theme = "dark" #nastavenei default mód na dark

    #funkcia ktorá zabezpečuje že po zmene témi obrazovky sa aplikujú správne farby
    def apply_theme():
        theme = THEMES[current_theme]
        frame_colors = ALGO_FRAME_COLORS[current_theme]

        # main layout
        root.configure(bg=theme["bg_main"])
        main_frame.configure(bg=theme["bg_main"])
        left_frame.configure(bg=theme["bg_left"])
        right_frame.configure(bg=theme["bg_main"])
        canvas.configure(bg=theme["bg_canvas"])

        # labels
        instruction_label.configure(bg=theme["bg_left"], fg=theme["text"])
        info_label.configure(bg=theme["bg_left"], fg=theme["text"])

        # log
        log_frame.configure(bg=theme["bg_left"])
        log_box.configure(
            bg=theme["log_bg"],
            fg=theme["text"],
            insertbackground=theme["text"]
        )

        # frames
        frames = [
            (csa_frame, "CSA"),
            (aco_frame, "ACO"),
            (ga_frame, "GA"),
            (abc_frame, "ABC"),
            (pso_frame, "PSO"),
            (ffa_frame, "FFA"),
            (controls_frame, "CONTROLS"),
        ]

        for frame, key in frames:
            bg = frame_colors[key]
            frame.configure(bg=bg, fg=theme["text"])

            for widget in frame.winfo_children():
                if isinstance(widget, tk.Label):
                    widget.configure(bg=bg, fg=theme["text"])
                elif isinstance(widget, tk.Entry):
                    widget.configure(
                        bg="#222222" if current_theme == "dark" else "white",
                        fg=theme["text"],
                        insertbackground=theme["text"]
                    )
                elif isinstance(widget, tk.Button):
                    widget.configure(
                        bg=bg,
                        fg=theme["text"],
                        activebackground=bg,
                        activeforeground=theme["text"]
                    )
                elif isinstance(widget, ctk.CTkButton):
                    widget.configure(
                        fg_color="#1976D2" if current_theme == "light" else "#0d47a1",
                        hover_color="#125ea8" if current_theme == "light" else "#08306b",
                        text_color="white"
                    )
        # --- CONTROL PANEL BUTTON COLORS ---
        btn_colors = CONTROL_BUTTON_COLORS[current_theme]

        # --- CONTROL BUTTON COLORS ---
        if current_theme == "dark":
            run_btn.configure(bg="#1b5e20", fg="white", activebackground="#003300", activeforeground="white")
            change_algo_button.configure(bg="#6a1b9a", fg="white", activebackground="#38006b", activeforeground="white")
            reset_button.configure(bg="#b71c1c", fg="white", activebackground="#7f0000", activeforeground="white")
        else:
            run_btn.configure(bg="#43a047", fg="white", activebackground="#00701a", activeforeground="white")
            change_algo_button.configure(bg="#8e24aa", fg="white", activebackground="#5c007a", activeforeground="white")
            reset_button.configure(bg="#e53935", fg="white", activebackground="#ab000d", activeforeground="white")

    #prepínač medzi svetlím a tmavým módom
    def toggle_theme():
        global current_theme

        if theme_switch.get() == 1:
            current_theme = "dark"
            ctk.set_appearance_mode("dark")
        else:
            current_theme = "light"
            ctk.set_appearance_mode("light")

        # Apply Tkinter theme
        apply_theme()

        # Apply Matplotlib theme
        import matplotlib as mpl
        mpl.rcParams.update(MATPLOTLIB_THEMES[current_theme])
        plt.close("all")

    theme_switch = ctk.CTkSwitch(
        root,
        text="Dark Mode",
        command=toggle_theme
    )
    theme_switch.select()
    theme_switch.place(relx=0.98, rely=0.02, anchor="ne")
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
    #funkcia na záznami v logu boxe
    def log_message(msg, color="black"):
        log_box.config(state="normal")
        log_box.insert("end", msg + "\n", ("color",))
        log_box.tag_configure("color", foreground=color)
        log_box.see("end")
        log_box.config(state="disabled")
        root.update_idletasks()
    #funkcia na čistenie logu
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
    # text pre info buton pre aco
    def show_info_aco():
        messagebox.showinfo("ACO Parameters\n Ant Colony Optimization", """Ant Colony Optimization:
    - ACO generations: Number of iterations.
    - Ant count: Number of ants constructing paths.
    - Alpha: Influence of pheromone trail.
    - Beta: Influence of visibility (distance).
    - Evaporation rate: Rate pheromones decay.
    - Q: Pheromone deposit amount.""")
    # text pre info buton pre ga
    def show_info_ga():
        messagebox.showinfo("GA Parameters", """Genetic Algorithm:
    - GA generations: Number of iterations.
    - Population size: Number of solutions per generation.
    - Elite rate: Portion of best solutions kept.
    - Mutation rate: Probability of a random swap.""")
    # text pre info buton pre abc
    def show_info_abc():
        messagebox.showinfo("ABC Parameters", """Artificial Bee Colony:
    - ABC generations: Number of iterations.
    - Bee count: Total bees in the colony.
    - employ_rate: Portion of employed bees.
    - scout_rate: Chance of random exploration.""")
    # text pre info buton pre pso
    def show_info_pso():
        messagebox.showinfo("PSO Parameters", """Particle Swarm Optimization:
    - PSO generations: Number of iterations.
    - Particle count: Number of candidate solutions.
    - c1: Cognitive coefficient (self-learning).
    - c2: Social coefficient (group-learning).
    - weight: Inertia controlling momentum.""")
    # text pre info buton pre ffa
    def show_info_ffa():
        messagebox.showinfo("FFA Parameters", """Firefly Algorithm:
    - FFA generations: Number of iterations.
    - Firefly count: Size of the firefly population.
    - FFA_Alpha: Randomness step size (0 = no randomness).
    - Beta0: Maximum attractiveness at zero distance.
    - Gamma: Light absorption (higher = less attraction range).
    - FFA_seed: Random seed for reproducibility.""")

    #text pre info buton pre csa
    def show_info_csa():
        messagebox.showinfo("CSA Parameters", """Cuckoo Search Algorithm:
    - CSA generations: Number of iterations.
    - Nest count: Number of nests (population size).
    - CSA_pa: Probability of discovering a foreign egg (0–1).
    - CSA_beta: Shape of Lévy distribution (1–3).
    - CSA_step: Step size scaling for Lévy flight.
    - CSA_seed: Random seed for reproducibility.""")
    def round_info_button(parent, command):
        return ctk.CTkButton(
            parent, text="ℹ", width=40, height=10, corner_radius=20,
            fg_color="#2196F3", hover_color="#1976D2", text_color="white",
            font=("Arial", 10, "bold"), command=command
        )

    # ---------- PARAM FRAMES ----------
    # --- CSA ---
    #vytvorenie param framu pre csa
    csa_frame = tk.LabelFrame(right_frame, text="Cuckoo Search Algorithm", font=("Arial", 11, "bold"), bg="#e8f4f8", relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    # default nastavenei parametrov pre csa
    csa_defaults = {
        "CSA generations": 1000,
        "Nest count": 30,
        "CSA_pa": 0.25,
        "CSA_beta": 1.5,
        "CSA_step": 0.3,
        "CSA_seed": 173,
    }
    for i, (key, default) in enumerate(csa_defaults.items()):
        tk.Label(csa_frame, text=f"{key}:", bg="#e8f4f8",
                 font=("Arial", 9)).grid(row=i, column=0, sticky="w", pady=3)
        e = tk.Entry(csa_frame, width=12, font=("Arial", 9))
        e.insert(0, str(default))
        e.grid(row=i, column=1, padx=(5, 0), pady=3)
        entry_widgets[key] = e
    round_info_button(csa_frame, show_info_csa).grid(columnspan=2, pady=5)

    # --- ACO ---
    #vytvorenei param framu pre aco
    aco_frame = tk.LabelFrame(right_frame, text="Ant Colony Optimization", font=("Arial", 11, "bold"), bg="#e8f4f8", relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    # default nastavenei parametrov pre aco
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
    #vytvorenie param framu pre ga
    ga_frame = tk.LabelFrame(right_frame, text="Genetic Algorithm", font=("Arial", 11, "bold"), bg="#f8f4e8", relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    # default nastavenei parametrov pre ga
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
    #vytvorenie param framu pre abc
    abc_frame = tk.LabelFrame(right_frame, text="Artificial Bee Colony", font=("Arial", 11, "bold"), bg="#f8e8f4", relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    # default nastavenei parametrov pre abc
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
    #vytvorenie param framu pre pso
    pso_frame = tk.LabelFrame(right_frame, text="Particle Swarm Optimization", font=("Arial", 11, "bold"), bg="#e8f8f4", relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    # default nastavenei parametrov pre pso
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
    #vytvorenie param framu pre ffa
    ffa_frame = tk.LabelFrame(right_frame, text="Firefly Algorithm",font=("Arial", 11, "bold"), bg="#fff3e0", relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    #default nastavenei parametrov pre ffa
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
    ALL_ALGO_NAMES = ["ACO", "GA", "ABC", "PSO", "FFA", "CSA"]
    algo_frame_map = {
        "ACO": aco_frame,
        "GA":  ga_frame,
        "ABC": abc_frame,
        "PSO": pso_frame,
        "FFA": ffa_frame,
        "CSA": csa_frame,
    }

    # Sloty v gridu right_frame — poradie vypĺňania (ľavý stĺpec prvý)
    GRID_SLOTS = [(0, 0), (1, 0), (0, 1), (1, 1)]

    # Aktuálne vybrané algoritmy (lowercase)
    selected_algorithms = ["aco", "ga", "abc", "pso"]  # predvolené
    #funckia na zobrazovanie param framov len pre vybraté algoritmi
    def refresh_param_layout():
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
    # pozadie checkboxu
    ALGO_UI_COLORS = {
        "ACO": "#e8f4f8",
        "GA":  "#f8f4e8",
        "ABC": "#f8e8f4",
        "PSO": "#e8f8f4",
        "FFA": "#fff3e0",
        "CSA": "#e8f8f4",
    }
    #funckia riadiaca vyberani algoritmov zo zoznamu
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
        #funckai na výber algoritmov z zoznamu
        def apply_selection():
            chosen = [k for k, v in vars_dict.items() if v.get()]
            #musí byť viac ako jeden vybratý
            if len(chosen) < 1:
                messagebox.showwarning("Selection Error",
                                       "Please select at least 1 algorithm.",
                                       parent=popup)
                return
            #max 4 na porovnanie
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
    #funkcia zabezpečujúca logovanie v multitread systéme
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
    #funckcia na pushovanie výsledkov do log queue
    def thread_log(msg, color="black"):
        log_queue.put((msg, color))

    #funckia na spúštanie simulácií
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
        #holdery na výsledky a errory do logov
        results = {algo: None for algo in selected_algorithms}
        errors  = {algo: None for algo in selected_algorithms}

        #pridradenei funkcí algoritmom, vyberá zo súboru
        algo_functions = {
            "aco": BP2_ACO.ACO,
            "ga":  BP2_GA.GA,
            "abc": BP2_ABC.ABC,
            "pso": BP2_PSO.PSO,
            "ffa": BP2_FFA.FFA,
            "csa": BP2_CSA.CSA,
        }

        #funkcia na vyberanie thread funckae pre vybraté algoritmi
        def make_runner(algo):
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

        #funkcia na vytvorenei samostaných threadov
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

        #funkcia na zobrazovanie výsledkov sysmulácií a zápis do logu
        def _show_results(res, prm):
            try:
                # Uppercase kľúče pre display_comparison;
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
    #funkcia na pridávanie vrcholov do kreslacej plochy
    def on_click(event):
        global cities
        x, y = event.x, event.y
        new_coord = (x, size - y)

        # Check if a city already exists at this position (within 12px radius)
        r = 6
        for coord in cords:
            existing_x = coord[0]
            existing_y = size - coord[1]
            if abs(existing_x - x) < r * 2 and abs(existing_y - y) < r * 2:
                messagebox.showwarning("Duplicate Position",
                                       "A city already exists at this position!")
                return

        dot_id = canvas.create_oval(x - r, y - r, x + r, y + r,
                                    fill=current_color, tags="city")
        cords.append(new_coord)
        city_shapes.append(dot_id)
        cities += 1
        info_label.config(text=f"Cities: {cities}")

    #funkcia na mazanie posledného pridaného vrcholu
    def undo(event=None):
        global cities
        if city_shapes:
            dot_id = city_shapes.pop()
            canvas.delete(dot_id)
            cords.pop()
            cities -= 1
            info_label.config(text=f"Cities: {cities}")
            canvas.update()
        else:
            messagebox.showinfo("Undo", "No more cities to remove!")

    #funkcia na generovanie vrcholov
    def generate_random_cities():
        global cities
        reset()
        try:
            n = int(generate_entry.get())
            if n < 3:
                messagebox.showwarning("Too Few Cities", "Please enter at least 3 cities.")
                return
            if n > 25000:
                messagebox.showwarning("Too Many Cities", "Maximum is 25000 cities.")
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
            cords.append((x, size - y))
            city_shapes.append((dot_id))
            cities += 1
        info_label.config(text=f"Cities: {cities}")

    #resetovanie kreliacej polchy
    #vymaže všetky vrcholy, logbox a pozadie
    def reset():
        global cities
        canvas.delete("city")
        cords.clear()
        city_shapes.clear()
        cities = 0
        clear_log()
        info_label.config(text=f"Cities: {cities}")

    # ==========================================================
    #  BUTTONS v controls_frame
    # ==========================================================
    button_style = {"font": ("Arial", 10, "bold"), "width": 20, "height": 1} # štýl buttonov

    #button na spustenie simulácie
    run_btn = tk.Button(
        controls_frame,
        text="▶  Run Comparison",
        command=on_enter,
        **button_style
    )
    run_btn.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    #button na zmenu algoritmov
    change_algo_button = tk.Button(
        controls_frame,
        text="⚙  Select Algorithms",
        command=open_algorithm_selector,
        **button_style
    )
    change_algo_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

    #buton na vyčistenie logboxu a kresliacej plochy
    reset_button = tk.Button(
        controls_frame,
        text="Reset",
        command=reset,
        **button_style
    )
    reset_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
    #generátor na control frame kde sú tlačidlá ovládajúce simulácie
    generate_frame = tk.Frame(controls_frame, bg="#f0f0f0")
    generate_frame.grid(row=3, column=0, columnspan=2, pady=5)
    #label na počet vypísaných miest
    tk.Label(generate_frame, text="Points:", font=("Arial", 9, "bold"),
             bg="#f0f0f0").pack(side="left", padx=(0, 5))
    #generate frame kde sa nachádza input okno a tlačidlo na genrovanie vrcholov
    generate_entry = tk.Entry(generate_frame, width=6, font=("Arial", 9))
    generate_entry.insert(0, "20")
    generate_entry.pack(side="left", padx=(0, 5))
    tk.Button(generate_frame, text="Generate Random",
              command=generate_random_cities,
              bg="#FF9800", fg="white",
              font=("Arial", 10, "bold"), height=1).pack(side="left")
    city_shapes = []
    canvas.bind("<Button-3>", undo) #prvím tlačidlom myši sa vymaže posledný vrchol
    canvas.bind("<Button-1>", on_click) #lavým tlačidlom myši sa pridá vrchol

    #funkcia na ukončenei po zavretí okna
    def on_close():
        root.after_cancel
        root.destroy()
    #podmenka ak sa okno zavrie tak sa vypnú procesy
    root.protocol("WM_DELETE_WINDOW", on_close)
    poll_log_queue()
    apply_theme()
    open_algorithm_selector()
    root.mainloop()