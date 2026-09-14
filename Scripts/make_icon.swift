import AppKit
import Foundation
let size = 1024
let image = NSImage(size: NSSize(width: size, height: size))
image.lockFocus()
NSColor(calibratedRed: 10/255, green: 0, blue: 148/255, alpha: 1).setFill()
NSRect(x: 0, y: 0, width: size, height: size).fill()
let ticket = NSBezierPath(roundedRect: NSRect(x: 238, y: 188, width: 548, height: 648), xRadius: 36, yRadius: 36)
NSColor.white.setStroke(); ticket.lineWidth = 34; ticket.stroke()
let rule = NSBezierPath()
rule.move(to: NSPoint(x: 345, y: 650)); rule.line(to: NSPoint(x: 678, y: 650))
rule.move(to: NSPoint(x: 345, y: 540)); rule.line(to: NSPoint(x: 588, y: 540))
rule.lineWidth = 28; rule.lineCapStyle = .round; rule.stroke()
let slash = NSBezierPath()
slash.move(to: NSPoint(x: 188, y: 168)); slash.line(to: NSPoint(x: 840, y: 848))
NSColor(calibratedRed: 10/255, green: 0, blue: 148/255, alpha: 1).setStroke()
slash.lineWidth = 104; slash.lineCapStyle = .round; slash.stroke()
NSColor(calibratedRed: 174/255, green: 207/255, blue: 1, alpha: 1).setStroke()
slash.lineWidth = 54; slash.stroke()
image.unlockFocus()
let bitmap = NSBitmapImageRep(data: image.tiffRepresentation!)!
let target = URL(fileURLWithPath: CommandLine.arguments[1])
try bitmap.representation(using: .png, properties: [:])!.write(to: target)
