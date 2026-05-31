import urllib.request
import json
import re
import os
import ssl
import sys

ssl._create_default_https_context = ssl._create_unverified_context
sys.stdout.reconfigure(encoding='utf-8')

def fetch_json(url, retries=5, delay=1.5):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except Exception as e:
            if i == retries - 1:
                raise e
            import time
            time.sleep(delay)

def graphql_query(query):
    req = urllib.request.Request(
        'https://beta.pokeapi.co/graphql/v1beta',
        data=json.dumps({'query': query}).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read())

LOCATION_RU = {
    "Area": "",
    "South": "(юг)",
    "North": "(север)",
    "West": "(запад)",
    "East": "(восток)",
    "Pallet Town": "Паллет Таун",
    "Cerulean City": "Серулин Сити",
    "Route": "Маршрут",
    "Alola Route": "Маршрут Алола",
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

METHOD_RU = {
    'walk': 'в траве',
    'old-rod': 'старая удочка',
    'good-rod': 'хорошая удочка',
    'super-rod': 'супер удочка',
    'surf': 'на воде',
    'rock-smash': 'разбивание камней',
    'headbutt': 'удар головой',
    'dark-grass': 'в темной траве',
    'grass-spots': 'в пятнах травы',
    'cave-spots': 'в пятнах пещеры',
    'bridge-spots': 'на мосту',
    'super-rod-spots': 'супер удочка (пятна)',
    'surf-spots': 'на воде (пятна)',
    'yellow-flowers': 'в желтых цветах',
    'purple-flowers': 'в фиолетовых цветах',
    'red-flowers': 'в красных цветах',
    'rough-terrain': 'на неровной местности',
    'gift': 'в подарок',
    'gift-egg': 'в подарок (яйцо)',
    'only-one': 'только один',
    'pokeflute': 'покэфлейта',
    'headbutt-low': 'удар головой (низкий)',
    'headbutt-normal': 'удар головой (обычный)',
    'headbutt-high': 'удар головой (высокий)',
    'squirt-bottle': 'бутылка с водой',
    'wailmer-pail': 'ведро Вейлмера',
    'seaweed': 'водоросли',
    'roaming-grass': 'блуждающий (в траве)',
    'roaming-water': 'блуждающий (на воде)',
    'devon-scope': 'девон-прицел',
    'feebas-tile-fishing': 'рыбалка на клетке Фибаса',
    'island-scan': 'островное сканирование',
    'sos-encounter': 'sos-вызов',
    'bubbling-spots': 'пузырящиеся пятна',
    'berry-piles': 'кучи ягод',
    'npc-trade': 'обмен с NPC',
    'sos-from-bubbling-spot': 'sos-вызов из пузырящегося пятна'
}

def translate_location(loc_name):
    loc_name = loc_name.replace("-", " ").title()
    for eng, ru in LOCATION_RU.items():
        loc_name = re.sub(rf'\b{eng}\b', ru, loc_name, flags=re.IGNORECASE)
    loc_name = re.sub(r'\s+', ' ', loc_name).strip()
    return loc_name

def translate_method(method_name):
    return METHOD_RU.get(method_name, method_name)

STARTER_SPECIES = {
    "bulbasaur", "ivysaur", "venusaur", "charmander", "charmeleon", "charizard", "squirtle", "wartortle", "blastoise",
    "chikorita", "bayleef", "meganium", "cyndaquil", "quilava", "typhlosion", "totodile", "croconaw", "feraligatr",
    "treecko", "grovyle", "sceptile", "torchic", "combusken", "blaziken", "mudkip", "marshtomp", "swampert",
    "turtwig", "grotle", "torterra", "chimchar", "monferno", "infernape", "piplup", "prinplup", "empoleon",
    "snivy", "servine", "serperior", "tepig", "pignite", "emboar", "oshawott", "dewott", "samurott",
    "chespin", "quilladin", "chesnaught", "fennekin", "braixen", "delphox", "froakie", "frogadier", "greninja",
    "rowlet", "dartrix", "decidueye", "litten", "torracat", "incineroar", "popplio", "brionne", "primarina",
    "grookey", "thwackey", "rillaboom", "scorbunny", "raboot", "cinderace", "sobble", "drizzile", "inteleon",
    "sprigatito", "floragato", "meowscarada", "fuecoco", "raboot", "skeledirge", "quaxly", "drizzile", "quaquaval"
}

def main():
    print("Downloading Russian names mapping...")
    ru_names_url = "https://raw.githubusercontent.com/sindresorhus/pokemon/main/data/ru.json"
    ru_names = fetch_json(ru_names_url)

    print("Fetching all Pokemon data from GraphQL...")
    offset = 0
    limit = 200
    all_pokemon_data = []

    while True:
        print(f"Fetching offset {offset}...")
        query = f"""
        query {{
          pokemon_v2_pokemon(offset: {offset}, limit: {limit}, order_by: {{id: asc}}) {{
            id
            name
            is_default
            pokemon_v2_pokemonspecy {{
              id
              name
              is_legendary
              is_mythical
              is_baby
            }}
            pokemon_v2_encounters {{
              pokemon_v2_version {{
                name
              }}
              pokemon_v2_locationarea {{
                name
              }}
              pokemon_v2_encounterslot {{
                pokemon_v2_encountermethod {{
                  name
                }}
              }}
            }}
          }}
        }}
        """

        try:
            res = graphql_query(query)
            chunk = res.get('data', {}).get('pokemon_v2_pokemon', [])
            if not chunk:
                break
            all_pokemon_data.extend(chunk)
            offset += limit
            
            # For testing, break early if needed
            # if offset >= 1000: break
        except Exception as e:
            print(f"Failed to fetch chunk {offset}: {e}")
            break

    print(f"Fetched {len(all_pokemon_data)} pokemons. Processing...")
    
    
    print("Fetching flavor texts to map species to versions for newer games...")
    flavor_query = """
    query {
      pokemon_v2_pokemonspeciesflavortext(where: {language_id: {_eq: 9}}) {
        pokemon_species_id
        pokemon_v2_version {
          name
        }
      }
    }
    """
    try:
        flavor_res = graphql_query(flavor_query)
        flavors = flavor_res.get('data', {}).get('pokemon_v2_pokemonspeciesflavortext', [])
        species_to_games = {}
        for item in flavors:
            sid = item['pokemon_species_id']
            v_name = item['pokemon_v2_version']['name']
            if sid not in species_to_games:
                species_to_games[sid] = set()
            species_to_games[sid].add(v_name)
    except Exception as e:
        print(f"Failed to fetch flavor texts: {e}")
        species_to_games = {}

    final_list = []

    for p in all_pokemon_data:
        specy = p['pokemon_v2_pokemonspecy']
        if not specy:
            continue

        species_name = specy['name']
        species_id = specy['id']
        pokemon_id = p['id']

        # Name
        en_name = p['name'].replace("-", " ").title()
        ru_name = en_name
        if 0 < species_id <= len(ru_names):
            ru_name = ru_names[species_id - 1]
            if "alola" in p['name']:
                ru_name = f"Алола {ru_name}"
            elif "galar" in p['name']:
                ru_name = f"Галар {ru_name}"
            elif "hisui" in p['name']:
                ru_name = f"Хисуи {ru_name}"
            elif "paldea" in p['name']:
                ru_name = f"Палдея {ru_name}"

        # Category
        category = "Обычный"
        if specy['is_mythical']:
            category = "Мифический"
        elif specy['is_legendary']:
            category = "Легендарный"
        elif species_name in STARTER_SPECIES:
            category = "Стартовый"

        # Image
        image_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon_id}.png"

        # Encounters
        encounters_dict = {}
        for enc in p.get('pokemon_v2_encounters', []):
            v_name = enc['pokemon_v2_version']['name']
            loc_name = translate_location(enc['pokemon_v2_locationarea']['name'])
            method_name = translate_method(enc['pokemon_v2_encounterslot']['pokemon_v2_encountermethod']['name'])

            enc_str = f"{loc_name} ({method_name})"

            if v_name not in encounters_dict:
                encounters_dict[v_name] = []

            if enc_str not in encounters_dict[v_name]:
                encounters_dict[v_name].append(enc_str)

        # Join multiple encounters per version
        for v, elist in encounters_dict.items():
            encounters_dict[v] = ", ".join(elist[:3]) + ("" if len(elist) <= 3 else " и др.")


        # Fallback for newer games via flavor text (Pokedex entries)
        if species_id in species_to_games:
            for v_name in species_to_games[species_id]:
                if v_name not in encounters_dict:
                    encounters_dict[v_name] = "Эволюция, специальное получение или перенос"

        final_list.append({
            "id": pokemon_id,
            "name_en": en_name,
            "name_ru": ru_name,
            "category": category,
            "image": image_url,
            "encounters": encounters_dict
        })

    print(f"Total processed: {len(final_list)}")
    
    with open("pokemon_data.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

    if os.path.exists("index.html"):
        print("Injecting database into index.html...")
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        new_data_str = f"const pokemonData = {json.dumps(final_list, ensure_ascii=False)};"
        pattern = r"const pokemonData = \[.*?\];"
        
        updated_html = re.sub(pattern, new_data_str, html_content, flags=re.DOTALL)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(updated_html)
        print("index.html successfully updated and ready!")

if __name__ == "__main__":
    main()
