from time import sleep


def pause():
    sleep(2)


# NB: we're running one extra job to offset the implicit slot.
def test_0(request):
    pause()


def test_1(request):
    pause()


def test_2(request):
    pause()
