# FUMEX – Randfasen und aufrechte Ladeplatine

Stand: 23. September 2026. Ergänzung zum [Projekt-Audit](audit-2026-09-23.md) und zur [Nachprüfung der Rundungen G2/G3](rounding-2026-09-23.md).

## Umgesetzte Änderungen

**Die vorgesehenen Randfasen werden mit BOSL2 aus ihren tatsächlichen Endkonturen erzeugt.** `profile_sweep_y()` verwendet `offset_sweep()` und `os_chamfer()` für Kopf, Rückwand und Kassette; die Bodenfase der Basis folgt demselben Verfahren. Die Fasenhöhe hängt damit nicht mehr von dünnen Hilfskörpern einer Hülloperation ab. BOSL2 ist als Git-Submodul auf `989cc33b56313238f3ffeafcbd2876b71a0a593a` festgelegt.

Die tangentialen R3,5-Rundungen entlang der langen Gehäuseseiten bleiben erhalten. Auch die geglätteten oberen Ecken, der angepasste Sockelübergang und der gewollte 15°-Knick bleiben bestehen. Die Änderung betrifft gezielt die Randfasen.

**Die Ladeplatine steht jetzt aufrecht auf dem Ballastdeckel.** Die Bauteile zeigen nach vorn, der Kühlkörper nach hinten. Zwei schmale, oben offene Endhalter ersetzen die umschließende Wanne. Links führt eine 1,4-mm-Nut die 1-mm-Platine; rechts bleibt die Rückseite wegen des überstehenden Kühlkörpers offen. Die Platine wird von oben eingesetzt.

| Bauteilseite | Kühlkörperseite |
|---|---|
| ![Aufrechte Platine von vorn](../img/04_charger_front.png) | ![Aufrechte Platine von hinten](../img/05_charger_back.png) |

Die Platine reicht von z = **32,2 bis 43,2 mm**, Kühlkörper samt Pad von **30,7 bis 44,7 mm**. Unter dem Kühlkörper bleiben 1,7 mm zur Deckelfläche. Der gedruckte Deckel ist einschließlich Halter 12,4 mm hoch.

## Geometrische Nachweise

- **Randfasen:** 24 Messungen an den tatsächlichen Netzkonturen; größte Abweichung vom vorgesehenen Profil etwa **0,0002 mm**.
- **Luftzugang:** Freiräume unmittelbar vor den Bauteilen und hinter dem Kühlkörper bleiben offen. Zwei zusammenhängende **Ø1,2-mm-Prüfkorridore** verbinden sie durch vorhandene Kopfbodenschlitze mit dem Plenum und durch Rückwandschlitze mit der Umgebung. Die Bauteilseite wird um das linke Platinenende herum angebunden.
- **Halter und Montage:** Die endgültigen Netze lassen Platine und Kühlkörper über 30 mm senkrecht ein- und ausbauen. Anschläge begrenzen die Verschiebung nach vorn und hinten. Der geprüfte Deckelhub umfasst Platine und Kühlkörper gemeinsam.
- Die bestehenden Prüfungen für obere Eckübergänge und Sockelfuge bleiben aktiv.

## Grenzen

Die Korridore beweisen freien geometrischen Zugang, **keine Luftmenge oder ausreichende Kühlung**. Temperaturen müssen mit realer Verkabelung im geschlossenen Gehäuse beim Laden geprüft werden, mit laufendem und stehendem Lüfter.

Zwischen Pad und rechter Führung bleiben nur **0,2 mm**. Padüberstand, Lötstellen und Kabelausgänge brauchen einen realen Passtest. Die offenen Halter verhindern kein Anheben an den Leitungen. Kabel dürfen die Luftwege nicht verschließen.

`lid_off` prüft ausschließlich **10 mm Aufwärtsbewegung** des bestückten Deckels. Anschließendes Ausfädeln und Kippen sind nicht nachgewiesen.

## Abschließende Prüfung

Der vollständige Export besteht: **7 Druckteiltypen / 10 Druckteile**, geschlossene Netze ohne degenerierte Dreiecke, **394 koaxiale Merkmals-Paare, 435 Baugruppenpaare und 8 Montagewege**. Die 14 dokumentierten Ausnahmen für beabsichtigte Passungen und Montagezustände bleiben bestehen. Die neuen Platinenanschläge greifen in beiden Richtungen nach 0,25 mm.

Alle vier Analysen über sämtliche sieben Teiltypen sind **CLEAN**: Inseln, Überhänge (100-mm²-Schwelle), Wanddicke und freie dünne Stege. Die Wanddickenanalyse meldet am Kopf dieselben numerischen Trimesh-Warnungen wie vor der Umstellung; 64.906 von 65.060 Stichproben liefern einen Messwert. Sie ist eine Stichprobe und kein lückenloser Wanddickennachweis.

Bambu Studio slict alle sieben Teile und alle vier Platten erfolgreich mit deaktivierten Stützen. **469,7 g / 15,3 h** als angeordnete Platten; **470,0 g / 16,1 h** als Einzelteilaufträge. Die bekannten Hinweise „floating cantilever“ an Basis und Kopf bleiben bestehen. Der Deckel mit den neuen Haltern hat keine Slicerwarnung.

Geschätzte Masse des aufgebauten Geräts: **1.007,6 g**, Kippwinkel **21,4°**. Es wurde kein realer Druck- oder Temperaturversuch durchgeführt.

Nachweise: [Geometrie und Montage](verification.json), [Druckbarkeitsanalysen](bosl2-charger-2026-09-23/analysis.json), [Slicer](slicer-summary.json), [aktualisierter Viewer](index.html). Modell-SHA-256: `544894c9fc4dc5176798e87bd9ad6000a1cbd028eab20a550ffad9b17326cd1d`. Die Fasenprüfung verwirft den vorherigen Modellstand; die Luftzugangsprüfung verwirft die frühere flache Platinenlage.
