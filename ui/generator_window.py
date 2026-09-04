"""Генерация и ручная модерация материалов Qwen."""

import threading
import tkinter as tk
from tkinter import messagebox, ttk

from config import COLORS, FONTS
from learning.content_models import ContentValidationError
from llm.content_generator import ContentGenerator
from llm.providers import LLMUnavailableError, OllamaProvider


class GeneratorWindow:
    def __init__(self, parent, app):
        self.app, self.candidates = app, []
        self.window = tk.Toplevel(parent); self.window.title('Генератор материалов Qwen')
        self.window.geometry('780x600'); self.window.configure(bg=COLORS['light'])
        controls = tk.Frame(self.window, bg=COLORS['light']); controls.pack(fill='x', padx=15, pady=12)
        self.kind = tk.StringVar(value='word'); self.topic = tk.StringVar(value='Work')
        self.level = tk.StringVar(value=app.db.get_setting('user_level', 'A2')); self.count = tk.IntVar(value=5)
        self.exercise_type = tk.StringVar(value='grammar_gap')
        ttk.Combobox(controls, textvariable=self.kind, state='readonly', width=14,
                     values=('word', 'exercise')).pack(side='left', padx=4)
        tk.Entry(controls, textvariable=self.topic, width=20).pack(side='left', padx=4)
        ttk.Combobox(controls, textvariable=self.level, state='readonly', width=5,
                     values=('A1','A2','B1','B2','C1','C2')).pack(side='left', padx=4)
        tk.Spinbox(controls, from_=1, to=20, textvariable=self.count, width=4).pack(side='left', padx=4)
        ttk.Combobox(controls, textvariable=self.exercise_type, state='readonly', width=16,
                     values=('grammar_gap', 'translation_ru_en', 'find_tense',
                             'correct_error', 'build_sentence')).pack(side='left', padx=4)
        self.generate_button = tk.Button(controls, text='Сгенерировать', command=self.generate,
                                         bg=COLORS['purple'], fg='white')
        self.generate_button.pack(side='left', padx=6)
        self.recommend_button = tk.Button(
            controls, text='Подобрать тему', command=self.recommend,
            bg=COLORS['info'], fg='white')
        self.recommend_button.pack(side='left', padx=4)
        self.status = tk.Label(self.window, bg=COLORS['light'], fg=COLORS['gray']); self.status.pack()
        body = tk.Frame(self.window, bg=COLORS['light']); body.pack(fill='both', expand=True, padx=15, pady=10)
        self.listbox = tk.Listbox(body, width=35); self.listbox.pack(side='left', fill='both')
        self.listbox.bind('<<ListboxSelect>>', self.show_selected)
        self.preview = tk.Text(body, wrap=tk.WORD, font=FONTS['small'], state='disabled')
        self.preview.pack(side='right', fill='both', expand=True, padx=(10,0))
        actions = tk.Frame(self.window, bg=COLORS['light']); actions.pack(pady=12)
        tk.Button(actions, text='Принять', command=lambda: self.review(True),
                  bg=COLORS['success'], fg='white').pack(side='left', padx=5)
        tk.Button(actions, text='Отклонить', command=lambda: self.review(False),
                  bg=COLORS['danger'], fg='white').pack(side='left', padx=5)
        self.refresh_pending()

    def generate(self):
        self.generate_button.config(state='disabled'); self.status.config(text='Qwen генерирует кандидатов…')
        model = self.app.db.get_setting('ollama_model', 'qwen3:4b')
        generator = ContentGenerator(OllamaProvider(model=model))
        kind, topic, level, count = self.kind.get(), self.topic.get().strip(), self.level.get(), self.count.get()
        exercise_type = self.exercise_type.get()
        def worker():
            try:
                if kind == 'word':
                    existing = [item['word'] for item in self.app.db.get_words()]
                    prompt, items, rejected = generator.generate_words(topic, level, count, existing)
                else:
                    prompt, items, rejected = generator.generate_exercises(
                        topic, level, count, exercise_type)
                self.app.db.stage_generated(kind, items, model, prompt)
                message = f'Принято валидатором: {len(items)}; отклонено: {len(rejected)}'
            except (LLMUnavailableError, ContentValidationError) as error:
                message = f'Генерация недоступна: {error}'
            self.window.after(0, lambda: self._generation_done(message))
        threading.Thread(target=worker, daemon=True).start()

    def recommend(self):
        self.recommend_button.config(state='disabled')
        self.status.config(text='Qwen анализирует локальную статистику…')
        model = self.app.db.get_setting('ollama_model', 'qwen3:4b')
        generator = ContentGenerator(OllamaProvider(model=model))
        context = self.app.db.get_recommendation_context()
        kind = self.kind.get()

        def worker():
            try:
                result = generator.recommend_content(context)
                self.app.db.set_setting('last_ai_recommendation', result)
                selected = (result['vocabulary_topic'] if kind == 'word'
                            else result['grammar_topic'])
                self.window.after(0, lambda: self._recommendation_done(selected, result['reason']))
            except (LLMUnavailableError, ContentValidationError) as error:
                message = f'Недоступно: {error}'
                self.window.after(0, lambda: self._recommendation_done('', message))
        threading.Thread(target=worker, daemon=True).start()

    def _recommendation_done(self, topic, reason):
        self.recommend_button.config(state='normal')
        if topic: self.topic.set(topic)
        self.status.config(text=reason)

    def _generation_done(self, message):
        self.generate_button.config(state='normal'); self.status.config(text=message); self.refresh_pending()

    def refresh_pending(self):
        self.candidates = self.app.db.get_pending_generated()
        self.listbox.delete(0, tk.END)
        for item in self.candidates:
            payload = item['payload']; title = payload.get('word') or payload.get('sentence', '')
            self.listbox.insert(tk.END, f"{item['content_type']}: {title[:38]}")

    def show_selected(self, event=None):
        selection = self.listbox.curselection()
        if not selection: return
        import json
        text = json.dumps(self.candidates[selection[0]]['payload'], ensure_ascii=False, indent=2)
        self.preview.config(state='normal'); self.preview.delete('1.0', tk.END)
        self.preview.insert('1.0', text); self.preview.config(state='disabled')

    def review(self, approve):
        selection = self.listbox.curselection()
        if not selection: return
        candidate = self.candidates[selection[0]]
        if candidate['content_type'] == 'word':
            try:
                self.app.db.review_generated_word(candidate['id'], approve)
            except Exception as error:
                messagebox.showerror('Ошибка', str(error)); return
            self.app.words_data = self.app.db.get_words()
            self.app.materials_tab.refresh(); self.app.update_stats()
        else:
            try:
                self.app.db.review_generated_exercise(candidate['id'], approve)
            except Exception as error:
                messagebox.showerror('Ошибка', str(error)); return
            self.app.exercises_data = self.app.db.get_exercises()
            self.app.exercises_tab.refresh_topics()
            self.app.materials_tab.refresh(); self.app.update_stats()
        self.refresh_pending()
