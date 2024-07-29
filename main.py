from customtkinter import CTk, CTkFrame, CTkLabel, CTkFont, IntVar, CTkTextbox, CTkEntry, StringVar, CTkButton
from customtkinter import CTkScrollableFrame, CTkCheckBox
import sqlite3 as db

WHITE = "#AAAAAA"
BLACK = "#242424"
DARK_GRAY = "#343434"
LIGHT_GRAY = "#505050"

FONT_FAMILY = "Kode Mono"

FOCUS_TIME = 30 * 60
BREAK_TIME = 5 * 60

class Window(CTk):
    def __init__(self):
        super().__init__()

        self.title('')
        self.iconbitmap('icon.ico')
        self._set_appearance_mode('dark')

        self.columnconfigure(index = 0, weight = 2, uniform = 'col')
        self.columnconfigure(index = 1, weight = 3, uniform = 'col')
        self.columnconfigure(index = 2, weight = 3, uniform = 'col')
        self.rowconfigure(index = 0, weight = 1, uniform = 'row')
        self.rowconfigure(index = 1, weight = 3, uniform = 'row')
        self.rowconfigure(index = 2, weight = 3, uniform = 'row')

        Timer(self)
        Notepad(self, 2, 'reminders')
        Notepad(self, 1, 'inbox')
        TasksManager(self, 1, 'Empty')
        TasksManager(self, 2, 'Empty')

        self.geometry('1536x795-9-1')

class Timer(CTkFrame):
    def __init__(self, parent):
        super().__init__(master = parent, fg_color = BLACK)

        self.parent = parent

        self.state = IntVar(value = 0)
        self.time = FOCUS_TIME
        self.full_time = self.time
        
        self.parent.bind('<Control-KeyPress-q>', lambda event: self.trigger())
        self.parent.bind('<Control-KeyPress-Q>', lambda event: self.trigger())
        self.parent.bind('<Control-KeyPress-w>', lambda event: self.reset())
        self.parent.bind('<Control-KeyPress-W>', lambda event: self.reset())

        self.create_widgets()
        self.update()
        self.bother()
    
    def create_widgets(self):
        font = CTkFont(family = FONT_FAMILY, size = 40, weight = 'bold')

        self.label = CTkLabel(master = self, fg_color = DARK_GRAY, font = font, text_color = WHITE, width = 130,
            corner_radius = 10)

        self.label.pack(pady = 15)
        self.grid(row = 0, column = 0, sticky = 'nesw')

    def trigger(self):
        if self.state.get() == 0:
            self.state.set(value = 1)
            self.count()
            self.parent.attributes('-topmost', False)

            try:
                self.message.destroy()
            except:
                pass

        else:
            self.state.set(value = 0)
            self.message = Entry(self.parent, 'bother')
            self.bother()

    def count(self):
        if self.state.get() == 1:
            self.time -= 1
            self.update()

            if self.time <= 0:
                self.trigger()
                self.reset()

            self.after(ms = 1000, func = self.count)

    def update(self):
        minutes, seconds = divmod(self.time, 60)
        formatted_time = f'{minutes:02}{seconds:02}'
        self.label.configure(text = formatted_time)

    def reset(self):
        if self.full_time == FOCUS_TIME:
            self.time = BREAK_TIME
            self.full_time = BREAK_TIME
        else:
            self.time = FOCUS_TIME
            self.full_time = FOCUS_TIME

        self.update()

    def bother(self):
        if self.state.get() == 0:           
            self.parent.state(newstate = 'normal')
            self.parent.attributes('-topmost', True)

            self.after(ms = 60000, func = self.bother)

