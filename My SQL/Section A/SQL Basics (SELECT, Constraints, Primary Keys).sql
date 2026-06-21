-- Section A — SQL Basics (SELECT, Constraints, Primary Keys)

#Q1. Write a query to display all columns and rows from the customer's table. 
SELECT * FROM customers;

#Q2. Retrieve only the first_name, last_name, and city of all customers. 
SELECT first_name, last_name, city FROM customers;

#Q3. List all unique categories available in the products table.
SELECT DISTINCT category FROM products;

#Q4. Identify the Primary Key of each table in the schema. Explain why a Primary Key must be unique and NOT NULL. 
/*Answer:-
Table	         Primary Key
customers	     customer_id
products	     product_id
orders	         order_id
order_items    	 item_id

Explanation
A Primary Key:

Uniquely identifies each record.
Cannot contain duplicate values.
Cannot contain NULL. */

#Q5. What constraints are applied to the email column in the customers table? What would happen if you tried to insert a duplicate email? 
/*Column Definition:

email VARCHAR(100) UNIQUE NOT NULL

Constraints Applied:

UNIQUE: Ensures that every customer has a unique email address. Duplicate email values are not allowed.
NOT NULL: Ensures that the email field cannot be left empty (NULL).

Example:

INSERT INTO customers
VALUES (
109,
'Raj',
'Patel',
'aarav.s@email.com',
'Surat',
'Gujarat',
'2024-09-01',
FALSE
);

Expected Result:

The query will fail because the email aarav.s@email.com already exists in the customers table.

Example error:

ERROR 1062 (23000): Duplicate entry 'aarav.s@email.com' for key 'customers.email'

Conclusion:
The UNIQUE constraint prevents duplicate email addresses, while the NOT NULL constraint ensures that every customer must have a valid email address. */

#Q6. Try inserting a product with unit_price = -50. What happens and which constraint prevents it? Write both the INSERT statement and explain the error. 
INSERT INTO products VALUES (209,'Mouse','Electronics','HP',-50,20);

/*Error produced: CHECK constraint violation on unit_price > 0.
The database rejects the row because –50 fails the check. This prevents nonsensical pricing data from entering the system.*/

