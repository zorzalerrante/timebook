window.timebook ?= {}
window.timebook.views ?= {}

timebook = window.timebook

# settings
current_order = 'score'
width = 320
height = 180
x_padding = 20
y_padding = 30
bubble_radius = 5

quantile = d3.scale.linear().domain([0,200]).range([0,width - x_padding])
axis = d3.svg.axis().scale(quantile).ticks(4).tickSize(height - y_padding + 5) 


height_scale = d3.scale.linear().range([0, height - y_padding])
connection_scale = d3.scale.linear().range([0, height - y_padding - bubble_radius])
order_functions =
    score: (a,b) -> d3.descending(+a.score, +b.score)
    alpha: (a,b) -> d3.ascending(a.name, b.name)
    
max_results = null
max_connections = null
bins = null
histo = d3.layout.histogram().range([0, 200]).bins(20).value((d) -> d.score)

# our page view
window.timebook.views.search = $$ {},
    '''
    <div id="home">        
        <div class="page-header">
            <h2>Search Results for '<span id="query-title" data-bind="query"></span>'</h2>
        </div>
        
        <div class="row-fluid">
            <div class="span2" id="facets">
            </div>
            
            <div class="span6">
                <div class="btn-toolbar">
                    <div class="btn-group sort-controls" data-toggle="buttons-radio">
                        <button class="btn" id="btn-order-score" data-ordername="score" data-toggle="button"><i class="icon-signal"></i> Score</button>
                        <button class="btn" id="btn-order-alpha" data-ordername="alpha"><i class="icon-font"></i> Name</button>
                    </div>
                                    
                    <div class="btn-group view-controls" data-toggle="buttons-radio">
                        <a class="btn" href="#tab-list" data-toggle="tab"><i class="icon-th-list"></i> List</a>
                        <a class="btn" href="#tab-condensed" data-toggle="tab"><i class="icon-th"></i> Portraits</a>
                    </div>
                </div>
                
                <hr />
                    <div class="tabbable">
                        <div class="tab-content">
                            <div class="tab-pane active" id="tab-list"></div>
                            <div class="tab-pane" id="tab-condensed">
                                <div class="row-fluid">
                                    <ul class="thumbnails"></ul>
                                </div>
                            </div>
                        </div>
                    </div>

            </div>
            
            <div class="span4">
                <h3>Overviews</h3>
                <h4>How is the score distributed?</h3>
                <div class="score-distribution">
                </div>
                <h4>Score and Connections</h4>
                <div class="score-connections">
                </div>
            </div>    
        </div>

    </div>
    ''',
    'change': () ->
        query = @model.get('query')
        
        d3.json "/api/explore/?query=#{timebook.urlencode(query)}", (json) ->             
            settings = 
                items: json.users
                facets: 
                    categories: 'Categories'
                facetSelector: '#facets'
                updateResults: (results) ->
                    console.log results
                    
                    results_full(results)
                    results_condensed(results)
                    
                    bins = histo(results)
                    
                    if not max_results
                        max_results = d3.max(bins, (d) -> d.length)
                        max_connections = d3.max(results, (d) -> d.connections)
                        height_scale.domain([0, max_results * 1.1])
                        connection_scale.domain([0, max_connections * 1.1])
                    results_histogram(results)
                    score_connections(results)
      
            $.facetelize(settings)
            
            
            
            d3.selectAll('.sort-controls button').on('click', (e) -> 
                current_order = d3.select(@).attr('data-ordername')
                $.facetUpdate()
            )
 

    
# the templates

highlight_results_bin = (bin, highlight=true) ->
    min_score = bin * 10
    max_score = (bin + 1) * 10

    d3.select('#tab-list').selectAll('div.result')
        .filter((d,i) -> min_score <= +d.score < max_score)
        .attr('class', if highlight then 'result highlight' else 'result')
        
    d3.select('#tab-condensed').selectAll('li.result')
        .filter((d,i) -> min_score <= +d.score < max_score)
        .selectAll('div.thumbnail')
            .attr('class', if highlight then 'thumbnail highlight' else 'thumbnail')

    
highlight_result = (profile, highlight=true) ->
    d3.select('#tab-list').selectAll('div.result')
        .filter((d,i) -> d.id == profile.id)
        .attr('class', if highlight then 'result highlight' else 'result')
        
    d3.select('#tab-condensed').selectAll('li.result')
        .filter((d,i) -> d.id == profile.id)
        .selectAll('div.thumbnail')
            .attr('class', if highlight then 'thumbnail highlight' else 'thumbnail')

results_full_template = _.template '''
    <div class="row-fluid">
        <div class="profile-avatar span2">
            <img src="<%= avatar %>" />
        </div>
    
        <div class="profile-data span10">
            <h3><%= name %> <small><%= job_title %></small></h3>
            <p class="profile-surrogate"><%= surrogate %></p>
            <p><span class="badge badge-inverse"><%= score %></span></p>
        </div>
    </div>
    <hr />
'''

results_full = (results) ->
    div = d3.select('#tab-list').selectAll('div.result')
        .data(results, (e) -> e.id)
        
    div.enter()
        .append('div')
        .attr('class', 'result')
        .on('mouseover', (d) ->
            histogram_do_highlight_bin(d.score)
            highlight_bubble(d)
        )
        .on('mouseout', (d) -> 
            histogram_do_highlight_bin(d.score, false)
            highlight_bubble(d, false)
        )
        
    div.exit()
        .remove()
        
    div.html((d) -> results_full_template(d))

    div.sort(order_functions[current_order])
    
    div.selectAll('img')
        .each((d) -> 
            if d3.select(@).attr('src') == ''
                d3.select(@).attr('src', "http://placehold.it/#{120}x#{120}")
            else    
                $(@).error(() -> $(@).unbind("error").attr("src", "http://placehold.it/#{120}x#{120}"))
        )
        

