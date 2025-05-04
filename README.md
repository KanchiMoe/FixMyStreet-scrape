


## .env

This project makes use of a .env file. It looks like this: 

```
# Logging
LOG_LEVEL=DEBUG

# DB
PGHOST=localhost
PGPORT=5432
PGDATABASE=fms
```

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
```


