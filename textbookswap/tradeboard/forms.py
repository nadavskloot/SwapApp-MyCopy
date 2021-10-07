from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator, MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Post, Message
# ************************************************************************
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Least, Greatest
# ************************************************************************


class BookSearchForm(forms.Form):
    title = forms.CharField(label="Title", max_length=100, required=False, validators=[MaxLengthValidator(100)],
                            widget=forms.TextInput(attrs={'class': "filter-text-input text-input-field", 'placeholder': ':############# ######## ######'}))

    def validate_digit(value):
        if (value != None and (len(value) != 10 and len(value) != 13)):
            print(value)
            raise ValidationError(f'Number of digits in "{value}"" is neither 10 nor 13',
                                  params={'value': value},
                                  )

    def validate_numeric(value):
        if (not(f'{value}'.isnumeric())):
            raise ValidationError(f'"{value}" Has non-numeric elements',
                                  params={'value': value},
                                  )

    ISBN = forms.CharField(label="ISBN", max_length=13,
                           validators=[validate_digit, validate_numeric], required=False, widget=forms.TextInput(attrs={'class': "filter-text-input text-input-field", 'placeholder': ':##########'}))

    author = forms.CharField(label="Author", max_length=50, required=False, validators=[MaxLengthValidator(50)],
                             widget=forms.TextInput(attrs={'class': "filter-text-input text-input-field", 'placeholder': ':##########'}))

    edition = forms.IntegerField(
        label="Edition", min_value=1, max_value=100, validators=[MinValueValidator(1), MaxValueValidator(100)], required=False, widget=forms.NumberInput(attrs={'class': "filter-int-input int-input-field", 'placeholder': ':##########'}))

    price = forms.IntegerField(
        label="Maximum price", min_value=1, max_value=400, validators=[MaxValueValidator(400)], required=False, widget=forms.NumberInput(attrs={'class': "filter-int-input int-input-field", 'placeholder': ':##########'}))

    # **************************************************************************************************************************************************************************
    MONTHS = {
        1: _('Jan'), 2: _('Feb'), 3: _('Mar'), 4: _('Apr'),
        5: _('May'), 6: _('Jun'), 7: _('Jul'), 8: _('Aug'),
        9: _('Sep'), 10: _('Oct'), 11: _('Nov'), 12: _('Dec')
    }
    posted_since = forms.DateField(
        label='posted since, ', widget=forms.SelectDateWidget(attrs={'class': "filter-date-select"}, months=MONTHS, empty_label=['----', '---', '--']), required=False)

    # **************************************************************************************************************************************************************************
    OTHER = "Other"
    TEXTBOOK = "Textbook"
    post_types = (
        (OTHER, "Other"),
        (TEXTBOOK, "Textbook"),
    )
    post_type = forms.ChoiceField(
        label='book type, ', initial="Other", widget=forms.Select(attrs={'class': "filter-type-select type-select-field"}), required=False, choices=post_types)

    # **************************************************************************************************************************************************************************

    DATE_POSTED = "-date_posted"
    PRICE = "price"
    EDITION = "edition"
    TITLE = "title"
    AUTHOR = "author"
    RELEVANCE = "-similarity"
    sort_types = (
        (DATE_POSTED, "Date Posted"),
        (PRICE, "Price"),
        (EDITION, "Edition"),
        (TITLE, "Title"),
        (AUTHOR, "Author"),
        (RELEVANCE, "Relevance")
    )
    sort_by = forms.ChoiceField(
        label='book type, ', initial=DATE_POSTED, widget=forms.Select(attrs={'class': "filter-type-select type-select-field"}), required=False, choices=sort_types)
    # **************************************************************************************************************************************************************************

    def filter(self):
        search_filters = self.cleaned_data
        posts = Post.objects.all()
        filtered = False
        if search_filters['author'] and search_filters['title']:
            filtered = True
            func = (TrigramSimilarity(
                'author', search_filters['author']) + TrigramSimilarity(
                'title', search_filters['title']))
            posts = posts.annotate(similarity=func).filter(similarity__gt=0.3)
        else:
            if search_filters['author']:
                filtered = True
                posts = posts.annotate(similarity=TrigramSimilarity(
                    'author', search_filters['author'])).filter(similarity__gt=0.3)
            if search_filters['title']:
                filtered = True
                posts = posts.annotate(similarity=TrigramSimilarity(
                    'title', search_filters['title'])).filter(similarity__gt=0.3)

        if search_filters['ISBN']:
            if(filtered):
                posts = posts | Post.objects.filter(
                    ISBN=search_filters['ISBN'])
            else:
                posts = Post.objects.filter(
                    ISBN=search_filters['ISBN'])
        if search_filters['edition']:
            posts = posts.filter(edition=search_filters['edition'])
        if search_filters['price']:
            posts = posts.filter(price__lte=search_filters['price'])
        if search_filters['posted_since']:
            posts = posts.filter(
                date_posted__gte=search_filters['posted_since'])
        if search_filters['sort_by'] == "-similarity":
            if search_filters['author'] or search_filters['title']:
                return(posts.order_by(search_filters['sort_by']))
            else:
                return(posts.order_by("-date_posted"))
        else:
            return(posts.order_by(search_filters['sort_by']))

