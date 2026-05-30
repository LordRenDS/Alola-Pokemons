import urllib.request
import json
import concurrent.futures
import re
import sys
import os
import ssl
import time

# Bypass local SSL certificate validation errors
ssl._create_default_https_context = ssl._create_unverified_context
sys.stdout.reconfigure(encoding='utf-8')

# Ultra Sun exclusives to exclude
ULTRA_SUN_EXCLUSIVES = {
    # Standard & forms
    "houndour", "houndoom", "cranidos", "rampardos", "cottonee", "whimsicott",
    "tirtouga", "carracosta", "rufflet", "braviary", "passimian", "turtonator",
    "omanyte", "omastar", "anorith", "armaldo", "golett", "golurk",
    "clauncher", "clawitzer", "tyrunt", "tyrantrum",
    "vulpix-alola", "ninetales-alola",
    # Legendaries / UBs
    "buzzwole", "kartana", "blacephalon", "solgaleo",
    "ho-oh", "raikou", "groudon", "latios", "dialga", "heatran", "reshiram", "tornadus", "xerneas"
}

STARTER_SPECIES = {
    "rowlet", "dartrix", "decidueye", "litten", "torracat", "incineroar", "popplio", "brionne", "primarina",
    # Island Scan starters
    "bulbasaur", "ivysaur", "venusaur", "charmander", "charmeleon", "charizard", "squirtle", "wartortle", "blastoise",
    "treecko", "grovyle", "sceptile", "torchic", "combusken", "blaziken", "mudkip", "marshtomp", "swampert",
    "turtwig", "grotle", "torterra", "chimchar", "monferno", "infernape", "piplup", "prinplup", "empoleon",
    "snivy", "servine", "serperior", "tepig", "pignite", "emboar", "oshawott", "dewott", "samurott",
    "chespin", "quilladin", "chesnaught", "fennekin", "braixen", "delphox", "froakie", "frogadier", "greninja"
}

LEGENDARY_SPECIES = {
    "cosmog", "cosmoem", "solgaleo", "lunala", "necrozma",
    "tapu-koko", "tapu-lele", "tapu-bulu", "tapu-fini",
    "nihilego", "buzzwole", "pheromosa", "xurkitree", "celesteela", "kartana", "guzzlord",
    "poipole", "naganadel", "stakataka", "blacephalon",
    "magearna", "marshadow", "zeraora",
    # Ultra Space Wilds legendaries available in Ultra Moon
    "mewtwo", "articuno", "zapdos", "moltres", "lugia", "entei", "suicune", "kyogre", "latias", "palkia", "regigigas", "giratina", "cresselia", "cobalion", "terrakion", "virizion", "thundurus", "zekrom", "yveltal", "zygarde", "regirock", "regice", "registeel", "rayquaza", "landorus", "kyurem"
}

EXTRA_UM_SPECIES = [
    # USW Legendaries (Kyogre, Palkia, Lugia, Entei, Zekrom, Yveltal, Latias, Regigigas, Thundurus, etc.)
    "mewtwo", "articuno", "zapdos", "moltres", "lugia", "entei", "suicune", "kyogre", "latias", "palkia", "regigigas", "thundurus", "zekrom", "yveltal", 
    "regirock", "regice", "registeel", "uxie", "mesprit", "azelf", "cresselia", "cobalion", "terrakion", "virizion", "rayquaza", "giratina", "landorus", "kyurem",
    # Island Scan base species & families
    "bulbasaur", "ivysaur", "venusaur",
    "charmander", "charmeleon", "charizard",
    "squirtle", "wartortle", "blastoise",
    "weedle", "kakuna", "beedrill",
    "pidgey", "pidgeotto", "pidgeot",
    "onix", "steelix",
    "horsea", "seadra", "kingdra",
    "rhyhorn", "rhydon", "rhyperior",
    "ralts", "kirlia", "gardevoir", "gallade",
    "aron", "lairon", "aggron",
    "spheal", "sealeo", "walrein",
    "swinub", "piloswine", "mamoswine",
    "rotom",
    "sewaddle", "swadloon", "leavanny",
    "litwick", "lampent", "chandelure",
    "axew", "fraxure", "haxorus",
    "honedge", "doublade", "aegislash",
    "scatterbug", "spewpa", "vivillon",
    "treecko", "grovyle", "sceptile",
    "torchic", "combusken", "blaziken",
    "mudkip", "marshtomp", "swampert",
    "turtwig", "grotle", "torterra",
    "chimchar", "monferno", "infernape",
    "piplup", "prinplup", "empoleon",
    "snivy", "servine", "serperior",
    "tepig", "pignite", "emboar",
    "oshawott", "dewott", "samurott",
    "tynamo", "eelektrik", "eelektross",
    "chespin", "quilladin", "chesnaught",
    "fennekin", "braixen", "delphox",
    "froakie", "frogadier", "greninja"
]

