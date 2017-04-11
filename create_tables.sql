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
    id serial PRIMARY KEY,
	denomination varchar(20),
	observation varchar(30)
	);
CREATE TABLE malles(
	reference varchar(6) NOT NULL PRIMARY KEY,
	type_id integer,
    observation varchar(300),
	FOREIGN KEY (type_id) REFERENCES malles_types(id)
	);
CREATE TABLE reservations_malles_rel(
	reservation_id integer,
	malle_ref varchar(6) REFERENCES malles(reference)
	);
CREATE TABLE fournisseurs(
	id serial PRIMARY KEY,
	nom varchar(30) NOT NULL,
	email varchar(30),
	phone varchar(14),
	observation varchar(300),
    UNIQUE(nom)
	);
CREATE TABLE produits(
	id serial PRIMARY KEY,
	nom varchar(30) NOT NULL,
    UNIQUE(nom)
	);
CREATE TABLE etats(
    id serial PRIMARY KEY,
    etat varchar(100)
    );
CREATE TABLE contenu_malles(
	malle_ref varchar(6) NOT NULL,
	produit_id integer NOT NULL,
    quantity integer NOT NULL,
    etat_id integer NOT NULL,
	PRIMARY KEY (produit_id, malle_ref),
	FOREIGN KEY (produit_id) REFERENCES produits(id),
	FOREIGN KEY (malle_ref) REFERENCES malles(reference),
	FOREIGN KEY (etat_id) REFERENCES etats(id)
	);
CREATE TABLE contenu_type(
	type_id integer,
	produit_id integer,
	quantity integer,
	FOREIGN KEY (type_id) REFERENCES malles_types(id),
	FOREIGN KEY (produit_id) REFERENCES produits(id)
	);
CREATE TABLE commandes(
	id serial PRIMARY KEY,
	fournisseur_id integer NOT NULL,
	produit_id integer NOT NULL,
    commande_number varchar(50),
	prix real,
	FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id),
	FOREIGN KEY (produit_id) REFERENCES produits(id)
	);

-- Relationnal tables
CREATE TABLE inputs(
	id serial PRIMARY KEY,
	fournisseur_id integer,
	produit_id integer NOT NULL,
    date_achat date NOT NULL,
	price real,
	FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id),
	FOREIGN KEY (produit_id) REFERENCES produits(id)
	);
CREATE TABLE sejours_malles_types_rel(
	id serial PRIMARY KEY,
	sejour_id integer NOT NULL,
	malle_type_id integer NOT NULL,
	FOREIGN KEY (sejour_id) REFERENCES sejours(id),
	FOREIGN KEY (malle_type_id) REFERENCES malles_types(id)
	);

