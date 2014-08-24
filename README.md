W katalogu bota:

    virtualenv venv
    pip install -r requirements.txt

    source venv/bin/activate

    scrapy crawl olx -o olx.json
    scrapy crawl gumtree -o gumtree.json