SPECIAL_OBTAIN = {
    # USW Legendaries
    "mewtwo": "Ультра-пространство (зеленый портал)",
    "articuno": "Ультра-пространство (красный портал)",
    "zapdos": "Ультра-пространство (красный портал)",
    "moltres": "Ультра-пространство (красный портал)",
    "lugia": "Ультра-пространство (красный портал, эксклюзив Ultra Moon)",
    "entei": "Ультра-пространство (зеленый портал, эксклюзив Ultra Moon)",
    "suicune": "Ультра-пространство (зеленый портал, требуется наличие Энтея и Райкоу)",
    "kyogre": "Ультра-пространство (синий портал, эксклюзив Ultra Moon)",
    "latias": "Ультра-пространство (синий портал, эксклюзив Ultra Moon)",
    "palkia": "Ультра-пространство (синий портал, эксклюзив Ultra Moon)",
    "regigigas": "Ультра-пространство (желтый портал, эксклюзив Ultra Moon)",
    "thundurus": "Ультра-пространство (красный портал, эксклюзив Ultra Moon)",
    "zekrom": "Ультра-пространство (красный портал, эксклюзив Ultra Moon)",
    "yveltal": "Ультра-пространство (красный портал, эксклюзив Ultra Moon)",
    "regirock": "Ультра-пространство (желтый портал)",
    "regice": "Ультра-пространство (желтый портал)",
    "registeel": "Ультра-пространство (желтый портал)",
    "uxie": "Ультра-пространство (синий портал)",
    "mesprit": "Ультра-пространство (синий портал)",
    "azelf": "Ультра-пространство (синий портал)",
    "cresselia": "Ультра-пространство (синий портал)",
    "cobalion": "Ультра-пространство (зеленый портал)",
    "terrakion": "Ультра-пространство (зеленый портал)",
    "virizion": "Ультра-пространство (зеленый портал)",
    "rayquaza": "Ультра-пространство (синий портал, требуется наличие Кайогра и Гроудона)",
    "giratina": "Ультра-пространство (синий портал, требуется наличие Палкии и Диалги)",
    "landorus": "Ультра-пространство (красный портал, требуется наличие Торнадуса и Тандуруса)",
    "kyurem": "Ультра-пространство (красный портал, требуется наличие Реширама и Зекрома)",
    # Island Scan Melemele
    "squirtle": "Островное сканирование (Мелемеле, Понедельник, Залив Калаэ)",
    "onix": "Островное сканирование (Мелемеле, Вторник, Холм Десяти Карат)",
    "horsea": "Островное сканирование (Мелемеле, Среда, Залив Калаэ)",
    "scatterbug": "Островное сканирование (Мелемеле, Четверг, Маршрут 1)",
    "bulbasaur": "Островное сканирование (Мелемеле, Пятница, Маршрут 2)",
    "litwick": "Островное сканирование (Мелемеле, Суббота, Кладбище Хауоли)",
    "charmander": "Островное сканирование (Мелемеле, Воскресенье, Вулкан Вела)",
    # Island Scan Akala
    "spheal": "Островное сканирование (Акала, Понедельник, Залив Хано)",
    "combusken": "Островное сканирование (Акала, Вторник, Маршрут 8)",
    "honedge": "Островное сканирование (Акала, Среда, Окраины Акала)",
    "beedrill": "Островное сканирование (Акала, Четверг, Маршрут 4)",
    "grovyle": "Островное сканирование (Акала, Пятница, Маршрут 5)",
    "marshtomp": "Островное сканирование (Акала, Суббота, Маршрут 6)",
    "ralts": "Островное сканирование (Акала, Воскресенье, Маршрут 6)",
    # Island Scan Ula'ula
    "swinub": "Островное сканирование (Улаула, Понедельник, Маршрут 13)",
    "prinplup": "Островное сканирование (Улаула, Вторник, Маршрут 12)",
    "grotle": "Островное сканирование (Улаула, Среда, Маршрут 10)",
    "pidgeot": "Островное сканирование (Улаула, Четверг, Маршрут 10)",
    "monferno": "Островное сканирование (Улаула, Пятница, Маршрут 11)",
    "axew": "Островное сканирование (Улаула, Суббота, Гора Хокулани)",
    "rhyhorn": "Островное сканирование (Улаула, Воскресенье, Гора Блаш)",
    # Island Scan Poni
    "aggron": "Островное сканирование (Пони, Понедельник, Каньон Пони)",
    "rotom": "Островное сканирование (Пони, Вторник, Каньон Пони)",
    "leavanny": "Островное сканирование (Пони, Среда, Луг Пони)",
    "chesnaught": "Островное сканирование (Пони, Четверг, Дикие земли Пони)",
    "greninja": "Островное сканирование (Пони, Пятница, Побережье Пони)",
    "delphox": "Островное сканирование (Пони, Суббота, Древний путь Пони)",
    "eelektross": "Островное сканирование (Пони, Воскресенье, Роща Пони)",
}

