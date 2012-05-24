# Timebook

Timebook is a project started on the Hack4Europe event organized by Europeana on the Museu Picasso at Barcelona on June 2011. It's a project by Luca Chiarandini & Eduardo Graells, PhD students at Universitat Pompeu Fabra / Yahoo! Research Barcelona. This is made as an example of what a social network of the past would be.
                
                
## Tools

* Python - the language in which we have coded the site and the data import/parsing.
* django - the web framework that powers the site's API.
* Coffeescript - the language in which we wrote the client side scripting.
* Agility.js - a tool in Javascript to code the client site structure.
* Whoosh - the search engine that powers our search box.
* Twitter Bootstrap - the design elements and layouts.
  
## Data Sources

* DBPedia - we parse linked data extracted from Wikipedia and build profiles (bio, basic information, connections, works, etc) and groups (built from categories).
* WikiQuote - we parse the content from WikiQuote's dumps and match some of them (not all because the data is not linked) to our profiles.
