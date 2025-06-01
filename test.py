class BookProgress:
    def __init__(self, title, total_pages):
        self.title = title
        self.total_pages = total_pages
        self.current_page = 0

    def update_page(self, page):
        self.current_page = page

    def show_progress(self):
        percent = (self.current_page / self.total_pages) * 100
        return f"{self.title}: {percent:.1f}% 완료"

class DailyReview:
    def __init__(self, date, content):
        self.date = date
        self.content = content

    def show_review(self):
        return f"{self.date} 리뷰:\n{self.content}"

class ChecklistItem:
    def __init__(self, task):
        self.task = task
        self.done = False

    def mark_done(self):
        self.done = True

class Checklist:
    def __init__(self):
        self.items = []

    def add_task(self, task):
        item = ChecklistItem(task)
        self.items.append(item)

    def show_all(self):
        for item in self.items:
            status = "✅" if item.done else "❌"
            print(f"{status} {item.task}")

# 메인 실행
if __name__ == "__main__":
    my_book = BookProgress("파이썬 기초", 300)
    my_book.update_page(120)
    print(my_book.show_progress())

    review = DailyReview("2025-05-20", "오늘은 집중 잘 했고 뽀모도로를 6번 했어!")
    print(review.show_review())

    checklist = Checklist()
    checklist.add_task("1장 복습하기")
    checklist.add_task("문제 5개 풀기")
    checklist.items[0].mark_done()

    print("\n오늘의 체크리스트:")
    checklist.show_all()