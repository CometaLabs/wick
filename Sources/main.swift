import Cocoa
import ServiceManagement

// Claude Code ejecuta este mismo binario como hook: responde y sale sin abrir la app.
if CommandLine.arguments.contains("--hook") {
    HookCLI.run()
}
// Para scripts y para quien prefiera la terminal: instala o quita los hooks y sale.
if let flag = CommandLine.arguments.first(where: { $0 == "--install-hooks" || $0 == "--uninstall-hooks" }) {
    do {
        if flag == "--install-hooks" { try HookInstaller.install() } else { try HookInstaller.uninstall() }
        print(flag == "--install-hooks" ? "Hooks de Wick instalados en \(WickPaths.claudeSettings.path)"
                                        : "Hooks de Wick quitados de \(WickPaths.claudeSettings.path)")
        exit(0)
    } catch {
        FileHandle.standardError.write("No se pudo leer \(WickPaths.claudeSettings.path) como JSON.\n".data(using: .utf8)!)
        exit(1)
    }
}

let isSpanish = Locale.preferredLanguages.first?.hasPrefix("es") ?? false
func L(_ es: String, _ en: String) -> String { isSpanish ? es : en }

private struct ManualOption {
    let label: String
    let seconds: TimeInterval?
}

private let manualOptions: [ManualOption] = [
    ManualOption(label: L("15 minutos", "15 minutes"), seconds: 15 * 60),
    ManualOption(label: L("30 minutos", "30 minutes"), seconds: 30 * 60),
    ManualOption(label: L("1 hora", "1 hour"), seconds: 3600),
    ManualOption(label: L("2 horas", "2 hours"), seconds: 2 * 3600),
    ManualOption(label: L("4 horas", "4 hours"), seconds: 4 * 3600),
    ManualOption(label: L("8 horas", "8 hours"), seconds: 8 * 3600),
    ManualOption(label: L("Hasta que la pare", "Until I stop it"), seconds: nil)
]

private let graceAfterStop: TimeInterval = 120
private let repoURL = URL(string: "https://github.com/CometaLabs/wick")!

final class AppDelegate: NSObject, NSApplicationDelegate, NSMenuDelegate {
    private var statusItem: NSStatusItem!
    private var header: HeaderView!
    private let menu = NSMenu()

    private let systemHold = AwakeHold(displayToo: false)
    private let displayHold = AwakeHold(displayToo: true)
    private let lid = LidController()

    private let watcher = AgentWatcher()
    private var hookSessions: [SessionRecord] = []
    private var sessions: [SessionRecord] = []
    private var lastScan = Date.distantPast
    private var hooksInstalled = false
    private var graceUntil = Date.distantPast
    private var manualActive = false
    private var manualEnd: Date?
    private var manualStart = Date()
    private var lowBattery = false
    private var lastBatteryCheck = Date.distantPast
    private var sleepStuck = false

    private var keepWhileWaiting: Bool {
        get { UserDefaults.standard.bool(forKey: "keepWhileWaiting") }
        set { UserDefaults.standard.set(newValue, forKey: "keepWhileWaiting") }
    }
    /// Detectar por proceso los agentes sin hooks (Codex, Gemini CLI…). Activado por defecto.
    private var watchOthers: Bool {
        get { UserDefaults.standard.object(forKey: "watchOthers") as? Bool ?? true }
        set { UserDefaults.standard.set(newValue, forKey: "watchOthers") }
    }
    private var lidPreference: Bool {
        get { UserDefaults.standard.bool(forKey: "lidWhileWorking") }
        set { UserDefaults.standard.set(newValue, forKey: "lidWhileWorking") }
    }

    private var iconFrame = 0
    private var blinkCountdown = 18
    private var lastIcon: MenuIcon.Mode?
    private var lastMood: Mascot?
    private var iconTick = 0

