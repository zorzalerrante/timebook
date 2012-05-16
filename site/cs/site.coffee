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

# the elements of the page

container = $$({},
    '''
    <div class="container-fluid">

    </div>
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
                <form class="navbar-search pull-left">
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
    <div class="page-header">
        <h2 />
        <p class="abstract" data-bind="abstract" />
    </div>
    <div class="row-fluid">
        <div class="span3 profile">
            <ul class="thumbnails"><li><a><img class="thumbnail depiction" data-bind="src depiction" /></a></li></ul>
            <div class="works" />
        </div>
        <div class="span5 connections">
            <ul class="links">
                <li class="dbpedia-link">&rarr;<a href="" data-bind="href uri">See <span data-bind="name"/> on DBPedia</a></li>
            </ul>
            <div class="following"/>
            <div class="followers"/>
        </div>
        <div class="span4 categories">
            <div class="groups"/>
        </div>
    </div>
    ''',
     
    '''
    & .abstract { font-style: italic; color: #777777; }
    & .profile  img.thumbnail { max-width: 210px; }
    & .connections img.thumbnail { max-height: 45px; }
    ''',   
         
    'change': () ->    
        data = @model.get()
        console.log data
        console.log @view.$('h2')
        
        @view.$('h2').text(data.fields.name)
        
    
        append_list = (elements, selection, ul_class, title, link_func) ->
            if elements? and elements.length? and elements.length > 0
                selection.append("<h3>#{title}</h3>")
                ul = $("<ul class=\"#{ul_class}\"/>").appendTo(selection)
                console.log ul
                for e in elements
                    ul.append("<li>#{link_func(e)}</li>")
            
        append_list(data.followers, @view.$('.followers'), 'thumbnails', 'Followers', 
          (e) -> "<a class=\"profile_link\" href=\"#profile#{e.pk}\" title=\"#{e.fields.name}\"><img class=\"thumbnail\" src=\"#{e.fields.depiction}\" /></a>"
        )
        
        append_list(data.following, @view.$('.following'), 'thumbnails', 'Following', 
          (e) -> "<a class=\"profile_link\" href=\"#profile#{e.pk}\" title=\"#{e.fields.name}\"><img class=\"thumbnail\" src=\"#{e.fields.depiction}\" /></a>"
        )
        
        @view.$('.profile_link').tooltip()
        @view.$('.profile_link').click((e) -> $(@).tooltip('hide'))
        
        @view.$('img.thumbnail').error(() -> $(@).unbind("error").attr("src", "http://placehold.it/#{90}x#{90}"))
        
        
        append_list(data.groups, @view.$('.groups'), 'nav nav-tabs nav-stacked', 'Groups', 
          (e) -> "<a class=\"category_link\" href=\"#category#{e.pk}\">#{e.fields.name}</a>"
        )
        
        append_list(data.works, @view.$('.works'), 'unstyled', 'Works', 
          (e) -> "<a class=\"work_link\" href=\"#work#{e.pk}\">#{e.fields.name}</a>"
        )

    'change:depiction': () -> @view.$('img.depiction').error(() -> $(@).unbind("error").attr("src", "http://placehold.it/#{210}x#{240}"))
      
)


category = $$({}, 
    '''
    <div class="row-fluid">
      <div class="span12">
        <h2 data-bind="name"/>
        <div class="members"></div>
      </div>
    </div>
    ''',
     
    '''
    & .members img.thumbnail { max-height: 120px; }
    ''',   
         
    'change': () ->
        console.log 'category'
        members = @model.get('members')
        console.log members
        ul = $('<ul class="media-grid"/>').appendTo(@view.$('div.members'))
        console.log ul
        
        for e in members
            ul.append("<li><a class=\"profile_link\" href=\"#profile#{e.pk}\" title=\"#{e.fields.name}\"><img class=\"thumbnail\" src=\"#{e.fields.depiction}\" /></a></li>")

        @view.$('.profile_link').tooltip()
        @view.$('.profile_link').click((e) -> $(@).tooltip('hide'))
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

header.view.$("#tags").typeahead(
    ajax: 
        url: "/api/search/"
        method: "GET"
        preProcess: (data) ->
            links = ("<a href=\"##{result.type}#{result.id}\">#{result.name}</a>" for result in data)
            links
    updater: (item) -> 
        re = /href=\"(.+)\"/ig
        parts = re.exec(item)
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
    
