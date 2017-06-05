import time
from io import StringIO
from lxml import etree
from django.contrib.sites.models import Site
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from datetime import datetime
from django.db.models import Q, Max, Min, Count, Sum, DecimalField, F
from django.http import Http404, HttpResponse, StreamingHttpResponse, HttpResponseNotAllowed
from django.shortcuts import render, get_object_or_404, redirect
from django.template import Context, loader
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.html import escape
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django_filters import FilterSet, CharFilter, NumberFilter, RangeFilter

from pure_pagination.mixins import PaginationMixin

from analytics.models import ProductAnalytics
from newsletter.models import SignUp
from newsletter.forms import SignUpForm
from taggit.models import Tag
from visual_site_elements.models import HorizontalTopBanner

from .forms import VariationInventoryFormSet, ProductFilterForm
from .mixins import StaffRequiredMixin, FilterMixin
from .models import Product, Variation, Category


# bunu price slider 'ın düzgün çalışması için kullanıyorum...
def update_session(request, *args, **kwargs):

    # if not request.is_ajax() or not request.method == 'POST':
    #     print("post ile ilgili sıkıntı var")
    #     return HttpResponseNotAllowed(['POST'])
    minimum_value = request.GET.get("min_value")
    maximum_value = request.GET.get("max_value")
    request.session['min_value'] = minimum_value
    request.session['max_value'] = maximum_value
    return HttpResponse('ok')


def big_xml(marketplace):
    products = Product.objects.all().order_by('istebu_product_no')

    def write_header():
        # global line_number_after
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<products>\n')

    def write_xml_node(product_instance):
        variation_instance = product.variation_set.first()
        output.write('<product>\n')
        output.write(
            '<istebu_product_no>' + '<![CDATA[{}]]>'.format(product_instance.istebu_product_no)
            + '</istebu_product_no>\n')
        output.write(
            '<product_barkod>' + '<![CDATA[{}]]>'.format(variation_instance.product_barkod) + '</product_barkod>\n')
        output.write(
            '<product_brand>' + '<![CDATA[{}]]>'.format(product_instance.get_brand()) + '</product_brand>\n')
        output.write(
            '<product_title>' + '<![CDATA[{}]]>'.format(product_instance.title) + '</product_title>\n')
        output.write(
            '<product_description>' + '<![CDATA[{}]]>'.format(escape(product_instance.description))
            + '</product_description>\n')
        output.write(
            '<product_category>' + '<![CDATA[{}]]>'.format(product_instance.get_main_category())
            + '</product_category>\n')
        output.write(
            '<product_price>' + '<![CDATA[{}]]>'.format(variation_instance.get_xml_sale_price(market=marketplace))
            + '</product_price>\n')
        if not product.kargo == "None":
            output.write(
                '<kargo>' + '<![CDATA[{}]]>'.format(product.kargo) + '</kargo>\n')
        else:
            output.write(
                '<kargo>' + '<![CDATA[{}]]>'.format("Mağaza Öder") + '</kargo>\n')

        try:
            media_url = product.productimage_set.first().sd_thumb
        except:
            media_url = "No Image"
        output.write(
            '<product_image>' + '<![CDATA[{}]]>'.format(media_url) + '</product_image>\n')

        domain = Site.objects.get_current().domain
        path = product.get_absolute_url()
        output.write(
            '<product_url>' + '<![CDATA[http://{domain}{path}]]>'.format(domain=domain, path=path)
            + '</product_url>\n')
        output.write(
            '<stok_adedi>' + '<![CDATA[{}]]>'.format(variation_instance.inventory) + '</stok_adedi>\n')
        output.write('</product>\n')

    product_iterator = products.iterator()

    for num, product in enumerate(product_iterator):
        output = StringIO()

        last_number = len(products) - 1

        if num == 0:
            # write header
            write_header()
        elif num == last_number:
            # write xml node + closing tag
            write_xml_node(product_instance=product)
            output.write('</products>')
        else:
            # write xml_nodes
            write_xml_node(product)

        output.seek(0)
        yield output.read()
        # time.sleep(0.2)


