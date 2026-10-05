import Foundation

enum AppLinks {
    static let website = URL(string: "https://finemenot.xyz/")!
    // The original feed retains the geometry contract used by releases through 1.0.5.
    static let publicDatabase = website.appending(path: "data/v2", directoryHint: .isDirectory)
    // A private test archive can pin reviewed inputs without changing the
    // downloader or publishing candidate data to the public update feed.
    static let database: URL = {
        if let value = Bundle.main.object(forInfoDictionaryKey: "CameraDatabaseURL") as? String,
           let url = URL(string: value), url.scheme == "https", url.host != nil {
            return url
        }
        return publicDatabase
    }()
}
