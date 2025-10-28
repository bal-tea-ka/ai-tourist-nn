// Модуль геокодирования адресов через Яндекс.Геокодер
const Geocoder = {
async geocode(address) {
return new Promise((resolve, reject) => {
if (typeof ymaps === 'undefined') {
reject(new Error('Яндекс.Карты не загружены'));
return;
}

text
        ymaps.geocode(address, { results: 1 }).then(
            (res) => {
                const firstGeoObject = res.geoObjects.get(0);
                if (!firstGeoObject) {
                    reject(new Error('Адрес не найден'));
                    return;
                }
                
                const coords = firstGeoObject.geometry.getCoordinates();
                resolve({
                    latitude: coords[0],
                    longitude: coords[1],
                    address: firstGeoObject.getAddressLine()
                });
            },
            (error) => {
                reject(error);
            }
        );
    });
}
};
