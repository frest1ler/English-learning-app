"""Product pages for the initial Windows/Linux desktop release."""

import random
from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDialogButtonBox, QFileDialog, QFormLayout,
    QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton,
    QSpinBox, QStackedLayout, QTableWidget, QTableWidgetItem, QTextBrowser,
    QVBoxLayout, QWidget,
)

from english_learning.application.learning_service import LearningService
from english_learning.presentation.ollama_panel import OllamaPanel
from learning.exercise_modes import instruction_for_type, topic_text


def heading(layout, title, subtitle=""):
    label = QLabel(title); label.setObjectName("title"); layout.addWidget(label)
    if subtitle:
        muted = QLabel(subtitle); muted.setObjectName("muted"); muted.setWordWrap(True); layout.addWidget(muted)


class BasePage(QWidget):
    changed = Signal()

    def __init__(self, service: LearningService):
        super().__init__(); self.service = service

    def refresh(self):
        pass


class LessonDialog(QDialog):
    def __init__(self, service, minutes, parent=None):
        super().__init__(parent); self.service = service
        self.tasks = service.daily_plan(minutes); self.index = 0; self.revealed = False
        self.setWindowTitle("Занятие на сегодня"); self.resize(650, 430)
        layout = QVBoxLayout(self); self.progress = QLabel(); self.prompt = QLabel()
        self.prompt.setObjectName("title"); self.prompt.setWordWrap(True)
        self.detail = QLabel(); self.detail.setWordWrap(True); self.answer = QLineEdit()
        self.answer.returnPressed.connect(self.submit)
        self.action = QPushButton("Проверить"); self.action.clicked.connect(self.submit)
        self.ratings = QFrame(); ratings_layout = QHBoxLayout(self.ratings)
        for value, title in enumerate(("Не помню", "Трудно", "Нормально", "Легко")):
            button = QPushButton(title); button.clicked.connect(lambda checked=False, rating=value: self.rate(rating))
            ratings_layout.addWidget(button)
        for widget in (self.progress, self.prompt, self.detail, self.answer, self.action, self.ratings):
            layout.addWidget(widget)
        self.show_task()

    def show_task(self):
        if self.index >= len(self.tasks):
            QMessageBox.information(self, "Готово", "Занятие завершено."); self.accept(); return
        item = self.tasks[self.index]; data = item["data"]; self.revealed = False
        self.progress.setText(f"Задание {self.index + 1} из {len(self.tasks)}")
        self.detail.clear()
        if item["kind"] == "word":
            self.prompt.setText(f"Вспомните перевод:\n{data['word']} {data['transcription']}")
            self.answer.hide(); self.action.setText("Показать ответ"); self.action.show(); self.ratings.hide()
        else:
            self.prompt.setText(data["sentence"]); self.answer.clear(); self.answer.show(); self.answer.setFocus()
            self.action.setText("Проверить"); self.action.show(); self.ratings.hide()

    def submit(self):
        task = self.tasks[self.index]; data = task["data"]
        if task["kind"] == "word":
            self.detail.setText(f"{data['translation']}\n{data.get('example', '')}")
            self.action.hide(); self.ratings.show(); return
        answer = self.answer.text().strip()
        if not answer: return
        correct = self.service.answer_matches(answer, data["answer"])
        self.service.database.record_answer(
            activity_type=data.get("exercise_type", "grammar_gap"), item_id=data.get("id"),
            topic_id=data.get("topic_id"), prompt=data["sentence"], user_answer=answer,
            correct_answer=data["answer"], is_correct=correct)
        self.detail.setText("Правильно" if correct else f"Ответ: {data['answer']}")
        self.index += 1; self.show_task()

    def rate(self, rating):
        data = self.tasks[self.index]["data"]
        self.service.review_word(data["id"], rating)
        self.index += 1; self.show_task()


class TodayPage(BasePage):
    def __init__(self, service):
        super().__init__(service); layout = QVBoxLayout(self); layout.setContentsMargins(32,32,32,32)
        heading(layout, "Сегодня", "Персональный план на основе повторений и слабых тем")
        self.summary = QLabel(); self.summary.setObjectName("title"); layout.addWidget(self.summary)
        row = QHBoxLayout(); row.addWidget(QLabel("Продолжительность"))
        self.minutes = QComboBox(); self.minutes.addItems(("5", "10", "15", "20")); self.minutes.setCurrentText(str(service.setting("lesson_duration", 15)))
        row.addWidget(self.minutes); row.addStretch(); layout.addLayout(row)
        start = QPushButton("Начать занятие"); start.clicked.connect(self.start); layout.addWidget(start); layout.addStretch(); self.refresh()

    def refresh(self):
        data = self.service.dashboard()
        self.summary.setText(f"Уровень {data['level']}\n{data['words']['due']} слов к повторению\n{data['sessions']['sessions']} завершённых занятий")

    def start(self):
        self.service.save_setting("lesson_duration", int(self.minutes.currentText()))
        LessonDialog(self.service, int(self.minutes.currentText()), self).exec(); self.changed.emit()


