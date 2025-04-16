from datetime import datetime


def greeting(request):
    current_time = datetime.now().time()
    if current_time.hour < 12:
        greeting = "buổi sáng"
    elif current_time.hour < 18:
        greeting = "buổi chiều"
    else:
        greeting = "buổi tối"

    return {"greeting": greeting}
