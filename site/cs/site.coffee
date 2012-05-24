# helper functions

append_list = (elements, selection, ul_class, title, link_func) ->
    if elements? and elements.length? and elements.length > 0
        selection.append("<h3>#{title}</h3>")
        ul = $("<ul class=\"#{ul_class}\"/>").appendTo(selection)
        console.log ul
        for e in elements
            ul.append("<li>#{link_func(e)}</li>")

draw_profile_list = (parent, members, class_name='member') ->
    member = parent.selectAll("div.#{class_name}").data(members)

    member.exit().remove()

    div = member.enter()
        .append('div').attr('class', class_name)
    
    row = div.append('div').attr('class', 'row-fluid')
    
    row.append('div').attr('class', 'span2')
        .append('img')
            .attr('src', (d) -> if d.fields.depiction then d.fields.depiction else "http://placehold.it/90x90")
            .attr('class', 'thumbnail pull-left')
       
    right = row.append('div').attr('class', 'span10')
    
    right.append('h3')
        .append('a')
        .text((d) -> d.fields.name)
        .attr('href', (d) -> "#profile#{d.pk}")
        
    right.append('p')
        .text((d) -> 
            if d.fields.birth_year and d.fields.death_year
                "#{d.fields.birth_year} - #{d.fields.death_year}"
            else if d.fields.birth_year
                "#{d.fields.birth_year}"
            else if d.fields.death_year
                "- #{d.fields.death_year}"
            else
                null
        )
        
draw_work_list = (parent, works, class_name='work') ->
    work = parent.selectAll("div.#{class_name}").data(works)

    work.exit().remove()

    div = work.enter()
        .append('div').attr('class', class_name)
    
    row = div.append('div').attr('class', 'row-fluid')
    
    row.append('div').attr('class', 'span2')
        .append('img')
            .attr('src', (d) -> if d.fields.depiction then d.fields.depiction else "http://placehold.it/90x90")
            .attr('class', 'thumbnail pull-left')
       
    right = row.append('div').attr('class', 'span10')
    
    right.append('h3')
        .append('a')
        .text((d) -> d.fields.name)
        .attr('href', (d) -> "#profile#{d.pk}")
# the elements of the page

container = $$({},
    '''
    <div class="container-fluid"></div>
    '''
)

header = $$({},
    '''
    <div class="navbar navbar-fixed-top" data-scrollspy="scrollspy">
        <div class="navbar-inner">
            <div class="container-fluid">
                <a class="brand" href="">TimeBook</a>
                <ul class="nav">  
                  <li><div id="fb-root"></div><div class="fb-login-button" id="login"></div></li>
                </ul>
                <form class="navbar-search pull-right">
                  <input id="tags" placeholder="Search" />
                </form>
                </div>
            </div>
        </div>
    </div>
    ''',
    'click #login': () ->
        return unless FB?
        console.log 'clicked'
        if fb_is_logged_in 
            fb_logout (response) -> 
                console.log 'fb_logout'
                console.log response
                fb_is_logged_in = false
        else 
            fb_login (response) -> 
                console.log 'fb_login'
                console.log response
                fb_is_logged_in = true
)

list = $$({}, '<div><div class="content"></div> </div>')

# our entities

person = $$({}, 
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
                    <li><a href="#tab-works" data-toggle="tab"><i class="icon icon-picture"></i> Works</a></li>
                    <li><a href="#tab-groups" data-toggle="tab"><i class="icon icon-th"></i> Groups</a></li>
                    <li><a href="#tab-quotes" data-toggle="tab"><i class="icon icon-comment"></i> Quotes</a></li>
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
        draw_profile_list(following_div, data.following)
        
        followers_div = connections_div.append('div').attr('class', 'span6')
        followers_div.append('h3').text('Followers')
        draw_profile_list(followers_div, data.followers)
                              
        @view.$('#tab-connections img.thumbnail').error(() -> $(@).unbind("error").attr("src", "http://placehold.it/#{90}x#{90}"))
        @view.$('img.thumbnail').error(() -> $(@).unbind("error").attr("src", "http://placehold.it/#{240}x#{270}"))
        
        
        append_list(data.groups, @view.$('#tab-groups'), 'nav nav-tabs nav-stacked', 'Groups', 
          (e) -> "<a class=\"category_link\" href=\"#category#{e.pk}\">#{e.fields.name}</a>"
        )
        
        works_div = d3.select(@view.$('#tab-works')[0]).append('div').attr('class', 'row-fluid')
        draw_work_list(works_div, data.works)
        
        @view.$('#tab-works img.thumbnail').error(() -> $(@).unbind("error").attr("src", "http://placehold.it/#{120}x#{120}"))
        
        for quote in data.quotes
            @view.$('#tab-quotes').append("<blockquote><p>#{quote.fields.content}</p></blockquote>")

)


