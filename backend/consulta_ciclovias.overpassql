[out:json][timeout:60];

area["name"="Belém"]
    ["boundary"="administrative"]
    ["admin_level"="8"]->.cidade;

way["highway"="cycleway"](area.cidade);

out tags geom;
