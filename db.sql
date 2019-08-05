create table if not exists proxy
(
	id serial not null,
	taskid varchar(20),
	proxy varchar(50)
);

alter table proxy owner to "postgres";

create table if not exists stock_master
(
	stockcode varchar(10),
	stockabbre varchar(100),
	industryclassification varchar(200)
);

alter table stock_master owner to "postgres";

create table if not exists stock_price
(
	id serial not null,
	taskid varchar(20),
	stockcode varchar(20),
	date date,
	open double precision,
	high double precision,
	low double precision,
	close double precision,
	adjclose double precision,
	volume double precision
);

alter table stock_price owner to "postgres";

create table if not exists sys_log
(
	id serial not null,
	taskid varchar(20),
	action varchar(100),
	status varchar(10),
	message varchar(5000),
	created_at date
);

alter table sys_log owner to "postgres";

