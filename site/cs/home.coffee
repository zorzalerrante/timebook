window.timebook ?= {}
window.timebook.views ?= {}

timebook = window.timebook

window.timebook.views.home = $$({},
    '''
    <div id="home">
        <div class="hero-unit">
        
            <h1>Welcome to Timebook</h1>

            <p>Timebook is a project started on the Hack4Europe event organized by Europeana on the Museu Picasso at Barcelona on June 2011. It's a project by <strong>Luca Chiarandini</strong> &amp; <strong>Eduardo Graells</strong>, PhD students at Universitat Pompeu Fabra / Yahoo! Research Barcelona. This is made as an example of what a social network of the past would be.</p>
            
            <p>To start, search for something on the search bar!</p>
        </div>
        
        <div class="page-header">
            <h2>Credits</h2>
        </div>
        
        <div class="row-fluid">
            <div class="span4">
                <h3>Authors</h3>
                
                Luca Chiarandini (<code>luca.chiarandini [a] gmail</code>) and Eduardo Graells (<code>eduardo.graells [a] gmail</code>). Both are PhD students at Universitat Pompeu Fabra under the supervision of Dr. Ricardo Baeza-Yates and Dr. Alejandro Jaimes.
                
                You can find the <a href="http://github.com/Carnby/timebook">source code for Timebook in github</a>.
                
            </div>
            <div class="span4">
                
                <h3>Tools</h3>

                <ul>
                    <li>Python - the language in which we have coded the site and the data import/parsing.</li>
                    <li><a href="https://www.djangoproject.com/">django</a> - the web framework that powers the site's API.</li>
                    <li><a href="http://coffeescript.org/">Coffeescript</a> - the language in which we wrote the client side scripting.</li>
                    <li><a href="http://agilityjs.com/">Agility.js</a> - a tool in Javascript to code the client site structure.</li>
                    <li><a href="https://bitbucket.org/mchaput/whoosh/wiki/Home">Whoosh</a> - the search engine that powers our search box.</li>
                    <li><a href="http://twitter.github.com/bootstrap/">Bootstrap</a> - the design elements and layouts.</li>
                </ul>
            </div>
            <div class="span4">
                <h3>Data Sources</h3>

                <ul>
                    <li><a href="http://dbpedia.org/About">DBPedia</a> - we parse linked data extracted from Wikipedia and build profiles (bio, basic information, connections, works, etc) and groups (built from categories).</li>
                    <li><a href="https://en.wikiquote.org/wiki/Main_Page">WikiQuote</a> - we parse the content from WikiQuote's dumps and match some of them (not all because the data is not linked) to our profiles.</li> 
                </ul>
            </div>
        </div>

    </div>
    '''
)