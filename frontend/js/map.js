// Модуль работы с Яндекс.Картами
let map = null;
let multiRoute = null;

const MapModule = {
init() {
return new Promise((resolve) => {
ymaps.ready(() => {
map = new ymaps.Map('map', {
center: CONFIG.DEFAULT_CENTER,
zoom: CONFIG.DEFAULT_ZOOM,
controls: ['zoomControl', 'fullscreenControl']
});
resolve();
});
});
},

text
buildRoute(points) {
    // Очистка предыдущего маршрута
    if (multiRoute) {
        map.geoObjects.remove(multiRoute);
    }
    
    // Построение нового маршрута
    multiRoute = new ymaps.multiRouter.MultiRoute({
        referencePoints: points.map(p => [p.latitude, p.longitude]),
        params: {
            routingMode: 'pedestrian' // Пешеходный маршрут
        }
    }, {
        boundsAutoApply: true,
        wayPointStartIconColor: '#00FF00',
        wayPointFinishIconColor: '#FF0000',
        routeActiveStrokeWidth: 6,
        routeActiveStrokeColor: '#0d6efd'
    });
    
    map.geoObjects.add(multiRoute);
    
    // Добавление меток для каждого места
    points.forEach((point, index) => {
        const placemark = new ymaps.Placemark(
            [point.latitude, point.longitude],
            {
                balloonContent: +"<strong></strong><br>"+,
                iconContent: (index + 1).toString()
            },
            {
                preset: 'islands#blueStretchyIcon'
            }
        );
        map.geoObjects.add(placemark);
    });
},

clear() {
    if (multiRoute) {
        map.geoObjects.remove(multiRoute);
        multiRoute = null;
    }
    map.geoObjects.removeAll();
}
};
