# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()
    """
    category='all'
    try:
        if (len(request.args) > 0):
            CATS.index(request.args[0])
            category=request.args[0]
        else:
            redirect(URL('index/all/1'))
    except ValueError:
        redirect(URL('index/all/1'))
        
    if (len(request.args) > 1 and request.args[1].isdigit() == True and int(request.args[1]) > 0):
        page_num = int(request.args[1])
    else:
        redirect(URL('index/'+category+'/1'))
    
    searching=False
    if len(request.args) > 2: 
        if (len(request.args[2]) > 7 and request.args[2][:7]=="search_"):
            search_terms=request.args[2][7:].split('_')
            searching=True
        else:
            redirect(URL('index/'+category+'/'+request.args[1]))
            
    if len(request.args) > 3:
        redirect(URL('index/'+category+'/1/'+request.args[2]))
    # print request.args[2][7:]
    # test_terms='book+meh+description'.split('+')
    
    db(db.listings.remove_date <= datetime.utcnow()).delete()
    
    cat_id=category
    if category == 'all':
        category='All'
        if searching:
            listdb=db(((db.listings.public==True) | (db.listings.public!=auth.is_logged_in())) & db.listings.content.contains(search_terms, all=True))
            #listdb=db(db.listings.description.contains(search_terms, all=True) | db.listings.title.contains(search_terms, all=True))
        else:
            listdb=db(((db.listings.public==True) | (db.listings.public!=auth.is_logged_in())))
    else:
        category=CATEGORIES[CATS.index(category)+1]   
        if searching:
            listdb=db((((db.listings.public==True) | (db.listings.public!=auth.is_logged_in())) & (db.listings.category==category)) & (db.listings.content.contains(search_terms, all=True)))
        else:
            listdb=db(((db.listings.public==True) | (db.listings.public!=auth.is_logged_in())) & (db.listings.category==category))
    
    page_length=len(listdb.select(db.listings.ALL))
        
    if page_length%9 == 0:
        page_length = page_length/9
    else:
        page_length = page_length/9+1
        
    if page_num > page_length:
        page_num = page_length
    
    limitrange = ((page_num-1)*9, (page_num)*9+1)
    if category == 'All':
        listings = listdb.select(db.listings.ALL, orderby=~db.listings.post_date, limitby=limitrange)
    else:
        listings = listdb.select(db.listings.ALL, orderby=~db.listings.post_date, limitby=limitrange)
    
    search=generate_search_form()
    if search.process().accepted:
        if len(search.vars.search) > 0:
            redirect(URL('index/'+cat_id+'/1/search_'+search.vars.search))
        else:
            redirect(URL('index/'+cat_id+'/'+request.args[1]))
            
#    response.flash = T("Welcome!")
    return dict(message=T('Shuttle-Stop'), listings=listings, page_length=page_length, page_num=page_num, category=category, search=search)
 
@auth.requires_login()  
def add():
    form = SQLFORM(db.listings)
#    desc = form.element('input', _name='description')
#    desc['_maxlength'] = '10'
    if form.process(onvalidation=form_check).accepted:
        session.flash = T('added!')
        redirect(URL('index/all/1'))
    return dict(form=form)
  
@auth.requires_login()   
def edit_posts():
    myposts=db(db.listings.user==auth.user_id).select(db.listings.ALL, orderby=~db.listings.post_date)
    return dict(myposts=myposts)
  
@auth.requires_login()  
def edit_post():
    listing = db.listings(request.args[0]) or redirect(URL('index/all/1'))
    if listing.user == auth.user_id:
        db.listings.remove_date.writable=False
        db.listings.title.writable=False
        db.listings.description.writable=False
        db.listings.public.writable=False
        db.listings.category.writable=False
        db.listings.image.readable=False
        db.listings.image.writable=False
        form = SQLFORM(db.listings, db.listings[request.args(0)], deletable=True, readable=True)
        form.element(_type='submit')['_value']='Done'
        if form.process().accepted:
            response.flash='edit complete'
            redirect(URL('edit_posts'))
        return dict(form=form, image=listing.image)
    else:
        redirect(URL('index/all/1'))
   
def form_check(form):
    try:
        rdate=datetime.strptime(form.vars.remove_date.split('.')[0], '%Y-%m-%d %H:%M:%S')
        pdate=datetime.utcnow()
        if rdate > pdate + timedelta(27,0):
            form.errors.remove_date = 'too far in future'
        elif rdate < pdate:
            form.errors.remove_date = 'requires future date'
    except ValueError:
        form.errors.remove_date = 'invalid date'
    if form.vars.category == CATEGORIES[0] or form.vars.category == CATEGORIES[1]:
        form.errors.category = 'value not allowed'
        
    form.vars.content=form.vars.title+' '+form.vars.description

@auth.requires_login()
def listing():
    try:
        if (len(request.args) > 0):
            listing = db.listings(request.args[0]) or redirect(URL('index/all/1'))
            user=db(db.auth_user.id==listing.user).select(db.auth_user.ALL)[0]
            # print type(username)
            return dict(listing=listing, username=user.username, email=user.email)
        else:
            redirect(URL('index/all/1'))
    except ValueError:
        redirect(URL('index/all/1'))

def generate_search_form():
    form=FORM(TR(TD(LABEL('Search: ', _style="position:relative; bottom:4px;"), 
        INPUT(_name='search', _id='search', _style="width:100px;"),
        INPUT(_type='submit', _value='Go', _style="position:relative; width:30px; bottom:4px;")))
    )   
    return form

def generate_listing():
    return TD(DIV(H5('Listing Title'), P('description: Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.'), A('Contact me!', _href='http://en.wikipedia.org')), _style='background:beige; border:4px solid white;')

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
