SELECT DISTINCT ON (map) map FROM sogis_ows_statistics.wms_requests



-- Anzahl Requests der letzten 24 Stunden in 5 Minuten Intervallen.

SELECT EXTRACT(EPOCH FROM t1.cumulative_datetime) * 1000::integer as cumulative_datetime, coalesce(t2.count, 0) as count
--FROM generate_series(NOW() - '1 day'::INTERVAL, NOW(), '5min') AS t1(cumulative_datetime)
FROM generate_series('2014-07-15 14:25:00'::timestamp,'2014-07-16 14:24:59'::timestamp, '5min') AS t1(cumulative_datetime)
LEFT OUTER JOIN 
(
 SELECT count(*), round(extract('epoch' from request_date) / 300),  timestamp with time zone 'epoch' + round(extract('epoch' from request_date) / 300) * 300 * INTERVAL '1 second' as cumulative_datetime
 FROM sogis_ows_statistics.wms_requests
-- Das geht wirklich nur mit NOW().
--WHERE request_date >= NOW() - '1 day'::INTERVAL
-- Zum testen:
 WHERE request_date >= '2014-07-15 14:25:00'::timestamp 
 AND request_date < '2014-07-16 14:24:59'::timestamp 
 GROUP BY round(extract('epoch' from request_date) / 300)
 ORDER BY round(extract('epoch' from request_date) / 300)
) AS t2
ON  t1.cumulative_datetime =  t2.cumulative_datetime
ORDER BY t1.cumulative_datetime;



SELECT EXTRACT(EPOCH FROM t1.cumulative_datetime) * 1000::integer as cumulative_datetime, coalesce(t2.count, 0) as count
FROM generate_series(NOW() - '1 day'::INTERVAL, NOW(), '15min') AS t1(cumulative_datetime)
--FROM generate_series('2014-07-15 14:00:00'::timestamp,'2014-07-16 14:00:00'::timestamp, '15min') AS t1(cumulative_datetime)
LEFT OUTER JOIN 
(
 SELECT count(*), round(extract('epoch' from request_date) / 900),  timestamp with time zone 'epoch' + round(extract('epoch' from request_date) / 900) * 900 * INTERVAL '1 second' as cumulative_datetime
 FROM sogis_ows_statistics.wms_requests
-- Das geht wirklich nur mit NOW().
 WHERE request_date >= NOW() - '1 day'::INTERVAL
-- Zum testen:
 --WHERE request_date >= '2014-07-15 14:00:00'::timestamp 
 --AND request_date <= '2014-07-16 14:00:00'::timestamp 
 GROUP BY round(extract('epoch' from request_date) / 900)
 ORDER BY round(extract('epoch' from request_date) / 900)
) AS t2
ON  t1.cumulative_datetime =  t2.cumulative_datetime
ORDER BY t1.cumulative_datetime;


----- scheint zu funkioniern!!!!!!

-- DAILY
SELECT t1.my_datetime * 60 * 1000, coalesce(t2.count, 0) as count
FROM
(
 SELECT round(EXTRACT(EPOCH FROM t1.cumulative_datetime) / 60) as my_datetime
 FROM generate_series(NOW() - '1 day'::INTERVAL, NOW(), '60sec') AS t1(cumulative_datetime)
) as t1
LEFT OUTER JOIN
(
 SELECT count(*) as count, round(extract('epoch' from request_date) / 60) as my_datetime, timestamp with time zone 'epoch' + round(extract('epoch' from request_date) / 60) * 60 * INTERVAL '1 second' as cumulative_datetime
 FROM sogis_ows_statistics.wms_requests
 WHERE request_date >= NOW() - '1 day'::INTERVAL
 GROUP BY round(extract('epoch' from request_date) / 60)
 ORDER BY round(extract('epoch' from request_date) / 60)
) as t2
ON t1.my_datetime = t2.my_datetime
ORDER BY t1.my_datetime;



SELECT t1.my_datetime * 60 * 1000, coalesce(t2.count, 0) as count
FROM
(
 SELECT round(EXTRACT(EPOCH FROM t1.cumulative_datetime) / 60) as my_datetime
 FROM generate_series(NOW() - '1 week'::INTERVAL, NOW(), '60sec') AS t1(cumulative_datetime)
) as t1
LEFT OUTER JOIN
(
 SELECT count(*) as count, round(extract('epoch' from request_date) / 60) as my_datetime, timestamp with time zone 'epoch' + round(extract('epoch' from request_date) / 60) * 60 * INTERVAL '1 second' as cumulative_datetime
 FROM sogis_ows_statistics.wms_requests
 WHERE request_date >= NOW() - '1 week'::INTERVAL
 GROUP BY round(extract('epoch' from request_date) / 60)
 ORDER BY round(extract('epoch' from request_date) / 60)
) as t2
ON t1.my_datetime = t2.my_datetime
ORDER BY t1.my_datetime;



