from decimal import Decimal

from django.core.management.base import BaseCommand

from catalog.models import Vehicle, Venue, VenueImage

CASTLE_IMAGES = [
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/5/53/Brzeg_Castle_03.jpg/1920px-Brzeg_Castle_03.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/8/8a/Castle_Ponovi%C4%8De%2C_Municipality_Litija%2C_Slovenia_%282026%29.jpg/1920px-Castle_Ponovi%C4%8De%2C_Municipality_Litija%2C_Slovenia_%282026%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/1/14/Castle_Tarde_in_La_Roque-Gageac.jpg/1920px-Castle_Tarde_in_La_Roque-Gageac.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/3/37/Castle_of_Compeyre_%283%29.jpg/1920px-Castle_of_Compeyre_%283%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d7/Castle_of_Montpoupon_19.jpg/1920px-Castle_of_Montpoupon_19.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/6/6f/Castle_of_Montresor_09.jpg/1920px-Castle_of_Montresor_09.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/b/b8/Castle_of_Otranto_03.jpg/1920px-Castle_of_Otranto_03.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/4/47/Castle_of_Peyrusse-le-Roc_20.jpg/1920px-Castle_of_Peyrusse-le-Roc_20.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/4/47/Chambord_Castle_Northwest_facade.jpg/1920px-Chambord_Castle_Northwest_facade.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c1/Eilean_Donan_Castle_Panorama.jpg/1920px-Eilean_Donan_Castle_Panorama.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/c/cc/Harlech_Castle_Gatehouse_Tower%2C_Merionethshire%2C_Wales_-_25-07-2017.jpg/1920px-Harlech_Castle_Gatehouse_Tower%2C_Merionethshire%2C_Wales_-_25-07-2017.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/f/ff/Hohenschwangau_-_Schloss_Neuschwanstein1.jpg/1920px-Hohenschwangau_-_Schloss_Neuschwanstein1.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/5/56/Leeds_Castle%2C_Kent%2C_England_3_-_May_09.jpg/1920px-Leeds_Castle%2C_Kent%2C_England_3_-_May_09.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/3/3c/Neuschwanstein_Castle_2024-02.jpg/1920px-Neuschwanstein_Castle_2024-02.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a3/Neuschwanstein_Castle_2024.jpg/1920px-Neuschwanstein_Castle_2024.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f8/Schloss_Neuschwanstein_2013.jpg/1920px-Schloss_Neuschwanstein_2013.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/1/1d/Spanish_Hall_of_Ambras_Castle%2C_Innsbruck_%28inside%29-2024-02-06.jpg/1920px-Spanish_Hall_of_Ambras_Castle%2C_Innsbruck_%28inside%29-2024-02-06.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/d/de/Val_Castle_%2815%29.jpg/1920px-Val_Castle_%2815%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/9/99/Val%C3%A8re_castle_in_Sion%2C_Switzerland%2C_Photo_by_Giles_Laurent.jpg/1920px-Val%C3%A8re_castle_in_Sion%2C_Switzerland%2C_Photo_by_Giles_Laurent.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/3/3a/Wawel_-_Castle_from_Sandomierz_Tower.jpg/1920px-Wawel_-_Castle_from_Sandomierz_Tower.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/4/48/001_Chateau_de_Chillon_and_Dents_du_Midi_Photo_by_Giles_Laurent.jpg/1920px-001_Chateau_de_Chillon_and_Dents_du_Midi_Photo_by_Giles_Laurent.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/2/2a/Chateau_Frontenac_at_dusk_in_Quebec_City.jpg/1920px-Chateau_Frontenac_at_dusk_in_Quebec_City.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d9/Chateau_Frontenac_illuminated_at_night_in_Quebec_City.jpg/1920px-Chateau_Frontenac_illuminated_at_night_in_Quebec_City.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e2/Chateau_Luynes.jpg/1920px-Chateau_Luynes.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f1/Chateau_Versailles_Galerie_des_Glaces.jpg/1920px-Chateau_Versailles_Galerie_des_Glaces.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d0/Chateau_de_Chenonceau_2008E.jpg/1920px-Chateau_de_Chenonceau_2008E.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/1/1f/Ch%C3%A2teau_de_Versailles%2C_galerie_des_glaces%2C_buste_d%27empereur_romain_05_%28N%C3%A9ron_%3F%29.jpg/1920px-Ch%C3%A2teau_de_Versailles%2C_galerie_des_glaces%2C_buste_d%27empereur_romain_05_%28N%C3%A9ron_%3F%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/6/6d/Ch%C3%A2teau_de_Versailles%2C_salon_de_la_paix%2C_buste_d%27empereur_romain_%28Claude%29.jpg/1920px-Ch%C3%A2teau_de_Versailles%2C_salon_de_la_paix%2C_buste_d%27empereur_romain_%28Claude%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/2/21/Diane_L%C3%A9onard_Roger_Versailles_MV5922.jpg/1920px-Diane_L%C3%A9onard_Roger_Versailles_MV5922.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e7/Le_Chateau_de_Versailles_%2C_Palace_of_Versailles%2C_France_2.JPG/1920px-Le_Chateau_de_Versailles_%2C_Palace_of_Versailles%2C_France_2.JPG?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/6/68/Le_Chateau_de_Versailles_%2C_Palace_of_Versailles%2C_France_3.JPG/1920px-Le_Chateau_de_Versailles_%2C_Palace_of_Versailles%2C_France_3.JPG?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/4/40/Le_Chateau_de_Versailles_%2C_Palace_of_Versailles%2C_France_8.JPG/1920px-Le_Chateau_de_Versailles_%2C_Palace_of_Versailles%2C_France_8.JPG?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/0/0d/Main_Fa%C3%A7ade%2C_Palace_of_Versailles%2C_Cour_Royale.jpg/1920px-Main_Fa%C3%A7ade%2C_Palace_of_Versailles%2C_Cour_Royale.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/9/91/Palace_of_Versailles%2C_Detail_%282%29.jpg/1920px-Palace_of_Versailles%2C_Detail_%282%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/d/d0/Palace_of_Versailles%2C_North_Detail.jpg/1920px-Palace_of_Versailles%2C_North_Detail.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/a/ad/Panorama_at_the_Ch%C3%A2teau_de_Versailles_-_Grand_Canal.jpg/1920px-Panorama_at_the_Ch%C3%A2teau_de_Versailles_-_Grand_Canal.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/2/2d/Plan_du_jardin_et_chateau_de_la_Reine.png/1920px-Plan_du_jardin_et_chateau_de_la_Reine.png?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/0/04/Vue_a%C3%A9rienne_du_domaine_de_Versailles_par_ToucanWings_-_Creative_Commons_By_Sa_3.0_-_083.jpg/1920px-Vue_a%C3%A9rienne_du_domaine_de_Versailles_par_ToucanWings_-_Creative_Commons_By_Sa_3.0_-_083.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/0/02/Vue_a%C3%A9rienne_du_domaine_de_Versailles_par_ToucanWings_-_Creative_Commons_By_Sa_3.0_-_113.jpg/1920px-Vue_a%C3%A9rienne_du_domaine_de_Versailles_par_ToucanWings_-_Creative_Commons_By_Sa_3.0_-_113.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/5/51/Water_reflection_of_the_Orangerie_garden_and_Palace_of_Versailles_with_blue_sky_in_France.jpg/1920px-Water_reflection_of_the_Orangerie_garden_and_Palace_of_Versailles_with_blue_sky_in_France.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c7/Arechi_Castle_%28Salerno%29.jpg/1920px-Arechi_Castle_%28Salerno%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/7/7f/Bernardo_Bellotto_-_View_of_Warsaw_from_the_Royal_Castle_-_Google_Art_Project.jpg/1920px-Bernardo_Bellotto_-_View_of_Warsaw_from_the_Royal_Castle_-_Google_Art_Project.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/0/05/Broken_cannon_-_Castle_of_Castelmola_-_Italy_2015.jpg/1920px-Broken_cannon_-_Castle_of_Castelmola_-_Italy_2015.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/7/7b/Castelbuono_Castle_01.jpg/1920px-Castelbuono_Castle_01.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/f/f3/Castle_of_Bard_%283%29.jpg/1920px-Castle_of_Bard_%283%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/9/94/Castle_of_Barletta_03.jpg/1920px-Castle_of_Barletta_03.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/c/ce/Castle_of_Barletta_11.jpg/1920px-Castle_of_Barletta_11.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
    'https://thumb.wikimedia.org/wikipedia/commons/thumb/e/e5/Castle_of_Moncalieri_%281%29.jpg/1920px-Castle_of_Moncalieri_%281%29.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail',
]



