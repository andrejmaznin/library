--
-- Файл сгенерирован с помощью SQLiteStudio v3.2.1 в Вс ноя 1 16:14:32 2020
--
-- Использованная кодировка текста: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: books
CREATE TABLE books (ids TEXT, name TEXT, author TEXT, year INTEGER, genre TEXT, position INTEGER);

-- Таблица: given
CREATE TABLE given (id TEXT, name TEXT);

-- Таблица: reader
CREATE TABLE reader (id TEXT, name TEXT, date TEXT, info TEXT);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
