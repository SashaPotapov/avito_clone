from datetime import datetime, timedelta


def format_published(post_date):
    months = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12,
    }

    post_date = post_date.split()
    post_day = post_date[0]
    post_month = post_date[1]

    year = int(datetime.now().strftime('%Y'))
    today = datetime.today().strftime('%d.%m.%Y')
    yesterday = (
        datetime.strptime(today, '%d.%m.%Y') - timedelta(1)
    ).strftime('%d.%m.%Y')

    if post_day == 'сегодня':
        del post_month
        post_day = today
        post_date = datetime.strptime(' '.join(post_date), '%d.%m.%Y %H:%M')

    elif post_day == 'вчера':
        del post_month
        post_day = yesterday
        post_date = datetime.strptime(' '.join(post_date), '%d.%m.%Y %H:%M')

    else:
        month = int(months.get(post_month))
        day = int(post_day)
        hours = int(post_date[3][:2])
        minutes = int(post_date[3][3:])
        post_date = datetime(year, month, day, hours, minutes)

    return post_date
