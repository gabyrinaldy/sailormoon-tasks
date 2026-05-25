import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# Biblioteca nativa do Windows para tocar sons WAV com perfeição!
import winsound

try:
    import pygame
    PYGAME_OK = True
except ImportError:
    PYGAME_OK = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- PALETA DE CORES SAILOR MOON ULTIMATE ---
COLOR_BG = "#FFF5F8"         # Rosa quase branco (Fundo)
COLOR_CARD = "#FFFFFF"       # Branco Puro (Cards)
COLOR_PINK_LIGHT = "#FFD1DC" # Rosa Bebê
COLOR_PINK_BRIGHT = "#FF85A2" # Rosa Choque (Glow/Hover)
COLOR_PURPLE_SOFT = "#F3E5F5" # Lilás Pastel
COLOR_TEXT = "#5D4037"       # Marrom Suave (Melhor contraste que preto)
COLOR_GOLD = "#FFD700"       # Dourado para Estrelas
DATA_FILE = os.path.join(BASE_DIR, "sailor_tasks_data.json")

# --- FONTES ---
FONT_TITLE = ("Gabriola", 20, "bold")
FONT_SUBTITLE = ("Trebuchet MS", 12, "bold")
FONT_BODY = ("Trebuchet MS", 10)

class SailorTasksApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌙 Sailor Tasks: Prisma Estelar 🌙")
        self.root.geometry("1050x850")
        self.root.configure(bg=COLOR_BG)

        if PYGAME_OK:
            try: pygame.mixer.init()
            except: pass

        self.load_data()

        # --- ESTILIZAÇÃO TTK ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=COLOR_PURPLE_SOFT, foreground=COLOR_TEXT, 
                        padding=[20, 8], font=("Trebuchet MS", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", COLOR_PINK_LIGHT)], foreground=[("selected", COLOR_TEXT)])

        # --- BARRA SUPERIOR MÁGICA ---
        self.setup_top_bar()

        # --- CONTAINER PRINCIPAL ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        self.tab_status = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_store = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_grades = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_pomodoro = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_charts = tk.Frame(self.notebook, bg=COLOR_BG)

        self.notebook.add(self.tab_status, text="✧ Missões ✧")
        self.notebook.add(self.tab_store, text="💖 Lojinha 💖")
        self.notebook.add(self.tab_grades, text="📚 Notas")
        self.notebook.add(self.tab_pomodoro, text="⏱ Pomodoro")
        self.notebook.add(self.tab_charts, text="📊 Poder")

        self.setup_status_tab()
        self.setup_store_tab()
        self.setup_grades_tab()
        self.setup_pomodoro_tab()
        self.setup_charts_tab()
        
        self.update_status_display()
        self.update_live_clock()

    # ================= UI HELPERS =================
    def apply_hover(self, button, color_on, color_off):
        button.bind("<Enter>", lambda e: button.config(bg=color_on))
        button.bind("<Leave>", lambda e: button.config(bg=color_off))

    def create_magic_divider(self, parent):
        lbl = tk.Label(parent, text="✧ 💖 ✧ 💖 ✧ 💖 ✧ 💖 ✧", bg=COLOR_CARD, fg=COLOR_PINK_LIGHT, font=("Trebuchet MS", 10))
        lbl.pack(pady=5)

    def setup_top_bar(self):
        frame = tk.Frame(self.root, bg=COLOR_BG)
        frame.pack(fill="x", padx=25, pady=10)

        self.btn_mute = tk.Button(frame, text="🔊 Som Ativo", bg=COLOR_PINK_LIGHT, fg=COLOR_TEXT, 
                                 font=FONT_BODY, relief="flat", padx=10, command=self.toggle_sound)
        self.btn_mute.pack(side="left", padx=5)
        self.apply_hover(self.btn_mute, "#FFE4E1", COLOR_PINK_LIGHT)

        self.btn_reset = tk.Button(frame, text="🔄 Resetar Poder", bg="#FF5C8A", fg="white", 
                                 font=FONT_BODY, relief="flat", padx=10, command=self.reset_stats)
        self.btn_reset.pack(side="left", padx=5)
        self.apply_hover(self.btn_reset, "#D81B60", "#FF5C8A")

        self.lbl_coins_top = tk.Label(frame, text=f"🪙 {self.moon_coins} Moedas", bg=COLOR_BG, 
                                     fg=COLOR_PINK_BRIGHT, font=FONT_TITLE)
        self.lbl_coins_top.pack(side="right")

    # ================= PROGRESS BAR =================
    def draw_progress_bar(self, parent):
        self.canvas_progress = tk.Canvas(parent, height=15, bg=COLOR_PURPLE_SOFT, bd=0, highlightthickness=1, highlightbackground=COLOR_PINK_LIGHT)
        self.canvas_progress.pack(fill="x", pady=5)
        self.bar_fill = self.canvas_progress.create_rectangle(0, 0, 0, 15, fill=COLOR_PINK_BRIGHT, outline="")

    def update_progress_bar(self, percent):
        self.canvas_progress.update()
        width = self.canvas_progress.winfo_width()
        fill_width = (percent / 100) * width
        self.canvas_progress.coords(self.bar_fill, 0, 0, fill_width, 15)

    # ================= PERSISTÊNCIA & SONS =================
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.skills = data.get("skills", {"Mente (Estudos)": 0, "Corpo (Saúde)": 0, "Alma (Lazer)": 0, "Ordem (Casa)": 0})
                    self.tasks = data.get("tasks", [])
                    self.rewards = data.get("rewards", [{"title": "Assistir Anime", "cost": 50}])
                    self.moon_coins = data.get("moon_coins", 0)
                    self.sound_on = data.get("sound_on", True)
            except: self.init_default_data()
        else: self.init_default_data()

    def init_default_data(self):
        self.skills = {"Mente (Estudos)": 0, "Corpo (Saúde)": 0, "Alma (Lazer)": 0, "Ordem (Casa)": 0}
        self.rewards = [{"title": "Assistir Anime", "cost": 50}]
        self.tasks = []
        self.moon_coins = 0
        self.sound_on = True

    def save_data(self):
        data = {"skills": self.skills, "tasks": self.tasks, "rewards": self.rewards, "moon_coins": self.moon_coins, "sound_on": self.sound_on}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        self.btn_mute.config(text="🔊 Som Ativo" if self.sound_on else "🔇 Som Mudo")
        self.save_data()

    def play_sound(self, name):
        if not self.sound_on: return
        wav_path = os.path.join(BASE_DIR, name + ".wav")
        mp3_path = os.path.join(BASE_DIR, name + ".mp3")
        
        if os.path.exists(wav_path):
            try: 
                winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                return
            except: pass
            
        if PYGAME_OK and os.path.exists(mp3_path):
            try: 
                snd = pygame.mixer.Sound(mp3_path)
                snd.play()
                return
            except: pass
            
        try:
            if name == "tarefa":
                winsound.Beep(900, 150)
                winsound.Beep(1200, 250)
            elif name == "levelup":
                winsound.Beep(1000, 150)
                winsound.Beep(1200, 150)
                winsound.Beep(1500, 400)
            elif name == "compra":
                winsound.Beep(1500, 100)
                winsound.Beep(2000, 150)
            elif name == "pomodoro_end":
                winsound.Beep(1300, 200)
                winsound.Beep(1000, 200)
                winsound.Beep(1300, 200)
                winsound.Beep(1000, 400)
        except: pass

    def reset_stats(self):
        if messagebox.askyesno("Aviso Crítico", "Tem certeza que deseja zerar todas as suas Moedas e Nível de Poder? 🥺"):
            self.moon_coins = 0
            for k in self.skills.keys():
                self.skills[k] = 0
            self.update_status_display()
            self.save_data()
            messagebox.showinfo("Renascimento", "Seu poder foi purificado! Comece uma nova jornada. ✨")

    # ================= TAB 1: STATUS & MISSÕES (MURAL KAWAII) =================
    def setup_status_tab(self):
        # Coluna da Esquerda (Status e Mascote)
        f_left = tk.Frame(self.tab_status, bg=COLOR_BG)
        f_left.pack(side="left", fill="both", expand=False, padx=10, pady=10)

        card_status = tk.Frame(f_left, bg=COLOR_CARD, padx=20, pady=20, highlightthickness=1, highlightbackground=COLOR_PINK_LIGHT)
        card_status.pack(fill="both")

        tk.Label(card_status, text="✨ NÍVEL DE PODER ✨", font=FONT_SUBTITLE, bg=COLOR_CARD, fg=COLOR_PINK_BRIGHT).pack()
        self.lbl_level = tk.Label(card_status, text="NÍVEL 1", font=FONT_TITLE, bg=COLOR_CARD, fg=COLOR_TEXT)
        self.lbl_level.pack()
        
        self.draw_progress_bar(card_status)
        self.lbl_xp_info = tk.Label(card_status, text="Faltam 30 XP", font=("Trebuchet MS", 8), bg=COLOR_CARD, fg=COLOR_TEXT)
        self.lbl_xp_info.pack()

        self.create_magic_divider(card_status)

        self.skill_labels = {}
        for skill in self.skills.keys():
            lbl = tk.Label(card_status, text=f"{skill}: 0", font=FONT_BODY, bg=COLOR_CARD, fg=COLOR_TEXT)
            lbl.pack(anchor="w", pady=2)
            self.skill_labels[skill] = lbl

        card_luna = tk.Frame(f_left, bg=COLOR_CARD, pady=15, highlightthickness=1, highlightbackground=COLOR_PINK_LIGHT)
        card_luna.pack(fill="x", pady=15)
        self.lbl_mascot = tk.Label(card_luna, text="🐈 Luna", font=FONT_SUBTITLE, bg=COLOR_CARD, fg=COLOR_PINK_BRIGHT)
        self.lbl_mascot.pack()
        self.lbl_mascot_msg = tk.Label(card_luna, text="Pronta para brilhar?", font=("Trebuchet MS", 9, "italic"), bg=COLOR_CARD, fg=COLOR_TEXT)
        self.lbl_mascot_msg.pack()

        # Coluna da Direita (Mural de Missões)
        f_right = tk.Frame(self.tab_status, bg=COLOR_BG)
        f_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        lbl_mural = tk.Label(f_right, text="📜 MURAL DE MISSÕES", font=FONT_TITLE, bg=COLOR_BG, fg=COLOR_TEXT)
        lbl_mural.pack(pady=(0, 5))

        # --- NOVO CARD DE INPUT SUPER KAWAII 🌸 ---
        card_input = tk.Frame(f_right, bg=COLOR_CARD, padx=15, pady=12, highlightthickness=1, highlightbackground=COLOR_PINK_LIGHT)
        card_input.pack(fill="x", pady=5)
        
        # Configuração estética comum para as caixas de texto pastel
        input_style = {"font": FONT_BODY, "bg": "#FFF9FA", "fg": COLOR_TEXT, "relief": "flat", 
                       "highlightthickness": 1, "highlightbackground": COLOR_PINK_LIGHT}

        # Campo 1: Nome da Missão
        tk.Label(card_input, text="✨ Nome da Missão Mágica:", font=("Trebuchet MS", 9, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT).pack(anchor="w")
        self.entry_task = tk.Entry(card_input, **input_style)
        self.entry_task.pack(fill="x", pady=(2, 8), ipady=3)

        # Campo 2: Descrição / Prazo
        tk.Label(card_input, text="📅 Detalhes & Prazo (ex: Prova na terça):", font=("Trebuchet MS", 9, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT).pack(anchor="w")
        self.entry_desc = tk.Entry(card_input, **input_style)
        self.entry_desc.pack(fill="x", pady=(2, 8), ipady=3)

        # Campo 3: Subtarefas
        tk.Label(card_input, text="🌸 Subtarefas (Separe por vírgula):", font=("Trebuchet MS", 9, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT).pack(anchor="w")
        self.entry_sub = tk.Entry(card_input, **input_style)
        self.entry_sub.pack(fill="x", pady=(2, 8), ipady=3)

        # Campo 4: Atributo Combobox
        tk.Label(card_input, text="🔮 Atributo Cósmico Correspondente:", font=("Trebuchet MS", 9, "bold"), bg=COLOR_CARD, fg=COLOR_TEXT).pack(anchor="w")
        self.combo_skill = ttk.Combobox(card_input, values=list(self.skills.keys()), state="readonly", font=FONT_BODY)
        self.combo_skill.current(0)
        self.combo_skill.pack(fill="x", pady=(2, 10))

        # Botão Invocar Missão
        btn_add = tk.Button(card_input, text="✦ Invocar Missão Cósmica ✦", bg=COLOR_PINK_LIGHT, fg=COLOR_TEXT, font=FONT_SUBTITLE, relief="flat", command=self.add_task)
        btn_add.pack(fill="x", pady=2, ipady=2)
        self.apply_hover(btn_add, COLOR_PINK_BRIGHT, COLOR_PINK_LIGHT)

        tk.Label(f_right, text="✨ Clique duplo na missão para abrir os detalhes e caixas de marcação!", font=("Trebuchet MS", 8, "italic"), bg=COLOR_BG, fg=COLOR_TEXT).pack(pady=5)

        # Listbox das Missões Ativas
        self.listbox_tasks = tk.Listbox(f_right, font=FONT_BODY, bd=1, bg=COLOR_CARD, relief="solid", selectbackground=COLOR_PINK_LIGHT, highlightthickness=0)
        self.listbox_tasks.pack(fill="both", expand=True)
        self.listbox_tasks.bind("<Double-1>", self.open_task_modal) 

        # Botão de Conclusão Principal
        btn_done = tk.Button(f_right, text="💖 Concluir Missão Principal 💖", bg=COLOR_PINK_BRIGHT, fg="white", font=FONT_SUBTITLE, relief="flat", command=self.complete_task)
        btn_done.pack(fill="x", pady=5)
        self.apply_hover(btn_done, "#FF5C8A", COLOR_PINK_BRIGHT)
        
        self.render_tasks_list()

    def update_status_display(self):
        total_xp = sum(self.skills.values())
        XP_PER_LEVEL = 30
        level = 1 + (total_xp // XP_PER_LEVEL)
        xp_in_level = total_xp % XP_PER_LEVEL
        percent = (xp_in_level / XP_PER_LEVEL) * 100

        self.lbl_level.config(text=f"NÍVEL {level}")
        self.update_progress_bar(percent)
        self.lbl_xp_info.config(text=f"{xp_in_level} / {XP_PER_LEVEL} XP para o próximo nível")
        self.lbl_coins_top.config(text=f"🪙 {self.moon_coins} Moedas")

        for s, v in self.skills.items():
            self.skill_labels[s].config(text=f"{s}: {v}")

        if level >= 5: self.lbl_mascot.config(text="🌙 Super Luna"); self.lbl_mascot_msg.config(text="Seu poder é magnífico!")
        elif level >= 3: self.lbl_mascot.config(text="🐈 Luna Atenta"); self.lbl_mascot_msg.config(text="Você está evoluindo!")
        else: self.lbl_mascot.config(text="🐈 Luna"); self.lbl_mascot_msg.config(text="Pronta para brilhar?")

        self.draw_chart()

    def add_task(self):
        t = self.entry_task.get().strip()
        if not t: 
            messagebox.showwarning("Aviso!", "Dê um nome para a sua Missão! 🎀")
            return
        
        desc = self.entry_desc.get().strip()
        if not desc: desc = "Sem detalhes informados."

        sub_str = self.entry_sub.get().strip()
        subs = []
        if sub_str:
            subs = [{"name": s.strip(), "done": False} for s in sub_str.split(",") if s.strip()]

        self.tasks.append({
            "title": t, 
            "desc": desc,
            "skill": self.combo_skill.get(), 
            "xp": 10,
            "subtasks": subs
        })
        
        self.entry_task.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.entry_sub.delete(0, tk.END)
        
        self.render_tasks_list()
        self.save_data()

    def render_tasks_list(self):
        self.listbox_tasks.delete(0, tk.END)
        for t in self.tasks: 
            self.listbox_tasks.insert(tk.END, f" ✦ {t['title']} ({t['skill'].split(' ')[0]})")

    def complete_task(self):
        try:
            idx = self.listbox_tasks.curselection()[0]
            task = self.tasks.pop(idx)
            
            total_xp_antes = sum(self.skills.values())
            level_antes = 1 + (total_xp_antes // 30)

            self.skills[task['skill']] += 10
            self.moon_coins += 15
            
            total_xp_depois = sum(self.skills.values())
            level_depois = 1 + (total_xp_depois // 30)

            if level_depois > level_antes:
                self.play_sound("levelup")
            else:
                self.play_sound("tarefa")

            self.update_status_display()
            self.render_tasks_list()
            self.save_data()
        except: pass

    def open_task_modal(self, event):
        selection = self.listbox_tasks.curselection()
        if not selection: return
        idx = selection[0]
        task = self.tasks[idx]

        top = tk.Toplevel(self.root)
        top.title("Detalhes da Missão")
        top.geometry("400x400")
        top.configure(bg=COLOR_CARD)
        top.grab_set() 

        tk.Label(top, text=task["title"], font=("Gabriola", 18, "bold"), fg=COLOR_PINK_BRIGHT, bg=COLOR_CARD).pack(pady=10)
        tk.Label(top, text=f"📝 Detalhes/Prazo: {task.get('desc', 'Sem descrição')}", font=FONT_BODY, bg=COLOR_CARD, fg=COLOR_TEXT, wraplength=350).pack(pady=5)
        
        tk.Label(top, text="Subtarefas:", font=FONT_SUBTITLE, bg=COLOR_CARD, fg=COLOR_TEXT).pack(pady=10)

        frame_subs = tk.Frame(top, bg=COLOR_CARD)
        frame_subs.pack(fill="both", expand=True, padx=20)

        sub_vars = []
        for i, sub in enumerate(task.get("subtasks", [])):
            var = tk.BooleanVar(value=sub["done"])
            chk = tk.Checkbutton(frame_subs, text=sub["name"], variable=var, bg=COLOR_CARD, font=FONT_BODY, 
                                 activebackground=COLOR_CARD, command=lambda i=i, var=var: self.toggle_subtask(idx, i, var))
            chk.pack(anchor="w")
            sub_vars.append(var)

        if not task.get("subtasks"):
            tk.Label(frame_subs, text="Nenhuma subtarefa registrada.", font=("Trebuchet MS", 9, "italic"), bg=COLOR_CARD, fg="gray").pack()

        tk.Button(top, text="Fechar 💖", bg=COLOR_PINK_LIGHT, fg=COLOR_TEXT, font=FONT_BODY, 
                  relief="flat", command=top.destroy).pack(pady=20)

    def toggle_subtask(self, task_idx, sub_idx, var):
        self.tasks[task_idx]["subtasks"][sub_idx]["done"] = var.get()
        self.save_data()

    # ================= TAB 2: LOJA (SISTEMA DE LISTA) =================
    def setup_store_tab(self):
        tk.Label(self.tab_store, text="💖 LOJINHA CÓSMICA 💖", font=FONT_TITLE, bg=COLOR_BG).pack(pady=10)
        
        # Área de criação de recompensa personalizada
        f_custom = tk.Frame(self.tab_store, bg=COLOR_PURPLE_SOFT, bd=1, relief="solid", padx=10, pady=10)
        f_custom.pack(fill="x", padx=50, pady=10)
        
        tk.Label(f_custom, text="Criar Recompensa Personalizada ✨", font=FONT_SUBTITLE, bg=COLOR_PURPLE_SOFT, fg=COLOR_TEXT).pack()
        tk.Label(f_custom, text="Escreva o item desejado para colocá-lo na lista por 50 moedas!", font=FONT_BODY, bg=COLOR_PURPLE_SOFT, fg=COLOR_TEXT).pack()
        
        self.entry_custom_reward = tk.Entry(f_custom, font=FONT_BODY, width=30)
        self.entry_custom_reward.pack(pady=5)
        
        # AGORA ADICIONA À LOJA EM VEZ DE COMPRAR DIRETO
        btn_custom = tk.Button(f_custom, text="✨ Adicionar à Lojinha (50 🌙) ✨", bg=COLOR_PINK_LIGHT, fg=COLOR_TEXT, font=FONT_BODY, relief="flat", command=self.add_custom_reward)
        btn_custom.pack(pady=5)
        self.apply_hover(btn_custom, COLOR_PINK_BRIGHT, COLOR_PINK_LIGHT)

        self.create_magic_divider(self.tab_store)

        # Lista de itens à venda
        self.listbox_store = tk.Listbox(self.tab_store, font=FONT_BODY, bd=1, relief="solid")
        self.listbox_store.pack(fill="both", expand=True, padx=50, pady=10)
        
        btn_buy = tk.Button(self.tab_store, text="🛍 Comprar Recompensa Selecionada 🛍", bg=COLOR_PINK_BRIGHT, fg="white", font=FONT_SUBTITLE, relief="flat", command=self.buy_item)
        btn_buy.pack(pady=10)
        self.apply_hover(btn_buy, "#FF5C8A", COLOR_PINK_BRIGHT)
        self.render_store()

    def add_custom_reward(self):
        recompensa = self.entry_custom_reward.get().strip()
        if not recompensa:
            messagebox.showwarning("Aviso!", "Escreva o nome do prêmio primeiro! 🎀")
            return

        # Insere na lista e salva
        self.rewards.append({"title": recompensa, "cost": 50})
        self.render_store()
        self.save_data()
        
        messagebox.showinfo("Lojinha Expandida! ✨", f"Sucesso! '{recompensa}' agora está disponível para compra na vitrine!")
        self.entry_custom_reward.delete(0, tk.END)

    def render_store(self):
        self.listbox_store.delete(0, tk.END)
        for r in self.rewards: self.listbox_store.insert(tk.END, f" 🪙 {r['cost']} Moedas - {r['title']}")

    def buy_item(self):
        try:
            idx = self.listbox_store.curselection()[0]
            item = self.rewards[idx]
            if self.moon_coins >= item['cost']:
                self.moon_coins -= item['cost']
                self.play_sound("compra") 
                self.update_status_display()
                self.save_data()
                messagebox.showinfo("Sucesso!", f"Você resgatou: {item['title']} ✨\nAproveite seu merecido prêmio!")
            else:
                messagebox.showerror("Aviso", "Você não tem Moedas Lunares suficientes para este item! 🥺")
        except: 
            messagebox.showwarning("Aviso", "Selecione um item da vitrine para comprar!")

    # ================= TAB 3: NOTAS (MÉDIA) =================
    def setup_grades_tab(self):
        f_grades = tk.Frame(self.tab_grades, bg=COLOR_CARD, bd=1, relief="solid", padx=20, pady=20)
        f_grades.pack(pady=30, padx=50, fill="both", expand=True)

        tk.Label(f_grades, text="Cristal das Notas 📚", font=FONT_TITLE, fg=COLOR_PINK_BRIGHT, bg=COLOR_CARD).pack(pady=10)
        tk.Label(f_grades, text="Quiz (20%) | PTI (20%) | Prova (60%)", font=FONT_BODY, bg=COLOR_CARD, fg=COLOR_TEXT).pack()

        tk.Label(f_grades, text="Nota do Quiz (0 a 10):", bg=COLOR_CARD, font=FONT_SUBTITLE).pack(pady=(15,0))
        self.entry_quiz = tk.Entry(f_grades, font=FONT_BODY, justify="center")
        self.entry_quiz.pack()

        tk.Label(f_grades, text="Nota do PTI (0 a 10):", bg=COLOR_CARD, font=FONT_SUBTITLE).pack(pady=(10,0))
        self.entry_pti = tk.Entry(f_grades, font=FONT_BODY, justify="center")
        self.entry_pti.pack()

        tk.Label(f_grades, text="Nota da Prova Presencial (0 a 10):", bg=COLOR_CARD, font=FONT_SUBTITLE).pack(pady=(10,0))
        self.entry_prova = tk.Entry(f_grades, font=FONT_BODY, justify="center")
        self.entry_prova.pack()
        tk.Label(f_grades, text="*Deixe a prova em branco para saber quanto precisa tirar", font=("Trebuchet MS", 8, "italic"), bg=COLOR_CARD, fg="gray").pack()

        btn_calc = tk.Button(f_grades, text="Calcular Magia! ✨", bg=COLOR_PINK_BRIGHT, fg="white", 
                             font=FONT_SUBTITLE, relief="flat", command=self.calcular_notas)
        btn_calc.pack(pady=20)
        self.apply_hover(btn_calc, "#FF5C8A", COLOR_PINK_BRIGHT)

        self.lbl_resultado_notas = tk.Label(f_grades, text="", font=FONT_SUBTITLE, bg=COLOR_CARD, fg=COLOR_PINK_BRIGHT)
        self.lbl_resultado_notas.pack()

    def calcular_notas(self):
        q_str = self.entry_quiz.get().replace(',', '.')
        p_str = self.entry_pti.get().replace(',', '.')
        prova_str = self.entry_prova.get().replace(',', '.')

        try:
            quiz = float(q_str) if q_str else None
            pti = float(p_str) if p_str else None
            prova = float(prova_str) if prova_str else None

            if quiz is not None and pti is not None and prova is not None:
                media = (quiz * 0.2) + (pti * 0.2) + (prova * 0.6)
                if media >= 6.0:
                    texto = f"Sua Média: {media:.2f}\nStatus: APROVADO! 🎉💖"
                    cor = "#32cd32"
                elif media < 5.7:
                    texto = f"Sua Média: {media:.2f}\nStatus: Prova de Recuperação 🥺"
                    cor = "#ff4500"
                else:
                    texto = f"Sua Média: {media:.2f}\nStatus: Quase lá (Consulte o professor!)"
                    cor = "#ff8c00"
                self.lbl_resultado_notas.config(text=texto, fg=cor)

            elif quiz is not None and pti is not None and prova is None:
                nota_necessaria = (6.0 - (quiz * 0.2) - (pti * 0.2)) / 0.6
                if nota_necessaria > 10:
                    texto = f"Precisaria de {nota_necessaria:.2f} na prova.\nInfelizmente já está na recuperação! 🌙"
                elif nota_necessaria <= 0:
                    texto = "Você já passou só com o Quiz e PTI! 🎉"
                else:
                    texto = f"Você precisa tirar pelo menos:\n{nota_necessaria:.2f}\nna Prova Presencial para passar! 📖✨"
                self.lbl_resultado_notas.config(text=texto, fg=COLOR_PINK_BRIGHT)
            else:
                self.lbl_resultado_notas.config(text="Preencha pelo menos Quiz e PTI!", fg="red")
        except ValueError:
            self.lbl_resultado_notas.config(text="Erro! Digite apenas números válidos.", fg="red")

    # ================= POMODORO & CLOCK =================
    def setup_pomodoro_tab(self):
        self.pomo_focus_min = 25
        self.pomo_break_min = 5
        self.time_left = self.pomo_focus_min * 60
        self.timer_running = False
        self.is_break = False
        self.cycles = 0

        self.lbl_pomo_title = tk.Label(self.tab_pomodoro, text="🌙 Foco Lunar", font=FONT_TITLE, bg=COLOR_BG, fg=COLOR_PINK_BRIGHT)
        self.lbl_pomo_title.pack(pady=(20, 5))

        self.lbl_cycles = tk.Label(self.tab_pomodoro, text="Ciclos Concluídos: 0", font=FONT_SUBTITLE, bg=COLOR_BG, fg=COLOR_TEXT)
        self.lbl_cycles.pack()

        self.lbl_pomo = tk.Label(self.tab_pomodoro, text=f"{self.pomo_focus_min:02d}:00", font=("Trebuchet MS", 60, "bold"), bg=COLOR_BG, fg=COLOR_PINK_BRIGHT)
        self.lbl_pomo.pack(pady=20)

        f_adjust = tk.Frame(self.tab_pomodoro, bg=COLOR_BG)
        f_adjust.pack(pady=10)

        f_focus = tk.Frame(f_adjust, bg=COLOR_BG)
        f_focus.pack(side="left", padx=20)
        tk.Label(f_focus, text="Tempo de Foco", font=FONT_BODY, bg=COLOR_BG, fg=COLOR_TEXT).pack()
        f_f_btns = tk.Frame(f_focus, bg=COLOR_BG)
        f_f_btns.pack()
        tk.Button(f_f_btns, text="- 5", font=("Trebuchet MS", 10, "bold"), bg=COLOR_PINK_LIGHT, fg=COLOR_TEXT, relief="flat", command=lambda: self.adjust_time('focus', -5)).pack(side="left", padx=2)
        self.lbl_focus_val = tk.Label(f_f_btns, text=f"{self.pomo_focus_min} min", font=FONT_BODY, bg=COLOR_BG, fg=COLOR_TEXT, width=6)
        self.lbl_focus_val.pack(side="left")
        tk.Button(f_f_btns, text="+ 5", font=("Trebuchet MS", 10, "bold"), bg=COLOR_PINK_LIGHT, fg=COLOR_TEXT, relief="flat", command=lambda: self.adjust_time('focus', 5)).pack(side="left", padx=2)

        f_break = tk.Frame(f_adjust, bg=COLOR_BG)
        f_break.pack(side="left", padx=20)
        tk.Label(f_break, text="Tempo de Pausa", font=FONT_BODY, bg=COLOR_BG, fg=COLOR_TEXT).pack()
        f_b_btns = tk.Frame(f_break, bg=COLOR_BG)
        f_b_btns.pack()
        tk.Button(f_b_btns, text="- 5", font=("Trebuchet MS", 10, "bold"), bg=COLOR_PINK_LIGHT, fg=COLOR_TEXT, relief="flat", command=lambda: self.adjust_time('break', -5)).pack(side="left", padx=2)
        self.lbl_break_val = tk.Label(f_b_btns, text=f"{self.pomo_break_min} min", font=FONT_BODY, bg=COLOR_BG, fg=COLOR_TEXT, width=6)
        self.lbl_break_val.pack(side="left")
        tk.Button(f_b_btns, text="+ 5", font=("Trebuchet MS", 10, "bold"), bg=COLOR_PINK_LIGHT, fg=COLOR_TEXT, relief="flat", command=lambda: self.adjust_time('break', 5)).pack(side="left", padx=2)

        f_controls = tk.Frame(self.tab_pomodoro, bg=COLOR_BG)
        f_controls.pack(pady=30)

        self.btn_start = tk.Button(f_controls, text="▶ Iniciar", font=FONT_SUBTITLE, bg=COLOR_PINK_LIGHT, fg=COLOR_TEXT, relief="flat", command=self.start_pomo, width=10)
        self.btn_start.pack(side="left", padx=10)
        self.apply_hover(self.btn_start, COLOR_PINK_BRIGHT, COLOR_PINK_LIGHT)

        self.btn_pause = tk.Button(f_controls, text="⏸ Pausar", font=FONT_SUBTITLE, bg=COLOR_PINK_LIGHT, fg=COLOR_TEXT, relief="flat", command=self.pause_pomo, width=10)
        self.btn_pause.pack(side="left", padx=10)
        self.apply_hover(self.btn_pause, COLOR_PINK_BRIGHT, COLOR_PINK_LIGHT)

        self.btn_reset = tk.Button(f_controls, text="🔄 Resetar", font=FONT_SUBTITLE, bg=COLOR_PINK_LIGHT, fg=COLOR_TEXT, relief="flat", command=self.reset_pomo, width=10)
        self.btn_reset.pack(side="left", padx=10)
        self.apply_hover(self.btn_reset, COLOR_PINK_BRIGHT, COLOR_PINK_LIGHT)

    def adjust_time(self, timer_type, amount):
        if timer_type == 'focus':
            self.pomo_focus_min = max(5, self.pomo_focus_min + amount)
            self.lbl_focus_val.config(text=f"{self.pomo_focus_min} min")
            if not self.timer_running and not self.is_break:
                self.time_left = self.pomo_focus_min * 60
                self.update_pomo_display()
        else:
            self.pomo_break_min = max(5, self.pomo_break_min + amount)
            self.lbl_break_val.config(text=f"{self.pomo_break_min} min")
            if not self.timer_running and self.is_break:
                self.time_left = self.pomo_break_min * 60
                self.update_pomo_display()

    def update_pomo_display(self):
        m, s = divmod(self.time_left, 60)
        self.lbl_pomo.config(text=f"{m:02d}:{s:02d}")

    def start_pomo(self):
        if not self.timer_running:
            self.timer_running = True
            self.run_pomo()

    def pause_pomo(self):
        self.timer_running = False

    def reset_pomo(self):
        self.timer_running = False
        self.is_break = False
        self.time_left = self.pomo_focus_min * 60
        self.lbl_pomo_title.config(text="🌙 Foco Lunar", fg=COLOR_PINK_BRIGHT)
        self.update_pomo_display()

    def run_pomo(self):
        if self.timer_running and self.time_left > 0:
            self.time_left -= 1
            self.update_pomo_display()
            self.root.after(1000, self.run_pomo)
        elif self.timer_running and self.time_left == 0:
            self.timer_running = False
            self.play_sound("pomodoro_end") 
            
            if not self.is_break:
                self.cycles += 1
                self.lbl_cycles.config(text=f"Ciclos Concluídos: {self.cycles}")
                self.is_break = True
                self.time_left = self.pomo_break_min * 60
                self.lbl_pomo_title.config(text="☕ Pausa Restauradora", fg="#4CAF50") 
                self.update_pomo_display()
                messagebox.showinfo("Pomodoro", "Ciclo de foco concluído! Hora de descansar um pouco. ✨")
            else:
                self.is_break = False
                self.time_left = self.pomo_focus_min * 60
                self.lbl_pomo_title.config(text="🌙 Foco Lunar", fg=COLOR_PINK_BRIGHT)
                self.update_pomo_display()
                messagebox.showinfo("Pomodoro", "Pausa terminada! Vamos voltar ao foco? 🚀")

    def update_live_clock(self):
        self.root.after(1000, self.update_live_clock)

    # ================= CHARTS =================
    def setup_charts_tab(self):
        tk.Label(self.tab_charts, text="📊 DISTRIBUIÇÃO DE PODER", font=FONT_TITLE, bg=COLOR_BG).pack(pady=20)
        self.canvas_chart = tk.Canvas(self.tab_charts, bg=COLOR_CARD, width=450, height=300, highlightthickness=1, highlightbackground=COLOR_PINK_LIGHT)
        self.canvas_chart.pack(pady=10)
        self.draw_chart()

    def draw_chart(self):
        self.canvas_chart.delete("all")
        width = 450
        height = 300
        bar_colors = ["#FFB6C1", "#87CEFA", "#98FB98", "#DDA0DD"]
        max_val = max(list(self.skills.values()) + [10]) 
        
        num_bars = len(self.skills)
        if num_bars == 0: return
        
        bar_width = width / num_bars
        
        for i, (skill, val) in enumerate(self.skills.items()):
            x0 = i * bar_width + 30
            y0 = height - (val / max_val * (height - 60)) - 30
            x1 = x0 + bar_width - 50
            y1 = height - 30
            
            self.canvas_chart.create_rectangle(x0, y0, x1, y1, fill=bar_colors[i%len(bar_colors)], outline=COLOR_PINK_BRIGHT, width=2)
            nome_curto = skill.split(" ")[0]
            self.canvas_chart.create_text((x0+x1)/2, y1 + 15, text=nome_curto, font=("Trebuchet MS", 10, "bold"), fill=COLOR_TEXT)
            self.canvas_chart.create_text((x0+x1)/2, y0 - 10, text=f"{val} XP", font=("Trebuchet MS", 9), fill=COLOR_TEXT)

if __name__ == "__main__":
    root = tk.Tk()
    app = SailorTasksApp(root)
    root.mainloop()