class VocabularyPage(BasePage):
    def __init__(self, service):
        super().__init__(service); self.items=[]; layout=QVBoxLayout(self); layout.setContentsMargins(24,24,24,24)
        heading(layout,"Словарь","Поиск, карточки и интервальное повторение")
        row=QHBoxLayout(); self.search=QLineEdit(); self.search.setPlaceholderText("Слово или перевод")
        self.search.textChanged.connect(self.refresh); row.addWidget(self.search)
        add=QPushButton("Добавить"); add.clicked.connect(self.add_word); row.addWidget(add)
        review=QPushButton("Повторить"); review.clicked.connect(self.review); row.addWidget(review); layout.addLayout(row)
        content=QHBoxLayout(); self.list=QListWidget(); self.list.currentRowChanged.connect(self.show_word)
        self.card=QTextBrowser(); content.addWidget(self.list,1); content.addWidget(self.card,2); layout.addLayout(content); self.refresh()

    def refresh(self):
        self.items=self.service.words(self.search.text() if hasattr(self,'search') else "")
        self.list.clear(); self.list.addItems([f"{x['word']} — {x['translation']}" for x in self.items])
        if self.items: self.list.setCurrentRow(0)

    def show_word(self,index):
        if index<0 or index>=len(self.items): return
        x=self.items[index]; self.card.setHtml(f"<h1>{x['word']}</h1><h3>{x['transcription']}</h3><p>{x['translation']}</p><p><i>{x['example']}</i></p><p>{x['example_translation']}</p>")

    def add_word(self):
        dialog=QDialog(self); dialog.setWindowTitle("Добавить слово"); form=QFormLayout(dialog); fields={}
        for key,title in (("word","Слово"),("translation","Перевод"),("transcription","Транскрипция"),("example","Пример"),("example_translation","Перевод примера")):
            fields[key]=QLineEdit(); form.addRow(title,fields[key])
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); form.addRow(buttons)
        if dialog.exec() and fields['word'].text().strip() and fields['translation'].text().strip():
            self.service.add_word({key:value.text().strip() for key,value in fields.items()}); self.refresh(); self.changed.emit()

    def review(self):
        words=self.service.due_words()
        if not words: QMessageBox.information(self,"Повторение","На сегодня слов нет."); return
        # Reuse the lesson card with a word-only five-minute plan by rating the first due words.
        dialog=QDialog(self); dialog.setWindowTitle("Повторение"); layout=QVBoxLayout(dialog); index={"value":0}
        prompt=QLabel(); prompt.setObjectName("title"); answer=QLabel(); show=QPushButton("Показать ответ")
        ratings=QFrame(); rating_layout=QHBoxLayout(ratings)
        def render():
            if index['value']>=len(words): dialog.accept(); return
            item=words[index['value']]; prompt.setText(f"{item['word']} {item['transcription']}"); answer.clear(); show.show(); ratings.hide()
        def reveal(): answer.setText(words[index['value']]['translation']); show.hide(); ratings.show()
        show.clicked.connect(reveal)
        for value,title in enumerate(("Не помню","Трудно","Нормально","Легко")):
            button=QPushButton(title)
            def rate(checked=False,rating=value): self.service.review_word(words[index['value']]['id'],rating); index['value']+=1; render()
            button.clicked.connect(rate); rating_layout.addWidget(button)
        for widget in (prompt,answer,show,ratings): layout.addWidget(widget)
        render(); dialog.exec(); self.changed.emit()


class PracticePage(BasePage):
    def __init__(self, service):
        super().__init__(service); self.queue=[]; self.index=0; layout=QVBoxLayout(self); layout.setContentsMargins(28,28,28,28)
        heading(layout,"Практика","Грамматика и перевод с управляемой сложностью")
        options=QHBoxLayout(); self.mode=QComboBox(); self.mode.addItem("Грамматика","grammar"); self.mode.addItem("RU → EN","translation")
        self.topic=QComboBox(); self.topic.addItems(service.topics()); self.hide_topic=QCheckBox("Скрывать время до ответа")
        start=QPushButton("Начать"); start.clicked.connect(self.start)
        for widget in (self.mode,self.topic,self.hide_topic,start): options.addWidget(widget)
        layout.addLayout(options); self.topic_label=QLabel(); self.instruction=QLabel(); self.prompt=QLabel(); self.prompt.setObjectName("title"); self.prompt.setWordWrap(True)
        self.answer=QLineEdit(); self.answer.returnPressed.connect(self.check); self.result=QLabel(); check=QPushButton("Проверить"); check.clicked.connect(self.check)
        for widget in (self.topic_label,self.instruction,self.prompt,self.answer,self.result,check): layout.addWidget(widget)
        layout.addStretch()

    def start(self):
        mode=self.mode.currentData(); self.queue=self.service.exercises(self.topic.currentText(),mode)[:30]; self.index=0; self.show_current()

    def show_current(self):
        if self.index>=len(self.queue): QMessageBox.information(self,"Практика","Тренировка завершена."); return
        item=self.queue[self.index]; hidden=self.hide_topic.isChecked()
        self.topic_label.setText(topic_text(item['rule'],not hidden)); self.instruction.setText(instruction_for_type(item.get('exercise_type','grammar_gap')))
        self.prompt.setText(item['sentence']); self.answer.clear(); self.answer.setFocus(); self.result.clear()

    def check(self):
        if not self.queue or not self.answer.text().strip(): return
        item=self.queue[self.index]; answer=self.answer.text().strip(); correct=self.service.answer_matches(answer,item['answer'])
        self.service.database.record_answer(activity_type=item.get('exercise_type','grammar_gap'),item_id=item.get('id'),topic_id=item.get('topic_id'),prompt=item['sentence'],user_answer=answer,correct_answer=item['answer'],is_correct=correct)
        self.topic_label.setText(topic_text(item['rule'],True,True)); self.result.setText("Правильно" if correct else f"Ответ: {item['answer']}")
        self.index+=1; self.changed.emit()


