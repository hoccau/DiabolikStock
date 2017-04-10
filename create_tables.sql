-- File used to create blank database structure --

CREATE TABLE lieux(
	id serial PRIMARY KEY ,
	ville varchar(25),
	CP integer,
	numero integer,
	rue varchar(30)
	);
CREATE TABLE vehicules(
	immatriculation char(7) NOT NULL PRIMARY KEY,
	model varchar(20),
	nbr_places integer
	);
CREATE TABLE sejours(
	id serial PRIMARY KEY,
	nom varchar(20),
	lieu_id integer,
	directeur varchar(20),
	nbr_enfants integer,
	observation varchar(100),
	FOREIGN KEY (lieu_id) REFERENCES lieux(id)
	);
CREATE TABLE reservations(
	id serial PRIMARY KEY,
	sejour_id integer,
	date_start date,
	date_end date,
	observation varchar(30),
	FOREIGN KEY (sejour_id) REFERENCES sejours(id)
	);
CREATE TABLE malles_types(
	reference varchar(6) NOT NULL PRIMARY KEY,
	denomination varchar(20),
	d_height real,
	d_width real,
	d_depth real,
	observation varchar(30)
	);
CREATE TABLE malles(
	id serial PRIMARY KEY,
	type_ref varchar(6),
	FOREIGN KEY (type_ref) REFERENCES malles_types(reference)
	);
CREATE TABLE reservations_malles_rel(
	reservation_id integer,
	malle_id integer REFERENCES malles(id)
	);
CREATE TABLE fournisseurs(
	id serial PRIMARY KEY,
	nom varchar(30) NOT NULL,
	email varchar(30),
	phone varchar(14),
	observation varchar(300),
    UNIQUE(nom)
	);
CREATE TABLE objets(
	id serial PRIMARY KEY,
	nom varchar(30),
	price real,
	etat varchar(40),
	quantity integer
	);
CREATE TABLE contenu_malles(
	object_id integer NOT NULL,
	malle_id integer NOT NULL,
	PRIMARY KEY (object_id, malle_id),
	FOREIGN KEY (object_id) REFERENCES objets(id),
	FOREIGN KEY (malle_id) REFERENCES malles(id)
	);
CREATE TABLE contenu_type(
	type_ref varchar(6),
	objet_id integer,
	quantity integer,
	FOREIGN KEY (type_ref) REFERENCES malles_types(reference),
	FOREIGN KEY (objet_id) REFERENCES objets(id)
	);
CREATE TABLE commandes(
	id serial PRIMARY KEY,
	fournisseur_id integer NOT NULL,
	produit_id integer NOT NULL,
	prix real,
	FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id),
	FOREIGN KEY (produit_id) REFERENCES objets(id)
	);

-- Relationnal tables
CREATE TABLE fournisseurs_produits_rel(
	id serial PRIMARY KEY,
	fournisseur_id integer,
	objet_id integer,
	current_price real,
	reference varchar(20),
	FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id),
	FOREIGN KEY (objet_id) REFERENCES objets(id)
	);
CREATE TABLE sejours_malles_types_rel(
	id serial PRIMARY KEY,
	sejour_id integer NOT NULL,
	malle_ref varchar(6) NOT NULL,
	FOREIGN KEY (sejour_id) REFERENCES sejours(id),
	FOREIGN KEY (malle_ref) REFERENCES malles_types(reference)
	);

