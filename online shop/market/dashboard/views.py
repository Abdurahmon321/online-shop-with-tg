from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from shop.models import Category, Brand, Product, ProductImage
from .forms import CategoryForm, BrandForm, ProductForm, ProductImageForm


def index(request):
    return render(request, 'dashboard/base.html')


# Category Views


class CategoryListView(ListView):
    model = Category
    template_name = 'admin_dashboard/category_list.html'


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'admin_dashboard/category_form.html'
    success_url = reverse_lazy('category-list')


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'admin_dashboard/category_form.html'
    success_url = reverse_lazy('category-list')


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'admin_dashboard/category_confirm_delete.html'
    success_url = reverse_lazy('category-list')


# Brand Views
class BrandListView(ListView):
    model = Brand
    template_name = 'admin_dashboard/brand_list.html'


class BrandCreateView(CreateView):
    model = Brand
    form_class = BrandForm
    template_name = 'admin_dashboard/brand_form.html'
    success_url = reverse_lazy('brand-list')


class BrandUpdateView(UpdateView):
    model = Brand
    form_class = BrandForm
    template_name = 'admin_dashboard/brand_form.html'
    success_url = reverse_lazy('brand-list')


class BrandDeleteView(DeleteView):
    model = Brand
    template_name = 'admin_dashboard/brand_confirm_delete.html'
    success_url = reverse_lazy('brand-list')


# Product Views
class ProductListView(ListView):
    model = Product
    template_name = 'admin_dashboard/product_list.html'


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'admin_dashboard/product_form.html'
    success_url = reverse_lazy('product-list')


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'admin_dashboard/product_form.html'
    success_url = reverse_lazy('product-list')


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'admin_dashboard/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')


# Product Image Views
class ProductImageCreateView(CreateView):
    model = ProductImage
    form_class = ProductImageForm
    template_name = 'admin_dashboard/productimage_form.html'
    success_url = reverse_lazy('product-list')


class ProductImageUpdateView(UpdateView):
    model = ProductImage
    form_class = ProductImageForm
    template_name = 'admin_dashboard/productimage_form.html'
    success_url = reverse_lazy('product-list')


class ProductImageDeleteView(DeleteView):
    model = ProductImage
    template_name = 'admin_dashboard/productimage_confirm_delete.html'
    success_url = reverse_lazy('product-list')