def img(photo_id, width=1600):
    return f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w={width}&q=80"


VENUES = [
    {
        "name": "Chateau de Lumiere",
        "slug": "chateau-de-lumiere",
        "country": "FR",
        "region": "Loire Valley",
        "description": (
            "A luminous French chateau set among manicured gardens and ancient woodland. "
            "Grand salons, a vaulted chapel, and terraces overlooking the river create an "
            "atmosphere of quiet grandeur for an unforgettable celebration.\n\n"
            "Includes exclusive use of the estate for the wedding weekend, on-site "
            "accommodation for the wedding party, and a dedicated events team."
        ),
        "capacity": 180,
        "price_from": Decimal("28500.00"),
        "cover": "1582719471384-894fbb16e074",
        "gallery": [
            ("1598928506311-c55ded91a20c", "Garden facade of the chateau"),
            ("1600585154340-be6161a56a0c", "Grand reception salon"),
            ("1519167758481-83f550bb49b3", "Evening celebration on the terrace"),
        ],
    },
    {
        "name": "Domaine de la Seine",
        "slug": "domaine-de-la-seine",
        "country": "FR",
        "region": "Normandy",
        "description": (
            "A romantic riverside estate in Normandy with ivy-clad stone walls, a private "
            "chapel, and sweeping lawns that roll down to the water. Ideal for an intimate "
            "yet spectacular gathering.\n\n"
            "The estate offers a farm-to-table kitchen, riverside ceremony space, and "
            "characterful suites for guests."
        ),
        "capacity": 150,
        "price_from": Decimal("22000.00"),
        "cover": "1600596542815-ffad4c1539a9",
        "gallery": [
            ("1600607687939-ce8a6c25118c", "Riverside ceremony lawn"),
            ("1464146072230-91cabc968266", "Stone courtyard dining"),
            ("1511285560929-80b456fea0bc", "Sunset over the estate"),
        ],
    },
    {
        "name": "Chateau de Provence",
        "slug": "chateau-de-provence",
        "country": "FR",
        "region": "Provence",
        "description": (
            "Sun-drenched Provencal chateau surrounded by lavender fields and olive groves. "
            "Honey-coloured stone, shaded courtyards, and an outdoor amphitheatre make it "
            "perfect for a warm-weather celebration.\n\n"
            "Includes a pool, vineyard views, and accommodation for up to forty guests."
        ),
        "capacity": 220,
        "price_from": Decimal("35000.00"),
        "cover": "1469371670807-013ccf25f16a",
        "gallery": [
            ("1564013799919-ab600027ffc6", "Lavender-lined approach"),
            ("1560448204-e02f11c3d0e2", "Courtyard reception"),
            ("1519741497674-611481863552", "Al fresco dinner"),
        ],
    },
    {
        "name": "Manoir de Bourgogne",
        "slug": "manoir-de-bourgogne",
        "country": "FR",
        "region": "Burgundy",
        "description": (
            "A historic manor house in the heart of Burgundy wine country. Timbered halls, "
            "a vaulted cellar, and vineyard terraces offer a refined, intimate setting for "
            "a celebration steeped in French tradition.\n\n"
            "Wine tastings and cellar tours can be arranged for guests."
        ),
        "capacity": 120,
        "price_from": Decimal("19500.00"),
        "cover": "1570129477492-45c003edd2be",
        "gallery": [
            ("1580587771525-78b9dba3b914", "Timbered great hall"),
            ("1464146072230-91cabc968266", "Vineyard terrace"),
            ("1519167758481-83f550bb49b3", "Evening in the courtyard"),
        ],
    },
    {
        "name": "Villa Toscana Serenita",
        "slug": "villa-toscana-serenita",
        "country": "IT",
        "region": "Tuscany",
        "description": (
            "A classic Tuscan villa perched on rolling hills, with cypress-lined drives, "
            "a frescoed ballroom, and sweeping views over vineyards and olive groves. "
            "The epitome of Italian romance.\n\n"
            "Includes a pool, private chapel, and accommodation for the wedding party."
        ),
        "capacity": 200,
        "price_from": Decimal("32000.00"),
        "cover": "1600607687939-ce8a6c25118c",
        "gallery": [
            ("1542314831-068cd1dbfeeb", "Cypress-lined drive"),
            ("1566073771259-6a8506099945", "Frescoed ballroom"),
            ("1519741497674-611481863552", "Al fresco Tuscan dinner"),
        ],
    },
    {
        "name": "Palazzo del Lago",
        "slug": "palazzo-del-lago",
        "country": "IT",
        "region": "Lake Como",
        "description": (
            "An elegant lakeside palazzo on the shores of Lake Como, with manicured gardens "
            "descending to the water, a marble terrace, and panoramic mountain views. "
            "Arrive by boat for a truly cinematic entrance.\n\n"
            "Private dock, lakeside ceremony, and luxury suites included."
        ),
        "capacity": 160,
        "price_from": Decimal("41000.00"),
        "cover": "1542314831-068cd1dbfeeb",
        "gallery": [
            ("1566073771259-6a8506099945", "Lakeside terrace"),
            ("1600585154340-be6161a56a0c", "Marble reception hall"),
            ("1511285560929-80b456fea0bc", "Sunset over the lake"),
        ],
    },
    {
        "name": "Villa Amalfi Blu",
        "slug": "villa-amalfi-blu",
        "country": "IT",
        "region": "Amalfi Coast",
        "description": (
            "A clifftop villa on the Amalfi Coast with cascading gardens, sea-view terraces, "
            "and a private beach. Bright, airy spaces and endless Mediterranean light make "
            "every moment feel like a celebration.\n\n"
            "Includes private beach access and boat transfers."
        ),
        "capacity": 140,
        "price_from": Decimal("38500.00"),
        "cover": "1566073771259-6a8506099945",
        "gallery": [
            ("1542314831-068cd1dbfeeb", "Clifftop ceremony"),
            ("1600607687939-ce8a6c25118c", "Sea-view reception"),
            ("1519741497674-611481863552", "Mediterranean evening"),
        ],
    },
    {
        "name": "Castello Umbro",
        "slug": "castello-umbro",
        "country": "IT",
        "region": "Umbria",
        "description": (
            "A restored medieval castle in the green heart of Umbria, with stone towers, "
            "a cloistered courtyard, and panoramic views over olive groves and hilltop towns. "
            "Rustic elegance meets timeless history.\n\n"
            "Features a chapel, wine cellar, and accommodation for guests."
        ),
        "capacity": 180,
        "price_from": Decimal("26000.00"),
        "cover": "1570129477492-45c003edd2be",
        "gallery": [
            ("1580587771525-78b9dba3b914", "Medieval courtyard"),
            ("1564013799919-ab600027ffc6", "Hilltop views"),
            ("1519167758481-83f550bb49b3", "Castle at dusk"),
        ],
    },
    {
        "name": "Palacio de Sevilla",
        "slug": "palacio-de-sevilla",
        "country": "ES",
        "region": "Andalusia",
        "description": (
            "A grand Andalusian palace with Moorish arches, tiled courtyards, and orange "
            "groves. Sunlit patios and a rooftop terrace overlooking the city create a "
            "warm, vibrant celebration space.\n\n"
            "Includes flamenco performances and Andalusian cuisine options."
        ),
        "capacity": 250,
        "price_from": Decimal("29500.00"),
        "cover": "1509840841025-9088ba78a826",
        "gallery": [
            ("1598928506311-c55ded91a20c", "Tiled courtyard"),
            ("1600585154340-be6161a56a0c", "Grand salon"),
            ("1519741497674-611481863552", "Rooftop celebration"),
        ],
    },
    {
        "name": "Finca Costa Brava",
        "slug": "finca-costa-brava",
        "country": "ES",
        "region": "Catalonia",
        "description": (
            "A contemporary estate on the Costa Brava with sea views, pine forests, and "
            "modernist architecture. Clean lines, outdoor pools, and sunset terraces suit "
            "a stylish, relaxed celebration.\n\n"
            "Beach access and water sports available for guests."
        ),
        "capacity": 130,
        "price_from": Decimal("24000.00"),
        "cover": "1580587771525-78b9dba3b914",
        "gallery": [
            ("1560448204-e02f11c3d0e2", "Sea-view terrace"),
            ("1600596542815-ffad4c1539a9", "Modernist villa"),
            ("1511285560929-80b456fea0bc", "Costa Brava sunset"),
        ],
    },
    {
        "name": "Castillo de Mallorca",
        "slug": "castillo-de-mallorca",
        "country": "ES",
        "region": "Balearic Islands",
        "description": (
            "A hilltop castle on Mallorca with panoramic Mediterranean views, ancient "
            "stone walls, and lush gardens. A magical setting for a destination wedding "
            "under the Balearic sun.\n\n"
            "Includes accommodation and private event spaces."
        ),
        "capacity": 170,
        "price_from": Decimal("33000.00"),
        "cover": "1560448204-e02f11c3d0e2",
        "gallery": [
            ("1509840841025-9088ba78a826", "Hilltop castle"),
            ("1564013799919-ab600027ffc6", "Garden ceremony"),
            ("1519741497674-611481863552", "Mediterranean evening"),
        ],
    },
    {
        "name": "Hacienda del Sol",
        "slug": "hacienda-del-sol",
        "country": "ES",
        "region": "Andalusia",
        "description": (
            "A sprawling hacienda in the Andalusian countryside with whitewashed walls, "
            "shaded patios, and a courtyard pool. Relaxed, sun-filled, and full of "
            "Spanish character.\n\n"
            "Horseback arrivals and traditional cuisine available."
        ),
        "capacity": 210,
        "price_from": Decimal("27500.00"),
        "cover": "1598928506311-c55ded91a20c",
        "gallery": [
            ("1580587771525-78b9dba3b914", "Courtyard pool"),
            ("1600585154340-be6161a56a0c", "Hacienda salon"),
            ("1511285560929-80b456fea0bc", "Sunset over the estate"),
        ],
    },
]