PRE_EVOLUTION_PARENTS = {
    "treecko": "grovyle",
    "torchic": "combusken",
    "mudkip": "marshtomp",
    "turtwig": "grotle",
    "chimchar": "monferno",
    "piplup": "prinplup",
    "snivy": "servine",
    "tepig": "pignite",
    "oshawott": "dewott",
    "chespin": "quilladin",
    "fennekin": "braixen",
    "froakie": "frogadier",
    "weedle": "kakuna",
    "pidgey": "pidgeotto",
    "aron": "lairon",
    "sewaddle": "swadloon",
    "tynamo": "eelektrik",
}

# Location Translations
LOCATION_RU = {
    "Alola Route": "Маршрут Алола",
    "Route": "Маршрут",
    "Melemele Sea": "Море Мелемеле",
    "Iki Town": "Ики Таун",
    "Mahalo Trail": "Тропа Махало",
    "Ruins Of Conflict": "Руины Борьбы",
    "Ten Carat Hill": "Холм Десяти Карат",
    "Hauoli Outskirts": "Окраины Хауоли",
    "Hauoli City": "Город Хауоли",
    "Sandy Cave": "Песчаная пещера",
    "Verdant Cavern": "Пещера Заросших",
    "Seaward Cave": "Приморская пещера",
    "Kalae Bay": "Залив Калаэ",
    "Paniola Town": "Город Паниола",
    "Paniola Ranch": "Ранчо Паниола",
    "Royal Avenue": "Королевская авеню",
    "Wela Volcano Park": "Парк вулкана Вела",
    "Brooklet Hill": "Холм Ручья",
    "Lush Jungle": "Пышные джунгли",
    "Digletts Tunnel": "Тоннель Диглеттов",
    "Memorial Hill": "Мемориальный холм",
    "Hano Beach": "Пляж Хано",
    "Hano Grand Resort": "Курорт Хано Гранд",
    "Aether Paradise": "Эфирный Рай",
    "Malie City": "Город Малие",
    "Mount Lanakila": "Гора Ланакила",
    "Altar Of The Moone": "Алтарь Луны",
    "Resolution Cave": "Пещера Решимости",
    "Vast Poni Canyon": "Каньон Пони",
    "Poni Meadow": "Луг Пони",
    "Poni Wilds": "Дикие земли Пони",
    "Poni Coast": "Побережье Пони",
    "Poni Gauntlet": "Вызов Пони",
    "Hauoli": "Хауоли",
    "Poni": "Пони",
    "Akala": "Акала",
    "Ulaula": "Улаула",
    "Melemele": "Мелемеле",
    "Lake Of The Moone": "Озеро Луны",
    "Mount Hokulani": "Гора Хокулани",
    "Blush Mountain": "Смущенная гора",
    "Hokulani Observatory": "Обсерватория Хокулани",
    "Thrifty Megamart": "Супермаркет Трифи",
    "Ulaula Meadow": "Луг Улаула",
    "Po Town": "По Таун",
    "Seafolk Village": "Деревня Морского Народа",
    "Poni Grove": "Роща Пони",
    "Ruins Of Hope": "Руины Надежды",
    "Ruins Of Abundance": "Руины Изобилия",
    "Ruins Of Life": "Руины Жизни",
    "Exeggutor Island": "Остров Экзеггуторов"
}

