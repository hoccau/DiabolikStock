-- File used to create blank database structure --
-- use \i create_table.sql --

CREATE TABLE lieux(
	id serial PRIMARY KEY,
    nom varchar(25),
	ville varchar(25),
	CP integer,
	numero integer,
	rue varchar(30),
    UNIQUE(nom)
	);
CREATE TABLE vehicules(
	immatriculation char(7) PRIMARY KEY,
	model varchar(20),
	nbr_places integer
	);
CREATE TABLE sejours(
	id serial PRIMARY KEY,
	nom varchar(20),
	lieu_id integer,
	directeur varchar(20),
	nbr_enfants integer,
	observation varchar(255),
	FOREIGN KEY (lieu_id) REFERENCES lieux(id)
	);
CREATE TABLE reservations(
	id serial PRIMARY KEY,
	sejour_id integer,
	date_start date,
	date_end date,
	observation varchar(255),
	FOREIGN KEY (sejour_id) REFERENCES sejours(id)
	);
CREATE TABLE malles_types(
    id serial PRIMARY KEY,
	denomination varchar(20),
	observation varchar(255),
    UNIQUE(denomination)
	);
CREATE TABLE malles(
	reference varchar(6) PRIMARY KEY,
	type_id integer,
    observation varchar(1024),
	FOREIGN KEY (type_id) REFERENCES malles_types(id)
	);
INSERT INTO malles(reference, observation) VALUES(
    'VSTOCK', 'Malle virtuelle, contenant le stock disponible. Si un 
    produit est entré, il est automatiquement ajouté à cette malle.');
CREATE TABLE reservations_malles_rel(
	reservation_id integer,
	malle_ref varchar(6) REFERENCES malles(reference)
	);
CREATE TABLE fournisseurs(
	id serial PRIMARY KEY,
	nom varchar(30) NOT NULL,
	email varchar(30),
	phone varchar(14),
	observation varchar(255),
    UNIQUE(nom)
	);
CREATE TABLE produits(
	id serial PRIMARY KEY,
	nom varchar(30) NOT NULL,
	fournisseur_id integer REFERENCES fournisseurs(id),
    UNIQUE(nom)
	);
CREATE TABLE etats(
    id integer PRIMARY KEY,
    etat varchar(100)
    );
INSERT INTO etats(id, etat) VALUES(1, 'neuf');
INSERT INTO etats(id, etat) VALUES(2, 'bon');
INSERT INTO etats(id, etat) VALUES(3, 'mauvais');
INSERT INTO etats(id, etat) VALUES(4, 'HS');

CREATE TABLE contenu_malles(
    id serial PRIMARY KEY,
	malle_ref varchar(6) NOT NULL,
	produit_id integer NOT NULL,
    quantity integer NOT NULL DEFAULT 0,
    etat_id integer,
	UNIQUE (produit_id, malle_ref),
	FOREIGN KEY (produit_id) REFERENCES produits(id),
	FOREIGN KEY (malle_ref) REFERENCES malles(reference),
	FOREIGN KEY (etat_id) REFERENCES etats(id)
	);
CREATE TABLE contenu_type(
	type_id integer,
	produit_id integer,
	quantity integer,
	FOREIGN KEY (type_id) REFERENCES malles_types(id),
	FOREIGN KEY (produit_id) REFERENCES produits(id),
    PRIMARY KEY (type_id, produit_id)
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

CREATE TABLE inputs(
	id serial PRIMARY KEY,
	fournisseur_id integer,
	produit_id integer NOT NULL,
    date_achat date NOT NULL,
	price real,
    quantity integer NOT NULL,
	FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id),
	FOREIGN KEY (produit_id) REFERENCES produits(id)
	);
CREATE TABLE sejours_malles_types_rel(
	sejour_id integer,
	malle_type_id integer,
	FOREIGN KEY (sejour_id) REFERENCES sejours(id),
	FOREIGN KEY (malle_type_id) REFERENCES malles_types(id),
    PRIMARY KEY (sejour_id, malle_type_id)
	);

CREATE VIEW contenu_check AS 
	SELECT produits.nom, 
	contenu_malles.quantity AS reel, 
	contenu_type.quantity AS attendu, 
	contenu_type.quantity - contenu_malles.quantity as difference,
	malle_ref,
    etats.etat
	FROM contenu_malles
    LEFT JOIN etats ON etats.id = contenu_malles.etat_id
	LEFT JOIN contenu_type ON contenu_malles.produit_id = contenu_type.produit_id
	LEFT JOIN malles ON malles.reference = contenu_malles.malle_ref
	INNER JOIN produits ON produits.id = contenu_malles.produit_id
	WHERE malles.type_id = contenu_type.type_id

