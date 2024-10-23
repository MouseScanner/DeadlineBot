import datetime


def seconds_to_string(seconds):
    # Количество секунд в одном дне
    seconds_in_day = 24 * 60 * 60
    # Количество секунд в одном часе
    seconds_in_hour = 60 * 60
    # Количество секунд в одной минуте
    seconds_in_minute = 60

    print(seconds, seconds_in_day)
    # Вычисляем количество дней, часов и минут в заданном количестве секунд
    days = seconds // seconds_in_day
    seconds = seconds % seconds_in_day
    hours = seconds // seconds_in_hour
    seconds = seconds % seconds_in_hour
    minutes = seconds // seconds_in_minute

    # Формируем строку с переводом в нужный формат
    result = ""
    if days > 0:
        result += f"{days} дней "
    if hours > 0:
        result += f"{hours} часов "
    if minutes > 0:
        result += f"{minutes} минут"

    # Возвращаем строку
    return result


def convert_input_date(input_str):
    # проверяем, что входная строка не пустая
    if not input_str:
        return 0, "Пожалуйста, введите дату или время."

    # разбиваем строку на части по пробелу
    parts = input_str.split()

    # проверяем, сколько частей получилось
    if len(parts) == 1:
        # если одна часть, то это должна быть дата в формате день.месяц.год
        try:
            # пробуем преобразовать строку в объект datetime
            date = datetime.datetime.strptime(parts[0], "%d.%m.%Y")
            # возвращаем объект datetime в виде день.месяц.год 0:00
            return 1, date.strftime("%d.%m.%Y 0:00")
        except ValueError:
            # если не получилось, то возвращаем сообщение об ошибке
            return 0, "Неверный формат даты. Пожалуйста, введите дату в виде день.месяц.год"
    elif len(parts) == 2:
        # если две части, то это должна быть дата и время или слово и время
        if parts[0] in ["сегодня", "завтра"]:
            # если первая часть - слово, то определяем дату по нему
            if parts[0] == "сегодня":
                # если слово - сегодня, то берем текущую дату
                date = datetime.date.today()
            else:
                # если слово - завтра, то берем дату на один день вперед
                date = datetime.date.today() + datetime.timedelta(days=1)
            # пробуем преобразовать вторую часть во время
            try:
                # пробуем преобразовать строку в объект time
                time = datetime.datetime.strptime(parts[1], "%H:%M").time()
                # соединяем дату и время в объект datetime
                datetime_obj = datetime.datetime.combine(date, time)
                # возвращаем объект datetime в виде день.месяц.год часы:минуты
                return 1, datetime_obj.strftime("%d.%m.%Y %H:%M")
            except ValueError:
                # если не получилось, то возвращаем сообщение об ошибке
                return 0, "Неверный формат времени. Пожалуйста, введите время в виде часы:минуты"
        else:
            # если первая часть - не слово, то это должна быть дата в формате день.месяц.год
            try:
                # пробуем преобразовать первую часть в объект date
                date = datetime.datetime.strptime(parts[0], "%d.%m.%Y").date()
                # пробуем преобразовать вторую часть во время
                try:
                    # пробуем преобразовать строку в объект time
                    time = datetime.datetime.strptime(parts[1], "%H:%M").time()
                    # соединяем дату и время в объект datetime
                    datetime_obj = datetime.datetime.combine(date, time)
                    # возвращаем объект datetime в виде день.месяц.год часы:минуты
                    return 1, datetime_obj.strftime("%d.%m.%Y %H:%M")
                except ValueError:
                    # если не получилось, то возвращаем сообщение об ошибке
                    return 0, "Неверный формат времени. Пожалуйста, введите время в виде часы:минуты"
            except ValueError:
                # если не получилось, то возвращаем сообщение об ошибке
                return 0, "Неверный формат даты. Пожалуйста, введите дату в виде день.месяц.год"
    else:
        # если больше двух частей, то это неверный ввод
        return 0, "Неверный ввод. Пожалуйста, введите дату или время в одном из допустимых форматов."
