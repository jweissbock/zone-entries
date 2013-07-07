drop table if exists users;
create table users (
	id integer primary key autoincrement,
	email text unique not null,
	password text not null,
	admin integer
);

drop table if exists entries;
create table entries (
	id integer primary key autoincrement, 
	gameid integer not null,
	tracker integer not null,
	team text not null,
	period integer not null,
	time integer not null,
	exittype text not null,
	player text not null,
	pressure text not null,
	strength text not null
);
