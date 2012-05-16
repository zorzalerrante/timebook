from django.db import models

# Create your models here.

class Interest(models.Model):
    facebook_id = models.CharField(db_index=True, max_length=255)
    name = models.CharField(max_length=255, db_index=True)
    category = models.CharField(max_length=255, db_index=True)
    field = models.CharField(max_length=255, db_index=True)

class User(models.Model):
    facebook_id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255)

    gender = models.CharField(max_length=255)
    last_updated = models.DateTimeField(auto_now=True)
    profile_url = models.CharField(max_length=255)
    website = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    locale = models.CharField(max_length=30)
    interests = models.ManyToManyField(Interest, db_index=True)
    
    def read_json(self, json):
        print json
        self.facebook_id = json['id']
        
        try:
            self.name = json['name']
        except KeyError:
            pass
          
        try:  
            self.first_name = json['first_name']
        except KeyError:
            pass
        
        try:
            self.last_name = json['last_name']
        except KeyError:
            pass
            
        try:
            self.user_name = json['username']
        except KeyError:
            pass
        
        try:
            self.profile_url = json['link']
        except KeyError:
            pass
        
        try:
            self.gender = json['gender']
        except KeyError:
            pass
        
        try:
            self.email = json['email']
        except KeyError:
            pass
        
        try:
            self.website = json['website']
        except KeyError:
            pass
        
        try:
            self.locale = json['locale']
        except KeyError:
            pass

    