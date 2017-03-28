from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from datetime import datetime
from django.db.models import Q, Max, Min, Count, Sum
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template import Context, loader
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django_filters import FilterSet, CharFilter, NumberFilter


from analytics.models import ProductAnalytics
from taggit.models import Tag

from .forms import VariationInventoryFormSet, ProductFilterForm
from .mixins import StaffRequiredMixin, FilterMixin
from .models import Product, Variation, Category


template_vars = {

}


def xml_latest(request):
    """
    returns an XML of the most latest posts
    """
    template_vars['products'] = Product.objects.all()

    # TODO: Burada henüz domain çalışmıyorkenki URL 'yi de koymayı unutma...
    if settings.DEBUG:
        domain = 'http://127.0.0.1:8000'
    else:
        domain = 'http://www.istebu.com'

    template_vars['domain'] = domain

    t = loader.get_template('products/xml/products.xml')
    c = Context(template_vars)

    return HttpResponse(t.render(c), content_type="text/xml")


# aşağıdaki view filtreleri context olarak gönderemiyor. Dolayısıyla
def product_list_by_tag(request, tag_slug=None):
    object_list = Product.objects.all()  # This is automatically returns active products.
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 9)  # 3 products in each page
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver the last page of results
        products = paginator.page(paginator.num_pages)

    return render(request, 'products/product_list.html', {'page': page,
                                                          'page_products': products,
                                                          'tag': tag,
                                                          'section': "Products"})


class CategoryListView(ListView):
    model = Category
    queryset = Category.objects.all()
    template_name = "products/products.html"
    # product_list.html vardı burada, tabii object olarak product göndermiyordu ve hata veriyordu.


class CategoryDetailView(DetailView):
    model = Category

    def get_context_data(self, *args, **kwargs):
        context = super(CategoryDetailView, self).get_context_data(*args, **kwargs)
        obj = self.get_object()
        product_set = obj.product_set.all()
        default_products = obj.default_category.all()
        products = (product_set | default_products).distinct()
        context["products"] = products
        return context


class VariationListView(StaffRequiredMixin, ListView):
    model = Variation
    queryset = Variation.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(VariationListView, self).get_context_data(*args, **kwargs)
        context["formset"] = VariationInventoryFormSet(queryset=self.get_queryset())
        return context

    def get_queryset(self, *args, **kwargs):
        product_pk = self.kwargs.get("pk")
        if product_pk:
            product = get_object_or_404(Product, pk=product_pk)
            queryset = Variation.objects.filter(product=product)
        return queryset

    def post(self, request, *args, **kwargs):
        formset = VariationInventoryFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save(commit=False)
            for form in formset:
                new_item = form.save(commit=False)
                # if new_item.title:
                product_pk = self.kwargs.get("pk")
                product = get_object_or_404(Product, pk=product_pk)
                new_item.product = product
                new_item.save()

            messages.success(request, "Your inventory and pricing has been updated.")
            return redirect("products")
        raise Http404


class ProductFilter(FilterSet):
    title = CharFilter(name='title', lookup_type='icontains', distinct=True)
    category = CharFilter(name='categories__title', lookup_type='icontains', distinct=True)
    # category_id = CharFilter(name='categories__id', lookup_type='icontains', distinct=True)
    min_price = NumberFilter(name='variation__price', lookup_type='gte', distinct=True)  # (some_price__gte=somequery)
    max_price = NumberFilter(name='variation__price', lookup_type='lte', distinct=True)
    tag = CharFilter(name='tags__name', lookup_type='icontains', distinct=True)

    class Meta:
        model = Product
        fields = [
            'min_price',
            'max_price',
            'category',
            'title',
            'description',
            'tag',
        ]


# def product_list(request):
#     qs = Product.objects.all()
#     ordering = request.GET.get("ordering")
#     if ordering:
#         qs = Product.objects.all().order_by(ordering)
#     f = ProductFilter(request.GET, queryset=qs)
#     return render(request, "products/product_list.html", {"object_list": f})


