import re
import os

class ExpertSystem:
    def __init__(self, rule_file):
        self.rule_file = rule_file
        self.rules = []
        self.working_memory = {}
        self.variable_options = {}  # Словарь для хранения возможных значений переменных
        self.skipped_vars = set()  # Множество для отслеживания пропущенных переменных
        self.load_rules()
        self.extract_variable_options()
        
    def load_rules(self):
        """Загрузка правил из файла"""
        self.rules = []
        try:
            with open(self.rule_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.parse_rule(line)
        except FileNotFoundError:
            print(f"Файл правил {self.rule_file} не найден. Создан новый файл.")
            open(self.rule_file, 'w').close()

    def extract_variable_options(self):
        """Извлечение возможных значений переменных из правил"""
        self.variable_options = {}
        
        for rule in self.rules:
            # Обрабатываем только условия (не заключения)
            for condition_var, condition_val in rule['conditions']:
                if condition_var not in self.variable_options:
                    self.variable_options[condition_var] = set()
                self.variable_options[condition_var].add(condition_val)
        
        # Добавляем недостающие варианты для ключевых переменных
        if 'изображение_на_мониторе' in self.variable_options:
            self.variable_options['изображение_на_мониторе'].add('да')  # Нормальное состояние
        
        # Преобразуем множества в отсортированные списки
        for var in self.variable_options:
            self.variable_options[var] = sorted(list(self.variable_options[var]))

    def parse_rule(self, line):
        """Парсинг правила из строки"""
        pattern = r'ЕСЛИ\s+(.+)\s+ТО\s+(.+)'
        match = re.match(pattern, line)
        if match:
            conditions_str = match.group(1)
            conclusion_str = match.group(2)
            
            # Разбор условий
            conditions = []
            for condition in conditions_str.split(' И '):
                parts = condition.split('=')
                if len(parts) == 2:
                    conditions.append((parts[0].strip(), parts[1].strip()))
            
            # Разбор заключения
            parts = conclusion_str.split('=')
            if len(parts) == 2:
                conclusion = (parts[0].strip(), parts[1].strip())
                self.rules.append({'conditions': conditions, 'conclusion': conclusion})
            else:
                print(f"Ошибка в формате заключения: {line}")
        else:
            print(f"Ошибка в формате правила: {line}")

    def save_rules(self):
        """Сохранение правил в файл"""
        with open(self.rule_file, 'w', encoding='utf-8') as f:
            for rule in self.rules:
                conditions = ' И '.join([f"{var}={val}" for var, val in rule['conditions']])
                conclusion = f"{rule['conclusion'][0]}={rule['conclusion'][1]}"
                f.write(f"ЕСЛИ {conditions} ТО {conclusion}\n")
        
        # После сохранения правил обновляем возможные значения переменных
        self.extract_variable_options()

    def add_rule(self):
        """Добавление нового правила через интерактивный ввод"""
        print("\nДобавление нового правила")
        print("Формат: ЕСЛИ условие1=значение1 И условие2=значение2 ТО вывод=значение")
        
        conditions = []
        while True:
            condition_var = input("Введите переменную условия (или Enter для завершения): ").strip()
            if not condition_var:
                break
            
            # Показываем возможные значения для этой переменной, если они есть
            if condition_var in self.variable_options:
                print(f"Возможные значения для {condition_var}: {', '.join(self.variable_options[condition_var])}")
            
            condition_val = input("Введите значение условия: ").strip()
            conditions.append(f"{condition_var}={condition_val}")
        
        if not conditions:
            print("Необходимо указать хотя бы одно условие!")
            return
            
        conclusion_var = input("Введите переменную вывода: ").strip()
        conclusion_val = input("Введите значение вывода: ").strip()
        
        conditions_str = " И ".join(conditions)
        rule_text = f"ЕСЛИ {conditions_str} ТО {conclusion_var}={conclusion_val}"
        
        self.parse_rule(rule_text)
        self.save_rules()
        print("Правило успешно добавлено!")

    def delete_rule(self):
        """Удаление правила"""
        self.show_rules()
        try:
            rule_num = int(input("Введите номер правила для удаления: "))
            if 1 <= rule_num <= len(self.rules):
                del self.rules[rule_num-1]
                self.save_rules()
                print("Правило успешно удалено!")
            else:
                print("Неверный номер правила!")
        except ValueError:
            print("Ошибка: введите число!")

    def show_rules(self):
        """Отображение всех правил"""
        print("\nБаза правил:")
        if not self.rules:
            print("Правил нет.")
            return
            
        for i, rule in enumerate(self.rules, 1):
            conditions = ' И '.join([f"{var}={val}" for var, val in rule['conditions']])
            conclusion = f"{rule['conclusion'][0]}={rule['conclusion'][1]}"
            print(f"{i}. ЕСЛИ {conditions} ТО {conclusion}")

    def show_facts(self):
        """Отображение рабочей базы данных"""
        print("\nТекущие факты:")
        if not self.working_memory:
            print("Фактов нет.")
            return
            
        for var, val in self.working_memory.items():
            print(f"{var} = {val}")

    def add_fact(self):
        """Добавление факта в рабочую память с выбором из вариантов"""
        var = input("Введите имя переменной: ").strip()
        
        # Если для переменной есть известные варианты, предлагаем выбрать
        if var in self.variable_options:
            print(f"Возможные значения для {var}:")
            for i, val in enumerate(self.variable_options[var], 1):
                print(f"{i}. {val}")
            
            try:
                choice = int(input("Выберите значение (введите номер): "))
                if 1 <= choice <= len(self.variable_options[var]):
                    val = self.variable_options[var][choice-1]
                    self.working_memory[var] = val
                    print(f"Добавлен факт: {var} = {val}")
                else:
                    print("Неверный выбор!")
            except ValueError:
                print("Ошибка: введите число!")
        else:
            # Если вариантов нет, запрашиваем произвольное значение
            val = input("Введите значение переменной: ").strip()
            self.working_memory[var] = val
            print(f"Добавлен факт: {var} = {val}")

    def infer(self):
        """Логический вывод с прямой цепочкой рассуждений"""
        added = True
        iteration = 0
        max_iterations = 20  # Защита от бесконечного цикла
        
        while added and iteration < max_iterations:
            iteration += 1
            added = False
            
            # Проверяем правила в порядке их приоритета (порядке в файле)
            for rule in self.rules:
                # Проверяем, можно ли применить правило
                rule_applicable, missing_var = self.check_rule_with_missing(rule)
                
                if rule_applicable:
                    conclusion_var, conclusion_val = rule['conclusion']
                    
                    # Проверяем, не противоречит ли новый факт существующим
                    if conclusion_var in self.working_memory:
                        if self.working_memory[conclusion_var] != conclusion_val:
                            print(f"Конфликт: {conclusion_var} уже имеет значение {self.working_memory[conclusion_var]}, но правило пытается установить {conclusion_val}")
                            continue
                    
                    if conclusion_var not in self.working_memory:
                        self.working_memory[conclusion_var] = conclusion_val
                        print(f"Выведен новый факт: {conclusion_var} = {conclusion_val}")
                        added = True
                        
                        # Если выявлена проблема, завершаем диагностику
                        if conclusion_var == 'проблема':
                            return True
                        
                        break  # Прерываем для повторного прохода по правилам
                elif missing_var and missing_var not in self.skipped_vars:
                    # Запрашиваем недостающий факт для этого правила
                    if self.query_missing_fact(missing_var):
                        added = True
                        
                        # Если пользователь выбрал "нормальное" состояние, пропускаем эту переменную
                        if missing_var == 'изображение_на_мониторе' and self.working_memory.get(missing_var) == 'да':
                            self.skipped_vars.add(missing_var)
                            
                        # Проверяем, не была ли выявлена проблема в процессе запроса
                        if 'проблема' in self.working_memory:
                            return True
                            
                        break  # Прерываем для повторного прохода по правилам
            
            if not added:
                # Если больше нечего добавлять, проверяем, есть ли правила, которые могут сработать
                # при наличии дополнительной информации
                if not self.query_any_missing_fact():
                    break
                    
        return False

    def check_rule(self, rule):
        """Проверка условий правила"""
        for condition_var, condition_val in rule['conditions']:
            if condition_var not in self.working_memory:
                return False
            if self.working_memory[condition_var] != condition_val:
                return False
        return True

    def check_rule_with_missing(self, rule):
        """Проверка условий правила с возвратом отсутствующей переменной"""
        for condition_var, condition_val in rule['conditions']:
            if condition_var not in self.working_memory:
                return False, condition_var  # Правило не применимо, возвращаем отсутствующую переменную
            if self.working_memory[condition_var] != condition_val:
                return False, None  # Условие не выполняется, но переменная есть
        return True, None  # Все условия выполнены

    def query_missing_fact(self, var):
        """Запрос одного недостающего факта"""
        # Не запрашиваем значения для переменных "проблема" и "решение"
        if var in ['проблема', 'решение']:
            self.skipped_vars.add(var)
            return False

        if var not in self.working_memory and var not in self.skipped_vars:
            # Если для переменной есть известные варианты, предлагаем выбрать
            if var in self.variable_options:
                print(f"\nДля продолжения диагностики нужно знать значение {var}:")
                options = self.variable_options[var]
                
                for i, val in enumerate(options, 1):
                    print(f"{i}. {val}")
                
                # Добавляем опцию пропуска
                print(f"{len(options) + 1}. Пропустить")
                
                try:
                    choice = int(input("Ваш выбор (введите номер): "))
                    if 1 <= choice <= len(options):
                        val = options[choice-1]
                        self.working_memory[var] = val
                        print(f"Добавлен факт: {var} = {val}")
                        return True
                    elif choice == len(options) + 1:
                        print(f"Пропускаем переменную {var}")
                        self.skipped_vars.add(var)
                        return False
                    else:
                        print("Неверный выбор!")
                        return False
                except ValueError:
                    print("Ошибка: введите число!")
                    return False
            else:
                # Если вариантов нет, запрашиваем произвольное значение
                val = input(f"Введите значение для {var} (или Enter для пропуска): ")
                if val:
                    self.working_memory[var] = val
                    return True
                else:
                    print(f"Пропускаем переменную {var}")
                    self.skipped_vars.add(var)
                    return False
        return False

    def query_any_missing_fact(self):
        """Запрос любой недостающей информации из всех правил"""
        # Сначала пытаемся найти правила, которые могут сработать с текущими данными
        for rule in self.rules:
            # Проверяем, можно ли применить правило
            rule_applicable, missing_var = self.check_rule_with_missing(rule)
            
            if rule_applicable:
                conclusion_var, conclusion_val = rule['conclusion']
                
                if conclusion_var not in self.working_memory:
                    self.working_memory[conclusion_var] = conclusion_val
                    print(f"Выведен новый факт: {conclusion_var} = {conclusion_val}")
                    
                    # Если выявлена проблема, завершаем диагностику
                    if conclusion_var == 'проблема':
                        return True
                    
                    return True
        
        # Если нет правил, которые можно применить, ищем переменные для запроса
        missing_vars = set()
        
        for rule in self.rules:
            for condition_var, _ in rule['conditions']:
                if (condition_var not in self.working_memory and 
                    condition_var not in self.skipped_vars):
                    missing_vars.add(condition_var)
        
        if not missing_vars:
            return False

        print("\nДля продолжения диагностики нужна дополнительная информация:")
        for var in missing_vars:
            if var not in self.working_memory and var not in self.skipped_vars:
                # Если для переменной есть известные варианты, предлагаем выбрать
                if var in self.variable_options:
                    print(f"\nВыберите значение для {var}:")
                    options = self.variable_options[var]
                    
                    for i, val in enumerate(options, 1):
                        print(f"{i}. {val}")
                    
                    print(f"{len(options) + 1}. Пропустить")
                    
                    try:
                        choice = int(input("Ваш выбор (введите номер): "))
                        if 1 <= choice <= len(options):
                            val = options[choice-1]
                            self.working_memory[var] = val
                            print(f"Добавлен факт: {var} = {val}")
                            
                            # Проверяем, не была ли выявлена проблема в процессе запроса
                            if 'проблема' in self.working_memory:
                                return True
                                
                            return True
                        elif choice == len(options) + 1:
                            print(f"Пропускаем переменную {var}")
                            self.skipped_vars.add(var)
                        else:
                            print("Неверный выбор!")
                    except ValueError:
                        print("Ошибка: введите число!")
                else:
                    # Если вариантов нет, запрашиваем произвольное значение
                    val = input(f"Введите значение для {var} (или Enter для пропуска): ")
                    if val:
                        self.working_memory[var] = val
                        
                        # Проверяем, не была ли выявлена проблема в процессе запроса
                        if 'проблема' in self.working_memory:
                            return True
                            
                        return True
                    else:
                        print(f"Пропускаем переменную {var}")
                        self.skipped_vars.add(var)
        
        return False

    def clear_facts(self):
        """Очистка рабочей памяти"""
        self.working_memory = {}
        self.skipped_vars = set()
        print("Рабочая память очищена.")

    def show_variable_options(self):
        """Показать возможные значения для всех переменных"""
        print("\nВозможные значения переменных (только для условий):")
        for var, options in self.variable_options.items():
            print(f"{var}: {', '.join(options)}")

    def get_input_with_options(self, var):
        """Получение ввода с вариантами выбора для переменной"""
        if var in self.variable_options:
            print(f"\nВыберите значение для {var}:")
            for i, val in enumerate(self.variable_options[var], 1):
                print(f"{i}. {val}")
            
            while True:
                try:
                    choice = int(input("Ваш выбор (введите номер): "))
                    if 1 <= choice <= len(self.variable_options[var]):
                        return self.variable_options[var][choice-1]
                    else:
                        print("Неверный выбор!")
                except ValueError:
                    print("Ошибка: введите число!")
        else:
            return input(f"Введите значение для {var}: ").strip()

def main():
    rule_file = "rules.txt"
    es = ExpertSystem(rule_file)
    
    while True:
        print("\n" + "="*60)
        print("Экспертная система диагностики неисправностей компьютера")
        print("1. Выполнить диагностику")
        print("2. Показать правила")
        print("3. Добавить правило")
        print("4. Удалить правило")
        print("5. Выход")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            # Очищаем рабочую память перед началом диагностики
            es.working_memory = {}
            es.skipped_vars = set()
            
            # Запрашиваем начальные симптомы
            print("\nДля начала диагностики ответьте на несколько вопросов:")
            
            # Получаем начальные данные с вариантами выбора
            if 'компьютер_включается' in es.variable_options:
                print("Выберите значение для компьютер_включается:")
                options = es.variable_options['компьютер_включается']
                for i, val in enumerate(options, 1):
                    print(f"{i}. {val}")
                
                try:
                    choice = int(input("Ваш выбор (введите номер): "))
                    if 1 <= choice <= len(options):
                        es.working_memory['компьютер_включается'] = options[choice-1]
                    else:
                        print("Неверный выбор! Установлено значение по умолчанию: нет")
                        es.working_memory['компьютер_включается'] = 'нет'
                except ValueError:
                    print("Ошибка: введите число! Установлено значение по умолчанию: нет")
                    es.working_memory['компьютер_включается'] = 'нет'
            
            print("\nНачинаем диагностику...")
            es.show_facts()
            
            # Выполняем вывод
            problem_found = es.infer()
            
            print("\nДиагностика завершена!")
            
            # Вывод результатов
            if 'проблема' in es.working_memory:
                print(f"\nВыявленная проблема: {es.working_memory['проблема']}")
                
                # Если есть рекомендация по решению, выводим её
                if 'решение' in es.working_memory:
                    print(f"Рекомендуемое решение: {es.working_memory['решение']}")
            else:
                print("\nНе удалось выявить конкретную проблему.")
                print("Возможные причины:")
                print("- Компьютер работает нормально")
                print("- Проблема не описана в базе знаний")
                print("Рекомендуется обратиться в сервисный центр для профессиональной диагностики.")
            
            es.show_facts()
            
        elif choice == '2':
            es.show_rules()
            
        elif choice == '3':
            es.add_rule()
            
        elif choice == '4':
            es.delete_rule()
            
        elif choice == '5':
            break
            
        else:
            print("Неверный выбор!")

if __name__ == "__main__":
    main()