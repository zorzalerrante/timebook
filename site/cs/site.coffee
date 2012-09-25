# the elements of the page

container = $$({},
    '''
    <div class="container-fluid"></div>
    '''
)

window.timebook ?= {}
timebook = window.timebook

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



# these variables and functions define what is being displayed

current = 1
current_item = null

show_person = (person_id) ->
    if current_item? then current_item.destroy()
    current_item = $$(timebook.views.person, {id: person_id}).persist($$.adapter.restful, 
        collection: 'profile'
        baseUrl: '/api/'
    ).load()
    list.append(current_item, '.content')

show_category = (category_id) ->
    if current_item? then current_item.destroy()
    console.log category_id
    current_item = $$(timebook.views.category, {id: category_id}).persist($$.adapter.restful, 
        collection: 'category'
        baseUrl: '/api/'
    ).load()
    list.append(current_item, '.content')  
    
show_other = (other, model={}) ->
    if current_item? then current_item.destroy()
    current_item = $$(other, model)
    current_item.view.sync()
    
    window.item = current_item
    list.append(current_item, '.content')
    current_item.trigger('change')

    

    
prepare_content = () ->
    hash = window.location.hash
    pid = hash.match(/\#profile([0-9]+)/)
    console.log pid
    if pid?
        show_person(pid[1])
        return
  
    cid = hash.match(/\#category([0-9]+)/)
    console.log cid
    if cid?
        show_category(cid[1])
        return 
        
    is_search = hash.match(/\#search\?q=([^&.]+)&?/)
    console.log is_search
    if is_search?
        query = $('#tags').attr('value')
        if not query
            $('#tags').attr('value', timebook.urldecode(is_search[1]))
        show_other(timebook.views.search, {'query': $('#tags').attr('value')})
        return
        
    show_other(timebook.views.home)

# our structure

container.append(list)

$$.document.append(header)
$$.document.append(container)

# configure _'s template

#_.templateSettings = {
#  interpolate : /\{\{(.+?)\}\}/g
#}

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
            query = $('#tags').attr('value')
            links = []
            links = ("<a href=\"##{result.type}#{result.id}\"><i class=\"icon icon-#{icons[result.type]}\"></i> #{result.name}</a>" for result in data)
            links.unshift("<a href=\"#search?q=#{encodeURIComponent(query)}\"><i class=\"icon-search\"></i> Search for <strong>#{query}</strong></a>")
            links
            
    updater: (item) -> 
        re = /href=\"(.+)\"><i/ig
        parts = re.exec(item)
        console.log parts
        query = $('#tags').attr('value')
        window.location.hash = parts[1]
        console.log item
        query
        
    sorter: (items) -> items
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

