drop table if exists books;
drop table if exists works;
drop table if exists series;
create table books (
  bookId integer primary key not null,
  workId integer
);
create table works (
  workId integer primary key not null,
  bestBookId integer,
  seriesId integer,
  position real,
  publicationDate integer,
  lastChecked integer
);
create table series (
  seriesId integer primary key not null,
  lastChecked integer
);