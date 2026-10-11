"""Seed dataset: structured plant profiles + documented cultivation regions.

Provenance policy
-----------------
Every requirement range below is compiled from published crop-requirement
references (FAO EcoCrop, USDA PLANTS, RHS growing guides, Feedipedia). They are
*indicative* agronomic envelopes, not guarantees, and each profile carries its
references in ``data_sources`` so the UI can show where a number came from.

Regions describe **documented cultivation**, i.e. places with established
commercial or historically documented production, and are listed with
``evidence_type="documented_cultivation"``. Nothing here is a fabricated farm,
boundary or yield statistic.
"""

from __future__ import annotations

from typing import Any

from app.services.plant_imagery import PLANT_IMAGERY

FAO_ECOCROP: dict[str, str] = {
    "label": "FAO EcoCrop crop requirement database",
    "url": "https://ecocrop.apps.fao.org/ecocrop/srv/en/home",
}
USDA_PLANTS: dict[str, str] = {
    "label": "USDA PLANTS Database",
    "url": "https://plants.usda.gov/",
}
RHS: dict[str, str] = {"label": "RHS growing guides", "url": "https://www.rhs.org.uk/"}
FAOSTAT: dict[str, str] = {
    "label": "FAOSTAT crop production statistics",
    "url": "https://www.fao.org/faostat/en/#data/QCL",
}
FEEDIPEDIA: dict[str, str] = {
    "label": "Feedipedia animal feed resources",
    "url": "https://www.feedipedia.org/",
}

REQUIREMENT_NOTE = (
    "Requirement ranges are compiled from published crop-requirement references "
    "and are indicative. Validate against local trial data before commercial planting."
)
REGION_NOTE = (
    "Listed places are documented cultivation areas (established commercial or "
    "historically recorded production), not a prediction that the crop will "
    "succeed there under current conditions."
)


def _src(*refs: dict[str, str], note: str = REQUIREMENT_NOTE) -> list[dict[str, str]]:
    return [dict(ref) for ref in refs] + [{"label": "Interpretation note", "note": note}]


def _region(
    slug: str,
    name: str,
    country: str,
    country_code: str,
    admin_area: str,
    latitude: float,
    longitude: float,
    description: str,
    climate_note: str,
    rank: int,
) -> dict[str, Any]:
    return {
        "slug": slug,
        "name": name,
        "country": country,
        "country_code": country_code,
        "admin_area": admin_area,
        "latitude": latitude,
        "longitude": longitude,
        "evidence_type": "documented_cultivation",
        "description": description,
        "climate_note": climate_note,
        "rank": rank,
        "data_sources": [dict(FAOSTAT), {"label": "Interpretation note", "note": REGION_NOTE}],
    }