def download_xml_streaming(request, marketplace):
    """Returns an XML file.
    This view responds with a generator that yields each row of the response as
    it's created.
    """
    if marketplace in ("n11", "gittigidiyor", "test",):
        # print("if mi çalışmıyor ? :", marketplace)
        pass
    else:
        raise Http404("The link is not available!")
    # products = Product.objects.all()
    response = StreamingHttpResponse(big_xml(marketplace), content_type='text/xml')
    response['Content-Disposition'] = 'attachment; filename=istebu.xml'

    return response


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

    title = CharFilter(name='title', lookup_expr='icontains', distinct=True)
    category = CharFilter(name='categories__slug', lookup_expr='iexact', distinct=True)
    # category_id = CharFilter(name='categories__id', lookup_type='icontains', distinct=True)
    # min_price = NumberFilter(name='variation__sale_price', lookup_expr='gte', distinct=True)  # (some_price__gte=somequery)
    # max_price = NumberFilter(name='variation__sale_price', lookup_expr='lte', distinct=True)
    tag = CharFilter(name='tags__name', lookup_expr='icontains', distinct=True)
    local_price = RangeFilter()

    class Meta:
        model = Product
        fields = [
            # 'min_price',
            # 'max_price',
            'category',
            'title',
            'description',
            'tag',
            'local_price'
        ]


# class PriceRangeFilter(FilterSet):
#         """Filter for Variations by Price"""
#         local_price = RangeFilter()
#
#         class Meta:
#             model = Variation
#             fields = ['local_price']

    # qs = Book.objects.all().order_by('title')
    #
    # # Range: Books between 5€ and 15€
    # f = F({'price_0': '5', 'price_1': '15'}, queryset=qs)
    #
    # # Min-Only: Books costing more the 11€
    # f = F({'price_0': '11'}, queryset=qs)
    #
    # # Max-Only: Books costing less than 19€
    # f = F({'price_1': '19'}, queryset=qs)


# def product_list(request):
#     qs = Product.objects.all()
#     ordering = request.GET.get("ordering")
#     if ordering:
#         qs = Product.objects.all().order_by(ordering)
#     f = ProductFilter(request.GET, queryset=qs)
#     print("queryset :", f.qs)
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

#
# class LatestProducts(ListView):
#     model = Product
#
#     def get_context_data(self, *args, **kwargs):
#         context = super(LatestProducts, self).get_context_data(*args, **kwargs)
#         qs = Product.objects.all()
#         # TODO: Buraya son gezilenleri listeleyen bir algoritma yaz.
#         if self.request.session.get('last_visited_item_list'):
#             last_visited_items = [Product.objects.get(pk=pk) for pk in self.request.session.get('last_visited_item_list')]
#             context['last_visited_item_list'] = last_visited_items[:3]
#
#         return context


