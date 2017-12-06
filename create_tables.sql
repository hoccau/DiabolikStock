-- File used to create blank database structure --
-- use \i create_table.sql --

CREATE TABLE IF NOT EXISTS lieux(
	id serial PRIMARY KEY,
    nom varchar(25),
	ville varchar(25),
	CP integer,
	numero integer,
	rue varchar(30),
    UNIQUE(nom)
	);
CREATE TABLE IF NOT EXISTS vehicules(
	immatriculation char(7) PRIMARY KEY,
	model varchar(20),
	nbr_places integer
	);
CREATE TABLE IF NOT EXISTS sejours(
	id serial PRIMARY KEY,
	nom varchar(20),
	lieu_id integer,
	directeur varchar(20),
	nbr_enfants integer,
	observation varchar(255),
	FOREIGN KEY (lieu_id) REFERENCES lieux(id)
	);
CREATE TABLE IF NOT EXISTS reservations(
	id serial PRIMARY KEY,
	sejour_id integer,
	date_start date,
	date_end date,
	observation varchar(255),
	FOREIGN KEY (sejour_id) REFERENCES sejours(id)
	);
CREATE TABLE IF NOT EXISTS malles_types(
    id serial PRIMARY KEY,
	denomination varchar(20),
	observation varchar(255),
    UNIQUE(denomination)
	);
CREATE TABLE IF NOT EXISTS malles(
	reference varchar(6) PRIMARY KEY,
	type_id integer,
    lieu_id integer, 
    section varchar(20),
    shelf varchar(20),
    slot varchar(20),
    observation varchar(1024),
	FOREIGN KEY (type_id) REFERENCES malles_types(id),
    FOREIGN KEY (lieu_id) REFERENCES lieux(id)
	);

INSERT INTO malles(reference, observation) VALUES(
    'VSTOCK', 'Malle virtuelle, contenant le stock disponible. Si un 
    produit est entré, il est automatiquement ajouté à cette malle.');
CREATE TABLE IF NOT EXISTS reservations_malles_rel(
	reservation_id integer,
	malle_ref varchar(6) REFERENCES malles(reference)
	);
CREATE TABLE IF NOT EXISTS fournisseurs(
	id serial PRIMARY KEY,
	nom varchar(30) NOT NULL,
	email varchar(30),
	phone varchar(14),
	observation varchar(255),
    UNIQUE(nom)
	);
CREATE TABLE IF NOT EXISTS produits(
	id serial PRIMARY KEY,
	nom varchar(30) NOT NULL,
	fournisseur_id integer REFERENCES fournisseurs(id),
    UNIQUE(nom)
	);
CREATE TABLE IF NOT EXISTS produits_fournisseur_rel(
    id serial PRIMARY KEY,
    fournisseur_id integer REFERENCES fournisseurs(id),
    produit_id integer REFERENCES produits(id),
    reference varchar(30),
    UNIQUE (fournisseur_id, produit_id)
    );
CREATE TABLE IF NOT EXISTS etats(
    id integer PRIMARY KEY,
    etat varchar(100)
    );
INSERT INTO etats(id, etat) VALUES(1, 'neuf');
INSERT INTO etats(id, etat) VALUES(2, 'bon');
INSERT INTO etats(id, etat) VALUES(3, 'mauvais');
INSERT INTO etats(id, etat) VALUES(4, 'HS');

CREATE TABLE IF NOT EXISTS contenu_type(
    id serial PRIMARY KEY,
	type_id integer,
	produit_id integer,
	quantity integer,
	FOREIGN KEY (type_id) REFERENCES malles_types(id) ON DELETE CASCADE,
	FOREIGN KEY (produit_id) REFERENCES produits(id),
    UNIQUE (type_id, produit_id)
	);
CREATE TABLE IF NOT EXISTS contenu_malles(
    id serial PRIMARY KEY,
	malle_ref varchar(6) NOT NULL,
	contenu_type_id integer NOT NULL,
    quantity integer NOT NULL DEFAULT 0,
    etat_id integer,
    observation varchar(255),
	UNIQUE (contenu_type_id, malle_ref),
	FOREIGN KEY (contenu_type_id) REFERENCES contenu_type(id) ON DELETE CASCADE,
	FOREIGN KEY (malle_ref) REFERENCES malles(reference) ON DELETE CASCADE,
	FOREIGN KEY (etat_id) REFERENCES etats(id)
	);
CREATE TABLE IF NOT EXISTS commandes(
	id serial PRIMARY KEY,
	fournisseur_id integer NOT NULL,
	produit_id integer NOT NULL,
    commande_number varchar(50),
	prix real,
	FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id),
	FOREIGN KEY (produit_id) REFERENCES produits(id)
	);

CREATE TABLE IF NOT EXISTS inputs(
	id serial PRIMARY KEY,
	fournisseur_id integer,
	produit_id integer NOT NULL,
    date_achat date NOT NULL,
	price real,
    quantity integer NOT NULL,
	FOREIGN KEY (fournisseur_id) REFERENCES fournisseurs(id),
	FOREIGN KEY (produit_id) REFERENCES produits(id)
	);
