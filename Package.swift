// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "FineMeNotCore",
    platforms: [.iOS(.v18), .macOS(.v15)],
    products: [.library(name: "CameraCore", targets: ["CameraCore"])],
    targets: [
        .target(name: "CameraCore"),
        .testTarget(name: "CameraCoreTests", dependencies: ["CameraCore"])
    ]
)
