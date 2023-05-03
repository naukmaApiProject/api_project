REGIONS = {'Kyiv': 9, 'Vinnytsia': 3, 'Lutsk': 2, 'Dnipro': 4, 'Donetsk': 5, 'Zhytomyr': 6, 'Uzhhorod': 7, 
'Zaporizhzhia': 8, 'Ivano-Frankivsk': 24, 'Kropyvnytskyi': 10, 'Luhansk': 11, 'Lviv': 12, 
'Mykolaiv': 13, 'Odesa': 14, 'Poltava': 15, 'Rivne': 16, 'Simferopol': 25, 'Sumy': 17, 
'Ternopil': 18, 'Kharkiv': 19, 'Kherson': 20, 'Khmelnytskyi': 21, 'Cherkasy': 22, 
'Chernivtsi': 1, 'Chernihiv': 23}

def get_region_id(name):
    return REGIONS[name]