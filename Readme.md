Anhand der Anleitung unten kann man sich die [öffentliche Rufzeichenliste der Bundesnetzagentur](https://www.bundesnetzagentur.de/SharedDocs/Downloads/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Frequenzen/Amateurfunk/Rufzeichenliste/Rufzeichenliste_AFU.html) (das Gesamtverzeichnis als PDF) als Karte visualisieren lassen. Es handelt sich dabei um ein extrem simples Python-Projekt, das ich an einem Abend zwecks zeitvertreib und Interesse an Python realisiert hatte. Fragen und Anmerkungen zur Programmierung sind willkommen, am besten zu diskutieren auf der [Github Website](https://github.com/thielul/CallmapGermany.git) des Projekts. 

**Hinweis:** Es gibt (und gab) keine Möglichkeit des Downloads der Karte oder von Daten, für die Daten siehe in die [öffentliche Rufzeichenliste der Bundesnetzagentur](https://www.bundesnetzagentur.de/SharedDocs/Downloads/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Frequenzen/Amateurfunk/Rufzeichenliste/Rufzeichenliste_AFU.html).

von [Ulrich Thiel, VK2UTL/DK1UT](mailto:u-thiel@gmx.net)

# News
* 26.05.2017: Viele kleine Verbesserungen (pdftotext unterstützt; Unicode-Probleme sollten behoben sein (hoffentlich); Datenbank-Struktur leicht verändert (separate Locations Datenbank)).
* 24.05.2017: Karte entfernt, Anleitung erweitert
* 23.05.2017: Projekt online gestellt

# Vorgehen

Die folgende Anleitung sollte eigentlich unter allen Betriebssystemen funktionieren (ich habe MacOS und Windows getestet). In jedem Fall wird alles, was ich unten schildere, in einem **Terminal** (Bash/Eingabeaufforderung) ausgeführt.


## Skripte
Die Quellen meiner Skripte gibt es auf der [Github Website](https://github.com/thielul/CallmapGermany) des Projekts (oder [hier](https://github.com/thielul/CallmapGermany.git) direkt zum Zip-Archiv). Dieses Archiv lädt man komplett runter (es enthält neben den Python-Skripten eine leere SQLite Datenbank names  ```calls.db```, **die benötigt wird**).

## Externe Tools

Wir benötigen folgende externe Tools:

* Eine [Python2](https://www.python.org/downloads/) Installation. Ich empfehle, gleich ein komplettes Bundle mit vielen Bibliotheken wie z.B. [Anaconda](https://www.continuum.io/downloads) zu installieren. Falls man bereits eine Python-Installation hat, sollte man beachten, dass man python2 aufruft, nicht python3 (beide Versionen können ko-existieren).

* Wir benötigen für Python die Bibliotheken [sqlite3](https://docs.python.org/2/library/sqlite3.html), [tqdm](https://pypi.python.org/pypi/tqdm) und [geocoder](https://pypi.python.org/pypi/geocoder). Falls nicht vorhanden, kann man diese einfach mittels [pip](https://pip.pypa.io/en/stable/installing/) installieren:

```
pip install sqlite3
pip install tqdm
pip install geocoder
```

Unter Umständen muss man obigen Kommandos ein ```sudo``` voranstellen. Falls pip selbst nicht vorhanden ist, kann man dies wie [hier](https://pip.pypa.io/en/stable/installing/) beschrieben installieren. (unter Windows müsste man im Internet mal recherchieren, wie man pip richtig installiert (hat jemand einen Link?); bei mir geht es, habe aber vergessen, wie es ging; man benötigt für die Installation in jedem Fall auch eine Eingabeaufforderung mit Admin-Rechten, das man mittels Rechtsklick auf *Eingabeaufforderung* und *Als Administrator öffnen* bekommt).

* Ein Tool zum Konvertieren von PDF-Datein in Text-Datein. Ich habe dazu [pdftotext](https://en.wikipedia.org/wiki/Pdftotext) verwendet, es ist Teil des Poppler-Bundles. Unter MacOS kann man das mittels [Homebrew](https://brew.sh) und dann ```brew install poppler``` installieren. Für Linux sollte sich das mit dem entsprechenden Paket-Manager installieren lassen. Für Windows gibt es das [hier](http://blog.alivate.com.au/poppler-windows/).

## Rufzeichenliste
Bei der [öffentlichen PDF-Datei der Bundesnetzagentur](https://www.bundesnetzagentur.de/SharedDocs/Downloads/DE/Sachgebiete/Telekommunikation/Unternehmen_Institutionen/Frequenzen/Amateurfunk/Rufzeichenliste/Rufzeichenliste_AFU.html) handelt es sich um eine ca. 9MB große PDF-Datei. Diese benötigen wir.

## Umwandlung in Text-Datei 
Die runtergeladene Rufzeichenliste wandeln wir wie folgt in eine Text-Datei um:

```
pdftotext -enc UTF-8 Rufzeichenliste_AFU.pdf calls.txt
``` 

Unter Windows gibt man das ähnlich in die Eingeabeaufforderung ein (man benutzt ```pdftotext.exe``` aus dem Poppler-Archiv). Da die PDF-Datei relativ groß ist, kann dies einen Moment dauern. Die entstandene Text-Datei ist ca. 4MB groß. Im Prinzip ist es egal, welches Tool man dazu benutzt; mein Skript im nächsten Schritt berücksichtigt aber gewisse Eigenarten von ps2ascii oder pdftotext, wird daher also ohne Modifikationen wahrscheinlich nur dafür richtig funktionieren.

## Erstellung der Datenbank

Das Rückgrat des Projekts ist eine SQL-Datenbank (genauer, SQLite-Datenbank), die wir aus der Text-Datei mittels

```
python makedb.py
```

erstellen. Dieses Skript geht die Text-Datei ```calls.txt``` zeilenweise durch, extrahiert die relevanten Daten, und speichert sie in die SQLite-Datenbank ```calls.db```. Dieser Teil ist natürlich am schwierigsten zu Programmieren. Ich verwende zum Parsen reguläre Ausdrücke. Es gibt leider ein paar Formatierfehler in der Rufzeichenliste selbst, die ich im Skript auch berücksichtigen muss. 

Die Datenbank selbst kann man sich z.B. mit dem netten Tool [SQLite Browser](http://sqlitebrowser.org) anschauen (im Tab *Browse Data*). Es besteht aus den beiden Tabellen ```Calls``` und ```Locations```, und einem View ```CallsComplete```. Die Tabelle ```Locations``` ist eine Liste mit Adressen, versehen mit einer eindeutigen Id, auf die in der Tabelle ```Calls``` referenziert wird. Diese Separation macht alles etwas effizienter. Das nette an SQL ist, dass man ganz leicht sehr komplexe Datenabfragen machen kann, z.B.

```
SELECT Count(*) FROM CallsComplete WHERE City="Berlin"
```

### Zu erledigen
  
1. Beim Parsen wird es bestimmt noch den einen oder anderen Fehler geben, vielleicht kann das jemand noch verbessern. Ich denke aber, zu 99.9% sollte alles in Ordnung sein.
2. Die Spalte *Category* wird momentan noch nicht gesetzt. Die Idee wäre, je nach Art der Station (Klubstation, Relais, etc.) die Kategorie zu setzen.

## Geocoding

Wie kommen wir nun von den in der Datenbank vorhandenen (und hoffentlich korrekt geparsten) Adressen zu Punkten in einer geographischen Karte? Die Antwort heißt *Geocoding*, womit wir dann schließlich im 21. Jahrhundert angekommen sind. Dabei handelt es sich um Datenbanken, die Adressen in geographische Koordinaten umwandeln (Länge/Breitengrad), und diese lassen sich dann in einer Karte visualisieren. Es gibt Geocoding-Schnittstellen von Google (diese habe ich benutzt), aber auch von OpenStreetMap und anderen Diensten. Weiterhin gibt es Python-Bibliotheken mit Schnittstellen zu diesen Schnittstellen. Ich habe [geocoder](https://pypi.python.org/pypi/geocoder) verwendet, das wir wie oben geschildert installiert haben. Wir machen einen kurzen Test mit dem Skript aus dem Archiv:

```
python geocode.py
Address: Alter Hellweg 56, 44379 Dortmund, Deutschland
7.37648 51.49813
```

Das Geocoding war erfolgreich und wir haben Längen- und Breitengrad erhalten. Ist die Adresse nicht vorhanden (in der Realität oder in der Geocoding-Datenbank), geht das natürlich nicht. Ein simpler Schreibfehler kann hier schon Probleme bereiten.

Mittels

```
python makegeo.py
```

werden die Adressen in der Datenbank einzeln durchgegangen, ein Geocoding abgefragt und die Koordinaten in die Spalten Lng/Lat der Tabelle ```Locations``` eingefügt. Gibt es vom Server keine Fehlermeldung (Adresse nicht gefunden oder ähnlich), wird in der Spalte Geocode eine 1 gesetzt, ansonsten eine 0. Man kann das Skript jederzeit unterbrechen und erneut starten; alle Einträge mit erfolgreichem Geocoding (Geocode=1) werden dabei übersprungen.

Da das Geocoding aus einzelnen Abfragen besteht, dauert dies sehr lange (1 Sekunde je Abfrage). Erschwerend kommt hinzu, dass Google ein Limit von 2,500 Abfragen pro Tag hat. Die 70,000 Adressen zu geocoden, dauert also eine Weile, wenn man nicht mehrere Computer mit verschiedenen IPs benutzen kann.  
 
**Hinweis:** Man kann natürlich immer auch Zwischen-Ergebnisse nach den Schritten unten visualisieren, d.h. man muss nicht ewig warten, um eine erste Karte zu sehen. Weiterhin kann man sich bei der ```SELECT``` Abfrage in ```makegeo.py``` auch auf einen festen Ort beschränken, was die Anzahl reduziert. Eine andere Möglichkeit wäre noch das Geocoding mittels OpenStreetMap. Dazu kann man in ```makegeo.py``` einfach *google* durch *osm* ersetzen (oder durch jeden anderen unterstützten Dienst). Schließlich könnten sich mehrere OMs zusammenschließen und gewisse Blöcke geocoden und die Ergebnisse mergen. Das SQL-Rückgrat macht das alles sehr leicht.

### Zu erledigen
  
1. Fehler in den Adressen erkennen und korrigieren.  
2. Geocoding-Fehler korrekt abfangen (ganz selten ist das Geocoding "erfolgreich", aber die Koordinaten stimmen nicht).  
3. Andere Dienste nutzen, wie z.B. OpenStreetMap.

## CSV-Datei

Mittels 

```
python makecsv.py
```

erstellt man eine CSV-Datei aus der Datenbank. Dabei gehe ich so vor, dass ich mittels der SQL-Abfrage

```
SELECT Lng, Lat FROM Locations WHERE Geocode=1
```

zunächst sämtliche Standorte sammle. In einem zweiten Schritt werden für jeden Standort alle Stationen an diesem Ort gesucht. Die Daten dazu werden in der Spalte *Label* der CSV-Datei eingefügt. In der Spalte *Marker* ist eine Anweisung für die Art der Markierung an diesem Ort.

### Zu erledigen

1. Weitere verschiedene Marker, z.B. für Relais oder Klubstationen.

## Google Fusion Tables

Jetzt haben wir alles zusammen für die Visualisierung der Daten: wir erstellen eine [Google Fusion Table](https://fusiontables.google.com). Dazu benötigt man einen Google-Account und klickt bei dem gerade genannten Link auf *Create a fusion table*. Dann kann man die erstellte CSV-Datei ```calls.csv``` hochladen. Bei erfolgreichem Import (es sollte eigentlich keine Probleme geben), kan man auf *Map of Lat* klicken und sieht sofort die Punkte visualisiert. Man kann jetzt noch unter *Change map styles* auf *Column* gehen und dort die Spalte *Marker* selektieren. Dann werden unsere individuellen Markierungen übernommen. Weiterhin kann man unter *Change info window* auf *Custom* klicken und dort *{Label}* eingeben, sodass unser individuell erstelltes Label verwendet wird. Fertig!

Meine Visualisierung ist nur privat und nicht öffentlich zu sehen.

Die Fusion Table findet man übrigens in seinem [Google Drive](http://drive.google.com), falls man später Änderungen durchführen möchte.

### Zu erledigen

1. Andere Dienste ausprobieren (obwohl die Fusion Tables recht genial sind).
2. Mit dem Skript ```makekml.py``` kann man auch eine KML-Datei mit den Daten erstellen, die man in viele Programme importieren kann. Ich habe das nicht weiter aktualisiert, aber dies bietet auch noch viele Möglichkeiten.
