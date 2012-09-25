window.timebook ?= {}
window.timebook.views ?= {}

timebook = window.timebook

window.timebook.views.person = $$({}, 
    '''
    <div class="row-fluid">
        <div class="span3 profile">
            <ul class="thumbnails"><li><a><img class="thumbnail depiction" src="http://placehold.it/240x270" /></a></li></ul>
        </div>
        <div class="span9">
            <div class="page-header">
                <h2 />
                <p class="abstract"/>
            </div>
            <div class="tabbable">
                <ul class="nav nav-tabs">
                    <li class="active"><a href="#tab-connections" data-toggle="tab"><i class="icon icon-random"></i> Connections</a></li>
                    <li><a href="#tab-works" data-toggle="tab"><i class="icon-picture"></i> Works</a></li>
                    <li><a href="#tab-groups" data-toggle="tab"><i class="icon-th"></i> Groups</a></li>
                    <li><a href="#tab-quotes" data-toggle="tab"><i class="icon-comment"></i> Quotes</a></li>
                </ul>
                <div class="tab-content">
                    <div class="tab-pane active" id="tab-connections"></div>
                    <div class="tab-pane" id="tab-works"></div>
                    <div class="tab-pane" id="tab-groups"></div>
                    <div class="tab-pane" id="tab-quotes"></div>
                </div>
            </div>
        </div>
    </div>
    ''',
     
    '''
    & .abstract { font-style: italic; color: #777777; }
    & .profile  img.thumbnail { max-width: 270px; }
    & #tab-connections img.thumbnail { max-height: 45px; max-width: 90%; }
    & #tab-works .thumbnail img { max-width: 120px; }
    & div.member { margin-bottom: 1em; }
    & div.work { margin-bottom: 1em; }
    ''',   
         
    'change': () ->    
        data = @model.get()
        console.log data
        console.log @view.$('h2')
        
        @view.$('h2').text(data.fields.name)
        @view.$('p.abstract').text(data.abstract)
        
        if data.fields.depiction
            @view.$('img.depiction').attr('src', data.fields.depiction)
                
        connections_div = d3.select(@view.$('#tab-connections')[0]).append('div').attr('class', 'row-fluid')
        
        following_div = connections_div.append('div').attr('class', 'span6')
        following_div.append('h3').text('Following')
        timebook.draw_profile_list(following_div, data.following)
        
        followers_div = connections_div.append('div').attr('class', 'span6')
        followers_div.append('h3').text('Followers')
        timebook.draw_profile_list(followers_div, data.followers)
                              
        @view.$('#tab-connections img.thumbnail').error(() -> $(@).unbind("error").attr("src", "http://placehold.it/#{90}x#{90}"))
        @view.$('img.thumbnail').error(() -> $(@).unbind("error").attr("src", "http://placehold.it/#{240}x#{270}"))
        
        
        timebook.append_list(data.groups, @view.$('#tab-groups'), 'nav nav-tabs nav-stacked', 'Groups', 
          (e) -> "<a class=\"category_link\" href=\"#category#{e.pk}\">#{e.fields.name}</a>"
        )
        
        works_div = d3.select(@view.$('#tab-works')[0]).append('div').attr('class', 'row-fluid')
        timebook.draw_work_list(works_div, data.works)
        
        @view.$('#tab-works img.thumbnail').error(() -> $(@).unbind("error").attr("src", "http://placehold.it/#{120}x#{120}"))
        
        for quote in data.quotes
            @view.$('#tab-quotes').append("<blockquote><p>#{quote.fields.content}</p></blockquote>")

)