VEHICLES = [
    {
        "name": "Ferrari 488 Spider",
        "category": "exotic",
        "description": "Open-top Italian exotic with a twin-turbo V8 and breathtaking performance. A dramatic, head-turning arrival.",
        "daily_price": Decimal("2400.00"),
        "image": "https://images.unsplash.com/photo-1544636331-e26879cd4d9b?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Lamborghini Huracan",
        "category": "exotic",
        "description": "Sharp, loud, and unmistakable. A supercar entrance that makes every arrival unforgettable.",
        "daily_price": Decimal("2600.00"),
        "image": "https://images.unsplash.com/photo-1583121274602-3e2820c69888?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "McLaren 720S",
        "category": "exotic",
        "description": "Lightweight British supercar with dihedral doors and extraordinary pace. The ultimate statement arrival.",
        "daily_price": Decimal("2500.00"),
        "image": "https://images.unsplash.com/photo-1502877338535-766e1452684a?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Porsche 911 Turbo S",
        "category": "exotic",
        "description": "Iconic everyday supercar performance with all-weather capability and timeless style.",
        "daily_price": Decimal("1300.00"),
        "image": "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Aston Martin DB11",
        "category": "exotic",
        "description": "Grand touring elegance with a sonorous V12. Refined, romantic, and unmistakably British.",
        "daily_price": Decimal("1900.00"),
        "image": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Rolls-Royce Phantom",
        "category": "limousine",
        "description": "The pinnacle of chauffeur-driven luxury. Whisper-quiet cabin and commanding presence for a grand entrance.",
        "daily_price": Decimal("1850.00"),
        "image": "https://images.unsplash.com/photo-1542362567-b07e54358753?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Mercedes-Maybach S-Class Pullman",
        "category": "limousine",
        "description": "Extended-wheelbase limousine with rear cabin opulence, privacy, and first-class comfort.",
        "daily_price": Decimal("2100.00"),
        "image": "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Cadillac Escalade Stretch Limousine",
        "category": "limousine",
        "description": "Spacious stretch limousine with party lighting and lounge seating for the wedding party.",
        "daily_price": Decimal("1200.00"),
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/8/82/2021_Cadillac_Escalade_stretch_limousine_with_a_gull-wing_door_configuration.jpg/1920px-2021_Cadillac_Escalade_stretch_limousine_with_a_gull-wing_door_configuration.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
    },
    {
        "name": "Lincoln Town Car Stretch Limousine",
        "category": "limousine",
        "description": "Classic stretch limousine with a timeless profile and comfortable, sociable cabin.",
        "daily_price": Decimal("950.00"),
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/6/62/Lincoln_Town_Car_limousine_in_Ukraine_01.jpg/1920px-Lincoln_Town_Car_limousine_in_Ukraine_01.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
    },
    {
        "name": "Hummer H2 Stretch Limousine",
        "category": "limousine",
        "description": "Bold, oversized stretch limousine for a statement arrival and group celebrations.",
        "daily_price": Decimal("1400.00"),
        "image": "https://thumb.wikimedia.org/wikipedia/commons/thumb/c/ce/Hummer_H2_stretched_limousine%2C_Ganzenhoef_rotonde%2C_met_metrostation.jpg/1920px-Hummer_H2_stretched_limousine%2C_Ganzenhoef_rotonde%2C_met_metrostation.jpg?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content=thumbnail",
    },
]



