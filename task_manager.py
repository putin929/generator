#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер задач с приоритетами
Простой и эффективный инструмент для управления задачами с системой приоритетов
"""

import json
import datetime
from enum import Enum
import os

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class Status(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskManager:
    def __init__(self, data_file="tasks.json"):
        self.data_file = data_file
        self.tasks = []
        self.next_id = 1
        self.load_data()
    
    def load_data(self):
        """Загружает задачи из файла"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', [])
                    self.next_id = data.get('next_id', 1)
                    
                    # Восстанавливаем даты из строк
                    for task in self.tasks:
                        if task.get('created_date'):
                            task['created_date'] = datetime.datetime.strptime(
                                task['created_date'], '%Y-%m-%d %H:%M:%S'
                            )
                        if task.get('due_date'):
                            task['due_date'] = datetime.datetime.strptime(
                                task['due_date'], '%Y-%m-%d'
                            ).date()
                        if task.get('completed_date'):
                            task['completed_date'] = datetime.datetime.strptime(
                                task['completed_date'], '%Y-%m-%d %H:%M:%S'
                            )
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
            self.tasks = []
            self.next_id = 1
    
    def save_data(self):
        """Сохраняет задачи в файл"""
        try:
            # Конвертируем даты в строки для JSON
            tasks_to_save = []
            for task in self.tasks:
                task_copy = task.copy()
                if task.get('created_date'):
                    task_copy['created_date'] = task['created_date'].strftime('%Y-%m-%d %H:%M:%S')
                if task.get('due_date'):
                    task_copy['due_date'] = task['due_date'].strftime('%Y-%m-%d')
                if task.get('completed_date'):
                    task_copy['completed_date'] = task['completed_date'].strftime('%Y-%m-%d %H:%M:%S')
                tasks_to_save.append(task_copy)
            
            data = {
                'tasks': tasks_to_save,
                'next_id': self.next_id
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка при сохранении данных: {e}")
    
    def add_task(self, title, description="", priority=Priority.MEDIUM, due_date=None):
        """
        Добавляет новую задачу
        
        Args:
            title (str): Название задачи
            description (str): Описание задачи
            priority (Priority): Приоритет задачи
            due_date (date): Срок выполнения
        """
        task = {
            'id': self.next_id,
            'title': title,
            'description': description,
            'priority': priority.value,
            'status': Status.TODO.value,
            'created_date': datetime.datetime.now(),
            'due_date': due_date,
            'completed_date': None
        }
        
        self.tasks.append(task)
        self.next_id += 1
        self.save_data()
        
        priority_name = priority.name.lower()
        print(f"✅ Задача добавлена: '{title}' (приоритет: {priority_name})")
    
    def get_task_by_id(self, task_id):
        """Находит задачу по ID"""
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def update_task_status(self, task_id, new_status):
        """Обновляет статус задачи"""
        task = self.get_task_by_id(task_id)
        if not task:
            print(f"❌ Задача с ID {task_id} не найдена")
            return
        
        old_status = task['status']
        task['status'] = new_status.value
        
        if new_status == Status.DONE and old_status != Status.DONE.value:
            task['completed_date'] = datetime.datetime.now()
        elif new_status != Status.DONE:
            task['completed_date'] = None
        
        self.save_data()
        print(f"✅ Статус задачи '{task['title']}' изменен на {new_status.value}")
    
    def delete_task(self, task_id):
        """Удаляет задачу"""
        task = self.get_task_by_id(task_id)
        if not task:
            print(f"❌ Задача с ID {task_id} не найдена")
            return
        
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
        self.save_data()
        print(f"🗑️ Задача '{task['title']}' удалена")
    
    def get_tasks(self, status=None, sort_by='priority'):
        """
        Получает отфильтрованные и отсортированные задачи
        
        Args:
            status (Status): Фильтр по статусу
            sort_by (str): Сортировка ('priority', 'due_date', 'created_date')
        """
        filtered_tasks = self.tasks.copy()
        
        if status:
            filtered_tasks = [t for t in filtered_tasks if t['status'] == status.value]
        
        # Сортировка
        if sort_by == 'priority':
            # Сортировка по приоритету (убывание) и дате создания
            filtered_tasks.sort(key=lambda x: (-x['priority'], x['created_date']))
        elif sort_by == 'due_date':
            # Сортировка по сроку выполнения (задачи без срока в конце)
            filtered_tasks.sort(key=lambda x: (
                x['due_date'] is None,
                x['due_date'] if x['due_date'] else datetime.date.max
            ))
        elif sort_by == 'created_date':
            filtered_tasks.sort(key=lambda x: x['created_date'], reverse=True)
        
        return filtered_tasks
    
    def display_tasks(self, status=None, show_completed=False):
        """Отображает задачи в красивом формате"""
        if status:
            tasks = self.get_tasks(status=status)
            print(f"\n📋 Задачи со статусом '{status.value.replace('_', ' ')}':")
        elif show_completed:
            tasks = self.get_tasks()
            print("\n📋 Все задачи:")
        else:
            tasks = [t for t in self.get_tasks() if t['status'] != Status.DONE.value]
            print("\n📋 Активные задачи:")
        
        if not tasks:
            print("Задач не найдено.")
            return
        
        print("-" * 100)
        
        for task in tasks:
            # Иконки для статуса
            status_icons = {
                'todo': '⏳',
                'in_progress': '🔄',
                'done': '✅'
            }
            
            # Иконки для приоритета
            priority_icons = {
                1: '🟢',  # LOW
                2: '🟡',  # MEDIUM
                3: '🟠',  # HIGH
                4: '🔴'   # URGENT
            }
            
            status_icon = status_icons.get(task['status'], '❓')
            priority_icon = priority_icons.get(task['priority'], '⚪')
            
            # Проверка просроченности
            overdue = ""
            if task['due_date'] and task['status'] != Status.DONE.value:
                if task['due_date'] < datetime.date.today():
                    overdue = " ⚠️ ПРОСРОЧЕНО"
                elif task['due_date'] == datetime.date.today():
                    overdue = " 🎯 СЕГОДНЯ"
            
            print(f"{status_icon} {priority_icon} [{task['id']}] {task['title']}{overdue}")
            
            if task['description']:
                print(f"    📝 {task['description']}")
            
            if task['due_date']:
                print(f"    📅 Срок: {task['due_date']}")
            
            if task['completed_date']:
                print(f"    ✅ Выполнено: {task['completed_date'].strftime('%Y-%m-%d %H:%M')}")
            
            print()
    
    def get_statistics(self):
        """Получает статистику по задачам"""
        total = len(self.tasks)
        todo = len([t for t in self.tasks if t['status'] == Status.TODO.value])
        in_progress = len([t for t in self.tasks if t['status'] == Status.IN_PROGRESS.value])
        done = len([t for t in self.tasks if t['status'] == Status.DONE.value])
        
        # Просроченные задачи
        overdue = len([
            t for t in self.tasks 
            if t['due_date'] and t['due_date'] < datetime.date.today() 
            and t['status'] != Status.DONE.value
        ])
        
        # Задачи на сегодня
        today_tasks = len([
            t for t in self.tasks 
            if t['due_date'] and t['due_date'] == datetime.date.today()
            and t['status'] != Status.DONE.value
        ])
        
        return {
            'total': total,
            'todo': todo,
            'in_progress': in_progress,
            'done': done,
            'overdue': overdue,
            'today': today_tasks
        }

def main():
    task_manager = TaskManager()
    
    print("=== МЕНЕДЖЕР ЗАДАЧ ===\n")
    
    while True:
        print("1. Добавить задачу")
        print("2. Показать активные задачи")
        print("3. Показать все задачи")
        print("4. Изменить статус задачи")
        print("5. Удалить задачу")
        print("6. Статистика")
        print("7. Выход")
        
        choice = input("\nВыберите действие (1-7): ")
        
        if choice == "1":
            title = input("Название задачи: ").strip()
            if not title:
                print("❌ Название задачи не может быть пустым")
                continue
            
            description = input("Описание (необязательно): ").strip()
            
            print("Приоритет:")
            print("1. Низкий")
            print("2. Средний")
            print("3. Высокий") 
            print("4. Срочный")
            
            try:
                priority_choice = int(input("Выберите приоритет (1-4, по умолчанию 2): ") or "2")
                priority = Priority(priority_choice)
            except (ValueError, KeyError):
                priority = Priority.MEDIUM
                print("Используется средний приоритет")
            
            # Срок выполнения
            due_date_str = input("Срок выполнения (YYYY-MM-DD) или Enter для пропуска: ").strip()
            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
                except ValueError:
                    print("❌ Неверный формат даты, срок не установлен")
            
            task_manager.add_task(title, description, priority, due_date)
            
        elif choice == "2":
            task_manager.display_tasks()
            
        elif choice == "3":
            task_manager.display_tasks(show_completed=True)
            
        elif choice == "4":
            try:
                task_id = int(input("ID задачи для изменения статуса: "))
                
                print("Новый статус:")
                print("1. К выполнению")
                print("2. В процессе")
                print("3. Выполнено")
                
                status_choice = int(input("Выберите статус (1-3): "))
                status_map = {1: Status.TODO, 2: Status.IN_PROGRESS, 3: Status.DONE}
                
                if status_choice in status_map:
                    task_manager.update_task_status(task_id, status_map[status_choice])
                else:
                    print("❌ Неверный выбор статуса")
                    
            except ValueError:
                print("❌ Введите корректный ID задачи")
                
        elif choice == "5":
            try:
                task_id = int(input("ID задачи для удаления: "))
                confirm = input(f"Вы уверены, что хотите удалить задачу {task_id}? (y/N): ")
                if confirm.lower() == 'y':
                    task_manager.delete_task(task_id)
                else:
                    print("Удаление отменено")
            except ValueError:
                print("❌ Введите корректный ID задачи")
                
        elif choice == "6":
            stats = task_manager.get_statistics()
            print("\n📊 СТАТИСТИКА ЗАДАЧ")
            print("=" * 30)
            print(f"📋 Всего задач: {stats['total']}")
            print(f"⏳ К выполнению: {stats['todo']}")
            print(f"🔄 В процессе: {stats['in_progress']}")
            print(f"✅ Выполнено: {stats['done']}")
            
            if stats['overdue'] > 0:
                print(f"⚠️ Просрочено: {stats['overdue']}")
            
            if stats['today'] > 0:
                print(f"🎯 На сегодня: {stats['today']}")
            
            if stats['total'] > 0:
                completion_rate = (stats['done'] / stats['total']) * 100
                print(f"📈 Процент выполнения: {completion_rate:.1f}%")
                
        elif choice == "7":
            print("До свидания! 📋")
            break
            
        else:
            print("❌ Неверный выбор. Попробуйте снова.")
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
