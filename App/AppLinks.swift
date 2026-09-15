import Foundation

enum AppLinks {
    static let website = URL(string: "https://finemenot.xyz/")!
    static let database = website.appending(path: "data", directoryHint: .isDirectory)
}