class RulesPage(BasePage):
    def __init__(self,service):
        super().__init__(service); self.items=service.rules(); layout=QHBoxLayout(self); self.list=QListWidget(); self.browser=QTextBrowser()
        self.list.addItems([x['title'] for x in self.items]); self.list.currentRowChanged.connect(self.show_rule)
        layout.addWidget(self.list,1); layout.addWidget(self.browser,3)
        if self.items:self.list.setCurrentRow(0)
    def show_rule(self,index):
        if 0<=index<len(self.items): self.browser.setPlainText(self.items[index]['content'])


class MaterialsPage(BasePage):
    def __init__(self,service):
        super().__init__(service); layout=QVBoxLayout(self); heading(layout,"Материалы","Локальная библиотека слов и упражнений")
        row=QHBoxLayout(); self.search=QLineEdit(); self.kind=QComboBox(); self.kind.addItems(("all","words","exercises")); self.level=QComboBox(); self.level.addItems(("all","A1","A2","B1","B2","C1","C2"))
        button=QPushButton("Найти"); button.clicked.connect(self.refresh)
        for widget in (self.search,self.kind,self.level,button):row.addWidget(widget)
        layout.addLayout(row); self.table=QTableWidget(0,5); self.table.setHorizontalHeaderLabels(("Тип","Уровень","Материал","Ответ","Источник")); layout.addWidget(self.table); self.refresh()
    def refresh(self):
        items=self.service.materials(self.kind.currentText(),self.search.text(),self.level.currentText())
        self.table.setRowCount(len(items))
        for row,item in enumerate(items):
            for column,value in enumerate((item['kind'],item['cefr_level'],item['title'],item['detail'],item['source'])): self.table.setItem(row,column,QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()


class ProgressPage(BasePage):
    def __init__(self,service):
        super().__init__(service); layout=QVBoxLayout(self); heading(layout,"Прогресс","Освоение слов, тем и история практики"); self.browser=QTextBrowser(); layout.addWidget(self.browser); self.refresh()
    def refresh(self):
        s=self.service.stats(); o=s['overall']; accuracy=o['correct']/o['attempts']*100 if o['attempts'] else 0
        lines=[f"Ответов: {o['attempts']}   Правильных: {o['correct']}   Точность: {accuracy:.1f}%",f"Слова: новые {s['words']['new']}, изучаются {s['words']['learning']}, освоены {s['words']['mastered']}","","Грамматика:"]
        lines += [f"{x['title']}: {x['mastery']*100:.0f}% ({x['attempts']} попыток)" for x in s['topics']]
        self.browser.setPlainText("\n".join(lines))


class SettingsPage(BasePage):
    theme_changed=Signal(str)
    def __init__(self,service):
        super().__init__(service); layout=QVBoxLayout(self); heading(layout,"Настройки","Интерфейс, локальные данные и AI")
        form=QFormLayout(); self.theme=QComboBox(); self.theme.addItems(("light","dark")); self.theme.setCurrentText(service.setting('theme','light'))
        form.addRow("Тема",self.theme); layout.addLayout(form)
        self.ollama=OllamaPanel(service); layout.addWidget(self.ollama)
        save=QPushButton("Сохранить"); save.clicked.connect(self.save); backup=QPushButton("Создать резервную копию"); backup.clicked.connect(self.backup)
        layout.addWidget(save); layout.addWidget(backup); layout.addStretch()
    def save(self):
        self.service.save_setting('theme',self.theme.currentText()); self.ollama.persist(); self.theme_changed.emit(self.theme.currentText())
    def backup(self):
        filename,_=QFileDialog.getSaveFileName(self,"Резервная копия","learning-backup.db","SQLite (*.db)")
        if filename:self.service.backup(Path(filename)); QMessageBox.information(self,"Копия","Резервная копия создана.")


PAGE_FACTORIES=(TodayPage,VocabularyPage,PracticePage,RulesPage,MaterialsPage,ProgressPage,SettingsPage)
