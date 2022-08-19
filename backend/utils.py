def paginate_resources(request, selection, max_page):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * max_page
    end = start + max_page

    resources = [resource.format() for resource in selection]
    current_resources = resources[start:end]

    return current_resources
