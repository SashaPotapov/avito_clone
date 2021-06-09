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

    today = datetime.today().strftime('%d.%m.%Y')
    yesterday = (datetime.strptime(today, '%d.%m.%Y') - timedelta(1)).strftime('%d.%m.%Y')

    if date[0] == 'сегодня':
        date[0] = today
        return ' '.join(date)
    elif date[0] == 'вчера':
        date[0] = yesterday
        return ' '.join(date)

    if date[1] in months:
        year = int(datetime.now().strftime('%Y'))
        month = int(months[date[1]])
        day = int(date[0])
        hours = int(date[3][:2])
        minutes = int(date[3][3:])
        date = datetime(year, month, day, hours, minutes).strftime('%d.%m.%Y в %H:%M')
        return date
