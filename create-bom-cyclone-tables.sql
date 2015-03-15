

--DROP TABLE IF EXISTS bom.cyclone_areas;

CREATE TABLE bom.cyclone_areas
(
  gid serial NOT NULL,
  areatype character varying(18),
  extent character varying(31),
  fcasttime character varying(20),
  issuetime character varying(20),
  expiryhrs double precision,
  distid character varying(12),
  distname character varying(6),
  geom geometry(MultiPolygon,4283),
  CONSTRAINT cyclone_areas_pkey PRIMARY KEY (gid, issuetime, distid)
)
WITH (OIDS=FALSE);
ALTER TABLE bom.cyclone_areas OWNER TO postgres;

CREATE INDEX cyclone_areas_geom_idx ON bom.cyclone_areas USING gist (geom);


--DROP TABLE IF EXISTS bom.cyclone_fix;

CREATE TABLE bom.cyclone_fix
(
  gid serial NOT NULL,
  fixtimeutc character varying(20),
  fixtimewa character varying(23),
  fixtiment character varying(23),
  fixtimeqld character varying(23),
  timeoffset double precision,
  fixtype character varying(8),
  category double precision,
  symbol character varying(7),
  fcasttime character varying(20),
  issuetime character varying(20),
  expiryhrs double precision,
  distid character varying(12),
  distname character varying(6),
  geom geometry(Point,4283),
  CONSTRAINT cyclone_fix_pkey PRIMARY KEY (gid, issuetime, distid)
)
WITH (OIDS=FALSE);
ALTER TABLE bom.cyclone_fix OWNER TO postgres;

CREATE INDEX cyclone_fix_geom_idx ON bom.cyclone_fix USING gist (geom);


--DROP TABLE IF EXISTS bom.cyclone_track;

CREATE TABLE bom.cyclone_track
(
  gid serial NOT NULL,
  tracktype character varying(8),
  starttime character varying(20),
  endtime character varying(20),
  fcasttime character varying(20),
  issuetime character varying(20),
  expiryhrs double precision,
  distid character varying(12),
  distname character varying(6),
  geom geometry(MultiLineString,4283),
  CONSTRAINT cyclone_track_pkey PRIMARY KEY (gid, issuetime, distid)
)
WITH (OIDS=FALSE);
ALTER TABLE bom.cyclone_track OWNER TO postgres;

CREATE INDEX cyclone_track_geom_idx ON bom.cyclone_track USING gist (geom);


--DROP TABLE IF EXISTS bom.cyclone_windarea;

CREATE TABLE bom.cyclone_windarea
(
  gid serial NOT NULL,
  windtype character varying(16),
  marinetype character varying(11),
  fixtime character varying(20),
  fixtype character varying(8),
  fcasttime character varying(20),
  issuetime character varying(20),
  expiryhrs double precision,
  distid character varying(12),
  distname character varying(6),
  geom geometry(MultiPolygon,4283),
  CONSTRAINT cyclone_windarea_pkey PRIMARY KEY (gid, issuetime, distid)
)
WITH (OIDS=FALSE);
ALTER TABLE bom.cyclone_windarea OWNER TO postgres;

CREATE INDEX cyclone_windarea_geom_idx ON bom.cyclone_windarea USING gist (geom);

