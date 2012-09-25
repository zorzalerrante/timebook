window.timebook ?= {}
window.timebook.views ?= {}

timebook = window.timebook

window.timebook.views.category = $$({}, 
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
        container = d3.select(@view.$('div.members')[0])
        
        @view.$('h2').text(category.fields.name)
        
        timebook.draw_profile_list(container, members)
        @view.$('img.thumbnail').error(() -> $(@).unbind("error").attr("src", "http://placehold.it/#{120}x#{120}"))

)