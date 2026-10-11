"""Botanical imagery resolved from Wikimedia Commons / Wikipedia.

Generated from the Wikipedia REST/MediaWiki API so every URL points at a real
file with real licence metadata. Regenerate with tools/fetch_plant_images.py.
"""

from __future__ import annotations

PLANT_IMAGERY: dict[str, dict[str, str | None]] = {
    "tomato": {
        "image_url": 'https://thumb.wikimedia.org/wikipedia/commons/thumb/8/89/Tomato_je.jpg/1280px-Tomato_je.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Tomato',
        "image_attribution": 'Softeis',
        "image_license": 'CC BY-SA 3.0',
    },
    "maize": {
        "image_url": 'https://upload.wikimedia.org/wikipedia/commons/e/e3/Zea_mays_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-283.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Maize',
        "image_attribution": "Franz Eugen Köhler, Köhler's Medizinal-Pflanzen",
        "image_license": 'Public domain',
    },
    "bread-wheat": {
        "image_url": 'https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a2/Bl%C3%A9_tendre_%28GRAPELLI%29_AO-5-cliche_Jean_Weber_%285%29_%2823975019962%29.jpg/1280px-Bl%C3%A9_tendre_%28GRAPELLI%29_AO-5-cliche_Jean_Weber_%285%29_%2823975019962%29.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Common_wheat',
        "image_attribution": 'INRA DIST from France',
        "image_license": 'CC BY 2.0',
    },
    "rice": {
        "image_url": 'https://upload.wikimedia.org/wikipedia/commons/0/0a/20201102.Hengnan.Hybrid_rice_Sanyou-1.6.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Rice',
        "image_attribution": 'China News Service',
        "image_license": 'CC BY 3.0',
    },
    "potato": {
        "image_url": 'https://thumb.wikimedia.org/wikipedia/commons/thumb/a/ab/Patates.jpg/1280px-Patates.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Potato',
        "image_attribution": 'Scott Bauer, USDA ARS',
        "image_license": 'Public domain',
    },
    "common-bean": {
        "image_url": 'https://upload.wikimedia.org/wikipedia/commons/c/ca/Snijboon_peulen_Phaseolus_vulgaris.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Phaseolus_vulgaris',
        "image_attribution": 'Rasbak',
        "image_license": 'CC BY-SA 3.0',
    },
    "sunflower": {
        "image_url": 'https://thumb.wikimedia.org/wikipedia/commons/thumb/4/40/Sunflower_sky_backdrop.jpg/1280px-Sunflower_sky_backdrop.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Common_sunflower',
        "image_attribution": 'Fir0002',
        "image_license": 'GFDL 1.2',
    },
    "basil": {
        "image_url": 'https://thumb.wikimedia.org/wikipedia/commons/thumb/9/97/Ocimum_basilicum_8zz.jpg/1280px-Ocimum_basilicum_8zz.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Basil',
        "image_attribution": 'Photo by David J. Stang',
        "image_license": 'CC BY-SA 4.0',
    },
    "lavender": {
        "image_url": 'https://upload.wikimedia.org/wikipedia/commons/4/40/Lavandula_angustifolia_-_K%C3%B6hler%E2%80%93s_Medizinal-Pflanzen-087.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Lavandula_angustifolia',
        "image_attribution": "Franz Eugen Köhler, Köhler's Medizinal-Pflanzen",
        "image_license": 'Public domain',
    },
    "soybean": {
        "image_url": 'https://upload.wikimedia.org/wikipedia/commons/8/82/Soybean.USDA.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Soybean',
        "image_attribution": None,
        "image_license": 'Public domain',
    },
    "carrot": {
        "image_url": 'https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a2/Vegetable-Carrot-Bundle-wStalks.jpg/1280px-Vegetable-Carrot-Bundle-wStalks.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Carrot',
        "image_attribution": 'Evan-Amos',
        "image_license": 'Public domain',
    },
    "apple": {
        "image_url": 'https://thumb.wikimedia.org/wikipedia/commons/thumb/a/a6/Pink_lady_and_cross_section.jpg/1280px-Pink_lady_and_cross_section.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Apple',
        "image_attribution": 'fir0002 flagstaffotos [at] gmail.com Canon 20D + Sigma 150mm f/2.8',
        "image_license": 'GFDL 1.2',
    },
    "arabica-coffee": {
        "image_url": 'https://thumb.wikimedia.org/wikipedia/commons/thumb/c/c7/Coffee_Flowers.JPG/1280px-Coffee_Flowers.JPG',
        "image_source_url": 'https://en.wikipedia.org/wiki/Coffea_arabica',
        "image_attribution": 'Marcelo Corrêa',
        "image_license": 'CC BY-SA 3.0',
    },
    "cucumber": {
        "image_url": 'https://thumb.wikimedia.org/wikipedia/commons/thumb/9/96/ARS_cucumber.jpg/1280px-ARS_cucumber.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Cucumber',
        "image_attribution": 'Stephen Ausmus, USDA ARS',
        "image_license": 'Public domain',
    },
    "lettuce": {
        "image_url": 'https://thumb.wikimedia.org/wikipedia/commons/thumb/d/da/Iceberg_lettuce_in_SB.jpg/1280px-Iceberg_lettuce_in_SB.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Lettuce',
        "image_attribution": 'en:User:Geographer',
        "image_license": 'CC BY 1.0',
    },
    "chickpea": {
        "image_url": 'https://thumb.wikimedia.org/wikipedia/commons/thumb/8/89/Chickpea_BNC.jpg/1280px-Chickpea_BNC.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Chickpea',
        "image_attribution": 'Prathyush Thomas',
        "image_license": 'GFDL 1.2',
    },
    "grape": {
        "image_url": 'https://upload.wikimedia.org/wikipedia/commons/d/dd/Cabernet_Sauvignon_Gaillac.jpg',
        "image_source_url": 'https://en.wikipedia.org/wiki/Vitis_vinifera',
        "image_attribution": None,
        "image_license": 'CC BY-SA 3.0',
    },
}