class Notepad(CTkFrame):
    def __init__(self, parent, col, notes_name):
        super().__init__(master = parent, fg_color = BLACK)

        self.parent = parent
        self.col = col
        self.notes_name = notes_name.capitalize()

        self.create_widgets()

        self.parent.bind('<Alt-KeyPress-q>', lambda event: self.take_notes())
        self.parent.bind('<Alt-KeyPress-Q>', lambda event: self.take_notes())
        self.notepad.bind('<Alt-KeyPress-w>', lambda event: self.open_notes())
        self.notepad.bind('<Alt-KeyPress-W>', lambda event: self.open_notes())
        self.notepad.bind('<Alt-KeyPress-e>', lambda event: self.export_notes())
        self.notepad.bind('<Alt-KeyPress-E>', lambda event: self.export_notes())

    def create_widgets(self):
        title_font = CTkFont(family = FONT_FAMILY, size = 22)
        notepad_font = CTkFont(family = FONT_FAMILY, size = 15)

        self.title = CTkLabel(master = self, text = self.notes_name, text_color = WHITE, font = title_font)

        self.notepad = CTkTextbox(master = self, fg_color = DARK_GRAY, height = 700, text_color = WHITE, font = notepad_font,
            scrollbar_button_color = WHITE, scrollbar_button_hover_color = WHITE, undo = True, wrap = 'word', corner_radius = 10)

        self.title.pack(pady = 10)
        self.notepad.pack(fill = 'x', padx = 10, pady = (0, 10))
        self.grid(row = 1, column = self.col, sticky = 'nesw', rowspan = 2)

        doc = open(file = f'notes/{self.notes_name}.txt', mode = 'r')
        notes = doc.read()
        self.notepad.insert(index = '1.0', text = notes)

    def take_notes(self):
        focused_widget = self.parent.focus_get()

        if focused_widget == self.parent:
            self.notepad.focus()
            self.notepad.mark_set(mark = 'insert', index = 'end')
        else:
            self.parent.focus()

            notes = self.notepad.get(index1 = '1.0', index2 = 'end-1c')
            doc = open(file = f'notes/{self.notes_name}.txt', mode = 'w')
            doc.write(notes)
            doc.close()

    def export_notes(self):
        Entry(self.parent, 'export notes', self.notepad)

    def open_notes(self):
        Entry(self.parent, 'open notes', self, self.col)