# Artık bu view 'ı her yerde kullanabiliriz.
class SignupFormView(FormView):
    form_class = SignUpForm
    success_url = reverse_lazy('products:products')

    def get_context_data(self, *args, **kwargs):
        context = super(SignupFormView, self).get_context_data(*args, **kwargs)
        context['form'] = self.get_form()
        return context

    def form_valid(self, form):
        instance = form.save(commit=False)
        email = form.cleaned_data.get('email')
        print(instance)
        print(instance)
        # Aynı e-posta ile kayıt olunmuş mu bak
        if SignUp.objects.filter(email=email).exists():
            # daha önce bu email ile kayıt olunmuş
            messages.error(self.request, 'Bu e-posta ile daha önce kayıt olunmuş!', "danger")
        else:
            # daha önce kayıt olunmamış kaydedebilirsin.
            instance.save()
            messages.success(self.request, 'Haber bültenimize başarıyla kayıt oldunuz.')
        return super(SignupFormView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        return FormView.post(self, request, *args, **kwargs)


class NewProductListView(FilterMixin, SignupFormView, PaginationMixin, ListView):
    model = Product
    filter_class = ProductFilter
    paginate_by = 12
    paginate_orphans = 10  # maximum gözüken sayfa sayısı
    queryset = Product.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(NewProductListView, self).get_context_data(*args, **kwargs)
        context["now"] = timezone.now()
        context["query"] = self.request.GET.get("q")  # None
        context["filter_form"] = ProductFilterForm(data=self.request.GET or None)  # BUNU KULLANMIYOR OLABİLİRİZ.

        context["number_of_object_list"] = len(context["object_list"])

        variation_qs = Variation.annotated.local_price().filter(
            product__in=context["object_list"]
        ).order_by('local_price')

        try:
            minimum_price = variation_qs.first().local_price
            context["minimum_price"] = minimum_price-1
            maximum_price = variation_qs.last().local_price
            context["maximum_price"] = maximum_price+1
        except:
            pass  # empty query döndürmüş demektir. O nedenlde de local_price set etmeye çalışırken patlar.

        paginated = self.paginate_queryset(context["object_list"], self.paginate_by)
        context["paginator"] = paginated[0]
        context["page_obj"] = paginated[1]
        context["object_list"] = paginated[2]

        context['queries'] = self.get_queries_without_page()
        context['categories'] = Category.objects.all().filter(active=True).filter(
            show_on_homepage=True).order_by('order', 'pk')
        context['tags'] = Tag.objects.all()
        context['banners'] = HorizontalTopBanner.objects.filter(category__title="Projeksiyon Cihazları")

        # most popular products
        most_viewed_product_list = Product.objects.annotate(num_views=Sum('productanalytics__count')).filter(
            num_views__gt=0).order_by('-num_views')
        context['most_popular_products'] = most_viewed_product_list[:3]

        if self.request.session.get('last_visited_item_list'):  # eğer varsa set et yoksa etme...
            context['last_visited_item_list'] = Product.objects.filter(
                pk__in=self.request.session.get('last_visited_item_list')).reverse()

        if self.request.GET.get('min_price', '') is not '':
            context["minimum_set_price_value"] = str(self.request.GET.get('min_price', ''))

        if self.request.GET.get('max_price', '') is not '':
            context["maximum_set_price_value"] = str(self.request.GET.get('max_price', ''))

        return context

    def get_queryset(self, *args, **kwargs):
        qs = super(NewProductListView, self).get_queryset(*args, **kwargs)
        query = self.request.GET.get("q")
        minimum_price = self.request.GET.get("min_price")
        maximum_price = self.request.GET.get("max_price")
        if query:
            # qs = self.model.objects.filter(
            #     Q(title__icontains=query) |
            #     Q(description__icontains=query)
            # )
            # try:
            #     qs2 = self.model.objects.filter(
            #         Q(price=query)
            #     )
            #     qs = (qs | qs2).distinct()
            # except:
            #     pass
            qs = self.model.objects.all().filter(title__icontains=query)
            # yukarıdakileri kaldırdım, sadece title yeterli.
            # description 'da aramaya gerek yok.
        # print("qs neymiş :", qs)
        if minimum_price or maximum_price:
            # print(minimum_price, maximum_price)
            variation_object_list = Variation.annotated.local_price().filter(
                product__in=qs
            ).order_by('local_price')
            f = ProductFilter({'local_price_0': minimum_price, 'local_price_1': maximum_price}, queryset=variation_object_list)
            # f = ProductFilter({'local_price_0': '730.0', 'local_price_1': '750.0'}, queryset=variation_object_list)
            # print("what is f?:", f.qs)
            # for var in f.qs:
            #     print(var.local_price)
            qs = qs.filter(variation__in=f.qs)

        # print(qs)
        return qs

    # This utility function removes page parameter for preserving the query parameters.
    def get_queries_without_page(self):
        queries_without_page = self.request.GET.copy()
        if "page" in queries_without_page:
            del queries_without_page['page']
        return queries_without_page


# bu da yine otomatik listeliyor ancak filtermixin çalışmıyor düzeltilecek...
# class CategoryDetailView(FilterMixin, SignupFormView, LatestProducts, PaginationMixin, ListView):
#     model = Product
#     filter_class = ProductFilter
#     paginate_by = 12
#     paginate_orphans = 10  # maximum gözüken sayfa sayısı
#     queryset = Product.objects.all()
#
#     def get_context_data(self, *args, **kwargs):
#         context = super(CategoryDetailView, self).get_context_data(*args, **kwargs)
#         context["now"] = timezone.now()
#         context["query"] = self.request.GET.get("q")  # None
#         context["filter_form"] = ProductFilterForm(data=self.request.GET or None)
#
#         print("context_object_list var mı?", context["object_list"])
#         # paginated = self.paginate_queryset(context["object_list"], self.paginate_by)
#         # context["paginator"] = paginated[0]
#         # context["page"] = paginated[0].get_page()
#         # print("page_nedir?", context["page"])
#         # context["page_obj"] = paginated[1]
#         # context["object_list"] = paginated[2]
#
#         minimum_price_aggregate = context["object_list"].aggregate(Min('price'))
#         minimum_price = minimum_price_aggregate['price__min']
#         context["minimum_price"] = minimum_price
#
#         maximum_price_aggregate = context["object_list"].aggregate(Max('price'))
#         maximum_price = maximum_price_aggregate['price__max']
#         context["maximum_price"] = maximum_price
#
#         paginated = self.paginate_queryset(context["object_list"], self.paginate_by)
#         context["paginator"] = paginated[0]
#         context["page_obj"] = paginated[1]
#         context["object_list"] = paginated[2]
#
#         context['queries'] = self.get_queries_without_page()
#         context['categories'] = Category.objects.all().filter(active=True).filter(show_on_homepage=True).order_by('order', 'pk')
#         context['tags'] = Tag.objects.all()
#         context['banners'] = HorizontalTopBanner.objects.filter(category__title="Projeksiyon Cihazları")
#         print(context['banners'])
#
#         # most popular products
#         most_viewed_product_list = Product.objects.annotate(num_views=Sum('productanalytics__count')).filter(num_views__gt=0).order_by('-num_views')
#         context['most_popular_products'] = most_viewed_product_list[:3]
#
#
#         if self.request.GET.get('min_price', '') is not '':
#             context["minimum_set_price_value"] = str(self.request.GET.get('min_price', ''))
#
#         if self.request.GET.get('max_price', '') is not '':
#             context["maximum_set_price_value"] = str(self.request.GET.get('max_price', ''))
#
#         return context
#
#     def get_queryset(self, *args, **kwargs):
#         qs = super(CategoryDetailView, self).get_queryset(*args, **kwargs)
#         query = self.request.GET.get("q")
#         if query:
#             qs = self.model.objects.filter(
#                 Q(title__icontains=query) |
#                 Q(description__icontains=query)
#             )
#             try:
#                 qs2 = self.model.objects.filter(
#                     Q(price=query)
#                 )
#                 qs = (qs | qs2).distinct()
#             except:
#                 pass
#         print("qs neymiş :", qs)
#         return qs
#
#     # This utility function removes page parameter for preserving the query parameters.
#     def get_queries_without_page(self):
#         queries_without_page = self.request.GET.copy()
#         if "page" in queries_without_page:
#             del queries_without_page['page']
#         return queries_without_page
#

# bu view tag üzerine tıklanınca filter yapıyor
class ProductListTagFilterView(NewProductListView):

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListTagFilterView, self).get_context_data(*args, **kwargs)
        tag_slug = self.kwargs["tag_slug"]
        print(tag_slug)
        qs = self.get_queryset()
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            context['object_list'] = qs.filter(tags__in=[tag])
        if context.get('object_list'):
            paginated = self.paginate_queryset(context["object_list"], self.paginate_by)
            context["paginator"] = paginated[0]
            context["page_obj"] = paginated[1]
            context["object_list"] = paginated[2]
        return context


