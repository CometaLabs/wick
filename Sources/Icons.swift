import Cocoa

/// Icono de la barra de menú: una velita con cara, dibujada en vectores para que se vea nítida
/// en cualquier pantalla y respete el modo claro y oscuro.
enum MenuIcon {
    enum Mode: Equatable {
        case working(frame: Int, blink: Bool)
        case waiting(blink: Bool)
        case idle
        case manual
    }

    static let flickerFrames = 6
    private static let flicker: [(h: CGFloat, tilt: CGFloat)] = [
        (3.4, 0.0), (3.0, -0.35), (3.7, 0.25), (3.2, -0.15), (3.6, 0.35), (2.9, -0.25)
    ]

    static func image(_ mode: Mode) -> NSImage {
        let size = NSSize(width: 18, height: 18)
        let template: Bool
        if case .waiting = mode { template = false } else { template = true }

        let image = NSImage(size: size, flipped: false) { _ in
            let ink: NSColor = template ? .black : .labelColor
            draw(mode, ink: ink)
            return true
        }
        image.isTemplate = template
        image.accessibilityDescription = "Wick"
        return image
    }

    private static func draw(_ mode: Mode, ink: NSColor) {
        guard let ctx = NSGraphicsContext.current else { return }

        // Cuerpo de la vela con dos goterones
        let body = NSBezierPath(roundedRect: NSRect(x: 4.5, y: 1.5, width: 9, height: 9.2), xRadius: 2.6, yRadius: 2.6)
        body.append(NSBezierPath(roundedRect: NSRect(x: 4.5, y: 6.6, width: 1.7, height: 3.8), xRadius: 0.85, yRadius: 0.85))
        body.append(NSBezierPath(roundedRect: NSRect(x: 11.2, y: 5.4, width: 1.7, height: 4.8), xRadius: 0.85, yRadius: 0.85))
        ink.setFill()
        body.fill()

        // Wick
        NSBezierPath(roundedRect: NSRect(x: 8.55, y: 10.2, width: 0.9, height: 1.9), xRadius: 0.45, yRadius: 0.45).fill()

        // Llama
        switch mode {
        case .working(let frame, _):
            let f = flicker[frame % flicker.count]
            flame(height: f.h, tilt: f.tilt).fill()
        case .manual:
            flame(height: 3.4, tilt: 0).fill()
        case .waiting:
            NSColor(srgbRed: 1.0, green: 0.55, blue: 0.12, alpha: 1).setFill()
            flame(height: 2.5, tilt: 0.25, radius: 1.6).fill()
        case .idle:
            break
        }

        // Cara: se recorta del cuerpo para que se vea el fondo de la barra
        ctx.saveGraphicsState()
        ctx.compositingOperation = .destinationOut
        NSColor.black.setFill()
        NSColor.black.setStroke()
        switch mode {
        case .idle:
            for x in [7.1, 10.9] as [CGFloat] {
                let arc = NSBezierPath()
                arc.lineWidth = 0.9
                arc.lineCapStyle = .round
                arc.appendArc(withCenter: NSPoint(x: x, y: 5.6), radius: 0.95, startAngle: 20, endAngle: 160)
                arc.stroke()
            }
        case .working(_, let blink), .waiting(let blink):
            var dx: CGFloat = 0
            if case .waiting = mode { dx = 0.45 }
            for x in [7.1, 10.9] as [CGFloat] {
                if blink {
                    NSBezierPath(roundedRect: NSRect(x: x - 1 + dx, y: 5.7, width: 2, height: 0.8), xRadius: 0.4, yRadius: 0.4).fill()
                } else {
                    NSBezierPath(ovalIn: NSRect(x: x - 0.95 + dx, y: 5.0, width: 1.9, height: 2.3)).fill()
                }
            }
        case .manual:
            for x in [7.1, 10.9] as [CGFloat] {
                NSBezierPath(ovalIn: NSRect(x: x - 0.95, y: 5.0, width: 1.9, height: 2.3)).fill()
            }
        }
        // boquita
        let mouth = NSBezierPath()
        mouth.lineWidth = 0.8
        mouth.lineCapStyle = .round
        mouth.appendArc(withCenter: NSPoint(x: 9, y: 4.2), radius: 0.9, startAngle: 200, endAngle: 340)
        mouth.stroke()
        ctx.restoreGraphicsState()
    }

    private static func flame(height h: CGFloat, tilt: CGFloat, radius r: CGFloat = 1.85) -> NSBezierPath {
        let c = NSPoint(x: 9, y: 12.6 + r * 0.55)
        let tip = NSPoint(x: c.x + tilt, y: c.y + r + h * 0.62)
        let p = NSBezierPath()
        p.move(to: NSPoint(x: c.x + r, y: c.y))
        p.appendArc(withCenter: c, radius: r, startAngle: 0, endAngle: 180, clockwise: true)
        p.curve(to: tip, controlPoint1: NSPoint(x: c.x - r, y: c.y + r * 0.9),
                controlPoint2: NSPoint(x: tip.x - r * 0.25, y: tip.y - h * 0.3))
        p.curve(to: NSPoint(x: c.x + r, y: c.y), controlPoint1: NSPoint(x: tip.x + r * 0.25, y: tip.y - h * 0.3),
                controlPoint2: NSPoint(x: c.x + r, y: c.y + r * 0.9))
        p.close()
        return p
    }
}

/// Mascota grande del menú: frames renderizados en Blender (Resources/mascot/<estado>/NN.png).
enum Mascot: String {
    case trabajando, esperando, descansando

    private static var cache: [Mascot: [NSImage]] = [:]

    var frames: [NSImage] {
        if let cached = Mascot.cache[self] { return cached }
        var list: [NSImage] = []
        let resources = ProcessInfo.processInfo.environment["WICK_RESOURCES"].map { URL(fileURLWithPath: $0) }
            ?? Bundle.main.resourceURL
        guard let base = resources?.appendingPathComponent("mascot/\(rawValue)") else { return [] }
        for i in 0..<60 {
            let url = base.appendingPathComponent(String(format: "%02d.png", i))
            guard let image = NSImage(contentsOf: url) else { break }
            image.size = NSSize(width: 128, height: 128)
            list.append(image)
        }
        Mascot.cache[self] = list
        return list
    }
}
