from datetime import datetime, timedelta


def format_published(date):
    months = {
        "января": 1,
        "февраля": 2,
        "марта": 3,
        "апреля": 4,
        "мая": 5,
        "июня": 6,
        "июля": 7,
        "августа": 8,
        "сентября": 9,
        "октября": 10,
        "ноября": 11,
        "декабря": 12
    }

    date = date.split()

    year = int(datetime.now().strftime('%Y'))
    month = int(datetime.now().strftime('%m'))
    today = datetime.today().strftime('%d.%m.%Y')
    yesterday = (datetime.strptime(today, '%d.%m.%Y') - timedelta(1)).strftime('%d.%m.%Y')

    if date[0] == 'сегодня':
        del date[1]
        date[0] = today
        date = datetime.strptime(' '.join(date), '%d.%m.%Y %H:%M')
        return date
    elif date[0] == 'вчера':
        del date[1]
        date[0] = yesterday
        date = datetime.strptime(' '.join(date), '%d.%m.%Y %H:%M')
        return date

    if date[1] in months:
        month = int(months[date[1]])
        day = int(date[0])
        hours = int(date[3][:2])
        minutes = int(date[3][3:])
        date = datetime(year, month, day, hours, minutes)
        return date