import random  # related products için kullanılıyor...


# SignupFormView sayfanın altındaki newsletter formu için gerekli.
class ProductDetailView(SignupFormView, DetailView):
    model = Product

    def get_success_url(self):
        instance = self.get_object()
        return reverse_lazy('products:product_detail', kwargs={'slug': instance.slug})

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        instance = self.get_object()
        context["related"] = sorted(Product.objects.get_related(instance)[:8], key=lambda x: random.random())
        print("related_products :", context["related"])
        # add count to analytics:
        analytics_object, created = ProductAnalytics.objects.get_or_create(product=instance)
        if self.request.user.is_authenticated():
            analytics_object.user = self.request.user  # burda sapıttı habire kamil yazdı durdu...
        analytics_object.add_count()
        analytics_object.save()

        # add products to visited list
        # eğer liste varsa gezdiği ürün listede mi bak:
        if self.request.session.get('last_visited_item_list'):
            if instance.pk not in self.request.session.get('last_visited_item_list'):
                if 0 <= len(self.request.session.get('last_visited_item_list')) < 3:
                    self.request.session['last_visited_item_list'].append(instance.pk)
                    self.request.session.modified = True
                    print("3 'ten küçük ya da hiç yok", len(self.request.session.get('last_visited_item_list')))
                    print(self.request.session.get('last_visited_item_list'))
                else:
                    del self.request.session.get('last_visited_item_list')[0]
                    self.request.session['last_visited_item_list'].append(instance.pk)
                    self.request.session.modified = True
                    print(self.request.session.get('last_visited_item_list'))
        else:
            self.request.session['last_visited_item_list'] = []
            self.request.session['last_visited_item_list'].append(instance.pk)
            self.request.session.modified = True
        # print("last visited list :", self.request.session['last_visited_item_list'])
        return context