class ProductListView(FilterMixin, ListView):
    model = Product
    queryset = Product.objects.all()
    filter_class = ProductFilter
    paginate_by = 12

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView, self).get_context_data(*args, **kwargs)
        # all_products = Product.objects.all()
        # print("count", context["object_list"].count())
        paginator = Paginator(context["object_list"], self.paginate_by)
        page = self.request.GET.get('page')
        print("number_of_pages:", paginator.num_pages)

        # ------------Paginator section--------------#
        try:
            page_products = paginator.page(page)
        except PageNotAnInteger:
            page_products = paginator.page(1)
        except EmptyPage:
            page_products = paginator.page(paginator.num_pages)

        # -------------Tags section-------------------#
        # get all id's of the object_list
        product_ids = []
        product_tags = []
        for t in context["object_list"]:
            try:
                product_ids += [t.id]
                product_tags += t.tags.all()
            except:
                pass

        # remove duplicates
        product_tags = list(set(product_tags))
        # print(product_tags)
        context['product_tag_list'] = product_tags

        # -------------Categories section-------------#
        context['categories'] = Category.objects.all().filter(parent=None).order_by('title')

        # ----------Most Visited deneme bu oldu----------------# # products model 'da queryset içine alınabilir mi? #
        most_viewed_product_list = Product.objects.annotate(num_views=Sum('productanalytics__count')).order_by('-num_views')
        # print(product_list)
        context['most_visited_products'] = most_viewed_product_list[:3]

        # ----------Price filter section---------------#
        # Yukarıda object listi içindeki minimum ve maksimumu buluyordum ama manasız değil gibi.
        # set minimum and maximum prices

        # get all products in object_list
        product_object_list = Product.objects.all().filter(pk__in=product_ids)
        minimum_price_aggregate = product_object_list.aggregate(Min('price'))
        minimum_price = minimum_price_aggregate['price__min']
        # yukarıdaki şekilde parse etmezsen,
        # python dictionary döndürdüğü için sıçıyorsun...
        context["minimum_price"] = minimum_price

        maximum_price_aggregate = product_object_list.aggregate(Max('price'))
        maximum_price = maximum_price_aggregate['price__max']
        context["maximum_price"] = maximum_price

        if self.request.GET.get('min_price', '') is not '':
            context["minimum_set_price_value"] = str(self.request.GET.get('min_price', ''))

        if self.request.GET.get('max_price', '') is not '':
            context["maximum_set_price_value"] = str(self.request.GET.get('max_price', ''))

        # ----------Other context data section-----------#
        context["now"] = timezone.now()
        context["query"] = self.request.GET.get("q")  # None
        context["filter_form"] = ProductFilterForm(data=self.request.GET or None)
        context["product_list_page"] = True
        context["page_products"] = page_products

        return context

    def get_queryset(self, *args, **kwargs):
        qs = super(ProductListView, self).get_queryset(*args, **kwargs)
        query = self.request.GET.get("q")
        if query:
            qs = self.model.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )
            try:
                qs2 = self.model.objects.filter(
                    Q(price=query)
                )
                qs = (qs | qs2).distinct()
            except:
                pass
        return qs


import random  # related products için kullanılıyor...


class ProductDetailView(DetailView):
    model = Product

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        instance = self.get_object()

        # #### NEW CODE ####
        # if self.request.session.get('last_visit'):
        #     # The session has a value for the last visit
        #     last_visit_time = self.request.session.get('last_visit')
        #     visits = self.request.session.get('visits', 0)
        #
        #     if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > 0:
        #         self.request.session['visits'] = visits + 1
        #         self.request.session['last_visit'] = str(datetime.now())
        # else:
        #     # The get returns None, and the session does not have a value for the last visit.
        #     self.request.session['last_visit'] = str(datetime.now())
        #     self.request.session['visits'] = 1
        #
        # print(self.request.session.get('visits'))
        # print(self.request.session.get('last_visit'))
        # #### END NEW CODE ####

        if self.request.session.get('last_visited_item_list'):
            if instance not in self.request.session.get('last_visited_item_list'):
                if 0 <= len(self.request.session.get('last_visited_item_list')) < 3:
                    self.request.session['last_visited_item_list'].append(instance)
                    self.request.session.modified = True
                    print("3 'ten küçük ya da hiç yok", len(self.request.session.get('last_visited_item_list')))
                    print(self.request.session.get('last_visited_item_list'))
                else:
                    del self.request.session.get('last_visited_item_list')[0]
                    self.request.session['last_visited_item_list'].append(instance)
                    self.request.session.modified = True
                    print(self.request.session.get('last_visited_item_list'))
        else:
            self.request.session['last_visited_item_list'] = []
            self.request.session['last_visited_item_list'].append(instance)
            self.request.session.modified = True

        # print last item
        # order_by("-title")

        # ben user authenticated olmasa da view sayısını arttıracağım...
        # if self.request.user.is_authenticated():
        #     tag = self.get_object()
        #     new_view = TagView.objects.add_count(self.request.user, tag)

        # yukarıdaki gibi herhangi bir değişkene de atmaya gerek yok.
        if self.request.user.is_authenticated():
            user = self.request.user  # eğer user login olmuşsa
        else:
            user = self.request.user.id  # eğer user login olmamışsa
        analytics, created = ProductAnalytics.objects.get_or_create(user=user, product=instance)
        analytics.add_count()


        context["related"] = sorted(Product.objects.get_related(instance)[:8], key=lambda x: random.random())
        return context


# detail view 'ı CBV olarak yazdık...
# def product_detail_view_func(request, id):
#     # product_instance = Product.objects.get(id=id)
#     product_instance = get_object_or_404(Product, id=id)
#     try:
#         product_instance = Product.objects.get(id=id)
#     except Product.DoesNotExist:
#         raise Http404
#     except:
#         raise Http404
#
#     template = "products/product_detail.html"
#     context = {
#         "object": product_instance
#     }
#     return render(request, template, context)


# Aşağıdaki de slug view olarak function based view...
# def detail_slug_view(request, slug=None):
#     product = Product.objects.get(slug=slug)
#     try:
#         product = get_object_or_404(Product, slug=slug)
#     except Product.MultipleObjectsReturned:
#         product = Product.objects.filter(slug=slug).order_by("-title").first()
#     # print slug
#     # product = 1
#     template = "products/product_detail.html"
#     context = {
#         "object": product
#     }
#     return render(request, template, context)
