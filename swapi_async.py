import asyncio
import aiohttp
import datetime
from more_itertools import chunked
from models import Base, SwapiPeople, Session, engine

MAX_CHUNK_SIZE = 10 # Константа для разбиения данных в запросах
async def get_people(people_id):
    print(f'people_id = {people_id}')
    session = aiohttp.ClientSession()
    print(f'session = {session}')
    response = await session.get(f'https://swapi.dev/api/people/{people_id}')
    json_data = await response.json()
    await session.close()
    return json_data

async def get_film_name(film_link):
    #print(f'film_link = {film_link}')
    session = aiohttp.ClientSession()
    #print(f'session = {session}')
    response = await session.get(film_link)
    json_data = await response.json()
    await session.close()
    film_name = json_data.get('title')
    return film_name

async def insert_to_db(people_json_list):
    #print(people_json_list)
    numb = 0
    async with Session() as session:
        swapi_people_list = []
        for people in people_json_list:
            numb += 1
            print(f"people - {numb}: {people}\n")
            
            #Получение списка названий по списку ссылок фильмов
            films_links_list= people.get('films')
            #Получение корутин по ссылке film
            films_names = [get_film_name(film_link) for film_link in films_links_list] # создание списка для хранения корутин
            #Получение списка с названием фильмов в асинхроне
            films_list = await asyncio.gather(*films_names)              
            films_list = ', '.join(films_list)
            print(f'films_names: {films_list}')




            
            swapi_people_list.append({'id': numb,
                                      'name': people.get('name'),
                                      'birth_year': people.get('birth_year'),
                                      'eye_color': people.get('eye_color'),
                                      'films': films_list,
                                      'gender': people.get('gender'),
                                      'hair_color': people.get('hair_color'),
                                      'height': people.get('height'),
                                      'homeworld': people.get('homeworld'),
                                      'mass': people.get('mass'),
                                      'skin_color': people.get('skin_color'),
                                      'species': people.get('species'),
                                      'starships': people.get('starships'),
                                      'vehicles': people.get('vehicles')
                                      }) 
        swapi_people_list = [SwapiPeople(**json_data) for json_data in swapi_people_list]                                
        print(f'swapi_people_list: {swapi_people_list}')
        session.add_all(swapi_people_list)
        await session.commit()


async def main():
    
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)

    # Все запросы группируются в партии по MAX_CHUNK_SIZE
    for ids_chunk in chunked(range(1, 5), MAX_CHUNK_SIZE):
        get_people_coros = [get_people(people_id) for people_id in ids_chunk] # создание списка для хранения корутин
            # Можно заменить вышеуказанным comprehantion-выражением
            # for people_id in ids_chunk:
            #     coro = get_people(people_id)
            #     coros.append(coro)
        people_json_list = await asyncio.gather(*get_people_coros) # формирование списка
        asyncio.create_task(insert_to_db(people_json_list)) # создание задачи на вставку данных в БД
    
    current_task = asyncio.current_task() # определение текущей задачи (для данной функции main())
    task_sets = asyncio.all_tasks() # формирование списка задач, которые должны быть выполнены до завершения работы с БД
    task_sets.remove(current_task) # из набора задачь удаляется текущая задача main
    
    await asyncio.gather(*task_sets) # ожидание что все задания на вставку завершились
    await engine.dispose() # завершение работы с базой данных

start = datetime.datetime.now()
asyncio.run(main())
print(datetime.datetime.now() - start)