# *********************************************************************************************************************************************************************************


class BookSellForm(forms.ModelForm):
    title = forms.CharField(label="Title", max_length=100, required=True, validators=[MaxLengthValidator(100)],
                            widget=forms.TextInput(attrs={'class': "post-text-input text-input-field", 'placeholder': ':# # ########### ######## ###### ## ########### ######## ######'}))

    def validate_digit(value):
        if (value != None and (len(value) != 10 and len(value) != 13)):
            print(value)
            raise ValidationError(f'Number of digits in "{value}"" is neither 10 nor 13',
                                  params={'value': value},
                                  )

    def validate_numeric(value):
        if (not(f'{value}'.isnumeric())):
            raise ValidationError(f'"{value}" Has non-numeric elements',
                                  params={'value': value},
                                  )

    ISBN = forms.CharField(label="ISBN", max_length=13,
                           validators=[validate_digit, validate_numeric], required=True, widget=forms.TextInput(attrs={'class': "post-text-input text-input-field", 'placeholder': ':##########'}))

    author = forms.CharField(label="Author", max_length=50, required=True, validators=[MaxLengthValidator(50)],
                             widget=forms.TextInput(attrs={'class': "post-text-input text-input-field", 'placeholder': ':####### # ##### ### # #####'}))

    description = forms.CharField(label="Description", max_length=350, required=True, validators=[MaxLengthValidator(350)],
                                  widget=forms.Textarea(attrs={'class': "input-description text-input-field"}))

    image = forms.ImageField(label="Image", required=False, widget=forms.FileInput(
        attrs={'class': 'image-input', 'onchange': 'upload_img(this);'}))

    edition = forms.IntegerField(
        label="Edition", min_value=1, max_value=100, required=True, validators=[MinValueValidator(1), MaxValueValidator(100), validate_numeric], widget=forms.NumberInput(attrs={'class': "post-int-input int-input-field", 'placeholder': ':##########'}))
    price = forms.IntegerField(
        label="Maximum price", min_value=1, max_value=400, required=True, validators=[MaxValueValidator(400), validate_numeric], widget=forms.NumberInput(attrs={'class': "post-int-input int-input-field", 'placeholder': ':##########'}))

    OTHER = "Other"
    TEXTBOOK = "Textbook"
    post_types = (
        (OTHER, "Other"),
        (TEXTBOOK, "Textbook"),
    )
    post_type = forms.ChoiceField(
        label='book type, ', initial="Other", widget=forms.Select(attrs={'class': "post-type-select type-select-field"}), required=False, choices=post_types)

    class Meta:
        model = Post
        fields = ('title', 'ISBN', 'author', 'description',
                  'image', 'edition', 'price', 'post_type')


class MessagingForm(forms.ModelForm):
    text = forms.CharField(label="message-text", max_length=250, validators=[MaxLengthValidator(250)],
                           widget=forms.Textarea(attrs={'class': "message-text-input-field", 'placeholder': 'Type a message', "max_length": "250", "rows": 2, 'autofocus': 'autofocus'}))
    image = forms.ImageField(label="message image", required=False, widget=forms.FileInput(
        attrs={'class': 'message-image-input-field invisible', 'onchange': 'previewMsgImg(this);'}))
    offer = forms.IntegerField(label="Offered price", required=False, widget=forms.NumberInput(
        attrs={'class': "message-offer-input-field"}))

    class Meta:
        model = Message
        fields = ('text', 'image', 'offer')
