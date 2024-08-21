# Content
- [Introduction to SQL](#introduction-to-sql)
- [SQL Categories](#sql-categories)
  - [DQL](#dql)
  - [DML](#dml)
  - [DDL](#ddl)
  - [DCL](#dcl)
  - [TCL](#tcl)
- [SQL Clauses](#sql-clauses)
- [SQL Functions](#sql-functions)
  - [Aggregate Functions](#aggregate-functions)
  - [String Functions](#string-functions)
  - [Date Functions](#date-functions)
  - [Numeric Functions](#numeric-functions)
  - [Conversion Functions](#conversion-functions)
  - [Conditional Functions](#conditional-functions)
  - [Mathematical Functions](#mathematical-functions)
  - [Window Functions](#window-functions) 
  - [System Functions](#system-functions)
- [Other SQL Concepts](#other-sql-concepts)
  - [Operators](#operators)
  - [Indexes](#indexes)
  - [Constraints](#constraints)
  - [Views](#views)
  - [Stored Procedures and Functions](#stored-procedures-and-functions)
  - [Triggers](#triggers)
  - [Transactions](#transactions)
- [Testing SQL](#testing-sql)
- [SQL Service INSTALLATION](#sql-service-installation)
- [Other SQL Concepts](#other-sql-concepts)
- [Hierarchical Structure of Databases](#hierarchical-structure-of-databases)





# Introduction to SQL

## `SQL` vs `NoSQL`

- SQL: `Structured Query Language`, used for storing `Structured Data`
- NoSQL: `Not Only SQL`, used for storing `Not Necessarily Structured Data`. It is a family of database management systems designed to handle the unique challenges posed by Big Data.



## SQL Standard
`ANSI` SQL is the standard for the SQL. It was created by "American National Standards Institute"



# SQL Categories
There are four categories of SQL:
- DQL (Data Query Language)
  - SELECT

- DML (Data Manipulation Language)
  - INSERT
  - UPDATE
  - DELETE

- DDL (Data Definition Language)
  - CREATE
  - ALTER
  - DROP
  - TRUNCATE

- DCL (Data Control Language)
  - GRANT
  - REVOKE

- TCL (Transaction Control Language)
  - BEGIN
  - COMMIT
  - ROLLBACK



## DQL (Data Query Language)

### SELECT

```sql
select last_name last_nm, first_name as first_nm
from public.actor;

-- `as` is an optional clause or command used to set a column's alias
```

#### DISTINCT
Ensures that the result set contains unique rows by eliminating duplicates.

```sql
SELECT DISTINCT film_id, store_id from inventory;
```

> **⚠**️ Be careful when using `DISTINCT` with more than one column!
If there is only one column, using or not using parenthesis is the same.
```sql
SELECT DISTINCT film_id from inventory;
```
is the same as:
```sql
SELECT DISTINCT(film_id) from inventory;
```

However, if there are more than one columns, the use of () is wrong:
```sql
-- this is the correct way
SELECT DISTINCT film_id, store_id from inventory;
```
Output:
![alt text](images/distinct_right.png)

```sql
-- this is the wrong way, which results in an error
SELECT DISTINCT(film_id, store_id) from inventory; -- notice there is no space between `DISTINCT` and `(`

-- this one is not wrong, yet will return a series of tuples
SELECT DISTINCT (film_id, store_id) from inventory;
```
Output:
![alt text](images/distinct_wrong.png)

`"["1","1"]"` means that there is one or more rows where `film_id` is `1` and `store_id` is `1`, the `DISTINCT` command will only return one row, hence `"["1","1"]"`.



#### Sub-queries
- Scalar Sub-queries: Return a single value
- Row Sub-queries: Return a single row
- Table Sub-queries: Return a single table
- Correlated Sub-queries: Refer to columns in the outer query
- Non-correlated Sub-queries: Independent of the outer query

> Using an alias defined in the SELECT clause directly in the WHERE clause will result in an error, because it's not allowed in query. To achieve the same result, use sub-queries.

Example 1: Create a report showing the actors that have been in more films than average
```sql
-- Solution 1: Using sub-queries
select fa.actor_id, concat(a.first_name, ' ', a.last_name), count(distinct film_id) as num_films
from film_actor fa
inner join actor a on a.actor_id = fa.actor_id
group by 1, 2
having count(distinct film_id) > ( 
	select avg(num_films)
	from (
		select actor_id, count(distinct film_id) as num_films
		from film_actor
		group by 1
	) as subquery
)
order by 3 desc
;

-- Solution 2: Using CTE
with 
actor_film_counts as (
	select actor_id, count(distinct film_id) as num_films
	from film_actor
	group by 1
),
average_films as (
	select avg(num_films) as avg_films
	from actor_film_counts
)

select afc.actor_id, concat(a.first_name, ' ', a.last_name), afc.num_films
from actor_film_counts afc
inner join actor a on a.actor_id = afc.actor_id
where num_films > (select avg_films from average_films)
order by 3 desc
;

-- Solution 3: Using Window Functions
select film_counts.actor_id, concat(a.first_name, ' ', a.last_name), film_counts.num_films
from (
	select actor_id, count(distinct film_id) as num_films, avg(count(distinct film_id)) over () as avg_films
	from film_actor
	group by 1
) as film_counts
inner join actor a on a.actor_id = film_counts.actor_id
where film_counts.num_films > avg_films
order by 3 desc
;
```


Example 2: Find the film ids that have more copies in inventory in Store 1 than in Store 2
```sql
select tb.film_id, f.title
from (
	select tb1.film_id, tb1.num_copies as num_copies_1, tb2.num_copies as num_copies_2
	from (
		select film_id, count(1) as num_copies
		from inventory
		where store_id=1
		group by 1
	) tb1
	inner join (
		select film_id, count(1) as num_copies
		from inventory
		where store_id=2
		group by 1
	) tb2 on tb1.film_id = tb2.film_id
) as tb
left join film f on f.film_id = tb.film_id
where tb.num_copies_1 > coalesce(tb.num_copies_2, 0)
;
-- using LEFT JOIN and COALESCE ensures that there are no films that are in Store 2 but not in Store 1
```





#### CASE WHEN

Example: Find the percentage difference in payment amounts from March to April 2007 (method 1):
```sql
select
  sum(case when date_trunc('Month', payment_date) = '2007-03-01' then amount else 0 end) as march_payment,
  sum(case when date_trunc('Month', payment_date) = '2007-04-01' then amount else 0 end) as april_payment,
  ((sum(case when date_trunc('Month', payment_date) = '2007-04-01' then amount else 0 end) - sum(case when date_trunc('Month', payment_date) = '2007-03-01' then amount else 0 end)) / sum(case when date_trunc('Month', payment_date) = '2007-03-01' then amount else 0 end)) * 100 as percentage_difference
from payment;
```

**Tip**
> Use `AVG()` and `CASE WHEN` to find the percentage of a particular item as part of the total:
```sql
select avg(case when rating in ('G', 'PG') then 1.0 else 0.0 end) from film;
-- Create a new column by assigning a numerical value 1.0 for 'G' or 'PG' rating, and 0.0 otherwise. Having the numbers, the SQL can then find the average of 'G' and 'PG' as part of the total. A very smart way to calculate the percentage.
```

> Use `SUM()` and `CASE WHEN` to count the number of a particular items in column:
```sql
select sum(case when rating in ('G', 'PG') then 1 else 0 end) from film;
```





#### CTE (Common Table Expression)
Find the percentage difference in payment amounts from March to April 2007 (method 2):
```sql
with monthly_payments as (
  select
    date_trunc('Month', payment.payment_date) as month_payment,
    sum(payment.amount) as total_payment
  from payment
  group by 1
)
select
  m1.total_payment as march_payment,
  m2.total_payment as april_payment,
  ((m2.total_payment - m1.total_payment) / m1.total_payment) * 100 as percentage_difference
from monthly_payments m1
join monthly_payments m2 on m1.month_payment='2007-03-01' and m2.month_payment='2007-04-01';
```

Method 3, using `CASE WHEN` and `CTE` together
```sql
with monthly_payments as (
  select
    sum(case when date_trunc('Month', payment_date) = '2007-03-01' then amount else 0 end) as march_payment,
    sum(case when date_trunc('Month', payment_date) = '2007-04-01' then amount else 0 end) as april_payment
  from payment
)
select
  march_payment,
  april_payment,
  ((april_payment - march_payment) / march_payment) * 100 as percentage_difference
from monthly_payments;
```



## DML (Data Manipulation Language)

### INSERT



### UPDATE



### DELETE
```sql
delete from staff_backup where staff_id=2;
```



## DDL (Data Definition Language)
- CREATE
- ALTER
- TRUNCATE
- DROP

### CREATE

#### CREATE a new table
```sql
CREATE TABLE film (
    film_id INTEGER PRIMARY KEY DEFAULT nextval('film_film_id_seq'::regclass),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    release_year YEAR,
    language_id SMALLINT NOT NULL,
    rental_duration SMALLINT NOT NULL DEFAULT 3,
    rental_rate NUMERIC(4,2) NOT NULL DEFAULT 4.99,
    length SMALLINT,
    replacement_cost NUMERIC(5,2) NOT NULL DEFAULT 19.99,
    rating MPAA_RATING DEFAULT 'G'::MPAA_RATING,
    last_update TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT now(),
    special_features TEXT[],
    fulltext TSVECTOR NOT NULL,
    CONSTRAINT fk_language_id FOREIGN KEY (language_id) REFERENCES language(language_id) ON UPDATE CASCADE ON DELETE RESTRICT
);
```

#### CREATE a new table from an existing table - Duplicate an existing table
```sql
CREATE table staff_backup as 
SELECT * FROM staff;

-- this means create a new blank table `staff_backup` then take everything from `staff` table and put it into `staff_backup`
```



#### CREATE a new database
```sql
psql -U my_postgres -d postgres -c "CREATE DATABASE dvdrental OWNER my_postgres;"
```



#### RESTORE a database from a backup file

```sql
pg_restore -U my_postgres -d dvdrental --no-owner /var/lib/postgresql/data/dvdrental.tar
```

> NOTE: Why do we need to specify `--no-owner` in the command?
This is what the owner looks like:
```plaintext
root@37eab2935dd1:/var/lib/postgresql/data# ls -al
total 2908
drwx------ 19 postgres postgres    4096 Aug  7 16:32 .
drwxr-xr-x  1 postgres postgres    4096 Jul 24 01:25 ..
drwx------  7 postgres postgres    4096 Aug  7 15:02 base
-rw-r--r--  1      501 dialout  2835456 Aug  7 15:02 dvdrental.tar
drwx------  2 postgres postgres    4096 Aug  8 01:18 global
drwx------  2 postgres postgres    4096 Aug  7 14:55 pg_commit_ts
```

The database is running in a docker container. The dvdrental.tar file was sent from the host to the container, hence having the owner of `501` and group of `dialout`.
To avoid possible conflicts when restoring the database, we need to specify `--no-owner` in the command. `--no-owner` ignores the ownership of database objects.



### ALTER



### TRUNCATE



### DROP

### Drop all tables from a database
```sql
-- PostgreSQL
psql -U my_postgres -d dvdrental -c "DO \$\$ DECLARE r RECORD; BEGIN FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP EXECUTE 'DROP TABLE IF EXISTS public.' || r.tablename || ' CASCADE'; END LOOP; END \$\$;"
```

### DROP the `dvdrental` database
1. Terminate connections to the database
```sql
psql -U my_postgres -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'dvdrental';"
```

> NOTE: the database name `-d postgres` has to be specified, otherwise the system will try to look for the same database name as that of the username (`my_postgres` in this case), which will result in a database not found error, since there is no `my_postgres` database.


2. Drop the database
```sql
psql -U my_postgres -d postgres -c "DROP DATABASE dvdrental;"
```



## DCL (Data Control Language)



## TCL (Transaction Control Language)





# SQL Clauses

## WHERE
used for filtering
```sql
select * from public.actor where first_name = 'Boom Boom';
```



## AND / OR
used to combine multiple conditions
```sql
select * from public.actor where first_name = 'Boom Boom' and `size` = 'E';
```

It's strongly suggested to use parenthesis to group multiple conditions
```sql
select * from film
where (rating = 'PG' OR rating = 'G') AND rental_rate <= 3.99;
```



## IN
```sql
select * from film
where rating in ('PG', 'G') AND rental_rate <= 3.99;
```



## BETWEEN ... AND
```sql
select * from film
where rating in ('PG', 'G') AND rental_rate between 2.99 and 3.99; -- between 2.99 and 3.99 means "greater than or equal to 2.99 and less than or equal to 3.99"
```



## LIKE
find fuzzy matches
```sql
select * from film where description like '%Drama%';
```



## ORDER BY
used to sort
```sql
select * from rental order by rental_date;
```



## GROUP BY
```sql
select customer_id, sum(amount) total_paid_by_customer
from payment
group by 1  -- this is the same as `group by customer_id`
order by 2; -- this is the same as `order by total_paid_by_customer`
```



## HAVING
```sql
select sum(amount), date(payment_date)
from payment
group by 2
having sum(amount) > 300;
```

NOTE: do not use `number` in the `having` clause



## JOIN
Three scenarios:
- Join criteria is not met
- Join criteria is met once
- Join criteria is met more than once


> **⚠️** JOINING ISSUEs:

Assumed that:
- Table A has two duplicated rows
- Table B also has two duplicated rows (and the values are same as those in Table A) 

<span style="color:red">**⚠️** What happens if we try to join these two tables? </span>

There will be <span style="color:red">four duplicated rows </span> in the joined table!!!

> If `n` rows from one table match with `m` rows in another table, the joining result is `n*m` rows. It's multiplicative.

### JOIN or INNER JOIN
Compared to VLOOKUP in spreadsheet:
INNER JOIN is used in databases to combine data from two or more tables based on a shared key, while VLOOKUP is a function in spreadsheets used to search for a value in a specified column and return a corresponding value from a different column.

`join` or `inner join` only returns rows that have matching values in both tables, i.e., the criteria is met.

#### Multiple INNER JOIN
```sql
select c.name, tb2.number_of_films
from category c
inner join (
	select tb.category_id, count(distinct row(film_id, rating)) as number_of_films
	from (
		select fc.category_id, f.film_id, f.rating
		from film_category fc
		inner join film f on fc.film_id = f.film_id
		where f.rating = 'G'
	) tb
	group by 1
) tb2 on c.category_id=tb2.category_id
order by 2 desc;
```

This can be shortened to:

```sql
select c.name, count(distinct f.film_id)
from film f
inner join film_category fc on f.film_id = fc.film_id
inner join category c on fc.category_id = c.category_id
where f.rating = 'G'
group by 1
order by 2 desc;
```



### OUTER JOIN

#### LEFT JOIN
```sql
select rental_id, customer_id, rental.staff_id, concat(first_name, ' ', last_name) as staff_name
from rental
left join staff_backup on rental.staff_id = staff_backup.staff_id;
```



#### RIGHT JOIN



#### FULL OUTER JOIN



#### CROSS JOIN



#### UNION 
To use `UNION`, each table must have the same number of columns and data types (columns can be different, but data types must be the same).

`UNION` will remove duplicated rows and show only unique ones.

> NOTE: NULL can be compatible with other data types.

```sql
select rental_id, customer_id, rental_date from rental_1158_1159
union
select rental_id, null as null_val, rental_date from rental_1158_1160;

-- This will also work
```



#### UNION ALL
Like `UNION`, to use `UNION ALL`, each table must have the same number of columns and data types (columns can be different, but data types must be the same).

Unlike `UNION`, `UNION ALL` will show duplicated rows




# SQL Functions

## Aggregate Functions

### COUNT()
return the number of rows
```sql
select count(*) from public.actor;

-- or
select count(1) from public.actor;
```

> `COUNT(*) ... AS distinct_rows` return distinct rows, taking all columns into account

```sql
select count(*)
from (
  select f.film_id, f.title, f.rating, count(fa.actor_id)
  from film f
  inner join film_actor fa on f.film_id = fa.film_id
  where f.rating = 'PG'
  group by f.film_id, f.title, f.rating
) as distinct_rows;
```



### SUM()



### AVG()



### MIN()



### MAX()



### GROUP_CONCAT() (or STRING_AGG())


## Date Functions

- Use `between ... and ...` to filter dates
```sql
select * from rental where rental_date between '2005-05-24' and '2005-05-25';
```

- Use comparison operators
```sql
select * from rental where rental_date > '2005-05-24';
```

remember the date format is: `YYYY-MM-DD`


### DATE()
```sql
select rental_date rental_datetime, date(rental_date) rental_date from rental;
```



### EXTRACT()
```sql
select rental_date rental_datetime, extract('Year' from rental_date) rental_year from rental;
-- Note: 'Year' or year is fine

select distinct extract(year from rental_date) from rental;

select distinct extract(month from rental_date) from rental;
```

We can extract 'Year', 'Month', 'Quarter', 'Week', 'Day', 'Hour', 'Minute', 'Second' from a date using `extract` function.



### Calculated Date Field
```sql
select rental_date, return_date, return_date - rental_date rental_period from rental;

select rental_date, return_date, extract(day from return_date - rental_date) rental_period_as_days from rental;
```



### DATE_TRUNC()
get the 1st day of the week, month, quarter, or year
```sql
select rental_date, date_trunc('Quarter', rental_date) rental_quarter from rental;
```

```sql
select date(date_trunc('Month', payment_date)) as month_payment, sum(amount)
from payment
group by month_payment
order by sum(amount) desc;
```

OUTPUT:
![alt text](images/sum_of_payment_by_month.png)



### CURRENT_DATE
a keyword to return the current date





## String Functions

### CONCAT()
```sql
select concat(first_name, ' ', last_name) from actor;
-- or
select first_name || ' ' || last_name from actor; -- this should belong to Operators section

create table staff_duplicate AS
select staff_id, concat(first_name, ' ', last_name) as staff_name
from staff

union all

select staff_id, concat(first_name, ' ', last_name) as staff_name
from staff
where staff_id=2
;
```



### SUBSTRING() or SUBSTR()
```sql
select title, substr(title, 2, 3) from film;
```



### UPPER() and LOWER()
```sql
select title, upper(title) from film;
select title, lower(split_part(title, ' ', 2)) from film;
```



### LEFT() and RIGHT()
```sql
select title, right(title, 2) from film;
```



### SPLIT_PART()
```sql
select title, split_part(title, ' ', 2) from film;
```


## Numeric Functions



## Conversion Functions

### CAST()
```sql
-- change the data type from integer to float or real 
select cast(count(*) as decimal) / (select count(*) from film) as proportion_g_pg
from film
where rating in ('PG', 'G');
```

### Convert an integer to a decimal number by multiplying `1.0`
```sql
select count(*) * 1.0
from film
where rating in ('G', 'PG')
;
```



## Conditional Functions

### COALESCE()
Take a lists of values and return the first non-null value.

```sql
select coalesce(address2, district), address2, district from address;
-- If the address2 is null, it will take the district. It will check like this line by line to form the `coalesce` column.

select coalesce(address2, 'unknown') from address;
-- If the address2 is null, it will take the `unknown` value.
```

> NOTE: In SQL, `null` and `blank` are different. `null` is a special value in SQL.



## Mathematical Functions



## Window Functions
Window functions in SQL are indeed powerful tools that allow  calculations across a set of table rows that are related to the current row. Unlike aggregate functions, which return a single value for a group of rows, window functions can return a value for each row in the result set, allowing us to see how the row relates to the entire set.

In simpler terms:
- Window functions operate on a “window” or subset of rows and produce results that are attached to each row in that window.
- They enable calculations like `running totals`, `ranking`, or `moving averages` that are based on the window of data for each row.

The OVER clause is used to defines the window or set of rows over which the function operates.

### Use Case 1: Aggregation with OVER (Calculating Average)
```sql
select actor_id
, count(distinct film_id) as film_counts
, avg(count(distinct film_id)) over () as avg_films
from film_actor
group by 1
;
```
**Explanation:**

- Purpose: This query calculates the number of distinct films each actor has appeared in (film_counts) and the average number of distinct films across all actors (avg_films).
- Window Function: avg(count(distinct film_id)) over () is a window function. The OVER () clause without any PARTITION BY or ORDER BY specifies that the average should be calculated over the entire result set.
- Behavior:
- count(distinct film_id) is aggregated per actor_id due to the GROUP BY.
- The avg() window function calculates the average of the film_counts for all actors, and this average is then repeated for each actor in the result.

**Key Points:**

- Global Context: The avg() calculation considers the entire dataset (OVER () means no specific partitioning).
- Repeated Values: The same average value (avg_films) is repeated for every row in the result.




### Use Case 2: Row Numbering with OVER (Partitioning Rows)
```sql
select row_number() over (partition by customer_id order by rental_id) as row_num, a.*
from rental a
;
```

**Explanation:**
- Purpose: This query generates a sequential row number for each row within each customer_id partition in the rental table.
- Window Function: row_number() over (partition by customer_id order by rental_id) is a window function that assigns a unique row number to each row order by rental_id within its customer_id group.
- Behavior:
- Partitioning: The PARTITION BY customer_id clause divides the result set into partitions based on customer_id. Within each partition, rows are numbered starting from 1.
- Ordering: With an ORDER BY clause, the order in which rows are numbered within each partition is guaranteed. In this case, it orders by rental_id of the dataset.

**Key Points:**
- Partitioned Context: The row numbers are calculated independently within each partition (customer_id).
- Unique Row Numbers: Each row within the same customer_id partition gets a unique number starting from 1, incremented by 1 for each subsequent row.


Summary of Differences:

1. Context:
- Use Case 1: The calculation (`avg()`) is applied globally across the entire result set.
- Use Case 2: The calculation (`row_number()`) is applied within partitions (groups of `customer_id`).
2. Function Type:
- Use Case 1: The window function is performing an `aggregate operation over the window`.
- Use Case 2: The window function is performing a `ranking operation within the partition`.
3. Repetition vs. Uniqueness:
- Use Case 1: The result of the window function (`avg()`) is the same for each row in the result set.
- Use Case 2: The result of the window function (`row_number()`) is unique for each row within a partition.

Window functions like these are incredibly versatile and can be used for a wide range of analytical tasks in SQL, from ranking rows to computing moving averages, cumulative sums, and much more.





### Other examples

Count over partitions by customer_id:
```sql
select count(1) over (partition by customer_id), a.*
from rental a
;
```
This method keeps all details of each row in the result with an extra `count` column:
![alt text](images/count_over_partition.png)

To find the number of rows where `customer_id = 1`, we can also use `group by`:
```sql
select customer_id, count(1)
from rental
group by 1
```
This method gets rid of all other columns in the output except the `group by` column:
![alt text](images/group_by_compare_to_over.png)

We can even perform more complex operations on `partition` like using multiple columns:
```sql
select count(1) over (partition by customer_id, staff_id), a.*
from rental a
;
```





## System Functions





# Other SQL Concepts

## Operators





### Arithmetic Operators
`+`, `-`, `*`, `/`, `**`, `%`

```sql
select film_id, title, round(rental_rate / rental_duration, 2) as rental_rate_per_day
from film; 
```



### Comparison Operators
`=`, `!=` or `<>`, `>`, `<`, `>=`, `<=`



### Logical Operators
`AND`, `OR`, `NOT`



### String Operators
`||` (or `+` in some databases for concatenation)



## Indexes
Create indexes to improve the performance of queries:
```sql
CREATE INDEX film_fulltext_idx ON film USING GIST (fulltext);
CREATE INDEX idx_fk_language_id ON film (language_id);
CREATE INDEX idx_title ON film (title);
```



## Constraints
- PRIMARY KEY: Uniquely identifies records
- FOREIGN KEY: Ensures referential integrity
- UNIQUE: Ensures all values are unique
- NOT NULL: Ensures a column cannot have NULL values
- CHECK: Ensures values meet a condition



## Views
`CREATE VIEW`: Create a virtual table based on a query



## Stored Procedures and Functions
- Stored Procedures: Precompiled SQL code that can be executed as a unit
- User-Defined Functions: Custom functions created by users



## Triggers
`CREATE TRIGGER`: Automatically perform actions in response to events

```sql
CREATE TRIGGER film_fulltext_trigger
    BEFORE INSERT OR UPDATE ON film
    FOR EACH ROW
    EXECUTE FUNCTION tsvector_update_trigger('fulltext', 'pg_catalog.english', 'title', 'description');

CREATE TRIGGER last_updated
    BEFORE UPDATE ON film
    FOR EACH ROW
    EXECUTE FUNCTION last_updated();
```



## Transactions
- `BEGIN TRANSACTION`: Start a transaction
- `COMMIT`: Commit changes
- `ROLLBACK`: Undo changes





# Testing SQL

## Accidental Duplication

```sql
-- let's create a table with deliberate duplications
create customer_with_dups as 
select * 
from customer 
UNION ALL
select * from customer
where customer_id in (1, 2, 3)
;

select count(1)
from (
  select r.*, cwd.*
  from rental r
  inner join customer_with_dups cwd on r.customer_id = cwd.customer_id
); -- 16151 rows

select count(1) from rental; -- 16044 rows only
```

Because the customer_with_dups table has duplications, the join will also result in duplications. 

To fix this, we can use `row_number()` in the Window Function to filter out duplicates. 

How does `row_number()` work with Window Function?

Let's check with `customer_id=2` using `row_number()` and Window Function: 
```sql
select row_number() over (partition by rental_id) as rn, r.*, cwd.*
from rental r
inner join customer_with_dups cwd on r.customer_id = cwd.customer_id
where customer_id = 2
;
```

Output:
![alt text](images/duplications.png)
we see that the rn column has {1; 2} rows repeatedly which shows duplications. We are only interested in the first row (rn=1)

```sql
select * 
from (
  select row_number() over (partition by rental_id) rn, r.*, cwd.*
  from rental a
  inner join customer_with_dups cwd on r.customer_id = cwd.customer_id
) tb
where rn = 1
;  -- 16044 rows
```

Now the duplicated rows have been filtered out.


## Missing Data

If we are not sure a table has missing values, use `LEFT JOIN` or `RIGHT JOIN`. Example we are not sure if `customer_with_missing` tables has missing data:

```sql
select sum(total)
from (
	select first_name, last_name, sum(amount) as total
	from payment p
	left join customer_with_missing cwm on p.customer_id = cwm.customer_id
	group by 1, 2
	order by 1
)
;

-- The sum amount will be exactly the same as:
select sum(total)
from (
	select first_name, last_name, sum(amount) as total
	from payment p
	inner join customer c on p.customer_id = c.customer_id
	group by 1, 2
	order by 1
)
;
```





# SQL Service INSTALLATION

## PostgreSQL

### Create docker containers for `postgres` and `pgadmin4` services using docker compose
Docker compose file: `docker-compose.yml`
```yml
version: '3.8'

services:
  postgres:
    image: postgres:latest
    restart: always
    environment:
      POSTGRES_USER: my_postgres
      POSTGRES_PASSWORD: MyLocalPostgresPassword
      POSTGRES_DB: my_local_postgres
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  pgadmin:
    image: dpage/pgadmin4
    restart: always
    environment:
      PGADMIN_DEFAULT_EMAIL: <email_address>
      PGADMIN_DEFAULT_PASSWORD: <pgadmin4_password>
    ports:
      - "8081:80"
    depends_on:
      - postgres

volumes:
  postgres_data:
```



### Use the `pgadmin` service to connect to the `postgres` service
In the browser, go to `http://localhost:8081`

Login with `<email_address>` and `<pgadmin4_password>`

Click on “Add New Server” (in the home interface)

Fill in teh details:
- Name: PostgreSQL
- Connection:
    - Host name/address: postgres
    - Port: 5432
    - Maintenance database: my_local_postgres
    - Username: my_postgres
    - Password: MyLocalPostgresPassword




### PostgreSQL error
After restoring the database using the interface and checking for the database in the docker container, we get the following error:

![alt text](images/db_not_exist_error.png)



## Administrative Commands (DBMS-Specific)

> DBMS stands for Database Management System.

### PostgreSQL (psql commands):
- `\l`: List all databases 
- `\c` dvdrental: Connect to a database called `dvdrental`
- `\dt`: List all tables in the database
- `\d` film: Describe a table in the database called `film`
- `\du`: List all users
- `\q`: Quit



### MySQL (mysql commands):
- `SHOW DATABASES`: List all databases
- `USE dvdrental`: Connect to a database called `dvdrental`
- `SHOW TABLES`: List all tables in the database
- `DESCRIBE film`: Describe a table in the database called `film`
- `SHOW GRANTS`: List all users
- `EXIT`: Quit





# Other

> **💡** PostgreSQL doesn't recognize the backtick (`). To handle identifiers that include spaces, special characters, or are case-sensitive, use double quotes (") instead.





# Hierarchical Structure of Databases

## Types of Databases

### Relational Database Management System (RDBMS)
1. SQL Variants
- MySQL
- PostgreSQL
- Oracle SQL (PL/SQL)
- Microsoft SQL Server (T-SQL)
- IBM Db2 SQL
- SQLite
- MariaDB
- PL/pgSQL (PostgreSQL)
- PL/SQL (Sybase)
- SAP HANA SQL
- Teradata SQL

2. Characteristics
- Data is stored in `tables` (rows and columns)
- Strong `ACID compliance`
- `SQL` is the primary query language


### NoSQL Databases
1. `Types` of NoSQL Databases
- `Key-value` Stores: ex, `Redis`, `Amazon DynamoDB`
- `Document` Stores: ex, `MongoDB`, `CouchDB`
- `Columnar` Databases: ex, `Apache Cassandra`, `HBase`
- `Graph` Databases: ex, `Neo4j`, `Amazon Neptune`

2. Characteristics
- Designed for `specific use cases` (e.g., high scalability, unstructured data)
- Data models vary (e.g., key-value pairs, documents, wide-column)
- No fixed schema, typically schema-less


## Database Architectures

### Cloud Databases
1. Characteristics
- Managed by cloud service providers (e.g., `AWS`, `Azure`, `Google Cloud`)
- Examples: `Amazon RDS` (`Relational`), `Google BigQuery` (`Data Warehousing`), `Amazon DynamoDB` (`NoSQL`), Teradata Cloud

2. Advantages
- Scalability, automatic backups, and high availability
- Pay-as-you-go pricing model

### In-Memory Databases
1. Characteristics
- Data is stored in memory (RAM) rather than disk
- Examples: `Redis`, `SAP HANA`

2. Advantages
- Extremely fast read/write operations
- Suitable for real-time analytics and caching

### Columnar Databases
1. Characteristics
- Data is stored in columns instead of rows
- Optimized for read-heavy operations and analytical queries
- Examples: `Apache Cassandra` (`NoSQL`), Amazon Redshift (`Data Warehousing`), `Teradata` (`RDBMS`/`Columnar`)

2. Advantages
- Efficient for querying large datasets
- Reduces the amount of data read from disk


## Data Warehousing

### Characteristics
1. Purpose
- Designed for `reporting` and `data analysis`
- Stores large volumes of historical data from various sources

2. Architecture
- Often uses columnar storage (e.g., `Amazon Redshift`, `Google BigQuery`)
- Can be `cloud-based` or `on-premises`

3. Examples
- Amazon Redshift (Cloud Columnar DB, SQL-based)
- Google BigQuery (Cloud Columnar DB, SQL-based)
- Snowflake (Cloud Data Warehouse)
- Teradata (On-premises or Cloud Data Warehouse, SQL-based)
- Apache Hive (SQL-Like Query Language for Hadoop-based Data Warehousing)


## Summary of Relationships

- RMDBMS and NoSQL are the two main types of databases, each with specific characteristics and use cases.
- SQL Variants are specific to RDBMS, while NoSQL Databases are diverse and tailored to different data models (e.g., key-value, document, columnar)
- Database Architectures refer to how databases are implemented and deployed (e.g., Cloud, In-Memory, Columnar)
- Data Warehousing is a specific use case often associated with columnar databases and can be implemented on various architectures, especially in the cloud

## Visual Example of Hierarchy and Relationships
1. Database Types
- Relational (RDBMS)
  - SQL Variants
  - ACID Compliance
- NoSQL
  - Key-Value, Document, Columnar, Graph
  - Schema-less

2. Database Architectures
- Cloud (Can be RDBMS, NoSQL, or Data Warehousing)
- In-Memory (RDBMS, NoSQL)
- Columnar (RDBMS, NoSQL, Data Warehousing)

3. Data Warehousing
- Cloud-based Columnar Databases
- SQL-based for analysis


## Teradata and Apache Hive in Context
- Teradata: An `RDBMS` optimized for `data warehousing`, often using a `columnar architecture`, available `both on-premises and in the cloud`.

- Apache Hive: A `data warehousing` solution that uses a SQL-like query language, designed for querying and managing large datasets `stored in a Hadoop-based distributed storage system`.
> Hadoop is an open source framework based on Java that manages the storage and processing of large amounts of data for applications.