class Command(BaseCommand):
    help = "Populate the catalog with sample venues, images, and luxury vehicles."

    def handle(self, *args, **options):
        venue_count = 0
        for index, data in enumerate(VENUES):
            base = index * 4
            cover_url = CASTLE_IMAGES[base % len(CASTLE_IMAGES)]
            venue, created = Venue.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "country": data["country"],
                    "region": data["region"],
                    "description": data["description"],
                    "capacity": data["capacity"],
                    "price_from": data["price_from"],
                    "cover_image_url": cover_url,
                    "is_published": True,
                },
            )
            venue.images.all().delete()
            for position in range(3):
                image_url = CASTLE_IMAGES[(base + 1 + position) % len(CASTLE_IMAGES)]
                VenueImage.objects.create(
                    venue=venue,
                    image_url=image_url,
                    alt_text=f"{data['name']} photo {position + 1}",
                    position=position,
                )
            venue_count += 1
            self.stdout.write(f"{'Created' if created else 'Updated'} venue: {venue.name}")

        Vehicle.objects.exclude(name__in=[d["name"] for d in VEHICLES]).delete()
        vehicle_count = 0
        for data in VEHICLES:
            vehicle, created = Vehicle.objects.update_or_create(
                name=data["name"],
                defaults={
                    "category": data["category"],
                    "description": data["description"],
                    "daily_price": data["daily_price"],
                    "image_url": data["image"],
                    "is_available": True,
                },
            )
            vehicle_count += 1
            self.stdout.write(f"{'Created' if created else 'Updated'} vehicle: {vehicle.name}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {venue_count} venues and {vehicle_count} vehicles populated."
            )
        )