class TasksManager(CTkFrame):
    def __init__(self, parent, row, name):
        self.parent = parent
        self.row = row
        self.name = name

        if self.row == 1:
            self.mod = 'Alt'
        else:
            self.mod = 'Control'

        super().__init__(master = parent, fg_color = BLACK)

        connection = db.connect(f'{self.row}.db')
        cursor = connection.cursor()
        cursor.execute(f'CREATE TABLE IF NOT EXISTS {self.name} (name TEXT, prio INTEGER)')
        connection.commit()
        connection.close()

        self.rowconfigure(index = 0, uniform = 'row', weight = 1)
        self.rowconfigure(index = 1, uniform = 'row', weight = 3)
        self.columnconfigure(index = 0, weight = 1)

        self.checkboxes_vars = list()
        self.focused_widget = self.parent

        self.create_widgets()
        self.restore_tasks()

        self.parent.bind(f'<{self.mod}-KeyPress-a>', lambda event: self.add_task())
        self.parent.bind(f'<{self.mod}-KeyPress-A>', lambda event: self.add_task())
        self.parent.bind(f'<{self.mod}-KeyPress-d>', lambda event: self.next_project(1))
        self.parent.bind(f'<{self.mod}-KeyPress-D>', lambda event: self.next_project(1))
        self.parent.bind(f'<{self.mod}-KeyPress-s>', lambda event: self.next_project(-1))
        self.parent.bind(f'<{self.mod}-KeyPress-S>', lambda event: self.next_project(-1))

    def create_widgets(self):
        label_font = CTkFont(family = FONT_FAMILY, size = 20)
        buttons_font = CTkFont(family = FONT_FAMILY, size = 16)

        header = CTkFrame(master = self, fg_color = BLACK)
        name_label = CTkLabel(master = header, text = self.name, text_color = WHITE, font = label_font)
        delete_button = CTkButton(master = header, fg_color = DARK_GRAY, text = 'D', width = 30, height = 30,
            hover_color = LIGHT_GRAY, font = buttons_font, text_color = WHITE, corner_radius = 10,
            command = self.delete_project)
        
        add_button = CTkButton(master = header, fg_color = DARK_GRAY, text = 'A', width = 30, height = 30,
            hover_color = LIGHT_GRAY, font = buttons_font, text_color = WHITE, corner_radius = 10,
            command = self.add_project)

        rename_button = CTkButton(master = header, fg_color = DARK_GRAY, text = 'R', width = 30, height = 30,
            hover_color = LIGHT_GRAY, font = buttons_font, text_color = WHITE, corner_radius = 10,
            command = self.rename_project)
        
        self.tasks_frame = CTkScrollableFrame(master = self, fg_color = DARK_GRAY, height = 300,
            scrollbar_button_color = WHITE, scrollbar_button_hover_color = WHITE, corner_radius = 10)

        header.grid(row = 0, column = 0, sticky = 'nesw', padx = 10, pady = 10)
        name_label.pack(side = 'left', padx = 10, pady = 10)
        delete_button.pack(side = 'right', padx = (0, 10))
        add_button.pack(side = 'right', padx = 5)
        rename_button.pack(side = 'right')
        self.tasks_frame.grid(row = 1, column = 0, sticky = 'nesw', padx = 10, pady = (0, 10))
        self.grid(row = self.row, column = 0, sticky = 'nesw')

    def add_project(self):
        Entry(self.parent, 'add project', self.row)

    def delete_project(self):
        connection = db.connect(f'{self.row}.db')
        cursor = connection.cursor()
        cursor.execute(f'DROP TABLE {self.name}')
        connection.commit()
        connection.close()

        self.destroy()
        TasksManager(self.parent, self.row, 'Empty')

    def rename_project(self):
        Entry(self.parent, 'rename project', self.row, self.name, self, self.parent)

    def next_project(self, step):
        connection = db.connect(f'{self.row}.db')
        cursor = connection.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type = ?', ('table',))
        projects = cursor.fetchall()
        connection.close()

        for a, project in enumerate(projects):
            if project[0] == self.name:
                next_project_index = a + step

                try:
                    next_project = projects[next_project_index][0]
                except:
                    next_project = projects[0][0]

        self.destroy()
        TasksManager(self.parent, self.row, next_project)

    def add_task(self):
        if self.focused_widget == self.parent:
            textbox_font = CTkFont(family = FONT_FAMILY, size = 15)
            entry_font = CTkFont(family = FONT_FAMILY, size = 14)

            self.task_frame = CTkFrame(master = self, fg_color = BLACK)
            
            self.textbox = CTkTextbox(master = self.task_frame, font = textbox_font, text_color = WHITE, height = 20,
                corner_radius = 0, border_spacing = 0, fg_color = BLACK, width = 275, activate_scrollbars = False,
                wrap = 'word', undo = True)
            
            self.entry = CTkEntry(master = self.task_frame, fg_color = DARK_GRAY, font = entry_font, justify = 'center',
                border_color = DARK_GRAY, width = 50, corner_radius = 10, text_color = WHITE)

            self.task_frame.grid(row = 0, column = 0, sticky = 'nesw', padx = 10, pady = 10)
            self.textbox.pack(side = 'left', padx = (15, 0), pady = 10)
            self.entry.pack(side = 'left', padx = 10, pady = 10)

            self.textbox.focus()
            self.focused_widget = self.textbox

            self.textbox.bind('<Escape>', lambda event: self.discard_task())
            self.entry.bind('<Escape>', lambda event: self.discard_task())

        elif self.focused_widget == self.textbox:
            self.entry.focus()
            self.focused_widget = self.entry

        elif self.focused_widget == self.entry:
            self.parent.focus()
            self.focused_widget = self.parent
            
            task = self.textbox.get(index1 = '1.0', index2 = 'end-1c')
            prio = self.entry.get()
            
            connection = db.connect(f'{self.row}.db')
            cursor = connection.cursor()
            cursor.execute(f'INSERT INTO {self.name} VALUES (?, ?)', (task, prio,))
            connection.commit()
            connection.close()

            self.destroy()
            TasksManager(self.parent, self.row, self.name)

    def discard_task(self):
        self.focused_widget = self.parent
        self.task_frame.destroy()

    def edit_task(self, event):
        try:
            self.old_val = event.widget.get(index1 = '1.0', index2 = 'end-1c')
        except:
            self.old_val = event.widget.get()

        if len(self.old_val) <= 3:
            self.col = 'prio'
        else:
            self.col = 'name'

        event.widget.bind(f'<FocusOut>', lambda event: self.save_edited_task(event))
        event.widget.bind(f'<{self.mod}-KeyPress-a>', lambda event: self.parent.focus())
        event.widget.bind(f'<{self.mod}-KeyPress-A>', lambda event: self.parent.focus())

        self.focused_widget = event.widget

    def save_edited_task(self, event):
        if self.focused_widget == event.widget:
            self.focused_widget = self.parent

            try:
                new_val = event.widget.get(index1 = '1.0', index2 = 'end-1c')
            except:
                new_val = event.widget.get()

            connection = db.connect(f'{self.row}.db')
            cursor = connection.cursor()
            cursor.execute(f'UPDATE {self.name} SET {self.col} = ? WHERE {self.col} = ?', (new_val, self.old_val,))
            connection.commit()
            connection.close()

            self.destroy()
            TasksManager(self.parent, self.row, self.name)

    def delete_task(self):
        connection = db.connect(f'{self.row}.db')
        cursor = connection.cursor()
        cursor.execute(f'SELECT prio FROM {self.name} ORDER BY prio ASC')
        prios = cursor.fetchall()

        for a, prio in enumerate(prios):
            checkbox = self.checkboxes_vars[a]
            checkbox_state = checkbox.get()

            if checkbox_state == 1:
                cursor.execute(f'DELETE FROM {self.name} WHERE prio = ?', (prio[0],))
                break

        connection.commit()
        connection.close()

        self.destroy()
        TasksManager(self.parent, self.row, self.name)

    def restore_tasks(self):
        connection = db.connect(f'{self.row}.db')
        cursor = connection.cursor()
        cursor.execute(f'SELECT name, prio FROM {self.name} ORDER BY prio ASC')
        tasks = cursor.fetchall()
        connection.close()

        for name, prio in tasks:
            checkbox_var = IntVar()
            self.checkboxes_vars.append(checkbox_var)
            
            textbox_font = CTkFont(family = FONT_FAMILY, size = 15)
            entry_font = CTkFont(family = FONT_FAMILY, size = 14)

            self.task_frame = CTkFrame(master = self.tasks_frame, fg_color = BLACK)
            checkbox = CTkCheckBox(master = self.task_frame, text = '', border_width = 1, border_color = WHITE,
                checkbox_width = 20, checkbox_height = 20, corner_radius = 15, hover_color = LIGHT_GRAY, width = 0,
                variable = checkbox_var, command = self.delete_task)
            
            self.textbox = CTkTextbox(master = self.task_frame, font = textbox_font, text_color = WHITE, height = 20,
                corner_radius = 0, border_spacing = 0, fg_color = BLACK, width = 225, activate_scrollbars = False,
                undo = True)
            
            self.entry = CTkEntry(master = self.task_frame, fg_color = DARK_GRAY, font = entry_font, justify = 'center',
                border_color = DARK_GRAY, width = 50, corner_radius = 10, text_color = WHITE)

            self.task_frame.pack(fill = 'x', padx = (0, 5), pady = (0, 5))
            checkbox.pack(side = 'left', padx = (10, 0), pady = 10)
            self.textbox.pack(side = 'left', pady = (6, 10))
            self.entry.pack(side = 'left', padx = 10, pady = 10)

            self.textbox.insert(index = '1.0', text = name)
            self.entry.insert(index = 'insert', string = prio)

            task_length = len(name)

            if task_length <= 25:
                # no permita que la tarea se expanda
                pass

            elif task_length <= 50:
                # permita que la tarea se expanda a dos lineas
                self.textbox.bind('<Enter>', lambda event: event.widget.configure(height = 2))
                self.textbox.bind('<Leave>', lambda event: event.widget.configure(height = 1))

            elif task_length <= 75:
                # permita que la tarea se expanda a tres lineas
                self.textbox.bind('<Enter>', lambda event: event.widget.configure(height = 3))
                self.textbox.bind('<Leave>', lambda event: event.widget.configure(height = 1))

            elif task_length <= 100:
                # permita que la tarea se expanda a cuatro lineas
                self.textbox.bind('<Enter>', lambda event: event.widget.configure(height = 4))
                self.textbox.bind('<Leave>', lambda event: event.widget.configure(height = 1))

            self.textbox.bind('<FocusIn>', lambda event: self.edit_task(event))
            self.entry.bind('<FocusIn>', lambda event: self.edit_task(event))

            first_char = name[0:1]
            if first_char == '#':
                self.textbox.configure(text_color = BLACK)

