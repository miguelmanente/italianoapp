from icrawler.builtin import BingImageCrawler

# Lista de comidas italianas que quieres descargar
busquedas = ['idraulico', 'meccanico', 'elettricista', 'pittore', 'muratore', 'falegname', 'fabbro']

for elemento in busquedas:
    bing_crawler = BingImageCrawler(storage={'root_dir': f'static/imagen/{elemento}'})
    # Reemplazamos la búsqueda con el nombre + contexto
    bing_crawler.crawl(keyword=f"{elemento} italia", max_num=1)


print("¡Descarga completada!")