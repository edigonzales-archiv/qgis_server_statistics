--Jahr
SELECT request_date::date, count(request_date) 
FROM qgis_server_statistics.wms_stats
WHERE map = 'grundbuchplan'
GROUP BY request_date::date;


--Monat
SELECT s.day::int, coalesce(t.value, 0) 
FROM generate_series(1,31) AS s(day) 
LEFT OUTER JOIN 
(
  SELECT COUNT(ogc_fid) AS value, EXTRACT(day FROM request_date) AS day 
  FROM qgis_server_statistics.wms_stats WHERE EXTRACT(month FROM request_date) = 9 
  GROUP BY day
) AS t 
ON s.day = t.day
ORDER BY s.day


--Woche
SELECT s.day::int, coalesce(t.value, 0) 
FROM generate_series(0,6) AS s(day) 
LEFT OUTER JOIN 
(
  SELECT COUNT(ogc_fid) AS value, EXTRACT(DOW FROM request_date) AS day 
  FROM qgis_server_statistics.wms_stats WHERE EXTRACT(week FROM request_date) = 38 
  GROUP BY day
) AS t 
ON s.day = t.day
ORDER BY s.day


--Tag
SELECT s.hour::int, coalesce(t.value, 0)
FROM generate_series(0,23) AS s(hour) 
LEFT OUTER JOIN 
(
  SELECT COUNT(ogc_fid) AS value, EXTRACT(hour FROM request_date) AS hour 
  FROM qgis_server_statistics.wms_stats WHERE date_trunc('day', request_date) = '2013-06-12' 
  GROUP BY hour
) AS t 
ON s.hour = t.hour
ORDER BY s.hour; 