    // MARK: arranque

    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        WickPaths.ensure()
        HookInstaller.writeHookScript()
        hooksInstalled = HookInstaller.isInstalled()

        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        statusItem.button?.imagePosition = .imageLeading
        statusItem.button?.font = NSFont.monospacedDigitSystemFont(ofSize: 12, weight: .medium)
        header = HeaderView(frame: NSRect(x: 0, y: 0, width: 300, height: 128))
        menu.delegate = self
        statusItem.menu = menu

        if lidPreference && !lid.start() {
            lidPreference = false
        }
        sleepStuck = Power.sleepDisabled() && !lid.running

        tick()
        let timer = Timer(timeInterval: 1, target: self, selector: #selector(tick), userInfo: nil, repeats: true)
        RunLoop.main.add(timer, forMode: .common)
        let anim = Timer(timeInterval: 0.1, target: self, selector: #selector(animateIcon), userInfo: nil, repeats: true)
        RunLoop.main.add(anim, forMode: .common)

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { self.firstRun() }
    }

    // MARK: primer arranque

    private var isInApplications: Bool {
        let path = Bundle.main.bundlePath
        return path.hasPrefix("/Applications/") || path.hasPrefix(WickPaths.home.path + "/Applications/")
    }

    /// 1) Si no está en Aplicaciones, se ofrece a moverse (abierta desde Descargas o desde el .dmg,
    ///    los hooks apuntarían a una ruta que desaparece). 2) La primera vez explica dónde vive,
    ///    ofrece los hooks de Claude Code y abre su menú para que se vea en la barra.
    private func firstRun() {
        if !isInApplications && !UserDefaults.standard.bool(forKey: "skipMoveToApplications") {
            if offerMoveToApplications() { return }
        }
        guard !UserDefaults.standard.bool(forKey: "onboarded") else { return }
        UserDefaults.standard.set(true, forKey: "onboarded")
        showWelcome()
        let usesClaude = FileManager.default.fileExists(atPath: WickPaths.home.appendingPathComponent(".claude").path)
        if !hooksInstalled && usesClaude { offerHooks() }
        statusItem.button?.performClick(nil)
    }

    /// Devuelve true si se ha movido y se está relanzando desde Aplicaciones.
    private func offerMoveToApplications() -> Bool {
        let alert = NSAlert()
        alert.messageText = L("¿Muevo Wick a Aplicaciones?", "Move Wick to Applications?")
        alert.informativeText = L("Así sigue funcionando después de reiniciar y la tienes siempre a mano.",
                                  "That way it keeps working after a restart and is always at hand.")
        alert.addButton(withTitle: L("Mover a Aplicaciones", "Move to Applications"))
        alert.addButton(withTitle: L("Ahora no", "Not now"))
        alert.icon = NSApp.applicationIconImage
        NSApp.activate(ignoringOtherApps: true)
        guard alert.runModal() == .alertFirstButtonReturn else {
            UserDefaults.standard.set(true, forKey: "skipMoveToApplications")
            return false
        }

        let fm = FileManager.default
        let source = URL(fileURLWithPath: Bundle.main.bundlePath)
        let destination = URL(fileURLWithPath: "/Applications/Wick.app")
        do {
            // Si ya hay una copia (otra versión), se cierra y va a la Papelera.
            for app in NSRunningApplication.runningApplications(withBundleIdentifier: Bundle.main.bundleIdentifier ?? "")
            where app.processIdentifier != ProcessInfo.processInfo.processIdentifier {
                app.terminate()
            }
            if fm.fileExists(atPath: destination.path) {
                try fm.trashItem(at: destination, resultingItemURL: nil)
            }
            try fm.copyItem(at: source, to: destination)
        } catch {
            let fail = NSAlert()
            fail.messageText = L("No he podido moverla", "Couldn't move it")
            fail.informativeText = L("Arrastra Wick a la carpeta Aplicaciones desde el Finder y ábrela desde ahí.",
                                     "Drag Wick into the Applications folder in Finder and open it from there.")
            fail.runModal()
            return false
        }
        let open = Process()
        open.executableURL = URL(fileURLWithPath: "/usr/bin/open")
        open.arguments = ["-n", destination.path]
        try? open.run()
        NSApp.terminate(nil)
        return true
    }

    private func showWelcome() {
        let alert = NSAlert()
        alert.messageText = L("Wick ya está en tu barra de menú", "Wick is now in your menu bar")
        alert.informativeText = L(
            "Busca la velita arriba a la derecha, junto al reloj. Se enciende sola cuando un agente se pone a trabajar.\n\nSi no la ves, tu barra está llena y macOS la esconde detrás de la cámara: mantén pulsada ⌘ y arrastra otros iconos para hacerle sitio.",
            "Look for the little candle at the top right, next to the clock. It lights up on its own when an agent starts working.\n\nIf you can't see it, your menu bar is full and macOS hides it behind the camera: hold ⌘ and drag other icons to make room.")
        alert.addButton(withTitle: L("Entendido", "Got it"))
        alert.icon = NSApp.applicationIconImage
        NSApp.activate(ignoringOtherApps: true)
        alert.runModal()
    }

    func applicationWillTerminate(_ notification: Notification) {
        systemHold.set(false, reason: "")
        displayHold.set(false, reason: "")
        lid.stop()
    }

    // MARK: estado

    private var working: [SessionRecord] { sessions.filter { $0.state == .working } }
    private var waiting: [SessionRecord] { sessions.filter { $0.state == .waiting } }

    private var autoAwake: Bool {
        if !working.isEmpty || Date() < graceUntil { return true }
        return keepWhileWaiting && !waiting.isEmpty
    }

    @objc private func tick() {
        let now = Date()
        hookSessions = SessionStore.load(now: now)
        if watchOthers && now.timeIntervalSince(lastScan) >= 3 {
            lastScan = now
            watcher.refresh(includeClaude: !hooksInstalled) { [weak self] in self?.mergeSessions() }
        }
        mergeSessions()
        if !working.isEmpty { graceUntil = now.addingTimeInterval(graceAfterStop) }

        if let end = manualEnd, now >= end {
            manualActive = false
            manualEnd = nil
        }
        if now.timeIntervalSince(lastBatteryCheck) > 30 {
            lastBatteryCheck = now
            lowBattery = Power.lowBattery
        }

        let reason = working.isEmpty ? "Wick: an AI agent just finished" : "Wick: an AI agent is working"
        systemHold.set(autoAwake && !lowBattery, reason: reason)
        displayHold.set(manualActive && !lowBattery, reason: "Wick: kept awake by hand")

        lid.refresh()
        if lidPreference && !lid.running { lidPreference = false }
        // La tapa cerrada solo se mantiene mientras un agente trabaja de verdad (o en modo manual),
        // no durante el margen tras terminar ni mientras te espera.
        lid.want(lidPreference && (!working.isEmpty || manualActive) && !lowBattery)

        updateButtonText()
        if isMenuOpen { header.update(snapshot()) }
    }

    private func mergeSessions() {
        let order: [AgentState: Int] = [.waiting: 0, .working: 1, .idle: 2]
        sessions = (hookSessions + (watchOthers ? watcher.sessions : [])).sorted {
            order[$0.state]! != order[$1.state]! ? order[$0.state]! < order[$1.state]! : $0.since > $1.since
        }
    }

    @objc private func animateIcon() {
        // La velita de verdad, animada; si no están las tiras, el icono vectorial.
        let mood: Mascot = !waiting.isEmpty ? .esperando : (!working.isEmpty || manualActive) ? .trabajando : .descansando
        let frames = MenuBarMascot.frames(mood)
        if !frames.isEmpty {
            if mood != lastMood { lastMood = mood; iconFrame = 0 }
            // descansando va más despacio, como una respiración
            iconTick += 1
            if mood != .descansando || iconTick % 2 == 0 { iconFrame = (iconFrame + 1) % frames.count }
            statusItem.button?.image = frames[iconFrame]
            return
        }
        let mode: MenuIcon.Mode
        blinkCountdown -= 1
        let blink = blinkCountdown <= 0
        if blinkCountdown < -1 { blinkCountdown = Int.random(in: 14...30) }

        if !waiting.isEmpty {
            mode = .waiting(blink: blink)
        } else if !working.isEmpty {
            iconFrame = (iconFrame + 1) % MenuIcon.flickerFrames
            mode = .working(frame: iconFrame, blink: blink)
        } else if manualActive {
            mode = .manual
        } else {
            mode = .idle
        }
        guard mode != lastIcon else { return }
        lastIcon = mode
        statusItem.button?.image = MenuIcon.image(mode)
        statusItem.button?.toolTip = snapshot().title
    }

    private func updateButtonText() {
        var text = ""
        if manualActive {
            text = " " + (manualEnd.map { Self.short($0.timeIntervalSinceNow) } ?? "∞")
        } else if waiting.count > 1 {
            text = " \(waiting.count)"
        }
        if statusItem.button?.title != text { statusItem.button?.title = text }
    }

    private func snapshot() -> MenuSnapshot {
        let awakeNote: String
        if lowBattery {
            awakeNote = L("Batería baja: dejo que el Mac duerma.", "Low battery: letting the Mac sleep.")
        } else if lid.running && lidPreference {
            awakeNote = L("No se dormirá, ni con la tapa cerrada.", "It won't sleep, even with the lid closed.")
        } else {
            awakeNote = L("El Mac no se dormirá.", "Your Mac won't sleep.")
        }

        if !waiting.isEmpty {
            let names = waiting.prefix(2).map(\.project).joined(separator: ", ")
            let sleepNote = keepWhileWaiting ? awakeNote : L("Mientras, el Mac puede dormir.", "Meanwhile, your Mac may sleep.")
            return MenuSnapshot(mascot: .esperando, title: L("Te está esperando", "Waiting for you"),
                            subtitle: L("En \(names).", "In \(names).") + "\n\(sleepNote)")
        }
        if !working.isEmpty {
            let count = working.count
            let first = working[0]
            let what = count == 1
                ? L("\(first.agentName) trabaja en \(first.project).", "\(first.agentName) is working on \(first.project).")
                : L("\(count) agentes trabajando.", "\(count) agents working.")
            return MenuSnapshot(mascot: .trabajando, title: L("Trabajando", "Working"), subtitle: "\(what)\n\(awakeNote)")
        }
        if manualActive {
            guard let end = manualEnd else {
                return MenuSnapshot(mascot: .trabajando, title: L("Despierta a mano", "Awake by hand"),
                                    subtitle: L("Hasta que la apagues.", "Until you blow it out.") + "\n\(awakeNote)")
            }
            let total = max(1, end.timeIntervalSince(manualStart))
            let left = end.timeIntervalSinceNow
            let until = DateFormatter.localizedString(from: end, dateStyle: .none, timeStyle: .short)
            return MenuSnapshot(mascot: .trabajando,
                                title: L("Quedan \(Self.long(left))", "\(Self.long(left)) left"),
                                subtitle: L("Despierta hasta las \(until).", "Awake until \(until)."),
                                progress: left / total)
        }
        if Date() < graceUntil {
            return MenuSnapshot(mascot: .descansando, title: L("Acaba de terminar", "Just finished"),
                            subtitle: L("Espero un par de minutos\npor si vuelve a ponerse.", "Waiting a couple of minutes\nin case it starts again."))
        }
        let sub = hooksInstalled || watchOthers
            ? L("Me enciendo sola cuando\ntu agente se pone a trabajar.", "I light up on my own when\nyour agent starts working.")
            : L("Actívame con tus agentes\npara encenderme sola.", "Turn on agent detection\nand I'll light up on my own.")
        return MenuSnapshot(mascot: .descansando, title: L("Descansando", "Resting"), subtitle: sub)
    }

    // MARK: menú

    private var isMenuOpen = false

    func menuWillOpen(_ menu: NSMenu) {
        isMenuOpen = true
        header.startAnimating()
    }

    func menuDidClose(_ menu: NSMenu) {
        isMenuOpen = false
        header.stopAnimating()
    }

    func menuNeedsUpdate(_ menu: NSMenu) {
        hooksInstalled = HookInstaller.isInstalled()
        sleepStuck = Power.sleepDisabled() && !lid.running
        hookSessions = SessionStore.load()
        mergeSessions()
        menu.removeAllItems()

        let headerItem = NSMenuItem()
        headerItem.view = header
        header.update(snapshot())
        menu.addItem(headerItem)

        if sleepStuck {
            menu.addItem(.separator())
            let fix = item(L("⚠︎ El Mac no se duerme al cerrar la tapa · Arreglar",
                             "⚠︎ Your Mac won't sleep when closed · Fix"), #selector(fixStuckSleep))
            fix.toolTip = L("Quedó así tras un reinicio con el modo tapa cerrada activo. Pide tu contraseña.",
                            "Left over from a restart while lid mode was on. Asks for your password.")
            menu.addItem(fix)
        }

        if !sessions.isEmpty {
            menu.addItem(.separator())
            menu.addItem(sectionTitle(L("Agentes", "Agents")))
            for session in sessions.prefix(6) {
                menu.addItem(sessionItem(session))
            }
        }

        menu.addItem(.separator())
        let auto = item("Claude Code (hooks)", #selector(toggleHooks))
        auto.state = hooksInstalled ? .on : .off
        auto.toolTip = L("Lo más preciso: sabe cuándo trabaja y cuándo te pide permiso. Añade unos hooks a ~/.claude/settings.json; quitarlo los borra.",
                         "Most precise: knows when it works and when it needs you. Adds hooks to ~/.claude/settings.json; turning it off removes them.")
        menu.addItem(auto)

        let others = item(L("Otros agentes (Codex, Gemini, Cursor…)", "Other agents (Codex, Gemini, Cursor…)"),
                          #selector(toggleWatchOthers))
        others.state = watchOthers ? .on : .off
        others.toolTip = L("Los detecta por su proceso: si gastan CPU, están trabajando.",
                           "Detected by their process: if they're using CPU, they're working.")
        menu.addItem(others)

        let wait = item(L("Seguir despierta mientras te espera", "Stay awake while it waits for you"), #selector(toggleKeepWhileWaiting))
        wait.state = keepWhileWaiting ? .on : .off
        menu.addItem(wait)

        let lidItem = item(L("También con la tapa cerrada", "Also with the lid closed"), #selector(toggleLid))
        lidItem.state = lidPreference && lid.running ? .on : .off
        lidItem.toolTip = L("Solo mientras un agente trabaja (o en modo manual). Pide tu contraseña una vez y se desactiva sola al terminar, al salir o con batería baja.",
                            "Only while an agent works (or in manual mode). Asks for your password once and turns itself off when done, on quit or on low battery.")
        menu.addItem(lidItem)

        menu.addItem(.separator())
        let manual = NSMenuItem(title: L("Mantener despierta a mano", "Keep awake by hand"), action: nil, keyEquivalent: "")
        let sub = NSMenu()
        for (index, option) in manualOptions.enumerated() {
            let entry = item(option.label, #selector(startManual(_:)))
            entry.tag = index
            sub.addItem(entry)
        }
        manual.submenu = sub
        menu.addItem(manual)
        if manualActive {
            if manualEnd != nil { menu.addItem(item(L("Añadir 30 minutos", "Add 30 minutes"), #selector(addHalfHour))) }
            menu.addItem(item(L("Apagar la llama", "Blow out the flame"), #selector(stopManual)))
        }

        menu.addItem(.separator())
        let login = item(L("Abrir al iniciar sesión", "Open at login"), #selector(toggleLogin))
        login.state = SMAppService.mainApp.status == .enabled ? .on : .off
        menu.addItem(login)
        menu.addItem(item(L("Wick en GitHub", "Wick on GitHub"), #selector(openRepo)))
        let quit = item(L("Salir de Wick", "Quit Wick"), #selector(quit))
        quit.keyEquivalent = "q"
        menu.addItem(quit)
    }

    private func item(_ title: String, _ action: Selector) -> NSMenuItem {
        let item = NSMenuItem(title: title, action: action, keyEquivalent: "")
        item.target = self
        return item
    }

    private func sectionTitle(_ title: String) -> NSMenuItem {
        let item = NSMenuItem(title: title, action: nil, keyEquivalent: "")
        item.attributedTitle = NSAttributedString(string: title, attributes: [
            .font: NSFont.systemFont(ofSize: 11, weight: .semibold),
            .foregroundColor: NSColor.secondaryLabelColor
        ])
        item.isEnabled = false
        return item
    }

    private func sessionItem(_ s: SessionRecord) -> NSMenuItem {
        let color: NSColor
        let state: String
        switch s.state {
        case .working: color = NSColor(srgbRed: 1, green: 0.55, blue: 0.1, alpha: 1); state = L("trabajando", "working")
        case .waiting: color = NSColor(srgbRed: 0.95, green: 0.3, blue: 0.2, alpha: 1); state = L("te espera", "needs you")
        case .idle:
            color = .tertiaryLabelColor
            state = s.agent == nil ? L("terminado", "done") : L("en pausa", "idle")
        }
        let since = Self.ago(Date().timeIntervalSince(s.since))
        let title = NSMutableAttributedString(string: "● ", attributes: [.foregroundColor: color,
                                                                          .font: NSFont.systemFont(ofSize: 11)])
        title.append(NSAttributedString(string: s.project, attributes: [.font: NSFont.menuFont(ofSize: 0)]))
        title.append(NSAttributedString(string: "  \(s.agentName) · \(state) · \(since)", attributes: [
            .font: NSFont.systemFont(ofSize: 12), .foregroundColor: NSColor.secondaryLabelColor
        ]))
        let item = NSMenuItem(title: s.project, action: s.cwd == nil ? nil : #selector(openSession(_:)), keyEquivalent: "")
        item.attributedTitle = title
        item.target = self
        item.representedObject = s.cwd
        item.toolTip = s.cwd
        return item
    }

    // MARK: acciones

    private func offerHooks() {
        let alert = NSAlert()
        alert.messageText = L("¿Me conecto también con Claude Code?", "Connect me to Claude Code too?")
        alert.informativeText = L(
            "Ya me enciendo sola cuando Codex, Gemini CLI u otros agentes trabajan. Con Claude Code puedo afinar más: sé cuándo te pide permiso y cuándo termina. Para eso añado unos hooks a ~/.claude/settings.json (antes guardo una copia). Puedes quitarlos desde el menú.",
            "I already light up when Codex, Gemini CLI or other agents are working. With Claude Code I can be more precise: I know when it needs your approval and when it's done. For that I add a few hooks to ~/.claude/settings.json (with a backup first). You can remove them from the menu.")
        alert.addButton(withTitle: L("Conectar", "Connect"))
        alert.addButton(withTitle: L("Ahora no", "Not now"))
        alert.icon = NSApp.applicationIconImage
        NSApp.activate(ignoringOtherApps: true)
        if alert.runModal() == .alertFirstButtonReturn { setHooks(true) }
    }

    private func setHooks(_ on: Bool) {
        do {
            if on { try HookInstaller.install() } else { try HookInstaller.uninstall() }
        } catch {
            let alert = NSAlert()
            alert.messageText = L("No he podido tocar ~/.claude/settings.json", "Couldn't update ~/.claude/settings.json")
            alert.informativeText = L("El archivo no es un JSON válido. Revísalo y vuelve a probar; no he cambiado nada.",
                                      "The file isn't valid JSON. Fix it and try again; nothing was changed.")
            NSApp.activate(ignoringOtherApps: true)
            alert.runModal()
        }
        hooksInstalled = HookInstaller.isInstalled()
        tick()
    }

    @objc private func toggleHooks() { setHooks(!hooksInstalled) }

    @objc private func toggleWatchOthers() {
        watchOthers.toggle()
        lastScan = .distantPast
        tick()
    }

    @objc private func toggleKeepWhileWaiting() {
        keepWhileWaiting.toggle()
        tick()
    }

    @objc private func toggleLid() {
        if lidPreference && lid.running {
            lidPreference = false
            lid.stop()
        } else {
            lidPreference = lid.start()
            if !lidPreference { NSSound.beep() }
        }
        sleepStuck = Power.sleepDisabled() && !lid.running
        tick()
    }

    @objc private func fixStuckSleep() {
        if Power.runAsAdmin("/usr/bin/pmset -a disablesleep 0") != nil {
            sleepStuck = Power.sleepDisabled() && !lid.running
        }
    }

    @objc private func startManual(_ sender: NSMenuItem) {
        guard manualOptions.indices.contains(sender.tag) else { return }
        manualActive = true
        manualStart = Date()
        manualEnd = manualOptions[sender.tag].seconds.map { Date().addingTimeInterval($0) }
        tick()
    }

    @objc private func addHalfHour() {
        guard let end = manualEnd else { return }
        manualEnd = end.addingTimeInterval(30 * 60)
        tick()
    }

    @objc private func stopManual() {
        manualActive = false
        manualEnd = nil
        tick()
    }

    @objc private func toggleLogin() {
        do {
            if SMAppService.mainApp.status == .enabled {
                try SMAppService.mainApp.unregister()
            } else {
                try SMAppService.mainApp.register()
            }
        } catch {
            let alert = NSAlert()
            alert.messageText = L("No he podido cambiarlo", "Couldn't change it")
            alert.informativeText = L("Mueve Wick a Aplicaciones y vuelve a probar, o añádela en Ajustes del Sistema → General → Ítems de inicio.",
                                      "Move Wick to Applications and try again, or add it in System Settings → General → Login Items.")
            NSApp.activate(ignoringOtherApps: true)
            alert.runModal()
        }
    }

    @objc private func openSession(_ sender: NSMenuItem) {
        guard let path = sender.representedObject as? String else { return }
        NSWorkspace.shared.open(URL(fileURLWithPath: path))
    }

    @objc private func openRepo() { NSWorkspace.shared.open(repoURL) }

    @objc private func quit() { NSApp.terminate(nil) }

    // MARK: formato

    /// Para la barra de menú: «3 h 59 min», «12 min», «45 s».
    static func short(_ seconds: TimeInterval) -> String {
        let s = max(0, Int(seconds.rounded(.up)))
        if s < 60 { return "\(s) s" }
        let m = (s + 59) / 60
        if m < 60 { return "\(m) min" }
        return m % 60 == 0 ? "\(m / 60) h" : "\(m / 60) h \(m % 60) min"
    }

    /// Para la cabecera del menú: «3 h 59 min», «12 min», «45 segundos».
    static func long(_ seconds: TimeInterval) -> String {
        let s = max(0, Int(seconds.rounded(.up)))
        return s < 60 ? L("\(s) segundos", "\(s) seconds") : short(seconds)
    }

    static func ago(_ seconds: TimeInterval) -> String {
        let m = Int(seconds / 60)
        if m < 1 { return L("ahora", "now") }
        if m < 60 { return "\(m) min" }
        return "\(m / 60) h"
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