category = $$({}, 
    '''
    <div class="row-fluid">
      <div class="span12">
        <div class="page-header">
            <h2></h2>
        </div>
      </div>
      <div class="row-fluid">
            <div class="members span12"></div>
      </div>
    </div>
    ''',
     
    '''
    & .members img.thumbnail { max-height: 120px; }
    & div.member { margin-bottom: 1em; }
    ''',   
         
    'change': () ->
        console.log 'category'
        category = @model.get() 
        console.log category
        members = @model.get('members')
        console.log members
        #ul = $('<ul class="media-grid"/>').appendTo(@view.$('div.members'))
        #console.log ul
        #console.log @view.$('div.members')
        
        container = d3.select(@view.$('div.members')[0])
        
        @view.$('h2').text(category.fields.name)
        
        draw_profile_list(container, members)
        '''
        list = d3.select(@view.$('div.members')[0]).append('ul').attr('class', 'thumbnails')
        
        for e in members
            container = list.append('li')
            container.append('div').attr('class', 'span3 thumbnail')
                .append('a').attr('class', 'profile_link').attr('href', "#profile#{e.pk}").attr('title', e.fields.name)
                .append('img').attr('class', 'thumbnail').attr('src', e.fields.depiction)
                
            bio_data = container.append('div').attr('class', 'span9')
                
            bio_data.append('h3').text(e.fields.name)
            
            #list.append("<li><a class=\"profile_link\" href=\"#profile#{e.pk}\" title=\"#{e.fields.name}\"><img class=\"thumbnail\" src=\"#{e.fields.depiction}\" /></a></li>")

        @view.$('.profile_link').tooltip()
        @view.$('.profile_link').click((e) -> $(@).tooltip('hide'))
        '''
        @view.$('img.thumbnail').error(() -> $(@).unbind("error").attr("src", "http://placehold.it/#{120}x#{120}"))

)

# these variables and functions define what is being displayed

current = 1
current_item = null

show_person = (person_id) ->
    if current_item? then current_item.destroy()
    current_item = $$(person, {id:person_id}).persist($$.adapter.restful, 
        collection: 'profile'
        baseUrl: '/api/'
    ).load()
    list.append(current_item, '.content')

show_category = (category_id) ->
    if current_item? then current_item.destroy()
    current_item = $$(category, {id:category_id}).persist($$.adapter.restful, 
        collection: 'category'
        baseUrl: '/api/'
    ).load()
    list.append(current_item, '.content')  
    
prepare_content = () ->
    pid = window.location.hash.match(/\#profile([0-9]+)/)
    console.log pid
    if pid? then show_person(pid[1])
  
    cid = window.location.hash.match(/\#category([0-9]+)/)
    console.log cid
    if cid? then show_category(cid[1])

# our structure

container.append(list)

$$.document.append(header)
$$.document.append(container)

# we test the content
prepare_content()

# our content depends on the hash on the page
$(window).bind('hashchange', (e) -> prepare_content())

# the autocomplete search

icons = {'profile': 'user', 'category': 'th'}
header.view.$("#tags").typeahead(
    ajax: 
        url: "/api/search/"
        method: "GET"
        preProcess: (data) ->
            links = []
            links = ("<a href=\"##{result.type}#{result.id}\"><i class=\"icon icon-#{icons[result.type]}\"></i> #{result.name}</a>" for result in data)
            links
    updater: (item) -> 
        re = /href=\"(.+)\"><i/ig
        parts = re.exec(item)
        console.log parts
        window.location.hash = parts[1]
        ''
)

# facebook login

fb_ping_timebook = (user_id) ->
    $.ajax
        url: "/api/user/login/?uid=#{user_id}"
        dataType: 'json'
        success: (json) ->
            if not json.status? or json.status != 'ok' 
                console.log 'invalid'
                console.log json
                console.log json.status
                return
            header.view.$('#login').text("<a href=\"\">#{json.data.name}</a>")
            console.log json
 
#some helper facebook functions

fb_init = () ->
    FB.init
        appId      : '389305971111798'
        status     : true
        cookie     : true
        xfbml      : true
   
fb_is_logged_in = false 

fb_check_status = (callback) -> if FB? then FB.getLoginStatus(callback)

fb_login = (callback) -> FB.login(callback, 
    scope: "user_about_me,user_interests,user_likes,email"
    perms: "user_about_me,user_interests,user_likes,email"
)

fb_logout = (callback) -> FB.logout(callback)   

# do the facebook integration. disabled for now
'''
fb_init()

fb_check_status (response) -> 
    if response.status? and response.status == 'connected'
        header.view.$('#login').text('<a href="">Logout</a>')
        fb_is_logged_in = true
        fb_ping_timebook(response.session.uid)
    else
        header.view.$('#login').text('<a href="">Login</a>')
        fb_is_logged_in = false

FB.Event.subscribe 'auth.login', (response) ->  
    fb_ping_timebook(response.session.uid)
    fb_is_logged_in = true

FB.Event.subscribe 'auth.logout', (response) ->
    header.view.$('#login').text('<a href="">Login</a>')
'''