class Entry(CTkEntry):
    def __init__(self, parent, use, *args):
        font = CTkFont(family = FONT_FAMILY, size = 15)
        self.entry_var = StringVar()

        super().__init__(master = parent, fg_color = DARK_GRAY, border_color = DARK_GRAY, font = font, text_color = WHITE,
            width = 500, textvariable = self.entry_var)

        self.grid(row = 0, column = 1, columnspan = 2)

        self.focus()
        self.bind('<Escape>', lambda event: self.cancel())
        self.bind('<Return>', lambda event: self.confirm())

        self.parent = parent
        self.use = use

        if self.use == 'export notes':
            self.notepad = args[0]

        elif self.use == 'open notes':
            self.notepad = args[0]
            self.col = args[1]

        elif self.use == 'bother':
            self.entry_var.set(value = 'Get up, check phone, exercise or read')

        elif self.use == 'add project':
            self.row = args[0]

        elif self.use == 'rename project':
            self.row = args[0]
            self.name = args[1]
            self.tasks_manager = args[2]
            self.parent = args[3]

    def cancel(self):
        self.destroy()

    def confirm(self):
        if self.use == 'export notes':
            notes_name = self.entry_var.get()
            
            try:
                open(file = f'notes/{notes_name}.txt', mode = 'x')

                notes = self.notepad.get(index1 = '1.0', index2 = 'end-1c')
                doc = open(file = f'notes/{notes_name}.txt', mode = 'w')
                doc.write(notes)
                doc.close()
        
                self.destroy()
            except:
                pass

        elif self.use == 'open notes':
            notes_name = self.entry_var.get()
            
            try:
                doc = open(file = f'notes/{notes_name}.txt', mode = 'r')
                
                self.notepad.destroy()
                Notepad(self.parent, self.col, notes_name)

                self.destroy()
            except:
                pass

        elif self.use == 'add project':
            name = self.entry_var.get()

            connection = db.connect(f'{self.row}.db')
            cursor = connection.cursor()
            cursor.execute(f'CREATE TABLE IF NOT EXISTS {name} (name TEXT, prio INTEGER)')
            connection.commit()
            connection.close()

            self.destroy()

        elif self.use == 'rename project':
            new_name = self.entry_var.get()

            connection = db.connect(f'{self.row}.db')
            cursor = connection.cursor()
            cursor.execute(f'ALTER TABLE {self.name} RENAME TO {new_name}')
            connection.commit()
            connection.close()

            self.destroy()
            self.tasks_manager.destroy()
            TasksManager(self.parent, self.row, new_name)

if __name__ == '__main__':
    window = Window()
    window.mainloop()
