# ==========================================================
# TSP tool
# tento kód obsahuje GUI a vyzualizáciu výsledkov
# táto časť sa používa na nastavovanie hyperparametrov
# importované BP2_*** knižnice sú mnou vytvorené algoritmy ktoré sa volajú na spúštanie simulácií
# ==========================================================
import BP2_GA #GA algoritmus
import BP2_ABC #ABC algoritmus
import BP2_ACO #ACO algoritmus
import BP2_PSO #PSO algoritmus
import threading
import queue
import time #knižnica na čas  používa sa na zistenie času behu algoritmov
import matplotlib#používa sa na vyzualizáciu výsledkov
import matplotlib.pyplot as plt #využíva sa na vyzualizáciu výsledkov
import tkinter as tk #využíva sa na GUI
import random # knižnica na generovanie náhodných hodnôt
from tkinter import filedialog, messagebox #využíva sa na GUI
import customtkinter as ctk #krajšie GUI a úprava buttonov
from PIL import Image, ImageTk #importovanie vlastných obrázkov na pozadie

# ----- Settings -----
size = 500 #definuje velkosť kresliacej plochy
cords = [] #zoznam koordinácií bodov v priestore
cities = 0 #počet vrcholov grafu
background_path = None #definovaná path na pozdaie
bg_preview = None #holder pre importovaný obrázok
bg_image_id = None #id obrázka na mazanie

#holdery na výsledky simulácií
ant_count = 0 #velkost populácie pri ACO
pop_size = 0 #velkosť populácie pri GA
bee_count = 0 #velkosť populácie pri ABC
particle_count = 0 #velkosť populácie pri PSO
best_tour_gen_aco = 0#najlepšia cesta pri ACO
best_tour_gen_ga = 0#najlepšia cesta pre GA
best_tour_gen_abc = 0#najlepšia cesta pri ABC
best_tour_gen_pso = 0#najlepšia cesta pri PSO

current_color = "#0000FF" #predvolená farba vrcholov

