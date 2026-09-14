import Foundation

public enum UpdateSchedule {
    public static var calendar: Calendar {
        var calendar = Calendar(identifier: .gregorian)
        calendar.timeZone = TimeZone(identifier: "America/Denver")!
        calendar.firstWeekday = 2
        calendar.minimumDaysInFirstWeek = 4
        return calendar
    }
    public static func currentWeekStart(at date: Date) -> Date {
        calendar.dateInterval(of: .weekOfYear, for: date)!.start
    }
    public static func nextRefresh(after date: Date) -> Date {
        calendar.date(byAdding: .day, value: 7, to: currentWeekStart(at: date))!
    }
    public static func isDue(generatedAt: Date, now: Date) -> Bool {
        generatedAt < currentWeekStart(at: now)
    }
}
