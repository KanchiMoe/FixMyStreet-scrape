


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

FixMyStreet report IDs increase over time, requiring regular updates to keep track of the latest one. This feature automates that process by determining the current highest report ID.

Before running, it checks the value of `run_AFH` in the meta table:

* If `run_AFH` is set to `1`, the feature proceeds.
* If `run_AFH` is set to `0`, it skips execution.

When enabled, the process starts from the current ``UPPER_NUMBER`` value stored in the meta table and increments sequentially. For each ID, it sends a request and checks the response status:

* If the response is a 404, it increments a counter for consecutive 404s.
* Once it encounters 5 consecutive 404s, it assumes the last successful (non-404) response, such as a 200, 403, or 410, was the highest valid report ID.
* That ID is then saved as the new `UPPER_NUMBER`. It will also set `run_AFH` to `0`.

This mechanism ensures ``UPPER_NUMBER`` stays up to date without manual intervention.

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
``UPPER_NUMBER``|Used to define the highest number to go to in the sequential strategy, range of numbers to pick from for the random strategy and checking that we have all possible rows from that.
`run_AFH`|Control if autofind highest report ID should run. `1` for yes, `0` for no.
