-- DROP TABLE sogis_ows_statistics.wms_requests;

CREATE TABLE sogis_ows_statistics.wms_requests
(
  ogc_fid serial NOT NULL,
  ip inet,
  request_date timestamp with time zone,
  request_url varchar,
  referer varchar,
  user_agent varchar,
  map varchar,
  layers varchar,
  format varchar,
  dpi varchar,
  version varchar,
  service varchar,
  request varchar,
  styles varchar,
  crs varchar,
  bbox varchar,
  bbox_geom geometry(Polygon, 21781),
  width double precision,
  height double precision,
  CONSTRAINT wms_requests_pkey PRIMARY KEY (ogc_fid),
  CONSTRAINT enforce_srid_bbox_geom CHECK (st_srid(bbox_geom) = 21781)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE sogis_ows_statistics.wms_requests OWNER TO stefan;
GRANT ALL ON TABLE sogis_ows_statistics.wms_requests TO stefan;
GRANT SELECT ON TABLE sogis_ows_statistics.wms_requests TO mspublic;

CREATE INDEX idx_wms_requests_bbox_geom
  ON sogis_ows_statistics.wms_requests
  USING gist
  (bbox_geom);

CREATE INDEX idx_wms_requests_request_date
  ON sogis_ows_statistics.wms_requests
  USING btree
  (request_date);

CREATE INDEX idx_wms_requests_map
  ON sogis_ows_statistics.wms_requests
  USING btree
  (map);

INSERT INTO geometry_columns VALUES ('"', 'sogis_ows_statistics', 'wms_requests', 'bbox_geom', 2, '21781', 'POLYGON');
