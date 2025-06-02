


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

The highest report ID on FixMyStreet grows each day, meaning you have to constantly increase this value. This feature aims to solve that problem by trying to find what the current highest report ID is.

It uses the value of `UPPER_NUMBER` from the meta table and counts up sequentially. If the response is 404, it keeps a counter of how many 404s it has encountered consecutively. If it hits 5 404s consecutively, it takes the last non-404 response (be it, 200, 403, 410, etc) and stores that as the newest `UPPER_NUMBER`.

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
