import requests

def get_area(cordinate):
    """
    Get area roughly
    座標から大雑把な場所の情報を返します
    """
    point = [cordinate[0], cordinate[2]]

    areas = [
        {
            'name': 'Top Lane',
            'polygon': [[-27, -50], [-57, -20], [-68, -31], [-32, -67], [32, -67], [68, -31], [57, -20], [27, -50]]
        },
        {
            'name': 'Mid Lane',
            'polygon': [[-50, -9], [-50, 9], [50, 9], [50, -9]]
        },
        {
            'name': 'Bot Lane',
            'polygon': [[-27, 50], [-57, 20], [-68, 31], [-32, 67], [32, 67], [68, 31], [57, 20], [27, 50]]
        },
        {
            'name': 'Jungle Top Left',
            'polygon': [[-42, -9], [-5, -9], [-14, -28], [-10, -50], [-27, -50], [-51, -27]]
        },
        {
            'name': 'Jungle Top Right',
            'polygon': [[42, -9], [7, -9], [2, -22], [9, -27], [9, -35], [0, -38], [4, -50], [27, -50], [51, -27]]
        },
        {
            'name': 'Jungle Bot Left',
            'polygon': [[-42, 9], [-7, 9], [-2, 22], [-9, 27], [-9, 35], [0, 38], [-4, 50], [-27, 50], [-51, 27]]
        },
        {
            'name': 'Jungle Bot Right',
            'polygon': [[42, 9], [5, 9], [14, 28], [10, 50], [27, 50], [51, 27]]
        },
        {
            'name': 'Home side Top Left',
            'polygon': [[-42, -9], [-51, -27], [-57, -20], [-50, -9]]
        },
        {
            'name': 'Home side Top Right',
            'polygon': [[42, -9], [51, -27], [57, -20], [50, -9]]
        },
        {
            'name': 'Home side Bot Left',
            'polygon': [[-42, 9], [-51, 27], [-57, 20], [-50, 9]]
        },
        {
            'name': 'Home side Bot Right',
            'polygon': [[42, 9], [51, 27], [57, 20], [50, 9]]
        },
        {
            'name': 'River Top',
            'polygon': [[-5, -9], [7, -9], [2, -22], [9, -27], [9, -35], [0, -38], [4, -50], [-10, -50], [-14, -28]]
        },
        {
            'name': 'River Bot',
            'polygon': [[5, 9], [-7, 9], [-2, 22], [-9, 27], [-9, 35], [0, 38], [-4, 50], [10, 50], [14, 28]]
        },
        {
            'name': 'River Bot',
            'polygon': [[5, 9], [-7, 9], [-2, 22], [-9, 27], [-9, 35], [0, 38], [-4, 50], [10, 50], [14, 28]]
        },
        {
            'name': 'Vain Home Left',
            'polygon': [[-86, 0], [-90, -9], [-68, -31], [-57, -20], [-50, -9], [-50, 9], [-57, 20], [-68, 31], [-90, 9]]
        },
        {
            'name': 'Vain Home Right',
            'polygon': [[86, 0], [90, -9], [68, -31], [57, -20], [50, -9], [50, 9], [57, 20], [68, 31], [90, 9]]
        },
        {
            'name': 'Sanctuary Left',
            'polygon': [[-86, 0], [-90, -9], [-90, -12], [-110, -12], [-110, 12], [-90, 12], [-90, 9]]
        },
        {
            'name': 'Sanctuary Right',
            'polygon': [[86, 0], [90, -9], [90, -12], [110, -12], [110, 12], [90, 12], [90, 9]]
        }
    ]


    return {}


def point_in_polygon(point, poly):
    x, y = point
    i = len(poly) - 1 # index of last polygon
    windingNumber, j, yi, yj = 0

    while i >= 0:
        yi = poly[i][1] - y
        yj = poly[j][1] - y

        if (yi > 0) != (yj > 0):
            counterClockwise = (yj > yi) ? True : False
            if counterClockwise == (yj * (poly[i][0] - x) > yi * (poly[j][0] - x)):
                windingNumber = counterClockwise ? windingNumber + 1 : windingNumber -1
        j = i--

    return (windingNumber % 2 == 1) ? True : False