results_condensed_template = _.template '''
        <div class="profile-data thumbnail">
            <img src="<%= avatar %>" />

            <h5><%= name %></h5>
            <p><span class="badge badge-inverse"><%= score %></span> <small><%= job_title %></small></p>
        </div>
'''

results_condensed = (results) ->
    li = d3.select('#tab-condensed ul.thumbnails').selectAll('li.result')
        .data(results, (e) -> e.id)
        
    li.enter()
        .append('li')
        .attr('class', 'result span3')
            
    li.exit()
        .remove()
        
    li.html((d) -> results_condensed_template(d))
    
    li.sort(order_functions[current_order])
    
    li.selectAll('img')
        .each((d) -> 
            if d3.select(@).attr('src') == ''
                d3.select(@).attr('src', "http://placehold.it/#{240}x#{240}")
            else    
                $(@).error(() -> $(@).unbind("error").attr("src", "http://placehold.it/#{240}x#{240}"))
        )


    
    
    
histogram_do_highlight_bin = (score, highlight=true) ->
    bin = Math.floor(score / 10)
    
    d3.selectAll('svg.histogram g.global rect.bin')
        .filter((d,i) -> i == bin)
        .attr('fill', if highlight then 'steelblue' else '#b77d38')
        .each((d) -> d.forEach (p) -> highlight_bubble(p, highlight))
    
results_histogram = (results) ->
    svg = d3.select('.score-distribution').selectAll('svg.histogram').data([1])
    
    svg.enter()
        .append('svg')
        .attr('class', 'histogram')
        .attr('width', width + 2 * x_padding)
        .attr('height', height)
        
    background = svg.selectAll('rect.background').data([1])
    
    background.enter()
        .append('rect')
            .attr('class', 'background')
            .attr('width', width - x_padding)
            .attr('height', height - y_padding)
            .attr('x', x_padding)
            .attr('y', 0)
        
    svg.selectAll('g.axis').data([1])
        .enter()
            .append("g")
            .attr("transform", "translate(#{x_padding},#{0})")
            .attr('class', 'x axis')
            .call(axis)
        
    g = svg.selectAll('g.global').data([1])
    
    g.enter()
        .append('g')
        .attr('class', 'global')
        .attr('transform', "translate(#{x_padding}, #{height - y_padding})scale(1, -1)")

    bar = g.selectAll('rect.bin').data(bins)
        
    bar.enter()
        .append('rect')
        .attr('class', 'bin')
        .attr('width', (width - x_padding) * 0.9 / 20)
        .attr('height', 0)
        .attr('fill', '#b77d38')
        .attr('x', (d,i) -> (width - x_padding) / 20 * i)
        .attr('y', 0)
        .on('mouseover', (d, i) ->
            histogram_do_highlight_bin(i * 10 + 1)
            highlight_results_bin(i)
        )
        .on('mouseout', (d, i) ->
            histogram_do_highlight_bin(i * 10 + 1, false)
            highlight_results_bin(i, false)
        )


    bar.transition()
        .delay(100)
        .attr('height', (d) -> height_scale(d.length))
        
        

highlight_bubble = (profile, highlight=true) ->    
    d3.selectAll('svg.bubbles g.global circle')
        .filter((d) -> d.id == profile.id)
        .transition(100)
        .attr('fill', if highlight then 'steelblue' else '#b77d38')
        

score_connections = (results) -> 
    svg = d3.select('.score-connections').selectAll('svg.bubbles').data([1])
    
    svg.enter()
        .append('svg')
        .attr('class', 'bubbles')
        .attr('width', width + 2 * x_padding)
        .attr('height', height)
    
    background = svg.selectAll('rect.background').data([1])
    
    background.enter()
        .append('rect')
            .attr('class', 'background')
            .attr('width', width - x_padding)
            .attr('height', height - y_padding)
            .attr('x', x_padding)
            .attr('y', 0)
        
        
    svg.selectAll('g.axis').data([1])
        .enter()
            .append("g")
            .attr("transform", "translate(#{x_padding},#{0})")
            .attr('class', 'x axis')
            .call(axis)
        
    g = svg.selectAll('g.global').data([1])

    g.enter()
        .append('g')
        .attr('class', 'global')
        .attr('transform', "translate(#{x_padding}, #{height - y_padding})scale(1, -1)")        

    bubbles = g.selectAll('circle.profile-bubble').data(results, (d) -> d.id)
        
    bubbles.enter()
        .append('circle')
        .attr('class', 'profile-bubble')
        .attr('r', bubble_radius)
        .attr('fill', '#b77d38')
        .attr('cx', 0)
        .attr('cy', 0)
        .on('mouseover', (d) ->
            highlight_bubble(d)
            highlight_result(d)
        )
        .on('mouseout', (d) ->
            highlight_bubble(d, false)
            highlight_result(d, false)
        )

    bubbles.transition()
        .delay(100)
        .attr('cx', (d) -> quantile(d.score))  
        .attr('cy', (d) -> connection_scale(d.connections)) 
        
    bubbles.exit()
        .remove()
        