def translate_location(loc_name):
    loc_name = loc_name.replace("Area", "").replace("South", "(юг)").replace("North", "(север)").replace("West", "(запад)").replace("East", "(восток)")
    loc_name = re.sub(r'\s+', ' ', loc_name).strip()
    for eng, ru in LOCATION_RU.items():
        loc_name = re.sub(rf'\b{eng}\b', ru, loc_name, flags=re.IGNORECASE)
    return loc_name

def clean_name(name):
    return name.replace("-", " ").title()

def fetch_json(url, retries=5, delay=1.5):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            if i == retries - 1:
                raise e
            print(f"Retrying {url} in {delay}s due to error: {e}")
            time.sleep(delay)

def get_pokemon_data(entry):
    species_name = entry['pokemon_species']['name']
    species_url = entry['pokemon_species']['url']
    
    if species_name in ULTRA_SUN_EXCLUSIVES:
        return None

    try:
        species_data = fetch_json(species_url)
    except Exception as e:
        print(f"Error fetching species {species_name}: {e}")
        return None

    species_id = species_data['id']

    # Check for Alolan forms in varieties
    is_alolan = False
    pokemon_id = species_id
    for var in species_data.get('varieties', []):
        var_name = var['pokemon']['name']
        if var_name.endswith('-alola'):
            is_alolan = True
            var_url = var['pokemon']['url']
            m_var = re.search(r'/pokemon/(\d+)/', var_url)
            if m_var:
                pokemon_id = int(m_var.group(1))
            break

    if is_alolan and f"{species_name}-alola" in ULTRA_SUN_EXCLUSIVES:
        return None

    # Determine category
    category = "Интернациональный"
    if species_name in STARTER_SPECIES:
        category = "Стартовый"
    elif species_name in LEGENDARY_SPECIES:
        category = "Легендарный"
    elif is_alolan or (species_id >= 722 and species_id <= 807):
        category = "Региональный"

    # Determine obtain method
    obtain_method = "Неизвестно"
    if species_name in SPECIAL_OBTAIN:
        obtain_method = SPECIAL_OBTAIN[species_name]
    elif species_name in PRE_EVOLUTION_PARENTS:
        obtain_method = f"Получается разведением (яйцо от {PRE_EVOLUTION_PARENTS[species_name].title()})"
    else:
        # Search direct encounters in Ultra Moon
        encounters_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/encounters"
        locations = []
        try:
            encounters = fetch_json(encounters_url)
            for enc in encounters:
                location_raw = enc['location_area']['name'].replace("-", " ").title()
                location_ru = translate_location(location_raw)
                for v_detail in enc['version_details']:
                    if v_detail['version']['name'] == 'ultra-moon':
                        for details in v_detail['encounter_details']:
                            method = details['method']['name']
                            if method == 'walk':
                                method_ru = "в траве"
                            elif method == 'surf':
                                method_ru = "на воде"
                            elif method == 'gift':
                                method_ru = "в подарок"
                            elif 'rod' in method:
                                method_ru = "рыбалка"
                            else:
                                method_ru = method
                            locations.append(f"{location_ru} ({method_ru})")
        except Exception:
            pass

        if locations:
            locations = list(set(locations))
            obtain_method = "Дикий покемон: " + ", ".join(locations[:3])
        else:
            from_species = species_data.get('evolves_from_species')
            if from_species:
                obtain_method = f"Эволюционирует из {clean_name(from_species['name'])}"
            else:
                if species_name in STARTER_SPECIES:
                    obtain_method = "Стартовый покемон (в подарок на Маршруте 1)"
                elif species_name in LEGENDARY_SPECIES:
                    obtain_method = "Особая локация Ультра-пространства"
                else:
                    obtain_method = "Особый подарок от персонажей или эволюция"

    # Sprites Artwork URL
    image_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_id}.png"

    en_display_name = clean_name(species_name)
    if is_alolan:
        en_display_name = f"Alola {en_display_name}"

    return {
        "id": pokemon_id,
        "species_id": species_id,
        "dex_num": entry['entry_number'],
        "name_en": en_display_name,
        "name_ru": "", # Filled later from ru.json
        "category": category,
        "is_alolan": is_alolan,
        "image": image_url,
        "obtain": obtain_method
    }

