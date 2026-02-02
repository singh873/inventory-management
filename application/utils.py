def grand_total(list):
    total=0
    for i in list:
        if i.status=="approved":
            total+= i.units_requested * i.product.price
    return total