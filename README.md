QGIS Server Statistics
======================

Grundidee
---------
Das Apache access.log wird nach (QGIS Server) WMS Requests durchsucht und allfällige Requests werden in eine Datenbanktabelle geschrieben. Aus den Daten in der Tabelle werden Charts erstellt.

Voraussetzungen
---------------

* PostgreSQL >= 8.3 
* Postgis >= 1.5
* Python 2.6 (für NV3D-Charts Python 2.7... OrderedDict)

Funktionsweise
--------------
Die Klasse hat `QgsServerStatistics` hat drei Methoden:

1. `create_sql`: Schreibt SQL-Befehle zum Erzeugen eines Schemas und einer Tabelle in eine Datei.
2. `update_database`: Durchsucht die Datei access.log nach WMS-Requests. Diese Aufrufe müssen eine bestimmten Systematik folgen (`/wms/qgis-projektename-ohne-extension?SERVICE=WMS&REQUEST=GetMap&....`). Gefunden Aufrufe werden in die Tabelle geschrieben. Es wird zwar jeweils die ganze Datei durchsucht aber nur *neue*, dh. in der Tabelle noch nicht vorhandene Requests, in die Tabelle importiert.
3. `export_json`: Schreibt json-Dateien als Grundlage für NVD3-Charts (requests / min). Je eine Datei für die letzten 24 Stunden, die letzten sieben Tage, die letzten 30 Tage und die letzten 365 Tage. Um die Datenmenge gering zu halten, kann das Beobachtungszeitintervall frei gewählt werden. Würde jede Minute einzeln beobachtet, so ergäbe das beim Jahreschart 525'600 Punkte. Zuviel für NVD3. Aus diesem Grund wird im Beobachtungszeitintervall (z.B. 1 Stunde) aufsummiert und dann die durchschnittliche Anzahl pro Minute eruiert. Dadurch fallen halt einige Spitzen in solchen Charts weg.

Achtung
-------
Unter Ubuntu 10.04 gibts standardmässig nur Python 2.6. Der Export in eine Json-Datei funktioniert aber über Dicts. Diese sind ungeordnet. NVD3 hat Sortierfunktionen. Eventuell reicht das bereits. Oder halt beim Generieren eine andere Lösung finden.

TODO
----
* Loggen
* Blacklists (z.B. IP des Kantons Solothurn etc.)
* Bessere Chartslösung (NV3D darfs schon sein, nur nicht so hingefrickelt wie bei mir).