def main():
    print("Downloading Russian names mapping...")
    ru_names_url = "https://raw.githubusercontent.com/sindresorhus/pokemon/main/data/ru.json"
    ru_names = fetch_json(ru_names_url)
    
    print("Fetching Alola Pokedex entries...")
    pokedex = fetch_json("https://pokeapi.co/api/v2/pokedex/21/")
    entries = pokedex.get('pokemon_entries', [])
    
    # Append EXTRA obtainable species caught via wormholes or island scan
    print("Appending non-Alola obtainable species (Island Scan and Wormholes)...")
    for species in EXTRA_UM_SPECIES:
        already_in = False
        for entry in entries:
            if entry['pokemon_species']['name'] == species:
                already_in = True
                break
        if not already_in:
            entries.append({
                "pokemon_species": {
                    "name": species,
                    "url": f"https://pokeapi.co/api/v2/pokemon-species/{species}/"
                },
                "entry_number": None
            })
            
    print(f"Loaded {len(entries)} entries. Processing...")
    
    pokemon_list = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_pokemon_data, entry): entry for entry in entries}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                spec_id = res['species_id']
                if 0 < spec_id <= len(ru_names):
                    ru_name = ru_names[spec_id - 1]
                    if res['is_alolan']:
                        ru_name = f"Алола {ru_name}"
                    res['name_ru'] = ru_name
                else:
                    res['name_ru'] = res['name_en']
                pokemon_list.append(res)
                print(f"Processed: {res['name_en']} ({res['name_ru']})")

    # Further translate evolved and pre-evolved parents names in obtain field
    # We do this after compiling the complete pokemon_list so all translations are fully resolved!
    print("Refining obtain method translations...")
    for res in pokemon_list:
        obtain = res['obtain']
        if "Эволюционирует из" in obtain:
            parent_eng = obtain.replace("Эволюционирует из ", "").strip().lower().replace(" ", "-")
            parent_ru = None
            for p in pokemon_list:
                if p['name_en'].lower().replace(" ", "-") == parent_eng or p['name_en'].lower().replace(" ", "") == parent_eng.replace("-", ""):
                    parent_ru = p['name_ru']
                    break
            if parent_ru:
                res['obtain'] = f"Эволюция {parent_ru}"
        elif "Получается разведением (яйцо от " in obtain:
            parent_eng = obtain.replace("Получается разведением (яйцо от ", "").replace(")", "").strip().lower().replace(" ", "-")
            parent_ru = None
            for p in pokemon_list:
                if p['name_en'].lower().replace(" ", "-") == parent_eng or p['name_en'].lower().replace(" ", "") == parent_eng.replace("-", ""):
                    parent_ru = p['name_ru']
                    break
            if parent_ru:
                res['obtain'] = f"Разведение (яйцо от {parent_ru})"

    # Sort: Alola Regional Dex entries first, then extra entries in national ID order
    pokemon_list.sort(key=lambda x: (0, x['dex_num']) if x['dex_num'] is not None else (1, x['id']))
    
    # Export to data.json
    with open("pokemon_data.json", "w", encoding="utf-8") as f:
        json.dump(pokemon_list, f, ensure_ascii=False, indent=2)
    print(f"Database compiled! Total Pokémon: {len(pokemon_list)}")

    # If index.html exists, inject data directly
    if os.path.exists("index.html"):
        print("Injecting database into index.html...")
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        new_data_str = f"const pokemonData = {json.dumps(pokemon_list, ensure_ascii=False)};"
        pattern = r"const pokemonData = \[\];\s*//\s*DATA_PLACEHOLDER"
        
        updated_html = re.sub(pattern, new_data_str, html_content)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(updated_html)
        print("index.html successfully updated and ready!")

if __name__ == "__main__":
    main()