SELECT t1.my_datetime * 1800 * 1000, coalesce(t2.count, 0) as count
FROM
(
 SELECT round(EXTRACT(EPOCH FROM t1.cumulative_datetime) / 1800) as my_datetime
 FROM generate_series(NOW() - '1 month'::INTERVAL, NOW(), '1800sec') AS t1(cumulative_datetime)
) as t1
LEFT OUTER JOIN
(
 SELECT count(*) as count, round(extract('epoch' from request_date) / 1800) as my_datetime, timestamp with time zone 'epoch' + round(extract('epoch' from request_date) / 1800) * 1800 * INTERVAL '1 second' as cumulative_datetime
 FROM sogis_ows_statistics.wms_requests
 WHERE request_date >= NOW() - '1 month'::INTERVAL
 GROUP BY round(extract('epoch' from request_date) / 1800)
 ORDER BY round(extract('epoch' from request_date) / 1800)
) as t2
ON t1.my_datetime = t2.my_datetime
ORDER BY t1.my_datetime;

SELECT t1.my_datetime * 3600 * 1000, coalesce(t2.count, 0) as count
FROM
(
 SELECT round(EXTRACT(EPOCH FROM t1.cumulative_datetime) / 3600) as my_datetime
 FROM generate_series(NOW() - '1 year'::INTERVAL, NOW(), '3600sec') AS t1(cumulative_datetime)
) as t1
LEFT OUTER JOIN
(
 SELECT count(*) as count, round(extract('epoch' from request_date) / 3600) as my_datetime, timestamp with time zone 'epoch' + round(extract('epoch' from request_date) / 3600) * 3600 * INTERVAL '1 second' as cumulative_datetime
 FROM sogis_ows_statistics.wms_requests
 WHERE request_date >= NOW() - '1 year'::INTERVAL
 GROUP BY round(extract('epoch' from request_date) / 3600)
 ORDER BY round(extract('epoch' from request_date) / 3600)
) as t2
ON t1.my_datetime = t2.my_datetime
ORDER BY t1.my_datetime;


-----


-- 5minuten = 300 s

SELECT count(*), round(extract('epoch' from request_date) / 300),  timestamp with time zone 'epoch' + round(extract('epoch' from request_date) / 300) * 300 * INTERVAL '1 second' as cumulative_datetime
FROM sogis_ows_statistics.wms_requests
-- Das geht wirklich nur mit NOW().
--WHERE request_date >= NOW() - '1 day'::INTERVAL
-- Zum testen:
WHERE request_date >= '2014-07-16 00:00:00'::timestamp 
AND request_date < '2014-07-16 23:59:59'::timestamp 
GROUP BY round(extract('epoch' from request_date) / 300)
ORDER BY round(extract('epoch' from request_date) / 300)




SELECT round(extract('epoch' from request_date) / 60), extract('epoch' from request_date), request_date
FROM sogis_ows_statistics.wms_requests
-- Das geht wirklich nur mit NOW()
--WHERE request_date >= NOW() - '1 day'::INTERVAL
WHERE request_date >= '2014-07-16 00:00:00'::timestamp 
AND request_date < '2014-07-16 23:59:59'::timestamp 
--GROUP BY round(extract('epoch' from request_date) / 60)
ORDER BY request_date



/**********************************************************/
--Jahr
SELECT request_date::date, count(request_date) 
FROM sogis_ows_statistics.wms_requests
WHERE map = 'grundbuchplan-nf'
GROUP BY request_date::date;


--Monat
SELECT s.day::int coalesce(t.value, 0) 
FROM generate_series(1,31) AS s(day) 
LEFT OUTER JOIN 
(
  SELECT COUNT(ogc_fid) AS value, EXTRACT(day FROM request_date) AS day 
  FROM sogis_ows_statistics.wms_requests WHERE EXTRACT(month FROM request_date) = 7 
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
  FROM sogis_ows_statistics.wms_requests WHERE EXTRACT(week FROM request_date) = 38 
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
  FROM sogis_ows_statistics.wms_requests WHERE date_trunc('day', request_date) = '2014-07-15' 
  GROUP BY hour
) AS t 
ON s.hour = t.hour
ORDER BY s.hour; 
