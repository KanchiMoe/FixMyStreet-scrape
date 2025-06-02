


## .env

This project makes use of a .env file. It looks like this: 

```
# Logging
LOG_LEVEL=DEBUG

# DB
PGHOST     = localhost
PGPORT     = 5432
PGDATABASE = fms
```

## Features

### Auto-find current highest report ID

FixMyStreet report IDs increase daily, requiring regular updates to track the latest one. This feature automates that process by identifying the current highest report ID.

It begins at the `UPPER_NUMBER` value stored in the meta table and increments sequentially. For each ID, it checks the response status:

* If the response is a 404, it increments a consecutive failure counter.

* After 5 consecutive 404s, it assumes the last successful response (e.g., 200, 403, 410) was the highest valid ID and updates `UPPER_NUMBER` accordingly.

## Database

### Table schema

```sql
CREATE TABLE "public"."details" ( 
  "id" INTEGER NOT NULL,
  "category" TEXT NULL,
  "title" TEXT NULL,
  "description" TEXT NULL,
  CONSTRAINT "PK_details" PRIMARY KEY ("id")
);

CREATE TABLE "public"."location" ( 
  "id" INTEGER NOT NULL,
  "latitude" DOUBLE PRECISION NULL,
  "longitude" DOUBLE PRECISION NULL,
  "council" TEXT NULL,
  CONSTRAINT "PK_location" PRIMARY KEY ("id")
);

CREATE TABLE "public"."method" ( 
  "id" INTEGER NOT NULL,
  "method" TEXT NULL,
  CONSTRAINT "PK_method" PRIMARY KEY ("id")
);

CREATE TABLE "public"."status" ( 
  "id" INTEGER NOT NULL,
  "status" TEXT NULL,
  "reported_timestamp" TIMESTAMP WITH TIME ZONE NULL,
  "editable" BOOLEAN NULL,
  CONSTRAINT "PK_fms" PRIMARY KEY ("id")
);

CREATE TABLE "public"."updates" ( 
  "id" INTEGER NOT NULL,
  "no_of_updates" INTEGER NULL,
  "latest_timestamp" TIMESTAMP WITH TIME ZONE NULL,
  CONSTRAINT "PK_updates" PRIMARY KEY ("id")
);

CREATE TABLE "public"."logs" ( 
  "id" INTEGER NOT NULL,
  "timestamp" TIMESTAMP WITH TIME ZONE NOT NULL,
  CONSTRAINT "PK_logs" PRIMARY KEY ("id")
);

CREATE TABLE "public"."meta" ( 
  "key" TEXT NOT NULL,
  "value" TEXT NULL
);
```

#### Meta table

The meta table is a key-value to store some miscellaneous data used by the program.

Key|Use
:--|:--
`UPPER_NUMBER`|Used to define the highest number to go to in the sequential strategy, range of numbers to pick from for the random strategy and checking that we have all possible rows from that.
