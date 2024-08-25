from .base import *


landheader = {
    'title': 'Dominion',
    'description': 'Drones, hidden and handheld cameras are used to expose the dark underbelly of modern animal agriculture, questioning the morality of humankind’s dominion over the animal kingdom. While mainly focusing on animals used for food, it also shows using them for clothing, entertainment and research.',
    'btnmain': {
        'label': 'Watch on Youtube',
        'link': 'https://www.youtube.com/watch?v=LQRAfJyEsko',
        'target': '_blank',
    },
    'btn2': {
        'label': 'More films',
        'link': 'films.html',
        'target': '_self',
    },
    'image': {
        'src': '../templates/assets/dominion.jpg',
        'link': 'https://www.youtube.com/watch?v=LQRAfJyEsko',
        'target': '_blank',
    },
}

features = {
    'label': "We recommend",
    'features': (
        {'title': 'Films', 'link': 'films.html', 'icon': 'bi-film', 'description': 'Curated list of the best films about animal liberation'},
        {'title': 'Books', 'link': 'books.html', 'icon': 'bi-book', 'description': 'Best books about veganism and environment'},
        {'title': 'Recipes and other apps', 'link': 'apps.html', 'icon': 'bi-layout-wtf', 'description': 'Useful applications and websites, like restaurants locator or a recipes catalog'},
        {'title': 'Statistics', 'link': 'stat.html', 'icon': 'bi-bar-chart-line', 'description': 'Agriculture and ecological data'},
    ),
}

testimonial = {
    'text': '“It takes nothing away from a human to be kind to an animal.”',
    'author': 'Joaquin Phoenix',
    'author_descr': 'American actor',
    'image': '../templates/assets/joaquin.jpg',
}

contact = {
    'title': 'Contact',
    'follow_us': 'Follow us',
    'donations': 'Donations',
}