# ==========================================================
#  Zobrazovanie výsledkov
# ==========================================================
def display_comparison(coords, aco_data, ga_data, abc_data, pso_data, params):
    #coords = definovanie rozloženia vrcholov v prestore
    #aco_data = výsledky simulácie ACO
    #ga_data = výsledky simulácie GA
    #abc_data = výsledky simulácie ABC
    #pso_data = výsledky simulácie PSO
    #background_path = cesta k obrázku na pozadie
    #params = knižnica všetkých hyperparametrov algoritmov
    matplotlib.use("TkAgg") # definovanie aby matplot vytváral výsledky do samostatného okna

    #vyberanie a priradovanie výsledkov z polí
    # ---- ACO data ---- 
    best_tours_over_time, best_lengths, best_tour_gen_aco = aco_data
    best_distance_aco = best_lengths[-1]
    best_route_aco = best_tours_over_time[-1]

    # ---- GA data ----
    best_route_ga, best_distances_ga, best_tour_gen_ga = ga_data
    best_route_ga = best_route_ga + [best_route_ga[0]]
    best_distance_ga = best_distances_ga[-1]

    # ---- ABC data ----
    best_route_abc, best_distances_abc, best_tour_gen_abc = abc_data
    best_distance_abc = best_distances_abc[-1]

    # ---- PSO data ----
    best_route_pso, best_distances_pso, best_tour_gen_pso = pso_data
    best_route_pso = best_route_pso + [best_route_pso[0]]
    best_distance_pso = best_distances_pso[-1]

    #funkcia na vykreslenie obrázka na pozadie
    def load_bg(ax):
        try:
            if background_path is not None:
                bg = plt.imread(background_path)
                ax.imshow(bg, extent=[0, size, 0, size], zorder=0, aspect="auto")
        except Exception:
            ax.set_facecolor("lightgray")

    #definovanie rozdelenia plochy 2 riadky 4 stĺpce
    # ACO | GA | porovnávací graf vývinu riešenia | ACO a GA hyperparametre
    # ABC | PSO | tabulka výsledkov | ABC a PSO hyperparametre
    fig, axs = plt.subplots(2, 4, figsize=(20, 8))
    fig.canvas.manager.set_window_title("ACO, GA, ABC, PSO Comparison")

    # ---------- ACO ----------
    #vykreslenie riešenia ACO
    ax_aco = axs[0, 0]
    load_bg(ax_aco)
    x_aco = [coords[i][0] for i in best_route_aco]
    y_aco = [coords[i][1] for i in best_route_aco]
    ax_aco.plot(x_aco, y_aco, "r-o", markersize=4, linewidth=1)
    for i, (x, y) in enumerate(coords):
        ax_aco.text(x + 2, y + 2, str(i), fontsize=8)
    ax_aco.set_xlim(0, size)
    ax_aco.set_ylim(0, size)
    ax_aco.set_title(f"ACO (Best={best_distance_aco:.1f})")

    # ---------- GA ----------
    # vykreslenie riešenia GA
    ax_ga = axs[0, 1]
    load_bg(ax_ga)
    x_ga = [coords[i][0] for i in best_route_ga]
    y_ga = [coords[i][1] for i in best_route_ga]
    ax_ga.plot(x_ga, y_ga, "g-o", markersize=4, linewidth=1)
    for i, (x, y) in enumerate(coords):
        ax_ga.text(x + 2, y + 2, str(i), fontsize=8)
    ax_ga.set_xlim(0, size)
    ax_ga.set_ylim(0, size)
    ax_ga.set_title(f"GA (Best={best_distance_ga:.1f})")

    # ---------- ABC ----------
    # vykreslenie riešenia ABC
    ax_abc = axs[1, 0]
    load_bg(ax_abc)
    x_abc = [coords[i][0] for i in best_route_abc]
    y_abc = [coords[i][1] for i in best_route_abc]
    ax_abc.plot(x_abc, y_abc, "m-o", markersize=4, linewidth=1)
    for i, (x, y) in enumerate(coords):
        ax_abc.text(x + 2, y + 2, str(i), fontsize=8)
    ax_abc.set_xlim(0, size)
    ax_abc.set_ylim(0, size)
    ax_abc.set_title(f"ABC (Best={best_distance_abc:.1f})")

    # ---------- PSO ----------
    # vykreslenie riešenia PSO
    ax_pso = axs[1, 1]
    load_bg(ax_pso)
    x_pso = [coords[i][0] for i in best_route_pso]
    y_pso = [coords[i][1] for i in best_route_pso]
    ax_pso.plot(x_pso, y_pso, "b-o", markersize=4, linewidth=1)
    for i, (x, y) in enumerate(coords):
        ax_pso.text(x + 2, y + 2, str(i), fontsize=8)
    ax_pso.set_xlim(0, size)
    ax_pso.set_ylim(0, size)
    ax_pso.set_title(f"PSO (Best={best_distance_pso:.1f})")

    # ---------- Graph ----------
    #graf vykreslovania vývinu riešenia cez generácie pre všetky 4 algoritmi
    ax_info = axs[0, 2]
    ax_info.set_title("Convergence Comparison", fontsize=11, fontweight="bold")
    ax_info.set_xlabel("Generation")
    ax_info.set_ylabel("Best Distance")
    ax_info.grid(True, alpha=0.3)

    ax_info.plot(best_lengths, "r-", lw=1.8, label="ACO")
    ax_info.plot(best_distances_ga, "g-", lw=1.8, label="GA")
    ax_info.plot(best_distances_abc, "m-", lw=1.8, label="ABC")
    ax_info.plot(best_distances_pso, "b-", lw=1.8, label="PSO")
    ax_info.legend(loc="upper right", fontsize=8)

    # ---------- Parameters (ACO and GA) ----------
    #vykreslovanie hyperparametrov ACO a GA
    ax_params_top = axs[0, 3]
    ax_params_top.axis("off")
    ax_params_top.set_title("Parameters (ACO & GA)", fontsize=11, fontweight="bold")

    params_text_top = f"ACO:\nACO generations: {params.get('ACO generations')}\nAnt count: {params.get('Ant count')}\nAlpha: {params.get('Alpha')}\nBeta: {params.get('Beta')}\nEvaporation rate: {params.get('Evaporation rate')}\nQ: {params.get('Q')}\n\n\nGA:\nGA generations: {params.get('GA generations')}\nPopulation size: {params.get('Population size')}\nElit rate: {params.get('Elit rate')}\nMutation rate: {params.get('Mutation rate')}"
    ax_params_top.text(0.5, 0.5, params_text_top, fontsize=9, ha="center", va="center", wrap=True)

    # ---------- Summary Statistics Table ----------
    # vytvorenie tabulky v ktorej je vidno najlepší vysledok a v akej generácií bol dosiahnutý
    ax_table = axs[1, 2]
    ax_table.axis("off")
    ax_table.set_title("Summary Statistics", fontsize=11, fontweight="bold")

    algorithms = [
        ("ACO", best_distance_aco, best_tour_gen_aco),
        ("GA", best_distance_ga, best_tour_gen_ga),
        ("ABC", best_distance_abc, best_tour_gen_abc),
        ("PSO", best_distance_pso, best_tour_gen_pso)
    ]

    winner = min(algorithms, key=lambda x: x[1])

    table_data = [
        ["Algorithm", "Distance", "Conv. Gen"],
    ]

    for name, dist, gen in algorithms:
        marker = "★" if name == winner[0] else ""
        table_data.append([f"{name} {marker}", f"{dist:.2f}", str(gen)])

    table = ax_table.table(cellText=table_data, cellLoc="center", loc="center",
                           colWidths=[0.35, 0.35, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    # Style the header row
    for i in range(3):
        table[(0, i)].set_facecolor("#4CAF50")
        table[(0, i)].set_text_props(weight="bold", color="white")

    # Highlight winner row
    for idx, (name, _, _) in enumerate(algorithms, 1):
        if name == winner[0]:
            for i in range(3):
                table[(idx, i)].set_facecolor("#ffffcc")

    # ---------- Parameters (ABC and PSO) ----------
    # vykreslovanie hyperparametrov ABC a PSO
    ax_params_bottom = axs[1, 3]
    ax_params_bottom.axis("off")
    ax_params_bottom.set_title("Parameters (ABC & PSO)", fontsize=11, fontweight="bold")

    params_text_bottom = f"ABC:\n Generations: {params.get('ABC generations')}\nBee count: {params.get('Bee count')}\nEmploy rate: {params.get('employ_rate')}\nScout rate: {params.get('scout_rate')} \n\n\nPSO:\nPSO generations: {params.get('PSO generations')}\nParticle count: {params.get('Particle count')}\nC1: {params.get('c1')}\nC2: {params.get('c2')}\nWeight: {params.get('weight')}"
    ax_params_bottom.text(0.5, 0.5, params_text_bottom, fontsize=9, ha="center", va="center", wrap=True)

    plt.tight_layout()
    manager = plt.get_current_fig_manager()
    try:
        manager.window.state('zoomed')
    except:
        manager.full_screen_toggle()

    plt.show()

# ==========================================================
#  TKINTER GUI

# ==========================================================
if __name__ == "__main__":
    root = tk.Tk()
    ctk.set_appearance_mode("light")
    root.title("TSP Comparison Tool") #názou okna
    root.state('zoomed') # definovanie otvorenia na full screen
    root.configure(bg="#f0f0f0") #preddefinovaná farba pozoadnia

    main_frame = tk.Frame(root, bg="#f0f0f0")
    main_frame.pack(padx=10, pady=10)

    # Lavá strana (Canvas + Log)
    #na lavej strane je 500x500 okno kde user kliká a pridáva vrcholy
    # X a Y je ukladaný do cords
    left_frame = tk.Frame(main_frame, bg="white", relief=tk.RIDGE, borderwidth=2)# definovanie pozadia na bielu a velkosť okrajov na 2
    left_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
    # definovanie nadpisu pre lavú stranu
    instruction_label = tk.Label(left_frame, text="Click to Add Cities", font=("Arial", 12, "bold"), bg="white", fg="#333")
    instruction_label.pack(pady=5)

    canvas = tk.Canvas(left_frame, width=size, height=size, bg="white")
    canvas.pack()

    # Color Slider (Horizontal - Below Canvas)
    color_frame = tk.Frame(left_frame, bg="white")
    color_frame.pack(pady=10, padx=10, fill="x")

    tk.Label(color_frame, text="Dot Color:", font=("Arial", 9, "bold"), bg="white").pack(side="left", padx=(0, 10))

    #funkcia na slider na vyberanie farby bodov ktoré sa vykreslujú v lavom okne
    def wavelength_to_rgb(wavelength):
        if wavelength >= 380 and wavelength < 440:
            r = -(wavelength - 440) / (440 - 380)
            g = 0.0
            b = 1.0
        elif wavelength >= 440 and wavelength < 490:
            r = 0.0
            g = (wavelength - 440) / (490 - 440)
            b = 1.0
        elif wavelength >= 490 and wavelength < 510:
            r = 0.0
            g = 1.0
            b = -(wavelength - 510) / (510 - 490)
        elif wavelength >= 510 and wavelength < 580:
            r = (wavelength - 510) / (580 - 510)
            g = 1.0
            b = 0.0
        elif wavelength >= 580 and wavelength < 645:
            r = 1.0
            g = -(wavelength - 645) / (645 - 580)
            b = 0.0
        elif wavelength >= 645 and wavelength <= 780:
            r = 1.0
            g = 0.0
            b = 0.0
        else:
            r = 0.0
            g = 0.0
            b = 0.0

        # Intensity correction for edges
        if wavelength >= 380 and wavelength < 420:
            factor = 0.3 + 0.7 * (wavelength - 380) / (420 - 380)
        elif wavelength >= 700 and wavelength <= 780:
            factor = 0.3 + 0.7 * (780 - wavelength) / (780 - 700)
        else:
            factor = 1.0

        r = int(r * factor * 255)
        g = int(g * factor * 255)
        b = int(b * factor * 255)

        return f"#{r:02x}{g:02x}{b:02x}"
    #funkcia na updatovanie farby a nastavenie farby pri vykreslovaní
    def update_color(*args):
        global current_color
        wavelength = color_slider.get()
        current_color = wavelength_to_rgb(wavelength)
        color_preview.config(bg=current_color)
    #vytvorenie slideru na farbu
    color_slider = tk.Scale(color_frame, from_=380, to=780, orient="horizontal", length=350, command=update_color, bg="white", showvalue=False, sliderlength=20, width=15)
    color_slider.set(470)  # Blue default
    color_slider.pack(side="left", padx=5)
    #okno na zobrazeneie nastavenej farby
    color_preview = tk.Label(color_frame, text="", width=8, height=1, bg=current_color,relief="solid", borderwidth=2)
    color_preview.pack(side="left", padx=(0, 0))

    # Initialize color
    update_color()

    #vytvorenie okna na logy
    info_label = tk.Label(left_frame, text=f"Cities: {cities}", font=("Arial", 9, "bold"), bg="white", fg="#333")
    info_label.pack(pady=(0, 0))
    log_frame = tk.Frame(left_frame, bg="white")
    log_frame.pack(pady=(0, 5))
    #pridanie scroll baru na log a nastavenei že sa dá scrollovať
    log_scroll = tk.Scrollbar(log_frame)
    log_scroll.pack(side="right", fill="y")
    #vytvorenie boxu na logy
    log_box = tk.Text(log_frame, height=8, width=58, font=("Consolas", 9), bg="#fafafa", fg="black", relief="solid", bd=1, wrap="word", yscrollcommand=log_scroll.set)
    log_box.pack(side="left", fill="both", expand=True)
    log_scroll.config(command=log_box.yview)
    #funkcia na pridávanie logov
    def log_message(msg, color="black"):
        log_box.config(state="normal")
        log_box.insert("end", msg + "\n", ("color",)) # vypísanei logu a prejsť na nový riadok
        log_box.tag_configure("color", foreground=color) # definovanie farby logu
        log_box.see("end") # ukončenie logu
        log_box.config(state="disabled")
        root.update_idletasks()
    #funkcia na čistenie logu pri resete
    def clear_log():
        log_box.config(state="normal")   # Make editable temporarily
        log_box.delete("1.0", "end")     # Delete all text
        log_box.insert("end", "Ready.\n", ("gray",))  # Optional: add default message
        log_box.config(state="disabled") # Lock it again

    log_message("Ready.\n", "gray")

    # RIGHT SIDE: Parameters
    #nastavovanie hyperparametrov na pravej strane
    right_frame = tk.Frame(main_frame, bg="#f0f0f0")
    right_frame.grid(row=0, column=1, sticky="n")

    entry_widgets = {}
    # ---------- INFO POPUP FUNCTIONS ----------
    #funkcia na info box pre vysvetlenie hyperparamtrov
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
    - Elit rate: Portion of best solutions kept.
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
    #funkcia na definovanie info buttonov aby boly modré a s i a zaoblené
    def round_info_button(parent, command):
        return ctk.CTkButton(
            parent,
            text="ℹ",
            width=40,
            height=10,
            corner_radius=20,
            fg_color="#2196F3",
            hover_color="#1976D2",
            text_color="white",
            font=("Arial", 10, "bold"),
            command=command
        )
    #---Pravá strana na nastavenie hyperparametrov---
    #aco paramete
    #definovanie framu na parametra aco
    aco_frame = tk.LabelFrame(right_frame, text="ACO Parameters", font=("Arial", 11, "bold"), bg="#e8f4f8", relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    aco_frame.grid(row=0, column=0, padx=5, pady=5, sticky="n")
    #predvolené parametra pre aco
    aco_defaults = {
        "ACO generations": 1000,
        "Ant count": 5,
        "Alpha": 1.0,
        "Beta": 2.0,
        "Evaporation rate": 0.1,
        "Q": 100.0,
        "ACO_seed": 173
    }
    #vyberanie a meneie parametrov bodal user vstupu
    for i, (key, default) in enumerate(aco_defaults.items()):
        tk.Label(aco_frame, text=f"{key}:", bg="#e8f4f8", font=("Arial", 9)).grid(row=i, column=0, sticky="w", pady=3)
        e = tk.Entry(aco_frame, width=12, font=("Arial", 9))
        e.insert(0, str(default))
        e.grid(row=i, column=1, padx=(5, 0), pady=3)
        entry_widgets[key] = e
    round_info_button(aco_frame, show_info_aco).grid(columnspan=2, pady=5)

    # --- GA Parameters ---
    #definovanie framu pre hyperparametre pre ga
    ga_frame = tk.LabelFrame(right_frame, text="GA Parameters", font=("Arial", 11, "bold"), bg="#f8f4e8", relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    ga_frame.grid(row=1, column=0, padx=5, pady=5, sticky="n")
    #predvolené parametre
    ga_defaults = {
        "GA generations": 1000,
        "Population size": 100,
        "Elit rate": 0.25,
        "Mutation rate": 0.1,
        "GA_seed": 173
    }
    #nastavenei parametrov podla user input
    for i, (key, default) in enumerate(ga_defaults.items()):
        tk.Label(ga_frame, text=f"{key}:", bg="#f8f4e8", font=("Arial", 9)).grid(row=i, column=0, sticky="w", pady=3)
        e = tk.Entry(ga_frame, width=12, font=("Arial", 9))
        e.insert(0, str(default))
        e.grid(row=i, column=1, padx=(5, 0), pady=3)
        entry_widgets[key] = e
    round_info_button(ga_frame, show_info_ga).grid(columnspan=2, pady=5)
    # --- ABC Parameters ---
    #okno pre hyperaparametre abc
    abc_frame = tk.LabelFrame(right_frame, text="ABC Parameters", font=("Arial", 11, "bold"), bg="#f8e8f4", relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    abc_frame.grid(row=0, column=1, padx=5, pady=5, sticky="n")
    #predvolené hyperaparametre pre abc
    abc_defaults = {
        "ABC generations": 1000,
        "Bee count": 20,
        "employ_rate": 0.7,
        "scout_rate": 0.01,
        "ABC_seed": 173,
    }
    #nastavenei parametrov podla user vstupu
    for i, (key, default) in enumerate(abc_defaults.items()):
        tk.Label(abc_frame, text=f"{key}:", bg="#f8e8f4", font=("Arial", 9)).grid(row=i, column=0, sticky="w", pady=3)
        e = tk.Entry(abc_frame, width=12, font=("Arial", 9))
        e.insert(0, str(default))
        e.grid(row=i, column=1, padx=(5, 0), pady=3)
        entry_widgets[key] = e
    round_info_button(abc_frame, show_info_abc).grid(columnspan=2, pady=5)
    # --- PSO Parameters ---
    #vytvorenie okna na nastavenie PSO
    pso_frame = tk.LabelFrame(right_frame, text="PSO Parameters", font=("Arial", 11, "bold"), bg="#e8f8f4", relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    pso_frame.grid(row=1, column=1, padx=5, pady=5, sticky="n")
    #predvolené hyperparametre PSO
    pso_defaults = {
        "PSO generations": 1000,
        "Particle count": 10,
        "c1": 1.5,
        "c2": 1.5,
        "weight": 0.9,
        "PSO_seed": 173
    }
    #nastavenie parametrov podla PSO
    for i, (key, default) in enumerate(pso_defaults.items()):
        tk.Label(pso_frame, text=f"{key}:", bg="#e8f8f4", font=("Arial", 9)).grid(row=i, column=0, sticky="w", pady=3)
        e = tk.Entry(pso_frame, width=12, font=("Arial", 9))
        e.insert(0, str(default))
        e.grid(row=i, column=1, padx=(5, 0), pady=3)
        entry_widgets[key] = e
    round_info_button(pso_frame, show_info_pso).grid(columnspan=2, pady=5)

    # ==========================================================
    #  CONTROLS
    # ==========================================================
    #vytvorenie okna na control buttony
    controls_frame = tk.LabelFrame(right_frame, text="Controls", font=("Arial", 11, "bold"), bg="#f0f0f0", relief=tk.GROOVE, borderwidth=2, padx=15, pady=10)
    controls_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")
    #funkcia enter buttonu na spustenie simulácie
    log_queue = queue.Queue()  # Thread-safe message queue


    def poll_log_queue():
        try:
            root.winfo_exists()  # raises TclError if window is destroyed
        except tk.TclError:
            return  # window is gone, stop rescheduling

        while True:
            try:
                msg, color = log_queue.get_nowait()
                log_message(msg, color)
            except queue.Empty:
                break
        root.after(100, poll_log_queue)
    def thread_log(msg, color="black"):
        log_queue.put((msg, color))

    def on_enter():
        if len(cords) < 3:
            messagebox.showwarning("Not Enough Cities", "Please add at least 3 cities before running.")
            return

        params = {k: (float(v.get()) if '.' in v.get() else int(v.get())) for k, v in entry_widgets.items()}
        clear_log()

        # Shared result containers — threads write here, main thread reads after join
        results = {
            "aco": None,
            "ga": None,
            "abc": None,
            "pso": None,
        }
        # Shared error flags — if a thread fails it sets its flag to an error string
        errors = {
            "aco": None,
            "ga": None,
            "abc": None,
            "pso": None,
        }

        # ------------------------------------------------------------------
        # Worker functions — one per algorithm
        # Each function runs in its own thread.
        # ------------------------------------------------------------------

        def run_aco():
            thread_log("Running ACO...", "blue")
            try:
                start = time.time()
                results["aco"] = BP2_ACO.ACO(cords, params)
                elapsed = round(time.time() - start, 2)
                thread_log(f"ACO finished successfully ✅  — {elapsed}s", "green")
            except ZeroDivisionError:
                errors["aco"] = "ZeroDivisionError"
                thread_log("ACO ❌ — Two cities share the same position!", "red")
            except Exception as e:
                errors["aco"] = str(e)
                thread_log(f"ACO ❌ failed — {e}", "red")

        def run_ga():
            thread_log("Running GA...", "blue")
            try:
                start = time.time()
                results["ga"] = BP2_GA.GA(cords, params)
                elapsed = round(time.time() - start, 2)
                thread_log(f"GA  finished successfully ✅  — {elapsed}s", "green")
            except ZeroDivisionError:
                errors["ga"] = "ZeroDivisionError"
                thread_log("GA  ❌ — Two cities share the same position!", "red")
            except Exception as e:
                errors["ga"] = str(e)
                thread_log(f"GA  ❌ failed — {e}", "red")

        def run_abc():
            thread_log("Running ABC...", "blue")
            try:
                start = time.time()
                results["abc"] = BP2_ABC.ABC(cords, params)
                elapsed = round(time.time() - start, 2)
                thread_log(f"ABC finished successfully ✅  — {elapsed}s", "green")
            except ZeroDivisionError:
                errors["abc"] = "ZeroDivisionError"
                thread_log("ABC ❌ — Two cities share the same position!", "red")
            except Exception as e:
                errors["abc"] = str(e)
                thread_log(f"ABC ❌ failed — {e}", "red")

        def run_pso():
            thread_log("Running PSO...", "blue")
            try:
                start = time.time()
                results["pso"] = BP2_PSO.PSO(cords, params)
                elapsed = round(time.time() - start, 2)
                thread_log(f"PSO finished successfully ✅  — {elapsed}s", "green")
            except ZeroDivisionError:
                errors["pso"] = "ZeroDivisionError"
                thread_log("PSO ❌ — Two cities share the same position!", "red")
            except Exception as e:
                errors["pso"] = str(e)
                thread_log(f"PSO ❌ failed — {e}", "red")

        # ------------------------------------------------------------------
        # Orchestrator — waits for all threads, then shows results.
        # Runs in its own thread so the tkinter main loop is never blocked.
        # ------------------------------------------------------------------

        def orchestrate():
            # Disable the Run button while algorithms are running
            run_btn.config(state="disabled")

            threads = [
                threading.Thread(target=run_aco, daemon=True),
                threading.Thread(target=run_ga, daemon=True),
                threading.Thread(target=run_abc, daemon=True),
                threading.Thread(target=run_pso, daemon=True),
            ]

            overall_start = time.time()

            # Launch all 4 threads simultaneously
            for t in threads:
                t.start()

            # Wait for every thread to finish
            for t in threads:
                t.join()

            total = round(time.time() - overall_start, 2)

            # Check whether any algorithm failed
            failed = [name.upper() for name, err in errors.items() if err is not None]
            if failed:
                thread_log(f"\nCompleted with errors in {total}s. Failed: {', '.join(failed)}", "red")
                thread_log("Fix the issues above and press Reset before retrying.", "red")
                run_btn.config(state="normal")
                return

            thread_log(f"\nAll algorithms finished in {total}s — displaying results...", "green")

            # Display results back on the main thread (matplotlib + tkinter must
            # run on the main thread; schedule via root.after with delay=0)
            root.after(0, lambda: _show_results(results, params))
            run_btn.config(state="normal")

        def _show_results(results, params):
            try:
                display_comparison(
                    cords,
                    results["aco"],
                    results["ga"],
                    results["abc"],
                    results["pso"],
                    params,
                )
                log_message("Results displayed successfully ✅", "green")
            except Exception as e:
                log_message(f"Results display failed ❌ — {e}", "red")

        # Kick off the orchestrator thread
        threading.Thread(target=orchestrate, daemon=True).start()


    #funkcia pre button na nahrávanie pozadia
    def upload_background():
        global background_path, bg_preview, bg_image_id
        path = filedialog.askopenfilename(title="Select Background Image", filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif")])
        if path:
            background_path = path
            img = Image.open(path).resize((size, size))
            bg_preview = ImageTk.PhotoImage(img)
            if bg_image_id:
                canvas.delete(bg_image_id)
            bg_image_id = canvas.create_image(0, 0, anchor="nw", image=bg_preview)
            canvas.tag_lower(bg_image_id)
    #funkcia na na lavé tlačidlo miši
    def on_click(event):
        global cities
        #definovanie X a Y podľa koordínácie kliku myšky
        x, y = event.x, event.y
        r = 6 # definovanie polomeru kruhu
        # create_oval and create_text return unique IDs — store them together
        dot_id = canvas.create_oval(x - r, y - r, x + r, y + r, fill=current_color, tags="city")
        text_id = canvas.create_text(x, y - 15, text=cities, tags="city", font=("Arial", 8))
        cords.append((x, size - y))#pridanie koordinácií | treba otočiť kôli displayu v matplotlib
        # also store both IDs for undoing later
        city_shapes.append((dot_id, text_id))
        cities += 1
        info_label.config(text=f"Cities: {cities}")
    #definovanie funkcie na pravé tlačidlo
    #je to funkcia na vymazanie posledného pridaného bodu
    def undo(event=None):
        global cities
        if city_shapes:  # if there's something to undo
            dot_id, text_id = city_shapes.pop()  # remove last drawn pair
            canvas.delete(dot_id)
            canvas.delete(text_id)
            cords.pop()
            cities -= 1
            info_label.config(text=f"Cities: {cities}")
            canvas.update()
        else:
            messagebox.showinfo("Undo", "No more cities to remove!")
    #funkcia na generovanie náhodného rozmiestnenia vrcholov
    def generate_random_cities():
        global cities
        reset()
        try:
            n = int(generate_entry.get())
            if n < 3:#podmienka aby vrcholov nebolo menej ako 3
                messagebox.showwarning("Too Few Cities", "Please enter at least 3 cities.")
                return
            if n > 2500:#podmienka aby sa neprekrívali dva body
                messagebox.showwarning("Too Many Cities", "Maximum is 500 cities.")
                return
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer.")
            return

        r = 6
        for _ in range(n):
            while True: #check na to aby sa dva body nenachádzali na rovnakom miest
                x = random.randint(r, size - r)
                y = random.randint(r, size - r)
                if (x, size - y) not in cords:
                    break
            dot_id = canvas.create_oval(x - r, y - r, x + r, y + r, fill=current_color, tags="city")#vykreslenie bodu
            text_id = canvas.create_text(x, y - 15, text=cities, tags="city", font=("Arial", 8))#label k bodu
            cords.append((x, size - y))#pridanie do pola
            city_shapes.append((dot_id, text_id))#pole na undo
            cities += 1#pridanie do counteru

        info_label.config(text=f"Cities: {cities}")
    #funkcia na reset button
    #vymažú sa všetky body
    #vymaže sa pozadie
    #resetuje sa log
    def reset():
        global cities, bg_preview, bg_image_id, background_path
        canvas.delete("city")
        if bg_image_id:              # remove background if present
            canvas.delete(bg_image_id)
            bg_image_id = None
        background_path = None       # clear stored path
        bg_preview = None
        cords.clear()
        city_shapes.clear()
        cities = 0
        clear_log()
        info_label.config(text=f"Cities: {cities}")

    # Buttons
    button_style = {"font": ("Arial", 10, "bold"), "width": 20, "height": 1}
    #button na on_enter
    run_btn = tk.Button(controls_frame, text="Run Comparison", command=on_enter, bg="#4CAF50", fg="white",
                        **button_style)
    run_btn.pack(pady=5)
    #button na ubload background
    tk.Button(controls_frame, text="Upload Background", command=upload_background, bg="#2196F3", fg="white", **button_style).pack(pady=5)
    #reset button
    tk.Button(controls_frame, text="Reset Cities", command=reset, bg="#f44336", fg="white", **button_style).pack(pady=5)
    # Generate random cities
    generate_frame = tk.Frame(controls_frame, bg="#f0f0f0")
    generate_frame.pack(pady=5)

    generate_frame = tk.Frame(controls_frame, bg="#f0f0f0")
    generate_frame.pack(pady=5)

    tk.Label(generate_frame, text="Points:", font=("Arial", 9, "bold"), bg="#f0f0f0").pack(side="left", padx=(0, 5))
    generate_entry = tk.Entry(generate_frame, width=6, font=("Arial", 9))
    generate_entry.insert(0, "20")
    generate_entry.pack(side="left", padx=(0, 5))
    tk.Button(generate_frame, text="Generate Random", command=generate_random_cities, bg="#FF9800", fg="white", font=("Arial", 10, "bold"), height=1).pack(side="left")
    city_shapes = []
    #pravé tlačidlo na undo
    canvas.bind("<Button-3>", undo)
    #lavé tlačidlo na on_click pridanie mesta
    canvas.bind("<Button-1>", on_click)


    def on_close():
        root.after_cancel  # cancels pending after callbacks
        root.destroy()


    root.protocol("WM_DELETE_WINDOW", on_close)
    poll_log_queue()
    #definovanie spustitelnosti kódu
    root.mainloop()