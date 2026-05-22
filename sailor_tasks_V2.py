import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime

# Tenta importar o pygame para o som.
try:
    import pygame
    PYGAME_OK = True
except ImportError:
    PYGAME_OK = False

# Determina a pasta exata onde este script está salvo para nunca errar o caminho do áudio
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- PALETA DE CORES SAILOR MOON PASTEL ---
COLOR_BG = "#FFF0F5"         # Lavender Blush (Fundo Geral)
COLOR_CARD = "#FFFFFF"       # Branco para os cards
COLOR_PINK = "#FFB6C1"       # Light Pink (Botões e Destaques)
COLOR_DARK_PINK = "#FF69B4"  # Hot Pink (Texto importante)
COLOR_PURPLE = "#E6E6FA"     # Lavender (Abas e detalhes)
COLOR_TEXT = "#4A4A4A"       # Cinza escuro para leitura confortável
DATA_FILE = os.path.join(BASE_DIR, "sailor_tasks_data.json")

class SailorTasksApp:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ Sailor Tasks PRO: Evolução Cósmica! ✨")
        self.root.geometry("850x700")
        self.root.configure(bg=COLOR_BG)

        # --- INICIALIZAR ÁUDIO ---
        if PYGAME_OK:
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"Aviso: Não foi possível inicializar o mixer do Pygame: {e}")

        # --- CARREGAR DADOS (PERSISTÊNCIA) ---
        self.load_data()

        # --- CONFIGURAÇÃO DE ESTILO ---
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=COLOR_PURPLE, foreground=COLOR_TEXT, padding=[15, 5], font=("Courier", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", COLOR_PINK)], foreground=[("selected", "white")])

        # --- ABAS ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_status = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_pomodoro = tk.Frame(self.notebook, bg=COLOR_BG)

        self.notebook.add(self.tab_status, text="🌙 Missões & Atributos")
        self.notebook.add(self.tab_pomodoro, text="⏱️ Relógio Cósmico (Pomodoro)")

        self.setup_status_tab()
        self.setup_pomodoro_tab()
        self.update_status_display()
        self.update_live_clock()

    # ================= PERSISTÊNCIA DE DADOS (JSON) =================
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.skills = data.get("skills", {
                        "Mente (Estudos/Foco)": 0,
                        "Corpo (Saúde/Exercício)": 0,
                        "Alma (Criatividade/Lazer)": 0,
                        "Ordem (Organização/Casa)": 0
                    })
                    self.tasks = data.get("tasks", [])
            except:
                self.init_default_data()
        else:
            self.init_default_data()

    def init_default_data(self):
        self.skills = {
            "Mente (Estudos/Foco)": 0,
            "Corpo (Saúde/Exercício)": 0,
            "Alma (Criatividade/Lazer)": 0,
            "Ordem (Organização/Casa)": 0
        }
        self.tasks = [
            {
                "title": "📚 Prova Importante",
                "desc": "Revisar todo o conteúdo para o exame",
                "skill": "Mente (Estudos/Foco)",
                "deadline": "27/05/2026 13:30"
            }
        ]

    def save_data(self):
        data = {
            "skills": self.skills,
            "tasks": self.tasks
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # ================= CONTROLE DE ÁUDIO REFORÇADO =================
    def play_sound(self, name_without_ext):
        sound_played = False
        if PYGAME_OK:
            for ext in [".mp3", ".wav", ".ogg"]:
                full_path = os.path.join(BASE_DIR, name_without_ext + ext)
                if os.path.exists(full_path):
                    try:
                        snd = pygame.mixer.Sound(full_path)
                        snd.play()
                        sound_played = True
                        break
                    except Exception as e:
                        print(f"👉 Erro do Pygame com {name_without_ext}{ext}: {e}")
        
        if not sound_played:
            try:
                import winsound
                full_path_wav = os.path.join(BASE_DIR, name_without_ext + ".wav")
                if os.path.exists(full_path_wav):
                    winsound.PlaySound(full_path_wav, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    sound_played = True
            except:
                pass
        
        if not sound_played:
            self.root.bell()

    # ================= SISTEMA DE POP-UPS KAWAII CUSTOMIZADOS =================
    def show_kawaii_popup(self, title, message, mode="info"):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("440x220")
        dialog.configure(bg=COLOR_BG)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centralizar na tela relativo ao app principal
        rx = self.root.winfo_x()
        ry = self.root.winfo_y()
        dialog.geometry(f"+{rx + 205}+{ry + 240}")
        
        frame = tk.Frame(dialog, bg=COLOR_CARD, bd=2, relief="flat", highlightbackground=COLOR_PINK, highlightthickness=2)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        icon_text = "✨💖 Success! 💖✨" if mode == "info" else "🔮⚠️ Alerta de Luna! ⚠️🔮"
        lbl_icon = tk.Label(frame, text=icon_text, bg=COLOR_CARD, fg=COLOR_DARK_PINK, font=("Courier", 12, "bold"))
        lbl_icon.pack(pady=8)
        
        lbl_msg = tk.Label(frame, text=message, bg=COLOR_CARD, fg=COLOR_TEXT, font=("Courier", 10, "bold"), wraplength=360, justify="center")
        lbl_msg.pack(pady=10, fill="both", expand=True)
        
        btn_ok = tk.Button(frame, text="✨ Entendido! ✨", bg=COLOR_PINK, fg="white", font=("Courier", 10, "bold"), relief="flat", padx=20, pady=3, command=dialog.destroy)
        btn_ok.pack(pady=5)
        
        self.root.wait_window(dialog)

    def ask_kawaii_confirm(self, title, message):
        self.confirm_result = False
        
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("440x220")
        dialog.configure(bg=COLOR_BG)
        dialog.transient(self.root)
        dialog.grab_set()
        
        rx = self.root.winfo_x()
        ry = self.root.winfo_y()
        dialog.geometry(f"+{rx + 205}+{ry + 240}")
        
        frame = tk.Frame(dialog, bg=COLOR_CARD, bd=2, relief="flat", highlightbackground=COLOR_DARK_PINK, highlightthickness=2)
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        lbl_icon = tk.Label(frame, text="🔮 Decisão Cósmica 🔮", bg=COLOR_CARD, fg=COLOR_DARK_PINK, font=("Courier", 12, "bold"))
        lbl_icon.pack(pady=8)
        
        lbl_msg = tk.Label(frame, text=message, bg=COLOR_CARD, fg=COLOR_TEXT, font=("Courier", 10, "bold"), wraplength=360, justify="center")
        lbl_msg.pack(pady=10, fill="both", expand=True)
        
        frame_btns = tk.Frame(frame, bg=COLOR_CARD)
        frame_btns.pack(pady=5)
        
        def yes_action():
            self.confirm_result = True
            dialog.destroy()
            
        def no_action():
            self.confirm_result = False
            dialog.destroy()
            
        btn_yes = tk.Button(frame_btns, text="💖 Sim, Luna! 💖", bg=COLOR_DARK_PINK, fg="white", font=("Courier", 10, "bold"), relief="flat", padx=15, pady=3, command=yes_action)
        btn_yes.pack(side="left", padx=10)
        
        btn_no = tk.Button(frame_btns, text="🌸 Cancelar 🌸", bg=COLOR_PURPLE, fg=COLOR_TEXT, font=("Courier", 10, "bold"), relief="flat", padx=15, pady=3, command=no_action)
        btn_no.pack(side="left", padx=10)
        
        self.root.wait_window(dialog)
        return self.confirm_result

    # ================= TAB 1: MISSÕES & STATUS =================
    def setup_status_tab(self):
        frame_status = tk.LabelFrame(self.tab_status, text="🌟 Status da Guerreira", bg=COLOR_CARD, fg=COLOR_DARK_PINK, font=("Courier", 12, "bold"), padx=15, pady=15)
        frame_status.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.lbl_level = tk.Label(frame_status, text="✨ NÍVEL 1 ✨", bg=COLOR_PURPLE, fg=COLOR_DARK_PINK, font=("Courier", 16, "bold"), padx=10, pady=10)
        self.lbl_level.pack(fill="x", pady=10)

        self.lbl_total_xp = tk.Label(frame_status, text="XP Total: 0", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Courier", 10, "italic"))
        self.lbl_total_xp.pack(anchor="w", pady=2)

        canvas = tk.Canvas(frame_status, height=2, bg=COLOR_BG, bd=0, highlightthickness=0)
        canvas.pack(fill="x", pady=10)

        self.skill_labels = {}
        for skill in self.skills.keys():
            lbl = tk.Label(frame_status, text=f"{skill}: 0 XP", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Courier", 11))
            lbl.pack(anchor="w", pady=5)
            self.skill_labels[skill] = lbl

        btn_reset_xp = tk.Button(frame_status, text="🌌 Resetar Atributos (Zerar) 🌌", bg="#FFCDD2", fg="#B71C1C", font=("Courier", 9, "bold"), relief="flat", pady=5, command=self.reset_progress)
        btn_reset_xp.pack(fill="x", side="bottom", pady=5)

        frame_tasks = tk.Frame(self.tab_status, bg=COLOR_BG)
        frame_tasks.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        lbl_titulo = tk.Label(frame_tasks, text="Nova Missão:", bg=COLOR_BG, fg=COLOR_DARK_PINK, font=("Courier", 11, "bold"))
        lbl_titulo.pack(anchor="w")
        self.entry_task = tk.Entry(frame_tasks, font=("Arial", 10), bd=2, relief="flat")
        self.entry_task.pack(fill="x", pady=2)

        lbl_desc = tk.Label(frame_tasks, text="Descrição / Subtarefas:", bg=COLOR_BG, fg=COLOR_DARK_PINK, font=("Courier", 10))
        lbl_desc.pack(anchor="w")
        self.entry_desc = tk.Entry(frame_tasks, font=("Arial", 10), bd=2, relief="flat")
        self.entry_desc.pack(fill="x", pady=2) # CORRIGIDO AQUI: py=2 mudado para pady=2!

        lbl_deadline = tk.Label(frame_tasks, text="Prazo / Data (Ex: DD/MM/AAAA HH:MM):", bg=COLOR_BG, fg=COLOR_DARK_PINK, font=("Courier", 10))
        lbl_deadline.pack(anchor="w")
        self.entry_deadline = tk.Entry(frame_tasks, font=("Arial", 10), bd=2, relief="flat")
        self.entry_deadline.pack(fill="x", pady=2)

        lbl_combo = tk.Label(frame_tasks, text="Atributo que vai treinar:", bg=COLOR_BG, fg=COLOR_DARK_PINK, font=("Courier", 10))
        lbl_combo.pack(anchor="w")
        self.combo_skill = ttk.Combobox(frame_tasks, values=list(self.skills.keys()), state="readonly")
        self.combo_skill.current(0)
        self.combo_skill.pack(fill="x", pady=2)

        btn_add = tk.Button(frame_tasks, text="✨ Invocar Missão ✨", bg=COLOR_PINK, fg="white", font=("Courier", 10, "bold"), relief="flat", command=self.add_task)
        btn_add.pack(fill="x", pady=10)

        lbl_lista = tk.Label(frame_tasks, text="📜 Mural de Missões Ativas", bg=COLOR_BG, fg=COLOR_DARK_PINK, font=("Courier", 11, "bold"))
        lbl_lista.pack(anchor="w")

        self.listbox_tasks = tk.Listbox(frame_tasks, font=("Arial", 10), bd=0, bg=COLOR_CARD, selectbackground=COLOR_PINK)
        self.listbox_tasks.pack(fill="both", expand=True, pady=5)

        self.render_tasks_list()

        btn_complete = tk.Button(frame_tasks, text="💖 Concluir Missão (Ganhar XP) 💖", bg=COLOR_DARK_PINK, fg="white", font=("Courier", 11, "bold"), relief="flat", command=self.complete_task)
        btn_complete.pack(fill="x", pady=5)

    def update_status_display(self):
        for skill, value in self.skills.items():
            self.skill_labels[skill].config(text=f"{skill}: {value} XP")
        
        total_xp = sum(self.skills.values())
        XP_PER_LEVEL = 30 
        self.current_level = 1 + (total_xp // XP_PER_LEVEL)
        xp_para_proximo = XP_PER_LEVEL - (total_xp % XP_PER_LEVEL)

        self.lbl_level.config(text=f"✨ SAILOR NÍVEL: {self.current_level} ✨")
        self.lbl_total_xp.config(text=f"XP Total: {total_xp} | Faltam {xp_para_proximo} XP para o próximo nível!")

    def render_tasks_list(self):
        self.listbox_tasks.delete(0, tk.END)
        for task in self.tasks:
            prazo = f" [Prazo: {task['deadline']}]" if task.get('deadline') else ""
            display_text = f"[{task['skill'].split(' ')[0]}] {task['title']} - {task['desc']}{prazo}"
            self.listbox_tasks.insert(tk.END, display_text)

    def add_task(self):
        title = self.entry_task.get()
        desc = self.entry_desc.get()
        skill = self.combo_skill.get()
        deadline = self.entry_deadline.get()

        if title == "":
            self.show_kawaii_popup("Aviso Luna", "Sua missão precisa de um nome, guerreira!", mode="warning")
            return

        task_data = {"title": title, "desc": desc, "skill": skill, "deadline": deadline}
        self.tasks.append(task_data)
        
        self.render_tasks_list()
        self.save_data() 

        self.entry_task.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.entry_deadline.delete(0, tk.END)

    def complete_task(self):
        try:
            selected_index = self.listbox_tasks.curselection()[0]
            task = self.tasks.pop(selected_index)
            
            old_level = self.current_level
            skill_up = task["skill"]
            self.skills[skill_up] += 10
            
            self.update_status_display()
            
            if self.current_level > old_level:
                self.play_sound("levelup")
                self.show_kawaii_popup("✨ EVOLUÇÃO CÓSMICA ✨", f"PELO PODER DO PRISMA LUNAR!\n\nVocê subiu para o NÍVEL {self.current_level}! 🎉🌟\nSuas energias estão aumentando!")
            else:
                self.play_sound("tarefa")
                self.show_kawaii_popup("Sucesso Mágico", f"Você concluiu '{task['title']}' com maestria e ganhou +10 XP em {skill_up}! 🎉")
                
            self.render_tasks_list()
            self.save_data() 
        except IndexError:
            self.show_kawaii_popup("Aviso Luna", "Selecione uma missão válida no mural para concluir!", mode="warning")

    def reset_progress(self):
        confirm = self.ask_kawaii_confirm("Confirmação Cósmica", "Guerreira, você tem certeza absoluta que deseja resetar seus níveis e apagar todo o seu progresso? 😱🔮")
        if confirm:
            for skill in self.skills.keys():
                self.skills[skill] = 0
            self.update_status_display()
            self.save_data()
            self.show_kawaii_popup("✨ Energias Resetadas ✨", "Suas habilidades cósmicas retornaram ao estado inicial!\nHora de recomeçar a sua jornada com tudo! 💪🌙")

    # ================= TAB 2: POMODORO =================
    def setup_pomodoro_tab(self):
        self.time_left = 25 * 60
        self.timer_running = False

        self.lbl_live_clock = tk.Label(self.tab_pomodoro, text="", bg=COLOR_BG, fg=COLOR_DARK_PINK, font=("Courier", 14, "bold"))
        self.lbl_live_clock.pack(pady=10)

        frame_timer = tk.Frame(self.tab_pomodoro, bg=COLOR_CARD, bd=0, padx=40, pady=30)
        frame_timer.pack(pady=20)

        frame_config = tk.Frame(frame_timer, bg=COLOR_CARD)
        frame_config.pack(pady=5)
        
        lbl_set_time = tk.Label(frame_config, text="Definir Tempo (min):", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Courier", 10, "bold"))
        lbl_set_time.pack(side="left", padx=5)
        
        self.spin_minutes = ttk.Spinbox(frame_config, from_=5, to=60, increment=5, width=5, font=("Courier", 11, "bold"), state="readonly", command=self.change_pomo_duration)
        self.spin_minutes.set(25)
        self.spin_minutes.pack(side="left", padx=5)

        self.lbl_timer = tk.Label(frame_timer, text="25:00", bg=COLOR_CARD, fg=COLOR_DARK_PINK, font=("Courier", 48, "bold"))
        self.lbl_timer.pack(pady=15)

        self.lbl_status_pomo = tk.Label(frame_timer, text="Pronta para focar?", bg=COLOR_CARD, fg=COLOR_TEXT, font=("Courier", 12, "italic"))
        self.lbl_status_pomo.pack(pady=5)

        btn_start = tk.Button(frame_timer, text="🌙 Iniciar", bg=COLOR_PINK, fg="white", font=("Courier", 11, "bold"), relief="flat", width=12, command=self.start_timer)
        btn_start.pack(side="left", padx=5, pady=10)

        btn_pause = tk.Button(frame_timer, text="⏸️ Pausar", bg=COLOR_PURPLE, fg=COLOR_TEXT, font=("Courier", 11, "bold"), relief="flat", width=9, command=self.pause_timer)
        btn_pause.pack(side="left", padx=5, pady=10)

        btn_reset = tk.Button(frame_timer, text="🔄 Reset", bg=COLOR_BG, fg=COLOR_TEXT, font=("Courier", 11, "bold"), relief="flat", width=9, command=self.reset_timer)
        btn_reset.pack(side="left", padx=5, pady=10)

    def update_live_clock(self):
        now = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        self.lbl_live_clock.config(text=f"💖 Horário Cósmico: {now} 💖")
        self.root.after(1000, self.update_live_clock)

    def change_pomo_duration(self):
        if not self.timer_running:
            mins = int(self.spin_minutes.get())
            self.time_left = mins * 60
            self.lbl_timer.config(text=f"{mins:02d}:00")

    def update_timer(self):
        if self.timer_running and self.time_left > 0:
            self.time_left -= 1
            mins, secs = divmod(self.time_left, 60)
            self.lbl_timer.config(text=f"{mins:02d}:{secs:02d}")
            self.root.after(1000, self.update_timer)
        elif self.time_left == 0 and self.timer_running:
            self.timer_running = False
            self.play_sound("levelup") 
            self.show_kawaii_popup("Fim do Turno Cósmico", "O tempo acabou! Descanse um pouco e recupere suas energias, guerreira! ✨")
            self.reset_timer()

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.lbl_status_pomo.config(text="Concentrando energia mágica...")
            self.update_timer()

    def pause_timer(self):
        self.timer_running = False
        self.lbl_status_pomo.config(text="Tempo congelado no espaço.")

    def reset_timer(self):
        self.timer_running = False
        mins = int(self.spin_minutes.get())
        self.time_left = mins * 60
        self.lbl_timer.config(text=f"{mins:02d}:00")
        self.lbl_status_pomo.config(text="Pronta para reiniciar o ciclo?")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    root = tk.Tk()
    app = SailorTasksApp(root)
    root.mainloop()