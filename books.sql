--
-- ���� ������������ � ������� SQLiteStudio v3.2.1 � �� ��� 1 16:14:32 2020
--
-- �������������� ��������� ������: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- �������: books
CREATE TABLE books (ids TEXT, name TEXT, author TEXT, year INTEGER, genre TEXT, position INTEGER);

-- �������: given
CREATE TABLE given (id TEXT, name TEXT);

-- �������: reader
CREATE TABLE reader (id TEXT, name TEXT, date TEXT, info TEXT);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
