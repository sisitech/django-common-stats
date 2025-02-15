from django.contrib import admin

class PageSizeMixin:
    list_per_page = 200  # Default number of items per page

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        # Get the page size from the query string
        page_size = request.GET.get('page_size')
        print("GETIND QUEYUIR",page_size)
        
        if page_size and page_size.isdigit():
            self.list_per_page = int(page_size)
        return queryset
    
    # Define actions for changing page size
    def set_page_size(self, request, queryset, size=200):
        self.list_per_page = size  # Adjust the page size dynamically
        self.message_user(request, f"Page size changed to {size} items.")
     
    def set_page_size_10(self, request, queryset):
        return self.set_page_size(request, queryset, size=100)
     
    def set_page_size_20(self, request, queryset):
        return self.set_page_size(request, queryset, size=200)
 
    def set_page_size_50(self, request, queryset):
        return self.set_page_size(request, queryset, size=500)

    def set_page_size_100(self, request, queryset):
        return self.set_page_size(request, queryset, size=1000)

    # actions = ['set_page_size_10','set_page_size_20', 'set_page_size_50', 'set_page_size_100']