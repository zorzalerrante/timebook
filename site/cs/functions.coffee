# helper functions
window.timebook ?= {}

timebook = window.timebook

timebook.append_list = (elements, selection, ul_class, title, link_func) ->
    if elements? and elements.length? and elements.length > 0
        selection.append("<h3>#{title}</h3>")
        ul = $("<ul class=\"#{ul_class}\"/>").appendTo(selection)
        console.log ul
        for e in elements
            ul.append("<li>#{link_func(e)}</li>")

timebook.draw_profile_list = (parent, members, class_name='member') ->
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
        
timebook.draw_work_list = (parent, works, class_name='work') ->
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
        .text((d) -> d.fields.name)
        
    

# get url params
timebook.get_query_vars = () ->
    vars = {}
    hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&')

    for pair in hashes
        hash = pair.split('=')
        vars[hash[0]] = hash[1]

    vars
    
# urldecode
# from http://stackoverflow.com/questions/3431512/javascript-equivalent-to-phps-urldecode

timebook.urldecode = (str) -> decodeURIComponent(str.replace(/\+/g, ' '))
timebook.urlencode = (str) -> encodeURIComponent(str)