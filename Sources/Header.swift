import Cocoa

struct MenuSnapshot {
    let mascot: Mascot
    let title: String
    let subtitle: String
}

// MARK: - Cabecera del menú: mascota animada + estado

final class HeaderView: NSView {
    private let imageView = NSImageView()
    private let title = NSTextField(labelWithString: "")
    private let subtitle = NSTextField(labelWithString: "")
    private var mascot: Mascot = .descansando
    private var frameIndex = 0
    private var timer: Timer?

    override init(frame: NSRect) {
        super.init(frame: frame)
        imageView.frame = NSRect(x: 8, y: 4, width: 120, height: 120)
        imageView.imageScaling = .scaleProportionallyUpOrDown
        addSubview(imageView)

        title.font = NSFont.systemFont(ofSize: 15, weight: .semibold)
        title.frame = NSRect(x: 130, y: 70, width: 160, height: 22)
        addSubview(title)

        subtitle.font = NSFont.systemFont(ofSize: 11.5)
        subtitle.textColor = .secondaryLabelColor
        subtitle.maximumNumberOfLines = 3
        subtitle.lineBreakMode = .byWordWrapping
        subtitle.frame = NSRect(x: 130, y: 20, width: 162, height: 48)
        subtitle.cell?.wraps = true
        addSubview(subtitle)
    }

    required init?(coder: NSCoder) { fatalError() }

    func update(_ s: MenuSnapshot) {
        title.stringValue = s.title
        subtitle.stringValue = s.subtitle
        if s.mascot != mascot {
            mascot = s.mascot
            frameIndex = 0
        }
        showFrame()
    }

    private func showFrame() {
        let frames = mascot.frames
        guard !frames.isEmpty else { return }
        imageView.image = frames[frameIndex % frames.count]
    }

    func startAnimating() {
        stopAnimating()
        let t = Timer(timeInterval: 1.0 / 12.0, repeats: true) { [weak self] _ in
            guard let self = self else { return }
            self.frameIndex += 1
            self.showFrame()
        }
        RunLoop.main.add(t, forMode: .common)
        timer = t
    }

    func stopAnimating() {
        timer?.invalidate()
        timer = nil
    }
}

