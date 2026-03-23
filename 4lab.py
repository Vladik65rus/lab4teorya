import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import os
import re

class RegexSearcher:
    """Класс для поиска подстрок с помощью регулярных выражений"""
    
    def __init__(self):
        self.results = []
        
    # ==================== ОБЩИЕ ====================
    def search_hex_color(self, text):
        pattern = r'#[0-9A-Fa-f]{3}\b'
        return self._search_pattern(text, pattern, "HEX цвет (3 символа)")
    
    def search_identifier(self, text):
        pattern = r'[a-zA-Z$_][a-zA-Z0-9]*\b'
        return self._search_pattern(text, pattern, "Идентификатор")
    
    def search_date(self, text):
        pattern = r'(?:(?:0[1-9]|1[0-2])/(?:0[1-9]|[12][0-9]|3[01])/(?:19|20)\d{2})'
        matches = self._search_pattern(text, pattern, "Дата MM/DD/YYYY")
        valid_matches = []
        for match in matches:
            if self._validate_date(match['match']):
                valid_matches.append(match)
            else:
                match['type'] = "❌ Некорректная дата"
                valid_matches.append(match)
        return valid_matches
    
    def _search_pattern(self, text, pattern, type_name):
        results = []
        compiled = re.compile(pattern, re.IGNORECASE)
        
        for match in compiled.finditer(text):
            start = match.start()
            end = match.end()
            matched_text = match.group()
            
            line_num = text[:start].count('\n') + 1
            last_newline = text[:start].rfind('\n')
            col_num = start - last_newline if last_newline != -1 else start + 1
            
            results.append({
                'type': type_name,
                'match': matched_text,
                'line': line_num,
                'col': col_num,
                'start': start,
                'end': end
            })
        
        return results
    
    def _validate_date(self, date_str):
        try:
            month, day, year = map(int, date_str.split('/'))
            if month < 1 or month > 12:
                return False
            days_in_month = [31, 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28,
                            31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if day < 1 or day > days_in_month[month - 1]:
                return False
            return True
        except:
            return False


class TextEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Языковой процессор - Вариант 75 (Rust)")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        self.current_file = None
        self.text_changed = False
        self.tooltip = None
        self.searcher = RegexSearcher()
        self.current_matches = []
        
        self.setup_ui()
        self.bind_events()
        
    def bind_events(self):
        self.text_editor.bind('<<Modified>>', self.on_text_modified)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def on_text_modified(self, event=None):
        if self.text_editor.edit_modified():
            self.text_changed = True
            self.text_editor.edit_modified(False)
            
    def on_closing(self):
        if self.text_changed:
            result = messagebox.askyesnocancel("Выход", "Сохранить изменения?")
            if result is None:
                return
            elif result:
                self.save_file()
        self.root.destroy()
        
    def setup_ui(self):
        self.create_menu()
        self.create_toolbar()
        
        # Создаем вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка 1: Лексический анализатор
        self.lexical_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.lexical_frame, text="📝 Лексический анализатор")
        self.setup_lexical_tab()
        
        # Вкладка 2: Поиск по регулярным выражениям
        self.regex_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.regex_frame, text="🔍 Поиск по регулярным выражениям")
        self.setup_regex_tab()
        
        self.create_status_bar()
        
    def setup_lexical_tab(self):
        """Вкладка с лексическим анализатором"""
        # Основной контейнер
        main_frame = tk.Frame(self.lexical_frame, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Верхняя панель с кнопкой Пуск
        top_panel = tk.Frame(main_frame, bg='#f0f0f0')
        top_panel.pack(fill=tk.X, pady=5)
        
        # Кнопка Пуск - большая и заметная
        start_btn = tk.Button(top_panel, text="▶ ПУСК", command=self.analyze_text,
                              bg='#F44336', fg='white', font=('Arial', 12, 'bold'),
                              relief=tk.RAISED, bd=3, width=15, height=1)
        start_btn.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Кнопка Очистить
        clear_btn = tk.Button(top_panel, text="🗑 ОЧИСТИТЬ", command=self.clear_lexical_results,
                              bg='#607D8B', fg='white', font=('Arial', 10, 'bold'),
                              relief=tk.RAISED, bd=2, width=12)
        clear_btn.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').pack(fill=tk.X, pady=5)
        
        # Панель с редактором
        editor_frame = tk.LabelFrame(main_frame, text="📝 Редактор (введите код Rust):", 
                                      font=("Arial", 10, "bold"), bg='#ffffff')
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.modified_label = tk.Label(editor_frame, text="", bg='#ffffff', fg='#ff0000')
        self.modified_label.pack(anchor='ne', padx=5, pady=2)
        
        self.text_editor = scrolledtext.ScrolledText(
            editor_frame, wrap=tk.WORD, font=("Courier New", 11),
            undo=True, background='#ffffff', foreground='#000000',
            insertbackground='#000000', selectbackground='#c0c0c0',
            padx=5, pady=5, height=12
        )
        self.text_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Пример кода
        example_text = """fun calc(a: Int, b: Int, c: Int): Int {
    return a + (b * c)
}

fun calc(a: Int, b: Int, c: Int): Int {
    return a * (b * c)
}"""
        self.text_editor.insert("1.0", example_text)
        
        # Панель с результатами
        result_frame = tk.LabelFrame(main_frame, text="📊 Результаты лексического анализа:", 
                                      font=("Arial", 10, "bold"), bg='#ffffff')
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Таблица
        columns = ('code', 'type', 'lexeme', 'position')
        self.lexical_table = ttk.Treeview(result_frame, columns=columns, show='headings', height=8)
        
        self.lexical_table.heading('code', text='🔢 Код')
        self.lexical_table.heading('type', text='🏷 Тип')
        self.lexical_table.heading('lexeme', text='📄 Лексема')
        self.lexical_table.heading('position', text='📍 Позиция')
        
        self.lexical_table.column('code', width=70, anchor='center')
        self.lexical_table.column('type', width=250, anchor='w')
        self.lexical_table.column('lexeme', width=120, anchor='center')
        self.lexical_table.column('position', width=200, anchor='center')
        
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.lexical_table.yview)
        self.lexical_table.configure(yscrollcommand=scrollbar.set)
        
        self.lexical_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Счетчик ошибок
        self.lexical_error_label = tk.Label(result_frame, text="❌ Ошибок: 0", 
                                             font=("Arial", 9, "bold"),
                                             bg='#ffffff', fg='#F44336')
        self.lexical_error_label.pack(side=tk.BOTTOM, pady=3)
        
        self.text_editor.bind('<KeyRelease>', self.update_cursor_position)
        self.text_editor.bind('<ButtonRelease-1>', self.update_cursor_position)
        
    def setup_regex_tab(self):
        """Вкладка с поиском по регулярным выражениям"""
        main_frame = tk.Frame(self.regex_frame, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Панель выбора
        panel_frame = tk.LabelFrame(main_frame, text="🔍 Параметры поиска", 
                                     font=("Arial", 10, "bold"), bg='#f5f5f5')
        panel_frame.pack(fill=tk.X, padx=5, pady=5)
        
        row1 = tk.Frame(panel_frame, bg='#f5f5f5')
        row1.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(row1, text="Выберите тип поиска:", 
                font=("Arial", 10), bg='#f5f5f5').pack(side=tk.LEFT)
        
        self.search_type = ttk.Combobox(row1, width=35, font=("Arial", 10))
        self.search_type['values'] = (
            "HEX цвет (3 символа) - #RGB",
            "Идентификатор - начинается с a-zA-Z$_",
            "Дата в формате MM/DD/YYYY"
        )
        self.search_type.current(0)
        self.search_type.pack(side=tk.LEFT, padx=10)
        
        search_btn = tk.Button(row1, text="▶ НАЙТИ", command=self.search_text,
                              bg='#F44336', fg='white', font=('Arial', 10, 'bold'), width=12)
        search_btn.pack(side=tk.LEFT, padx=10)
        
        clear_btn = tk.Button(row1, text="🗑 ОЧИСТИТЬ", command=self.clear_regex_results,
                              bg='#607D8B', fg='white', font=('Arial', 10, 'bold'), width=12)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        row2 = tk.Frame(panel_frame, bg='#f5f5f5')
        row2.pack(fill=tk.X, padx=10, pady=5)
        
        self.pattern_label = tk.Label(row2, text="Регулярное выражение: #[0-9A-Fa-f]{3}\\b", 
                                       font=("Courier New", 10), bg='#f5f5f5', fg='#2196F3')
        self.pattern_label.pack(side=tk.LEFT)
        
        self.search_type.bind('<<ComboboxSelected>>', self.update_pattern_label)
        
        # Редактор
        editor_frame = tk.LabelFrame(main_frame, text="📝 Редактор (введите код Rust или текст):", 
                                      font=("Arial", 10, "bold"), bg='#ffffff')
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.regex_editor = scrolledtext.ScrolledText(
            editor_frame, wrap=tk.WORD, font=("Courier New", 11),
            undo=True, background='#ffffff', foreground='#000000',
            insertbackground='#000000', selectbackground='#c0c0c0',
            padx=5, pady=5, height=8
        )
        self.regex_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Результаты
        result_frame = tk.LabelFrame(main_frame, text="📊 Результаты поиска:", 
                                      font=("Arial", 10, "bold"), bg='#ffffff')
        result_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ('type', 'match', 'position')
        self.regex_table = ttk.Treeview(result_frame, columns=columns, show='headings', height=8)
        
        self.regex_table.heading('type', text='🏷 Тип')
        self.regex_table.heading('match', text='📄 Найденная подстрока')
        self.regex_table.heading('position', text='📍 Позиция')
        
        self.regex_table.column('type', width=200, anchor='w')
        self.regex_table.column('match', width=350, anchor='w')
        self.regex_table.column('position', width=150, anchor='center')
        
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.regex_table.yview)
        self.regex_table.configure(yscrollcommand=scrollbar.set)
        
        self.regex_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.regex_table.bind('<ButtonRelease-1>', self.on_regex_click)
        
        self.match_count_label = tk.Label(result_frame, text="🔍 Найдено: 0", 
                                          font=("Arial", 9, "bold"),
                                          bg='#ffffff', fg='#4CAF50')
        self.match_count_label.pack(side=tk.BOTTOM, pady=3)
        
        # Пример текста
        example_regex = """#F00 #ABC #123

Идентификаторы: $myVar _myVar myVar123 myVar

Даты: 12/31/2020 02/29/2020 01/01/2024 02/29/2021 (некорректная)
13/01/2020 (некорректная)"""
        self.regex_editor.insert("1.0", example_regex)
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="📄 Создать", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="📂 Открыть", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="💾 Сохранить", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="💾 Сохранить как", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="🚪 Выход", command=self.on_closing, accelerator="Ctrl+Q")
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="↶ Отменить", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="↷ Повторить", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="✂ Вырезать", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="📋 Копировать", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="📝 Вставить", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="🔲 Выделить все", command=self.select_all, accelerator="Ctrl+A")
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="❓ Справка", command=self.show_help, accelerator="F1")
        help_menu.add_command(label="ℹ О программе", command=self.show_about)
        
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
        self.root.bind('<Control-z>', lambda e: self.undo())
        self.root.bind('<Control-y>', lambda e: self.redo())
        self.root.bind('<Control-x>', lambda e: self.cut())
        self.root.bind('<Control-c>', lambda e: self.copy())
        self.root.bind('<Control-v>', lambda e: self.paste())
        self.root.bind('<Control-a>', lambda e: self.select_all())
        self.root.bind('<F1>', lambda e: self.show_help())
        
    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bg='#e0e0e0', height=45)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        toolbar.pack_propagate(False)
        
        buttons = [
            ("📄", self.new_file, "Создать", "#4CAF50"),
            ("📂", self.open_file, "Открыть", "#2196F3"),
            ("💾", self.save_file, "Сохранить", "#FF9800"),
            ("|", None, None, None),
            ("↶", self.undo, "Отменить", "#9C27B0"),
            ("↷", self.redo, "Повторить", "#9C27B0"),
            ("|", None, None, None),
            ("✂", self.cut, "Вырезать", "#E91E63"),
            ("📋", self.copy, "Копировать", "#E91E63"),
            ("📝", self.paste, "Вставить", "#E91E63"),
            ("|", None, None, None),
            ("❓", self.show_help, "Справка", "#607D8B"),
            ("ℹ", self.show_about, "О программе", "#607D8B")
        ]
        
        for icon, command, tooltip, color in buttons:
            if icon == "|":
                sep = tk.Frame(toolbar, bg='#a0a0a0', width=2, height=30)
                sep.pack(side=tk.LEFT, padx=5, pady=8)
                sep.pack_propagate(False)
            else:
                btn = tk.Button(toolbar, text=icon, command=command,
                              bg=color, fg='white',
                              font=('Segoe UI', 11, 'bold'),
                              relief=tk.RAISED, bd=2,
                              width=3, height=1)
                btn.pack(side=tk.LEFT, padx=2, pady=8)
                self.create_tooltip(btn, tooltip)
    
    def create_tooltip(self, widget, text):
        def enter(event):
            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() + 30
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.tooltip, text=text, background="#ffffe0", 
                           relief="solid", borderwidth=1, font=('Arial', 9))
            label.pack()
        def leave(event):
            if hasattr(self, 'tooltip') and self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)
    
    def create_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg='#e0e0e0', height=25)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.pack_propagate(False)
        
        self.cursor_pos_label = tk.Label(self.status_bar, text="📍 Стр: 1  Стлб: 1",
                                         bg='#e0e0e0', fg='#000000')
        self.cursor_pos_label.pack(side=tk.LEFT, padx=5)
        
        self.file_info_label = tk.Label(self.status_bar, text="", bg='#e0e0e0', fg='#000000')
        self.file_info_label.pack(side=tk.LEFT, padx=20)
        
        self.status_label = tk.Label(self.status_bar, text="✅ Готов", 
                                     bg='#e0e0e0', fg='#000000')
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        self.text_editor.bind('<KeyRelease>', self.update_cursor_position)
        self.text_editor.bind('<ButtonRelease-1>', self.update_cursor_position)
        
    def update_cursor_position(self, event=None):
        try:
            cursor = self.text_editor.index(tk.INSERT)
            line, col = cursor.split('.')
            self.cursor_pos_label.config(text=f"📍 Стр: {line}  Стлб: {int(col)+1}")
            
            content = self.text_editor.get("1.0", tk.END)
            lines = content.count('\n')
            chars = len(content) - 1
            self.file_info_label.config(text=f"📊 Строк: {lines}  Символов: {chars}")
            
            if self.text_changed:
                self.modified_label.config(text="✏ Изменено")
                self.status_label.config(text="⚠ Изменено")
            else:
                self.modified_label.config(text="")
                self.status_label.config(text="✅ Готов")
        except:
            pass
    
    def update_pattern_label(self, event=None):
        patterns = {
            0: r"#[0-9A-Fa-f]{3}\b",
            1: r"[a-zA-Z$_][a-zA-Z0-9]*\b",
            2: r"(?:0[1-9]|1[0-2])/(?:0[1-9]|[12][0-9]|3[01])/(?:19|20)\d{2}"
        }
        idx = self.search_type.current()
        pattern = patterns.get(idx, r"[a-zA-Z][a-zA-Z0-9]*")
        self.pattern_label.config(text=f"Регулярное выражение: {pattern}")
    
    # ==================== ЛЕКСИЧЕСКИЙ АНАЛИЗ ====================
    def analyze_text(self):
        """Лексический анализатор для Rust"""
        text = self.text_editor.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Предупреждение", "⚠ Введите текст для анализа")
            return
        
        self.clear_lexical_results()
        
        error_count = 0
        counter = 1
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            counter, errors = self._analyze_line(line, line_num, counter)
            error_count += errors
        
        self.lexical_error_label.config(text=f"❌ Ошибок: {error_count}")
        
        if error_count == 0:
            self.status_label.config(text="✅ Лексический анализ завершен: ОШИБОК НЕТ")
        else:
            self.status_label.config(text=f"⚠ Лексический анализ завершен: найдено {error_count} ошибок")
    
    def _analyze_line(self, line, line_num, counter):
        """Анализ одной строки"""
        i = 0
        n = len(line)
        errors = 0
        
        while i < n:
            c = line[i]
            
            if c.isspace():
                i += 1
                continue
            
            if c.isalpha():
                start = i
                while i < n and (line[i].isalnum() or line[i] == '_'):
                    i += 1
                word = line[start:i]
                counter, err = self._check_word(word, line_num, start+1, i, counter)
                errors += err
                continue
            
            if c.isdigit():
                start = i
                while i < n and line[i].isdigit():
                    i += 1
                number = line[start:i]
                self.lexical_table.insert('', 'end', values=(counter, 'целое без знака', number, f"строка {line_num}, {start+1}-{i}"))
                counter += 1
                continue
            
            token_map = {
                '=': (10, 'оператор присваивания'),
                '+': (16, 'оператор сложения'),
                '-': (17, 'оператор вычитания'),
                '*': (18, 'оператор умножения'),
                '/': (19, 'оператор деления'),
                '(': (5, 'открывающая скобка'),
                ')': (6, 'закрывающая скобка'),
                '{': (7, 'открывающая фигурная'),
                '}': (8, 'закрывающая фигурная'),
                ';': (9, 'точка с запятой'),
                ',': (4, 'запятая'),
                ':': (99, '❌ ОШИБКА!')
            }
            
            if c in token_map:
                code, type_name = token_map[c]
                if code == 99:
                    errors += 1
                self.lexical_table.insert('', 'end', values=(counter, type_name, c, f"строка {line_num}, {i+1}-{i+1}"))
                counter += 1
                i += 1
            else:
                self.lexical_table.insert('', 'end', values=(counter, '❌ ОШИБКА!', c, f"строка {line_num}, {i+1}-{i+1}"))
                errors += 1
                counter += 1
                i += 1
        
        return counter, errors
    
    def _check_word(self, word, line_num, start, end, counter):
        """Проверка слова на ключевые слова и типы"""
        errors = 0
        if word == "fun":
            self.lexical_table.insert('', 'end', values=(counter, '🔑 ключевое слово - fun', word, f"строка {line_num}, {start}-{end}"))
        elif word == "return":
            self.lexical_table.insert('', 'end', values=(counter, '🔑 ключевое слово - return', word, f"строка {line_num}, {start}-{end}"))
        elif word in ["Int", "i32", "i64", "f32", "f64", "bool"]:
            self.lexical_table.insert('', 'end', values=(counter, '❌ ОШИБКА!', word, f"строка {line_num}, {start}-{end}"))
            errors += 1
        else:
            self.lexical_table.insert('', 'end', values=(counter, '📝 идентификатор', word, f"строка {line_num}, {start}-{end}"))
        return counter + 1, errors
    
    def clear_lexical_results(self):
        for item in self.lexical_table.get_children():
            self.lexical_table.delete(item)
        self.lexical_error_label.config(text="❌ Ошибок: 0")
    
    # ==================== ПОИСК ПО РЕГУЛЯРНЫМ ВЫРАЖЕНИЯМ ====================
    def search_text(self):
        text = self.regex_editor.get("1.0", tk.END)
        if not text.strip():
            messagebox.showwarning("Предупреждение", "⚠ Нет данных для поиска")
            return
        
        self.clear_regex_results()
        
        idx = self.search_type.current()
        results = []
        
        if idx == 0:
            results = self.searcher.search_hex_color(text)
        elif idx == 1:
            results = self.searcher.search_identifier(text)
        elif idx == 2:
            results = self.searcher.search_date(text)
        
        self.current_matches = results
        
        for result in results:
            self.regex_table.insert('', 'end', values=(
                result['type'],
                result['match'],
                f"строка {result['line']}, {result['col']}"
            ))
        
        self.match_count_label.config(text=f"🔍 Найдено: {len(results)}")
        self.status_label.config(text=f"✅ Поиск завершен: найдено {len(results)} совпадений")
    
    def on_regex_click(self, event):
        item = self.regex_table.selection()
        if not item:
            return
        
        values = self.regex_table.item(item[0], 'values')
        if len(values) < 3:
            return
        
        match_text = values[1]
        
        for match in self.current_matches:
            if match['match'] == match_text:
                self.regex_editor.tag_remove('highlight', '1.0', tk.END)
                self.regex_editor.tag_configure('highlight', background='yellow', foreground='black')
                
                start_pos = f"1.0+{match['start']}c"
                end_pos = f"1.0+{match['end']}c"
                self.regex_editor.tag_add('highlight', start_pos, end_pos)
                self.regex_editor.see(start_pos)
                break
    
    def clear_regex_results(self):
        for item in self.regex_table.get_children():
            self.regex_table.delete(item)
        self.match_count_label.config(text="🔍 Найдено: 0")
        self.regex_editor.tag_remove('highlight', '1.0', tk.END)
    
    # ==================== ОБЩИЕ ====================
    def undo(self): 
        current = self.notebook.index(self.notebook.select())
        if current == 0:
            try: self.text_editor.edit_undo()
            except: pass
        else:
            try: self.regex_editor.edit_undo()
            except: pass
    
    def redo(self): 
        current = self.notebook.index(self.notebook.select())
        if current == 0:
            try: self.text_editor.edit_redo()
            except: pass
        else:
            try: self.regex_editor.edit_redo()
            except: pass
    
    def copy(self):
        current = self.notebook.index(self.notebook.select())
        if current == 0:
            self.text_editor.event_generate("<<Copy>>")
        else:
            self.regex_editor.event_generate("<<Copy>>")
    
    def cut(self):
        current = self.notebook.index(self.notebook.select())
        if current == 0:
            self.text_editor.event_generate("<<Cut>>")
        else:
            self.regex_editor.event_generate("<<Cut>>")
    
    def paste(self):
        current = self.notebook.index(self.notebook.select())
        if current == 0:
            self.text_editor.event_generate("<<Paste>>")
        else:
            self.regex_editor.event_generate("<<Paste>>")
    
    def select_all(self):
        current = self.notebook.index(self.notebook.select())
        if current == 0:
            self.text_editor.tag_add(tk.SEL, "1.0", tk.END)
        else:
            self.regex_editor.tag_add(tk.SEL, "1.0", tk.END)
        return "break"
    
    def new_file(self):
        current = self.notebook.index(self.notebook.select())
        if current == 0:
            self.text_editor.delete("1.0", tk.END)
            self.clear_lexical_results()
        else:
            self.regex_editor.delete("1.0", tk.END)
            self.clear_regex_results()
    
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Текстовые файлы", "*.txt"), ("Rust файлы", "*.rs"), ("Все файлы", "*.*")])
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    current = self.notebook.index(self.notebook.select())
                    if current == 0:
                        self.text_editor.delete("1.0", tk.END)
                        self.text_editor.insert("1.0", f.read())
                        self.clear_lexical_results()
                    else:
                        self.regex_editor.delete("1.0", tk.END)
                        self.regex_editor.insert("1.0", f.read())
                        self.clear_regex_results()
                self.status_label.config(text=f"✅ Открыт файл: {os.path.basename(path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"❌ Не удалось открыть файл:\n{str(e)}")
    
    def save_file(self):
        current = self.notebook.index(self.notebook.select())
        if current == 0:
            path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                               filetypes=[("Текстовые файлы", "*.txt"), ("Rust файлы", "*.rs"), ("Все файлы", "*.*")])
            if path:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.text_editor.get("1.0", tk.END))
                self.status_label.config(text=f"✅ Сохранено: {os.path.basename(path)}")
        else:
            path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                               filetypes=[("Текстовые файлы", "*.txt"), ("Rust файлы", "*.rs"), ("Все файлы", "*.*")])
            if path:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.regex_editor.get("1.0", tk.END))
                self.status_label.config(text=f"✅ Сохранено: {os.path.basename(path)}")
    
    def save_as_file(self):
        self.save_file()
    
    def show_help(self):
        messagebox.showinfo("Справка", 
            "📚 СПРАВКА\n\n"
            "📌 Лексический анализатор (вкладка 1):\n"
            "   - Введите код Rust\n"
            "   - Нажмите кнопку 'ПУСК'\n"
            "   - Результаты появятся в таблице\n\n"
            "🔍 Поиск по регулярным выражениям (вкладка 2):\n"
            "   - HEX цвет (3 символа): #RGB\n"
            "   - Идентификатор: буква, $ или _, затем буквы/цифры\n"
            "   - Дата: MM/DD/YYYY (с проверкой високосных годов)\n\n"
            "🖱 Кликните на результат для подсветки в тексте")
    
    def show_about(self):
        messagebox.showinfo("О программе", 
            "🦀 Языковой процессор\n"
            "Вариант 75: Rust\n\n"
            "📝 Лексический анализатор (ЛР №2, №3)\n"
            "🔍 Поиск по регулярным выражениям (ЛР №4)\n\n"
            "© 2026")


def main():
    root = tk.Tk()
    app = TextEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
