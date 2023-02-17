DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS staffs;
DROP TABLE IF EXISTS checkouts;
DROP TABLE IF EXISTS history;
DROP TABLE IF EXISTS interactions;


CREATE TABLE assets(
	id text NOT NULL,
	asset_type text NOT NULL,
	asset_status text NOT NULL
    );
CREATE UNIQUE INDEX asset_id on assets (id);


CREATE TABLE staffs(
    id text NOT NULL,
	FirstName text NOT NULL,
    LastName text NOT NULL,
    Division text NOT NULL,
    Department text NOT NULL,
    Title text NOT NULL
    );




CREATE TABLE checkouts(
	assetid text NOT NULL,
	staffid text NOT NULL,
	department text NOT NULL,
	timestamp timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
CREATE UNIQUE INDEX check_a_id on checkouts (assetid);


CREATE TABLE history(
	assetid text NOT NULL,
	staffid text NOT NULL,
	department text NOT NULL,
	division text NOT NULL,
    checkouttime timestamp NOT NULL,
	returntime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
    );



CREATE TABLE interactions(
	event text NOT NULL,
	timestamp timestamp NOT NULL
    );