PLANT_SEED: list[dict[str, Any]] = [
    # ------------------------------------------------------------------ 1
    {
        "slug": "tomato",
        "common_name": "Tomato",
        "scientific_name": "Solanum lycopersicum",
        "family": "Solanaceae",
        "short_description": "Warm-season fruiting vegetable grown worldwide, in open fields and under glass.",
        "description": (
            "Tomato is a tender perennial usually cultivated as an annual. It needs a "
            "frost-free growing period, steady warmth for fruit set, and consistent soil "
            "moisture. Fruit set becomes unreliable above roughly 35 C, and plants are "
            "damaged by temperatures near freezing. Most commercial production is "
            "irrigated and often stake- or trellis-supported."
        ),
        "lifecycle": "annual",
        "growth_habit": "herbaceous",
        "difficulty": "beginner",
        "tags": ["full sun", "warm season", "irrigated", "container friendly", "frost sensitive"],
        "temp_min_c": 10.0,
        "temp_max_c": 35.0,
        "temp_optimal_min_c": 18.0,
        "temp_optimal_max_c": 27.0,
        "temperature_notes": "Growth is checked below about 10 C and fruit set fails above about 35 C. Frost is lethal.",
        "frost_tolerance": "none",
        "rainfall_min_mm": 400.0,
        "rainfall_max_mm": 1600.0,
        "rainfall_notes": "Frequently grown under irrigation; even moisture matters more than total rainfall, and wet foliage encourages disease.",
        "soil_ph_min": 5.5,
        "soil_ph_max": 7.5,
        "soil_textures": ["loam", "sandy loam", "silt loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "Fertile, well-drained soil with added organic matter. Waterlogging promotes root disease.",
        "water_requirement": "high",
        "water_notes": "Requires consistent moisture through flowering and fruit development; irregular watering causes fruit cracking and blossom end rot.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Six or more hours of direct sun; more sun in cool climates, some afternoon shade in very hot ones.",
        "growing_season_days_min": 90,
        "growing_season_days_max": 150,
        "growing_season_notes": "From transplanting to first harvest, depending on cultivar.",
        "cultivation_steps": [
            {"order": 1, "title": "Start seed warm", "detail": "Sow 6-8 weeks before the last expected frost at 20-25 C; germination is poor below 15 C."},
            {"order": 2, "title": "Harden off", "detail": "Move seedlings outdoors gradually over 7-10 days once nights stay above about 10 C."},
            {"order": 3, "title": "Prepare the bed", "detail": "Work in compost, confirm drainage, and set plants slightly deeper than they grew in the pot."},
            {"order": 4, "title": "Support and space", "detail": "Stake, cage or trellis, and space to the cultivar's spread to keep airflow around the foliage."},
            {"order": 5, "title": "Water and feed steadily", "detail": "Water deeply and regularly at the base; feed after the first truss sets rather than pushing leaf growth early."},
            {"order": 6, "title": "Harvest on colour", "detail": "Pick at full colour for fresh use, or at first blush if fruit must travel."},
        ],
        "common_problems": [
            {"name": "Late blight", "description": "A water-mould disease that spreads fast in cool, wet weather; remove affected plants promptly."},
            {"name": "Blossom end rot", "description": "A calcium-delivery disorder driven by irregular watering rather than a lack of calcium in the soil."},
            {"name": "Fruit cracking", "description": "Follows heavy watering after a dry spell."},
            {"name": "Hornworm and whitefly", "description": "Common chewing and sap-sucking pests, worse in long warm seasons."},
        ],
        "regions": [
            _region("almeria-spain", "Almería", "Spain", "ESP", "Andalusia", 36.8381, -2.4597, "Europe's largest concentration of protected vegetable production, with tomato grown extensively under plastic greenhouses.", "Semi-arid Mediterranean; production depends on greenhouse climate control and irrigation.", 1),
            _region("puglia-italy", "Puglia", "Italy", "ITA", "Puglia", 41.4620, 15.5446, "Long-established field and protected tomato production, including processing types.", "Hot, dry Mediterranean summers with irrigation from local aquifers.", 2),
            _region("central-valley-usa", "Central Valley, California", "United States", "USA", "California", 36.7378, -119.7871, "Major processing-tomato district with large-scale irrigated field production.", "Mediterranean with very hot, dry summers; entirely dependent on irrigation.", 3),
            _region("kurnool-india", "Kurnool district, Andhra Pradesh", "India", "IND", "Andhra Pradesh", 15.8281, 78.0373, "Significant open-field tomato growing area in southern India.", "Tropical semi-arid, with production timed around the monsoon.", 4),
            _region("weifang-china", "Weifang, Shandong", "China", "CHN", "Shandong", 36.7069, 119.1618, "Intensive vegetable production region and a major tomato supply area.", "Warm continental with cold winters; much production is under cover.", 5),
            _region("culiacan-mexico", "Culiacán, Sinaloa", "Mexico", "MEX", "Sinaloa", 24.8091, -107.3940, "Winter vegetable export district producing tomato for North American markets.", "Hot semi-arid winter growing season, fully irrigated.", 6),
        ],
    },
    # ------------------------------------------------------------------ 2
    {
        "slug": "maize",
        "common_name": "Maize",
        "scientific_name": "Zea mays",
        "family": "Poaceae",
        "short_description": "The world's largest cereal crop by production, grown for grain, fodder and food.",
        "description": (
            "Maize is a warm-season C4 cereal with high heat tolerance and high water demand "
            "during tasselling and grain fill. It is killed by frost at any growth stage and "
            "yield is very sensitive to drought stress around flowering. It is grown from "
            "tropical highlands to temperate latitudes with short-season hybrids."
        ),
        "lifecycle": "annual",
        "growth_habit": "herbaceous",
        "difficulty": "beginner",
        "tags": ["full sun", "cereal", "warm season", "bulk crop", "frost sensitive"],
        "temp_min_c": 10.0,
        "temp_max_c": 40.0,
        "temp_optimal_min_c": 20.0,
        "temp_optimal_max_c": 30.0,
        "temperature_notes": "Germination is very slow below 10 C and stops near 8 C; growth is fastest at 20-30 C.",
        "frost_tolerance": "none",
        "rainfall_min_mm": 500.0,
        "rainfall_max_mm": 800.0,
        "rainfall_notes": "Roughly 500-800 mm is needed in season, with the critical demand around flowering; supplementary irrigation raises yields.",
        "soil_ph_min": 5.5,
        "soil_ph_max": 7.5,
        "soil_textures": ["loam", "sandy loam", "silt loam", "clay loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "Deep, fertile, well-drained soil; it will not tolerate waterlogging, and saline soils depress yield.",
        "water_requirement": "high",
        "water_notes": "Water stress during tasselling and silking causes the largest yield losses.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun; as a C4 crop it converts high light intensity efficiently.",
        "growing_season_days_min": 90,
        "growing_season_days_max": 140,
        "growing_season_notes": "From sowing to grain maturity, varying widely with hybrid and latitude.",
        "cultivation_steps": [
            {"order": 1, "title": "Wait for warm soil", "detail": "Sow only once soil at sowing depth is reliably above 10 C; cold, wet seedbeds cause uneven emergence."},
            {"order": 2, "title": "Prepare a fine seedbed", "detail": "Level and consolidate the seedbed for even sowing depth, which drives even maturity."},
            {"order": 3, "title": "Sow to the right density", "detail": "Row spacing and population depend on hybrid and rainfall; dense stands suffer more in dry years."},
            {"order": 4, "title": "Control early weeds", "detail": "Maize competes poorly with weeds in the first weeks, so early weed control matters most."},
            {"order": 5, "title": "Protect the flowering window", "detail": "Irrigate if possible around tasselling and silking; this is when water stress costs the most yield."},
            {"order": 6, "title": "Harvest at black layer", "detail": "Grain is mature when the kernel black layer forms; dry to a safe storage moisture."},
        ],
        "common_problems": [
            {"name": "Fall armyworm", "description": "Larvae feed in the whorl and can defoliate young plants."},
            {"name": "Stalk and ear rots", "description": "Favoured by wet conditions late in the season and by insect damage."},
            {"name": "Drought at flowering", "description": "The single largest cause of yield loss in rain-fed maize."},
            {"name": "Nutrient deficiency", "description": "Nitrogen shortage in particular shows as pale, V-shaped leaf yellowing."},
        ],
        "regions": [
            _region("iowa-usa", "Iowa", "United States", "USA", "Iowa", 41.8780, -93.0977, "Core of the United States Corn Belt, with very high-yielding rain-fed and irrigated production.", "Continental, with warm humid summers and adequate summer rainfall.", 1),
            _region("mato-grosso-brazil", "Mato Grosso", "Brazil", "BRA", "Mato Grosso", -12.6819, -56.9211, "Brazil's largest maize and soybean producing state, with a second-crop maize system.", "Tropical wet-dry; the second crop relies on residual soil moisture.", 2),
            _region("punjab-india", "Punjab", "India", "IND", "Punjab", 31.1471, 75.3412, "High-productivity irrigated cereal district.", "Semi-arid subtropical, fully irrigated via canal and tube well.", 3),
            _region("free-state-south-africa", "Free State", "South Africa", "ZAF", "Free State", -28.4541, 26.7968, "South Africa's principal maize-producing province.", "Cool highveld with summer rainfall and frequent mid-season dry spells.", 4),
            _region("jilin-china", "Jilin", "China", "CHN", "Jilin", 43.8378, 126.5496, "Part of China's north-east maize belt.", "Cold winters, warm moist summers, single cropping season.", 5),
            _region("jalisco-mexico", "Jalisco", "Mexico", "MEX", "Jalisco", 20.6597, -103.3496, "Maize growing region and part of the crop's centre of origin.", "Subtropical highland with a summer rainy season.", 6),
        ],
    },
    # ------------------------------------------------------------------ 3
    {
        "slug": "bread-wheat",
        "common_name": "Bread wheat",
        "scientific_name": "Triticum aestivum",
        "family": "Poaceae",
        "short_description": "Cool-season cereal that supplies a large share of global calories.",
        "description": (
            "Bread wheat is a cool-season cereal grown as a winter or spring crop. It "
            "tolerates light to moderate frost when dormant or tillering and completes grain "
            "fill best under moderate temperatures with a dry ripening period. Heat above "
            "about 30 C shortens grain fill and reduces quality."
        ),
        "lifecycle": "annual",
        "growth_habit": "herbaceous",
        "difficulty": "intermediate",
        "tags": ["cereal", "cool season", "frost tolerant", "bulk crop", "rain-fed"],
        "temp_min_c": 3.0,
        "temp_max_c": 32.0,
        "temp_optimal_min_c": 15.0,
        "temp_optimal_max_c": 25.0,
        "temperature_notes": "Winter types tolerate hard frost when dormant; grain fill is best at 15-25 C, and heat above about 30 C reduces yield and quality.",
        "frost_tolerance": "moderate",
        "rainfall_min_mm": 350.0,
        "rainfall_max_mm": 900.0,
        "rainfall_notes": "Lower rainfall than most cereals, but moisture at stem extension and flowering is decisive.",
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.5,
        "soil_textures": ["loam", "clay loam", "silt loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "Adaptable across fertile loams and clays; dislikes acidic and waterlogged soils.",
        "water_requirement": "moderate",
        "water_notes": "Rain-fed in humid temperate regions; irrigation is used in drier districts to secure grain fill.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun; long days favour yield in higher latitudes.",
        "growing_season_days_min": 100,
        "growing_season_days_max": 180,
        "growing_season_notes": "Spring types mature fastest; winter types need vernalisation and a longer season.",
        "cultivation_steps": [
            {"order": 1, "title": "Choose winter or spring type", "detail": "Winter types need a cold period to vernalise and are sown in autumn; spring types are sown once soil can be worked."},
            {"order": 2, "title": "Prepare a firm seedbed", "detail": "Consolidate after sowing for good seed-to-soil contact and even establishment."},
            {"order": 3, "title": "Manage nitrogen by growth stage", "detail": "Split nitrogen so the crop has enough for tillering and again for grain protein."},
            {"order": 4, "title": "Watch disease at stem extension", "detail": "Rusts and septoria develop quickly in humid, mild conditions during stem extension."},
            {"order": 5, "title": "Harvest dry", "detail": "Combine grain once it is below safe storage moisture to avoid spoilage."},
        ],
        "common_problems": [
            {"name": "Rust diseases", "description": "Stripe, leaf and stem rusts can cause severe losses and spread on wind."},
            {"name": "Septoria leaf blotch", "description": "Splashes in wet seasons and reduces green leaf area."},
            {"name": "Lodging", "description": "Tall, over-fertilised crops fall over in wind and rain, complicating harvest."},
            {"name": "Heat at grain fill", "description": "Shortens grain fill and reduces grain weight."},
        ],
        "regions": [
            _region("punjab-india-wheat", "Punjab", "India", "IND", "Punjab", 30.9010, 75.8573, "Centre of India's irrigated wheat production and the Green Revolution.", "Semi-arid subtropical, entirely dependent on irrigation for reliable yield.", 1),
            _region("kansas-usa", "Kansas", "United States", "USA", "Kansas", 38.5266, -96.7265, "Major winter wheat producing state in the southern Great Plains.", "Semi-arid continental, with dry summers and unreliable rainfall.", 2),
            _region("saskatchewan-canada", "Saskatchewan", "Canada", "CAN", "Saskatchewan", 52.9399, -106.4509, "Core of Canadian spring wheat production.", "Short, cool growing season with cold winters; rain-fed.", 3),
            _region("beauce-france", "Beauce", "France", "FRA", "Centre-Val de Loire", 48.2000, 1.6000, "Part of the highly productive Paris Basin wheat area.", "Cool temperate with reliable rainfall through grain fill.", 4),
            _region("nsw-australia", "New South Wales", "Australia", "AUS", "New South Wales", -33.5000, 147.0000, "Large-scale rain-fed winter cereal belt.", "Mediterranean to semi-arid with highly variable rainfall.", 5),
        ],
    },
    # ------------------------------------------------------------------ 4
    {
        "slug": "rice",
        "common_name": "Rice",
        "scientific_name": "Oryza sativa",
        "family": "Poaceae",
        "short_description": "Semi-aquatic cereal grown in flooded paddies across tropical and subtropical regions.",
        "description": (
            "Rice is unique among major cereals in tolerating standing water, which is how most "
            "of it is grown. It needs high temperatures for most of the season and large amounts "
            "of water, whether from rainfall or irrigation. Cool temperatures during flowering "
            "cause spikelet sterility and serious yield loss."
        ),
        "lifecycle": "annual",
        "growth_habit": "herbaceous",
        "difficulty": "intermediate",
        "tags": ["cereal", "flooded", "tropical", "high water use", "warm season"],
        "temp_min_c": 15.0,
        "temp_max_c": 40.0,
        "temp_optimal_min_c": 22.0,
        "temp_optimal_max_c": 32.0,
        "temperature_notes": "Growth slows below 15 C, and temperatures under about 18 C at flowering cause sterility.",
        "frost_tolerance": "none",
        "rainfall_min_mm": 1000.0,
        "rainfall_max_mm": 2500.0,
        "rainfall_notes": "Rain-fed lowland rice needs roughly 1000-2500 mm; irrigated rice is grown in much drier climates using diverted or pumped water.",
        "soil_ph_min": 5.5,
        "soil_ph_max": 7.0,
        "soil_textures": ["clay", "clay loam", "silt loam"],
        "soil_drainage": "poor drainage tolerated",
        "soil_notes": "Puddled clay or clay loam holds the water layer; lighter soils lose too much water to seepage.",
        "water_requirement": "high",
        "water_notes": "The most water-demanding major cereal in flooded systems; alternate wetting and drying can reduce use substantially.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun with long days; yields fall under heavy cloud.",
        "growing_season_days_min": 100,
        "growing_season_days_max": 180,
        "growing_season_notes": "From transplanting or direct sowing to harvest, varying by variety and latitude.",
        "cultivation_steps": [
            {"order": 1, "title": "Establish the paddy", "detail": "Level the field and build bunds so the water layer can be held at an even depth."},
            {"order": 2, "title": "Raise or sow", "detail": "Transplant seedlings from a nursery for better weed control, or direct-sow into puddled or dry soil."},
            {"order": 3, "title": "Manage the water layer", "detail": "Keep a shallow flood for most of the season; drain briefly at rooting and before harvest."},
            {"order": 4, "title": "Weed early", "detail": "Weeds compete hardest in the first three weeks while the canopy is open."},
            {"order": 5, "title": "Protect flowering", "detail": "Avoid cold water and cold air at flowering, when the crop is most sensitive."},
            {"order": 6, "title": "Drain and harvest", "detail": "Drain the field to firm the soil so equipment or people can work, then harvest at grain maturity."},
        ],
        "common_problems": [
            {"name": "Rice blast", "description": "A fungal disease causing lesions on leaves and neck rot, worst under high nitrogen and humid conditions."},
            {"name": "Brown planthopper", "description": "Sap-feeding insect that can cause abrupt wilting and yield collapse."},
            {"name": "Stem borer", "description": "Larvae tunnel into stems, producing dead hearts and white heads."},
            {"name": "Cold at flowering", "description": "Causes spikelet sterility and empty panicles."},
        ],
        "regions": [
            _region("mekong-delta-vietnam", "Mekong Delta", "Vietnam", "VNM", "Mekong Delta", 10.0452, 105.7469, "A major export-producing lowland rice system with multiple cropping cycles.", "Tropical monsoon, with flooding driven by both rainfall and the Mekong's hydrology.", 1),
            _region("west-bengal-india", "West Bengal", "India", "IND", "West Bengal", 22.9868, 87.8550, "One of India's largest rice producing states, with monsoon-fed and irrigated paddy.", "Sub-humid tropical monsoon with a pronounced wet season.", 2),
            _region("central-java-indonesia", "Central Java", "Indonesia", "IDN", "Central Java", -7.1510, 110.1403, "Densely cropped paddy landscape with long-established irrigation systems.", "Equatorial monsoon; rice grown year-round where water allows.", 3),
            _region("hunan-china", "Hunan", "China", "CHN", "Hunan", 27.6090, 111.7080, "Major rice producing province with double-cropping in the south.", "Humid subtropical monsoon with hot wet summers.", 4),
            _region("arkansas-usa", "Arkansas", "United States", "USA", "Arkansas", 34.7465, -92.2896, "Leading rice producing state in the United States, grown in flooded paddies.", "Humid subtropical; production fully depends on irrigation from rivers and aquifers.", 5),
            _region("nile-delta-egypt", "Nile Delta", "Egypt", "EGY", "Nile Delta", 30.7997, 31.0000, "Irrigated rice production on the Nile floodplain.", "Hot arid climate; rice is grown only where Nile water is available.", 6),
        ],
    },
    # ------------------------------------------------------------------ 5
    {
        "slug": "potato",
        "common_name": "Potato",
        "scientific_name": "Solanum tuberosum",
        "family": "Solanaceae",
        "short_description": "Temperate tuber crop with the highest yield per hectare of any major staple.",
        "description": (
            "Potato is grown from seed tubers rather than seed. It performs best in cool "
            "climates with moderate moisture: tuber bulking slows sharply above about 25 C. "
            "The haulm is damaged by frost, and warm, humid weather drives late blight, the "
            "disease most associated with crop losses."
        ),
        "lifecycle": "annual",
        "growth_habit": "herbaceous",
        "difficulty": "beginner",
        "tags": ["cool season", "root crop", "frost sensitive", "high yield", "temperate"],
        "temp_min_c": 5.0,
        "temp_max_c": 30.0,
        "temp_optimal_min_c": 15.0,
        "temp_optimal_max_c": 20.0,
        "temperature_notes": "Tuber growth is fastest at 15-20 C and largely stops above about 25 C; frost blackens the haulm.",
        "frost_tolerance": "none",
        "rainfall_min_mm": 400.0,
        "rainfall_max_mm": 800.0,
        "rainfall_notes": "Needs a well-distributed 400-800 mm; dry spells during bulking cut yield, and waterlogging causes rot.",
        "soil_ph_min": 5.0,
        "soil_ph_max": 6.5,
        "soil_textures": ["sandy loam", "loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "Loose, deep, slightly acidic soil produces clean tubers; alkaline soils encourage common scab.",
        "water_requirement": "moderate",
        "water_notes": "Even moisture during tuber bulking matters most; swings between drought and heavy water cause tuber defects.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun; long days promote haulm growth while short days favour tuber initiation in some types.",
        "growing_season_days_min": 70,
        "growing_season_days_max": 140,
        "growing_season_notes": "From planting to maturity; earlies mature in 70-90 days, maincrops longer.",
        "cultivation_steps": [
            {"order": 1, "title": "Choose certified seed tubers", "detail": "Certified seed is the main defence against tuber-borne disease."},
            {"order": 2, "title": "Chit or pre-sprout", "detail": "Sprouting seed tubers before planting advances maturity, useful for early crops."},
            {"order": 3, "title": "Plant into cool soil", "detail": "Plant once soil is workable and above about 7 C, in furrows about 10-15 cm deep."},
            {"order": 4, "title": "Earth up ridges", "detail": "Ridging prevents tubers greening in light and improves drainage."},
            {"order": 5, "title": "Irrigate through bulking", "detail": "Keep the ridge moist during tuber bulking; the crop is most drought-sensitive then."},
            {"order": 6, "title": "Harvest and cure", "detail": "Cut haulm to set skin, then lift and cure tubers before storage."},
        ],
        "common_problems": [
            {"name": "Late blight", "description": "The historic potato disease; spreads explosively in warm, wet weather and destroys foliage within days."},
            {"name": "Potato cyst nematode", "description": "Soil-borne pest that persists for years and stunts roots."},
            {"name": "Common scab", "description": "Surface blemishing that is worse in alkaline, dry soils."},
            {"name": "Colorado potato beetle", "description": "Defoliating beetle with rapid resistance to insecticides."},
        ],
        "regions": [
            _region("prince-edward-island-canada", "Prince Edward Island", "Canada", "CAN", "Prince Edward Island", 46.2382, -63.1311, "Long-established seed and table potato production region.", "Cool maritime; short season with reliable moisture.", 1),
            _region("idaho-usa", "Idaho", "United States", "USA", "Idaho", 43.6150, -116.2023, "Leading United States potato producing state, largely irrigated.", "Semi-arid with cool nights; production depends on irrigation.", 2),
            _region("bavaria-germany", "Bavaria", "Germany", "DEU", "Bavaria", 48.7904, 11.4979, "Important European potato growing area for both table and processing markets.", "Cool temperate with adequate summer rainfall.", 3),
            _region("uttar-pradesh-india", "Uttar Pradesh", "India", "IND", "Uttar Pradesh", 26.8467, 80.9462, "India's largest potato producing state, grown as a cool-season winter crop.", "Subtropical; the crop is grown in the coolest months with irrigation.", 4),
            _region("inner-mongolia-china", "Inner Mongolia", "China", "CHN", "Inner Mongolia", 40.8175, 111.7656, "Rapidly expanded potato production area, including processing types.", "Cold continental with a short, cool growing season.", 5),
            _region("cundinamarca-colombia", "Cundinamarca", "Colombia", "COL", "Cundinamarca", 4.8000, -74.3000, "High-Andean potato production on the tropical altiplano.", "Equatorial but cool because of altitude; grown year-round.", 6),
        ],
    },
    # ------------------------------------------------------------------ 6
    {
        "slug": "common-bean",
        "common_name": "Common bean",
        "scientific_name": "Phaseolus vulgaris",
        "family": "Fabaceae",
        "short_description": "Nitrogen-fixing grain and pod legume grown across temperate and tropical regions.",
        "description": (
            "Common bean is grown for dry grain, fresh pods or shelled beans. It is a short-season "
            "warm-season legume that fixes nitrogen with rhizobia, and it is sensitive to frost, "
            "waterlogging and heat at flowering. Optimum temperatures are moderate, and nights above "
            "roughly 22 C reduce pod set."
        ),
        "lifecycle": "annual",
        "growth_habit": "herbaceous",
        "difficulty": "beginner",
        "tags": ["legume", "nitrogen fixing", "warm season", "short season", "frost sensitive"],
        "temp_min_c": 10.0,
        "temp_max_c": 32.0,
        "temp_optimal_min_c": 18.0,
        "temp_optimal_max_c": 24.0,
        "temperature_notes": "Very sensitive to frost; high night temperatures at flowering reduce pod set.",
        "frost_tolerance": "none",
        "rainfall_min_mm": 400.0,
        "rainfall_max_mm": 800.0,
        "rainfall_notes": "Moderate, well-distributed rainfall; excess causes root rots.",
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.0,
        "soil_textures": ["loam", "sandy loam", "silt loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "Tolerant of poor soils but not of acidity or waterlogging; inoculation helps on first-time ground.",
        "water_requirement": "moderate",
        "water_notes": "Most sensitive to drought at flowering and pod fill.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun; some varieties are sensitive to day length.",
        "growing_season_days_min": 60,
        "growing_season_days_max": 120,
        "growing_season_notes": "Bush types mature fastest; climbing types crop over a longer period.",
        "cultivation_steps": [
            {"order": 1, "title": "Sow after the frosts", "detail": "Sow once soil is above about 12 C; cold, wet soil causes seed rots."},
            {"order": 2, "title": "Inoculate if new ground", "detail": "Treat seed with the appropriate rhizobia strain where beans have not been grown before."},
            {"order": 3, "title": "Space for airflow", "detail": "Avoid dense, damp canopies that encourage foliar disease."},
            {"order": 4, "title": "Water at flowering", "detail": "The crop is most drought-sensitive once flowering starts."},
            {"order": 5, "title": "Harvest by type", "detail": "Pick pods young for fresh use, or leave until the pods dry for grain."},
        ],
        "common_problems": [
            {"name": "Anthracnose and common bacterial blight", "description": "Seed- and splash-borne diseases that mark pods and leaves."},
            {"name": "Root rots", "description": "Encouraged by compacted, wet soil and cool planting conditions."},
            {"name": "Bean rust", "description": "Pustules on leaves in humid conditions."},
            {"name": "Aphids and bean beetles", "description": "Sap-sucking pests that also transmit viruses."},
        ],
        "regions": [
            _region("parana-brazil", "Paraná", "Brazil", "BRA", "Paraná", -24.4870, -51.7900, "Major dry-bean producing state, with multiple cropping seasons.", "Subtropical with summer rainfall; beans often follow another crop.", 1),
            _region("sinaloa-mexico-bean", "Sinaloa", "Mexico", "MEX", "Sinaloa", 25.1721, -107.4795, "Winter dry-bean production for domestic and export markets.", "Hot semi-arid winter season with irrigation.", 2),
            _region("rift-valley-kenya", "Rift Valley", "Kenya", "KEN", "Rift Valley", 0.2827, 36.0000, "Significant bean growing area, often intercropped with maize.", "Highland tropical with bimodal rainfall.", 3),
            _region("maharashtra-india-bean", "Maharashtra", "India", "IND", "Maharashtra", 19.7515, 75.7139, "Major pulse and bean growing state.", "Tropical monsoon, grown largely on residual moisture.", 4),
            _region("michigan-usa", "Michigan", "United States", "USA", "Michigan", 43.3266, -84.5365, "Leading United States dry bean producing state.", "Cool temperate; short-season bush types dominate.", 5),
        ],
    },
    # ------------------------------------------------------------------ 7
    {
        "slug": "sunflower",
        "common_name": "Sunflower",
        "scientific_name": "Helianthus annuus",
        "family": "Asteraceae",
        "short_description": "Oilseed and ornamental crop with deep roots and strong drought tolerance.",
        "description": (
            "Sunflower is a deep-rooted warm-season oilseed that extracts water from well below the "
            "depth most crops reach, which gives it better drought tolerance than maize. It needs a "
            "frost-free season, full sun and reasonably deep soil. Seedlings tolerate light frost, "
            "but flowering and seed fill are damaged by hard frost."
        ),
        "lifecycle": "annual",
        "growth_habit": "herbaceous",
        "difficulty": "beginner",
        "tags": ["oilseed", "full sun", "drought tolerant", "deep rooting", "warm season"],
        "temp_min_c": 6.0,
        "temp_max_c": 38.0,
        "temp_optimal_min_c": 20.0,
        "temp_optimal_max_c": 28.0,
        "temperature_notes": "Seedlings tolerate light frost; germination needs soil above about 8 C.",
        "frost_tolerance": "light",
        "rainfall_min_mm": 300.0,
        "rainfall_max_mm": 800.0,
        "rainfall_notes": "Lower rainfall requirement than most oilseeds because of its deep root system.",
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.5,
        "soil_textures": ["loam", "sandy loam", "silt loam", "clay loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "Deep, well-drained soil allows the taproot to reach subsoil moisture; it dislikes waterlogging.",
        "water_requirement": "moderate",
        "water_notes": "Most critical water demand is from bud formation to flowering.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun; heads track the sun while young and face east at maturity.",
        "growing_season_days_min": 90,
        "growing_season_days_max": 140,
        "growing_season_notes": "From sowing to seed maturity, depending on hybrid.",
        "cultivation_steps": [
            {"order": 1, "title": "Sow shallow into warm soil", "detail": "Sow 3-5 cm deep once soil is above about 8 C; deeper sowing delays establishment."},
            {"order": 2, "title": "Thin to a stand", "detail": "Sunflowers do not compensate well for crowding, so thin to the target population early."},
            {"order": 3, "title": "Control weeds before canopy closure", "detail": "Early weed competition is the main yield risk for a slow-establishing crop."},
            {"order": 4, "title": "Irrigate at bud and flower", "detail": "Water stress between bud formation and flowering costs the most yield."},
            {"order": 5, "title": "Protect heads from birds", "detail": "As seed fills, heads become attractive to birds and may need protection."},
            {"order": 6, "title": "Harvest at correct moisture", "detail": "Harvest when the back of the head has browned and seed moisture is safe for storage."},
        ],
        "common_problems": [
            {"name": "Downy mildew", "description": "Soil-borne disease that stunts seedlings in cool, wet conditions."},
            {"name": "Sclerotinia head rot", "description": "Persists in soil for years and rots heads in wet seasons."},
            {"name": "Bird damage", "description": "Significant where large flocks feed on maturing heads."},
            {"name": "Stem lodging", "description": "Tall heads in wind, especially after high nitrogen."},
        ],
        "regions": [
            _region("southern-ukraine", "Southern Ukraine", "Ukraine", "UKR", "Southern Ukraine", 47.0000, 33.0000, "Among the largest sunflower producing areas in the world.", "Continental steppe with hot dry summers; deep soils hold moisture.", 1),
            _region("krasnodar-russia", "Krasnodar Krai", "Russia", "RUS", "Krasnodar Krai", 45.0355, 38.9753, "Major sunflower production district in southern Russia.", "Warm continental with adequate summer warmth.", 2),
            _region("buenos-aires-argentina", "Buenos Aires Province", "Argentina", "ARG", "Buenos Aires", -36.6769, -60.5583, "Core of Argentine sunflower production.", "Temperate humid to sub-humid pampas.", 3),
            _region("constanta-romania", "Constanța", "Romania", "ROU", "Constanța", 44.1598, 28.6348, "Sunflower producing region on the Black Sea coast.", "Warm, dry summers suited to the crop.", 4),
            _region("inner-mongolia-sunflower", "Inner Mongolia", "China", "CHN", "Inner Mongolia", 40.8175, 111.7656, "Large and expanding oilseed sunflower area.", "Cold continental with a short warm season.", 5),
        ],
    },
    # ------------------------------------------------------------------ 8
    {
        "slug": "basil",
        "common_name": "Basil",
        "scientific_name": "Ocimum basilicum",
        "family": "Lamiaceae",
        "short_description": "Fast-growing warm-season culinary herb harvested repeatedly through the season.",
        "description": (
            "Basil is a tender annual herb grown for fresh leaf. It grows very fast in warm weather "
            "and is extremely frost-sensitive: even a brief cold spell causes blackening and leaf "
            "loss. It is usually irrigated and grown in a warm, sunny position, and repeated "
            "harvesting of growing tips keeps plants productive."
        ),
        "lifecycle": "annual",
        "growth_habit": "herbaceous",
        "difficulty": "beginner",
        "tags": ["herb", "warm season", "container friendly", "frost sensitive", "irrigated"],
        "temp_min_c": 12.0,
        "temp_max_c": 35.0,
        "temp_optimal_min_c": 20.0,
        "temp_optimal_max_c": 30.0,
        "temperature_notes": "Growth stalls below about 12 C and plants are damaged by any frost.",
        "frost_tolerance": "none",
        "rainfall_min_mm": 400.0,
        "rainfall_max_mm": 1000.0,
        "rainfall_notes": "Usually irrigated; the fresh-leaf crop has little stored water reserve.",
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.5,
        "soil_textures": ["loam", "sandy loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "Light, fertile, well-drained soil; it dislikes sitting wet.",
        "water_requirement": "moderate",
        "water_notes": "Keep evenly moist; wilting reduces leaf quality quickly.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun; some afternoon shade helps in very hot climates.",
        "growing_season_days_min": 60,
        "growing_season_days_max": 90,
        "growing_season_notes": "From sowing to first harvest; cutting starts earlier than seed production.",
        "cultivation_steps": [
            {"order": 1, "title": "Sow warm", "detail": "Sow at 20-25 C; germination is slow and unreliable in cold soil."},
            {"order": 2, "title": "Transplant after frost risk ends", "detail": "Basil will be killed by the first cold night, so wait until nights are reliably warm."},
            {"order": 3, "title": "Pinch out the tips", "detail": "Removing the growing tip stops early flowering and promotes branching for repeated cuts."},
            {"order": 4, "title": "Harvest regularly", "detail": "Frequent cutting maintains quality; leaving flower spikes reduces leaf production."},
            {"order": 5, "title": "Keep watering consistent", "detail": "Drought stress causes early flowering and tough leaves."},
        ],
        "common_problems": [
            {"name": "Downy mildew", "description": "Yellowing between veins followed by grey sporulation on the leaf underside; devastating in humid crops."},
            {"name": "Cold damage", "description": "Blackening and necrosis from a single cold night."},
            {"name": "Early flowering", "description": "Triggered by stress or long days, reducing leaf yield."},
            {"name": "Fusarium wilt", "description": "Soil-borne wilt that persists in the soil."},
        ],
        "regions": [
            _region("liguria-italy", "Liguria", "Italy", "ITA", "Liguria", 44.4056, 8.9463, "Home of Genoese pesto production and distinctive basil cultivars.", "Mild Mediterranean; production largely on terraced coastal slopes.", 1),
            _region("provence-france", "Provence", "France", "FRA", "Provence-Alpes-Côte d'Azur", 43.9352, 5.0470, "Mediterranean herb growing area with established aromatic crop production.", "Hot dry Mediterranean summers with irrigation.", 2),
            _region("tamil-nadu-india", "Tamil Nadu", "India", "IND", "Tamil Nadu", 11.1271, 78.6569, "Significant area for Ocimum species grown as culinary and medicinal herbs.", "Tropical monsoon; grown across most of the year with irrigation.", 3),
            _region("thailand-tha", "Central Thailand", "Thailand", "THA", "Central Thailand", 14.0188, 100.3143, "Humid tropical herb and vegetable production area.", "Tropical monsoon with high humidity throughout the year.", 4),
        ],
    },
    # ------------------------------------------------------------------ 9
    {
        "slug": "lavender",
        "common_name": "English lavender",
        "scientific_name": "Lavandula angustifolia",
        "family": "Lamiaceae",
        "short_description": "Hardy, drought-tolerant subshrub grown for essential oil and ornamental use.",
        "description": (
            "English lavender is a woody perennial that wants dry, sunny summers and sharply "
            "drained, low-fertility soil. It is one of the most cold-hardy lavender species but "
            "fails quickly in heavy or waterlogged ground, especially in winter. Summer humidity "
            "and wet foliage encourage root and shoot diseases."
        ),
        "lifecycle": "perennial",
        "growth_habit": "subshrub",
        "difficulty": "intermediate",
        "tags": ["perennial", "herb", "drought tolerant", "full sun", "well-drained"],
        "temp_min_c": -15.0,
        "temp_max_c": 35.0,
        "temp_optimal_min_c": 15.0,
        "temp_optimal_max_c": 28.0,
        "temperature_notes": "Established plants tolerate hard winter frost; the crop fails on wet winter soil rather than cold alone.",
        "frost_tolerance": "high",
        "rainfall_min_mm": 300.0,
        "rainfall_max_mm": 800.0,
        "rainfall_notes": "Prefers dry climates; yields and oil quality fall in humid, high-rainfall areas.",
        "soil_ph_min": 6.5,
        "soil_ph_max": 7.8,
        "soil_textures": ["sandy", "sandy loam", "gravelly"],
        "soil_drainage": "sharply drained",
        "soil_notes": "Lean, gritty, alkaline soil. Rich or waterlogged soil shortens the plant's life.",
        "water_requirement": "low",
        "water_notes": "Drought tolerant once established; overwatering is the commonest cause of failure.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun is essential for flower and oil production.",
        "growing_season_days_min": None,
        "growing_season_days_max": None,
        "growing_season_notes": "A woody perennial: flowers from the second year and lives for many years with annual pruning.",
        "cultivation_steps": [
            {"order": 1, "title": "Plant into free-draining ground", "detail": "Add grit to heavy soils or plant on a raised ridge; drainage matters more than fertility."},
            {"order": 2, "title": "Keep it lean", "detail": "Avoid rich manures and high-nitrogen feeds, which produce soft growth prone to disease."},
            {"order": 3, "title": "Prune after flowering", "detail": "Cut back the flowering stems without cutting into bare old wood, which may not regrow."},
            {"order": 4, "title": "Water sparingly", "detail": "Water only to establish; mature plants dislike summer irrigation."},
            {"order": 5, "title": "Harvest at peak flowering", "detail": "Cut stems for oil when about half the florets are open."},
        ],
        "common_problems": [
            {"name": "Phytophthora root rot", "description": "The main killer in wet or heavy soil, especially over winter."},
            {"name": "Lavender shab", "description": "A bacterial disease, spread by sap-feeding insects, that kills branches."},
            {"name": "Winter wet", "description": "More damaging than winter cold in most gardens."},
            {"name": "Leggy unpruned plants", "description": "Woody stems that are cut into bare wood rarely regenerate."},
        ],
        "regions": [
            _region("provence-lavender", "Provence", "France", "FRA", "Provence-Alpes-Côte d'Azur", 43.9352, 5.0470, "Best-known lavender growing area in the world, on calcareous upland plateaux.", "Dry Mediterranean summers on thin, stony limestone soils.", 1),
            _region("bulgaria-lavender", "Rose Valley and Dobrudzha", "Bulgaria", "BGR", "Dobrich", 43.5700, 27.8300, "The largest lavender oil producing country, with extensive field plantings.", "Warm continental with dry summers and cold winters.", 2),
            _region("tasmania-australia", "Tasmania", "Australia", "AUS", "Tasmania", -42.0409, 147.2318, "Australian lavender production region with cool, dry summers.", "Cool temperate, drier than mainland Australia.", 3),
            _region("norfolk-england", "Norfolk", "United Kingdom", "GBR", "Norfolk", 52.6309, 1.2974, "Long-established lavender growing area in eastern England.", "Cool, relatively dry rainshadow with light soils.", 4),
        ],
    },
    # ------------------------------------------------------------------ 10
    {
        "slug": "soybean",
        "common_name": "Soybean",
        "scientific_name": "Glycine max",
        "family": "Fabaceae",
        "short_description": "Oil and protein legume with strong nitrogen fixation and wide adaptation.",
        "description": (
            "Soybean is a short-day legume grown for oil and protein meal. It fixes nitrogen "
            "effectively, needs warm soil to establish, and is sensitive to day length, which "
            "restricts cultivars to fairly narrow latitude bands. Frost kills the crop and water "
            "stress during pod fill reduces both yield and seed size."
        ),
        "lifecycle": "annual",
        "growth_habit": "herbaceous",
        "difficulty": "intermediate",
        "tags": ["legume", "oilseed", "nitrogen fixing", "warm season", "short day"],
        "temp_min_c": 10.0,
        "temp_max_c": 38.0,
        "temp_optimal_min_c": 20.0,
        "temp_optimal_max_c": 30.0,
        "temperature_notes": "Germination is poor below 10 C; cultivars are matched to latitude because of day-length sensitivity.",
        "frost_tolerance": "none",
        "rainfall_min_mm": 450.0,
        "rainfall_max_mm": 900.0,
        "rainfall_notes": "Needs about 450-900 mm in season, with peak demand during pod fill.",
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.0,
        "soil_textures": ["loam", "silt loam", "clay loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "Tolerates a wide range of soils but not salinity, acidity or waterlogging; inoculation helps on new ground.",
        "water_requirement": "moderate",
        "water_notes": "Most sensitive from flowering through pod fill.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun; flowering responds to day length, so planting date is a key decision.",
        "growing_season_days_min": 90,
        "growing_season_days_max": 150,
        "growing_season_notes": "Maturity group determines the season length; frost must be avoided until pods are filled.",
        "cultivation_steps": [
            {"order": 1, "title": "Match maturity group to latitude", "detail": "Choosing a cultivar from the wrong latitude band risks frost damage or poor pod fill."},
            {"order": 2, "title": "Sow into warm soil", "detail": "Wait for about 12 C at sowing depth; cold, saturated soil causes poor emergence."},
            {"order": 3, "title": "Inoculate seed on new ground", "detail": "Soybean-specific rhizobia may be absent where the crop has not been grown."},
            {"order": 4, "title": "Manage weeds early", "detail": "The canopy closes late, so early weed control protects yield."},
            {"order": 5, "title": "Irrigate during pod fill", "detail": "Water stress while seeds are filling reduces seed size and yield."},
            {"order": 6, "title": "Harvest at low moisture", "detail": "Combine once seed moisture is safe, since pods shatter when very dry."},
        ],
        "common_problems": [
            {"name": "Soybean rust", "description": "Wind-borne fungal disease that defoliates the canopy."},
            {"name": "Soybean cyst nematode", "description": "Soil pest that persists for years and suppresses yield with few visible symptoms."},
            {"name": "Sudden death syndrome", "description": "Soil-borne pathogen favoured by cool, wet conditions early and stress later."},
            {"name": "Aphids", "description": "Can build to damaging populations during pod fill."},
        ],
        "regions": [
            _region("mato-grosso-soy", "Mato Grosso", "Brazil", "BRA", "Mato Grosso", -12.6819, -56.9211, "Largest soybean producing state in Brazil and a global supply centre.", "Tropical wet-dry with a pronounced dry season at harvest.", 1),
            _region("iowa-soy", "Iowa", "United States", "USA", "Iowa", 41.8780, -93.0977, "Leading United States soybean producing state, largely rain-fed.", "Continental with warm, moist summers.", 2),
            _region("buenos-aires-soy", "Buenos Aires Province", "Argentina", "ARG", "Buenos Aires", -36.6769, -60.5583, "Core of the Argentine soybean and crushing complex.", "Temperate sub-humid pampas.", 3),
            _region("heilongjiang-china", "Heilongjiang", "China", "CHN", "Heilongjiang", 47.3530, 127.0000, "China's principal soybean producing province.", "Cold continental with a short growing season.", 4),
            _region("madhya-pradesh-soy", "Madhya Pradesh", "India", "IND", "Madhya Pradesh", 22.9734, 78.6569, "India's largest soybean producing state, grown on monsoon rainfall.", "Tropical monsoon; rain-fed and highly rainfall dependent.", 5),
        ],
    },
    # ------------------------------------------------------------------ 11
    {
        "slug": "carrot",
        "common_name": "Carrot",
        "scientific_name": "Daucus carota",
        "family": "Apiaceae",
        "short_description": "Cool-season root vegetable that needs deep, stone-free soil for straight roots.",
        "description": (
            "Carrot is a biennial grown as an annual for its taproot. It wants cool, moist "
            "conditions and, above all, a deep, fine, stone-free seedbed: clods and stones cause "
            "forked and split roots. It is relatively frost-hardy for a root crop, and quality "
            "falls when the crop experiences heat or drought."
        ),
        "lifecycle": "biennial",
        "growth_habit": "herbaceous",
        "difficulty": "beginner",
        "tags": ["root crop", "cool season", "deep soil", "short season", "half hardy"],
        "temp_min_c": 5.0,
        "temp_max_c": 30.0,
        "temp_optimal_min_c": 15.0,
        "temp_optimal_max_c": 21.0,
        "temperature_notes": "Cool temperatures give the best roots; above about 25 C growth slows and flavour sharpens.",
        "frost_tolerance": "light",
        "rainfall_min_mm": 350.0,
        "rainfall_max_mm": 800.0,
        "rainfall_notes": "Even moisture prevents splitting; the crop is often grown under irrigation.",
        "soil_ph_min": 6.0,
        "soil_ph_max": 6.8,
        "soil_textures": ["sandy loam", "loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "Deep, stone-free and low in fresh manure, which causes root forking.",
        "water_requirement": "moderate",
        "water_notes": "Irregular watering after a dry spell splits the roots, so keep moisture even.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun is best, though partial shade is tolerated.",
        "growing_season_days_min": 70,
        "growing_season_days_max": 120,
        "growing_season_notes": "From sowing to harvest, varying with the cultivar's root size.",
        "cultivation_steps": [
            {"order": 1, "title": "Prepare a deep, fine tilth", "detail": "Break up the top 30 cm and remove stones; this is the single biggest factor in root quality."},
            {"order": 2, "title": "Sow thinly and evenly", "detail": "Sow at 1-2 cm depth, then thin seedlings to the final spacing to avoid forked roots."},
            {"order": 3, "title": "Control weeds early", "detail": "Carrot seedlings are slow and easily swamped."},
            {"order": 4, "title": "Keep moisture even", "detail": "Water consistently; swings cause cracking."},
            {"order": 5, "title": "Harvest on size", "detail": "Lift before the roots become woody; frosted ground makes later lifting difficult."},
        ],
        "common_problems": [
            {"name": "Carrot fly", "description": "Root damage from larvae; barrier methods and resistant cultivars help."},
            {"name": "Forked and split roots", "description": "Caused by stones, clods, fresh manure and uneven watering."},
            {"name": "Alternaria leaf blight", "description": "Foliar disease favoured by warm, wet conditions."},
            {"name": "Bolting", "description": "Cold snaps after sowing induce flowering and ruin root quality."},
        ],
        "regions": [
            _region("california-carrot", "Central Valley, California", "United States", "USA", "California", 35.3733, -119.0187, "Very large-scale irrigated carrot production, including fresh and processing markets.", "Semi-arid with irrigation and a long growing window.", 1),
            _region("punjab-india-carrot", "Punjab", "India", "IND", "Punjab", 31.1471, 75.3412, "Cool-season carrot production on irrigated land.", "Subtropical; carrots are grown in the cooler months.", 2),
            _region("shandong-china-carrot", "Shandong", "China", "CHN", "Shandong", 36.6683, 117.9970, "Major vegetable producing region with substantial carrot output.", "Warm continental with cold winters; spring and autumn crops dominate.", 3),
            _region("aquitaine-france", "Nouvelle-Aquitaine", "France", "FRA", "Nouvelle-Aquitaine", 44.8378, -0.5792, "French vegetable growing region with sandy soils suited to root crops.", "Temperate maritime with reliable rainfall.", 4),
            _region("cambridgeshire-uk", "Cambridgeshire", "United Kingdom", "GBR", "Cambridgeshire", 52.2053, 0.1218, "Root vegetable production on light fenland soils.", "Cool temperate; rain-fed with irrigation available.", 5),
        ],
    },
    # ------------------------------------------------------------------ 12
    {
        "slug": "apple",
        "common_name": "Apple",
        "scientific_name": "Malus domestica",
        "family": "Rosaceae",
        "short_description": "Temperate perennial fruit tree that requires winter chill to crop reliably.",
        "description": (
            "Apple is a long-lived temperate tree crop. Most cultivars need a period of winter "
            "chill to break dormancy and flower evenly, which is why apples are grown mainly in "
            "temperate latitudes and at altitude in the tropics. Trees are very cold-hardy when "
            "dormant but frost during bloom destroys the crop."
        ),
        "lifecycle": "perennial",
        "growth_habit": "tree",
        "difficulty": "intermediate",
        "tags": ["perennial", "fruit", "temperate", "winter chill", "trees"],
        "temp_min_c": -30.0,
        "temp_max_c": 35.0,
        "temp_optimal_min_c": 18.0,
        "temp_optimal_max_c": 24.0,
        "temperature_notes": "Dormant trees survive severe cold; frost at flowering, and insufficient winter chill in warm climates, are the practical limits.",
        "frost_tolerance": "high",
        "rainfall_min_mm": 600.0,
        "rainfall_max_mm": 1200.0,
        "rainfall_notes": "Well-distributed rainfall suits apples; irrigation is used where summers are dry.",
        "soil_ph_min": 5.5,
        "soil_ph_max": 7.0,
        "soil_textures": ["loam", "sandy loam", "clay loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "Deep, well-drained soil; trees will not tolerate waterlogging, which causes collar rot.",
        "water_requirement": "moderate",
        "water_notes": "Most critical from bloom through fruit swell; dry spells reduce fruit size.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun for good flowering and fruit colour.",
        "growing_season_days_min": 100,
        "growing_season_days_max": 200,
        "growing_season_notes": "Fruit development from bloom to harvest; a young tree takes several years to crop.",
        "cultivation_steps": [
            {"order": 1, "title": "Check the winter chill", "detail": "Most cultivars need a cold dormancy period; warm climates require low-chill cultivars."},
            {"order": 2, "title": "Plant a compatible pollinator", "detail": "Most apples are not self-fertile and need a different cultivar flowering at the same time."},
            {"order": 3, "title": "Plant bare-root in dormancy", "detail": "Plant in winter into well-drained soil, keeping the graft union above soil level."},
            {"order": 4, "title": "Train and prune annually", "detail": "An open-centred framework improves light penetration and fruit quality."},
            {"order": 5, "title": "Thin the fruit", "detail": "Thinning after the June drop improves the size and quality of the remaining fruit."},
            {"order": 6, "title": "Harvest by ripeness test", "detail": "Judge ripeness by skin colour, ease of picking and pip colour rather than the calendar."},
        ],
        "common_problems": [
            {"name": "Apple scab", "description": "The most important foliar and fruit disease in wet climates; overwinters in fallen leaves."},
            {"name": "Codling moth", "description": "Larvae tunnel into the fruit; control relies on well-timed intervention."},
            {"name": "Fire blight", "description": "Bacterial disease favoured by warm, wet bloom weather."},
            {"name": "Winter chill shortfall", "description": "Poor, erratic flowering where winters are too warm."},
        ],
        "regions": [
            _region("shaanxi-china-apple", "Shaanxi", "China", "CHN", "Shaanxi", 34.3416, 108.9398, "Central to China's very large apple production on the Loess Plateau.", "High-altitude temperate with cold winters and dry, sunny summers.", 1),
            _region("washington-usa-apple", "Washington State", "United States", "USA", "Washington", 46.6000, -120.5000, "Leading United States apple producing state, in an irrigated semi-desert.", "Semi-arid with cold winters and cool nights; fully irrigated.", 2),
            _region("himachal-india-apple", "Himachal Pradesh", "India", "IND", "Himachal Pradesh", 31.1048, 77.1734, "Himalayan apple belt where altitude supplies the needed winter chill.", "Cool highland with a distinct winter; low-latitude but high-altitude climate.", 3),
            _region("aomori-japan-apple", "Aomori", "Japan", "JPN", "Aomori", 40.8222, 140.7474, "Japanese apple production region known for careful orchard management.", "Cool temperate with heavy winter snow.", 4),
            _region("rio-negro-argentina", "Río Negro", "Argentina", "ARG", "Río Negro", -39.0333, -67.5833, "Southern hemisphere apple production district in Patagonia.", "Cool, dry and windy temperate climate.", 5),
            _region("south-tyrol-italy", "South Tyrol", "Italy", "ITA", "South Tyrol", 46.4983, 11.3548, "One of Europe's most intensively managed apple districts.", "Alpine valley with cool nights and good sunshine.", 6),
        ],
    },
    # ------------------------------------------------------------------ 13
    {
        "slug": "arabica-coffee",
        "common_name": "Arabica coffee",
        "scientific_name": "Coffea arabica",
        "family": "Rubiaceae",
        "short_description": "High-value perennial beverage crop of cool tropical highlands.",
        "description": (
            "Arabica coffee is grown at altitude in the tropics, where temperatures stay close to "
            "the 15-24 C it prefers. It is sensitive to frost, to heat above roughly 30 C, and to "
            "long dry spells, yet it also needs a pronounced dry period to ripen and process the "
            "crop. Quality is closely tied to elevation and to slow, even cherry development."
        ),
        "lifecycle": "perennial",
        "growth_habit": "shrub",
        "difficulty": "advanced",
        "tags": ["perennial", "beverage crop", "tropical highland", "shade grown", "frost sensitive"],
        "temp_min_c": 5.0,
        "temp_max_c": 30.0,
        "temp_optimal_min_c": 15.0,
        "temp_optimal_max_c": 24.0,
        "temperature_notes": "Frost causes serious damage; sustained temperatures above about 30 C stress the plant and reduce quality.",
        "frost_tolerance": "none",
        "rainfall_min_mm": 1200.0,
        "rainfall_max_mm": 2200.0,
        "rainfall_notes": "Needs 1200-2200 mm with a drier period for flowering and harvest.",
        "soil_ph_min": 5.5,
        "soil_ph_max": 6.5,
        "soil_textures": ["loam", "sandy loam", "volcanic loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "Deep, well-drained, slightly acidic soils, often volcanic; poor drainage causes root disease.",
        "water_requirement": "high",
        "water_notes": "Evenly distributed rainfall is ideal; irrigation is used in districts with a marked dry season.",
        "sunlight_requirement": "partial_shade",
        "sunlight_hours_min": 4.0,
        "sunlight_notes": "Traditionally grown under shade trees; full sun is possible with high inputs and irrigation.",
        "growing_season_days_min": None,
        "growing_season_days_max": None,
        "growing_season_notes": "A perennial bush that begins bearing about three to four years after planting, with fruit taking six to nine months to ripen.",
        "cultivation_steps": [
            {"order": 1, "title": "Choose an altitude band", "detail": "Site selection by elevation drives both the temperature regime and cup quality."},
            {"order": 2, "title": "Raise or buy healthy seedlings", "detail": "Use resistant cultivars where leaf rust is a known problem."},
            {"order": 3, "title": "Plant with shade and wind protection", "detail": "Shade trees moderate temperature extremes and wind; they also add organic matter."},
            {"order": 4, "title": "Manage soil and mulch", "detail": "Keep a mulch layer and control erosion on sloping ground."},
            {"order": 5, "title": "Prune and feed", "detail": "Remove unproductive wood and replace nutrients removed with the crop."},
            {"order": 6, "title": "Harvest selectively", "detail": "Pick ripe cherries only; selective picking is a major determinant of cup quality."},
        ],
        "common_problems": [
            {"name": "Coffee leaf rust", "description": "Fungal disease that defoliates bushes and has caused major losses across producing regions."},
            {"name": "Coffee berry borer", "description": "A beetle that bores into the cherry and damages the bean."},
            {"name": "Frost", "description": "A single frost can kill limbs or whole bushes in marginal areas."},
            {"name": "Heat and drought stress", "description": "Causes flower abortion and poor cherry fill; a growing concern in warming highlands."},
        ],
        "regions": [
            _region("huila-colombia", "Huila", "Colombia", "COL", "Huila", 2.5359, -75.5277, "Colombia's most productive coffee department, on Andean slopes.", "Equatorial highland: near-constant day length, cool at altitude, bimodal rainfall.", 1),
            _region("minas-gerais-brazil", "Minas Gerais", "Brazil", "BRA", "Minas Gerais", -18.5122, -44.5550, "Brazil's largest coffee producing state.", "Tropical highland with a distinct dry winter for harvesting and processing.", 2),
            _region("yirgacheffe-ethiopia", "Gedeo Zone (Yirgacheffe)", "Ethiopia", "ETH", "Southern Nations", 6.1630, 38.2000, "Part of the crop's centre of origin, with forest coffee and washed specialty production.", "Tropical highland with a long wet season and a short dry spell.", 3),
            _region("nyeri-kenya", "Nyeri", "Kenya", "KEN", "Nyeri", -0.4201, 36.9476, "Kenyan highland district producing washed arabica on volcanic soils.", "Equatorial highland with two rainy seasons and cool nights.", 4),
            _region("antigua-guatemala", "Antigua", "Guatemala", "GTM", "Sacatepéquez", 14.5586, -90.7295, "Volcanic highland coffee district with a marked dry season.", "Tropical highland with a pronounced dry season during harvest.", 5),
            _region("sumatra-indonesia", "Sumatra", "Indonesia", "IDN", "North Sumatra", 2.5000, 98.5000, "Wet-hulled arabica production on volcanic highland.", "Equatorial, very humid, with afternoon cloud cover acting as natural shade.", 6),
        ],
    },
    # ------------------------------------------------------------------ 14
    {
        "slug": "cucumber",
        "common_name": "Cucumber",
        "scientific_name": "Cucumis sativus",
        "family": "Cucurbitaceae",
        "short_description": "Fast, high-water vine crop grown in fields and extensively under cover.",
        "description": (
            "Cucumber is a fast-growing warm-season vine with a short time to harvest. It requires "
            "warmth, steady moisture and high light, and it is intolerant of frost and of cold, wet "
            "roots. In humid field conditions, downy and powdery mildews are the dominant production "
            "constraints, and much commercial production is grown under cover for control."
        ),
        "lifecycle": "annual",
        "growth_habit": "vine",
        "difficulty": "beginner",
        "tags": ["warm season", "vine", "high water use", "frost sensitive", "container friendly"],
        "temp_min_c": 12.0,
        "temp_max_c": 35.0,
        "temp_optimal_min_c": 20.0,
        "temp_optimal_max_c": 30.0,
        "temperature_notes": "Growth stops in cold conditions below about 12 C and the crop is killed by frost.",
        "frost_tolerance": "none",
        "rainfall_min_mm": 400.0,
        "rainfall_max_mm": 1000.0,
        "rainfall_notes": "Requires consistent moisture; the crop has shallow roots and little drought tolerance.",
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.0,
        "soil_textures": ["loam", "sandy loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "Fertile, well-drained soil rich in organic matter; cold, wet soil causes root diseases.",
        "water_requirement": "high",
        "water_notes": "Frequent irrigation keeps fruit tender; water stress causes bitter, misshapen fruit.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun; reflected light under cover improves yields.",
        "growing_season_days_min": 50,
        "growing_season_days_max": 80,
        "growing_season_notes": "From sowing or transplanting to first harvest, making it one of the fastest field crops.",
        "cultivation_steps": [
            {"order": 1, "title": "Sow or transplant when warm", "detail": "Wait until soil is above about 15 C; cold soil causes seed and root rots."},
            {"order": 2, "title": "Provide support or space", "detail": "Trellising keeps fruit clean and greatly improves airflow and disease control."},
            {"order": 3, "title": "Water little and often", "detail": "Shallow roots make frequent, moderate watering better than rare heavy soaking."},
            {"order": 4, "title": "Harvest young and often", "detail": "Frequent picking of young fruit keeps the plant producing."},
            {"order": 5, "title": "Watch for mildew", "detail": "Maintain airflow and remove diseased leaves early; humid conditions favour both mildews."},
        ],
        "common_problems": [
            {"name": "Downy mildew", "description": "Angular yellow leaf spots followed by rapid defoliation in humid crops."},
            {"name": "Powdery mildew", "description": "White fungal growth on leaves, common in warm dry days with cool humid nights."},
            {"name": "Cucumber beetles", "description": "Feeding damage and transmission of bacterial wilt."},
            {"name": "Bitter fruit", "description": "Triggered by water stress, high temperatures or uneven nutrition."},
        ],
        "regions": [
            _region("shandong-china-cucumber", "Shandong", "China", "CHN", "Shandong", 36.7069, 119.1618, "Major cucumber producing province with extensive protected cultivation.", "Warm continental; winter production is under glass or plastic.", 1),
            _region("almeria-spain-cucumber", "Almería", "Spain", "ESP", "Andalusia", 36.8381, -2.4597, "Large protected cucumber production area for European markets.", "Semi-arid; greenhouse climate control compensates for extremes.", 2),
            _region("sinaloa-mexico-cucumber", "Sinaloa", "Mexico", "MEX", "Sinaloa", 24.8091, -107.3940, "Winter cucumber production for the North American export window.", "Hot semi-arid winter season with irrigation.", 3),
            _region("karnataka-india", "Karnataka", "India", "IND", "Karnataka", 15.3173, 75.7139, "Substantial open-field and protected cucumber production.", "Tropical; grown through the year where water is available.", 4),
            _region("westland-netherlands", "Westland", "Netherlands", "NLD", "South Holland", 52.0000, 4.2000, "High-tech glasshouse district producing cucumbers with precise climate control.", "Maritime temperate; production is entirely climate-controlled.", 5),
        ],
    },
    # ------------------------------------------------------------------ 15
    {
        "slug": "lettuce",
        "common_name": "Lettuce",
        "scientific_name": "Lactuca sativa",
        "family": "Asteraceae",
        "short_description": "Short-season leafy crop that favours cool, moist growing conditions.",
        "description": (
            "Lettuce is a fast, shallow-rooted leafy crop that produces best in cool weather. It "
            "bolts, turning bitter and running to seed, when temperatures exceed roughly 25 C, and "
            "it needs frequent irrigation because its roots are shallow. It is widely grown in "
            "field rotations close to markets and under protection for year-round supply."
        ),
        "lifecycle": "annual",
        "growth_habit": "herbaceous",
        "difficulty": "beginner",
        "tags": ["leafy", "cool season", "short season", "container friendly", "high water use"],
        "temp_min_c": 2.0,
        "temp_max_c": 28.0,
        "temp_optimal_min_c": 12.0,
        "temp_optimal_max_c": 20.0,
        "temperature_notes": "Above about 25 C the crop bolts and leaves turn bitter; light frost is tolerated.",
        "frost_tolerance": "light",
        "rainfall_min_mm": 300.0,
        "rainfall_max_mm": 600.0,
        "rainfall_notes": "Almost always irrigated; shallow roots cannot buffer dry spells.",
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.0,
        "soil_textures": ["loam", "sandy loam", "silt loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "Fertile soil with good moisture-holding capacity and free drainage.",
        "water_requirement": "high",
        "water_notes": "Frequent light irrigation is essential; stress causes tipburn and bolting.",
        "sunlight_requirement": "partial_sun",
        "sunlight_hours_min": 4.0,
        "sunlight_notes": "Full sun in cool conditions, light shade in warm ones reduces bolting.",
        "growing_season_days_min": 45,
        "growing_season_days_max": 80,
        "growing_season_notes": "From sowing to harvest; heat accelerates bolting and shortens the usable window.",
        "cultivation_steps": [
            {"order": 1, "title": "Sow for a cool window", "detail": "Time sowings to avoid the hottest weeks; lettuce is a cool-season crop."},
            {"order": 2, "title": "Sow shallowly", "detail": "Sow no more than about 1 cm deep; light is needed for good germination."},
            {"order": 3, "title": "Thin or transplant", "detail": "Space plants so air can move between heads, reducing disease."},
            {"order": 4, "title": "Irrigate frequently", "detail": "Keep the shallow root zone moist with small, frequent applications."},
            {"order": 5, "title": "Harvest promptly", "detail": "Cut heads or leaves before they begin to bolt for the best quality."},
        ],
        "common_problems": [
            {"name": "Bolting", "description": "Heat and long days trigger flowering; leaves turn bitter and unmarketable."},
            {"name": "Tipburn", "description": "Brown leaf margins caused by calcium delivery problems under rapid growth."},
            {"name": "Downy mildew", "description": "Cool, humid conditions cause pale patches with white sporulation."},
            {"name": "Aphids and slugs", "description": "Common pests of dense, moist leafy canopies."},
        ],
        "regions": [
            _region("salinas-california", "Salinas Valley, California", "United States", "USA", "California", 36.6777, -121.6555, "The best-known cool-season lettuce producing district in the world.", "Cool maritime fog moderates summer; fully irrigated.", 1),
            _region("westland-netherlands-lettuce", "Westland", "Netherlands", "NLD", "South Holland", 52.0000, 4.2000, "Glasshouse lettuce production for year-round European supply.", "Climate-controlled production independent of outdoor conditions.", 2),
            _region("murcia-spain", "Murcia", "Spain", "ESP", "Murcia", 37.9922, -1.1307, "Export-oriented protected and field lettuce production.", "Warm Mediterranean; winter production dominant.", 3),
            _region("lazio-italy", "Lazio", "Italy", "ITA", "Lazio", 41.9028, 12.4964, "Field vegetable production supplying Italian markets.", "Mild Mediterranean with cool, moist winters.", 4),
            _region("nile-delta-lettuce", "Nile Delta", "Egypt", "EGY", "Nile Delta", 30.7997, 31.0000, "Winter lettuce and vegetable production for export.", "Hot arid; grown in the cool season with irrigation.", 5),
        ],
    },
    # ------------------------------------------------------------------ 16
    {
        "slug": "chickpea",
        "common_name": "Chickpea",
        "scientific_name": "Cicer arietinum",
        "family": "Fabaceae",
        "short_description": "Cool-season pulse of semi-arid regions, grown largely on stored soil moisture.",
        "description": (
            "Chickpea is a cool-season grain legume well adapted to semi-arid environments, where it "
            "is usually grown as a winter or post-monsoon crop on stored soil moisture. It fixes "
            "nitrogen, tolerates alkaline soils, and fails in waterlogged ground. Heat during pod fill "
            "and humidity at flowering are the main climatic constraints."
        ),
        "lifecycle": "annual",
        "growth_habit": "herbaceous",
        "difficulty": "intermediate",
        "tags": ["legume", "pulse", "semi-arid", "nitrogen fixing", "cool season"],
        "temp_min_c": 5.0,
        "temp_max_c": 40.0,
        "temp_optimal_min_c": 15.0,
        "temp_optimal_max_c": 30.0,
        "temperature_notes": "Tolerates cool early conditions; heat and drought during pod fill reduce seed size.",
        "frost_tolerance": "none",
        "rainfall_min_mm": 300.0,
        "rainfall_max_mm": 600.0,
        "rainfall_notes": "Grown extensively on stored soil moisture with 300-600 mm, or less where residual moisture is deep.",
        "soil_ph_min": 6.0,
        "soil_ph_max": 8.0,
        "soil_textures": ["clay loam", "loam", "sandy loam"],
        "soil_drainage": "well-drained",
        "soil_notes": "One of the most alkaline-tolerant pulses, but it will not survive waterlogging.",
        "water_requirement": "low",
        "water_notes": "Deep roots draw on stored moisture; irrigation is used mainly at flowering and pod fill in dry years.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun; most cultivars are day-length neutral or long-day.",
        "growing_season_days_min": 90,
        "growing_season_days_max": 150,
        "growing_season_notes": "From sowing to maturity; shorter in warm regions with rapid early growth.",
        "cultivation_steps": [
            {"order": 1, "title": "Sow into stored moisture", "detail": "Sow at the end of the rains so the crop grows on water already in the profile."},
            {"order": 2, "title": "Inoculate or use treated seed", "detail": "Treat seed against seed-borne disease and use the correct rhizobia type where chickpea is new."},
            {"order": 3, "title": "Avoid excess nitrogen", "detail": "Heavy nitrogen fertiliser promotes leaf growth and delays maturity, reducing yield."},
            {"order": 4, "title": "Control pod borer", "detail": "Pod-boring caterpillars are the main yield-limiting pest in many regions."},
            {"order": 5, "title": "Harvest before pod shatter", "detail": "Timing matters, as the crop can shed seed rapidly once fully mature."},
        ],
        "common_problems": [
            {"name": "Ascochyta blight", "description": "Seed- and residue-borne disease that spreads fast in wet weather."},
            {"name": "Pod borer", "description": "Larvae feed inside pods and destroy developing seed."},
            {"name": "Fusarium wilt", "description": "Soil-borne wilt that persists for years in infested fields."},
            {"name": "Waterlogging", "description": "Rapidly kills chickpea in poorly drained ground."},
        ],
        "regions": [
            _region("madhya-pradesh-chickpea", "Madhya Pradesh", "India", "IND", "Madhya Pradesh", 22.9734, 78.6569, "The largest chickpea producing state in the world's largest producing country.", "Tropical monsoon; the crop grows post-monsoon on stored moisture.", 1),
            _region("queensland-australia", "Queensland", "Australia", "AUS", "Queensland", -26.0000, 150.0000, "Large-scale rain-fed chickpea production on stored subsoil water.", "Subtropical with summer rainfall and a dry winter cropping window.", 2),
            _region("anatolia-turkey", "Central Anatolia", "Turkey", "TUR", "Central Anatolia", 39.0000, 34.0000, "Long-standing chickpea growing region in the Near East.", "Semi-arid continental with cold winters and dry summers.", 3),
            _region("ethiopia-chickpea", "Oromia", "Ethiopia", "ETH", "Oromia", 8.5000, 39.0000, "Significant chickpea producing area, mainly as a rain-fed pulse.", "Tropical highland with a single dependable rainy season.", 4),
            _region("sinaloa-mexico-chickpea", "Sinaloa", "Mexico", "MEX", "Sinaloa", 25.1721, -107.4795, "Winter chickpea production for export, largely irrigated.", "Hot semi-arid winter; relies on irrigation.", 5),
        ],
    },
    # ------------------------------------------------------------------ 17
    {
        "slug": "grape",
        "common_name": "Grape vine",
        "scientific_name": "Vitis vinifera",
        "family": "Vitaceae",
        "short_description": "Perennial vine grown for wine, table grapes and dried fruit.",
        "description": (
            "The grape vine is a deep-rooted, long-lived temperate perennial. It wants a warm, sunny "
            "growing season with a dry ripening period, and it benefits from a period of winter "
            "dormancy. Its quality is driven as much by site and season as by management, and it is "
            "very sensitive to fungal disease in humid conditions."
        ),
        "lifecycle": "perennial",
        "growth_habit": "vine",
        "difficulty": "advanced",
        "tags": ["perennial", "vine", "fruit", "mediterranean", "well-drained"],
        "temp_min_c": -20.0,
        "temp_max_c": 40.0,
        "temp_optimal_min_c": 18.0,
        "temp_optimal_max_c": 30.0,
        "temperature_notes": "Hardiness varies widely with cultivar and vine age; spring frost at budburst and winter freeze are the main risks.",
        "frost_tolerance": "moderate",
        "rainfall_min_mm": 400.0,
        "rainfall_max_mm": 800.0,
        "rainfall_notes": "Prefers moderate rainfall with a dry ripening period; rain near harvest dilutes quality and encourages rot.",
        "soil_ph_min": 6.0,
        "soil_ph_max": 7.5,
        "soil_textures": ["gravelly", "sandy loam", "loam", "stony"],
        "soil_drainage": "sharply drained",
        "soil_notes": "Deep, well-drained, often stony and low-fertility soils; rich soils produce excess foliage and dilute fruit.",
        "water_requirement": "low",
        "water_notes": "A deep root system confers drought tolerance, though irrigation is used in very dry regions and regulated deficit irrigation is a quality tool.",
        "sunlight_requirement": "full_sun",
        "sunlight_hours_min": 6.0,
        "sunlight_notes": "Full sun for sugar accumulation; too much direct heat can scorch exposed fruit.",
        "growing_season_days_min": 150,
        "growing_season_days_max": 200,
        "growing_season_notes": "From budburst to harvest; vines take about three years to bear a commercial crop.",
        "cultivation_steps": [
            {"order": 1, "title": "Choose a warm, drained site", "detail": "Site and soil drainage determine both yield and fruit quality more than anything applied later."},
            {"order": 2, "title": "Establish the trellis first", "detail": "Vines are trained to a trellis system that determines canopy shape and light exposure."},
            {"order": 3, "title": "Plant dormant vines", "detail": "Plant bare-root vines in winter dormancy into well-drained soil."},
            {"order": 4, "title": "Prune in dormancy", "detail": "Winter pruning sets the crop level for the coming season and balances growth with fruit."},
            {"order": 5, "title": "Manage the canopy", "detail": "Shoot positioning and leaf removal around the fruit zone improve airflow and ripeness."},
            {"order": 6, "title": "Harvest by ripeness", "detail": "Judge harvest by sugar, acidity and flavour, sampling across the block."},
        ],
        "common_problems": [
            {"name": "Downy and powdery mildew", "description": "The two dominant fungal diseases; both are severe in humid, warm conditions."},
            {"name": "Botrytis bunch rot", "description": "Rots ripening bunches, particularly after rain."},
            {"name": "Phylloxera", "description": "Root-feeding insect; control is normally by grafting onto resistant rootstocks."},
            {"name": "Spring frost", "description": "Frost after budburst destroys emerging shoots and the season's crop."},
        ],
        "regions": [
            _region("bordeaux-france", "Bordeaux", "France", "FRA", "Nouvelle-Aquitaine", 44.8378, -0.5792, "One of the world's most referenced wine producing regions, with a maritime climate.", "Temperate maritime; vintage heavily influenced by harvest-time rainfall.", 1),
            _region("tuscany-italy", "Tuscany", "Italy", "ITA", "Tuscany", 43.7711, 11.2486, "Long-established wine region on rolling hills with a strong maritime influence.", "Warm Mediterranean with dry, sunny summers.", 2),
            _region("la-rioja-spain", "La Rioja", "Spain", "ESP", "La Rioja", 42.2871, -2.5396, "Spanish wine region with a continental influence moderated by altitude.", "Continental Mediterranean with a marked day-night temperature range.", 3),
            _region("napa-valley-usa", "Napa Valley, California", "United States", "USA", "California", 38.5025, -122.2654, "New World wine region with a warm, dry growing season moderated by coastal fog.", "Mediterranean; dry season through ripening with irrigation.", 4),
            _region("mendoza-argentina", "Mendoza", "Argentina", "ARG", "Mendoza", -32.8895, -68.8458, "High-altitude Argentine wine production on the Andean foothills.", "Semi-arid, high altitude with intense sun and cold nights.", 5),
            _region("barossa-australia", "Barossa Valley", "Australia", "AUS", "South Australia", -34.5300, 138.9500, "Australian wine region with a warm, dry ripening season.", "Mediterranean with hot, dry summers and irrigation from the Murray system.", 6),
        ],
    },
]


def _canonical_image_url(url: str | None) -> str | None:
    """Store the canonical Wikimedia host so responses need no redirect hop."""
    if not url:
        return None
    return url.replace("//thumb.wikimedia.org/", "//upload.wikimedia.org/")


def _with_imagery(plant: dict[str, Any]) -> dict[str, Any]:
    imagery = PLANT_IMAGERY.get(plant["slug"], {})
    merged = dict(plant)
    merged.update(
        {
            "image_url": _canonical_image_url(imagery.get("image_url")),
            "image_attribution": imagery.get("image_attribution"),
            "image_license": imagery.get("image_license"),
            "image_source_url": imagery.get("image_source_url"),
        }
    )
    merged.setdefault(
        "data_sources",
        _src(
            FAO_ECOCROP,
            USDA_PLANTS,
            RHS,
            *([FEEDIPEDIA] if plant["slug"] in {"maize", "bread-wheat", "soybean"} else []),
        ),
    )
    return merged


def all_seed_plants() -> list[dict[str, Any]]:
    return [_with_imagery(plant) for plant in PLANT_SEED]
