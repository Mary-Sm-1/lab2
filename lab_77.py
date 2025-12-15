import re
import urllib.request
import urllib.error
from typing import Optional


class MyFile:
    """
    Класс для работы с файлами и URL.
    Поддерживает режимы: read, write, append, url.
    """
    
    def __init__(self, path: str, mode: str = "read"):
        """
        Инициализация объекта MyFile.
        
        Args:
            path: Путь к файлу или URL
            mode: Режим работы ('read', 'write', 'append', 'url')
        
        Raises:
            ValueError: Если указан недопустимый режим
        """
        self.path = path
        self.mode = mode.lower()
        self.file = None
        
        # Проверяем допустимость режима
        valid_modes = ["read", "write", "append", "url"]
        if self.mode not in valid_modes:
            raise ValueError(f"Недопустимый режим '{mode}'. Допустимые режимы: {valid_modes}")
        
        # Если режим url, проверяем что передан URL
        if self.mode == "url" and not self._is_url(path):
            raise ValueError(f"'{path}' не является валидным URL для режима 'url'")
    
    def _is_url(self, path: str) -> bool:
        """Проверяет, является ли строка URL."""
        url_patterns = ["http://", "https://", "ftp://", "file://"]
        return any(path.startswith(pattern) for pattern in url_patterns)
    
    def _open_file(self):
        """Открывает файл в соответствии с режимом."""
        if self.mode == "read":
            self.file = open(self.path, 'r', encoding='utf-8')
        elif self.mode == "write":
            self.file = open(self.path, 'w', encoding='utf-8')
        elif self.mode == "append":
            self.file = open(self.path, 'a', encoding='utf-8')
    
    def _close_file(self):
        """Закрывает файл, если он открыт."""
        if self.file and not self.file.closed:
            self.file.close()
    
    def read(self) -> str:
        """
        Читает содержимое файла.
        
        Returns:
            str: Содержимое файла
            
        Raises:
            ValueError: Если объект не в режиме 'read'
            IOError: Если файл не существует или не может быть прочитан
        """
        if self.mode != "read":
            raise ValueError(f"Метод read() доступен только в режиме 'read', текущий режим: '{self.mode}'")
        
        try:
            self._open_file()
            return self.file.read()
        except FileNotFoundError:
            raise IOError(f"Файл '{self.path}' не найден")
        except PermissionError:
            raise IOError(f"Нет прав на чтение файла '{self.path}'")
        finally:
            self._close_file()
    
    def write(self, content: str) -> bool:
        """
        Записывает содержимое в файл.
        
        Args:
            content: Строка для записи
            
        Returns:
            bool: True если запись успешна
            
        Raises:
            ValueError: Если объект не в режиме 'write' или 'append'
            IOError: Если файл не может быть записан
        """
        if self.mode not in ["write", "append"]:
            raise ValueError(f"Метод write() доступен только в режимах 'write' или 'append', текущий режим: '{self.mode}'")
        
        try:
            self._open_file()
            self.file.write(content)
            return True
        except PermissionError:
            raise IOError(f"Нет прав на запись в файл '{self.path}'")
        except Exception as e:
            raise IOError(f"Ошибка при записи в файл: {e}")
        finally:
            self._close_file()
    
    def read_url(self) -> str:
        """
        Читает содержимое веб-страницы по URL.
        
        Returns:
            str: HTML-содержимое страницы
            
        Raises:
            ValueError: Если объект не в режиме 'url'
            IOError: Если URL недоступен
        """
        if self.mode != "url":
            raise ValueError(f"Метод read_url() доступен только в режиме 'url', текущий режим: '{self.mode}'")
        
        try:
            # Устанавливаем заголовки, чтобы не блокировали как бота
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            req = urllib.request.Request(self.path, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                # Пытаемся определить кодировку
                content = response.read()
                
                # Пробуем разные кодировки
                encodings = ['utf-8', 'cp1251', 'koi8-r', 'iso-8859-1']
                
                for encoding in encodings:
                    try:
                        return content.decode(encoding)
                    except UnicodeDecodeError:
                        continue
                
                # Если ни одна кодировка не подошла, возвращаем как utf-8 с заменой ошибок
                return content.decode('utf-8', errors='replace')
                
        except urllib.error.HTTPError as e:
            raise IOError(f"HTTP ошибка {e.code}: {e.reason} для URL {self.path}")
        except urllib.error.URLError as e:
            raise IOError(f"Ошибка URL: {e.reason} для URL {self.path}")
        except TimeoutError:
            raise IOError(f"Таймаут при загрузке URL {self.path}")
        except Exception as e:
            raise IOError(f"Ошибка при чтении URL: {e}")
    
    def count_urls(self) -> int:
        """
        Подсчитывает количество URL-адресов на веб-странице.
        
        Returns:
            int: Количество найденных URL
            
        Raises:
            ValueError: Если объект не в режиме 'url'
        """
        if self.mode != "url":
            raise ValueError(f"Метод count_urls() доступен только в режиме 'url', текущий режим: '{self.mode}'")
        
        try:
            html_content = self.read_url()
            
            # Регулярное выражение для поиска URL в HTML
            # Ищем ссылки в href, src и других атрибутах
            url_patterns = [
                r'href=["\'](https?://[^"\']+)["\']',  # href="http://..."
                r'src=["\'](https?://[^"\']+)["\']',   # src="http://..."
                r'url\(["\']?(https?://[^"\')]+)["\']?\)',  # url(http://...)
            ]
            
            urls = set()  # Используем set чтобы избежать дубликатов
            
            for pattern in url_patterns:
                found_urls = re.findall(pattern, html_content, re.IGNORECASE)
                urls.update(found_urls)
            
            # Также ищем ссылки без кавычек (более общий паттерн)
            general_pattern = r'https?://[^\s<>"\']+'
            general_urls = re.findall(general_pattern, html_content, re.IGNORECASE)
            urls.update(general_urls)
            
            return len(urls)
            
        except Exception as e:
            # Если не удалось прочитать URL, возвращаем 0
            print(f"Предупреждение: не удалось подсчитать URL: {e}")
            return 0
    
    def write_url(self, filepath: str) -> bool:
        """
        Сохраняет содержимое веб-страницы в файл.
        
        Args:
            filepath: Путь к файлу для сохранения
            
        Returns:
            bool: True если запись успешна
            
        Raises:
            ValueError: Если объект не в режиме 'url'
            IOError: Если URL недоступен или файл не может быть записан
        """
        if self.mode != "url":
            raise ValueError(f"Метод write_url() доступен только в режиме 'url', текущий режим: '{self.mode}'")
        
        try:
            # Читаем содержимое URL
            content = self.read_url()
            
            # Создаем объект для записи в файл
            file_writer = MyFile(filepath, "write")
            success = file_writer.write(content)
            
            if success:
                print(f"Содержимое URL успешно сохранено в файл: {filepath}")
            
            return success
            
        except Exception as e:
            raise IOError(f"Ошибка при сохранении содержимого URL в файл: {e}")
    
    def __enter__(self):
        """Поддержка контекстного менеджера."""
        if self.mode in ["read", "write", "append"]:
            self._open_file()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Завершение работы контекстного менеджера."""
        if self.mode in ["read", "write", "append"]:
            self._close_file()
    
    def __repr__(self):
        return f"MyFile(path='{self.path}', mode='{self.mode}')"
    
    def __del__(self):
        """Деструктор - закрывает файл при удалении объекта."""
        self._close_file()


def display_menu():
    """Отображает меню для пользователя."""
    print("\n" + "=" * 50)
    print("МЕНЮ РАБОТЫ С ФАЙЛАМИ И URL")
    print("=" * 50)
    print("1. Работа с файлом (чтение/запись)")
    print("2. Работа с URL")
    print("3. Выход")
    print("=" * 50)


def file_operations():
    """Обрабатывает операции с файлами."""
    print("\n" + "-" * 30)
    print("РАБОТА С ФАЙЛАМИ")
    print("-" * 30)
    
    # Запрос пути к файлу
    file_path = input("Введите путь к файлу: ").strip()
    
    # Выбор режима работы
    print("\nВыберите режим работы:")
    print("1. Чтение файла")
    print("2. Запись в файл (перезапись)")
    print("3. Добавление в файл")
    
    mode_choice = input("Введите номер режима (1-3): ").strip()
    
    mode_map = {
        "1": "read",
        "2": "write", 
        "3": "append"
    }
    
    if mode_choice not in mode_map:
        print("Ошибка: неверный выбор режима")
        return
    
    mode = mode_map[mode_choice]
    
    try:
        # Создаем объект MyFile
        file_obj = MyFile(file_path, mode)
        
        if mode == "read":
            # Чтение файла
            content = file_obj.read()
            print(f"\nСодержимое файла '{file_path}':")
            print("=" * 40)
            print(content)
            print("=" * 40)
            
        elif mode in ["write", "append"]:
            # Запись или добавление в файл
            print(f"\nВведите содержимое для {'записи' if mode == 'write' else 'добавления'}:")
            print("(Для завершения ввода введите пустую строку или 'END' на отдельной строке)")
            print("-" * 40)
            
            lines = []
            line_num = 1
            while True:
                line = input(f"Строка {line_num}: ").strip()
                if line == "" or line.upper() == "END":
                    break
                lines.append(line)
                line_num += 1
            
            content = "\n".join(lines)
            
            # Выполняем запись
            success = file_obj.write(content)
            if success:
                action = "записано" if mode == "write" else "добавлено"
                print(f"\n✓ Содержимое успешно {action} в файл '{file_path}'")
                
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")


def url_operations():
    """Обрабатывает операции с URL."""
    print("\n" + "-" * 30)
    print("РАБОТА С URL")
    print("-" * 30)
    
    # Запрос URL
    url = input("Введите URL (например, https://example.com): ").strip()
    
    # Проверяем, что URL начинается с протокола
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    
    try:
        # Создаем объект MyFile в режиме url
        url_obj = MyFile(url, "url")
        
        # Выбор операции с URL
        print("\nВыберите операцию:")
        print("1. Прочитать содержимое страницы")
        print("2. Подсчитать количество ссылок на странице")
        print("3. Сохранить содержимое страницы в файл")
        
        operation = input("Введите номер операции (1-3): ").strip()
        
        if operation == "1":
            # Чтение содержимого URL
            content = url_obj.read_url()
            print(f"\nСодержимое страницы '{url}':")
            print("=" * 60)
            print(content[:1000] + ("..." if len(content) > 1000 else ""))
            print("=" * 60)
            print(f"Общий размер: {len(content)} символов")
            
        elif operation == "2":
            # Подсчет ссылок
            url_count = url_obj.count_urls()
            print(f"\n✓ На странице '{url}' найдено {url_count} URL-адресов")
            
        elif operation == "3":
            # Сохранение содержимого в файл
            save_path = input("Введите путь для сохранения файла: ").strip()
            if not save_path:
                # Генерируем имя файла на основе URL
                domain = url.split("//")[-1].split("/")[0]
                save_path = f"{domain}_content.html"
            
            success = url_obj.write_url(save_path)
            if success:
                print(f"\n✓ Содержимое успешно сохранено в файл '{save_path}'")
                
        else:
            print("\n✗ Ошибка: неверный выбор операции")
            
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        print("Возможные причины:")
        print("- Отсутствует интернет-соединение")
        print("- URL недоступен или не существует")
        print("- Ошибка доступа к URL")


def main():
    """Основная функция программы."""
    print("=" * 50)
    print("ПРОГРАММА ДЛЯ РАБОТЫ С ФАЙЛАМИ И URL")
    print("=" * 50)
    
    while True:
        display_menu()
        
        choice = input("\nВыберите действие (1-3): ").strip()
        
        if choice == "1":
            file_operations()
        elif choice == "2":
            url_operations()
        elif choice == "3":
            print("\nДо свидания!")
            break
        else:
            print("\nОшибка: введите число от 1 до 3")
        
        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nПрограмма завершена пользователем.")
    except Exception as e:
        print(f"\nПроизошла непредвиденная ошибка: {e}")