CREATE TABLE IF NOT EXISTS sejours_malles_types_rel(
	sejour_id integer,
	malle_type_id integer,
	FOREIGN KEY (sejour_id) REFERENCES sejours(id),
	FOREIGN KEY (malle_type_id) REFERENCES malles_types(id),
    PRIMARY KEY (sejour_id, malle_type_id)
	);

CREATE TABLE IF NOT EXISTS users(
    id serial PRIMARY KEY,
    name varchar(32) NOT NULL,
    email varchar(32),
    password_salt varchar(32) NOT NULL,
    password_hash varchar(128) NOT NULL,
    UNIQUE(name)
    );

CREATE TABLE IF NOT EXISTS groups(
    id serial PRIMARY KEY,
    name varchar(16) NOT NULL,
    UNIQUE(name)
    );

CREATE TABLE IF NOT EXISTS users_groups_rel(
    id serial PRIMARY KEY,
    user_id integer REFERENCES users(id),
    group_id_ integer REFERENCES groups(id),
    UNIQUE(user_id, group_id_)
    );

INSERT INTO groups(name) VALUES('admin');
INSERT INTO groups(name) VALUES('user');

CREATE TABLE IF NOT EXISTS malle_log(
    id serial PRIMARY KEY,
    user_id integer,
    malle_ref varchar(6),
    date_check timestamp,
    observation varchar(128),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (malle_ref) REFERENCES malles(reference)
    );

CREATE TABLE IF NOT EXISTS meta(
    version integer,
    creation_date date
    );

INSERT INTO meta(version, creation_date) VALUES(1, CURRENT_DATE);

CREATE VIEW contenu_check AS
    SELECT produits.nom, 
    contenu_type.quantity as Qtt_p, 
    contenu_malles.quantity as Qtt_r,
    etats.etat,
    contenu_malles.observation
    FROM contenu_malles
    INNER JOIN contenu_type ON contenu_type.id = contenu_malles.contenu_type_id
    INNER JOIN produits ON contenu_type.produit_id = produits.id
    INNER JOIN etats ON etats.id = contenu_malles.etat_id;

CREATE VIEW bon_de_commande AS
	SELECT 
	fournisseurs.nom AS fournisseur,
	fournisseurs.email,
	fournisseurs.phone,
	produits.nom,
	contenu_type.quantity - contenu_malles.quantity AS quantity
    FROM contenu_malles
	LEFT JOIN contenu_type ON contenu_type.id = contenu_malles.contenu_type_id
    LEFT JOIN malles ON malles.reference::text = contenu_malles.malle_ref::text
    INNER JOIN produits ON produits.id = contenu_type.produit_id
    LEFT JOIN fournisseurs ON fournisseurs.id = produits.fournisseur_id
  	WHERE malles.type_id = contenu_type.type_id
  	AND contenu_type.quantity - contenu_malles.quantity > 0
	ORDER BY fournisseur;

CREATE OR REPLACE FUNCTION contenu_malle_init() 
RETURNS TRIGGER AS $contenu_malle_init$
-- This function add blank contenu_malle from contenu_type according to the 
-- type of the new malle. It is triggered at the malle insert. 
    BEGIN
        INSERT INTO contenu_malles(
            malle_ref,
            contenu_type_id,
            quantity,
            etat_id
            )
        SELECT
           NEW.reference,
           id,
           '0',
           '1'
        FROM contenu_type
        WHERE contenu_type.type_id = NEW.type_id;
        RETURN NEW;
    END;
$contenu_malle_init$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION contenu_malle_update() 
RETURNS TRIGGER AS $contenu_malle_update$
-- This function add blank contenu_malle from contenu_type according to the 
-- type of the new malle. It is triggered at the contenu_malle insert. 
    BEGIN
        INSERT INTO contenu_malles(
            malle_ref,
            contenu_type_id,
            quantity,
            etat_id
            )
        SELECT
           reference,
           NEW.id,
           '0',
           '1'
        FROM malles
        WHERE malles.type_id = NEW.type_id;
        RETURN NEW;
    END;
$contenu_malle_update$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION contenu_malle_delete() 
RETURNS TRIGGER AS $contenu_malle_delete$
-- This function delete contenu_malle when the associated contenu_type is 
-- deleted. 
    BEGIN
        DELETE FROM contenu_malles 
        WHERE OLD.id = contenu_malles.contenu_type_id;
        RETURN OLD;
    END;
$contenu_malle_delete$ LANGUAGE plpgsql;

CREATE TRIGGER contenu_malle_trig AFTER INSERT ON malles
    FOR EACH ROW EXECUTE PROCEDURE contenu_malle_init();
CREATE TRIGGER update_type_trig AFTER INSERT ON contenu_type
    FOR EACH ROW EXECUTE PROCEDURE contenu_malle_update();
CREATE TRIGGER delete_type_trig BEFORE DELETE ON contenu_type
    FOR EACH ROW EXECUTE PROCEDURE contenu_malle_delete();
