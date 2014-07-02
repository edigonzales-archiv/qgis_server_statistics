-- DROP TABLE qgis_server_statistics.wms_stats;

CREATE TABLE qgis_server_statistics.wms_stats
(
  ogc_fid serial NOT NULL,
  ip inet,
  request_date timestamp,
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
  CONSTRAINT wms_stats_pkey PRIMARY KEY (ogc_fid),
  CONSTRAINT enforce_srid_bbox_geom CHECK (st_srid(bbox_geom) = 21781)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE qgis_server_statistics.wms_stats OWNER TO stefan;
GRANT ALL ON TABLE qgis_server_statistics.wms_stats TO stefan;
GRANT SELECT ON TABLE qgis_server_statistics.wms_stats TO mspublic;

CREATE INDEX idx_wms_stats_bbox_geom
  ON qgis_server_statistics.wms_stats
  USING gist
  (bbox_geom);

CREATE INDEX idx_wms_stats_request_date
  ON qgis_server_statistics.wms_stats
  USING btree
  (request_date);

CREATE INDEX idx_wms_stats_map
  ON qgis_server_statistics.wms_stats
  USING btree
  (map);

INSERT INTO geometry_columns VALUES ('"', 'qgis_server_statistics', 'wms_stats', 'bbox_geom', 2, '21781', 'POLYGON');
